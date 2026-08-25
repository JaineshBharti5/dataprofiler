import pytest

from dataprofiler.histogram import Histogram


def test_histogram_basic():
    histogram = Histogram(bins=5)

    for value in range(1, 101):
        histogram.update(value)

    result = histogram.to_dict()

    assert result["count"] == 100
    assert result["min"] == 1.0
    assert result["max"] == 100.0

    total = sum(
        item["count"]
        for item in result["histogram"]
    )

    assert total == 100


def test_histogram_constant_values():
    histogram = Histogram(bins=10)

    for _ in range(50):
        histogram.update(25)

    result = histogram.to_dict()

    assert result["count"] == 50
    assert result["min"] == 25.0
    assert result["max"] == 25.0
    assert result["bins"] == 1


def test_histogram_empty():
    histogram = Histogram()

    result = histogram.to_dict()

    assert result["count"] == 0
    assert result["histogram"] == []


def test_histogram_ignores_invalid_values():
    histogram = Histogram()

    histogram.update(None)

    with pytest.raises(ValueError):
        histogram.update("abc")

    assert histogram.count == 0


def test_histogram_bounded_memory():
    histogram = Histogram(bins=20)

    for value in range(100000):
        histogram.update(value)

    assert histogram.count == 100000
    assert len(histogram.bin_counts) == 20