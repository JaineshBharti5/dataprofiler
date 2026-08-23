from dataprofiler import DataProfiler
from dataprofiler.hyperloglog import HyperLogLog
from dataprofiler.countminsketch import CountMinSketch


def test_hyperloglog_small():
    hll = HyperLogLog(b=10)
    for value in ["a", "b", "c", "d"]:
        hll.add(value)
    estimate = hll.count()
    assert abs(estimate - 4) <= 1  # chhoti cardinality near-exact honi chahiye


def test_hyperloglog_large():
    hll = HyperLogLog(b=10)
    true_count = 100000
    for i in range(true_count):
        hll.add(f"user{i}")
    estimate = hll.count()
    error_pct = abs(estimate - true_count) / true_count * 100
    assert error_pct < 10  # 10% ke andar error rehna chahiye


def test_countminsketch_accuracy():
    cms = CountMinSketch()
    for _ in range(50000):
        cms.add("apple")
    for _ in range(10000):
        cms.add("banana")
    assert cms.estimate("apple") == 50000
    assert cms.estimate("banana") == 10000


def test_dataprofiler_nulls():
    profiler = DataProfiler()
    sample_data = ["a", "b", "a", None, "c", "a", "", "b", "d", "a"]
    for value in sample_data:
        profiler.update(value)
    assert profiler.total_count == 10
    assert profiler.null_count == 2