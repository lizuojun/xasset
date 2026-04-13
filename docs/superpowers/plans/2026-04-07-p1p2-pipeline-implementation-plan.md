# P1+P2 AI 生成 Pipeline & 基础设施实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建可扩展的 AI 资产生成 Pipeline 框架，以 house 场景布局逻辑端到端跑通验证。

**Architecture:** Stage 注册表 + Pipeline 编排器，Service 层封装所有外部依赖（Mesh 分析、Sample 检索、存储），Pipeline 只做纯计算不写 DB，所有持久化由 GenerationService 完成。当前阶段同步执行，接口语义为异步（submit → job_id → poll → result）。

**Tech Stack:** Python 3.11+, SQLAlchemy 2.0 async, aiosqlite, pytest + pytest-asyncio, uv

---

## 文件结构

```
xasset/
  pipeline/
    __init__.py
    context.py          # PipelineInput, PipelineContext, VariationInput, RoleTarget, AssetTarget
    stage.py            # Stage Protocol
    registry.py         # StageRegistry, StageNotFound
    pipeline.py         # Pipeline, PipelineConfig
    stages/
      __init__.py
      scene_understand.py  # SceneUnderstandStage(stub), SceneUnderstandOutput, SceneRegion
      layout_compose.py    # HouseLayoutComposeStage, LayoutOutput, PlacedGroup
      stylize.py           # StylizeStage(stub), StylizeOutput
  services/
    __init__.py
    mesh.py             # MeshService, PlacementZones, PlacementSlot
    sample_search.py    # SampleSearchService
    generation.py       # GenerationService
  jobs/
    __init__.py
    job.py              # Job, JobStatus, JobResult
    store.py            # InMemoryJobStore
  storage/
    __init__.py
    base.py             # StorageBackend Protocol
    local.py            # LocalFileStorage

tests/
  pipeline/
    __init__.py
    test_registry.py
    test_pipeline.py
    test_stages.py
  services/
    __init__.py
    test_mesh.py
    test_sample_search.py
    test_generation.py
  jobs/
    __init__.py
    test_job_store.py
  storage/
    __init__.py
    test_local_storage.py
  test_pipeline_integration.py
```

---

## Task 1：Job 层

**Files:**
- Create: `xasset/jobs/__init__.py`
- Create: `xasset/jobs/job.py`
- Create: `xasset/jobs/store.py`
- Create: `tests/jobs/__init__.py`
- Create: `tests/jobs/test_job_store.py`

- [ ] **Step 1: 写测试**

```python
# tests/jobs/test_job_store.py
import uuid
from datetime import datetime, timezone
from xasset.jobs.job import Job, JobStatus, JobResult
from xasset.jobs.store import InMemoryJobStore

def test_job_defaults():
    job = Job()
    assert job.status == "pending"
    assert job.id is not None
    assert job.result is None
    assert job.error is None

def test_job_store_create_and_get():
    store = InMemoryJobStore()
    job = Job()
    store.create(job)
    fetched = store.get(job.id)
    assert fetched is not None
    assert fetched.id == job.id

def test_job_store_get_missing_returns_none():
    store = InMemoryJobStore()
    assert store.get("nonexistent") is None

def test_job_store_update():
    store = InMemoryJobStore()
    job = Job()
    store.create(job)
    job.status = "done"
    store.update(job)
    assert store.get(job.id).status == "done"

def test_job_status_fields():
    status = JobStatus(job_id="abc", status="running", progress=0.5, message="stage 1")
    assert status.progress == 0.5

def test_job_result_fields():
    asset_id = uuid.uuid4()
    result = JobResult(job_id="abc", asset_id=asset_id, stage_outputs={"x": 1})
    assert result.asset_id == asset_id
    assert result.error is None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/jobs/test_job_store.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.jobs'`

- [ ] **Step 3: 实现 job.py**

```python
# xasset/jobs/job.py
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class JobStatus:
    job_id: str
    status: str          # "pending" | "running" | "done" | "failed"
    progress: float = 0.0
    message: str | None = None


@dataclass
class JobResult:
    job_id: str
    asset_id: uuid.UUID | None
    stage_outputs: dict[str, Any]
    error: str | None = None


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"      # "pending" | "running" | "done" | "failed"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    result: JobResult | None = None
    error: str | None = None
```

- [ ] **Step 4: 实现 store.py**

```python
# xasset/jobs/store.py
from xasset.jobs.job import Job


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self, job: Job) -> None:
        self._jobs[job.id] = job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def update(self, job: Job) -> None:
        self._jobs[job.id] = job
```

- [ ] **Step 5: 创建 `__init__.py` 文件**

```bash
# 创建空文件
echo "" > xasset/jobs/__init__.py
echo "" > tests/jobs/__init__.py
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/jobs/test_job_store.py -v
```
预期：`6 passed`

- [ ] **Step 7: Commit**

```bash
git add xasset/jobs/ tests/jobs/
git commit -m "feat: add Job layer (Job, JobStatus, JobResult, InMemoryJobStore)"
```

---

## Task 2：Storage 抽象层

**Files:**
- Create: `xasset/storage/__init__.py`
- Create: `xasset/storage/base.py`
- Create: `xasset/storage/local.py`
- Create: `tests/storage/__init__.py`
- Create: `tests/storage/test_local_storage.py`

- [ ] **Step 1: 写测试**

```python
# tests/storage/test_local_storage.py
import pytest
from pathlib import Path
from xasset.storage.local import LocalFileStorage


@pytest.fixture
def storage(tmp_path):
    return LocalFileStorage(tmp_path / "storage")


def test_put_and_get(storage):
    url = storage.put("assets/test.bin", b"hello world")
    assert url == "local://assets/test.bin"
    assert storage.get(url) == b"hello world"


def test_exists_true(storage):
    url = storage.put("file.txt", b"data")
    assert storage.exists(url) is True


def test_exists_false(storage):
    assert storage.exists("local://nonexistent.txt") is False


def test_delete(storage):
    url = storage.put("to_delete.bin", b"data")
    storage.delete(url)
    assert storage.exists(url) is False


def test_nested_key(storage):
    url = storage.put("a/b/c/file.bin", b"nested")
    assert storage.get(url) == b"nested"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/storage/test_local_storage.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.storage'`

- [ ] **Step 3: 实现 base.py**

```python
# xasset/storage/base.py
from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageBackend(Protocol):
    def put(self, key: str, data: bytes) -> str:
        """Store data under key. Returns URL of the form '<scheme>://<key>'."""
        ...

    def get(self, url: str) -> bytes:
        """Retrieve data by URL."""
        ...

    def exists(self, url: str) -> bool:
        """Return True if the URL exists in storage."""
        ...

    def delete(self, url: str) -> None:
        """Delete data at URL. No-op if not found."""
        ...
```

