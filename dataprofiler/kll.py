import random


class KLLSketch:
    """
    Streaming KLL-style quantile sketch.

    Uses bounded memory through level compaction and provides
    approximate quantiles for large streams.
    """

    def __init__(self, k=200, seed=42):
        if k < 8:
            raise ValueError("k must be at least 8")

        self.k = k
        self.levels = [[]]
        self.count = 0
        self._random = random.Random(seed)

    def _ensure_level(self, level):
        while len(self.levels) <= level:
            self.levels.append([])

    def update(self, value):
        if value is None:
            return

        value = float(value)

        self.count += 1
        self.levels[0].append(value)

        self._compress(0)

    def _compress(self, level):
        self._ensure_level(level)

        if len(self.levels[level]) <= self.k:
            return

        values = sorted(self.levels[level])

        # Keep one randomly selected parity.
        offset = self._random.randint(0, 1)

        promoted = values[offset::2]

        self.levels[level] = []

        self._ensure_level(level + 1)
        self.levels[level + 1].extend(promoted)

        self._compress(level + 1)

    def _weighted_values(self):
        weighted = []

        for level, values in enumerate(self.levels):
            weight = 2 ** level

            for value in values:
                weighted.append((value, weight))

        weighted.sort(key=lambda item: item[0])

        return weighted

    def quantile(self, q):
        if not 0 <= q <= 1:
            raise ValueError("q must be between 0 and 1")

        if self.count == 0:
            return None

        weighted = self._weighted_values()

        total_weight = sum(
            weight for _, weight in weighted
        )

        if total_weight == 0:
            return None

        target = q * total_weight

        cumulative = 0

        for value, weight in weighted:
            cumulative += weight

            if cumulative >= target:
                return value

        return weighted[-1][0]

    def percentile(self, p):
        if not 0 <= p <= 100:
            raise ValueError(
                "percentile must be between 0 and 100"
            )

        return self.quantile(p / 100.0)

    def to_dict(self):
        return {
            "count": self.count,
            "k": self.k,
            "p50": self.percentile(50),
            "p90": self.percentile(90),
            "p95": self.percentile(95),
            "p99": self.percentile(99),
        }