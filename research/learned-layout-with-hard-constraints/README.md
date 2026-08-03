# 数据驱动的室内布局：学习式打分/生成 + 约束编码进候选生成过程

**日期**: 2026-07-31
**状态**: 方案讨论中（未落代码）
**关联**: [polygon-encoder-baseline](../polygon-encoder-baseline/README.md)（已有的 segment 编码器设计，本文档不重复，直接复用其 `PolygonSegment` schema 和 Transformer 编码方案）

---

## 0. 问题定义

`xasset/pipeline/stages/layout/house/compose.py` 目前的 `HouseLayoutComposeStage` 是一个空 stub——`placed_groups` 恒为空列表（此前尝试过"配置驱动的 Zone 规则式写法"，效果不理想，已推倒重来，见 git 历史 `d603c64`）。

用户目标：把这一层从**规则式逐段适配**（人工写 `groups.json` 的 zone 规则、`score_walls_for_group` 打分公式）升级为**数据驱动的学习式方法**，同时严格满足空间约束（家具不能出界、不能互相碰撞、门口留出通行净宽等）。

两个关键设计取舍已经和用户确认：

| 决策点 | 选择 |
|--------|------|
| 学习目标形态 | **学习式打分/生成模型**（不是纯检索+重适配） |
| 约束落地方式 | **约束直接编码进候选生成过程**（生成阶段结构性地不产生非法候选，而不是生成后再过滤/打回） |

**Taxonomy 落地（已完成，2026-08-03）**：`region_type`/`group_code` 里混进的"主/次排序"语义已拆分为独立的 `SceneRegion.priority: int` 字段（0=无主次概念，1=主，2+=次，数字越大越次要），原始输入数据的 room type 字符串不做改写，仅在 `scene_understand.py` 解析进 xasset 内部结构时做一次规范化。相应地 `groups.json` 里纯粹因主/次拆分的 Group（`100201`主卧床/`100202`次卧床、`100601`/`100602`马桶、`100701`/`100702`浴缸）合并为单一 code（各保留原 master 系列 code：`100201`/`100601`/`100701`，`footprint_range` 取两者并集），`region_groups` 的 `master_bedroom`/`bedroom`、`bathroom`/`master_bathroom` 对应合并为 `bedroom`/`bathroom` 两个 key。详见 4.1 节。

---

## 1. 数据盘点：能拿到什么训练数据

调研了 `D:\Projects\XEditor-Ref\ihome-layout`（早期智能软装布局服务的历史代码，用户本人的历史项目），核心结论：

### 1.1 `House/` —— 本地、自包含，可直接用

- `house_data_dict.json`（8 户）+ `house_data_more.json`（3 户）= **11 户真实户型、99 个已布置房间**。每个房间自带：
  - `floor`：边界多边形（flat `[x,z,...]` 数组）
  - `door_info` / `window_info` / `hole_info` / `baywindow_info`：开洞几何
  - `furniture_info`：每件家具实例的 `position` / `rotation`（四元数）/ `scale` / `size` / `type`
  - 全部是字面数值，**零远程依赖**（不需要 OSS/网络）
- `house_sample_dict.json`：**128 条**已打分的 Group 级布局样本，按 `room_type × 面积桶` 分组，每条含 `type/code/position/rotation/size/size_min/size_rest/obj_main/obj_type` 等字段，并通过 `source_house`/`source_room` 精确回指到上面 99 个房间之一。这是"房间几何 → Group 布局结果"的**成对训练样本**。
  - 实测各房间类型样本数（详见下方分布表）：`Bathroom` 23 条最多，多数房间类型个位数到十几条，`SecondBathroom`/`Corridor`/`LaundryRoom` 各仅 1 条。
- `house_feature_dict.json` 是空文件（`{}`），不可用。

**房间类型样本分布**（`house_sample_dict.json`，共 128 条）：

| room_type | 样本数 | group_types 覆盖 |
|---|---|---|
| Bathroom | 23 | Appliance, Bath, Cabinet, Toilet |
| MasterBedroom | 13 | Armoire, Bed, Cabinet, Media, Rest, Work |
| Kitchen | 14 | Appliance |
| Balcony | 14 | Appliance, Cabinet, Rest |
| Hallway | 12 | Cabinet |
| LivingDiningRoom | 10 | Appliance, Cabinet, Dining, Media, Meeting, Rest, Work |
| SecondBedroom | 10 | Armoire, Bed, Cabinet, Media, Work |
| Library | 5 | Cabinet, Rest, Work |
| LivingRoom | 4 | Cabinet, Media, Meeting |
| DiningRoom | 4 | Cabinet, Dining |
| Bedroom / KidsRoom / OtherRoom | 3 各 | — |
| CloakRoom / StorageRoom / Aisle | 2~3 各 | — |
| SecondBathroom / Corridor / LaundryRoom | 1 各 | — |

