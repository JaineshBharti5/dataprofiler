import pytest

from dataprofiler.anomaly import AnomalyDetector


def test_empty_detector():
    detector = AnomalyDetector()

    result = detector.to_dict()

    assert result["count"] == 0
    assert result["anomaly_count"] == 0
    assert result["anomaly_percent"] == 0.0


def test_basic_statistics():
    detector = AnomalyDetector()

    for value in [10, 20, 30, 40, 50]:
        detector.update(value)

    result = detector.to_dict()

    assert result["count"] == 5
    assert result["mean"] == 30.0
    assert result["stddev"] > 0


def test_constant_values():
    detector = AnomalyDetector()

    for value in [10, 10, 10, 10, 10]:
        assert detector.update(value) is False

    result = detector.to_dict()

    assert result["count"] == 5
    assert result["anomaly_count"] == 0


def test_invalid_values():
    detector = AnomalyDetector()

    assert detector.update(None) is False
    assert detector.update("abc") is False

    result = detector.to_dict()

    assert result["count"] == 0


def test_invalid_threshold():
    with pytest.raises(ValueError):
        AnomalyDetector(threshold=0)


def test_anomaly_tracking():
    detector = AnomalyDetector(threshold=2.0)

    for value in [
        10,
        11,
        10,
        12,
        11,
        10,
        100,
    ]:
        detector.update(value)

    result = detector.to_dict()

    assert result["count"] == 7
    assert result["anomaly_count"] >= 1
    assert result["anomaly_percent"] > 0