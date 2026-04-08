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
