# xasset/pipeline/stages/understand/scene_understand.py
"""understand 层 Stage —— 轮廓阶段：产出轮廓线 + 语义标签 + 轮廓语义。

契约见 xasset/pipeline/schemas/understand.py。
视觉路线设计见 docs/understand-vision-route.md。

**按 Artist 范式组织**（这是本文件最关键的结构）：

    理解侧出想法 → 约束侧落地 → 校验门 → 不通过则回拉

对应到本 Stage：
    ① 产出想法：② 分割 + ④ 语义标注（理解侧，技术可替换）
    ② 落地：  ③ 几何后处理（约束侧，确定性）
    ③ 校验：  硬约束（tools/constraint）
    ④ 回拉：  refine_idea —— **已预留，当前 max_fix_iterations=1 即不启用**

为什么预留回拉而不是直接写流水线：
    Artist 要求的是"迭代收敛"，不是"单向流水线"。
    当前先做单次求解（见 docs/iteration-convergence.md 第 8 节"先不要做迭代"），
    但结构要按 Artist 摆好——将来把 max_fix_iterations 调到 3 就是迭代了，
    不需要重写 run()。

输入类型（由用户选择，不自动判定）：
- "drawing" 图纸 / 平面图 → 几何后处理时正交化
- "photo"   实景照片     → 正交化关闭
- SceneVector（结构化）  → 直接解析，不过视觉路线
"""
from __future__ import annotations

from typing import Any

from xasset.pipeline.schemas import (
    ContourSemantics,
    Polygon,
    SceneRegion,
    UnderstandOutput,
)
from xasset.pipeline.stage import StageInputs
from xasset.pipeline.stages.understand.interfaces import (
    RegionLabeler,
    RegionMask,
    RegionSegmenter,
    StubLabeler,
    StubSegmenter,
)
from xasset.scene.config import SceneConfig, load_scene_config
from xasset.tools.constraint import understand_hard_constraints
from xasset.tools.geometry.contour import (
    ScaleInfo,
    infer_scale_from_area,
    mask_to_polygon,
)
from xasset.tools.geometry.mesh import polygon_area
from xasset.tools.geometry.normalize import normalize_scene_vector


class _Idea:
    """理解侧产出的「想法」——一个尚未落地的区域候选。

    刻意与最终产物 SceneRegion 分开：
    - 想法：mask + 语义（还没有米制多边形）
    - 产物：SceneRegion（有 Polygon、面积、轮廓语义）

    这样"回拉新想法"时，改的是想法，不是已落地的产物。
    """

    def __init__(
        self,
        mask: RegionMask | None,
        region_type: str,
        *,
        confidence: float = 1.0,
        scale: ScaleInfo | None = None,
    ) -> None:
        self.mask = mask
        self.region_type = region_type
        self.confidence = confidence
        self.scale = scale


