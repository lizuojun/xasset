# xasset/tools/quality/rules.py
"""软规则评估 —— 把"什么样的结果算好"变成可计算的确定性检查。

设计依据见 docs/iteration-convergence.md 第 4 节：
- 软规则清单是**场景业务知识**，放在配置文件里（如 data/house/rules.yaml），
  领域专家可直接编辑，不需要改 Python 代码。
- 配置只声明"查什么 + 阈值"；具体的几何计算在本文件实现。
- 规则分两级：scene（全场景通用）+ region_type（区域专属）。

为什么不做成 LLM 打分：
- LLM 打分不可复现、不可解释、无法调参；
- 显式规则能让领域专家直接参与，也便于回归测试。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class RuleLevel(str, Enum):
    REQUIRED = "required"       # 必须满足
    PREFERRED = "preferred"     # 尽力而为


@dataclass
class RuleSpec:
    """一条软规则的配置声明。"""

    rule_id: str
    level: RuleLevel
    desc: str = ""
    weight: int = 1
    params: dict = field(default_factory=dict)


@dataclass
class RuleViolation:
    """一次软规则不满足。"""

    rule_id: str
    level: RuleLevel
    message: str
    region_id: str | None = None


@dataclass
class RuleReport:
    """软规则评估结果。"""

    violations: list[RuleViolation] = field(default_factory=list)

    @property
    def required_violations(self) -> list[RuleViolation]:
        return [v for v in self.violations if v.level is RuleLevel.REQUIRED]

    @property
    def preferred_violations(self) -> list[RuleViolation]:
        return [v for v in self.violations if v.level is RuleLevel.PREFERRED]

    @property
    def ok(self) -> bool:
        """没有 required 级违规即视为通过（preferred 只影响优化方向）。"""
        return not self.required_violations

    @property
    def score(self) -> float:
        """简单可比的代理分数：required 违规重罚，preferred 轻罚。

        注意：这只是**排序用的**代理分数，不是"美观程度"。真正的判据是
        required 是否清零 + preferred 违规是否在减少。
        """
        score = 100.0
        score -= 25.0 * len(self.required_violations)
        score -= sum(1 for v in self.violations if v.level is RuleLevel.PREFERRED) * 2.0
        return max(0.0, score)


# 规则实现签名： (region, context) -> 违规消息 or None
RuleImpl = Callable[[Any, dict], "str | None"]


class RuleRegistry:
    """rule_id → 实现函数的映射。

    配置里只写 id 和阈值，具体几何计算注册在代码中。这样：
    - 领域专家能读改配置
    - 开发者能优化实现
    两者解耦。
    """

    def __init__(self) -> None:
        self._impls: dict[str, RuleImpl] = {}

    def register(self, rule_id: str, impl: RuleImpl) -> "RuleRegistry":
        self._impls[rule_id] = impl
        return self

    def get(self, rule_id: str) -> RuleImpl | None:
        return self._impls.get(rule_id)

    def known(self) -> set[str]:
        return set(self._impls)


class QualityConfig:
    """加载并持有某个场景的软规则配置。"""

    def __init__(self, config: dict, registry: RuleRegistry) -> None:
        self._config = config
        self._registry = registry
        self.scene = config.get("scene", "")
        self._scene_rules = [self._parse(r) for r in config.get("scene_rules", [])]
        self._region_rules: dict[str, list[RuleSpec]] = {}
        self._typical_area: dict[str, tuple[float, float]] = {}

        for region_type, block in (config.get("region_rules") or {}).items():
            self._region_rules[region_type] = [
                self._parse(r) for r in block.get("rules", [])
            ]
            area = block.get("typical_area_m2")
            if area and len(area) == 2:
                self._typical_area[region_type] = (float(area[0]), float(area[1]))

    @classmethod
    def load(cls, path: str | Path, registry: RuleRegistry) -> "QualityConfig":
        with open(path, encoding="utf-8") as fh:
            return cls(json.load(fh), registry)

    @staticmethod
    def _parse(raw: dict) -> RuleSpec:
        return RuleSpec(
            rule_id=raw["id"],
            level=RuleLevel(raw.get("level", "preferred")),
            desc=raw.get("desc", ""),
            weight=int(raw.get("weight", 1)),
            params=raw.get("params") or {},
        )

    def typical_area(self, region_type: str) -> tuple[float, float] | None:
        return self._typical_area.get(region_type)

    def rules_for(self, region_type: str) -> list[RuleSpec]:
        """某区域类型适用的全部规则（场景通用 + 区域专属）。"""
        return list(self._scene_rules) + list(self._region_rules.get(region_type, []))

    def evaluate(self, regions: list) -> RuleReport:
        """对一组区域评估全部软规则。

        regions: SceneRegion 列表（pydantic 契约）
        """
        report = RuleReport()
        for region in regions:
            ctx = {
                "typical_area": self.typical_area(region.region_type),
                "all_regions": regions,
            }
            for spec in self.rules_for(region.region_type):
                impl = self._registry.get(spec.rule_id)
                if impl is None:
                    # 配置声明了但代码未实现 —— 跳过而不是崩，便于配置先行
                    continue
                try:
                    msg = impl(region, {**ctx, "params": spec.params})
                except Exception as exc:  # 规则实现本身出错不应打断整轮评估
                    msg = f"规则执行出错: {exc}"
                if msg:
                    report.violations.append(
                        RuleViolation(
                            rule_id=spec.rule_id,
                            level=spec.level,
                            message=msg,
                            region_id=getattr(region, "region_id", None),
                        )
                    )
        return report
