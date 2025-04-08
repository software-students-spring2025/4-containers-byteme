"""unit tests for sentiment analysis functions"""

import pytest
from ml_client import analyze_sentiment

def test_analyze_sentiment_returns_valid_output():
    """Test that analyze_sentiment returns a dictionary"""
    text = "Today was such a good day. I woke up feeling refreshed and energized."
    result = analyze_sentiment(text)
    assert isinstance(result, dict), "Result should be a dictionary."

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
    assert "negative" in result, "Expected 'negative' key in result"
    assert "positive" in result, "Expected 'positive' key in result"
    assert "neutral" in result, "Expected 'neutral' key in result"
    assert "composite_score" in result, "Expected 'composite_score' key in result"
    assert result[expected_key] > 0, f"Expected {expected_key} sentiment score to be greater than 0"


@pytest.mark.parametrize(
    "text",
    ["It was a sunny day", "It was an average day", "I'm so frustrated right now"],
)
def test_composite_score_range(text):
    """test composite score range"""
    result = analyze_sentiment(text)
    assert 1.0 <= result["composite_score"] <= 5.0, "Composite score out of range."


def test_analyze_sentiment_positive():
    """Test sentiment scores for positive text"""
    text = "Today was such a good day. I woke up feeling refreshed and energized."
    sentiment_score = analyze_sentiment(text)
    assert sentiment_score["positive"] > 0.5, (
        "Expected positive sentiment score to be greater than 0.5"
    )
    assert sentiment_score["negative"] < 0.1, (
        "Expected negative sentiment score to be less than 0.1"
    )
    assert sentiment_score["composite_score"] > 3, (
        "Expected composite score to be greater than 3"
    )


def test_analyze_sentiment_negative():
    """Test sentiment scores for negative text"""
    text = "I feel frustrated today. Nothing seems to be going right at work"
    sentiment_score = analyze_sentiment(text)
    assert sentiment_score["positive"] < 0.1, (
        "Expected positive sentiment score to be less than 0.1"
    )
    assert sentiment_score["negative"] > 0.5, (
        "Expected negative sentiment score to be greater than 0.5"
    )
    assert sentiment_score["composite_score"] < 3, (
        "Expected composite score to be less than 3"
    )
    
