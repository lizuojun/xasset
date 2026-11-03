# tests/conftest.py
"""pytest 全局配置 —— 实现三层测试分离。

## 三层测试的约定（见 docs/data-workflow.md）

| 层 | 位置 | 依赖 | 特点 |
|----|------|------|------|
| **单元测试** | `tests/**/test_*.py` | 无外部数据 | 永远可跑，CI 必过 |
| **集成测试** | `tests/integration/` | 需要真实图片/数据集 | **无数据时自动 skip** |
| **端到端脚本** | `scripts/` | 手工运行 | 人工看结果 |

**关键**：集成测试缺数据时必须 **skip 而非 fail**——
这样 `pytest` 在任何机器上都能跑通，不会因为没下载数据集就红。
"""
from __future__ import annotations

from pathlib import Path

import pytest

# 项目根
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TEST_IMAGES_DIR = DATA_DIR / "test_images"
EXTERNAL_DIR = PROJECT_ROOT / "external"


def pytest_configure(config):
    """注册自定义标记。"""
    config.addinivalue_line(
        "markers", "integration: 集成测试（需要真实数据，无数据时跳过）"
    )
    config.addinivalue_line(
        "markers", "slow: 较慢的测试"
    )


# ── 集成测试用的 fixture（无数据时 skip）──────────────────────────────

@pytest.fixture
def test_image() -> Path:
    """任意一张测试用户型图。

    找不到时 skip 而不是 fail —— 这是三层分离的核心约定。
    """
    if not TEST_IMAGES_DIR.exists():
        pytest.skip(f"测试图片目录不存在: {TEST_IMAGES_DIR}")

    imgs = [
        p for p in TEST_IMAGES_DIR.iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
    ]
    if not imgs:
        pytest.skip(
            f"{TEST_IMAGES_DIR} 下没有图片。"
            f"把户型图放进去即可，或参考 data/sources.json 的 test_images 段。"
        )
    return imgs[0]


@pytest.fixture
def external_dataset():
    """某个已下载的外部数据集。用法：external_dataset("cubicasa5k")"""
    def _get(name: str) -> Path:
        p = EXTERNAL_DIR / name
        if not p.exists():
            pytest.skip(
                f"外部数据集未下载: {p}。"
                f"数据源声明见 data/sources.json。"
            )
        return p
    return _get
