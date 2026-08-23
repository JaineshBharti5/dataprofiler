# DataProfiler

Lightweight, framework-agnostic streaming data profiler that estimates dataset statistics without loading the whole dataset into memory.

## Why

Most profiling tools either need a full in-memory pass (pandas `.nunique()`, `.value_counts()`) or a heavyweight cluster (Spark, DataSketches). DataProfiler works in a single pass, with constant memory, using nothing but plain Python.

## How it works

- **HyperLogLog** — estimates the number of unique values using probabilistic counting (~2-5% error, constant memory, regardless of dataset size)
- **Count-Min Sketch** — estimates how often any given value appears, without storing every value seen
- Both are combined behind a single `DataProfiler` class, along with null/empty tracking

## Usage

```python
from dataprofiler import DataProfiler

profiler = DataProfiler()
data = ["a", "b", "a", None, "c", "a", "", "b", "d", "a"]

for value in data:
    profiler.update(value)

profiler.report()
```

Output:
```
Total rows: 10
Null percent: 20.0
Unique estimate: 4
```

## Project structure

```
dataprofiler/
├── hyperloglog.py      # cardinality estimation
├── countminsketch.py   # frequency estimation
├── profiler.py         # combines both into DataProfiler
└── __init__.py
```

## Running tests

```bash
pytest test_profiler.py -v
```
