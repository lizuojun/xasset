# xasset/tools/datasets/

> **状态：未实现。** 本文件只记录规划，避免后续不知道这块该长什么样。

## 职责

公开数据集的**获取与转换**：把外部数据集标注变成符合 `pipeline/schemas/` 契约的内部数据。

## 为什么现在不实现

按 `research/public-datasets-survey/README.md` 第 7 节：

> 现在 `understand` 的视觉路线还没定，不知道最终要什么标注粒度。
> 贸然下载转换，很可能发现格式不对、要重做。

## 规划的脚本

| 脚本 | 职责 | 前置条件 |
|------|------|---------|
| `fetch_cubicasa5k.py` | 从 Zenodo 下载并解压 | 无需申请 |
| `fetch_osm.py` | 按区域从 Overpass API 拉矢量 | 无需申请 |
| `fetch_rplan.py` | 解压已审批下载的包 | **需先通过申请** |
| `fetch_structured3d.py` | 解压已审批下载的包 | **需先通过申请** |
| `convert_cubicasa5k.py` | SVG 多边形 → `SceneRegion` | 契约稳定 |
| `convert_osm.py` | GeoJSON → `SceneRegion` | urban 契约细化 |
| `common.py` | 共享：坐标变换、尺度推断、类别映射 | — |

## 设计约束

1. **幂等**：同一输入跑两次，输出必须一致
2. **原始数据落 `external/<name>/`，内化结果落 `data/<scene>/converted/`**
3. **转换后必须跑硬约束验证**，输出违规率（见 `docs/workflow.md` 第二节）
4. **类别映射表单独放**：数据集的类别词表 → 我们的 `region_type`，映射关系是领域知识，要能单独维护

## 关键难点（提前记录）

### 尺度推断

CubiCasa5K / RPLAN 给的是**像素坐标，没有真实米制尺寸**。

可选方案：
- 用标准门宽（0.9m）反推像素/米比例
- 用房间类型的典型面积反推
- 若数据集本身带尺寸标注则直接读取

**这决定了能否用这些数据补充面积阈值统计。**

### 类别词表映射

CubiCasa5K 有 80+ 类别，我们有 ~11 个 `region_type`。需要设计与维护一张映射表。
