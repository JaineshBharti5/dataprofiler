from .types import is_null


class ValidationEngine:
    """
    Streaming data-quality validation engine.

    Supports rules such as:
        nullable
        min
        max
        min_length
        max_length
        allowed_values
    """

    def __init__(self, rules=None):
        self.rules = rules or {}
        self.stats = {}

        for column in self.rules:
            self.stats[column] = {
                "checked": 0,
                "violations": 0,
                "null_violations": 0,
                "min_violations": 0,
                "max_violations": 0,
                "min_length_violations": 0,
                "max_length_violations": 0,
                "allowed_values_violations": 0,
            }

    def update(self, column, value):
        """
        Validate one value against a column's rules.
        """

        if column not in self.rules:
            return

        rules = self.rules[column]
        stats = self.stats[column]

        stats["checked"] += 1

        violated = False

        # -----------------------------
        # Nullable
        # -----------------------------

        if is_null(value):
            if rules.get("nullable") is False:
                stats["null_violations"] += 1
                violated = True

            if violated:
                stats["violations"] += 1

            return

        # -----------------------------
        # Numeric minimum
        # -----------------------------

        if "min" in rules:
            try:
                numeric_value = float(value)

                if numeric_value < rules["min"]:
                    stats["min_violations"] += 1
                    violated = True

            except (ValueError, TypeError):
                pass

        # -----------------------------
        # Numeric maximum
        # -----------------------------

        if "max" in rules:
            try:
                numeric_value = float(value)

                if numeric_value > rules["max"]:
                    stats["max_violations"] += 1
                    violated = True

            except (ValueError, TypeError):
                pass

        # -----------------------------
        # Minimum length
        # -----------------------------

        if "min_length" in rules:

            if len(str(value)) < rules["min_length"]:
                stats["min_length_violations"] += 1
                violated = True

        # -----------------------------
        # Maximum length
        # -----------------------------

        if "max_length" in rules:

            if len(str(value)) > rules["max_length"]:
                stats["max_length_violations"] += 1
                violated = True

        # -----------------------------
        # Allowed values
        # -----------------------------

        if "allowed_values" in rules:

            if value not in rules["allowed_values"]:
                stats["allowed_values_violations"] += 1
                violated = True

        if violated:
            stats["violations"] += 1

    def validate(self, data):
        """
        Validate a dictionary representing one row.
        """

        if not isinstance(data, dict):
            raise ValueError(
                "Validation input must be a dictionary."
            )

        for column, value in data.items():
            self.update(column, value)

    def column_result(self, column):
        """
        Return validation result for one column.
        """

        if column not in self.rules:
            raise ValueError(
                f"No rules defined for column '{column}'."
            )

        stats = self.stats[column]
        checked = stats["checked"]

        violation_percent = (
            stats["violations"] / checked * 100
            if checked > 0
            else 0.0
        )

        status = (
            "PASS"
            if stats["violations"] == 0
            else "FAIL"
        )

        return {
            "status": status,
            "checked": checked,
            "violations": stats["violations"],
            "violation_percent": round(
                violation_percent,
                2
            ),
            "details": {
                "null": stats["null_violations"],
                "min": stats["min_violations"],
                "max": stats["max_violations"],
                "min_length": (
                    stats["min_length_violations"]
                ),
                "max_length": (
                    stats["max_length_violations"]
                ),
                "allowed_values": (
                    stats["allowed_values_violations"]
                ),
            },
        }

    def report(self):
        """
        Return validation results for all columns.
        """

        return {
            column: self.column_result(column)
            for column in self.rules
        }