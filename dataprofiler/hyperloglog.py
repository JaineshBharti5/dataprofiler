import hashlib
import math


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
        rank = self._leading_zeros(remaining_bits, bits=128 - self.b) + 1
        self.buckets[bucket_index] = max(self.buckets[bucket_index], rank)

    def count(self):
        alpha = 0.7213 / (1 + 1.079 / self.m)
        raw_estimate = alpha * (self.m ** 2) / sum(2 ** -b for b in self.buckets)

        if raw_estimate <= 2.5 * self.m:
            zeros = self.buckets.count(0)
            if zeros != 0:
                return int(self.m * math.log(self.m / zeros))

        return int(raw_estimate)