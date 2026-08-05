# data/house/ — 室内场景样本数据

来源：历史项目 `ihome-layout` 的 `House/` 模块（11 户真实户型、99 个房间几何+家具，128 条 Group 级布局标注）。原始数据本地拷贝在 `raw/`，转换脚本 `convert.py`，转换结果在 `converted/`。设计依据见 `mapping/README.md`，架构背景见 `research/learned-layout-with-hard-constraints/README.md`。

## 转换结果（`convert.py` 跑出的 `converted/conversion_report.json`）

| 指标 | 数值 |
|------|------|
| 房间总数 | 99（`house_data_dict.json` 75 + `house_data_more.json` 24） |
| 房间几何转换 | **99/99 全部成功**，逐一跑通 `SceneUnderstandStage` + `RoomDecomposer` 无异常 |
| Group 布局样本总数 | 128 |
| 样本可追溯到本地房间（resolved） | 73（57%） |
| 样本追溯不到本地房间（unresolved，`source_house` 指向外部语料） | 55（43%）——按约定全部保留，标记 `resolved: false` |

## 结论：taxonomy 设计是否覆盖真实数据？

**房间类型（region_type）层面**：99 个房间里，69 个通过 `region_type_map.json` 映射到 xasset 现有 `region_groups` key（`LivingDiningRoom`/`Kitchen`/`Bathroom`/`Balcony`/`Library`/`LivingRoom`/`DiningRoom`/`KidsRoom`/`Hallway`/`Bedroom`），20 个通过 xasset 自带的 `_normalize_region_type()`（`master_bedroom`/`second_bedroom` 等主次前缀）直接命中，**10 个完全没有对应项**（`Aisle`/`CloakRoom`/`Corridor`/`LaundryRoom`/`OtherRoom`/`StorageRoom` 各 1~2 间，空字符串 3 间）。这 10 间房的几何仍然转换成功（floor/door/window 都是有效数据），只是没有 Group 布局能力——这是真实存在但目前 xasset 尚未覆盖的场景，是否要补齐留给后续决策。

**Group 类型层面**（`group_type_map.json` 里 `code: null` 的条目，来自真实 128 条样本的统计）：暴露出几个**真实存在但 xasset `groups.json` 未覆盖**的组合，按出现频次排序：

1. `(Cabinet, living_dining_room)` ×14 — 客餐厅场景下真实存在"柜子"这类家具，但 `groups.json` 的 `living_dining_room` 目前只有会客组/餐桌组/影视墙组，没有柜类 code
2. `(Cabinet, bedroom)` ×9 — 卧室场景下 `Cabinet`（区别于 `Armoire` 衣柜）没有对应 code
3. `(Appliance, bathroom)` ×5 — 卫生间电器（浴霸/换气扇等）没有对应 code
4. `(Cabinet, balcony)` ×4、`(Cabinet, living_room)` ×4 — 阳台/客厅柜类同样缺失
5. 其余（`storage_room`/`cloak_room`/`aisle`/`other_room`/`laundry_room` 相关）都落在上面提到的 10 个"完全无 region_type"房间类型下，自然也没有 Group

**总结**：这次转换验证了两件事——(1) 最近完成的 `SceneRegion.priority` 拆分 + Group 合并（29组×11区域类型）在几何层面**完全兼容**真实历史数据，99/99 房间零异常；(2) 但也如实暴露出 `groups.json` 的 Group 覆盖范围比真实历史数据窄——尤其是"柜类"家具在多个房间类型下系统性缺失（这不是这次 taxonomy 重构引入的新问题，是原有 `groups.json` 设计阶段就没覆盖到的缺口，转换工作只是第一次用真实数据把它量化出来）。是否要据此扩充 `groups.json`，留给下一轮单独决策，本次转换脚本按约定不自动修补。

## 目录结构

```
house/
  raw/                      # 原始 JSON 只读拷贝
  mapping/
    region_type_map.json    # legacy room type -> xasset region_type
    group_type_map.json     # (legacy group.type, region_type) -> xasset group_code
    README.md                # 映射设计依据、统计数据、已知缺口清单
  converted/
    rooms/                   # 99 个房间，一房间一文件
    layout_samples/          # 128 条布局样本，一样本一文件
    conversion_report.json   # 转换统计（本文档"转换结果"表格的数据来源）
  convert.py                 # 转换脚本，可重跑
```

## 已知局限 / 后续可做

- `furniture_reference` 里的原始家具实例只是参考数据（供人工核对几何是否转换正确），不是 `PlacedGroup`，不建议直接用于训练。
- `rotation` 统一换算成绕 Y 轴的 yaw 角度（度），两个源文件原始表示不同（四元数 vs 3 元 Euler），已在 `convert.py` 里分支处理并做了实际验证。
- `house_data_dict.json` 的家具 `size` 原始单位是 cm，`house_data_more.json` 是 m——转换脚本已统一换算成 m（`size_m` 字段）。
- `obj_main`（素材 id）只作占位关联 id 保留，未接入 xasset 自己的 asset 体系（用户已确认后续会重新编码）。
- `role_assets` 目前全部留空——`Layer 2` 打分/生成模型训练时需要的候选级特征（segment/offset/rotation 相对墙面的占比）尚未从这批数据里派生，是下一步工作。
