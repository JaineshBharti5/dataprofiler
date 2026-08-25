import math


class AnomalyDetector:
    """
    Streaming anomaly detector based on mean and standard deviation.

    Uses Welford-style running statistics and does not store
    the complete dataset.

    A value is considered anomalous when its absolute z-score
    is greater than the configured threshold.
    """

    def __init__(self, threshold=3.0):
        if threshold <= 0:
            raise ValueError(
                "threshold must be greater than 0"
            )

        self.threshold = float(threshold)

        self.count = 0
        self._mean = 0.0
        self._m2 = 0.0

        self.anomaly_count = 0

    def update(self, value):
        """
        Process one numeric value.

        Returns True if the value is detected as an anomaly.
        """

        if value is None:
            return False

        try:
            value = float(value)
        except (ValueError, TypeError):
            return False

        if not math.isfinite(value):
            return False

        # Need enough observations before calculating
        # a meaningful deviation.
        if self.count < 2:
            self.count += 1

            delta = value - self._mean
            self._mean += delta / self.count
            delta2 = value - self._mean
            self._m2 += delta * delta2

            return False

        variance = self._m2 / (self.count - 1)
        stddev = math.sqrt(variance)

        is_anomaly = False

        if stddev > 0:
            z_score = abs(
                (value - self._mean) / stddev
            )

            if z_score > self.threshold:
                is_anomaly = True
                self.anomaly_count += 1

        # Update statistics after checking anomaly.
        self.count += 1

        delta = value - self._mean
        self._mean += delta / self.count
        delta2 = value - self._mean
        self._m2 += delta * delta2

        return is_anomaly

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

    @property
    def anomaly_percent(self):
        if self.count == 0:
            return 0.0

        return round(
            self.anomaly_count
            / self.count
            * 100,
            2
        )

    def to_dict(self):
        return {
            "count": self.count,
            "threshold": self.threshold,
            "mean": (
                round(self.mean, 6)
                if self.mean is not None
                else None
            ),
            "stddev": round(
                self.stddev,
                6
            ),
            "anomaly_count": self.anomaly_count,
            "anomaly_percent": self.anomaly_percent,
        }