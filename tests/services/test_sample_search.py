# tests/services/test_sample_search.py
import math
from xasset.models.sample import STYLE_VECTOR_DIM, PARTITION_VECTOR_DIM
from xasset.services.sample_search import SampleSearchService


def _make_sample(style, style_vector, scene_type="house", sample_level="zone"):
    from xasset.models.sample import Sample
    import types
    s = types.SimpleNamespace()
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
