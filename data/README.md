# data/

场景样本数据。按场景类型分子目录（与 `docs/pipeline-map.md`/xasset 内部 `scene_type` 词汇一致：`house` / `urban` / `wild`）。

## 约定

- 原始数据放 `<scene>/raw/`，只读拷贝，不加工——转换脚本的输入，永远可以重新生成。
- 映射表放 `<scene>/mapping/`，JSON 文件 + README 说明设计依据；跟转换脚本的 Python 代码分离，方便评审和以后单独调整映射关系而不改代码。
- 转换结果放 `<scene>/converted/`，包含转换后的样本文件和一份 `conversion_report.json`（转换统计：成功/跳过数、映射覆盖缺口清单）。
- 转换脚本 `<scene>/convert.py`，一次性/可重跑，不修改 `xasset/` 包本身。

## 子目录

| 目录 | 状态 | 说明 |
|------|------|------|
| `house/` | 有数据 | 11 户真实户型、99 个房间几何+家具、128 条 Group 布局标注，转换自历史项目数据。详见 `house/README.md`。 |
| `urban/` | 空壳 | 暂无数据源，`docs/pipeline-map.md` 里 urban 场景的 geometry/layout 仍是 P0 缺口，等有数据再填。 |
| `wild/` | 空壳 | 同上，wild 场景暂无数据源。 |

## 与 research/ 的关系

`data/` 是样本数据本体（可被训练/验证代码直接消费），`research/learned-layout-with-hard-constraints/README.md` 是数据驱动布局方案的架构讨论文档——本目录第一批 house 数据就是为了支撑那份文档里规划的训练/验证需求而转换的。