- [ ] **Step 4: 实现 local.py**

```python
# xasset/storage/local.py
from pathlib import Path


class LocalFileStorage:
    """File-system backed storage. URLs have the form local://<key>."""

    PREFIX = "local://"

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes) -> str:
        path = self.base_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"{self.PREFIX}{key}"

    def get(self, url: str) -> bytes:
        return self._path(url).read_bytes()

    def exists(self, url: str) -> bool:
        return self._path(url).exists()

    def delete(self, url: str) -> None:
        self._path(url).unlink(missing_ok=True)

    def _path(self, url: str) -> Path:
        key = url.removeprefix(self.PREFIX)
        return self.base_dir / key
```

- [ ] **Step 5: 创建 `__init__.py` 文件**

```bash
echo "" > xasset/storage/__init__.py
echo "" > tests/storage/__init__.py
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/storage/test_local_storage.py -v
```
预期：`5 passed`

- [ ] **Step 7: Commit**

```bash
git add xasset/storage/ tests/storage/
git commit -m "feat: add Storage abstraction layer (StorageBackend Protocol, LocalFileStorage)"
```

---

## Task 3：Pipeline 核心数据类型

**Files:**
- Create: `xasset/pipeline/__init__.py`
- Create: `xasset/pipeline/context.py`
- Create: `tests/pipeline/__init__.py`

- [ ] **Step 1: 写测试**

```python
# tests/pipeline/__init__.py  (空文件)
```

```python
# 在 tests/pipeline/ 下新建 test_context.py，放入以下内容
# tests/pipeline/test_context.py
import uuid
from xasset.pipeline.context import (
    PipelineInput, PipelineContext, VariationInput, RoleTarget, AssetTarget,
)


def test_pipeline_input_defaults():
    inp = PipelineInput(input_type="text", scene_type="house")
    assert inp.text_description is None
    assert inp.image_url is None
    assert inp.style is None
    assert inp.constraints == {}


def test_pipeline_context_stage_outputs_default_empty():
    inp = PipelineInput(input_type="text", scene_type="house")
    ctx = PipelineContext(job_id="j1", input=inp)
    assert ctx.stage_outputs == {}
    assert ctx.status == "running"
    assert ctx.error is None


def test_pipeline_context_stage_outputs_writable():
    inp = PipelineInput(input_type="text", scene_type="house")
    ctx = PipelineContext(job_id="j1", input=inp)
    ctx.stage_outputs["my_stage"] = {"result": 42}
    assert ctx.stage_outputs["my_stage"]["result"] == 42


def test_variation_input_defaults():
    v = VariationInput()
    assert v.replace_models is None
    assert v.replace_materials is None
    assert v.replace_lights is False
    assert v.replace_accessories is False


def test_role_target_fields():
    gid = uuid.uuid4()
    t = RoleTarget(group_instance_id=gid, role="sofa")
    assert t.role == "sofa"


def test_asset_target_fields():
    aid = uuid.uuid4()
    t = AssetTarget(asset_instance_id=aid)
    assert t.asset_instance_id == aid
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_context.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.pipeline'`

- [ ] **Step 3: 实现 context.py**

```python
# xasset/pipeline/context.py
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineInput:
    input_type: str               # "text" | "image" | "concept_art"
    scene_type: str               # "house" | "urban" | "wild"
    text_description: str | None = None
    image_url: str | None = None
    style: str | None = None
    constraints: dict = field(default_factory=dict)


@dataclass
class RoleTarget:
    """Identifies a role slot within a placed group for model replacement."""
    group_instance_id: uuid.UUID
    role: str                     # e.g. "sofa", "coffee_table"


@dataclass
class AssetTarget:
    """Identifies a specific asset instance for material/light replacement."""
    asset_instance_id: uuid.UUID


@dataclass
class VariationInput:
    replace_models: list[RoleTarget] | None = None
    replace_materials: list[AssetTarget] | None = None
    replace_lights: bool = False
    replace_accessories: bool = False
    style: str | None = None


@dataclass
class PipelineContext:
    job_id: str
    input: PipelineInput
    stage_outputs: dict[str, Any] = field(default_factory=dict)
    status: str = "running"       # "running" | "done" | "failed"
    error: str | None = None
```

- [ ] **Step 4: 创建 `__init__.py` 文件**

```bash
echo "" > xasset/pipeline/__init__.py
echo "" > xasset/pipeline/stages/__init__.py  # 提前建好，Task 6 会用到
mkdir -p xasset/pipeline/stages
echo "" > tests/pipeline/__init__.py
```

- [ ] **Step 5: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_context.py -v
```
预期：`6 passed`

- [ ] **Step 6: Commit**

```bash
git add xasset/pipeline/ tests/pipeline/
git commit -m "feat: add Pipeline core data types (PipelineInput, PipelineContext, VariationInput)"
```

---

## Task 4：Stage Protocol + StageRegistry

**Files:**
- Create: `xasset/pipeline/stage.py`
- Create: `xasset/pipeline/registry.py`
- Modify: `tests/pipeline/test_registry.py` (新建)

- [ ] **Step 1: 写测试**

```python
# tests/pipeline/test_registry.py
import pytest
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stage import Stage
from xasset.pipeline.registry import StageRegistry, StageNotFound


class _EchoStage:
    name = "echo"
    scene_types = ["house"]

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["echo"] = {"scene_type": ctx.input.scene_type}


class _WildcardStage:
    name = "wildcard"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        ctx.stage_outputs["wildcard"] = True


def _make_ctx(scene_type="house"):
    inp = PipelineInput(input_type="text", scene_type=scene_type)
    return PipelineContext(job_id="j1", input=inp)


def test_register_and_get():
    registry = StageRegistry()
    registry.register(_EchoStage())
    stage = registry.get("echo", "house")
    assert stage.name == "echo"


def test_get_missing_stage_raises():
    registry = StageRegistry()
    with pytest.raises(StageNotFound):
        registry.get("nonexistent", "house")


def test_get_wrong_scene_type_raises():
    registry = StageRegistry()
    registry.register(_EchoStage())
    with pytest.raises(StageNotFound):
        registry.get("echo", "urban")


def test_wildcard_scene_type_matches_any():
    registry = StageRegistry()
    registry.register(_WildcardStage())
    assert registry.get("wildcard", "house").name == "wildcard"
    assert registry.get("wildcard", "urban").name == "wildcard"
    assert registry.get("wildcard", "wild").name == "wildcard"


