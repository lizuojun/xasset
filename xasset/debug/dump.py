# xasset/debug/dump.py
"""Main debug dump entry point."""
import os
from xasset.debug.renderers.region_2d import render_region_2d
from xasset.debug.renderers.mesh_obj import export_mesh_obj
from xasset.debug.renderers.layout_2d import render_layout_2d


def _run(fn, out, path):
    fn(out, path)
    return [path]


def _run_layout(layout_out, ctx, d):
    path = os.path.join(d, "layout_plan.png")
    understand = ctx.stage_outputs.get("understand")
    if understand is None:
        return []
    render_layout_2d(layout_out, understand, path)
    return [path]


STAGE_RENDERERS = {
    "understand": [
        lambda out, ctx, d: _run(render_region_2d, out,
                                  os.path.join(d, "understand_regions.png")),
    ],
    "geometry": [
        lambda out, ctx, d: _run(export_mesh_obj, out,
                                  os.path.join(d, "geometry_mesh.obj")),
    ],
    "layout": [
        lambda out, ctx, d: _run_layout(out, ctx, d),
    ],
}


def debug_dump(ctx, output_dir: str = "debug/") -> list[str]:
    """
    Dump all available stage outputs to files.
    Returns list of generated file paths.
    ctx must have a .stage_outputs dict.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    for stage_key, renderers in STAGE_RENDERERS.items():
        out = ctx.stage_outputs.get(stage_key)
        if out is None:
            continue
        for renderer in renderers:
            try:
                paths = renderer(out, ctx, output_dir)
                generated.extend(paths)
            except Exception as e:
                print(f"[debug_dump] {stage_key} renderer failed: {e}")
    return generated
