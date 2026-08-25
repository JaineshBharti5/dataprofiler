from .hyperloglog import HyperLogLog
from .countminsketch import CountMinSketch


class DataProfiler:
    def __init__(self):
        self.hll = HyperLogLog(b=10)
        self.cms = CountMinSketch()
        self.total_count = 0
        self.null_count = 0

    def update(self, value):
        self.total_count += 1
        if value is None or value == "":
            self.null_count += 1
            return
        self.hll.add(value)
        self.cms.add(value)

    def report(self):
        null_pct = (self.null_count / self.total_count) * 100
        print("Total rows:", self.total_count)
        print("Null percent:", round(null_pct, 2))
        print("Unique estimate:", self.hll.count())