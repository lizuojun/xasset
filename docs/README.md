# xasset 文档索引

> **不知道看哪份？先看这一页。**
> 更新：2026-09

---

## 我想……

| 我想知道…… | 看这里 |
|------------|--------|
| **系统是怎么设计的、为什么这么设计** | [`architecture.md`](architecture.md) |
| **怎么在这个项目里做事**（推进/代码/数据/测试） | [`workflow.md`](workflow.md) |
| **现在做到哪了、下一步做什么** | [`task-progress.md`](task-progress.md) |
| **每个 Stage 的输入输出字段是什么** | [`stage-io-contract-spec.md`](stage-io-contract-spec.md) |
| **迭代怎么收敛、"不够好"怎么判定** | [`iteration-convergence.md`](iteration-convergence.md) |
| **硬约束的数值依据是哪条国标** | [`constraint-standard-references.md`](constraint-standard-references.md) |
| **本机能不能跑某个模型** | [`env-capabilities.json`](env-capabilities.json) |
| **understand 怎么做、做到什么程度算完** | [`stages/`](stages/) |

---

## 文档清单

| 文档 | 讲什么 | 什么时候看 |
|------|--------|-----------|
| **architecture.md** | 理念（Artist）、六层 Stage、六场景契约、五条原则 | 理解设计意图 |
| **workflow.md** | 七步推进法、代码组织、数据流程、测试规范、环境能力 | 动手做事前 |
| **task-progress.md** | 进度快照、各 Stage 状态、下一步建议 | 想知道进展 |
| **stage-io-contract-spec.md** | 六层契约的完整字段定义 | 写 Stage / 改契约 |
| **iteration-convergence.md** | 三类"不满意"、软规则、收敛判据、迭代 trace | 设计 Stage 内部逻辑 |
| **constraint-standard-references.md** | 22 条国标依据（带条款号） | 定硬约束数值 |
| **env-capabilities.json** | 硬件 / 依赖 / API 支持情况 | 判断可行性 |
| **stages/understand-vision-route.md** | understand 的四层架构、几何后处理设计 | 做 understand |
| **stages/understand-acceptance.md** | understand 的 8 维验收标准与基线 | 判断 understand 做完了吗 |

---

## 调研文档（research/）

| 文档 | 讲什么 |
|------|--------|
| `foundation-models-multimodal/` | 主流大模型/多模态能力边界（写 prompt 前对照） |
| `public-datasets-survey/` | 公开数据集候选、可转性、许可 |
| `scene-recognition-from-raw-input/` | 输入识别技术选型（图片/文字/图纸各用什么模型） |

---

## 常用命令

```bash
# 跑测试（集成测试缺数据时自动 skip）
pytest

# 端到端：一张图 → 轮廓 → 对比图
python scripts/run_understand.py data/test_images/sample_floorplan.jpg

# 探测本地环境能力
python scripts/probe_env.py
```

---

## 文档维护原则

为避免文档膨胀（曾一度达到 17 份、3675 行，接近代码 70%）：

| 原则 | 说明 |
|------|------|
| **按用途分，不按话题分** | 同一用途的内容合并到一份，不因为"讨论过"就新建 |
| **一份文档只回答一类问题** | 想查进度就只翻 task-progress，不掺杂设计 |
| **过时的直接删** | 历史记录留在 git 里，不留在 docs 里 |
| **能压缩就压缩** | 8 个指标不需要 200 行 |

**新文档加进来之前先问：这个内容能不能并进现有文档？**
