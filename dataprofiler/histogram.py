import math


class Histogram:
    """
    Adaptive streaming histogram.

    Uses fixed memory and derives its range from observed
    minimum and maximum values.

    Values are stored only as bin counters, never as the
    complete dataset.
    """

    def __init__(self, bins=20):
        if bins < 2:
            raise ValueError("bins must be at least 2")

        self.bins = bins
        self.count = 0

        self.observed_min = None
        self.observed_max = None

        self.bin_counts = [0] * bins

    def update(self, value):
        if value is None:
            return

        value = float(value)

        if not math.isfinite(value):
            return

        # First observation
        if self.count == 0:
            self.count = 1
            self.observed_min = value
            self.observed_max = value
            self.bin_counts[0] = 1
            return

        old_min = self.observed_min
        old_max = self.observed_max

        # If range has not changed, place value directly.
        if old_min <= value <= old_max and old_min != old_max:
            index = self._bin_index(value, old_min, old_max)
            self.bin_counts[index] += 1
            self.count += 1
            return

        # Range changed.
        self._expand_range(value)
        self.count += 1

    def _bin_index(self, value, minimum, maximum):
        if minimum == maximum:
            return 0

        width = (maximum - minimum) / self.bins

        index = int((value - minimum) / width)

        if index < 0:
            index = 0

        if index >= self.bins:
            index = self.bins - 1

        return index

    def _expand_range(self, value):
        old_min = self.observed_min
        old_max = self.observed_max
        old_counts = self.bin_counts[:]

        new_min = min(old_min, value)
        new_max = max(old_max, value)

        self.observed_min = new_min
        self.observed_max = new_max

        self.bin_counts = [0] * self.bins

        # Re-map previous bins using their approximate centers.
        if old_min == old_max:
            self.bin_counts[
                self._bin_index(old_min, new_min, new_max)
            ] += old_counts[0]

        else:
            old_width = (old_max - old_min) / self.bins

            for i, count in enumerate(old_counts):
                if count == 0:
                    continue

                center = (
                    old_min
                    + (i + 0.5) * old_width
                )

                index = self._bin_index(
                    center,
                    new_min,
                    new_max
                )

                self.bin_counts[index] += count

        # Add the new value.
        index = self._bin_index(
            value,
            new_min,
            new_max
        )

        self.bin_counts[index] += 1

    def to_dict(self):
        if self.count == 0:
            return {
                "bins": self.bins,
                "count": 0,
                "min": None,
                "max": None,
                "histogram": []
            }

        if self.observed_min == self.observed_max:
            return {
                "bins": 1,
                "count": self.count,
                "min": self.observed_min,
                "max": self.observed_max,
                "histogram": [
                    {
                        "lower": self.observed_min,
                        "upper": self.observed_max,
                        "count": self.count
                    }
                ]
            }

        width = (
            self.observed_max - self.observed_min
        ) / self.bins

        histogram = []

        for i, count in enumerate(self.bin_counts):
            lower = (
                self.observed_min
                + i * width
            )

            upper = (
                self.observed_min
                + (i + 1) * width
            )

            histogram.append({
                "lower": round(lower, 6),
                "upper": round(upper, 6),
                "count": count
            })

        return {
            "bins": self.bins,
            "count": self.count,
            "min": self.observed_min,
            "max": self.observed_max,
            "histogram": histogram
        }