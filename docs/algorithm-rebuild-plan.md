# 算法重做：Phase 1 执行记录（已完成）

> 状态：已完成（2026-09）
> 本文档是「算法全面重做」**第一阶段（清理 + 骨架 + 分支重置）的执行记录**，不再承载算法形态的设计。
> 当前算法形态的设计与 Stage 接口规范，见 **`docs/stage-paradigm-design.md`**（Artist 范式）。
>
> 关联文档：
> - `docs/stage-paradigm-design.md` —— Artist 范式（当前算法形态权威）
> - `docs/pipeline-map.md` —— 六层管线当前全景
> - `research/unified-scene-pipeline/README.md` —— 调研背景与术语来源

---

## 一句话背景

保持架构外壳不变（六层 Stage、三场景、Stage 接口、阶段产物 schema、先插件后整体服务、三分支并行），把每一层内部的算法实现从「规则式确定性算法」替换为「LLM 驱动的生成式编排」——后来演进并定型为 **Artist 范式**（LLM × 边界约束 迭代收敛），见 `stage-paradigm-design.md`。

---

## 已完成的决策

| 决策 | 结论 |
|------|------|
| 工具位置 | 独立 `tools/` 层（几何 / 约束），与 pipeline 主干分离 |
| `services/sample_search.py` | 一并清理，检索随算法一起重做 |
| `services/placement_zone.py` | 一并清理 |
| `config/loader.py` / `config/schemas.py` | 清理（GroupDefinition 加载器未接入 Stage） |
| Phase 1 git 操作 | 由 agent 执行 |
| 分支 | 三分支重置到干净基底，保留历史（不 reset --hard 销毁） |

---

## 已完成的代码变更

### 新增

| 位置 | 内容 |
|------|------|
| `llm/provider.py` | `LLMProvider` 抽象 + `LLMRequest` / `LLMResponse` + `StubLLMProvider` |
| `llm/orchestrate.py` | `StageLLMSpec` / `LLMStageOrchestrator` / `StubStageOrchestrator` |
| `tools/geometry/` | 三角剖分、UV 映射、多边形归一化（自 `pipeline/utils/` 迁入） |
| `tools/constraint/` | `ConstraintSet` / `ConstraintRule` / `ValidationResult`（校验门） |

> 注：`llm/orchestrate.py` 的「每阶段 LLM 编排」角色在 Artist 范式下已调整为「Stage 内部自调用」，编排逻辑下沉到各 Stage 内部，见 `stage-paradigm-design.md` 第 5 节。

### 清理

| 位置 | 清理内容 |
|------|---------|
| `stage/understand/scene_understand.py` | 词表归一化 `_ROOM_TYPE_PRIORITY_MAP`、门连通规则、手写字段映射（保留阶段产物 schema） |
| `stage/geometry/house/mesh_build.py` | `MeshBuilderService` 规则式网格构建（保留阶段产物 schema） |
| `stage/layout/house/compose.py` | 组合布局规则逻辑（保留阶段产物 schema） |
| `stage/layout/house/room_decompose.py` | 615 行规则算法（删除） |
| `stage/layout/house/groups.json` | 29 组布局配置（删除） |
| `pipeline/utils/` | `mesh_utils.py` / `uv_utils.py` / `vector_normalize.py`（迁入 `tools/geometry/`） |
| `services/sample_search.py` / `placement_zone.py` | 删除 |
| `config/loader.py` / `schemas.py` | 删除 |
| `debug/renderers/house/decompose_2d.py` | 删除 |
| `products/cli/zone_debug.py` | 删除 |
| 相关 tests | 删除算法专用测试，保留框架测试 |

### 保留不动（框架契约）

`pipeline/stage.py` / `registry.py` / `pipeline.py` / `context.py`、六层 Stage 类名与 `run(ctx)` 签名、各层阶段产物 schema。

---

## 分支结果

`master` / `xasset-urban` / `xasset-outdoor` 三分支重置到同一个干净基底（清理 commit），工作区干净、尚未分叉；未合并的 `feat/unify-door-rendering` 分支已删除。

---

## 后续

算法的具体形态（每层 Stage 的 LLM 与边界约束怎么协作、Stage 接口怎么改、产品形态怎么包装）**已不再由本文档承载**，全部见 `docs/stage-paradigm-design.md`。
