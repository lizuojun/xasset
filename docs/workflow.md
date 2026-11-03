# 工作范式

> **怎么做事**：推进方法、代码组织、数据流程、测试规范。
> 更新：2026-09
> 关联：`docs/architecture.md`（做什么）

---

## 0. 要解决什么问题

**以前的情况**：每遇到新问题就临时探一次环境、临时写个脚本——知识散落在对话里，下次重新来一遍。

**现在**：把"推进一件事"的套路固定下来，任何新场景/新 Stage 都照着走。

---

## 1. 七步推进范式

任何新工作（新 Stage、新场景、新数据源、新算法），都走这七步：

```
① 定理想态  → 什么样算"做完了"（可量化的判据）
② 探环境    → 本地硬件/依赖/API 能不能支持
③ 定契约    → 输入输出先定死，两侧职责分清
④ 搭骨架    → 结构按 Artist 摆好，实现先占位
⑤ 备数据    → 测试素材 + 声明式来源 + 失败经验
⑥ 单点打通  → 先让最小链路能跑通（不求好）
⑦ 量化迭代  → 用指标驱动改进，不是凭感觉
```

| 步 | 产出 | 检查点（不满足就不往下走） |
|----|------|--------------------------|
| ① | 可量化的完成判据 | **能回答"怎么算做完了"** |
| ② | `docs/env-capabilities.json` | 关键能力有明确"支持/不支持/有条件" |
| ③ | `pipeline/schemas/*.py` | 输入输出能表达多上游依赖 |
| ④ | Stage 类 + Protocol 接口 | 两侧可替换、有迭代入口 |
| ⑤ | `data/sources.json` + 测试素材 | 失败经验已记录 |
| ⑥ | 端到端脚本 | **跑出一张真实结果图** |
| ⑦ | 指标 + 基线 | 有可比较的数字 |

### 自查清单（做任何新工作前）

```
[ ] 我能说出"什么算做完了"吗？
[ ] 环境能支持吗？查过 env-capabilities 吗？
[ ] 输入输出契约定了吗？
[ ] 结构是 Artist 形状吗（两侧可换/有迭代入口）？
[ ] 有测试素材吗？来源记录了吗？
[ ] 能跑出真实结果吗？
[ ] 有可比较的数字吗？
```

---

## 2. 代码组织

### 2.1 目录职责

```
xasset/
├── pipeline/          ← 框架与编排
│   ├── stage.py           Stage 协议
│   ├── pipeline.py        执行器
│   ├── schemas/           【契约】Stage 间唯一数据协议
│   └── stages/            各 Stage 实现（只编排，不含场景知识）
│
├── scene/             ← 【场景知识】配置的唯一入口
├── tools/             ← 主链路算法（参与生成）
│   ├── geometry/          几何算法
│   ├── constraint/        【硬约束】+ 国标常数
│   ├── quality/           【软规则】
│   ├── io/                图片读取（I/O）
│   └── datasets/          数据集下载与转换（不入运行时）
│
├── viz/               ← 可视化（产品与调试共用，不参与生成）
├── datasource/        ← 数据源管理
├── llm/               ← LLM 抽象
├── debug/             ← 纯开发期调试
│
data/<scene>/          ← 【场景数据】
├── scene.json             场景定义（区域词表、面积先验）
├── rules.json             软规则清单
└── converted/             转换后的历史数据
```

### 2.2 判断新功能放哪

| 问题 | 放哪 |
|------|------|
| 它参与"生成场景数据"吗？ | 是 → `tools/` |
| 它是给人看的图/指标吗？ | 是 → `viz/` |
| 它是某场景的业务参数吗？ | 是 → `data/<scene>/*.json` |
| 它只在开发时用？ | 是 → `debug/` 或 `tools/datasets/` |
| 它是 Stage 的编排逻辑？ | 是 → `pipeline/stages/` |

**一句话**：`tools/` 是"算"，`viz/` 是"看"，`data/` 是"知识"，`debug/` 是"临时"。

### 2.3 场景知识必须外置（核心原则）

**问题实例（曾经犯过）**：面积先验在 `scene_understand.py` 和 `rules.json` 里**各写一份**，改一处不同步；加 urban 要再复制一份。

**解决**：统一到 `data/<scene>/scene.json`

```python
from xasset.scene import load_scene_config
cfg = load_scene_config(scene_type)
area = cfg.typical_area(region_type)      # 唯一来源
```

**Stage 代码里不出现任何具体数值或区域名。** 有测试保证：
```python
def test_area_prior_is_not_hardcoded_in_stage():
    assert "_TYPICAL_AREA" not in src
```

### 2.4 新增场景 = 零代码改动

| 步骤 | 改代码吗 |
|------|---------|
| 1. 建 `data/<scene>/scene.json` | ❌ |
| 2. 建 `data/<scene>/rules.json` | ❌ |
| 3. 若有专属硬约束，加国标常数 | 🟡 加数据 |
| 4. 若需专属 Stage，新建文件并注册 | ✅ 只加不改 |

### 2.5 不要做的事

| 反模式 | 为什么不行 |
|--------|-----------|
| 在 Stage 里硬编码场景参数 | 加场景要改代码 |
| 把渲染代码写进 Stage | 测试 Stage 时要装 matplotlib |
| 为每个场景复制一份 Stage | 改一处要改 N 处 |
| 新建一套"skill"概念 | 与 Artist 的两种抽象冲突 |
| 把数据集下载放进运行时依赖 | 违反"clone 即跑" |

---

## 3. 数据流程

### 3.1 三层职责

| 层 | 位置 | 谁维护 |
|----|------|--------|
| **声明** | `data/sources.json` | 人（可读可改） |
| **管理** | `xasset/datasource/` | 代码 |
| **执行** | `tools/datasets/` | 代码（待实现） |

