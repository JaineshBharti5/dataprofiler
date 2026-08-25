from .types import detect_type, is_null
from .hyperloglog import HyperLogLog
from .countminsketch import CountMinSketch
from .numeric import NumericStats
from .kll import KLLSketch
from .topk import TopK
from .histogram import Histogram
from .quality import QualityMetrics
from .anomaly import AnomalyDetector


class ColumnProfile:
    """
    Streaming profile for a single data column.

    Combines statistical sketches, type detection,
    numeric analysis, data-quality metrics and
    anomaly detection while keeping bounded memory usage.
    """

    def __init__(
        self,
        top_k=10,
        histogram_bins=20,
        anomaly_threshold=3.0
    ):
        self.top_k = top_k
        self.histogram_bins = histogram_bins
        self.anomaly_threshold = anomaly_threshold

        # General counters
        self.total_count = 0
        self.null_count = 0

        # Type detection
        self.type_counts = {}

        # Cardinality
        self.hll = HyperLogLog(b=10)

        # Frequency
        self.cms = CountMinSketch()

        # Numeric statistics
        self.numeric = NumericStats()

        # Approximate quantiles
        self.kll = KLLSketch(k=200)

        # Frequent values
        self.topk = TopK(k=top_k)

        # Numeric distribution
        self.histogram = Histogram(
            bins=histogram_bins
        )

        # Data quality
        self.quality = QualityMetrics()

        # Anomaly detection
        self.anomaly = AnomalyDetector(
            threshold=anomaly_threshold
        )

    def update(self, value):
        """
        Process one value in streaming fashion.
        """

        self.total_count += 1

        # Data quality
        self.quality.update(value)

        # Type detection
        value_type = detect_type(value)

        self.type_counts[value_type] = (
            self.type_counts.get(value_type, 0) + 1
        )

        # Null values
        if is_null(value):
            self.null_count += 1
            return

        # Cardinality
        self.hll.add(value)

        # Frequency
        self.cms.add(value)

        # Top-K
        self.topk.update(value)

        # Numeric processing
        if value_type in {"integer", "float"}:
            numeric_value = float(value)

            self.numeric.update(
                numeric_value
            )

            self.kll.update(
                numeric_value
            )

            self.histogram.update(
                numeric_value
            )

            # Anomaly detection
            self.anomaly.update(
                numeric_value
            )

    @property
    def inferred_type(self):
        """
        Return the dominant non-null type.
        """

        non_null_types = {
            key: value
            for key, value in self.type_counts.items()
            if key != "null"
        }

        if not non_null_types:
            return "null"

        return max(
            non_null_types,
            key=non_null_types.get
        )

    def to_dict(self):
        """
        Return the complete column profile.
        """

        quality = self.quality.to_dict(
            unique_estimate=self.hll.count()
            if self.total_count > self.null_count
            else 0
        )

        result = {
            "rows": self.total_count,
            "null_count": self.null_count,
            "null_percent": quality["null_percent"],
            "type": self.inferred_type,
            "type_counts": self.type_counts,
            "unique_estimate": self.hll.count(),
            "quality": quality,
            "top_k": self.topk.to_dict(),
        }

        # Numeric information
        if self.numeric.count > 0:

            result["numeric"] = (
                self.numeric.to_dict()
            )

            result["quantiles"] = {
                "p50": self.kll.percentile(50),
                "p90": self.kll.percentile(90),
                "p95": self.kll.percentile(95),
                "p99": self.kll.percentile(99),
            }

            result["histogram"] = (
                self.histogram.to_dict()
            )

            result["anomaly"] = (
                self.anomaly.to_dict()
            )

        else:

            result["numeric"] = None
            result["quantiles"] = None
            result["histogram"] = None
            result["anomaly"] = None

        return result

    def report(self):
        """
        Print and return the complete profile.
        """

        result = self.to_dict()

        print(
            "Rows:",
            result["rows"]
        )

        print(
            "Type:",
            result["type"]
        )

        print(
            "Null count:",
            result["null_count"]
        )

        print(
            "Null percent:",
            result["null_percent"]
        )

        print(
            "Unique estimate:",
            result["unique_estimate"]
        )

        print("\nData Quality")
        print("------------")

        quality = result["quality"]

        print(
            "Completeness:",
            quality["completeness_percent"],
            "%"
        )

        print(
            "Uniqueness:",
            quality["uniqueness_percent"],
            "%"
        )

        print(
            "Duplicate rate:",
            quality["duplicate_percent"],
            "%"
        )

        if result["numeric"] is not None:

            numeric = result["numeric"]
            quantiles = result["quantiles"]
            anomaly = result["anomaly"]

            print("\nNumeric Statistics")
            print("------------------")

            print(
                "Count:",
                numeric["count"]
            )

            print(
                "Sum:",
                numeric["sum"]
            )

            print(
                "Mean:",
                numeric["mean"]
            )

            print(
                "Min:",
                numeric["min"]
            )

            print(
                "Max:",
                numeric["max"]
            )

            print(
                "Variance:",
                numeric["variance"]
            )

            print(
                "Stddev:",
                numeric["stddev"]
            )

            print("\nQuantiles")
            print("---------")

            print(
                "P50:",
                quantiles["p50"]
            )

            print(
                "P90:",
                quantiles["p90"]
            )

            print(
                "P95:",
                quantiles["p95"]
            )

            print(
                "P99:",
                quantiles["p99"]
            )

            print("\nAnomaly Detection")
            print("-----------------")

            print(
                "Threshold:",
                anomaly["threshold"]
            )

            print(
                "Anomaly count:",
                anomaly["anomaly_count"]
            )

            print(
                "Anomaly percent:",
                anomaly["anomaly_percent"],
                "%"
            )

        print("\nTop-K")
        print("-----")

        for item in result["top_k"]["top"]:
            print(
                f"{item['value']}: "
                f"{item['count']}"
            )

        return result