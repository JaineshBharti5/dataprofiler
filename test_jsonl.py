import json

import pytest

from dataprofiler import DataProfiler
from dataprofiler.readers.jsonl import (
    iter_jsonl,
    profile_jsonl,
)


def test_iter_jsonl(tmp_path):
    filename = tmp_path / "data.jsonl"

    records = [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 30},
    ]

    with open(filename, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    result = list(iter_jsonl(filename))

    assert result == records


def test_profile_jsonl(tmp_path):
    filename = tmp_path / "data.jsonl"

    records = [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 30},
        {"name": "Alice", "age": 40},
    ]

    with open(filename, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")

    profiles = profile_jsonl(
        filename,
        DataProfiler
    )

    assert "name" in profiles
    assert "age" in profiles

    assert profiles["age"].total_count == 3
    assert profiles["age"].numeric_count == 3

    assert profiles["name"].total_count == 3


def test_invalid_json(tmp_path):
    filename = tmp_path / "bad.jsonl"

    filename.write_text(
        '{"name": "Alice"}\n'
        '{"invalid": }\n',
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        list(iter_jsonl(filename))


def test_jsonl_requires_objects(tmp_path):
    filename = tmp_path / "bad.jsonl"

    filename.write_text(
        '["a", "b"]\n',
        encoding="utf-8"
    )

    with pytest.raises(ValueError):
        profile_jsonl(filename, DataProfiler)