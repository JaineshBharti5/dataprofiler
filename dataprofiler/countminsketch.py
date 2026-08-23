import hashlib
import random


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