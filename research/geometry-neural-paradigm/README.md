# 几何输入输出的神经网络模型范式

**问题**：多边形面积、三角剖分、网格生成等几何运算有解析解，但用神经网络方法做相关研究吗？涉及哪些向量化/几何化的输入表示范式？

---

## 1. 主要研究方向

### 1.1 Learned Triangulation（学习三角剖分）

| 论文 | 方法 | 要点 |
|------|------|------|
| **PointTriNet** (Sharp & Ovsjanikov, ECCV 2020) | GNN + 点集输入 | 从 3D 点集直接学习生成三角剖分；用概率分布预测 edges，避免传统 Delaunay 的刚性约束 |
| **DeepDT** (Luo, Mi & Tao, AAAI 2021) | 深度学习 + Delaunay | 从 Delaunay 三角剖分学习几何特征，用于曲面重建；关键是把四面体和三角网格之间的关系编码进网络 |
| **Learning Meshing from Delaunay** (Zhang & Tao, IJCV 2025) | GNN 变体 (Local-Face GNN) | 显式输出网格连接关系 + 顶点位置，而非隐式表达 |
| **RL-based Meshing** (Thacher et al., CAD 2025) | 强化学习 + GNN + Delaunay | 用 RL 驱动顶点分布和修改，Delaunay 算法做三角剖分；评估网格质量奖励 |

### 1.2 Differentiable Geometry（可微几何运算）

| 论文 | 方法 | 要点 |
|------|------|------|
| **DDSL** (Jiang et al., ICCV 2019) | 可微 Simplex 层 | 桥接网格表达（点云/三角/四面体）与栅格图像；用 Non-Uniform Fourier Transform 做可微光栅化；支持端到端训练 polygon generator |
| **Neural Geometry Processing** (Williamson & Mitra, 2024) | 球面神经曲面 | 直接在神经表示上计算微分几何算子（法线、第一/第二基本形式、Laplace-Beltrami），不需要转回 mesh |

### 1.3 Geometric Deep Learning（几何深度学习基础）

- **Primal-Dual Mesh CNN** (Milano et al., NeurIPS 2020)：利用 mesh 的拓扑-几何对偶性扩展图卷积
- **Learning Geometric Operators on Meshes** (Wang et al., 2019)：学习算子的谱表示，处理不同三角剖分的等变性
- **Neural Mesh Simplification** (Potamias et al., CVPR 2022)：用 GNN 学习 mesh 简化（边坍缩），输出简化后的三角剖分

---

## 2. 几何数据 → 向量表达的几个范式

| 范式 | 代表方法 | 输入形式 | 适用场景 |
|------|---------|---------|---------|
| **Point-based** | PointNet, PointTriNet | `(N, 3)` 点云 | 非结构化 3D 数据 |
| **Graph-based** | MeshCNN, GNN variants | `(V, E, F)` 图结构 | 已有拓扑的 mesh |
| **Voxel-based** | 3D CNN | `(H, W, D)` 体素网格 | 规整化处理 |
| **Implicit / SDF** | DeepSDF, NeRF, Occupancy Networks | 坐标 → 函数值 | 连续曲面表达 |
| **Spectral / Operator** | Laplace-Beltrami eigenbasis | 特征谱 | 形状分析、变形 |
| **Polygonal / Vector** | PolygonRNN, DDSL | 多边形顶点序列 | 2D 几何、建筑平面图 |
| **Simplicial Complex** | Persistent Homology, TDA | 持续同调特征 | 拓扑特征提取 |

---

## 3. 与我们 xasset 的关系

我们 pipeline 的 understand 层输入是 SceneVector JSON（多边形 + 门窗），要做的推理包括：
- 区域类型识别（living_room vs bedroom vs kitchen）
- 门窗语义（入户门、内门、飘窗）
- 空间关系（相邻、对向、共墙）

现有研究的可参考点：

| 需求 | 可参考方向 |
|------|-----------|
| 多边形 → 特征向量 | PolygonRNN, Graph-based encoding |
| 多边形相似/分类 | 用 GNN 学 graph embedding；可结合 region area/proportion/ratio |
| 房间类型识别 | 把 room polygon + door/window 拼成 graph，节点=房间/开口，边=相邻/共墙 |
| 三角剖分 | 非学习路径用 ear-cut（已实现）；学习路径参考 PointTriNet 做非刚性布网 |

---

## 4. 值得精读的论文

1. **PointTriNet** — 2020, ECCV. 从点集学三角剖分，开山之作
2. **DDSL** — 2019, ICCV. 可微多边形光栅化，端到端训练 polygon generator
3. **DeepDT** — 2021, AAAI. Delaunay 特征编码用于曲面重建
4. **Neural Geometry Processing** — 2024, arXiv. 直接在神经表达上做几何处理
5. **Survey: AI for Mesh Generation** — 2025, arXiv (Owen et al.). 工程仿真中 AI 网格生成综述

---

## 5. 待深入的问题

- [ ] 是否有 NN 方法直接预测多边形面积？（有解析解但可以验证几何学习能力）
- [ ] 多边形 encoder 有哪些成熟的 baseline？（PolyGen, House-GAN, FloorNet 等建筑平面图方向）
- [ ] 门洞/窗洞如何编码进 graph？（额外节点、边属性、注意力机制）
- [ ] 相邻关系网络（wall adjacency, room adjacency）的训练数据如何构造？
