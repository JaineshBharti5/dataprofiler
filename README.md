# DataProfiler

Lightweight, framework-agnostic streaming data profiler that estimates dataset statistics without loading the whole dataset into memory.

## Features

- HyperLogLog for unique-value estimation
- Count-Min Sketch for frequency estimation
- Null and empty-value tracking
- CSV profiling
- Multiple-column profiling
- JSON reports
- Large dataset processing
- No pandas or Spark required

## How it works

**HyperLogLog** estimates the number of unique values using probabilistic counting with constant memory.

**Count-Min Sketch** estimates how frequently values appear without storing every value.

Both are combined behind a single `DataProfiler` class.

## Basic Usage

```python
from dataprofiler import DataProfiler

profiler = DataProfiler()

data = ["a", "b", "a", None, "c", "a", "", "b", "d", "a"]

for value in data:
    profiler.update(value)

profiler.report()