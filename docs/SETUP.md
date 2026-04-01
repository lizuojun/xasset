# 新机器初始化指南

## 前置条件

| 工具 | 说明 | 安装方式 |
|------|------|---------|
| Git | 版本管理 | https://git-scm.com |
| Docker Desktop | 运行本地 PostgreSQL | https://www.docker.com/products/docker-desktop |
| uv | Python 包管理 | `curl -LsSf https://astral.sh/uv/install.sh \| sh`（Mac/Linux）或 `winget install astral-sh.uv`（Windows） |

---

## 第一步：克隆代码

```bash
git clone https://github.com/<你的用户名>/xasset.git
cd xasset
```

---

## 第二步：安装 Python 依赖

```bash
uv sync
```

uv 会自动读取 `.python-version`（3.11）和 `pyproject.toml`，创建虚拟环境并安装所有依赖。

---

## 第三步：启动本地数据库

项目根目录有 `docker-compose.yml`，一条命令启动 PostgreSQL + pgvector：

```bash
docker compose up -d
```

启动后：
- 主库：`localhost:5432`，数据库名 `xasset`
- 测试库：`localhost:5433`，数据库名 `xasset_test`

> 数据持久化在 Docker volume `pgdata` 中，重启 Docker 不会丢失数据。

---

## 第四步：配置环境变量

复制模板并填写本地配置：

```bash
cp .env.example .env
```

`.env` 内容（默认值与 docker-compose 对应，通常不需要修改）：

```ini
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/xasset
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/xasset
```

> `.env` 已在 `.gitignore` 中，不会被提交到 git。

---

## 第五步：初始化数据库表结构

```bash
uv run alembic upgrade head
```

---

## 第六步：运行测试验证环境

不依赖数据库的单元测试：

```bash
uv run pytest tests/test_config.py tests/test_schemas.py -v
```

需要数据库的完整测试（确保 Docker 已启动）：

```bash
TEST_DB_URL=postgresql+asyncpg://postgres:password@localhost:5433/xasset_test \
uv run pytest -v
```

全部通过即表示环境就绪。

---

## 日常开发同步流程

```bash
# 开始工作前，拉取最新代码
git pull

# 工作完成后，推送到 GitHub
git add <文件>
git commit -m "..."
git push
```

---

## 切换到生产数据库

只需修改 `.env`，代码不需要任何改动：

```ini
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/xasset_prod
DATABASE_URL_SYNC=postgresql://<user>:<password>@<host>:5432/xasset_prod
```
