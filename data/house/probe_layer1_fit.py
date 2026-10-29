"""
data/house/probe_layer1_fit.py — 一次性探针脚本

验证问题：数据量还不够训练模型，但"数据驱动布局"这条流程本身能不能跑通？
输入（data/house/converted/layout_samples/*.json 里 73 条 resolved 样本，即
真实历史设计的房间→Group 摆放结果）和 xasset 现有的几何管线（RoomDecomposer
产出的 WallSegment/depth_profile）之间，数据格式是否对得上？

用法：
    python data/house/probe_layer1_fit.py

不修改 xasset/ 包本身；只读 data/house/converted/、xasset/pipeline/stages/
layout/house/groups.json，写 data/house/converted/probe_report.json。

已知局限（详见 data/house/PROBE_FINDINGS.md）：
- "墙段关联检查"是本脚本手写的近似逻辑，不是被删除的 score_walls_for_group()
  的精确复刻。已按 GroupDefinition.wall_offset_ratio 区分贴墙(0.0)/岛式
  居中(0.5)/翻转贴对面墙(1.0)三种情况，但候选墙段的选取仍是启发式匹配，
  不保证覆盖所有真实摆放模式。
- size 的 x/z 分量固定 size[0]→w, size[2]→d（物体局部坐标系下的固定映射，
  与 rotation_yaw_deg 无关，PROBE_FINDINGS.md 结论二有实测验证）。
- 目的是看流程通不通、格式对不对，不是产出一个可信的"合法率"指标。
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

_HERE = Path(__file__).parent
_CONVERTED = _HERE / "converted"
_ROOMS = _CONVERTED / "rooms"
_SAMPLES = _CONVERTED / "layout_samples"

sys.path.insert(0, str(_HERE.parent.parent))
from xasset.pipeline.context import PipelineInput, PipelineContext  # noqa: E402
from xasset.pipeline.stages.understand.scene_understand import SceneUnderstandStage  # noqa: E402
from xasset.pipeline.stages.layout.house.room_decompose import RoomDecomposer  # noqa: E402


# ── groups.json footprint + wall_offset_ratio lookup ─────────────────────────

def _load_footprint_by_code() -> dict[int, list[list[float]] | None]:
    groups_json = (
        _HERE.parent.parent
        / "xasset" / "pipeline" / "stages" / "layout" / "house" / "groups.json"
    )
    raw = json.loads(groups_json.read_text(encoding="utf-8"))
    return {g["code"]: g.get("footprint_range") for g in raw["groups"]}


def _load_wall_offset_ratio_by_code() -> dict[int, float]:
    groups_json = (
        _HERE.parent.parent
        / "xasset" / "pipeline" / "stages" / "layout" / "house" / "groups.json"
    )
    raw = json.loads(groups_json.read_text(encoding="utf-8"))
    return {g["code"]: g.get("wall_offset_ratio", 0.0) for g in raw["groups"]}


# ── 房间几何加载（复用 convert.py 里验证过的构造方式） ───────────────────────

def _load_region_and_walls(room_file: str):
    room = json.loads((_ROOMS / room_file).read_text(encoding="utf-8"))
    scene_vector = {
        "meta": {"coordinate": "xzy", "unit": "m", "version": "1.0"},
        "rooms": [{
            "id": room["room_id"],
            "type": room["region_type"],  # 已规范化的值，不是 region_type_raw
            "height": room["height"],
            "floor": room["boundary"],
            "doors": [
                {"id": d["id"], "pts": d["pts"], "to_room": d["to_room"]}
                for d in room["doors"]
            ],
            "windows": [
                {"id": w["id"], "window_type": w["window_type"], "pts": w["pts"],
                 "height": w.get("height")}
                for w in room["windows"]
            ],
        }],
    }
    ctx = PipelineContext(str(uuid.uuid4()), PipelineInput(
        input_type="vector", scene_type="house", scene_vector=scene_vector,
    ))
    SceneUnderstandStage().run(ctx)
    out = ctx.stage_outputs["understand"]
    if not out.regions:
        raise ValueError("no regions produced")
    region = out.regions[0]
    walls, curtains = RoomDecomposer().decompose(region)
    return region, walls, curtains


# ── 格式适配层：layout_samples[].placed_groups[] -> PlacedGroup 兼容 dict ────

def _adapt_placed_group(raw: dict, format_issues: list[str]) -> dict:
    """把转换脚本产出的字段名适配成 compose.py::PlacedGroup 的字段名。

    已知差异（如实记录，不默默转换）：
    - 源字段是 rotation_yaw_deg，PlacedGroup 是 rotation —— 值语义/单位一致
      （都是绕 Y 轴角度，单位度），只是命名不同，这里做重命名。
    - PlacedGroup 有 sub_positions 字段，源数据没有对应信息 —— 留空 {}。
    """
    if "rotation_yaw_deg" not in raw:
        format_issues.append(f"missing rotation_yaw_deg on group_code={raw.get('group_code')}")
    return {
        "group_code": raw.get("group_code"),
        "region_type": None,  # 由外层填充，源数据在样本级不是逐 group 存
        "position": raw.get("position"),
        "rotation": raw.get("rotation_yaw_deg", 0.0),  # 改名：rotation_yaw_deg -> rotation
        "role_assets": {},  # PlacedGroup 有此字段，源数据无对应信息，留空
        "sub_positions": {},  # PlacedGroup 有此字段，源数据无对应信息，留空
        "_raw_size": raw.get("size"),
        "_raw_obj_type": raw.get("obj_type"),
    }


# ── 尺寸检查 ──────────────────────────────────────────────────────────────────

def _axis_align_size(size: list[float], rotation_deg: float) -> tuple[float, float]:
    """size[x,y,z] 的 x/z 分量对齐成 (w, d)。

    修正（v3）：size 是在物体自身的局部/摆放坐标系下记录的——size[0] 恒对应
    "沿墙方向"（w），size[2] 恒对应"朝房间内的深度方向"（d），这个对应关系
    与 rotation_yaw_deg（物体在世界坐标系里怎么摆）无关，不需要跟着旋转角度
    做轴交换。v2 曾按最接近的直角把 w/d 反过来对齐，实测在 rot≈±90° 的样本上
    系统性判反（例：100902 电视组 rot=-90.001 时 size=[1.04,1.489,0.084]，
    0.084 明明是贴墙的薄边应对应 d，v2 却把它塞进 w，报深度超限），去掉轴
    交换后 pass 率从 64/144 升到 105/144——确认是脚本 bug，不是近似取舍。
    """
    return size[0], size[2]


def _check_size(placed: dict, footprint: list[list[float]] | None) -> dict:
    """检查 Group 深度分量是否落在 footprint_range 的 d 区间内。

    深度分量受子物件影响较小（子物件通常挂在锚点两侧而非前后延伸，例如床头
    柜在床的左右而非头尾），实测吻合度高，保留作为唯一硬性判断；宽度分量受
    Group 级 size（含子物件外包框）与 footprint_range（锚点角色本身尺寸）
    粒度不对齐影响较大（详见 PROBE_FINDINGS.md 结论二），仅记录差值供参考，
    不计入 pass/fail。
    """
    if footprint is None:
        return {"status": "skip_no_footprint"}
    size = placed["_raw_size"]
    if not size or len(size) < 3:
        return {"status": "skip_no_size"}
    w, d = _axis_align_size(size, placed["rotation"])
    (w_min, w_max), (d_min, d_max) = footprint
    w_ok = w_min <= w <= w_max
    d_ok = d_min <= d <= d_max
    return {
        "status": "pass" if d_ok else "fail",  # 只用深度分量判定；宽度仅供参考
        "w": round(w, 3), "d": round(d, 3),
        "w_range": [w_min, w_max], "d_range": [d_min, d_max],
        "w_ok": w_ok, "d_ok": d_ok,
    }


# ── 贴墙检查 ──────────────────────────────────────────────────────────────────

_WALL_MATCH_SLACK = 0.3  # m — 距离匹配的容差（wall_offset_ratio 非 0 时房间深度不确定性更大，适度放宽）


def _point_to_segment_perp(pt: list[float], p0: list[float], p1: list[float]) -> tuple[float, float] | None:
    """pt 到线段 p0-p1 所在直线的垂直距离 + 投影参数 t，投影落在线段范围内才返回值。"""
    ax, az = p0
    bx, bz = p1
    dx, dz = bx - ax, bz - az
    len2 = dx * dx + dz * dz
    if len2 < 1e-9:
        return None
    t = ((pt[0] - ax) * dx + (pt[1] - az) * dz) / len2
    if not (-0.05 <= t <= 1.05):
        return None
    perp = abs((pt[0] - ax) * dz - (pt[1] - az) * dx) / (len2 ** 0.5)
    return perp, t


def _depth_at_t(seg, t: float) -> float:
    """seg.depth_profile 是按 [t0,t1] 区间分段的深度采样；取 t 落在哪个区间的 depth。"""
    if not seg.depth_profile:
        return 0.0
    for ds in seg.depth_profile:
        if ds.t0 - 1e-6 <= t <= ds.t1 + 1e-6:
            return ds.depth
    return min(ds.depth for ds in seg.depth_profile)


def _check_wall_fit(placed: dict, footprint: list[list[float]] | None,
                     wall_offset_ratio: float, walls) -> dict:
    """判定"关联到哪段墙"：不是只判"贴墙"，wall_offset_ratio 描述的是家具沿
    深度方向从贴墙(0)滑到房间对面(1)这条轨迹上的位置比例（见 groups.json
    GroupDefinition.wall_offset_ratio 注释：0.0=贴墙, 0.5=岛式居中, 1.0=180°
    翻转贴对面墙）。work/dining 这类 ratio>0 的 Group 依然需要先关联到"最合适
    的 WallSegment"，只是不贴墙——期望的墙-中心距离统一用
        expected = d/2 + ratio * (该点实际可用房间深度 D - d)
    计算，D 从候选墙段自己的 depth_profile 在对应位置取值，不再是固定容差。
    ratio=0 时退化为"贴墙"（expected=d/2），与之前的贴墙检查完全兼容。
    """
    if footprint is None:
        return {"status": "skip_no_footprint"}
    pos = placed["position"]
    if not pos or len(pos) < 3:
        return {"status": "skip_no_position"}
    pt = [pos[0], pos[2]]  # xz 平面

    (w_min, w_max), (d_min, d_max) = footprint
    d_avg = (d_min + d_max) / 2.0

    best_seg = None
    best_diff = None
    best_info = None
    for seg in walls:
        if seg.seg_type not in ("wall", "window"):
            continue
        r = _point_to_segment_perp(pt, seg.p0, seg.p1)
        if r is None:
            continue
        perp_dist, t = r
        room_depth_here = _depth_at_t(seg, t)
        if room_depth_here < d_min:
            continue  # 这段墙这个位置的可用深度不够放这个 footprint，不是候选
        expected = d_avg / 2.0 + wall_offset_ratio * max(room_depth_here - d_avg, 0.0)
        diff = abs(perp_dist - expected)
        if diff <= _WALL_MATCH_SLACK and (best_diff is None or diff < best_diff):
            best_diff = diff
            best_seg = seg
            best_info = {"perp_dist": round(perp_dist, 3), "expected": round(expected, 3),
                         "room_depth_here": round(room_depth_here, 3)}

    if best_seg is None:
        return {"status": "no_matching_wall", "wall_offset_ratio": wall_offset_ratio}

    length_ok = best_seg.length >= w_min
    depth_ok = best_info["room_depth_here"] >= d_min
    return {
        "status": "pass" if (length_ok and depth_ok) else "fail",
        "perp_dist": best_info["perp_dist"],
        "expected_dist": best_info["expected"],
        "seg_length": round(best_seg.length, 3),
        "seg_depth_here": best_info["room_depth_here"],
        "w_min": w_min, "d_min": d_min,
        "wall_offset_ratio": wall_offset_ratio,
        "length_ok": length_ok, "depth_ok": depth_ok,
    }


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    footprint_by_code = _load_footprint_by_code()
    wall_offset_ratio_by_code = _load_wall_offset_ratio_by_code()
    sample_files = sorted(_SAMPLES.glob("*.json"))

    report = {
        "total_samples": 0,
        "resolved_samples": 0,
        "total_placed_groups": 0,
        "groups_with_code": 0,
        "groups_without_code": 0,
        "format_issues": [],
        "size_check": {"pass": 0, "fail": 0, "skip_no_footprint": 0, "skip_no_size": 0,
                        "by_code": {}, "fail_examples": []},
        "wall_check": {"pass": 0, "fail": 0, "no_matching_wall": 0,
                        "skip_no_footprint": 0, "skip_no_position": 0,
                        "by_code": {}, "fail_examples": []},
        "pipeline_errors": [],
    }

    room_cache: dict[str, tuple] = {}

    for sf in sample_files:
        sample = json.loads(sf.read_text(encoding="utf-8"))
        report["total_samples"] += 1
        if not sample["resolved"]:
            continue
        report["resolved_samples"] += 1

        room_file = sample["source_room_file"]
        if room_file not in room_cache:
            try:
                room_cache[room_file] = _load_region_and_walls(room_file)
            except Exception as e:
                report["pipeline_errors"].append({
                    "sample": sf.name, "room_file": room_file,
                    "error": f"{type(e).__name__}: {e}",
                })
                continue
        region, walls, curtains = room_cache[room_file]

        for raw_group in sample["placed_groups"]:
            report["total_placed_groups"] += 1
            code = raw_group.get("group_code")
            if code is None:
                report["groups_without_code"] += 1
                continue
            report["groups_with_code"] += 1

            placed = _adapt_placed_group(raw_group, report["format_issues"])
            footprint = footprint_by_code.get(code)
            wall_offset_ratio = wall_offset_ratio_by_code.get(code, 0.0)

            size_result = _check_size(placed, footprint)
            wall_result = _check_wall_fit(placed, footprint, wall_offset_ratio, walls)

            code_key = str(code)
            sc_bucket = report["size_check"]["by_code"].setdefault(code_key, {"pass": 0, "fail": 0, "skip": 0})
            if size_result["status"] == "pass":
                report["size_check"]["pass"] += 1
                sc_bucket["pass"] += 1
            elif size_result["status"] == "fail":
                report["size_check"]["fail"] += 1
                sc_bucket["fail"] += 1
                if len(report["size_check"]["fail_examples"]) < 20:
                    report["size_check"]["fail_examples"].append({
                        "sample": sf.name, "group_code": code, **size_result,
                    })
            else:
                report["size_check"][size_result["status"]] += 1
                sc_bucket["skip"] += 1

            wc_bucket = report["wall_check"]["by_code"].setdefault(code_key, {"pass": 0, "fail": 0, "no_matching_wall": 0, "skip": 0})
            status = wall_result["status"]
            if status == "pass":
                report["wall_check"]["pass"] += 1
                wc_bucket["pass"] += 1
            elif status == "fail":
                report["wall_check"]["fail"] += 1
                wc_bucket["fail"] += 1
                if len(report["wall_check"]["fail_examples"]) < 20:
                    report["wall_check"]["fail_examples"].append({
                        "sample": sf.name, "group_code": code, **wall_result,
                    })
            elif status == "no_matching_wall":
                report["wall_check"]["no_matching_wall"] += 1
                wc_bucket["no_matching_wall"] += 1
            else:
                report["wall_check"][status] += 1
                wc_bucket["skip"] += 1

    (_CONVERTED / "probe_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"samples: {report['total_samples']} total, {report['resolved_samples']} resolved")
    print(f"placed_groups: {report['total_placed_groups']} total "
          f"({report['groups_with_code']} with code, {report['groups_without_code']} without)")
    print(f"size_check: pass={report['size_check']['pass']} fail={report['size_check']['fail']} "
          f"skip_no_footprint={report['size_check']['skip_no_footprint']} skip_no_size={report['size_check']['skip_no_size']}")
    print(f"wall_check: pass={report['wall_check']['pass']} fail={report['wall_check']['fail']} "
          f"no_matching_wall={report['wall_check']['no_matching_wall']} "
          f"skip_no_footprint={report['wall_check']['skip_no_footprint']} skip_no_position={report['wall_check']['skip_no_position']}")
    print(f"format_issues: {len(report['format_issues'])}")
    print(f"pipeline_errors: {len(report['pipeline_errors'])}")
    print(f"report -> {_CONVERTED / 'probe_report.json'}")


if __name__ == "__main__":
    main()
