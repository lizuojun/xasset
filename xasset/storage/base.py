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
