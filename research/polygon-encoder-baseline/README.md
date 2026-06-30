# 多边形 Encoder 成熟基线 & 墙面特征编码方案

**问题**：墙体分段（w/d/q）、门、窗这些结构化特征，已有成熟的 polygon encoder baseline 吗？怎么把这些简单向量 encode 进神经网络做布局预测？

---

## 1. 成熟的多边形 Encoder Baseline

### 1.1 建筑/户型方向

| 模型 | 输入 | 编码方式 | 输出 | 适用性 |
|------|------|---------|------|--------|
| **Graph2Plan** (Hu et al., 2020) | 房间 bubble diagram（图） + 建筑边界 | GNN (GraphSAGE) → 卷积 layout decoder | 房间多边形坐标 | ✅ 最接近我们场景：graph 输入，矢量输出 |
| **House-GAN** (Nauata et al., 2020) | bubble graph + noise | 图卷积 → CNN decoder | 户型像素图 → 后处理矢量化 | ⚠️ 输出是像素，需要后处理 |
| **HouseDiffusion** (Shabani et al., 2023) | 图约束 + 扩散模型 | 扩散去噪 | 房间边界框 | ✅ 图条件 + 生成式 |
| **HouseGAN++** (Nauata et al., 2021) | bubble graph | 关系网络 + 生成式 | 户型图 | 改进版，约束更强 |
| **FloorNet** (Liu et al., 2018) | 户型图像 | 多分支 CNN | 墙/门/窗矢量 | 是 image→vector，反向 |

### 1.2 通用多边形方向

| 模型 | 编码方式 | 要点 |
|------|---------|------|
| **PolygonRNN** (Acuna et al., 2018) | CNN backbone + RNN decoder | RNN 逐顶点生成多边形，适用标注/分割 |
| **PolyGen** (Nash et al., 2020) | Transformer encoder + autoregressive decoder | 自回归生成 mesh 多边形面；顶点+面分两阶段 |
| **PolyDiffuse** (Chen et al., 2023) | 扩散模型 | 多边形顶点去噪生成 |
| **FloorPlanTransformer** (Para et al., 2021) | Transformer | 房间关系作为 attention graph，直接输出墙线端点 |

### 1.3 图编码器通用基线

| 编码器 | 适用数据类型 | 要点 |
|--------|------------|------|
| **GCN** (Kipf & Welling, 2017) | 图节点 + 邻接矩阵 | 最基础；卷积聚合邻居特征 |
| **GraphSAGE** (Hamilton et al., 2017) | 大规模图 | 采样邻居，inductive 推理 |
| **GAT** (Velickovic et al., 2018) | 异构边重要度 | 注意力机制区分边权重 |
| **GIN** (Xu et al., 2019) | 图分类/回归 | 表达能力接近 WL test |
| **Transformer (Vaswani et al., 2017)** | 序列/集合 | 全局注意力，适合我们的有序墙段序列 |

---

## 2. 我们的数据特点分析

经过 `room_decompose` 后，每个房间的输出是一个**边界遍历序列**，包含三种 segment：

```
房间 A:
  wall  (w=2.0, d=5.0, q=0.33) → 门 (w=1.0, type=入户) → wall (w=1.5, d=3.8, q=0.25) → ...
  wall  (w=3.5, d=5.0, q=0.50) → 窗 (w=2.0, d=7.0, q=0.33) → wall (w=1.5, d=5.0, q=0.25) → ...
```

每个 segment 有：
- **几何**：`(p0, p1, length, inward_normal, corner_type)`
- **语义**：`(seg_type: wall|door|window)`
- **分析**：`(depth_profile[], wall_quality, opens_into, curtain_zone)`

### 关键特点

| 特点 | 影响 |
|------|------|
| **有序序列**（边界遍历顺序） | 不是无序集合，顺序含空间拓扑信息 |
| **异构节点**（wall/door/window) | 不同类型属性不同，门有 opens_into，窗无 |
| **全局关系**（共墙、对向、相邻） | 纯序列丢失 room-room 关系 |
| **分段数可变**（不同房间墙段数不同） | 需要变长输入处理 |

---

## 3. 编码方案设计空间

### 方案 A：纯净向量编码（最简单）

把每个 segment encode 成固定长度向量，room 内 concat 或 pool：

