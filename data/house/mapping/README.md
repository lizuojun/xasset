# 映射表说明

## `region_type_map.json`

legacy `room["type"]` → xasset `region_type`。

- `master_bedroom`/`MasterBedroom`/`second_bedroom`/`SecondBedroom`/`master_bathroom`/`MasterBathroom` 这类带主次前缀的类型，**不在本表处理**——xasset 自身的 `_normalize_region_type()`（`xasset/pipeline/stages/understand/scene_understand.py`）已经负责把它们拆成 `(region_type, priority)`，本表只处理该函数不认识的字符串。
- `mapped`：单纯是大小写/命名风格差异（`LivingRoom`→`living_room`），xasset `groups.json` 里有对应 `region_groups` key。
- `unmapped`：legacy 数据里出现但 xasset 完全没有对应 `region_type` 的房间类型（`Aisle`/`CloakRoom`/`Corridor`/`LaundryRoom`/`OtherRoom`/`StorageRoom`，以及空字符串）。这些房间的**几何仍然转换**（floor/door/window 都有效数据），`region_type` 保留一个 snake_case 化的占位名，但 `group_code` 全部为 `null`——这是真实的功能覆盖缺口，不是转换脚本的疏漏。

## `group_type_map.json`

legacy `(group.type, region_type)` → xasset `group_code`。

`group.type` 到 `group_code` **不是一对一**：同一个 legacy 类型（比如 `Cabinet`）在不同房间类型下对应完全不同的 xasset Group（餐边柜/玄关柜/卧室衣柜/书柜/浴室柜），必须按房间类型区分。这张表是按真实数据统计出来的——用 `data/house/raw/house_sample_dict.json` 里全部 128 条样本，枚举了每个 `group.type` 实际出现在哪些 `region_type`（房间类型）下（见下方"统计依据"），再逐条查 `xasset/pipeline/stages/layout/house/groups.json` 的 `region_groups` 有没有对应 code。

### 统计依据（legacy 数据里 group.type 实际出现的房间类型）

```
Appliance -> Balcony, Bathroom, Kitchen, LaundryRoom, LivingDiningRoom
Armoire   -> Bedroom, KidsRoom, MasterBedroom, SecondBedroom
Bath      -> Bathroom
Bed       -> Bedroom, KidsRoom, MasterBedroom, SecondBedroom
Cabinet   -> Aisle, Balcony, Bathroom, Bedroom, CloakRoom, DiningRoom, Hallway,
             KidsRoom, Library, LivingDiningRoom, LivingRoom, MasterBedroom,
             OtherRoom, SecondBathroom, SecondBedroom, StorageRoom
Dining    -> DiningRoom, LivingDiningRoom
Media     -> Bedroom, LivingDiningRoom, LivingRoom, MasterBedroom, SecondBedroom
Meeting   -> LivingDiningRoom, LivingRoom
Rest      -> Balcony, Library, LivingDiningRoom, MasterBedroom
Toilet    -> Bathroom
Work      -> Bedroom, KidsRoom, Library, LivingDiningRoom, MasterBedroom, SecondBedroom
```

### 发现的真实覆盖缺口（`code: null` 的条目）

这次转换的一个直接产出是暴露出 `groups.json` 里若干"legacy 数据里真实存在，但 xasset 当前 Group 定义没覆盖"的组合，例如：

- `living_room`/`living_dining_room` 完全没有 cabinet 类 code（legacy 数据里客厅/客餐厅确实会摆餐边柜/电视柜之外的柜子）
- `bathroom` 没有 appliance 类 code（浴霸/换气扇等，legacy 用 `Appliance` 类型表示）
- `balcony` 没有 cabinet 类 code
- 若干 `unmapped` 的 legacy 房间类型（`Aisle`/`CloakRoom` 等）本身在 xasset 里没有 region_type，自然也没有对应 Group

这些缺口是否需要补齐（新增 Group/region_groups 条目），留给后续单独决策，不在本次转换脚本里自动修补——转换脚本如实记录 `code: null` + `note` 说明原因，写入 `conversion_report.json`。

### 特殊说明

- `Cabinet`（kids_room）和 `Armoire`（kids_room）当前都映射到同一个 code `100503`——legacy 数据把"柜子"和"衣柜"当成两种不同的家具类型，但 xasset 儿童房目前只有一个衣柜类 Group，两者语义有重叠，标注了 `note` 提示需要人工复核（是否要在 xasset 里为儿童房拆出独立的"玩具柜"之类的 code）。
- `Rest`（library）复用了 `100402`（卧室休闲角）的 code，因为 xasset 目前没有为书房单独定义"休闲角"Group，语义上近似借用。
