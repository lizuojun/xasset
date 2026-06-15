# xasset/jobs/store.py
import copy
from xasset.jobs.job import Job


class InMemoryJobStore:
    """In-memory job store with value-copy semantics.

    create() and update() store a shallow copy of the job, so mutations to the
    caller's object after the call do not affect the stored state.
    get() returns the stored copy directly; callers should not mutate it.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self, job: Job) -> None:
        self._jobs[job.id] = copy.copy(job)

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def update(self, job: Job) -> None:
        self._jobs[job.id] = copy.copy(job)
