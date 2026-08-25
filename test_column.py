from dataprofiler.column import ColumnProfile


def test_numeric_column():
    profile = ColumnProfile()

    for value in [10, 20, 30, 40, 50]:
        profile.update(value)

    result = profile.to_dict()

    assert result["rows"] == 5
    assert result["type"] == "integer"
    assert result["null_count"] == 0
    assert result["numeric"]["mean"] == 30.0
    assert result["numeric"]["min"] == 10.0
    assert result["numeric"]["max"] == 50.0


def test_string_column():
    profile = ColumnProfile()

    for value in [
        "Alice",
        "Bob",
        "Alice",
        "Charlie",
    ]:
        profile.update(value)

    result = profile.to_dict()

    assert result["rows"] == 4
    assert result["type"] == "string"
    assert result["null_count"] == 0
    assert result["unique_estimate"] >= 1


def test_null_values():
    profile = ColumnProfile()

    for value in [
        None,
        "",
        "null",
        "Alice",
    ]:
        profile.update(value)

    result = profile.to_dict()

    assert result["rows"] == 4
    assert result["null_count"] == 3
    assert result["null_percent"] == 75.0


def test_float_column():
    profile = ColumnProfile()

    for value in [
        10.5,
        20.5,
        30.5,
    ]:
        profile.update(value)

    result = profile.to_dict()

    assert result["type"] == "float"
    assert result["numeric"]["mean"] == 20.5


def test_type_counts():
    profile = ColumnProfile()

    values = [
        10,
        20,
        30.5,
        None,
    ]

    for value in values:
        profile.update(value)

    result = profile.to_dict()

    assert result["type_counts"]["integer"] == 2
    assert result["type_counts"]["float"] == 1
    assert result["type_counts"]["null"] == 1


def test_quality_metrics():
    profile = ColumnProfile()

    values = [
        "Alice",
        "Alice",
        "Bob",
        None,
        "Charlie",
    ]

    for value in values:
        profile.update(value)

    result = profile.to_dict()

    assert result["quality"]["rows"] == 5
    assert result["quality"]["null_count"] == 1
    assert result["quality"]["null_percent"] == 20.0
    assert result["quality"]["completeness_percent"] == 80.0


def test_quality_duplicates():
    profile = ColumnProfile()

    values = [
        "a",
        "a",
        "a",
        "b",
        "b",
    ]

    for value in values:
        profile.update(value)

    result = profile.to_dict()

    assert result["quality"]["rows"] == 5
    assert result["quality"]["unique_estimate"] == 2
    assert result["quality"]["uniqueness_percent"] == 40.0
    assert result["quality"]["duplicate_percent"] == 60.0