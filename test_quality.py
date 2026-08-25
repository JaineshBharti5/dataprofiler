from dataprofiler.quality import QualityMetrics


def test_quality_empty():
    quality = QualityMetrics()

    result = quality.to_dict(
        unique_estimate=0
    )

    assert result["rows"] == 0
    assert result["null_count"] == 0
    assert result["null_percent"] == 0.0
    assert result["completeness_percent"] == 0.0


def test_quality_complete_data():
    quality = QualityMetrics()

    for value in [
        "a",
        "b",
        "c",
        "d",
    ]:
        quality.update(value)

    result = quality.to_dict(
        unique_estimate=4
    )

    assert result["rows"] == 4
    assert result["null_count"] == 0
    assert result["null_percent"] == 0.0
    assert result["completeness_percent"] == 100.0
    assert result["uniqueness_percent"] == 100.0
    assert result["duplicate_percent"] == 0.0


def test_quality_with_nulls():
    quality = QualityMetrics()

    for value in [
        "a",
        None,
        "b",
        None,
        "c",
    ]:
        quality.update(value)

    result = quality.to_dict(
        unique_estimate=3
    )

    assert result["rows"] == 5
    assert result["null_count"] == 2
    assert result["null_percent"] == 40.0
    assert result["completeness_percent"] == 60.0


def test_quality_duplicates():
    quality = QualityMetrics()

    for value in [
        "a",
        "a",
        "a",
        "b",
        "b",
    ]:
        quality.update(value)

    result = quality.to_dict(
        unique_estimate=2
    )

    assert result["rows"] == 5
    assert result["uniqueness_percent"] == 40.0
    assert result["duplicate_percent"] == 60.0