class SceneUnderstandStage:
    name = "scene_understand"
    layer = "understand"
    scene_types = ["*"]
    requires: list[str] = []            # 只依赖 PipelineInput
    output_type = UnderstandOutput

    # ── Artist 迭代参数 ────────────────────────────────────────
    # 当前为 1 = 单次求解，不做回拉（符合 iteration-convergence.md 第 8 节建议）
    # 将来改成 3 就是真正的迭代，结构不用动
    max_fix_iterations: int = 1

    def __init__(
        self,
        segmenter: RegionSegmenter | None = None,
        labeler: RegionLabeler | None = None,
        *,
        simplify_tolerance_m: float = 0.05,
        orthogonalize_angle_tol_deg: float = 15.0,
        scene_config: SceneConfig | None = None,
        use_threshold_segmenter: bool = True,
    ) -> None:
        # 理解侧：技术可替换
        # 默认用阈值分割器（零依赖，对线条户型图有效）；
        # 传入自己的实现即可替换，Stage 其它代码不用改。
        if segmenter is not None:
            self._segmenter = segmenter
        elif use_threshold_segmenter:
            from xasset.pipeline.stages.understand.segmenters import (
                ThresholdRegionSegmenter,
            )
            self._segmenter = ThresholdRegionSegmenter()
        else:
            self._segmenter = StubSegmenter()

        self._labeler = labeler or StubLabeler()
        # 约束侧参数（确定性）
        self._simplify_tol = simplify_tolerance_m
        self._ortho_tol = orthogonalize_angle_tol_deg
        # 约束侧校验门
        self._hard_constraints = understand_hard_constraints()
        # 场景知识（区域词表 / 面积先验）—— 从配置读，不硬编码
        self._scene_config = scene_config

    # ── Stage 入口（Artist 形状）────────────────────────────────

    def run(self, inputs: StageInputs) -> UnderstandOutput:
        inp = inputs.pipeline_input

        # 路线 0：结构化输入（SceneVector），不走视觉路线
        if inp.scene_vector:
            return self._from_scene_vector(inp)

        # 路线 1/2：图片输入，走「想法 → 落地 → 校验 → 回拉」
        if inp.image_url or inp.input_type in ("image", "concept_art"):
            return self._from_image(inp)

        # 路线 3：暂无可处理输入
        return UnderstandOutput(
            scene_type=inp.scene_type,
            style=inp.style,
            regions=[],
        )

    # ── 图片路线：Artist 形状的迭代收敛 ────────────────────────

    def _from_image(self, inp) -> UnderstandOutput:
        """图片 → 轮廓。

        结构是 Artist 的「想法 → 落地 → 校验 → (回拉)」。
        当前 max_fix_iterations=1，等价于单次求解 + 强制校验。
        """
        input_kind = inp.constraints.get("input_kind", "drawing")
        image = inp.image_url

        # 取图片高度 —— 用于建立统一的米制坐标系
        image_height = _image_height_px(image)

        # ① 理解侧：产出想法（分割 + 语义）
        idea = self.produce_idea(image, inp, input_kind=input_kind)

        output = None
        for iteration in range(self.max_fix_iterations):
            # ② 约束侧：把想法落地成米制多边形
            output = self.realize(
                idea, inp,
                input_kind=input_kind,
                image_height_px=image_height,
            )

            # ③ 校验门（强制，无例外）
            result = self._hard_constraints.validate(None, output)
            if result.ok:
                break

            # ④ 回拉新想法 —— 当前是最后一步，不继续；将来会用它修正
            if iteration + 1 < self.max_fix_iterations:
                idea = self.refine_idea(idea, result, inp)

        return output

    # ── 理解侧 ────────────────────────────────────────────────

    def produce_idea(self, image: Any, inp, *, input_kind: str) -> list[_Idea]:
        """① 理解侧：分割 + 语义标注，产出「想法」列表。

        这是**可替换**的部分——换分割模型或标注模型不影响其它逻辑。
        """
        masks = self._segmenter.segment(image, input_kind=input_kind)

        # 先用占位多边形调标注器（标注器需要知道有几个区域）
        stub_polys = [Polygon(points=[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
                      for _ in masks]
        labels = self._labeler.label(image, stub_polys, scene_type=inp.scene_type)

        ideas: list[_Idea] = []
        for i, m in enumerate(masks):
            label = labels[i] if i < len(labels) else None
            ideas.append(_Idea(
                mask=m,
                region_type=(
                    label.region_type if label
                    else (m.hint_region_type or "")
                ),
                confidence=label.confidence if label else 1.0,
            ))
        return ideas

    def refine_idea(self, idea: list[_Idea], errors, inp) -> list[_Idea]:
        """④ 回拉：带着校验失败信息重新产生想法。

        **当前未启用**（max_fix_iterations=1）。
        将来启用时的做法：
        - 若错误是"开口悬空"，说明分割出的区域有裂缝 → 让分割器重出 mask
        - 若错误是"面积不合规"，说明尺度推断错了 → 换尺度来源重算

        这里先保留结构，返回原想法（不做改动）。
        """
        return idea

    # ── 尺度推断 ──────────────────────────────────────────────

    def _scene_scale(self, ideas: list[_Idea], scene_config: SceneConfig) -> ScaleInfo | None:
        """推断**整个场景共用**的像素→米尺度。

        为什么必须共用：
            如果每个区域各算各的尺度，每块都会被"拉到"典型面积，
            房间之间的大小差异就被抹平了 —— 相对关系失真。

        做法：
            取面积最大的那个区域，用它的典型面积反推尺度。
            大区域（通常是客厅）的典型面积区间相对稳定，
            而且像素量大、面积估计误差小。

        局限（必须承认）：
            这个方法是估算，不是精确测量。真正可靠的做法是
            找到一个已知尺寸的参照物（如标准门宽 0.9m）。
            参照物识别属于理解侧的工作，接入后应优先使用。
        """
        # 优先：任一 idea 自带尺度（来自参照物）
        for idea in ideas:
            if idea.scale is not None:
                return idea.scale

        # 兜底：用最大区域的典型面积反推
        best_px_area = 0.0
        best_region_type = ""
        for idea in ideas:
            if idea.mask is None or not idea.mask.mask:
                continue
            px = _mask_pixel_area(idea.mask.mask)
            if px > best_px_area:
                best_px_area = px
                best_region_type = idea.region_type

        if best_px_area <= 0:
            return None

        return infer_scale_from_area(
            px_area=best_px_area,
            expected_area_m2=scene_config.typical_area(best_region_type),
        )

    # ── 场景配置 ──────────────────────────────────────────────

    def _resolve_scene_config(self, scene_type: str) -> SceneConfig:
        """取得场景配置。注入优先，否则按 scene_type 从 data/<scene>/scene.json 读。

        若该场景还没建配置文件（如 urban 未开始），退化为一个空配置，
        用 SceneConfig 的 fallback 面积——**不让流程因为缺配置而崩**。
        """
        if self._scene_config is not None:
            return self._scene_config
        try:
            return load_scene_config(scene_type)
        except FileNotFoundError:
            # 场景配置缺失：用空配置 + 默认兜底，保证流程能跑
            return SceneConfig(scene=scene_type)

    # ── 约束侧 ────────────────────────────────────────────────

    def realize(
        self,
        ideas: list[_Idea],
        inp,
        *,
        input_kind: str,
        image_height_px: int | None = None,
    ) -> UnderstandOutput:
        """② 约束侧：把「想法」落地成合法的米制多边形。

        这是**确定性**的部分——mask → 多边形的所有计算都在
        tools/geometry/contour.py 里，不涉及任何模型。

        Parameters
        ----------
        image_height_px : 原图高度（像素）。
            用于把 Y 轴翻转后整体偏移到正区间，使所有区域落在同一坐标系里。
            None 时用各区域自身包围盒（只有单区域时合理）。
        """
        # 正交化只用于图纸；实景照片不加正交化（真实墙角未必垂直）
        do_orthogonalize = (input_kind == "drawing")

        # 场景知识从配置读（不在代码里硬编码面积先验）
        scene_config = self._resolve_scene_config(inp.scene_type)

        # 整个场景共用一个尺度 —— 不能每个区域各自算，
        # 否则各区域被缩放到相似大小，相对关系就失真了。
        scene_scale = self._scene_scale(ideas, scene_config)

        regions: list[SceneRegion] = []
        for idx, idea in enumerate(ideas):
            if idea.mask is None or not idea.mask.mask:
                continue

            scale = idea.scale or scene_scale
            if scale is None:
                continue

            # 原点策略：
            # - 知道整图高度 → 以"整图左下角"为原点，所有区域共享同一坐标系
            # - 不知道 → 用本区域包围盒（只适合单区域，多区域会重叠）
            if image_height_px is not None:
                origin_px = (image_height_px, 0)
            else:
                origin_px = idea.mask.origin_px

            contour = mask_to_polygon(
                idea.mask.mask,
                scale,
                simplify_tolerance_m=self._simplify_tol,
                orthogonalize_result=do_orthogonalize,
                angle_tolerance_deg=self._ortho_tol,
                origin_px=origin_px,
                # mask 已裁过包围盒，轮廓点需要加上包围盒偏移
                mask_offset_px=idea.mask.origin_px,
            )
            if len(contour.polygon) < 3:
                continue

            regions.append(SceneRegion(
                region_id=f"region_{idx}",
                region_type=idea.region_type,
                boundary=Polygon(points=contour.polygon),
                area=contour.area_m2,
                semantics=ContourSemantics(),
            ))

        return UnderstandOutput(
            scene_type=inp.scene_type,
            regions=regions,
            style=inp.style,
            constraints=dict(inp.constraints or {}),
        )

    # ── 路线 0：结构化输入 ─────────────────────────────────────

    def _from_scene_vector(self, inp) -> UnderstandOutput:
        """从 SceneVector 解析出轮廓线 + 语义 + 轮廓语义。

        这条路线不涉及视觉，直接解析已有的结构化数据。
        """
        norm = normalize_scene_vector(inp.scene_vector)
        rv = norm.scene_vector
        constraints = dict(inp.constraints or {})

        if norm.excluded_room_ids:
            constraints["_excluded_room_ids"] = norm.excluded_room_ids
        if norm.excluded_opening_ids:
            constraints["_excluded_opening_ids"] = norm.excluded_opening_ids

        regions: list[SceneRegion] = []
        for room_idx, room in enumerate(rv.get("rooms", [])):
            floor = room.get("floor", [])
            boundary = Polygon(points=[tuple(p) for p in floor]) if len(floor) >= 3 else None
            if boundary is None:
                continue
            regions.append(
                SceneRegion(
                    region_id=room.get("id", f"room_{room_idx}"),
                    region_type=room.get("type") or inp.region_type or "",
                    boundary=boundary,
                    area=polygon_area(floor),
                    height=room.get("height") or constraints.get("room_height"),
                    semantics=ContourSemantics(),   # 待理解侧重做：开口/固定边解析
                )
            )

        return UnderstandOutput(
            scene_type=inp.scene_type,
            regions=regions,
            style=inp.style,
            constraints=constraints,
        )


# ── 辅助 ────────────────────────────────────────────────────────────────

def _mask_pixel_area(mask: list[list[bool]]) -> float:
    return float(sum(1 for row in mask for v in row if v))


def _image_height_px(image) -> int | None:
    """取图片高度（像素）。取不到返回 None。"""
    try:
        from pathlib import Path

        if isinstance(image, (str, Path)):
            from PIL import Image
            with Image.open(image) as im:
                return im.size[1]
    except Exception:
        pass
    return None