def test_specific_overrides_wildcard():
    """Scene-specific impl takes priority over wildcard."""
    class _HouseSpecific:
        name = "wildcard"
        scene_types = ["house"]
        def run(self, ctx): pass

    registry = StageRegistry()
    registry.register(_WildcardStage())
    registry.register(_HouseSpecific())
    assert registry.get("wildcard", "house").scene_types == ["house"]
    assert registry.get("wildcard", "urban").scene_types == ["*"]


def test_pipeline_for_returns_ordered_stages():
    from xasset.pipeline.pipeline import PipelineConfig
    registry = StageRegistry()
    registry.register(_EchoStage())
    registry.register(_WildcardStage())
    config = PipelineConfig(scene_type="house", stages=["wildcard", "echo"])
    stages = registry.pipeline_for(config)
    assert [s.name for s in stages] == ["wildcard", "echo"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_registry.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.pipeline.stage'`

- [ ] **Step 3: 实现 stage.py**

```python
# xasset/pipeline/stage.py
from typing import Protocol, runtime_checkable
from xasset.pipeline.context import PipelineContext


@runtime_checkable
class Stage(Protocol):
    name: str
    scene_types: list[str]       # ["house"] or ["*"] for all scene types

    def run(self, ctx: PipelineContext) -> None:
        """Execute stage logic. Write output to ctx.stage_outputs[self.name].
        Raise an exception to signal failure."""
        ...
```

- [ ] **Step 4: 实现 registry.py**

```python
# xasset/pipeline/registry.py
from xasset.pipeline.stage import Stage


class StageNotFound(Exception):
    pass


class StageRegistry:
    def __init__(self) -> None:
        # name → { scene_type → Stage }
        self._stages: dict[str, dict[str, Stage]] = {}

    def register(self, stage: Stage) -> "StageRegistry":
        if stage.name not in self._stages:
            self._stages[stage.name] = {}
        for scene_type in stage.scene_types:
            self._stages[stage.name][scene_type] = stage
        return self

    def get(self, name: str, scene_type: str) -> Stage:
        if name not in self._stages:
            raise StageNotFound(f"Stage '{name}' not registered")
        bucket = self._stages[name]
        if scene_type in bucket:
            return bucket[scene_type]
        if "*" in bucket:
            return bucket["*"]
        raise StageNotFound(
            f"Stage '{name}' has no implementation for scene_type='{scene_type}'"
        )

    def pipeline_for(self, config: "PipelineConfig") -> list[Stage]:  # type: ignore[name-defined]
        from xasset.pipeline.pipeline import PipelineConfig  # avoid circular import
        return [self.get(name, config.scene_type) for name in config.stages]
```

- [ ] **Step 5: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_registry.py -v
```
预期：`6 passed`

- [ ] **Step 6: Commit**

```bash
git add xasset/pipeline/stage.py xasset/pipeline/registry.py tests/pipeline/test_registry.py
git commit -m "feat: add Stage Protocol and StageRegistry with scene_type dispatch"
```

---

## Task 5：Pipeline 编排器

**Files:**
- Create: `xasset/pipeline/pipeline.py`
- Create: `tests/pipeline/test_pipeline.py`

- [ ] **Step 1: 写测试**

```python
# tests/pipeline/test_pipeline.py
import pytest
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry


class _WriteStage:
    def __init__(self, name, value):
        self.name = name
        self.scene_types = ["*"]
        self._value = value

    def run(self, ctx):
        ctx.stage_outputs[self.name] = self._value


class _FailStage:
    name = "fail"
    scene_types = ["*"]

    def run(self, ctx):
        raise ValueError("intentional failure")


class _ReadPreviousStage:
    name = "reader"
    scene_types = ["*"]

    def run(self, ctx):
        ctx.stage_outputs["reader"] = ctx.stage_outputs.get("writer")


def _make_input(scene_type="house"):
    return PipelineInput(input_type="text", scene_type=scene_type)


def test_pipeline_runs_stages_in_order():
    registry = StageRegistry()
    registry.register(_WriteStage("writer", "written"))
    registry.register(_ReadPreviousStage())
    config = PipelineConfig(scene_type="house", stages=["writer", "reader"])
    pipeline = Pipeline(registry)
    ctx = pipeline.run(_make_input(), config)
    assert ctx.stage_outputs["reader"] == "written"


def test_pipeline_sets_status_done_on_success():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"


def test_pipeline_sets_status_failed_on_error():
    registry = StageRegistry()
    registry.register(_FailStage())
    config = PipelineConfig(scene_type="house", stages=["fail"])
    with pytest.raises(ValueError, match="intentional failure"):
        Pipeline(registry).run(_make_input(), config)


def test_pipeline_uses_provided_job_id():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config, job_id="my-job")
    assert ctx.job_id == "my-job"


def test_pipeline_generates_job_id_if_not_provided():
    registry = StageRegistry()
    registry.register(_WriteStage("s1", 1))
    config = PipelineConfig(scene_type="house", stages=["s1"])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.job_id is not None and len(ctx.job_id) > 0


def test_empty_stage_list_returns_done():
    registry = StageRegistry()
    config = PipelineConfig(scene_type="house", stages=[])
    ctx = Pipeline(registry).run(_make_input(), config)
    assert ctx.status == "done"
    assert ctx.stage_outputs == {}
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_pipeline.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.pipeline.pipeline'`

- [ ] **Step 3: 实现 pipeline.py**

```python
# xasset/pipeline/pipeline.py
import uuid
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.registry import StageRegistry


@dataclass
class PipelineConfig:
    scene_type: str
    stages: list[str]
    stage_configs: dict[str, dict] = field(default_factory=dict)


class Pipeline:
    def __init__(self, registry: StageRegistry) -> None:
        self._registry = registry

    def run(
        self,
        input: PipelineInput,
        config: PipelineConfig,
        job_id: str | None = None,
    ) -> PipelineContext:
        """Execute all stages in order. Returns PipelineContext.
        Raises the stage exception on failure (after setting ctx.status='failed')."""
        ctx = PipelineContext(
            job_id=job_id or str(uuid.uuid4()),
            input=input,
        )
        try:
            for stage_name in config.stages:
                stage = self._registry.get(stage_name, config.scene_type)
                stage.run(ctx)
            ctx.status = "done"
        except Exception as exc:
            ctx.status = "failed"
            ctx.error = str(exc)
            raise
        return ctx
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_pipeline.py -v
```
预期：`6 passed`

- [ ] **Step 5: Commit**

```bash
git add xasset/pipeline/pipeline.py tests/pipeline/test_pipeline.py
git commit -m "feat: add Pipeline orchestrator and PipelineConfig"
```