```
seg_vec = MLP([w, d_mean, d_min, d_max, q, seg_type_onehot, corner_type_onehot])
room_vec = concat(seg_vec_1, seg_vec_2, ..., seg_vec_N)  # 或 mean/max pool
```

- ✅ 极简，训练快
- ❌ 丢失空间顺序和几何拓扑
- 适用场景：先快速验证"w/d/q 确实能预测布局"

### 方案 B：有序序列编码（RNN / Transformer）

segment 按边界遍历顺序排列，用序列模型编码：

```
[seg_0, seg_1, ..., seg_N] → LSTM / Transformer Encoder → room_embedding
```

- ✅ 保留顺序信息
- ✅ 可以处理变长序列（padding or attention mask）
- ⚠️ 序列只建模"相邻 segment 沿墙关系"，不建模"对向墙的关系"

### 方案 C：图神经网络 (GNN) 编码

把每个房间建模为图：
- **节点**：每个 wall segment + 每个 door/window + 房间本身
- **边**：
  - `adjacent_wall`：同房间边界上相邻的 segment
  - `opens_into`：门 → 门洞对应的另一房间
  - `opposite`：对向墙之间的边（通过 depth ray 确定）
  - `shares_corner`：共享角点的墙段

```
graph → GNN → node_embeddings → pool → room_embedding
```

- ✅ 最强表达能力
- ✅ 可以同时编码 room-room 关系（整层楼）
- ⚠️ 训练数据量要求高

### 方案 D：双通道编码（几何 + 语义）

两个并行编码器：
1. **几何通道**：`[w, d, corner_types, normal]` → MLP → geom_vec
2. **语义通道**：`[q, seg_type_onehot, opens_to_type]` → MLP → sem_vec
3. 拼接：`[geom_vec, sem_vec]` → 融合 MLP → seg_embedding

然后方案 A/B/C 的组合。

---

## 4. 针对"布局预测"的初步架构建议

假设布局任务的输入是一个房间的 wall segment 序列，输出是该房间的 placed_groups（家具布局）：

```
输入: Room WallSegment 序列
    seg_i = [w, d, q, depth_profile, seg_type, corner_type, normal]

编码 (推荐方案 B 起步):
    1. segment 级 MLP: seg_i → 128d embedding
    2. Transformer Encoder (4-layer, 4-head): 序列 → room embedding (256d)
    3. [可选] 加入 positional encoding (沿墙位置 + 角类型)

解码:
    4. room embedding → FC → 预测每面墙的可用空间分布
    5. 或: autoregressive 生成 placed_groups 序列
```

### 为什么从方案 B 起步

| 方案 | 复杂度 | 需要数据量 | 表达力 | 起步推荐 |
|------|--------|----------|--------|---------|
| A (pool) | 低 | 少 | 弱 | 快速验证 |
| **B (序列)** | **中** | **中** | **中等** | **← 从这里开始** |
| C (GNN) | 高 | 多 | 强 | 进阶方案 |
| D (双通道) | 高 | 多 | 强 | 和 B/C 组合 |

---

## 5. Polygon Segment List — 统一输入特征 Schema

按"多边形边界遍历顺序"组织成一个**同构 segment 列表**，每条 segment 自含所有上下文：

```
PolygonSegment:
  # ---- 类型 ----
  seg_type       : wall | door | window           # 自身是什么
  
  # ---- 房间上下文 ----
  room_type      : living_room | bedroom | ...     # 所属房间类型
  room_area      : float                            # 所属房间面积 (m²)
  room_aspect    : float                            # 所属房间长宽比
  
  # ---- 门专用 ----
  to_room_type   : living_room | bedroom | ... | exterior | null
                                                    # 通向什么房间（仅 door 有值）
  is_entry       : bool                             # 是否入户门
  
  # ---- 几何 ----
  w              : float                            # 段宽 (m)
  d              : float                            # 进深 (m)
  q              : float [0, 1]                     # 墙品质分
  d_min          : float                            # 进深最小值
  d_max          : float                            # 进深最大值
  
  # ---- 角特征 ----
  corner_left    : convex | concave | flat          # 段左端点角类型
  corner_right   : convex | concave | flat          # 段右端点角类型
  
  # ---- 位置编码 ----
  order          : int                              # 在边界遍历中的序号 (0..N-1)
  total_segments : int                              # 该房间总 segment 数
  is_corner      : bool                             # 是否为角段 (corner_left or right != flat)
  
  # ---- 空间关系 ----
  adjacent_to    : living_room | bedroom | ... | exterior | null
                                                    # 该墙共墙的邻接房间类型（仅 wall 有值，null=外墙）
  opposite_idx   : int | null                       # 对向墙 segment 的 order 序号（仅 wall 有值，由 depth ray-cast 确定）
  corner_pair    : [concave|convex, concave|convex]  # 左右角的类型对，明确阴角阳角关系
  corner_shared  : [bool, bool]                     # 左右角是否与相邻房间共角
```

