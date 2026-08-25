import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from dataprofiler import DataProfiler
from dataprofiler.readers.parquet import (
    iter_parquet,
    profile_parquet,
)


def create_parquet_file(path):
    table = pa.table({
        "name": [
            "Alice",
            "Bob",
            "Alice",
        ],
        "age": [
            20,
            30,
            40,
        ],
        "score": [
            80.5,
            90.0,
            95.5,
        ],
    })

    pq.write_table(table, path)


def test_iter_parquet(tmp_path):
    filename = tmp_path / "data.parquet"

    create_parquet_file(filename)

    records = list(
        iter_parquet(
            filename,
            batch_size=2
        )
    )

    assert len(records) == 3

    assert records[0]["name"] == "Alice"
    assert records[1]["age"] == 30


def test_profile_parquet(tmp_path):
    filename = tmp_path / "data.parquet"

    create_parquet_file(filename)

    profiles = profile_parquet(
        filename,
        DataProfiler,
        batch_size=2
    )

    assert "name" in profiles
    assert "age" in profiles
    assert "score" in profiles

    assert profiles["age"].total_count == 3
    assert profiles["age"].numeric_count == 3

    assert profiles["score"].numeric_count == 3


def test_invalid_batch_size(tmp_path):
    filename = tmp_path / "data.parquet"

    create_parquet_file(filename)

    with pytest.raises(ValueError):
        list(
            iter_parquet(
                filename,
                batch_size=0
            )
        )