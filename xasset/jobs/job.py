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
