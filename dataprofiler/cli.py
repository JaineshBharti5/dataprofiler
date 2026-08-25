import argparse
import json
import sys

from .profiler import DataProfiler


def print_profile(result):
    """Print a readable dataset profile."""

    print()
    print("=" * 60)
    print("              DATAPROFILER REPORT")
    print("=" * 60)

    print(f"Rows: {result.get('rows', 0)}")
    print(f"Columns: {len(result.get('columns', {}))}")

    print()
    print("COLUMN SUMMARY")
    print("-" * 60)

    for name, profile in result.get("columns", {}).items():

        print(f"\n{name}")
        print(f"  Type: {profile.get('type')}")
        print(f"  Rows: {profile.get('rows')}")
        print(f"  Null %: {profile.get('null_percent')}")
        print(
            f"  Unique estimate: "
            f"{profile.get('unique_estimate')}"
        )

        quality = profile.get("quality")

        if quality:
            print(
                f"  Completeness: "
                f"{quality.get('completeness_percent')}%"
            )

            print(
                f"  Uniqueness: "
                f"{quality.get('uniqueness_percent')}%"
            )

            print(
                f"  Duplicate rate: "
                f"{quality.get('duplicate_percent')}%"
            )

        anomaly = profile.get("anomaly")

        if anomaly is not None:
            print(
                f"  Anomalies: "
                f"{anomaly.get('anomaly_count')}"
            )

            print(
                f"  Anomaly rate: "
                f"{anomaly.get('anomaly_percent')}%"
            )

    # Health score
    health = result.get("health_score")

    if health:
        print()
        print("DATA HEALTH")
        print("-" * 60)

        print(
            f"Score: {health['score']}/100"
        )

        print(
            f"Status: {health['status']}"
        )

        components = health.get(
            "components",
            {}
        )

        print(
            f"Completeness: "
            f"{components.get('completeness')}%"
        )

        print(
            f"Uniqueness: "
            f"{components.get('uniqueness')}%"
        )

        print(
            f"Validation: "
            f"{components.get('validation')}%"
        )

        print(
            f"Anomaly rate: "
            f"{components.get('anomaly_rate')}%"
        )

    # Validation
    validation = result.get("validation")

    if validation:
        print()
        print("VALIDATION")
        print("-" * 60)

        for column, item in validation.items():

            print(
                f"{column}: "
                f"{item['status']} "
                f"({item['violations']} violations)"
            )

    print()
    print("=" * 60)


def load_rules(filename):
    """Load validation rules from JSON."""

    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except FileNotFoundError:
        raise ValueError(
            f"Rules file not found: {filename}"
        )

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid rules JSON: {error}"
        )


def profile_command(args):
    """Run dataset profiling."""

    rules = None

    if args.rules:
        rules = load_rules(args.rules)

    result = DataProfiler.profile_dataset(
        filename=args.filename,
        file_type=args.file_type,
        top_k=args.top_k,
        histogram_bins=args.histogram_bins,
        rules=rules,
        anomaly_threshold=args.anomaly_threshold
    )

    if args.output:

        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4
            )

        print(
            f"Report saved to: {args.output}"
        )

    else:
        print_profile(result)

    return 0


def validate_command(args):
    """Run validation rules against a dataset."""

    if not args.rules:
        print(
            "Error: --rules is required "
            "for validation."
        )

        return 1

    rules = load_rules(
        args.rules
    )

    result = DataProfiler.profile_dataset(
        filename=args.filename,
        file_type=args.file_type,
        rules=rules,
        anomaly_threshold=args.anomaly_threshold
    )

    validation = result.get(
        "validation",
        {}
    )

    print()
    print("=" * 60)
    print("              VALIDATION REPORT")
    print("=" * 60)

    failed = False

    for column, item in validation.items():

        status = item["status"]

        print(
            f"{column}: {status}"
        )

        print(
            f"  Checked: "
            f"{item['checked']}"
        )

        print(
            f"  Violations: "
            f"{item['violations']}"
        )

        print(
            f"  Violation %: "
            f"{item['violation_percent']}%"
        )

        if status == "FAIL":
            failed = True

    print("=" * 60)

    return 1 if failed else 0


def build_parser():
    """Create CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="dataprofiler",
        description=(
            "Streaming data profiling, "
            "quality and validation tool."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # -------------------------------------------------
    # Profile command
    # -------------------------------------------------

    profile = subparsers.add_parser(
        "profile",
        help="Profile a dataset."
    )

    profile.add_argument(
        "filename",
        help="CSV, JSONL or Parquet file."
    )

    profile.add_argument(
        "--file-type",
        choices=[
            "csv",
            "jsonl",
            "parquet"
        ],
        default=None,
        help="Override automatic file-type detection."
    )

    profile.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of frequent values to keep."
    )

    profile.add_argument(
        "--histogram-bins",
        type=int,
        default=20,
        help="Number of histogram bins."
    )

    profile.add_argument(
        "--anomaly-threshold",
        type=float,
        default=3.0,
        help="Z-score anomaly threshold."
    )

    profile.add_argument(
        "--rules",
        help="JSON validation rules file."
    )

    profile.add_argument(
        "--output",
        help="Save report as JSON."
    )

    profile.set_defaults(
        func=profile_command
    )

    # -------------------------------------------------
    # Validate command
    # -------------------------------------------------

    validate = subparsers.add_parser(
        "validate",
        help="Validate a dataset."
    )

    validate.add_argument(
        "filename",
        help="CSV, JSONL or Parquet file."
    )

    validate.add_argument(
        "--rules",
        required=True,
        help="JSON validation rules file."
    )

    validate.add_argument(
        "--file-type",
        choices=[
            "csv",
            "jsonl",
            "parquet"
        ],
        default=None
    )

    validate.add_argument(
        "--anomaly-threshold",
        type=float,
        default=3.0
    )

    validate.set_defaults(
        func=validate_command
    )

    return parser


def main():
    parser = build_parser()

    args = parser.parse_args()

    if not hasattr(args, "func"):

        parser.print_help()

        return 0

    try:
        return args.func(args)

    except Exception as error:

        print(
            f"Error: {error}",
            file=sys.stderr
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())