**每个房间是一个 `List[PolygonSegment]`**，长度 = 该房间的 wall+door+window 总数（从 room_decompose 产出）。

### 示例：case1 客厅的一个门 segment

```json
{
  "seg_type": "door",
  "room_type": "living_room",
  "room_area": 35.0,
  "room_aspect": 1.4,
  "to_room_type": "kitchen",
  "is_entry": false,
  "w": 1.0,
  "d": null,
  "q": null,
  "d_min": null,
  "d_max": null,
  "corner_left": "flat",
  "corner_right": "flat",
  "order": 5,
  "total_segments": 17,
  "is_corner": false
}
```

### 示例：一个 wall segment

```json
{
  "seg_type": "wall",
  "room_type": "living_room",
  "room_area": 35.0,
  "room_aspect": 1.4,
  "to_room_type": null,
  "is_entry": false,
  "w": 3.5,
  "d": 5.0,
  "q": 0.50,
  "d_min": 1.0,
  "d_max": 5.0,
  "corner_left": "convex",
  "corner_right": "flat",
  "order": 0,
  "total_segments": 17,
  "is_corner": true
}
```

### 关键设计决策

| 决策 | 理由 |
|------|------|
| 一个列表涵盖所有信息 | 不需要额外传 room_meta，segment 自含所属房间属性 |
| door 和 wall 共用一个 schema | 简化编码器输入，door 的 d/q 填 null 即可 |
| `to_room_type` 编码门的"对面含义" | 厨房门 vs 卧室门 → 布局约束完全不同 |
| `adjacent_to` 编码共墙关系 | 与厨房共墙 vs 外墙 → 可用进深不同（外墙有窗、共墙有门洞） |
| `opposite_idx` 编码对向关系 | 知道"哪段墙在我对面" → 布局时的回避/对齐决策 |
| `corner_pair` 编码阴角阳角 | 凹角是稀缺优质位（L形房间角），凸角靠近开口区 |
| `corner_shared` 编码共角关系 | 与隔壁房间共用角点 → 角区可能有门洞或走廊 |
| `order / total_segments` 做位置编码 | 替代 Transformer positional encoding，让模型知道段在全室中的位置 |
| `d_min / d_max` 代替 depth_profile 序列 | depth_profile 是变长数组，pool 成 [min, max] 降低复杂度（进阶可保留 raw profile 用 1D CNN） |

### 空间关系示意图

以 case1 客厅为例，一段南墙 wall segment 的空间关系：

```
             opposite_idx=4
    (0,5) ======================= (7,5)  ← 北墙 (房间对向)
           │                  │
           │  r-living 客厅    │
           │    35m²          │
           │                  │
    (0,0) ======================= (7,0)  ← 南墙
        ↑           ↑            ↑
   corner_left   seg[0]      corner_right
   adjacent_to   wall w=2.0   adjacent_to
   = exterior    d=5.0        = exterior
                              （入户门在 seg[1]）

corner_left:  convex, shared_with=r-bed2 的南墙
corner_right: convex, shared_with=r-kitchen 的西墙
adjacent_to:  exterior（南向外墙）

seg[0] 的 opposite_idx=4 → 对面是北墙 seg[4]（d=1.0，被入户门深度压缩过）
```

### 关系编码到 Graph 的映射

如果后续上 GNN（方案 C），上述关系直接映射为边：

| 关系字段 | → 图边类型 | 含义 |
|----------|----------|------|
| `adjacent_to` | `shared_wall` | 两房间共墙 |
| `opposite_idx` | `faces` | 对向 face-to-face 关系 |
| `corner_shared` | `shares_corner` | 两房间在角点相接 |
| `to_room_type` (门) | `connects_to` | 门连接两房间 |
| `order` (相邻) | `next_in_loop` | 边界遍历中的前后关系 |

