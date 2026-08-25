import pytest

from dataprofiler.topk import TopK


def test_topk_basic():
    topk = TopK(k=3)

    values = [
        "apple",
        "banana",
        "apple",
        "orange",
        "apple",
        "banana",
        "banana",
        "banana",
        "orange",
    ]

    for value in values:
        topk.update(value)

    result = topk.top()

    assert result[0] == ("banana", 4)
    assert result[1] == ("apple", 3)
    assert result[2] == ("orange", 2)


def test_topk_estimate():
    topk = TopK(k=2)

    topk.update("a")
    topk.update("a")
    topk.update("b")

    assert topk.estimate("a") == 2
    assert topk.estimate("b") == 1
    assert topk.estimate("x") == 0


def test_topk_empty_values():
    topk = TopK(k=3)

    topk.update(None)
    topk.update("")

    assert topk.top() == []


def test_topk_invalid_k():
    with pytest.raises(ValueError):
        TopK(k=0)


def test_topk_dict():
    topk = TopK(k=2)

    for value in ["a", "a", "b", "c"]:
        topk.update(value)

    result = topk.to_dict()

    assert result["k"] == 2
    assert len(result["top"]) == 2