### 1.2 `HouseSearch/` —— 主要是检索/提取代码，本地 JSON 多为索引而非几何本体

- 核心算法（`house_search.py`/`house_propose.py`/`group_sample_search.py`）是**手工特征向量 + 加权距离检索**：给定房间的 `[room_type, 主家具w/d, ...]` 向量，在样本库里找最相似的历史设计，再用几何规则重新贴合到新房间的墙面上。这是一个可解释的强基线，但不是学习式方法。
- 本地 `group_sample_data_roles.json`（~7600 条）是特征向量索引，`key` 指向远程 OSS 上的完整场景 JSON，本地不含几何本体。
- `source/scene_map.json`（2万条）、`group/all_design_list.json` 等同样只存**指向云端 OSS 对象存储的远程 URL**，不是几何数据。
- `LayoutByRule/house_analysis.py::room_line()` 是这套系统自己的"房间分解"实现（segment + `score`/`score_pre`/`score_post` + `depth_all` 深度剖面），概念上与 xasset 现有的 `RoomDecomposer`/`WallSegment`（`xasset/pipeline/stages/layout/house/room_decompose.py`）高度对应——可以作为设计对照，但不提供额外的可复用数据。
- **凭据清理（已完成，2026-08-03）**：`HouseSearch/data_oss.py`、`DataAccess/data_oss.py`、`DataAccess/data_oss_ex.py` 三处硬编码的 OSS `ACCESS_ID`/`ACCESS_SECRET` 已置空清理（这套代码是 `ihome-layout` 作者本人的历史项目，不是第三方代码，问题只是"旧代码遗留的失效凭据不该继续躺在文件里"，跟数据授权无关）。
- **数据来源提醒**：`house_sample_dict.json`/`house_data_dict.json` 里的几何和布局数值本身是自有数据，可以放心用；但家具部分引用的是外部素材库目录 id（`obj_main`/`jid`），这批 id 目前先作为**关联 ID**保留占位（用于追溯"这个 Group 当时配的是哪类素材"），后续会重新编码/替换为 xasset 自己的资产 id 体系，不直接对外部素材库产生依赖。

### 1.3 数据规模对训练意味着什么

99 个房间、128 条 Group 样本，这个量级：
- **不足以**从零训练一个高容量生成模型（如自回归 Transformer decoder 从头学 position/rotation 分布）
- **足以**作为：
  1. `polygon-encoder-baseline.md` 里 Phase 1（自监督 Masked Segment Prediction）的**验证集**，因为 Phase 1 不需要标注,可以另外用 xasset 自己合成的户型批量生成
  2. Phase 2/3（弱监督/强监督）的**小样本微调集**或**打分器的校准集**——尤其适合训练"这个候选摆放合理吗"的判别式打分模型，而不是生成式模型（判别任务需要的样本量远小于生成任务）
  3. 检索式方法（1.2 提到的 baseline）的候选来源，作为学习式方法的对照基线

---

## 2. 核心思路：把约束编码进候选生成过程

### 2.1 为什么不做"生成后过滤/打分修正"

后验证过滤的问题：生成器如果不知道约束存在，大概率生成大量非法样本，过滤后剩余合法候选的分布会严重偏离生成器本身建模的分布（reject sampling 效率低，且训练时的 loss 信号里包含大量"合法性"噪声，模型很难把精力放在"好不好看"上）。用户已经明确选择让约束**结构性地**存在于候选生成这一步，而不是后处理。

### 2.2 约束的天然落点：xasset 已有的 WallSegment 表示

`RoomDecomposer.decompose()` 产出的 `WallSegment` 列表已经带有：

- `depth_profile`：沿墙每一段的**可用进深**（已经排除了门洞、窗台等不可放置区域）
- `length`：段长
- `wall_quality`：位置质量分（已经隐含了"角落/门洞附近扣分"等规则）
- `seg_type`：wall/door/window（决定能不能贴靠）

