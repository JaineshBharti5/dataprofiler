\# DataProfiler



Lightweight, framework-agnostic streaming data profiler — combines HyperLogLog

(cardinality estimation) and Count-Min Sketch (frequency estimation) to profile

large datasets without loading everything into memory.



\## Features

\- Estimate unique value count (HyperLogLog)

\- Estimate frequency of any given value (Count-Min Sketch)

\- Track null/empty percentage

\- Constant memory usage, regardless of dataset size



\## Usage



```python

from dataprofiler import DataProfiler



profiler = DataProfiler()

data = \["a", "b", "a", None, "c", "a", "", "b", "d", "a"]



for value in data:

&#x20;   profiler.update(value)



profiler.report()

```



\## Tests



```

pytest test\_profiler.py -v

```

