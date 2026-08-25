import json
import subprocess
import sys


def test_cli_help():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataprofiler.cli"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_profile():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataprofiler.cli",
            "profile",
            "test_data.csv"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "DATAPROFILER REPORT" in result.stdout
    assert "Rows: 4" in result.stdout


def test_cli_profile_json_output(tmp_path):
    output_file = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataprofiler.cli",
            "profile",
            "test_data.csv",
            "--output",
            str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert output_file.exists()

    with open(
        output_file,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    assert data["rows"] == 4
    assert "columns" in data
    assert "health_score" in data


def test_cli_validate():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataprofiler.cli",
            "validate",
            "test_data.csv",
            "--rules",
            "rules.json"
        ],
        capture_output=True,
        text=True
    )

    # Validation should fail because product
    # contains a null value.
    assert result.returncode == 1
    assert "VALIDATION REPORT" in result.stdout
    assert "product: FAIL" in result.stdout
    assert "Violations: 1" in result.stdout


def test_cli_invalid_command():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "dataprofiler.cli",
            "unknown"
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode != 0