# JiaJia 待办事项

**最后更新：** 2026-04-07

---

## P0 收尾（切回 PostgreSQL 后执行）

当前 xasset 代码已完整实现，测试 29/29 通过，使用 SQLite 本地运行。
以下操作在获得 PostgreSQL 环境后完成。

### 环境准备

- [ ] 安装 Docker Desktop（需 IT 授权）或本地安装 PostgreSQL 16
- [ ] 启动数据库：`docker compose up -d`（docker-compose.yml 已就绪）
- [ ] 在 postgres 中创建 pgvector 扩展：
  ```sql
  CREATE DATABASE xasset;
  CREATE DATABASE xasset_test;
  \c xasset
  CREATE EXTENSION IF NOT EXISTS vector;
  \c xasset_test
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

### 切回 PostgreSQL

- [ ] 更新 `.env`：
  ```
  DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/xasset
  DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/xasset
  ```
- [ ] 还原 `xasset/models/sample.py` 中的向量列（`JSON` → `Vector`）：
  ```python
  from pgvector.sqlalchemy import Vector
  style_vector: Mapped[Optional[list]] = mapped_column(Vector(STYLE_VECTOR_DIM))
  partition_vector: Mapped[Optional[list]] = mapped_column(Vector(PARTITION_VECTOR_DIM))
  ```
- [ ] 还原 `xasset/repositories/sample.py` 中的向量搜索（Python 余弦距离 → pgvector `<->` 算子）
- [ ] 还原各模型文件中的 `UUID`/`JSONB`（当前已用通用 `Uuid`/`JSON` 替代，实际上通用类型在 PostgreSQL 下也能工作，**可以不还原**，保持现状即可）
- [ ] `uv add asyncpg pgvector`，移除 `aiosqlite`

### Alembic 迁移验证（P0 最后一项）

- [ ] 执行迁移：`uv run alembic upgrade head`，预期 8 张表无报错
  - `asset_definition`, `asset_instance`
  - `commerce_metadata`, `listing`, `platform_config`
  - `sample`, `group_instance`, `region`
- [ ] 为向量列创建索引：
  ```sql
  CREATE INDEX sample_style_vector_idx
    ON sample USING ivfflat (style_vector vector_l2_ops) WITH (lists = 100);
  CREATE INDEX sample_partition_vector_idx
    ON sample USING ivfflat (partition_vector vector_l2_ops) WITH (lists = 100);
  ```
- [ ] 更新 `tests/conftest.py` 中的 `TEST_DB_URL` 指向 `xasset_test`
- [ ] 重跑全套测试：`uv run pytest tests/ -v`，全部通过

---

## P0 之后的阶段规划

详见 `docs/superpowers/specs/2026-03-24-overall-roadmap-design.md`

| 阶段 | 子项目 | 前置 |
|------|--------|------|
| Phase 1 | **P1** AI 生成 Pipeline（三阶段生成链路） | P0 |
| Phase 1 | **P2** 基础设施（OSS/任务队列/REST API）| P0，与 P1 并行 |
| Phase 2 | **P3** 资产库 Web 应用 | P0、P2 |
| Phase 2 | **P4** 商业化系统 | P3 |
| Phase 3 | **P5** Omniverse 插件 | P0、P2 |

### P1/P2 启动前补充工作

- [ ] 补充 `xasset/data/groups/house.json` 中的完整 Group 定义（卧室组、餐厅组、书房组等），可参考 `ref/Furniture/furniture_group_dict.json` 迁移
- [ ] 补充 `xasset/data/groups/urban.json` 和 `wild.json`（当前为占位文件）

---

## 备注

- Supabase 项目已创建（db.cngxirrdnlwwizbtvken.supabase.co），因公司网络策略无法访问，暂未使用
- 公司机器无 Docker/PostgreSQL 安装权限，P0 测试以 SQLite 替代运行
