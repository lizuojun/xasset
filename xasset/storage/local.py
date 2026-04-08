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
