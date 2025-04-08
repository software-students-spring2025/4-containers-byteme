"""unit tests for sentiment analysis functions"""
import pytest
from ml_client import analyze_sentiment


@pytest.mark.parametrize(
    "text,expected_key",
    [
        ("It was a sunny day", "positive"),
        ("It was an average day", "neutral"),
        ("I'm so frustrated right now", "negative"),
    ],
)
def test_analyze_sentiment_keys(text, expected_key):
    """
    Test that analyze_sentiment returns valid keys and expected dominant sentiment.

    This test verifies that the output dictionary from analyze_sentiment includes
    all expected sentiment keys ('positive', 'neutral', 'negative', 'composite_score'),
    and that the sentiment corresponding to the expected key has a non-zero score.
    """
    result = analyze_sentiment(text)
    assert "negative" in result
    assert "positive" in result
    assert "neutral" in result
    assert "composite_score" in result
    assert result[expected_key] > 0


@pytest.mark.parametrize(
    "text",
    ["It was a sunny day", "It was an average day", "I'm so frustrated right now"],
)
def test_composite_score_range(text):
    """test composite score range"""
    result = analyze_sentiment(text)
    assert 1.0 <= result["composite_score"] <= 5.0
