import pytest

from dataprofiler.health import HealthScore


def test_perfect_score():

    health = HealthScore()

    result = health.report(
        completeness=100,
        uniqueness=100,
        validation=100,
        anomalies=0
    )

    assert result["score"] == 100.0
    assert result["status"] == "EXCELLENT"


def test_zero_score():

    health = HealthScore()

    result = health.report(
        completeness=0,
        uniqueness=0,
        validation=0,
        anomalies=100
    )

    assert result["score"] == 0.0
    assert result["status"] == "POOR"


def test_mixed_score():

    health = HealthScore()

    result = health.report(
        completeness=90,
        uniqueness=80,
        validation=95,
        anomalies=10
    )

    assert 0 < result["score"] < 100
    assert "components" in result


def test_anomalies_reduce_score():

    health = HealthScore()

    without_anomalies = health.calculate(
        100,
        100,
        100,
        0
    )

    with_anomalies = health.calculate(
        100,
        100,
        100,
        50
    )

    assert with_anomalies < without_anomalies


def test_invalid_weights():

    with pytest.raises(ValueError):

        HealthScore(
            completeness_weight=0.5,
            uniqueness_weight=0.5,
            validation_weight=0.5,
            anomaly_weight=0.5
        )


def test_negative_weight():

    with pytest.raises(ValueError):

        HealthScore(
            completeness_weight=-0.1,
            uniqueness_weight=0.3,
            validation_weight=0.5,
            anomaly_weight=0.3
        )


def test_score_is_clamped():

    health = HealthScore()

    result = health.calculate(
        150,
        -10,
        200,
        -20
    )

    assert 0 <= result <= 100