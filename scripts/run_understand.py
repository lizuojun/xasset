#!/usr/bin/env python
"""端到端验证脚本 —— 拿一张户型图跑 understand，出对比图。

这是**三层测试的第三层**：人工运行的验证脚本（不是自动化测试）。

用法：
    python scripts/run_understand.py data/test_images/xxx.png
    python scripts/run_understand.py xxx.png --kind photo --out out/

输出：
    out/compare.png    原图 | 识别轮廓 并排对比
    out/contours.png   纯轮廓线框图
    out/regions.json   understand 的阶段产物（可存档对比）

为什么单独一个脚本而不写进 pytest：
    pytest 验证"代码对不对"，本脚本用于"人眼看结果对不对"。
    两者目的不同，混在一起会让测试变慢且需要人工判断。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 让脚本能直接跑（不需要 pip install -e）
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xasset.pipeline.context import PipelineInput
from xasset.pipeline.stage import StageInputs
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage
from xasset.tools.io import image_to_mask, load_image, mask_stats
from xasset.viz import plot_regions, render_side_by_side


def _fit_ppm(img, regions) -> tuple[float, tuple[float, float]]:
    """计算把米制坐标映射回图片像素所需的 (缩放, 原点偏移)。

    **这是让对比图能对齐的关键。**
    Stage 输出的米制坐标以"整图左下角"为原点（origin_px=(H,0)），
    所以要映射回像素时：
        px_col = x_m * ppm
        px_row = H - z_m * ppm          ← Y 要翻回去

    ppm 的取值：让所有区域的米制包围盒铺满图像（视觉上最清晰）。
    严格来说应该用 Stage 内部真实的 ppm，但那需要 Stage 输出它 ——
    见 docs/task-progress.md 的后续项。
    """
    if not regions:
        return 1.0, (0.0, 0.0)
    xs, zs = [], []
    for r in regions:
        for x, z in r.boundary.points:
            xs.append(x)
            zs.append(z)
    if not xs:
        return 1.0, (0.0, 0.0)

    m_w = max(xs) - min(xs)
    m_h = max(zs) - min(zs)
    if m_w <= 0 or m_h <= 0:
        return 1.0, (0.0, 0.0)

    ppm = min(img.width / m_w, img.height / m_h) * 0.9
    return ppm, (0.0, 0.0)


def main() -> int:
    ap = argparse.ArgumentParser(description="跑 understand 阶段并出对比图")
    ap.add_argument("image", help="户型图路径")
    ap.add_argument("--kind", choices=["drawing", "photo"], default="drawing",
                    help="输入类型：图纸(默认) / 实景照片")
    ap.add_argument("--scene", default="house", help="场景类型")
    ap.add_argument("--out", default="out", help="输出目录")
    args = ap.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[错误] 图片不存在: {img_path}")
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. 读图 ──
    print(f"[1/5] 读取图片: {img_path}")
    img = load_image(img_path)
    print(f"      尺寸: {img.width} x {img.height}")

    # ── 2. 分割（当前用阈值）──
    print("[2/5] 分割（阈值化）")
    mask = image_to_mask(img_path, threshold=200, invert=True)
    stats = mask_stats(mask)
    print(f"      前景像素: {stats['pixels_on']} / {stats['total']} "
          f"({stats['ratio']*100:.1f}%)")

    # ── 3. 跑 Stage ──
    print("[3/5] 运行 understand Stage")
    stage = SceneUnderstandStage()
    inp = PipelineInput(
        input_type="image",
        scene_type=args.scene,
        image_url=str(img_path),
        constraints={"input_kind": args.kind},
    )
    out = stage.run(StageInputs(inp, {}))
    print(f"      产出区域数: {len(out.regions)}")

    # ── 4. 出图 ──
    #
    # understand 产物是**米制**坐标（原点在整图左下角），原图是**像素**坐标。
    # 渲染时要按 px_col = x*ppm, px_row = H - z*ppm 映射回图片。
    print("[4/5] 渲染对比图")

    ppm, _ = _fit_ppm(img, out.regions)
    compare = out_dir / "compare.png"
    render_side_by_side(
        img_path, out.regions, compare,
        pixel_per_meter=ppm,
        flip_y=True,
    )
    print(f"      {compare}")

    contours = out_dir / "contours.png"
    plot_regions(out.regions, contours, title=f"识别轮廓（{len(out.regions)} 个区域）")
    print(f"      {contours}")

    # ── 5. 存产物 ──
    print("[5/5] 保存阶段产物")
    regions_json = out_dir / "regions.json"
    regions_json.write_text(out.model_dump_json(indent=2), encoding="utf-8")
    print(f"      {regions_json}")

    for r in out.regions:
        print(f"      - {r.region_id}: {r.region_type or '(未标注)'} "
              f"{r.area:.2f}m² {len(r.boundary.points)} 顶点")

    if not out.regions:
        print()
        print("[提示] 没有产出区域，原因通常是：")
        print("       - 分割器仍是 StubSegmenter（未接入真实模型）")
        print("       - 或阈值不适合这张图")

    print()
    print("完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
