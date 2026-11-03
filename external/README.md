# 外部数据集目录

> **本目录的大部分内容不进 git。** 只有本 README 和 `.gitignore` 被跟踪。
>
> 定位：存放从外部下载的公开数据集原始文件。它们是**可再生资源**（可通过脚本重新获取），
> 体积大，不适合放进版本控制。

---

## 为什么单独一个目录

`data/` 放的是**我们自己的、不可再生的数据**（历史户型转换结果），必须版本化。
`external/` 放的是**外部的、可重新下载的数据集**，不进版本控制。

两者混在一起会导致：
- 仓库体积膨胀（CubiCasa5K 解压后上 G，且 Git 历史一旦写入无法撤销）
- `git clone` 变慢
- 数据"存一份永远不动"，无法按需重新拉取

---

## 目录约定

```
external/
├── README.md            ← 本文件（进 git）
├── .gitignore           ← 忽略下面所有数据集目录（进 git）
├── cubicas5k/           ← 5000 张户型图 + SVG 标注（不跟踪）
├── rplan/               ← 中国户型（不跟踪，需申请）
├── structured3d/        ← 3D 结构 + floorplan（不跟踪，需申请）
└── osm/                 ← OpenStreetMap 切片（不跟踪）
```

**转换后的结果不留在本目录**，而是写进 `data/<scene>/converted/`（见下）。

---

## 数据集清单

详细调研见 `research/public-datasets-survey/README.md`。

| 目录 | 数据集 | 规模 | 获取方式 | 用途 |
|------|--------|------|---------|------|
| `cubicasa5k/` | CubiCasa5K | 5000 张，80+ 类 | 直接下载（Zenodo） | 室内轮廓 + 房间类别 |
| `rplan/` | RPLAN | ~8 万 | **需填表申请** | 中国户型统计先验 |
| `structured3d/` | Structured3D | 3500 套 | **需填协议申请** | 3D 结构 + floorplan 验证 |
| `osm/` | OpenStreetMap | 全球 | 直接下载（Overpass API） | 城市地块 / 道路矢量 |

---

## 获取流程

```bash
# 1. 下载（脚本在 tools/datasets/，尚未实现）
python tools/datasets/fetch_cubicasa5k.py --dest external/cubicasa5k

# 2. 转换成我们的契约（脚本在 tools/datasets/）
python tools/datasets/convert_cubicasa5k.py \
    --src external/cubicasa5k \
    --dest data/house/converted/cubicasa5k

# 3. 转换结果进 data/，原始数据留 external/
```

> **注意**：`tools/datasets/` 下的脚本**尚未实现**。
> 按 `research/public-datasets-survey/README.md` 第 7 节，
> 要等 `understand` 的视觉路线确定后再做——否则不知道最终要什么标注粒度。

---

## 许可提醒

| 数据集 | 商用 |
|--------|------|
| OSM | ✅ 可用（ODbL，需署名 + 保持开放） |
| CubiCasa5K | ⚠️ 待核实 |
| RPLAN | ❌ 学术研究用途 |
| Structured3D | ⚠️ 需读 Terms of Use |

**商业发布前必须逐一确认。** 用这些数据训练或验证出的模型/规则，其商用边界要单独评估。

---

## 已申请状态

| 数据集 | 申请状态 | 备注 |
|--------|---------|------|
| CubiCasa5K | ⬜ 未下载 | 无需申请 |
| RPLAN | ⬜ 未申请 | **建议尽早提交表单**，审批需时间 |
| Structured3D | ⬜ 未申请 | **建议尽早提交表单** |
| OSM | ⬜ 未下载 | 无需申请 |
