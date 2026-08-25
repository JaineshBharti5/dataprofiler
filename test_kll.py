import pytest

from dataprofiler.kll import KLLSketch


def test_kll_basic():
    sketch = KLLSketch(k=50)

    for value in range(1, 101):
        sketch.update(value)

    assert sketch.count == 100

    p50 = sketch.percentile(50)
    p95 = sketch.percentile(95)

    assert 30 <= p50 <= 70
    assert 80 <= p95 <= 100


def test_kll_empty():
    sketch = KLLSketch()

    assert sketch.quantile(0.5) is None


def test_kll_invalid_quantile():
    sketch = KLLSketch()

    # Add a value so validation is reached
    sketch.update(10)

    with pytest.raises(ValueError):
        sketch.quantile(1.5)


def test_kll_percentiles():
    sketch = KLLSketch(k=100)

    for value in range(1000):
        sketch.update(value)

    result = sketch.to_dict()

    assert result["count"] == 1000
    assert result["p50"] is not None
    assert result["p95"] is not None
    assert result["p99"] is not None