# xasset/datasource/manager.py
"""数据源管理 —— 声明式获取，避免"每次临时找 URL"的重复劳动。

**解决的核心问题**（见 docs/data-workflow.md）：

    重构前：每次要图就临时找 URL → 试 → 失败 → 下次再试一遍
    重构后：来源写在 data/sources.json → 失败原因也记进去 → 下次直接跳过

三层职责：
- `data/sources.json`  ← 声明（谁维护：人）
- 本模块               ← 读取与状态记录（谁维护：代码）
- `tools/datasets/`    ← 实际下载与转换（谁维护：代码，待实现）
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


# 状态枚举（与 sources.json 里的 status 字段对应）
STATUS_NOT_FETCHED = "not_fetched"
STATUS_NOT_APPLIED = "not_applied"
STATUS_FETCHED = "fetched"
STATUS_UNREACHABLE = "unreachable"
STATUS_PARTIAL = "partially_verified"


@dataclass
class DataSource:
    """一个数据源。"""

    name: str
    kind: str = "dataset"
    scene: str = ""
    purpose: str = ""
    license: str = ""
    requires_approval: bool = False
    approval_url: str | None = None
    primary_url: str | None = None
    mirrors: list[str] = field(default_factory=list)
    status: str = STATUS_NOT_FETCHED
    notes: str = ""
    failure_notes: str = ""

    @property
    def usable_now(self) -> bool:
        """现在能否直接获取（不需审批、状态不是不可达）。"""
        return (
            not self.requires_approval
            and self.status != STATUS_UNREACHABLE
            and self.primary_url is not None
        )

    @property
    def needs_user_action(self) -> bool:
        """是否需要用户先做什么（申请 / 手动下载）。"""
        return (
            self.requires_approval
            or self.status == STATUS_UNREACHABLE
        )

    def urls(self) -> list[str]:
        """要尝试的 URL 顺序：主源在前，镜像在后。"""
        out = []
        if self.primary_url:
            out.append(self.primary_url)
        out.extend(self.mirrors)
        return out


class SourceCatalog:
    """数据源清单。"""

    def __init__(self, raw: dict) -> None:
        self._raw = raw
        self._sources: dict[str, DataSource] = {}
        self._test_images: dict[str, dict] = raw.get("test_images") or {}

        for name, spec in (raw.get("sources") or {}).items():
            self._sources[name] = DataSource(
                name=name,
                kind=spec.get("kind", "dataset"),
                scene=spec.get("scene", ""),
                purpose=spec.get("purpose", ""),
                license=spec.get("license", ""),
                requires_approval=bool(spec.get("requires_approval", False)),
                approval_url=spec.get("approval_url"),
                primary_url=spec.get("primary_url"),
                mirrors=list(spec.get("mirrors") or []),
                status=spec.get("status", STATUS_NOT_FETCHED),
                notes=spec.get("notes", ""),
                failure_notes=spec.get("failure_notes", ""),
            )

    # ── 查询 ────────────────────────────────────────────────

    def get(self, name: str) -> DataSource:
        if name not in self._sources:
            raise KeyError(
                f"数据源 '{name}' 未声明。请在 data/sources.json 里添加。"
            )
        return self._sources[name]

    def all_sources(self) -> list[DataSource]:
        return list(self._sources.values())

    def by_scene(self, scene: str) -> list[DataSource]:
        return [s for s in self._sources.values() if s.scene == scene]

    def fetchable_now(self) -> list[DataSource]:
        """现在就能直接下载的（无需审批、非不可达）。"""
        return [s for s in self._sources.values() if s.usable_now]

    def need_user_action(self) -> list[DataSource]:
        """需要用户先处理的（申请 / 手动下载）。"""
        return [s for s in self._sources.values() if s.needs_user_action]

    def test_images(self) -> dict[str, dict]:
        return dict(self._test_images)

    # ── 报告 ────────────────────────────────────────────────

    def status_report(self) -> str:
        """人读的状态报告。

        用纯 ASCII 标记（不用 emoji）——Windows 的 GBK 终端无法编码 emoji，
        会直接抛 UnicodeEncodeError。
        """
        lines = ["数据源状态：", ""]
        for s in self.all_sources():
            mark = {
                "fetched": "[OK]",
                "not_fetched": "[--]",
                "not_applied": "[AP]",
                "unreachable": "[XX]",
                "partially_verified": "[??]",
            }.get(s.status, "[??]")
            action = ""
            if s.requires_approval and s.status == STATUS_NOT_APPLIED:
                action = "  <- 需申请"
            elif s.status == STATUS_UNREACHABLE:
                action = "  <- 不可达，需替代方案"
            lines.append(f"{mark} {s.name:<20} {s.status:<20}{action}")

        need = self.need_user_action()
        if need:
            lines.append("")
            lines.append("需要你处理的：")
            for s in need:
                if s.requires_approval:
                    lines.append(f"  - {s.name}: 申请 {s.approval_url or '(见文档)'}")
                elif s.status == STATUS_UNREACHABLE:
                    lines.append(f"  - {s.name}: {s.failure_notes[:60]}")
        return "\n".join(lines)


def load_catalog(data_root: str | Path | None = None) -> SourceCatalog:
    """加载数据源清单。"""
    root = Path(data_root) if data_root else _DEFAULT_DATA_ROOT
    path = root / "sources.json"
    if not path.exists():
        raise FileNotFoundError(f"数据源清单不存在: {path}")
    with open(path, encoding="utf-8") as fh:
        return SourceCatalog(json.load(fh))