---

## Task 6：Stage Output 类型 + Stub 实现

**Files:**
- Create: `xasset/pipeline/stages/scene_understand.py`
- Create: `xasset/pipeline/stages/layout_compose.py`  ← 只定义输出类型和占位方法，Task 9 填充实现
- Create: `xasset/pipeline/stages/stylize.py`
- Create: `tests/pipeline/test_stages.py`

- [ ] **Step 1: 写测试**

```python
# tests/pipeline/test_stages.py
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandStage, SceneUnderstandOutput, SceneRegion,
)
from xasset.pipeline.stages.stylize import StylizeStage, StylizeOutput


def _ctx(scene_type="house", style=None):
    inp = PipelineInput(input_type="text", scene_type=scene_type, style=style)
    return PipelineContext(job_id="j1", input=inp)


def test_scene_understand_stub_returns_output():
    stage = SceneUnderstandStage()
    ctx = _ctx(scene_type="house", style="现代简约")
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["scene_understand"]
    assert isinstance(out, SceneUnderstandOutput)
    assert out.scene_type == "house"
    assert len(out.regions) > 0


def test_scene_understand_stub_region_fields():
    stage = SceneUnderstandStage()
    ctx = _ctx()
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["scene_understand"]
    region: SceneRegion = out.regions[0]
    assert region.region_type in ("living_room", "bedroom", "dining_room")
    assert region.area > 0
    assert len(region.boundary) >= 3


def test_scene_understand_preserves_style():
    stage = SceneUnderstandStage()
    ctx = _ctx(style="北欧")
    stage.run(ctx)
    out: SceneUnderstandOutput = ctx.stage_outputs["scene_understand"]
    assert out.style == "北欧"


def test_stylize_stub_returns_output():
    stage = StylizeStage()
    ctx = _ctx()
    stage.run(ctx)
    out: StylizeOutput = ctx.stage_outputs["stylize"]
    assert isinstance(out, StylizeOutput)


def test_stage_name_and_scene_types():
    assert SceneUnderstandStage.name == "scene_understand"
    assert "*" in SceneUnderstandStage.scene_types
    assert StylizeStage.name == "stylize"
    assert "*" in StylizeStage.scene_types
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_stages.py -v
```
预期：`ModuleNotFoundError`

- [ ] **Step 3: 实现 scene_understand.py**

```python
# xasset/pipeline/stages/scene_understand.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class SceneRegion:
    region_type: str             # "living_room" | "bedroom" | "dining_room" | etc.
    boundary: list[list[float]]  # 多边形顶点列表，XZ 平面，Y-up，单位 cm
    area: float                  # m²


@dataclass
class SceneUnderstandOutput:
    scene_type: str
    regions: list[SceneRegion]
    style: str | None = None
    constraints: dict = field(default_factory=dict)


class SceneUnderstandStage:
    name = "scene_understand"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns a fixed living room region for any house input."""
        ctx.stage_outputs["scene_understand"] = SceneUnderstandOutput(
            scene_type=ctx.input.scene_type,
            style=ctx.input.style,
            regions=[
                SceneRegion(
                    region_type="living_room",
                    boundary=[[0, 0, 0], [500, 0, 0], [500, 0, 400], [0, 0, 400]],
                    area=20.0,
                )
            ],
        )
```

- [ ] **Step 4: 实现 stylize.py**

```python
# xasset/pipeline/stages/stylize.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class StylizeOutput:
    material_assignments: list[dict] = field(default_factory=list)
    light_config: dict | None = None
    camera_hints: list[dict] = field(default_factory=list)


class StylizeStage:
    name = "stylize"
    scene_types = ["*"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns empty stylize output."""
        ctx.stage_outputs["stylize"] = StylizeOutput()
```

- [ ] **Step 5: 创建 layout_compose.py 的输出类型占位（实现在 Task 9）**

```python
# xasset/pipeline/stages/layout_compose.py
from dataclasses import dataclass, field
from xasset.pipeline.context import PipelineContext


@dataclass
class PlacedGroup:
    group_code: int              # references GroupDefinition.code
    region_type: str
    position: list[float]        # [x, y, z] group anchor, unit cm
    rotation: float              # Y-axis rotation in degrees
    role_assets: dict[str, str | None] = field(default_factory=dict)
    # role_name → asset_id string (None if unassigned)


@dataclass
class LayoutOutput:
    scene_type: str
    placed_groups: list[PlacedGroup] = field(default_factory=list)


class HouseLayoutComposeStage:
    name = "layout_compose"
    scene_types = ["house"]

    def run(self, ctx: PipelineContext) -> None:
        """Stub: returns empty layout. Full implementation in Task 9."""
        ctx.stage_outputs["layout_compose"] = LayoutOutput(
            scene_type=ctx.input.scene_type,
        )
```

- [ ] **Step 6: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_stages.py -v
```
预期：`5 passed`

- [ ] **Step 7: Commit**

```bash
git add xasset/pipeline/stages/ tests/pipeline/test_stages.py
git commit -m "feat: add Stage output types and stub implementations (SceneUnderstand, Stylize, LayoutCompose)"
```

---

## Task 7：MeshService

**Files:**
- Create: `xasset/services/__init__.py`
- Create: `xasset/services/mesh.py`
- Create: `tests/services/__init__.py`
- Create: `tests/services/test_mesh.py`

- [ ] **Step 1: 写测试**

```python
# tests/services/test_mesh.py
from xasset.services.mesh import MeshService, PlacementZones, PlacementSlot
from xasset.models.asset import AssetDefinition


def _make_asset(object_type="house/room/furniture/sofa", computed_features=None, raw_data=None):
    asset = AssetDefinition.__new__(AssetDefinition)
    asset.object_type = object_type
    asset.computed_features = computed_features
    asset.raw_data = raw_data or {}
    return asset


def test_no_geometry_returns_empty_zones():
    service = MeshService()
    asset = _make_asset(raw_data={})
    zones = service.get_placement_zones(asset)
    assert zones.top == []
    assert zones.back == []
    assert zones.front == []


def test_cache_hit_returns_cached_zones():
    service = MeshService()
    cached = {
        "top": [{"surface_type": "top", "center": [0, 80, 0], "size": [60, 0, 40], "height": 80.0}],
        "back": [],
        "front": [],
    }
    asset = _make_asset(computed_features={"placement_zones": cached})
    zones = service.get_placement_zones(asset)
    assert len(zones.top) == 1
    assert zones.top[0].surface_type == "top"
    assert zones.top[0].height == 80.0


