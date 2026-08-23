from dataprofiler import DataProfiler
from dataprofiler.hyperloglog import HyperLogLog
from dataprofiler.countminsketch import CountMinSketch

# HyperLogLog test
hll = HyperLogLog(b=10)
for i in range(100000):
    hll.add(f"user{i}")
print(hll.count())

# CountMinSketch test
cms = CountMinSketch()
for i in range(50000):
    cms.add("apple")
for i in range(10000):
    cms.add("banana")
print(cms.estimate("apple"))
print(cms.estimate("banana"))

# DataProfiler test
profiler = DataProfiler()
sample_data = ["a", "b", "a", None, "c", "a", "", "b", "d", "a"]
for value in sample_data:
    profiler.update(value)
profiler.report()