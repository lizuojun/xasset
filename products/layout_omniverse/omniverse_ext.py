# products/layout-omniverse/omniverse_ext.py
"""
XAsset House Layout — Omniverse Extension Entry Point

To register as an Omniverse extension:
1. Place this directory inside your Kit app's exts/ folder
2. Update the extension.toml to point to this module
3. The extension loads a UI window with a "Generate" button

Architecture:
    UI panel  →  agent.layout_house(scene_vector)  →  adapter.write_layout_to_usd()
      ↑                                                   ↑
      └── scene_vector JSON (file path or inline)         └── output .usda
"""

import omni.kit.commands           # type: ignore
import omni.usd                     # type: ignore
import omni.ui as ui                # type: ignore


class XAssetLayoutWindow(ui.Window):
    """Omniverse extension window for house layout generation."""

    def __init__(self, title: str = "XAsset Layout"):
        super().__init__(title)
        self._scene_json_path = ""

    def _on_generate(self):
        try:
            from products.layout_omniverse.agent import layout_house
            from products.layout_omniverse.adapter import write_layout_to_usd

            import json, os

            if not self._scene_json_path:
                raise RuntimeError("scene.json path is empty")
            if not os.path.isfile(self._scene_json_path):
                raise RuntimeError(f"File not found: {self._scene_json_path}")

            with open(self._scene_json_path, "r", encoding="utf-8") as f:
                scene_vector = json.load(f)

            result = layout_house(scene_vector)

            usd_path = self._scene_json_path.replace(".json", ".usda")
            write_layout_to_usd(result, usd_path)

            stage = omni.usd.get_context().get_stage()
            if stage:
                _merge_sub_layer(stage, usd_path)

        except Exception as exc:
            print(f"[XAsset] Layout generation failed: {exc}")

    def build(self):
        with self.frame:
            with ui.VStack(spacing=8):
                ui.Label("House Layout Generator", height=24)

                self._scene_json_field = ui.StringField()
                self._scene_json_field.model.add_value_changed_fn(
                    lambda m: setattr(self, "_scene_json_path", m.get_value_as_string())
                )

                ui.Button("Generate", clicked_fn=self._on_generate)


def _merge_sub_layer(stage, usd_path: str) -> None:
    from pxr import Sdf
    root_layer = stage.GetRootLayer()
    sub_path = Sdf.Layer.CreateAnonymous().identifier
    root_layer.subLayerPaths.append(usd_path)


def on_startup():
    window = XAssetLayoutWindow()
    window.show()


def on_shutdown():
    pass
