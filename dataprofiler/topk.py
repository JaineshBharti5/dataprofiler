from collections import Counter


class TopK:
    """
    Streaming Top-K frequency tracker.

    Keeps a bounded candidate set instead of storing every
    unique value in the dataset.
    """

    def __init__(self, k=10, capacity=None):
        if k < 1:
            raise ValueError("k must be at least 1")

        self.k = k
        self.capacity = capacity or max(k * 10, 100)

        if self.capacity < k:
            raise ValueError("capacity must be >= k")

        self.counts = Counter()

    def update(self, value):
        if value is None or value == "":
            return

        self.counts[value] += 1

        if len(self.counts) > self.capacity:
            self._trim()

    def _trim(self):
        top = self.counts.most_common(self.capacity // 2)
        self.counts = Counter(dict(top))

    def top(self, k=None):
        k = k or self.k

        if k < 1:
            raise ValueError("k must be at least 1")

        return self.counts.most_common(k)

    def estimate(self, value):
        return self.counts.get(value, 0)

    def to_dict(self):
        return {
            "k": self.k,
            "top": [
                {
                    "value": value,
                    "count": count
                }
                for value, count in self.top()
            ]
        }