def test_force_recompute_bypasses_cache():
    service = MeshService()
    cached = {
        "top": [{"surface_type": "top", "center": [0, 80, 0], "size": [60, 0, 40], "height": 80.0}],
        "back": [],
        "front": [],
    }
    asset = _make_asset(computed_features={"placement_zones": cached})
    # force_recompute=True skips cache; no geometry → empty zones
    zones = service.get_placement_zones(asset, force_recompute=True)
    assert zones.top == []


def test_result_written_to_computed_features():
    service = MeshService()
    asset = _make_asset()
    service.get_placement_zones(asset)
    assert "placement_zones" in asset.computed_features


def test_placement_slot_fields():
    slot = PlacementSlot(surface_type="top", center=[0, 80, 0], size=[60, 0, 40], height=80.0)
    assert slot.surface_type == "top"
    assert slot.height == 80.0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/services/test_mesh.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.services'`

- [ ] **Step 3: 实现 mesh.py**

```python
# xasset/services/mesh.py
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PlacementSlot:
    surface_type: str            # "top" | "back" | "front"
    center: list[float]          # [x, y, z] in object local space, unit cm
    size: list[float]            # [w, h, d] available area
    height: float                # height above bbox.min.y


@dataclass
class PlacementZones:
    top: list[PlacementSlot]
    back: list[PlacementSlot]
    front: list[PlacementSlot]


def _zones_to_dict(zones: PlacementZones) -> dict:
    def slots(lst):
        return [
            {"surface_type": s.surface_type, "center": s.center,
             "size": s.size, "height": s.height}
            for s in lst
        ]
    return {"top": slots(zones.top), "back": slots(zones.back), "front": slots(zones.front)}


def _dict_to_zones(d: dict) -> PlacementZones:
    def slots(lst):
        return [PlacementSlot(**item) for item in lst]
    return PlacementZones(
        top=slots(d.get("top", [])),
        back=slots(d.get("back", [])),
        front=slots(d.get("front", [])),
    )


class MeshService:
    """Synchronous mesh analysis service.

    Checks AssetDefinition.computed_features for cached PlacementZones.
    On cache miss, computes via GLM adapter (if geometry is available).
    Updates asset.computed_features in-memory; caller must commit to DB.
    """

    def get_placement_zones(
        self,
        asset: "AssetDefinition",  # type: ignore[name-defined]
        force_recompute: bool = False,
    ) -> PlacementZones:
        if not force_recompute and asset.computed_features:
            cached = asset.computed_features.get("placement_zones")
            if cached:
                return _dict_to_zones(cached)

        zones = self._compute(asset)

        features = dict(asset.computed_features or {})
        features["placement_zones"] = _zones_to_dict(zones)
        asset.computed_features = features

        return zones

    def _compute(self, asset: "AssetDefinition") -> PlacementZones:  # type: ignore[name-defined]
        """Compute placement zones from mesh geometry.
        Returns empty zones if no geometry is available."""
        raw_data = asset.raw_data or {}
        geometry_url = raw_data.get("geometry_url", "")
        if not geometry_url or not geometry_url.startswith("local://"):
            return PlacementZones(top=[], back=[], front=[])
        return self._compute_from_obj(geometry_url, asset.object_type or "")

    def _compute_from_obj(self, geometry_url: str, object_type: str) -> PlacementZones:
        """Use GLM adapter to compute placement zones from OBJ file."""
        try:
            _ref = Path(__file__).parent.parent.parent / "ref"
            if str(_ref) not in sys.path:
                sys.path.insert(0, str(_ref))
            from Furniture.glm_interface import glm_read_obj
            from Furniture.glm_shape import glm_shape_obj
        except ImportError:
            return PlacementZones(top=[], back=[], front=[])

        local_path = geometry_url.removeprefix("local://")
        model = glm_read_obj(local_path)
        if not model:
            return PlacementZones(top=[], back=[], front=[])

        decor_bot, decor_bak, decor_frt, ratio = glm_shape_obj(model, type=object_type)
        return PlacementZones(
            top=self._slots_from_glm(decor_bot, "top"),
            back=self._slots_from_glm(decor_bak, "back"),
            front=self._slots_from_glm(decor_frt, "front"),
        )

    def _slots_from_glm(self, decor: dict, surface_type: str) -> list[PlacementSlot]:
        slots = []
        for height_key, items in decor.items():
            for item in items:
                if len(item) >= 7:
                    slots.append(PlacementSlot(
                        surface_type=surface_type,
                        center=[item[0], item[1], item[2]],
                        size=[abs(item[3] - item[0]), 0, abs(item[5] - item[2])],
                        height=float(height_key),
                    ))
        return slots
```

- [ ] **Step 4: 创建 `__init__.py` 文件**

```bash
echo "" > xasset/services/__init__.py
echo "" > tests/services/__init__.py
```

- [ ] **Step 5: 运行测试确认通过**

```bash
uv run pytest tests/services/test_mesh.py -v
```
预期：`5 passed`

- [ ] **Step 6: Commit**

```bash
git add xasset/services/__init__.py xasset/services/mesh.py tests/services/__init__.py tests/services/test_mesh.py
git commit -m "feat: add MeshService with GLM adapter and computed_features cache"
```

---

## Task 8：SampleSearchService

**Files:**
- Create: `xasset/services/sample_search.py`
- Create: `tests/services/test_sample_search.py`

- [ ] **Step 1: 写测试**

```python
# tests/services/test_sample_search.py
import math
from xasset.models.sample import STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM
from xasset.services.sample_search import SampleSearchService


def _make_sample(style, style_vector, scene_type="house", sample_level="zone"):
    from xasset.models.sample import Sample
    s = Sample.__new__(Sample)
    s.style = style
    s.scene_type = scene_type
    s.sample_level = sample_level
    s.style_vector = style_vector
    s.partition_vector = [0.0] * PARTITION_VECTOR_DIM
    s.score = 80
    return s


def test_find_by_style_returns_closest():
    samples = [
        _make_sample("现代", [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1)),
        _make_sample("古典", [0.0] * STYLE_VECTOR_DIM),
    ]
    service = SampleSearchService(samples)
    results = service.find_by_style(
        scene_type="house",
        sample_level="zone",
        style_vector=[1.0] + [0.0] * (STYLE_VECTOR_DIM - 1),
        limit=1,
    )
    assert len(results) == 1
    assert results[0].style == "现代"


def test_find_by_style_filters_scene_type():
    samples = [
        _make_sample("现代", [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1), scene_type="urban"),
        _make_sample("古典", [0.0] * STYLE_VECTOR_DIM, scene_type="house"),
    ]
    service = SampleSearchService(samples)
    results = service.find_by_style(
        scene_type="house",
        sample_level="zone",
        style_vector=[1.0] + [0.0] * (STYLE_VECTOR_DIM - 1),
    )
    assert all(s.scene_type == "house" for s in results)


def test_find_by_style_empty_samples():
    service = SampleSearchService([])
    results = service.find_by_style("house", "zone", [0.0] * STYLE_VECTOR_DIM)
    assert results == []


def test_find_by_style_cache_hit():
    samples = [_make_sample("现代", [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1))]
    service = SampleSearchService(samples)
    query = [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1)
    r1 = service.find_by_style("house", "zone", query, limit=1)
    r2 = service.find_by_style("house", "zone", query, limit=1)
    assert r1 == r2
    assert service.cache_hits == 1


def test_add_samples_clears_cache():
    samples = [_make_sample("现代", [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1))]
    service = SampleSearchService(samples)
    query = [1.0] + [0.0] * (STYLE_VECTOR_DIM - 1)
    service.find_by_style("house", "zone", query)
    new_sample = _make_sample("新样式", [0.5] + [0.0] * (STYLE_VECTOR_DIM - 1))
    service.add_samples([new_sample])
    # Cache should be cleared after adding samples
    assert service.cache_hits == 0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/services/test_sample_search.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.services.sample_search'`