这意味着"某个 Group（比如床，footprint 1.8m×2.2m）能不能放在某段墙的某个位置"这个**硬约束**，在生成之前就是可以精确计算的：只要 `segment.length - 已占用长度 ≥ footprint.w` 且 `segment 在该位置的 depth ≥ footprint.d`，候选就是几何合法的。这跟旧的规则式 `score_walls_for_group()` 本质上做的是同一件事——**只是现在建议把"打分排序"这一步换成学习式打分，而不是手写公式，但"候选空间构造"这一步（即约束）本身继续沿用几何计算，不学习**。

于是问题被拆成两层：

```
Layer 1（约束/几何，不学习）: WallSegment + depth_profile → 生成"几何合法"的候选放置位姿集合
Layer 2（学习）           : 候选集合 + 房间/家具上下文 → 打分 or 排序 or 挑选
```

这个拆分直接解决了"约束怎么落地"的问题：约束在 Layer 1 用解析几何/占用区间计算强制满足,学习模型（Layer 2）**永远看不到、也不可能生成非法候选**——它只是在合法候选之间做选择或打分，天然无法违反约束。

### 2.3 序列化/自回归生成，逐个 Group 摆放，动态维护占用状态

一个房间要摆多个 Group（比如卧室：床组 + 书桌组 + 衣柜组），Group 之间也要避免碰撞。方案：

1. 维护一个"墙段占用状态"（每段 `WallSegment` 减去已放置 Group 占用的 `[t0, t1]` 区间，类似现有 `used_ranges` 字段已经预留的设计）
2. 每一步：
   - 从待放置 Group 列表里选下一个要放的 Group（可以按 `groups.json` 里的优先级/tier，也可以让模型自己学"先放哪个"）
   - **候选生成（Layer 1，几何计算）**：遍历当前未满占用的墙段，用 `score_walls_for_group()` 式的几何检查筛出所有几何合法的 `(segment, offset, rotation)` 候选，数量通常是几到几十个，不是无穷连续空间
   - **候选打分（Layer 2，学习模型）**：模型给每个候选打分（可以是简单的候选打分器，也可以是更复杂的、条件于"已放置 Group + 房间整体"的上下文打分）
   - 选出最高分候选，更新占用状态，进入下一步
3. 这个过程本身是**自回归**的，但"自回归"体现在"选择候选"而不是"直接回归连续坐标"——这是关键区别：模型永远在一个离散、几何合法的候选集里做选择（或者输出候选打分向量），不会直接输出可能非法的 `(x, y, rotation)` 浮点数。

这也顺带解决了"Group 之间碰撞"的约束：因为占用状态是逐步更新的，第 N 个 Group 的候选生成天然排除了已经被前 N-1 个 Group 占用的区间——不需要额外的碰撞检测环节。

### 2.4 Layer 1（编码器）用 Transformer，Layer 2（打分器）不需要

`polygon-encoder-baseline.md` 建议编码器（产出 `room_embedding`）用 4 层 Transformer，这个选择在这里依然成立且理由更清晰了：房间墙段之间存在"对向墙""共墙"等**非局部关系**（比如 seg[0] 和 seg[4] 是对面墙，但序列位置不相邻），纯 RNN/LSTM 只建模局部相邻关系，需要手工加边才能捕捉这种跨位置关系；Transformer 的全局 attention 天然能学到这种关系，不需要显式建图。房间墙段数通常 10~20 段，attention 的 O(N²) 计算量完全不是问题。

但 Layer 2（候选打分/选择）**不建议用 Transformer**：经过 2.3 节的候选生成，每一步的候选集合只有几到几十个（不是连续空间，也不是长序列），候选之间的相对关系已经被"占用状态逐步更新"处理掉了（后放置的候选天然感知不到已被占用的区间）。这种规模下一个小 MLP（输入=候选几何特征 + `room_embedding` + 已放置 Group 摘要）打分就足够，上 Transformer 只是引入不必要的参数量和过拟合风险，尤其是在下节要讨论的小数据量前提下。

### 2.5 与 polygon-encoder-baseline.md 的接口

