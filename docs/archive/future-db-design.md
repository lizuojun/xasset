# 数据库设计（存档 — 当前已移除，P2 阶段恢复）

> **移除日期**: 2026-06-15
> **原状态**: 已完成 8 表 SQLAlchemy 模型 + Pydantic schema + Alembic 迁移
> **移除原因**: 当前管线完全在内存 PipelineContext 运行，DB 层零引用。等 P2 REST API / P4 商业化阶段再恢复。
> **恢复方式**: 从此文档还原模型定义，重建 Alembic 迁移即可。

---

## 架构概述

- **ORM**: SQLAlchemy 2.0 async
- **DB**: PostgreSQL 16 + pgvector（开发期用 SQLite + aiosqlite）
- **迁移**: Alembic
- **验证**: Pydantic v2 + pydantic-settings

## 表结构（8 表）

### 1. asset_definition — 资产定义表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| name | String(256) | |
| asset_level | Enum: object/group/zone/scene | 资产层级 |
| state | Enum: draft/published/deprecated | 生命周期 |
| scene_type | String(64) | house/urban/wild |
| object_type | String(256) | 物件类型 |
| role_hints | JSON | 角色提示 |
| style | String(128) | 风格标签 |
| tags | JSON | 标签 |
| source | JSON | 来源信息 |
| raw_data | JSON | 原始数据 |
| packaged_data | JSON | 打包后数据 (usd_url, gltf_url) |
| layout | JSON | 布局信息 |
| light | JSON | 光照信息 |
| computed_features | JSON | 计算特征 |
| metadata_extra | JSON | 预留扩展 |
| created_at/updated_at/created_by | | 审计字段 |

关系：
- `canonical_children` → AssetInstance (scene_id=None 的默认模板)
- `commerce` → CommerceMetadata (一对一)

### 2. asset_instance — 资产实例表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| definition_id | FK → asset_definition.id | |
| scene_id | FK → asset_definition.id (nullable) | 所属场景 |
| parent_id | FK → asset_instance.id (nullable) | 父实例 |
| position | JSON [x,y,z] | Y-up |
| rotation | JSON [qx,qy,qz,qw] | |
| scale | JSON [sx,sy,sz] | |
| group_id | UUID | |
| role | String(128) | |
| overrides | JSON | 属性覆写 |

### 3. sample — 样本表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| scene_type | String(64) | |
| sample_level | String(32) | |
| style | String(128) | |
| score | Integer | |
| scale_range | JSON | |
| groups | JSON | |
| material | JSON | |
| source_id | UUID | |
| style_vector | JSON (128维) | **待 pgvector 迁移** |
| partition_vector | JSON (64维) | **待 pgvector 迁移** |
| distribution_vector | JSON | **待 pgvector 迁移** |
| created_at | DateTime | |

向量维度常数：`STYLE_VECTOR_DIM=128`, `PARTITION_VECTOR_DIM=64`

### 4. region — 区域表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| scene_id | FK → asset_definition.id | |
| type | String(128) | 区域类型 |
| boundary | JSON | 多边形边界 |
| groups | JSON | 关联的 group 列表 |
| partition_vector | JSON | |
| distribution_vector | JSON | |
| doors | JSON | `[{"pts":..., "normal":..., "center":..., "width":...}, ...]` |
| windows | JSON | `[{"pts":..., "sill_height":..., "height":..., "center":..., "width":...}, ...]` |

### 5. group_instance — 组实例表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | |
| definition_code | Integer | 引用 GroupDefinition JSON 配置 |
| scene_id | FK → asset_definition.id | |
| position | JSON | |
| rotation | JSON | |
| scale | JSON | |
| role_assignments | JSON | |

### 6-8. 商业化表（P4 阶段）

- **listing**: 上架信息（title, type, credit_price, license_type, transferable 等）
- **commerce_metadata**: 资产商业化元数据（owner, version, watermark, license, credit 等）
- **platform_config**: 平台配置（exchange_rate, revenue_share, currency）

---

## 恢复步骤 (P2 时)

1. 还原 `xasset/db/base.py` + `xasset/db/connection.py`
2. 还原 4 个 `xasset/models/*.py`
3. 还原 3 个 `xasset/repositories/*.py`
4. 还原 3 个 `xasset/schemas/*.py`
5. 还原 Alembic 迁移 (`migrations/`)
6. 添加依赖: `sqlalchemy[asyncio]`, `aiosqlite`/`asyncpg`, `pgvector`, `alembic`
7. 将 sample 的 3 个 JSON 向量列切换为 pgvector 类型