**核心原则：URL 绝不写进脚本。** 要加数据源，改 JSON。

### 3.2 获取顺序

```
1. 读 sources.json 找 source
2. requires_approval=true 且未申请 → 提示用户，不盲目重试
3. 按 primary_url 尝试，失败依次试 mirrors
4. 成功 → 记录路径
5. 失败 → 原因写回 failure_notes  ← 下次不用重试
```

### 3.3 失败经验的记录（关键）

`sources.json` 里已记录的真实教训：

```json
"wikipedia_floorplans": {
  "status": "unreachable",
  "failure_notes": "盲猜的 thumb URL，哈希前缀猜不中，返回 400",
  "root_cause": "Wikimedia thumb 路径含精确哈希前缀，必须走 API 取真实 URL"
}
```

**不只记现象，要记根因**——否则下次还是踩同一个坑。有测试保证这条记录不被删。

### 3.4 本地管理

```
external/<name>/                ← 原始数据（不进 git）
data/<scene>/
├── scene.json                  ← 场景定义
├── rules.json                  ← 软规则
└── converted/<name>/           ← 内化后的结果（可进 git）
data/test_images/               ← 测试图（可进 git）
```

**判断标准**：
- 能通过脚本重新获取 → `external/`（不跟踪）
- 我们生成的、体积可控 → `data/`（跟踪）

### 3.5 各场景数据获取要点

| 场景 | 数据源 | 有真实尺寸 | 规范依据 | 难度 |
|------|--------|-----------|---------|------|
| **室内 house** | 自有 99 套<br>RPLAN（需申请）<br>Structured3D（需申请）<br>CubiCasa5K | ✅ 自有<br>✅ RPLAN<br>❌ CubiCasa | GB 50096（22 条） | ⭐ 低 |
| **城市 urban** | OSM（矢量）<br>SpaceNet | ✅ 经纬度 | GB 50180、CJJ 37（待查） | ⭐⭐ 中 |
| 乡村 rural | GB/T 50445（待查） | ❌ | 待查 | ⭐⭐⭐ |
| 山林 mountain | DEM、GlobeLand30 | 🟡 | 无强制规范 | ⭐⭐⭐⭐ |
| 海洋 ocean | GEBCO、OSM 岸线 | 🟡 | 强专业 | ⭐⭐⭐⭐ |
| 沙漠 desert | DEM、地表覆盖 | 🟡 | 无强制规范 | ⭐⭐⭐⭐ |

**每个场景都要回答三个问题**：
1. 规范怎么说（硬约束）
2. 哪里能验证（测试集）
3. 自己的真实数据在哪（软规则阈值）

### 3.6 找测试图的正确方法（踩过的坑）

```bash
# 1. 用 API 搜索页面
curl "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=floor%20plan&format=json"
# 2. 查页面上的文件
curl ".../titles=Floor%20plan&prop=images&format=json"
# 3. 用文件名取真实下载地址（关键）
curl ".../titles=File:Sample%20Floorplan.jpg&prop=imageinfo&iiprop=url&format=json"
# 4. 下载（必须带 User-Agent）
curl -H "User-Agent: xasset/0.1" -o sample.jpg "<真实URL>"
```

**已知不可行**：盲猜 wikimedia thumb URL（哈希前缀）、盲猜 GitHub raw 路径、GitHub API（速率限制）

---

## 4. 测试流程：三层分离

| 层 | 位置 | 依赖 | 行为 |
|----|------|------|------|
| **单元测试** | `tests/**/test_*.py` | 无外部数据 | 永远可跑，CI 必过 |
| **集成测试** | `tests/integration/` | 真实图片/数据集 | **无数据时 skip** |
| **端到端脚本** | `scripts/` | 手工运行 | 人工看结果 |

### 为什么集成测试要 skip 而不是 fail

```python
@pytest.fixture
def test_image() -> Path:
    if not TEST_IMAGES_DIR.exists():
        pytest.skip("测试图片目录不存在")
    ...
```

**效果**：`pytest` 在任何机器上都能跑绿。如果改成 fail，新人 clone 后立刻看到红叉，会误以为代码坏了。

### 运行方式

```bash
pytest                          # 全部（集成测试自动 skip）
pytest -m "not integration"     # 只跑单元
python scripts/run_understand.py data/test_images/xxx.png   # 端到端
```

---

## 5. 环境能力

| 资源 | 结论 |
|------|------|
| CPU / 内存 | 16 核 / 63.7 GB — 充裕 |
| GPU | RTX 2060 SUPER **8GB** — 可跑 7B 量化，**多模态受限** |
| Ollama | 已装，有 llama3.2:3b + nomic-embed-text |
| Anthropic 代理 | 端点存在，**但未配 auth token** |
| torch / transformers | **未安装** |

**能力判断**：
- ✅ 几何算法、阈值分割、小 LLM（3B）
- 🟡 云端 LLM（需配 key）、本地 SAM（需装 torch）
- ❌ **本地多模态大模型（8GB 不够）** → 看图走云端 API

**重新探测**：`python scripts/probe_env.py`
**完整清单** → `docs/env-capabilities.json`

---

## 6. 任务验收

**每个任务必须有可量化的判据**，否则会出现"永远做不完"或"不知道做完了"。

写法样板见 `docs/stages/understand-acceptance.md`：
- 8 个维度，每个都有「当前基线 → 目标」
- **"未测"也是一种状态**——它告诉你下一步该做什么

---

## 7. 一句话记住

> **先定"什么算完"，再探"能不能做"，然后"先跑通再跑好"。**
>
> 每做一件新事，都问：**这次的产出能不能被下次复用？**
