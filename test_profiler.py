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
def test_from_csv():
    with open("test_data.csv", "w", encoding="utf-8") as f:
        f.write("product,city\n")
        f.write("Laptop,Delhi\n")
        f.write("Phone,Mumbai\n")
        f.write("Laptop,Delhi\n")
        f.write(",Chennai\n")

    profiler = DataProfiler.from_csv("test_data.csv", "product")

    assert profiler.total_count == 4
    assert profiler.null_count == 1


def test_profile_csv():
    profilers = DataProfiler.profile_csv("test_data.csv")

    assert "product" in profilers
    assert "city" in profilers
    assert profilers["product"].total_count == 4
    assert profilers["city"].total_count == 4


def test_json_report():
    profiler = DataProfiler()
    profiler.update("a")
    profiler.update("b")
    profiler.update("a")

    profiler.to_json("test_report.json")

    import json
    with open("test_report.json", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_rows"] == 3
    assert data["null_percent"] == 0.0