- [ ] **Step 3: 实现 sample_search.py**

```python
# xasset/services/sample_search.py
import hashlib
import json
import math


def _cosine_distance(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


def _cache_key(scene_type: str, sample_level: str, vector: list[float], limit: int) -> str:
    v_hash = hashlib.md5(json.dumps(vector, separators=(",", ":")).encode()).hexdigest()
    return f"{scene_type}:{sample_level}:{limit}:{v_hash}"


class SampleSearchService:
    """Synchronous in-memory sample search with LRU-style cache.

    Pre-seeded with Sample objects; caller is responsible for loading from DB.
    """

    def __init__(self, samples: list) -> None:
        self._samples = list(samples)
        self._style_cache: dict[str, list] = {}
        self._partition_cache: dict[str, list] = {}
        self.cache_hits = 0

    def add_samples(self, samples: list) -> None:
        """Add samples and invalidate all caches."""
        self._samples.extend(samples)
        self._style_cache.clear()
        self._partition_cache.clear()
        self.cache_hits = 0

    def find_by_style(
        self,
        scene_type: str,
        sample_level: str,
        style_vector: list[float],
        limit: int = 10,
    ) -> list:
        key = _cache_key(scene_type, sample_level, style_vector, limit)
        if key in self._style_cache:
            self.cache_hits += 1
            return self._style_cache[key]

        candidates = [
            s for s in self._samples
            if s.scene_type == scene_type
            and s.sample_level == sample_level
            and s.style_vector is not None
        ]
        candidates.sort(key=lambda s: _cosine_distance(style_vector, s.style_vector))
        result = candidates[:limit]
        self._style_cache[key] = result
        return result

    def find_by_partition(
        self,
        scene_type: str,
        partition_vector: list[float],
        limit: int = 10,
    ) -> list:
        key = _cache_key(scene_type, "any", partition_vector, limit)
        if key in self._partition_cache:
            self.cache_hits += 1
            return self._partition_cache[key]

        candidates = [
            s for s in self._samples
            if s.scene_type == scene_type
            and s.partition_vector is not None
        ]
        candidates.sort(key=lambda s: _cosine_distance(partition_vector, s.partition_vector))
        result = candidates[:limit]
        self._partition_cache[key] = result
        return result
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/services/test_sample_search.py -v
```
预期：`5 passed`

- [ ] **Step 5: Commit**

```bash
git add xasset/services/sample_search.py tests/services/test_sample_search.py
git commit -m "feat: add SampleSearchService with in-memory cosine search and LRU cache"
```

---

## Task 9：HouseLayoutComposeStage（实现）

**Files:**
- Modify: `xasset/pipeline/stages/layout_compose.py`
- Create: `tests/pipeline/test_layout_compose.py`

- [ ] **Step 1: 写测试**

```python
# tests/pipeline/test_layout_compose.py
from xasset.pipeline.context import PipelineInput, PipelineContext
from xasset.pipeline.stages.scene_understand import (
    SceneUnderstandOutput, SceneRegion,
)
from xasset.pipeline.stages.layout_compose import (
    HouseLayoutComposeStage, LayoutOutput, PlacedGroup,
)
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService


def _ctx_with_scene(region_type="living_room", style=None):
    inp = PipelineInput(input_type="text", scene_type="house", style=style)
    ctx = PipelineContext(job_id="j1", input=inp)
    ctx.stage_outputs["scene_understand"] = SceneUnderstandOutput(
        scene_type="house",
        style=style,
        regions=[
            SceneRegion(
                region_type=region_type,
                boundary=[[0, 0, 0], [500, 0, 0], [500, 0, 400], [0, 0, 400]],
                area=20.0,
            )
        ],
    )
    return ctx


def _make_stage():
    mesh_svc = MeshService()
    sample_svc = SampleSearchService([])
    return HouseLayoutComposeStage(mesh_service=mesh_svc, sample_search=sample_svc)


def test_stage_name_and_scene_types():
    assert HouseLayoutComposeStage.name == "layout_compose"
    assert "house" in HouseLayoutComposeStage.scene_types


def test_returns_layout_output():
    stage = _make_stage()
    ctx = _ctx_with_scene()
    stage.run(ctx)
    out = ctx.stage_outputs["layout_compose"]
    assert isinstance(out, LayoutOutput)
    assert out.scene_type == "house"


def test_living_room_gets_meeting_group():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="living_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    assert len(out.placed_groups) > 0
    group = out.placed_groups[0]
    assert isinstance(group, PlacedGroup)
    assert group.group_code == 100001   # house-meeting group code
    assert group.region_type == "living_room"


def test_placed_group_has_position():
    stage = _make_stage()
    ctx = _ctx_with_scene()
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    group = out.placed_groups[0]
    assert len(group.position) == 3


def test_unknown_region_type_produces_no_groups():
    stage = _make_stage()
    ctx = _ctx_with_scene(region_type="storage_room")
    stage.run(ctx)
    out: LayoutOutput = ctx.stage_outputs["layout_compose"]
    assert out.placed_groups == []
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/pipeline/test_layout_compose.py -v
```
预期：`TypeError: HouseLayoutComposeStage() takes no arguments` または `AssertionError`

- [ ] **Step 3: 实现 layout_compose.py**

