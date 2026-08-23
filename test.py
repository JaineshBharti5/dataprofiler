import hashlib
import math
import random


class HyperLogLog:
    def __init__(self, b=10):
        self.b = b
        self.m = 2 ** b
        self.buckets = [0] * self.m

    def _hash(self, value):
        h = hashlib.md5(str(value).encode()).hexdigest()
        return int(h, 16)

    def _leading_zeros(self, x, bits=118):
        binary = format(x, f'0{bits}b')
        count = 0
        for char in binary:
            if char == '0':
                count += 1
            else:
                break
        return count

    def add(self, value):
        x = self._hash(value)
        bucket_index = x & (self.m - 1)
        remaining_bits = x >> self.b
        # fix: bits depends on b, was hardcoded to 118 (only correct for b=10)
        rank = self._leading_zeros(remaining_bits, bits=128 - self.b) + 1
        self.buckets[bucket_index] = max(self.buckets[bucket_index], rank)

    def count(self):
        alpha = 0.7213 / (1 + 1.079 / self.m)
        raw_estimate = alpha * (self.m ** 2) / sum(2 ** -b for b in self.buckets)

        # fix: small-range correction (linear counting) for low cardinality
        if raw_estimate <= 2.5 * self.m:
            zeros = self.buckets.count(0)
            if zeros != 0:
                return int(self.m * math.log(self.m / zeros))

        return int(raw_estimate)


class CountMinSketch:
    def __init__(self, width=2000, depth=5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        self.seeds = [random.randint(0, 10**6) for _ in range(depth)]

    def _hash(self, value, seed):
        h = hashlib.md5(f"{seed}-{value}".encode()).hexdigest()
        return int(h, 16) % self.width

    def add(self, value):
        for i in range(self.depth):
            idx = self._hash(value, self.seeds[i])
            self.table[i][idx] += 1

    def estimate(self, value):
        counts = []
        for i in range(self.depth):
            idx = self._hash(value, self.seeds[i])
            counts.append(self.table[i][idx])
        return min(counts)


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


if __name__ == "__main__":
    # HyperLogLog test — 100,000 unique values
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

    # DataProfiler test — small sample with nulls
    profiler = DataProfiler()
    sample_data = ["a", "b", "a", None, "c", "a", "", "b", "d", "a"]
    for value in sample_data:
        profiler.update(value)
    profiler.report()

import random

data = []
for i in range(3000):
    times = random.randint(1, 10)   # har item 1-10 baar repeat hota hai
    data += [f"item{i}"] * times
random.shuffle(data)

profiler2 = DataProfiler()
for value in data:
    profiler2.update(value)

profiler2.report()