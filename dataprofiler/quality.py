from .types import is_null


class QualityMetrics:
    """
    Streaming data-quality metrics.

    Tracks nulls and derives completeness,
    uniqueness and duplicate-rate metrics.
    """

    def __init__(self):
        self.total_count = 0
        self.null_count = 0

    def update(self, value):
        self.total_count += 1

        if is_null(value):
            self.null_count += 1

    def completeness(self):
        if self.total_count == 0:
            return 0.0

        return round(
            (
                (self.total_count - self.null_count)
                / self.total_count
            ) * 100,
            2
        )

    def null_percent(self):
        if self.total_count == 0:
            return 0.0

        return round(
            (self.null_count / self.total_count) * 100,
            2
        )

    def to_dict(self, unique_estimate=None):
        result = {
            "rows": self.total_count,
            "null_count": self.null_count,
            "null_percent": self.null_percent(),
            "completeness_percent": self.completeness(),
        }

        if unique_estimate is not None:
            result["unique_estimate"] = unique_estimate

            if self.total_count > 0:
                uniqueness = (
                    unique_estimate
                    / self.total_count
                    * 100
                )

                result["uniqueness_percent"] = round(
                    min(uniqueness, 100),
                    2
                )

                result["duplicate_percent"] = round(
                    max(100 - uniqueness, 0),
                    2
                )
            else:
                result["uniqueness_percent"] = 0.0
                result["duplicate_percent"] = 0.0

        return result