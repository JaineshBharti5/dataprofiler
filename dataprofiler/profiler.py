import csv
import json

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

    def to_dict(self):
        null_pct = (
            (self.null_count / self.total_count) * 100
            if self.total_count > 0 else 0
        )

        return {
            "total_rows": self.total_count,
            "null_percent": round(null_pct, 2),
            "unique_estimate": self.hll.count()
        }

    def report(self):
        result = self.to_dict()

        print("Total rows:", result["total_rows"])
        print("Null percent:", result["null_percent"])
        print("Unique estimate:", result["unique_estimate"])

        return result

    def to_json(self, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)

        print("JSON report saved to:", filename)

    @classmethod
    def from_csv(cls, filename, column):
        profiler = cls()

        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header.")

            if column not in reader.fieldnames:
                raise ValueError(
                    f"Column '{column}' not found. "
                    f"Available columns: {reader.fieldnames}"
                )

            for row in reader:
                profiler.update(row.get(column))

        return profiler
    @classmethod
    def profile_csv(cls, filename):
        profilers = {}

        with open(filename, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header.")

            for column in reader.fieldnames:
                profilers[column] = cls()

            for row in reader:
                for column in reader.fieldnames:
                    profilers[column].update(row.get(column))

        return profilers
