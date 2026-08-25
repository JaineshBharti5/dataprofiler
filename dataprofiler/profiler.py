import csv
import json

from .column import ColumnProfile
from .validator import ValidationEngine
from .health import HealthScore


class DataProfiler:
    """
    Backward-compatible profiler with dataset-level
    profiling, quality metrics, anomaly detection,
    validation and health scoring.
    """

    def __init__(
        self,
        top_k=10,
        histogram_bins=20,
        rules=None,
        anomaly_threshold=3.0
    ):
        self.top_k = top_k
        self.histogram_bins = histogram_bins
        self.rules = rules or {}
        self.anomaly_threshold = anomaly_threshold

        self.column = ColumnProfile(
            top_k=top_k,
            histogram_bins=histogram_bins,
            anomaly_threshold=anomaly_threshold
        )

        self.validator = ValidationEngine(
            self.rules
        )

        self.health = HealthScore()

    # -------------------------------------------------
    # Backward-compatible properties
    # -------------------------------------------------

    @property
    def total_count(self):
        return self.column.total_count

    @property
    def null_count(self):
        return self.column.null_count

    @property
    def numeric_count(self):
        return self.column.numeric.count

    @property
    def hll(self):
        return self.column.hll

    @property
    def cms(self):
        return self.column.cms

    @property
    def numeric(self):
        return self.column.numeric

    @property
    def kll(self):
        return self.column.kll

    @property
    def topk(self):
        return self.column.topk

    @property
    def histogram(self):
        return self.column.histogram

    @property
    def anomaly(self):
        return self.column.anomaly

    # -------------------------------------------------
    # Update
    # -------------------------------------------------

    def update(self, value):
        self.column.update(value)

    # -------------------------------------------------
    # Dictionary output
    # -------------------------------------------------

    def to_dict(self):
        result = self.column.to_dict()

        return {
            "total_rows": result["rows"],
            "null_count": result["null_count"],
            "null_percent": result["null_percent"],
            "unique_estimate": result["unique_estimate"],
            "numeric_count": (
                result["numeric"]["count"]
                if result["numeric"] is not None
                else 0
            ),
            "numeric": result["numeric"],
            "quantiles": result["quantiles"],
            "top_k": result["top_k"],
            "histogram": result["histogram"],
            "type": result["type"],
            "type_counts": result["type_counts"],
            "quality": result["quality"],
            "anomaly": result["anomaly"],
        }

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    def validate(self, column, value):
        self.validator.update(
            column,
            value
        )

    def validation_report(self):
        return self.validator.report()

    # -------------------------------------------------
    # Report
    # -------------------------------------------------

    def report(self):
        result = self.to_dict()

        print("Total rows:", result["total_rows"])
        print("Null count:", result["null_count"])
        print("Null percent:", result["null_percent"])
        print("Unique estimate:", result["unique_estimate"])
        print("Type:", result["type"])

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

            print("Count:", numeric["count"])
            print("Sum:", numeric["sum"])
            print("Mean:", numeric["mean"])
            print("Min:", numeric["min"])
            print("Max:", numeric["max"])
            print("Variance:", numeric["variance"])
            print("Stddev:", numeric["stddev"])

            print("\nQuantiles")
            print("---------")

            print("P50:", quantiles["p50"])
            print("P90:", quantiles["p90"])
            print("P95:", quantiles["p95"])
            print("P99:", quantiles["p99"])

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

    # -------------------------------------------------
    # JSON
    # -------------------------------------------------

    def to_json(self, filename):
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.to_dict(),
                file,
                indent=4
            )

    # -------------------------------------------------
    # CSV single column
    # -------------------------------------------------

    @classmethod
    def from_csv(cls, filename, column):

        profiler = cls()

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV file has no header."
                )

            if column not in reader.fieldnames:
                raise ValueError(
                    f"Column '{column}' not found. "
                    f"Available columns: "
                    f"{reader.fieldnames}"
                )

            for row in reader:
                profiler.update(
                    row.get(column)
                )

        return profiler

    # -------------------------------------------------
    # CSV all columns
    # -------------------------------------------------

    @classmethod
    def profile_csv(cls, filename):

        profilers = {}

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV file has no header."
                )

            for column in reader.fieldnames:
                profilers[column] = cls()

            for row in reader:

                for column in reader.fieldnames:
                    profilers[column].update(
                        row.get(column)
                    )

        return profilers

    # -------------------------------------------------
    # Dataset profiling
    # -------------------------------------------------

    @classmethod
    def profile_dataset(
        cls,
        filename,
        file_type=None,
        top_k=10,
        histogram_bins=20,
        rules=None,
        anomaly_threshold=3.0
    ):

        if file_type is None:
            file_type = (
                filename
                .split(".")[-1]
                .lower()
            )

        if file_type == "csv":

            return cls._profile_csv_dataset(
                filename,
                top_k,
                histogram_bins,
                rules,
                anomaly_threshold
            )

        if file_type == "jsonl":

            return cls._profile_jsonl_dataset(
                filename,
                top_k,
                histogram_bins,
                rules,
                anomaly_threshold
            )

        if file_type == "parquet":

            return cls._profile_parquet_dataset(
                filename,
                top_k,
                histogram_bins,
                rules,
                anomaly_threshold
            )

        raise ValueError(
            f"Unsupported file type: {file_type}. "
            f"Supported types: csv, jsonl, parquet"
        )

    # -------------------------------------------------
    # Health calculation
    # -------------------------------------------------

    @staticmethod
    def _dataset_health(
        columns,
        validation=None
    ):
        if not columns:
            return HealthScore().report(
                0,
                0,
                0,
                100
            )

        completeness = []
        uniqueness = []
        anomaly_rates = []

        for profile in columns.values():

            quality = profile["quality"]

            completeness.append(
                quality["completeness_percent"]
            )

            uniqueness.append(
                quality["uniqueness_percent"]
            )

            anomaly = profile.get("anomaly")

            if anomaly is not None:
                anomaly_rates.append(
                    anomaly["anomaly_percent"]
                )

        avg_completeness = (
            sum(completeness)
            / len(completeness)
        )

        avg_uniqueness = (
            sum(uniqueness)
            / len(uniqueness)
        )

        avg_anomaly_rate = (
            sum(anomaly_rates)
            / len(anomaly_rates)
            if anomaly_rates
            else 0.0
        )

        if validation:
            total_checked = sum(
                item["checked"]
                for item in validation.values()
            )

            total_violations = sum(
                item["violations"]
                for item in validation.values()
            )

            validation_score = (
                100.0
                if total_checked == 0
                else (
                    100.0
                    - (
                        total_violations
                        / total_checked
                        * 100
                    )
                )
            )
        else:
            validation_score = 100.0

        health = HealthScore()

        return health.report(
            completeness=avg_completeness,
            uniqueness=avg_uniqueness,
            validation=validation_score,
            anomalies=avg_anomaly_rate
        )

    # -------------------------------------------------
    # CSV dataset
    # -------------------------------------------------

    @classmethod
    def _profile_csv_dataset(
        cls,
        filename,
        top_k,
        histogram_bins,
        rules,
        anomaly_threshold
    ):

        profiles = {}
        validator = ValidationEngine(rules)
        total_rows = 0

        with open(
            filename,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV file has no header."
                )

            for column in reader.fieldnames:

                profiles[column] = ColumnProfile(
                    top_k=top_k,
                    histogram_bins=histogram_bins,
                    anomaly_threshold=anomaly_threshold
                )

            for row in reader:

                total_rows += 1

                for column in reader.fieldnames:

                    value = row.get(column)

                    profiles[column].update(
                        value
                    )

                    validator.update(
                        column,
                        value
                    )

        columns = {
            name: profile.to_dict()
            for name, profile in profiles.items()
        }

        result = {
            "rows": total_rows,
            "columns": columns
        }

        if rules:
            result["validation"] = (
                validator.report()
            )

        result["health_score"] = (
            cls._dataset_health(
                columns,
                result.get("validation")
            )
        )

        return result

    # -------------------------------------------------
    # JSONL dataset
    # -------------------------------------------------

    @classmethod
    def _profile_jsonl_dataset(
        cls,
        filename,
        top_k,
        histogram_bins,
        rules,
        anomaly_threshold
    ):

        from .readers.jsonl import iter_jsonl

        profiles = {}
        validator = ValidationEngine(rules)
        total_rows = 0

        for record in iter_jsonl(filename):

            if not isinstance(record, dict):
                raise ValueError(
                    "Each JSONL record must be a JSON object."
                )

            total_rows += 1

            for column, value in record.items():

                if column not in profiles:

                    profiles[column] = ColumnProfile(
                        top_k=top_k,
                        histogram_bins=histogram_bins,
                        anomaly_threshold=anomaly_threshold
                    )

                profiles[column].update(
                    value
                )

                validator.update(
                    column,
                    value
                )

        columns = {
            name: profile.to_dict()
            for name, profile in profiles.items()
        }

        result = {
            "rows": total_rows,
            "columns": columns
        }

        if rules:
            result["validation"] = (
                validator.report()
            )

        result["health_score"] = (
            cls._dataset_health(
                columns,
                result.get("validation")
            )
        )

        return result

    # -------------------------------------------------
    # Parquet dataset
    # -------------------------------------------------

    @classmethod
    def _profile_parquet_dataset(
        cls,
        filename,
        top_k,
        histogram_bins,
        rules,
        anomaly_threshold
    ):

        from .readers.parquet import iter_parquet

        profiles = {}
        validator = ValidationEngine(rules)
        total_rows = 0

        for record in iter_parquet(filename):

            if not isinstance(record, dict):
                raise ValueError(
                    "Each Parquet record must be a row object."
                )

            total_rows += 1

            for column, value in record.items():

                if column not in profiles:

                    profiles[column] = ColumnProfile(
                        top_k=top_k,
                        histogram_bins=histogram_bins,
                        anomaly_threshold=anomaly_threshold
                    )

                profiles[column].update(
                    value
                )

                validator.update(
                    column,
                    value
                )

        columns = {
            name: profile.to_dict()
            for name, profile in profiles.items()
        }

        result = {
            "rows": total_rows,
            "columns": columns
        }

        if rules:
            result["validation"] = (
                validator.report()
            )

        result["health_score"] = (
            cls._dataset_health(
                columns,
                result.get("validation")
            )
        )

        return result