`polygon-encoder-baseline.md` 已经设计好了 `PolygonSegment` → Transformer Encoder → `room_embedding` 的编码流程。这份文档的 Layer 2 打分模型直接消费该 `room_embedding`（作为房间整体上下文）+ 候选自身的几何特征（`(segment_idx, offset_ratio, rotation, footprint)`）+ 已放置 Group 的历史 embedding（可以用同一套 Transformer 或者简单的 GRU 累积），输出一个标量分数。两份文档合起来就是完整的编码器+决策器架构；这份文档不重复编码器细节。

---

## 3. 数据不足的应对策略

128 条 Group 样本无法支撑端到端训练一个"看房间就能摆好所有家具"的生成模型。数据规模的量级差异很大，分两部分单独算：

- **Phase 1（编码器自监督预训练）**：数据可以程序化无限生成，不是瓶颈。喂饱一个 4 层小 Transformer 编码器，大概几千到几万个合成房间量级就足够。
- **Phase 2/3（打分器的监督/微调）**：128 条**撑不起任何"从零训练"的监督模型**——分散到 19 种房间类型后，多数类型只有个位数样本（`SecondBathroom`/`Corridor`/`LaundryRoom` 各仅 1 条），连小样本微调都勉强，更谈不上支撑一个需要正负样本对比的排序模型。真要"从零学出"一个不依赖蒸馏、纯数据驱动的打分器，每个房间类型大概需要至少几百条量级（且需要同时有负样本/低分候选做对比），现有数据差距还很大。

因此不建议直接拿 128 条去"训练"打分器，更现实的路径是**蒸馏**：用规则式的 `score_walls_for_group` 公式在（无限生成的）合成户型上跑出海量伪标注打分信号，训练 Layer 2 打分器去模仿这个打分函数；House/ 的 128 条真实样本**只作验证集**——检验蒸馏出来的模型是否能把真实设计师的历史选择排在候选列表前列，而不是直接拿它调参数。这样"学习"这一步解决的问题从"凭空学会审美"降级为"逼近一个已知打分函数 + 少量真实数据校准"，对数据量的要求低得多，也更贴近 128 条样本能负担的规模。

数据策略分层：

| 数据来源 | 用途 | 规模 |
|---|---|---|
| xasset 自己合成的户型（程序化生成随机但合法的房间边界+门窗） | Phase 1 自监督预训练 `room_embedding` 编码器（不需要标注） | 可无限生成 |
| `groups.json` 现有规则式 `score_walls_for_group` 打分公式 | 弱监督：让 Layer 2 打分模型蒸馏模仿现有规则打分，作为冷启动 | 可无限生成（规则可以跑在合成户型上） |
| House/ 99 房间 + 128 Group 样本 | **验证集**，不直接参与训练：衡量蒸馏出的打分器排序是否接近真实设计师的选择 | 99 房间 / 128 样本 |
| HouseSearch 检索式方法（1.2） | 作为对照 baseline，评估学习式方法是否真的比"检索+重适配"更好 | ~7600 条特征索引（需 OSS 才能取到完整几何） |

这个策略的关键假设：**"合法性"约束的学习成本几乎为零**（因为约束不学习，是 Layer 1 解析计算），学习模型真正要学的是"哪个合法候选更符合人类审美/习惯"，这是一个比"学会不碰撞"轻得多的任务，也是小样本更能负担得起的任务。

### 3.1 数据获取计划（已确认，待执行）

按优先级排序，前三项是"补数据"，第四项是"搞懂现有字段"（成本低、不依赖新数据、但能直接验证 Layer 1 的正确性，优先级实际上最高）：

1. **同房间类型下补充更多 Group 布局样本**，尤其当前样本数很少的类型（`LivingRoom` 4 条 / `DiningRoom` 4 条 / `KidsRoom` 3 条等，见 1.1 节分布表）。目标：每类至少补到几十条，把"验证集"升级为"能做小样本监督"的训练集，减少对蒸馏伪标签的依赖。
   规模建议（因 Layer 2 只是小 MLP，不是 Transformer，数据门槛本身不高）：下限每类型 **~30 条**（刚够看到信号）；目标 **50~100 条**（能训练+留验证集）；稳健 **200+ 条**（能分 train/val，容忍类型内部多样性）。组合空间大的类型（如 `LivingDiningRoom`，覆盖 Meeting/Dining/Media/Work/Rest/Cabinet/Appliance 七种 Group）门槛应比单一 Group 类型的房间（如 `Kitchen`，只有 Appliance）更高。现有 `Bathroom` 23 条已接近下限，`LivingRoom`/`DiningRoom`/`KidsRoom` 离下限还差一截。
