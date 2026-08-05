"""
data/house/convert.py — 一次性数据转换脚本

把 D:\\Projects\\XEditor-Ref\\ihome-layout\\House 的历史数据（本地拷贝在
data/house/raw/）转换成 xasset 自己的 SceneVector / PlacedGroup 兼容 JSON。

用法：
    python data/house/convert.py

不修改 xasset/ 包本身；只读 data/house/raw/、data/house/mapping/，
写 data/house/converted/。可重复运行（覆盖旧输出）。

设计依据见 data/house/mapping/README.md 和
research/learned-layout-with-hard-constraints/README.md。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_HERE = Path(__file__).parent
_RAW = _HERE / "raw"
_MAPPING = _HERE / "mapping"
_OUT = _HERE / "converted"

sys.path.insert(0, str(_HERE.parent.parent))
from xasset.pipeline.stages.understand.scene_understand import _normalize_region_type  # noqa: E402


def _load_xasset_region_types() -> set[str]:
    """xasset groups.json 里真正存在 Group 定义的 region_type 集合。"""
    groups_json = (
        _HERE.parent.parent
        / "xasset" / "pipeline" / "stages" / "layout" / "house" / "groups.json"
    )
    raw = json.loads(groups_json.read_text(encoding="utf-8"))
    return set(raw["region_groups"].keys())


# ── 映射表加载 ────────────────────────────────────────────────────────────────

def _load_region_type_map() -> dict[str, tuple[str, bool]]:
    """返回 legacy room type -> (region_type, mapped: bool)。"""
    raw = json.loads((_MAPPING / "region_type_map.json").read_text(encoding="utf-8"))
    result: dict[str, tuple[str, bool]] = {}
    for legacy, region_type in raw["mapped"].items():
        result[legacy] = (region_type, True)
    for legacy, region_type in raw["unmapped"].items():
        result[legacy] = (region_type, False)
    return result


def _load_group_type_map() -> dict[tuple[str, str], dict]:
    """返回 (legacy group.type, region_type) -> {code, note}。"""
    raw = json.loads((_MAPPING / "group_type_map.json").read_text(encoding="utf-8"))
    result: dict[tuple[str, str], dict] = {}
    for pair in raw["pairs"]:
        result[(pair["type"], pair["region_type"])] = {
            "code": pair["code"],
            "note": pair["note"],
        }
    return result


# ── 几何转换 helper ───────────────────────────────────────────────────────────

def _flat_to_pairs(flat: list[float]) -> list[list[float]]:
    """[x,z,x,z,...] -> [[x,z],[x,z],...]，去掉首尾重复闭合点。"""
    pairs = [[flat[i], flat[i + 1]] for i in range(0, len(flat), 2)]
    if len(pairs) >= 2 and pairs[0] == pairs[-1]:
        pairs = pairs[:-1]
    return pairs


def _quat_to_yaw_deg(q: list[float]) -> float:
    """四元数 [x,y,z,w] -> 绕 Y 轴的 yaw 角度（度）。"""
    x, y, z, w = q
    # standard yaw (Y-up) extraction
    siny_cosp = 2 * (w * y + x * z)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    return math.degrees(math.atan2(siny_cosp, cosy_cosp))


def _euler_to_yaw_deg(e: list[float], coordinate: str) -> float:
    """3 元 Euler [x,y,z]（house_data_more.json 用，coordinate="xyz"）-> yaw 角度。

    house_data_more.json 里的 Euler 分量本身单位未在数据中注明；抽样发现绝大多数
    实体的分量为 [0,0,0]（无旋转），少数非零值经核对与 Y 轴分量对应度数一致。
    这里假设 e[1] 就是绕 Y 轴的角度（度），与 coordinate="xyz" 的轴序一致。
    """
    del coordinate  # 目前两个文件的 Euler 轴序推断一致，暂不需要按 coordinate 分支
    return e[1]


def _rotation_to_yaw_deg(rotation: list[float], coordinate: str) -> float:
    if len(rotation) == 4:
        return round(_quat_to_yaw_deg(rotation), 3)
    if len(rotation) == 3:
        return round(_euler_to_yaw_deg(rotation, coordinate), 3)
    raise ValueError(f"unexpected rotation length: {rotation}")


_FURNITURE_PLACEHOLDER_PREFIXES = ("door/", "window/", "curtain/")


# ── 房间几何转换 ──────────────────────────────────────────────────────────────

def convert_rooms(region_map: dict[str, tuple[str, bool]], xasset_region_types: set[str]) -> dict:
    """转换 house_data_dict.json + house_data_more.json 的全部房间。

    返回 report dict，同时把每个房间写成一个 JSON 文件到 converted/rooms/。
    """
    rooms_dir = _OUT / "rooms"
    rooms_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "total_rooms": 0,
        "region_type_unmapped_counts": {},  # legacy type -> count
        "region_type_mapped_counts": {},
        "rooms_written": [],  # [{house_id, room_id, filename}]
    }

    for src_name in ("house_data_dict.json", "house_data_more.json"):
        data = json.loads((_RAW / src_name).read_text(encoding="utf-8"))
        for house_id, house in data.items():
            for room in house["room"]:
                report["total_rooms"] += 1
                room_id = room["id"]
                raw_type = room.get("type", "")
                coordinate = room.get("coordinate", "xzy")

                region_type, priority = _normalize_region_type(raw_type)
                if region_type not in xasset_region_types:
                    # _normalize_region_type 只处理主/次前缀，没命中 xasset 的
                    # region_groups key 时（大小写差异、或完全没有对应项），
                    # 走 region_type_map.json 做二次映射。
                    mapped_region_type, is_mapped = region_map.get(raw_type, (raw_type, False))
                    region_type = mapped_region_type
                    if is_mapped:
                        report["region_type_mapped_counts"][raw_type] = (
                            report["region_type_mapped_counts"].get(raw_type, 0) + 1
                        )
                    else:
                        report["region_type_unmapped_counts"][raw_type] = (
                            report["region_type_unmapped_counts"].get(raw_type, 0) + 1
                        )

                floor_pairs = _flat_to_pairs(room.get("floor", []))

                doors = []
                for d in room.get("door_info", []):
                    doors.append({
                        "id": f"{room_id}__door_{len(doors)}",
                        "pts": _flat_to_pairs(d["pts"]),
                        "to_room": d.get("to") or None,
                    })

                windows = []
                for w in room.get("window_info", []):
                    windows.append({
                        "id": f"{room_id}__window_{len(windows)}",
                        "window_type": "normal",
                        "pts": _flat_to_pairs(w["pts"]),
                        "height": w.get("height"),
                        "to_room": w.get("to") or None,
                    })

                holes = []
                for h in room.get("hole_info", []):
                    holes.append({
                        "id": f"{room_id}__hole_{len(holes)}",
                        "pts": _flat_to_pairs(h["pts"]),
                        "to_room": h.get("to") or None,
                    })

                furniture = []
                skipped_placeholder = 0
                # furniture_info[].size 单位在两个源文件里不一致：
                # house_data_dict.json 用 cm，house_data_more.json 用 m（已用真实样本核实：
                # 前者窗帘 262cm/沙发 215cm 量级，后者射灯 0.1m 量级）。这里统一换算成 m。
                size_unit_divisor = 100.0 if src_name == "house_data_dict.json" else 1.0
                for f in room.get("furniture_info", []):
                    ftype = f.get("type", "")
                    if ftype.startswith(_FURNITURE_PLACEHOLDER_PREFIXES):
                        skipped_placeholder += 1
                        continue
                    raw_size = f.get("size")
                    furniture.append({
                        "id": f.get("id"),
                        "type": ftype,
                        "size_m": [round(v / size_unit_divisor, 4) for v in raw_size] if raw_size else None,
                        "position": f.get("position"),
                        "rotation_yaw_deg": _rotation_to_yaw_deg(f["rotation"], coordinate),
                    })

                out = {
                    "house_id": house_id,
                    "room_id": room_id,
                    "region_type": region_type,
                    "region_type_raw": raw_type,
                    "priority": priority,
                    "source_file": src_name,
                    "coordinate_raw": coordinate,
                    "unit": room.get("unit", "m"),
                    "area": room.get("area"),
                    "height": room.get("height"),
                    "boundary": floor_pairs,
                    "doors": doors,
                    "windows": windows,
                    "holes": holes,
                    "furniture_reference": furniture,
                    "furniture_placeholder_skipped": skipped_placeholder,
                }

                filename = f"{house_id}__{room_id}.json"
                (rooms_dir / filename).write_text(
                    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                report["rooms_written"].append({
                    "house_id": house_id, "room_id": room_id, "filename": filename,
                })

    return report


# ── Group 布局标注转换 ────────────────────────────────────────────────────────

def _find_room_file(house_id: str, room_id: str, rooms_written: list[dict]) -> str | None:
    for r in rooms_written:
        if r["house_id"] == house_id and r["room_id"] == room_id:
            return r["filename"]
    return None


def convert_layout_samples(
    group_map: dict[tuple[str, str], dict],
    region_map: dict[str, tuple[str, bool]],
    xasset_region_types: set[str],
    rooms_written: list[dict],
) -> dict:
    samples_dir = _OUT / "layout_samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads((_RAW / "house_sample_dict.json").read_text(encoding="utf-8"))

    report = {
        "total_samples": 0,
        "resolved": 0,
        "unresolved": 0,
        "group_code_gaps": {},  # "(type, region_type)" -> count
        "samples_written": [],
    }

    for legacy_room_type, buckets in data.items():
        region_type, _priority = _normalize_region_type(legacy_room_type)
        if region_type not in xasset_region_types:
            region_type, _is_mapped = region_map.get(legacy_room_type, (legacy_room_type, False))

        for area_bucket, samples in buckets.items():
            for idx, sample in enumerate(samples):
                report["total_samples"] += 1

                source_house = sample.get("source_house")
                source_room = sample.get("source_room")
                room_file = None
                if source_house and source_room and source_room != "none":
                    room_file = _find_room_file(source_house, source_room, rooms_written)

                resolved = room_file is not None
                if resolved:
                    report["resolved"] += 1
                else:
                    report["unresolved"] += 1

                placed_groups = []
                for g in sample.get("group", []):
                    gtype = g.get("type", "")
                    lookup = group_map.get((gtype, region_type))
                    code = lookup["code"] if lookup else None
                    if code is None:
                        key = f"({gtype}, {region_type})"
                        report["group_code_gaps"][key] = report["group_code_gaps"].get(key, 0) + 1

                    rotation = g.get("rotation", [0, 0, 0, 1])
                    yaw = _rotation_to_yaw_deg(rotation, "xzy")

                    placed_groups.append({
                        "group_code": code,
                        "group_type_raw": gtype,
                        "position": g.get("position"),
                        "rotation_yaw_deg": yaw,
                        "size": g.get("size"),
                        "size_min": g.get("size_min"),
                        "offset": g.get("offset"),
                        "obj_main": g.get("obj_main"),
                        "obj_type": g.get("obj_type"),
                        "role_assets": {},
                    })

                out = {
                    "legacy_room_type": legacy_room_type,
                    "region_type": region_type,
                    "area_bucket": area_bucket,
                    "resolved": resolved,
                    "source_house": source_house if resolved else None,
                    "source_room": source_room if resolved else None,
                    "source_room_file": room_file,
                    "placed_groups": placed_groups,
                }

                filename = f"{legacy_room_type}__{area_bucket}__{idx}.json"
                (samples_dir / filename).write_text(
                    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                report["samples_written"].append(filename)

    return report


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    region_map = _load_region_type_map()
    group_map = _load_group_type_map()
    xasset_region_types = _load_xasset_region_types()

    room_report = convert_rooms(region_map, xasset_region_types)
    layout_report = convert_layout_samples(
        group_map, region_map, xasset_region_types, room_report["rooms_written"]
    )

    conversion_report = {
        "rooms": {
            "total": room_report["total_rooms"],
            "region_type_mapped_counts": room_report["region_type_mapped_counts"],
            "region_type_unmapped_counts": room_report["region_type_unmapped_counts"],
        },
        "layout_samples": {
            "total": layout_report["total_samples"],
            "resolved": layout_report["resolved"],
            "unresolved": layout_report["unresolved"],
            "group_code_gaps": layout_report["group_code_gaps"],
        },
    }
    (_OUT / "conversion_report.json").write_text(
        json.dumps(conversion_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"rooms: {room_report['total_rooms']} converted -> {_OUT / 'rooms'}")
    print(
        f"layout_samples: {layout_report['total_samples']} converted "
        f"({layout_report['resolved']} resolved / {layout_report['unresolved']} unresolved) "
        f"-> {_OUT / 'layout_samples'}"
    )
    print(f"report -> {_OUT / 'conversion_report.json'}")


if __name__ == "__main__":
    main()
