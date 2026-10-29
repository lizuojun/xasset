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
