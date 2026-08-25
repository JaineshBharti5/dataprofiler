from datetime import datetime


def is_null(value):
    """
    Check whether a value represents a null or empty value.
    """

    if value is None:
        return True

    if isinstance(value, str):
        return value.strip().lower() in {
            "",
            "null",
            "none",
            "nan",
        }

    return False


def detect_type(value):
    """
    Detect the basic data type of a single value.

    Returns:
        null
        boolean
        integer
        float
        datetime
        string
    """

    if is_null(value):
        return "null"

    # Boolean must be checked before integer because
    # bool is a subclass of int in Python.
    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "float"

    if isinstance(value, datetime):
        return "datetime"

    if isinstance(value, str):
        text = value.strip()

        # Boolean
        if text.lower() in {
            "true",
            "false",
        }:
            return "boolean"

        # Integer
        try:
            int(text)
            return "integer"
        except ValueError:
            pass

        # Float
        try:
            float(text)
            return "float"
        except ValueError:
            pass

        # Datetime
        datetime_formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
        ]

        for fmt in datetime_formats:
            try:
                datetime.strptime(text, fmt)
                return "datetime"
            except ValueError:
                continue

        return "string"

    return "string"


def infer_column_type(values):
    """
    Infer the type of a column from multiple values.

    Null values are ignored.

    Returns:
        null
        boolean
        integer
        float
        datetime
        string
        mixed
    """

    detected = []

    for value in values:
        value_type = detect_type(value)

        if value_type != "null":
            detected.append(value_type)

    # All values are null
    if not detected:
        return "null"

    unique_types = set(detected)

    # One consistent type
    if len(unique_types) == 1:
        return detected[0]

    # Integer + float = float
    if unique_types <= {
        "integer",
        "float",
    }:
        return "float"

    # Different incompatible types
    return "mixed"