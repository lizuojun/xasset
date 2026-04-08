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
