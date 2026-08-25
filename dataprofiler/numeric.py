import math


class NumericStats:
    """
    Streaming numeric statistics using Welford's algorithm.

    Uses constant memory and supports one-value-at-a-time updates.
    """

    def __init__(self):
        self.count = 0
        self.sum = 0.0
        self.min = None
        self.max = None

        self._mean = 0.0
        self._m2 = 0.0

    def update(self, value):
        """Update statistics with one numeric value."""
        if value is None:
            return

        value = float(value)

        if not math.isfinite(value):
            return

        self.count += 1
        self.sum += value

        if self.min is None or value < self.min:
            self.min = value

        if self.max is None or value > self.max:
            self.max = value

        delta = value - self._mean
        self._mean += delta / self.count
        delta2 = value - self._mean
        self._m2 += delta * delta2

    @property
    def mean(self):
        if self.count == 0:
            return None
        return self._mean

    @property
    def variance(self):
        if self.count < 2:
            return 0.0
        return self._m2 / (self.count - 1)

    @property
    def stddev(self):
        return math.sqrt(self.variance)

    def to_dict(self):
        return {
            "count": self.count,
            "sum": round(self.sum, 6),
            "mean": round(self.mean, 6) if self.mean is not None else None,
            "min": self.min,
            "max": self.max,
            "variance": round(self.variance, 6),
            "stddev": round(self.stddev, 6),
        }