```python
# xasset/pipeline/stages/layout_compose.py
from dataclasses import dataclass, field
from pathlib import Path

from xasset.pipeline.context import PipelineContext
from xasset.pipeline.stages.scene_understand import SceneUnderstandOutput, SceneRegion
from xasset.config.loader import load_group_configs, get_group_by_code
from xasset.config.schemas import GroupDefinition

# 房间类型 → GroupDefinition code 映射
_REGION_TO_GROUP: dict[str, int] = {
    "living_room": 100001,    # house-meeting（会客组）
}

# GroupDefinition 配置目录
_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "groups"


@dataclass
class PlacedGroup:
    group_code: int
    region_type: str
    position: list[float]          # [x, y, z] group anchor, unit cm
    rotation: float                # Y-axis rotation in degrees
    role_assets: dict[str, str | None] = field(default_factory=dict)
    # role_name → asset_id string or None if not yet assigned


@dataclass
class LayoutOutput:
    scene_type: str
    placed_groups: list[PlacedGroup] = field(default_factory=list)


class HouseLayoutComposeStage:
    name = "layout_compose"
    scene_types = ["house"]

    def __init__(self, mesh_service, sample_search) -> None:
        self._mesh = mesh_service
        self._sample_search = sample_search
        load_group_configs(_DATA_DIR)

    def run(self, ctx: PipelineContext) -> None:
        scene_out: SceneUnderstandOutput | None = ctx.stage_outputs.get("scene_understand")
        placed_groups: list[PlacedGroup] = []

        regions = scene_out.regions if scene_out else []
        for region in regions:
            group_code = _REGION_TO_GROUP.get(region.region_type)
            if group_code is None:
                continue
            group_def = get_group_by_code("house", group_code)
            if group_def is None:
                continue
            placed = self._place_group(group_def, region)
            placed_groups.append(placed)

        ctx.stage_outputs["layout_compose"] = LayoutOutput(
            scene_type=ctx.input.scene_type,
            placed_groups=placed_groups,
        )

    def _place_group(self, group_def: GroupDefinition, region: SceneRegion) -> PlacedGroup:
        # Compute anchor position: center of region boundary at floor level
        xs = [v[0] for v in region.boundary]
        zs = [v[2] for v in region.boundary]
        cx = (min(xs) + max(xs)) / 2
        cz = (min(zs) + max(zs)) / 2

        role_assets: dict[str, str | None] = {
            role.name: None for role in group_def.roles
        }

        return PlacedGroup(
            group_code=group_def.code,
            region_type=region.region_type,
            position=[cx, 0.0, cz],
            rotation=0.0,
            role_assets=role_assets,
        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/pipeline/test_layout_compose.py -v
```
预期：`5 passed`

- [ ] **Step 5: 运行全套测试确认无回归**

```bash
uv run pytest tests/ -v
```
预期：全部通过

- [ ] **Step 6: Commit**

```bash
git add xasset/pipeline/stages/layout_compose.py tests/pipeline/test_layout_compose.py
git commit -m "feat: implement HouseLayoutComposeStage with GroupDefinition-based layout"
```

---

## Task 10：GenerationService

**Files:**
- Create: `xasset/services/generation.py`
- Create: `tests/services/test_generation.py`

- [ ] **Step 1: 写测试**

```python
# tests/services/test_generation.py
import pytest
from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.services.generation import GenerationService
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService
from xasset.jobs.store import InMemoryJobStore
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage
from xasset.pipeline.stages.stylize import StylizeStage


def _make_service():
    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(HouseLayoutComposeStage(
        mesh_service=MeshService(),
        sample_search=SampleSearchService([]),
    ))
    registry.register(StylizeStage())
    pipeline = Pipeline(registry)
    job_store = InMemoryJobStore()
    return GenerationService(pipeline=pipeline, job_store=job_store)


def test_submit_returns_job_id():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house", text_description="客厅")
    job_id = service.submit(inp)
    assert isinstance(job_id, str)
    assert len(job_id) > 0


def test_get_status_done_after_sync_submit():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    status = service.get_status(job_id)
    assert status.status == "done"
    assert status.job_id == job_id


def test_get_result_has_stage_outputs():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)
    assert result.job_id == job_id
    assert "layout_compose" in result.stage_outputs


def test_get_status_unknown_job_raises():
    service = _make_service()
    with pytest.raises(KeyError):
        service.get_status("nonexistent-job-id")


def test_submit_with_custom_config():
    service = _make_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["scene_understand"])
    job_id = service.submit(inp, config=config)
    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" not in result.stage_outputs


def test_submit_variation_returns_job_id():
    import uuid
    service = _make_service()
    variation = VariationInput(replace_accessories=True)
    job_id = service.submit_variation(
        source_asset_id=uuid.uuid4(),
        variation=variation,
    )
    assert isinstance(job_id, str)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/services/test_generation.py -v
```
预期：`ModuleNotFoundError: No module named 'xasset.services.generation'`

- [ ] **Step 3: 实现 generation.py**

```python
# xasset/services/generation.py
import uuid
from datetime import datetime, timezone

from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.jobs.job import Job, JobResult, JobStatus
from xasset.jobs.store import InMemoryJobStore


_DEFAULT_HOUSE_STAGES = ["scene_understand", "layout_compose", "stylize"]


class GenerationService:
    """Main entry point for asset generation.

    submit() is synchronous internally but exposes async-compatible semantics
    (submit → job_id → get_status → get_result).
    """

    def __init__(self, pipeline: Pipeline, job_store: InMemoryJobStore) -> None:
        self._pipeline = pipeline
        self._job_store = job_store

    def submit(
        self,
        input: PipelineInput,
        config: PipelineConfig | None = None,
    ) -> str:
        """Run the pipeline synchronously and store the result. Returns job_id."""
        job = Job()
        job.status = "running"
        self._job_store.create(job)

        if config is None:
            stages = _DEFAULT_HOUSE_STAGES if input.scene_type == "house" else []
            config = PipelineConfig(scene_type=input.scene_type, stages=stages)

        try:
            ctx = self._pipeline.run(input, config, job_id=job.id)
            job.status = "done"
            job.finished_at = datetime.now(timezone.utc)
            job.result = JobResult(
                job_id=job.id,
                asset_id=None,
                stage_outputs=ctx.stage_outputs,
            )
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = datetime.now(timezone.utc)

        self._job_store.update(job)
        return job.id

    def submit_variation(
        self,
        source_asset_id: uuid.UUID,
        variation: VariationInput,
    ) -> str:
        """Run a partial pipeline to produce a variation of an existing asset.

        Which stages run is determined by the variation flags.
        Whether the result is saved as a new AssetDefinition is the caller's decision.
        """
        stages: list[str] = []
        if variation.replace_models or variation.replace_accessories:
            stages.append("layout_compose")
        if variation.replace_materials or variation.replace_lights:
            stages.append("stylize")
        if not stages:
            stages = ["stylize"]

        inp = PipelineInput(
            input_type="text",
            scene_type="house",
            constraints={"source_asset_id": str(source_asset_id)},
            style=variation.style,
        )
        config = PipelineConfig(scene_type="house", stages=stages)
        return self.submit(inp, config=config)

    def get_status(self, job_id: str) -> JobStatus:
        job = self._job_store.get(job_id)
        if job is None:
            raise KeyError(f"Job '{job_id}' not found")
        return JobStatus(
            job_id=job.id,
            status=job.status,
            progress=1.0 if job.status in ("done", "failed") else 0.5,
            message=job.error,
        )

    def get_result(self, job_id: str) -> JobResult:
        job = self._job_store.get(job_id)
        if job is None:
            raise KeyError(f"Job '{job_id}' not found")
        if job.result is None:
            return JobResult(
                job_id=job.id,
                asset_id=None,
                stage_outputs={},
                error=job.error,
            )
        return job.result

    def cancel(self, job_id: str) -> None:
        """No-op for synchronous execution. Reserved for future async queue."""
        pass
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/services/test_generation.py -v
```
预期：`6 passed`