2. **同一房间形状下的多个不同布局方案**（同一户型，多种合理摆法）。这是当前数据完全没有的维度——现有样本是 1 户型→1 布局的单一映射。有了"多方案对比"，才能直接训练 Layer 2 的 **listwise 排序**（哪个方案更好），而不必完全依赖蒸馏出来的伪标签。
   规模建议（这一档比第 1 类贵，因为不是"多找户型"而是"同户型多摆几种方案"）：下限每户型 **3 个方案**（够形成粗略的偏序关系）；目标每户型 **5~10 个方案**，覆盖 **50~100 个不同户型**。listwise 排序器的泛化更依赖"户型数量"而非"单户型的方案数"——10 个户型各 3 方案，优先于 3 个户型各 10 方案。
3. **明确的负样本/差评样本**（不合理的摆法，哪怕是人工构造的反例）。判别式打分模型天然需要正负对比，现有数据全是"正例"（认为好的设计），没有负例，模型学不出"边界在哪"。
   规模建议：可以**混合来源**，不必全靠人工。大部分负样本可程序化生成（数量无限）——把正样本做扰动：转 180°、挪到挡住门口通行路径的位置、家具尺寸相对房间过大等"合法但差"的扰动。但扰动策略需要校准方向，因此需要一批**人工确认过的真负样本**做锚点：每类型 **20~30 条**足够，程序化负样本补足剩余量。
4. **搞懂 `House/` 的 `size_rest` 字段的权威定义**（示例值 `[0.0, 0.519943, 1.240926, 0.692284]`，猜测是四个方向剩余空间）。不需要新数据，是把现有字段的含义确认清楚；一旦确认，可以直接作为"合法性 mask"的监督信号来源，校验 Layer 1 几何计算（`WallSegment.depth_profile`/占用区间）算得对不对。

> 以上规模是基于"小 MLP + 蒸馏为主"这个架构选择的经验估计，不是精确推导值；真正的门槛要等第一批数据到手、看训练曲线后再校准。如果只能优先补一类，第 1 类投入产出比最高（门槛最低、能立刻把"小样本监督"从假设变可行）；第 2 类最贵但价值最独特（唯一能解决 listwise 缺数据的问题）；第 3 类可靠程序化扰动省下大半人工成本。

**数据收集进行中**（2026-08-03）：用户已着手寻找/补充上述数据。

### 3.2 其他开放问题

- [ ] Layer 2 打分模型的具体形式：pointwise 打分（每个候选独立打分，取 argmax）还是 listwise（一次看所有候选排序，类似 learning-to-rank）？listwise 更能捕捉候选之间的相对优劣，但训练信号构造更复杂——3.1 第 2 项数据到位后，listwise 会更可行。
- [ ] Group 摆放顺序（先摆床还是先摆衣柜）本身要不要也学习？还是继续沿用 `groups.json` 的 tier/priority 硬编码？（倾向于先硬编码顺序，只学"给定顺序下,某一步怎么选候选"，降低问题复杂度）
- [ ] 房间整体是否需要"回退"机制——如果第 3 个 Group 无论怎么选候选都会导致后续 Group 无处安放（比如房间被前几个 Group 占满），要不要支持回溯重选？还是接受"贪心selection 可能产出次优全局解"作为 v1 的已知局限？
- [ ] 合成户型生成器（Phase 1 数据来源）需要多真实？纯随机矩形房间 vs 参考 House/ 里 11 户真实户型的统计分布（面积/长宽比/开门位置）做参数化采样？

## 4. Taxonomy 统一（已完成，2026-08-03）

### 4.1 问题：`region_type`/`group_code` 里混进了"排序"语义

`groups.json` 曾把 `master_bedroom`/`bedroom`、`bathroom`/`master_bathroom` 当作并列的 `region_type`，对应地床/马桶/浴缸也拆成 `100201`/`100202`、`100601`/`100602`、`100701`/`100702` 两个 code。这把两种不同维度的信息压进了同一个字符串/编号：

1. **功能类别**（这个房间是干什么的）——卧室、卫生间
2. **实例排序/优先级**（这个房间在户型里的地位）——主卧 vs 次卧、主卫 vs 次卫

这个混淆有两个实际代价：

