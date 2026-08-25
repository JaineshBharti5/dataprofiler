import json


def iter_jsonl(filename):
    """
    Stream records from a JSON Lines file.

    Yields one JSON object at a time without loading
    the complete file into memory.
    """
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}"
                ) from exc


def profile_jsonl(filename, profiler_class):
    """
    Profile every field in a JSONL file.

    Returns:
        dict[str, DataProfiler]
    """
    profilers = {}

    for record in iter_jsonl(filename):
        if not isinstance(record, dict):
            raise ValueError(
                "Each JSONL record must be a JSON object."
            )

        for key, value in record.items():
            if key not in profilers:
                profilers[key] = profiler_class()

            profilers[key].update(value)

    return profilers