- [ ] **Step 5: Commit**

```bash
git add xasset/services/generation.py tests/services/test_generation.py
git commit -m "feat: add GenerationService (submit, get_status, get_result, submit_variation)"
```

---

## Task 11：端到端集成测试

**Files:**
- Create: `tests/test_pipeline_integration.py`

- [ ] **Step 1: 写测试**

```python
# tests/test_pipeline_integration.py
"""
端到端验证：文字描述 → Pipeline → house 布局结果
"""
from xasset.pipeline.context import PipelineInput, VariationInput
from xasset.pipeline.pipeline import Pipeline, PipelineConfig
from xasset.pipeline.registry import StageRegistry
from xasset.pipeline.stages.scene_understand import SceneUnderstandStage, SceneUnderstandOutput
from xasset.pipeline.stages.layout_compose import HouseLayoutComposeStage, LayoutOutput
from xasset.pipeline.stages.stylize import StylizeStage, StylizeOutput
from xasset.services.generation import GenerationService
from xasset.services.mesh import MeshService
from xasset.services.sample_search import SampleSearchService
from xasset.jobs.store import InMemoryJobStore
import uuid


def _make_full_service():
    registry = StageRegistry()
    registry.register(SceneUnderstandStage())
    registry.register(HouseLayoutComposeStage(
        mesh_service=MeshService(),
        sample_search=SampleSearchService([]),
    ))
    registry.register(StylizeStage())
    return GenerationService(
        pipeline=Pipeline(registry),
        job_store=InMemoryJobStore(),
    )


def test_full_house_pipeline_end_to_end():
    """文字描述 → 完整 Pipeline → 三个 Stage 都产生输出"""
    service = _make_full_service()
    inp = PipelineInput(
        input_type="text",
        scene_type="house",
        text_description="一个现代简约风格的客厅，约20平方米",
        style="现代简约",
    )
    job_id = service.submit(inp)

    status = service.get_status(job_id)
    assert status.status == "done"

    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" in result.stage_outputs
    assert "stylize" in result.stage_outputs


def test_scene_understand_output_structure():
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house", style="北欧")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: SceneUnderstandOutput = result.stage_outputs["scene_understand"]
    assert out.scene_type == "house"
    assert out.style == "北欧"
    assert len(out.regions) > 0


def test_layout_output_has_placed_groups():
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: LayoutOutput = result.stage_outputs["layout_compose"]
    assert isinstance(out, LayoutOutput)
    assert len(out.placed_groups) > 0
    group = out.placed_groups[0]
    assert group.group_code == 100001
    assert group.region_type == "living_room"
    assert len(group.position) == 3


def test_layout_group_has_all_roles():
    """会客组 (100001) 应包含 sofa, coffee_table, rug, accessory 四个角色"""
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    job_id = service.submit(inp)
    result = service.get_result(job_id)

    out: LayoutOutput = result.stage_outputs["layout_compose"]
    group = out.placed_groups[0]
    assert "sofa" in group.role_assets
    assert "coffee_table" in group.role_assets


def test_variation_pipeline_skips_scene_understand():
    """变体生成不执行 scene_understand Stage"""
    service = _make_full_service()
    variation = VariationInput(replace_accessories=True)
    job_id = service.submit_variation(
        source_asset_id=uuid.uuid4(),
        variation=variation,
    )
    result = service.get_result(job_id)
    assert "scene_understand" not in result.stage_outputs
    assert "layout_compose" in result.stage_outputs


def test_partial_pipeline_config():
    """只跑 scene_understand，layout_compose 不执行"""
    service = _make_full_service()
    inp = PipelineInput(input_type="text", scene_type="house")
    config = PipelineConfig(scene_type="house", stages=["scene_understand"])
    job_id = service.submit(inp, config=config)
    result = service.get_result(job_id)
    assert "scene_understand" in result.stage_outputs
    assert "layout_compose" not in result.stage_outputs
```

- [ ] **Step 2: 运行测试确认通过**

```bash
uv run pytest tests/test_pipeline_integration.py -v
```
预期：`6 passed`

- [ ] **Step 3: 运行全套测试**

```bash
uv run pytest tests/ -v
```
预期：全部通过（包含 P0 的 29 个测试）

- [ ] **Step 4: Commit**

```bash
git add tests/test_pipeline_integration.py
git commit -m "test: add end-to-end pipeline integration tests for P1+P2"
```

---

## 验证清单

P1+P2 实施完成后，以下全部满足：

- [ ] `uv run pytest tests/ -v` 全部通过（含 P0 的 29 个 + P1/P2 新增测试）
- [ ] `GenerationService.submit()` 返回 job_id，`get_status()` 返回 "done"
- [ ] house 场景完整 Pipeline 三个 Stage 均产生输出
- [ ] 会客组（group_code=100001）出现在 LayoutOutput 的 placed_groups 中
- [ ] `submit_variation()` 只执行受影响的 Stage，不执行 scene_understand
- [ ] 局部 pipeline_config 可以只跑指定 Stage
- [ ] MeshService 对无 geometry 的资产返回空 PlacementZones
- [ ] SampleSearchService 第二次相同查询命中缓存（cache_hits == 1）
- [ ] LocalFileStorage put/get/exists/delete 均正常
- [ ] 所有模块均可在新机器 `git clone` 后直接运行，无需额外安装或配置
