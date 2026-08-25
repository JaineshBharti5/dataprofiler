from dataprofiler.numeric import NumericStats


def test_numeric_stats():
    stats = NumericStats()

    for value in [1, 2, 3, 4, 5]:
        stats.update(value)

    result = stats.to_dict()

    assert result["count"] == 5
    assert result["sum"] == 15.0
    assert result["mean"] == 3.0
    assert result["min"] == 1.0
    assert result["max"] == 5.0


def test_empty_stats():
    stats = NumericStats()

    result = stats.to_dict()

    assert result["count"] == 0
    assert result["mean"] is None