- **数据被稀释**：同一功能类别被拆成多个桶，每桶样本更少，直接加重第 3 节讨论的"数据不足"问题
- **处理不一致**：合并前 `bathroom`→[马桶`100601`,浴缸`100701`,柜`100505`]，`master_bathroom`→[马桶`100602`,浴缸`100702`,**柜同样是`100505`**]——马桶/浴缸按主次拆了，柜子却没拆，说明"排序该不该编码进类型字符串"这件事本身没有统一规则

### 4.2 方案：拆成独立的 `priority` 字段，原始输入不改写

- `SceneRegion` 新增 `priority: int = 0`（0=无主次概念，1=主，2+=次，数字越大越次要）
- **原始输入数据（scene_vector 里的 `room.type`）保持原样不动**——不强制要求上游把 `MasterBedroom` 改名成别的字符串
- 规范化发生在 `scene_understand.py::_parse_scene_vector` 这一层：`_normalize_region_type()` 把原始 type 字符串映射成 `(region_type, priority)` 一对，只影响 xasset 内部的 `SceneRegion`，不改写输入 dict
- 相应地 `groups.json` 里纯粹因主/次拆分（而非真实家具差异）的 Group 合并为一个 code：
  - `100201`(主卧床)+`100202`(次卧床) → 单一 `100201`，`footprint_range` 取两者并集 `[[1.5,2.2],[2.0,2.4]]`，`asset_types` 补上 single 床型
  - `100601`+`100602`（马桶）→ 单一 `100601`
  - `100701`+`100702`（浴缸）→ 单一 `100701`，`footprint_range` 同样取并集
  - `100203`（儿童床）**不合并**——是真实家具差异（可配置婴儿床），不是主次拆分
  - `100501`/`502`/`503`/`504`/`505`（各类柜子）**不合并**——按房间功能区分是真实语义差异，不是主次拆分
- `region_groups` 的 `master_bedroom`/`bedroom` 合并为 `bedroom`（取配置更完整的 `master_bedroom` 列表），`bathroom`/`master_bathroom` 合并为 `bathroom`
- 结果：`groups.json` 从 32 个 Group / 14 个 region_type 收敛为 **29 个 Group / 11 个 region_type**（[docs/pipeline-map.md](../../docs/pipeline-map.md) 已同步更新）

### 4.3 为什么这对生成式/学习式算法更友好

- **taxonomy 越碎，小样本问题越严重**——合并后同一功能类别的样本不再被人为拆散，直接改善 3.1 节的数据稀疏问题
- **`priority` 天然支持任意数量的同类房间**（三间卧室也能表达为 1/2/3），而枚举字符串（`master_`/`second_`）只能覆盖两档，遇到三间卧室就得再发明新前缀
- **正交于 `scene_type`**：`priority` 不含任何"卧室"专属语义，未来 urban/wild 场景要表达"主广场 vs 次要广场"之类的排序时可以直接复用同一个字段，不需要为每个场景类型重新发明 `master_`/`second_` 式的字符串前缀
- **合并 Group 后决策空间更连续**：把 100201/100202 这种"几乎相同、仅尺寸区间不同"的两个 code 合并成一个，配合更宽的 `footprint_range`，"选多大的床"从"分类选择两个几乎一样的 code"变成"在一个连续尺寸区间里定位"——这对 Layer 2 打分/生成模型更友好，不需要额外学习两个几乎重叠 code 之间的分类边界

## 5. 下一步（暂不写代码）

1. 把 `House/house_data_dict.json` + `house_data_more.json` + `house_sample_dict.json` 转换成 xasset 自己的 `SceneVector` + `LayoutOutput` 格式，验证现有 `RoomDecomposer` 能不能正确处理这 99 个真实户型（这一步本身就是对现有几何管线的一次真实数据回归测试，不涉及学习模型）。转换时旧数据里 `region_type`/`group.type` 需要经过 4.2 节的映射表（另建独立映射文档维护，见下方数据转换工作目录）。
2. 推进 3.1 的数据获取计划（尤其是第 4 项 `size_rest` 字段含义确认，成本最低）
3. 明确 Layer 2 打分模型的输入特征 schema（候选级特征：属于哪个 segment、offset、rotation、footprint 相对该 segment 长度/深度的占比；上下文特征：`room_embedding`、已放置 Group 的摘要）
4. 决定合成户型生成器的参数分布，跑出第一批 Phase 1 自监督数据
