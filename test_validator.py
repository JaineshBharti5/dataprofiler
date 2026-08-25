from dataprofiler.validator import ValidationEngine


def test_nullable_rule():

    engine = ValidationEngine({
        "age": {
            "nullable": False
        }
    })

    engine.update("age", 20)
    engine.update("age", None)

    result = engine.column_result("age")

    assert result["status"] == "FAIL"
    assert result["checked"] == 2
    assert result["violations"] == 1
    assert result["details"]["null"] == 1


def test_min_max_rules():

    engine = ValidationEngine({
        "age": {
            "min": 0,
            "max": 120
        }
    })

    engine.update("age", 20)
    engine.update("age", -5)
    engine.update("age", 150)

    result = engine.column_result("age")

    assert result["status"] == "FAIL"
    assert result["checked"] == 3
    assert result["violations"] == 2
    assert result["details"]["min"] == 1
    assert result["details"]["max"] == 1


def test_length_rules():

    engine = ValidationEngine({
        "username": {
            "min_length": 3,
            "max_length": 10
        }
    })

    engine.update("username", "ab")
    engine.update("username", "alice")
    engine.update(
        "username",
        "verylongusername"
    )

    result = engine.column_result("username")

    assert result["status"] == "FAIL"
    assert result["violations"] == 2
    assert result["details"]["min_length"] == 1
    assert result["details"]["max_length"] == 1


def test_allowed_values():

    engine = ValidationEngine({
        "status": {
            "allowed_values": [
                "active",
                "inactive"
            ]
        }
    })

    engine.update("status", "active")
    engine.update("status", "inactive")
    engine.update("status", "deleted")

    result = engine.column_result("status")

    assert result["status"] == "FAIL"
    assert result["violations"] == 1
    assert result["details"]["allowed_values"] == 1


def test_validation_pass():

    engine = ValidationEngine({
        "age": {
            "min": 0,
            "max": 120,
            "nullable": False
        }
    })

    engine.update("age", 20)
    engine.update("age", 40)
    engine.update("age", 80)

    result = engine.column_result("age")

    assert result["status"] == "PASS"
    assert result["checked"] == 3
    assert result["violations"] == 0
    assert result["violation_percent"] == 0.0


def test_row_validation():

    engine = ValidationEngine({
        "age": {
            "min": 0,
            "max": 120
        },
        "status": {
            "allowed_values": [
                "active",
                "inactive"
            ]
        }
    })

    engine.validate({
        "age": 25,
        "status": "active"
    })

    engine.validate({
        "age": 150,
        "status": "deleted"
    })

    result = engine.report()

    assert result["age"]["violations"] == 1
    assert result["status"]["violations"] == 1