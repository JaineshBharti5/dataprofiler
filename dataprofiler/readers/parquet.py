import pyarrow.parquet as pq


def iter_parquet(filename, batch_size=10000):
    """
    Stream records from a Parquet file in batches.

    Only one batch is held in memory at a time.
    """

    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    parquet_file = pq.ParquetFile(filename)

    for batch in parquet_file.iter_batches(
        batch_size=batch_size
    ):
        for record in batch.to_pylist():
            yield record


def profile_parquet(
    filename,
    profiler_class,
    batch_size=10000
):
    """
    Profile every column in a Parquet file.
    """

    profilers = {}

    for record in iter_parquet(
        filename,
        batch_size=batch_size
    ):
        if not isinstance(record, dict):
            raise ValueError(
                "Each Parquet record must be a row object."
            )

        for column, value in record.items():

            if column not in profilers:
                profilers[column] = profiler_class()

            profilers[column].update(value)

    return profilers