from datetime import datetime

from dataprofiler.types import (
    detect_type,
    infer_column_type,
    is_null,
)


def test_null_detection():
    assert is_null(None)
    assert is_null("")
    assert is_null("null")
    assert is_null("None")
    assert not is_null("hello")


def test_basic_types():
    assert detect_type(10) == "integer"
    assert detect_type(10.5) == "float"
    assert detect_type(True) == "boolean"
    assert detect_type("hello") == "string"


def test_string_numbers():
    assert detect_type("123") == "integer"
    assert detect_type("123.45") == "float"


def test_string_boolean():
    assert detect_type("true") == "boolean"
    assert detect_type("FALSE") == "boolean"


def test_datetime():
    assert detect_type(
        "2026-08-26"
    ) == "datetime"


def test_datetime_object():
    assert detect_type(
        datetime(2026, 8, 26)
    ) == "datetime"


def test_infer_integer_column():
    values = [
        "10",
        "20",
        "30",
        None,
    ]

    assert infer_column_type(values) == "integer"


def test_infer_float_column():
    values = [
        "10",
        "20.5",
        "30",
    ]

    assert infer_column_type(values) == "float"


def test_infer_string_column():
    values = [
        "Alice",
        "Bob",
        "Charlie",
    ]

    assert infer_column_type(values) == "string"


def test_infer_mixed_column():
    values = [
        "Alice",
        "123",
    ]

    assert infer_column_type(values) == "mixed"


def test_empty_column():
    assert infer_column_type(
        [None, "", "null"]
    ) == "null"