# xasset/services/mesh.py
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlacementSlot:
    surface_type: str            # "top" | "back" | "front"
    center: list[float]          # [x, y, z] in object local space, unit cm
    size: list[float]            # [w, h, d] available area
    height: float                # height above bbox.min.y


@dataclass
class PlacementZones:
    top: list[PlacementSlot]
    back: list[PlacementSlot]
    front: list[PlacementSlot]


def _zones_to_dict(zones: PlacementZones) -> dict:
    def slots(lst):
        return [
            {"surface_type": s.surface_type, "center": s.center,
             "size": s.size, "height": s.height}
            for s in lst
        ]
    return {"top": slots(zones.top), "back": slots(zones.back), "front": slots(zones.front)}


def _dict_to_zones(d: dict) -> PlacementZones:
    def slots(lst):
        return [PlacementSlot(**item) for item in lst]
    return PlacementZones(
        top=slots(d.get("top", [])),
        back=slots(d.get("back", [])),
        front=slots(d.get("front", [])),
    )


class MeshService:
    """Synchronous mesh analysis service.

    Checks AssetDefinition.computed_features for cached PlacementZones.
    On cache miss, computes via GLM adapter (if geometry is available).
    Updates asset.computed_features in-memory; caller must commit to DB.
    """

    def get_placement_zones(
        self,
        asset,
        force_recompute: bool = False,
    ) -> PlacementZones:
        if not force_recompute and asset.computed_features:
            cached = asset.computed_features.get("placement_zones")
            if cached:
                return _dict_to_zones(cached)

        zones = self._compute(asset)

        features = dict(asset.computed_features or {})
        features["placement_zones"] = _zones_to_dict(zones)
        asset.computed_features = features

        return zones

    def _compute(self, asset) -> PlacementZones:
        """Compute placement zones from mesh geometry.
        Returns empty zones if no geometry is available."""
        raw_data = asset.raw_data or {}
        geometry_url = raw_data.get("geometry_url", "")
        if not geometry_url or not geometry_url.startswith("local://"):
            return PlacementZones(top=[], back=[], front=[])
        return self._compute_from_obj(geometry_url, asset.object_type or "")

    def _compute_from_obj(self, geometry_url: str, object_type: str) -> PlacementZones:
        """Use GLM adapter to compute placement zones from OBJ file."""
        try:
            _ref = Path(__file__).parent.parent.parent / "ref"
            if str(_ref) not in sys.path:
                sys.path.insert(0, str(_ref))
            from Furniture.glm_interface import glm_read_obj
            from Furniture.glm_shape import glm_shape_obj
        except ImportError:
            return PlacementZones(top=[], back=[], front=[])

        local_path = geometry_url.removeprefix("local://")
        model = glm_read_obj(local_path)
        if not model:
            return PlacementZones(top=[], back=[], front=[])

        decor_bot, decor_bak, decor_frt, ratio = glm_shape_obj(model, type=object_type)
        return PlacementZones(
            top=self._slots_from_glm(decor_bot, "top"),
            back=self._slots_from_glm(decor_bak, "back"),
            front=self._slots_from_glm(decor_frt, "front"),
        )

    def _slots_from_glm(self, decor: dict, surface_type: str) -> list[PlacementSlot]:
        slots = []
        for height_key, items in decor.items():
            for item in items:
                if len(item) >= 7:
                    slots.append(PlacementSlot(
                        surface_type=surface_type,
                        center=[item[0], item[1], item[2]],
                        size=[abs(item[3] - item[0]), 0, abs(item[5] - item[2])],
                        height=float(height_key),
                    ))
        return slots