### 编码流程

```
PolygonSegment 列表 (N 段)
  → Embedding: seg_type + room_type + to_room_type + corner → onehot concat
  → Feature:  [w, d, q, d_min, d_max, room_area, room_aspect, is_entry, is_corner] → normalize
  → segment_vec = concat(Embed, Feature) → MLP(256)
  → [可选] + Learnable Positional Encoding (order/N)
  → Transformer Encoder (有序序列)  or  Attention Pooling (无序)
  → room_embedding → 布局解码
```

---

## 6. 关键的 Open Questions

- [ ] w/d/q 三者之间需要做 interaction（cross-attention）还是简单 concat 就够？
- [ ] depth_profile（变长采样序列）是否保留？pool 成 [min, max, mean, std] vs 1D CNN vs 保留全序列
- [ ] corner_type 的"凹角"如何给额外的注意力权重？（凹角 → 优秀布局位）
- [ ] door 的 `to_room_type` 信息是否需要跨房间传播（整层图）？
- [ ] 训练数据：合成户型 + 人工布局标注？还是直接用规则（groups.json）做弱监督？

---

## 7. 具体实施建议 (2026-06-29)

### 7.1 输入：PolygonSegment 列表

从 `room_decompose` 产出直接序列化：

```python
def to_polygon_segment_list(region, segs) -> list[dict]:
    result = []
    n = len(segs)
    for i, seg in enumerate(segs):
        item = {
            "seg_type": seg.seg_type,
            "room_type": region.region_type,
            "room_area": region.area,
            "to_room_type": seg.opens_into,   # door 专用
            "is_entry": seg.seg_type == "door" and seg.opens_into is None,
            "w": seg.length,
            "d": None, "d_min": None, "d_max": None, "q": None,
            "corner_left": seg.corner_pre,
            "corner_right": seg.corner_post,
            "order": i, "total_segments": n,
            "adjacent_to": None,     # 需共墙检测预计算
            "opposite_idx": None,    # 需 ray-cast 预计算
        }
        if seg.seg_type == "wall":
            depths = [ds.depth for ds in seg.depth_profile]
            item["d"] = depths[0] if depths else 0
            item["d_min"] = min(depths) if depths else 0
            item["d_max"] = max(depths) if depths else 0
            item["q"] = seg.wall_quality
        result.append(item)
    return result
```

### 7.2 编码器：Transformer Encoder（方案 B）

```
输入:   PolygonSegment 列表 → onehot + 数值归一化 → ~20d raw
Embed:  raw → MLP(128) + Sinusoidal PE(order/N)
Enc:    4-layer Transformer (d=128, 4-head) → CLS token 256d
Output: CLS → room_embedding → 布局解码
```

### 7.3 为什么不先上 GNN

| 因素 | Transformer (B) | GNN (C) |
|------|:--:|:--:|
| 数据量 | 几百个房间 | 几千个楼层 |
| 实施复杂度 | 标准库半天 | 异构图 + 边类型 |
| 可验证性 | attention map 可视 | 黑盒 |
| 当前阶段 | 规则驱动 groups.json | 无真实布局标注 |

→ **Transformer 先验证路径可行，再升级 GNN。**

### 7.4 训练路线

| 阶段 | 数据 | 方法 |
|------|------|------|
| **Phase 1: 自监督** | 合成户型 1000+ | Masked Segment Prediction（随机 mask，预测 w/d/q） |
| **Phase 2: 弱监督** | groups.json 匹配 | group_code 分类 + position 回归 |
| **Phase 3: 强监督** | 设计师标注 | 自回归生成 placed_groups |

Phase 1 不需要任何标注——encoder 通过 mask 预测学习段间空间关系（对向、共墙、阴角阳角如何影响 w/d/q）。

### 7.5 当前位置

xasset 已具备：
- ✅ room_decompose → WallSegment 列表
- ✅ w / d / q + depth_profile + corner_type
- ✅ 可视化（case1 / case2）

下一步：
1. 实现 `to_polygon_segment_list()` → JSON/DataFrame
2. 搭建 Phase 1 自监督训练（Masked Segment Prediction）
3. attention map 可视验证是否学到空间关系
