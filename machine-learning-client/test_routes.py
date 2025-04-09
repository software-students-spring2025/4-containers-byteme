"""unit tests for ml-client routes"""

from unittest.mock import patch
import pytest
from ml_client import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@patch("ml_client.entries_col")
@patch("ml_client.analyze_sentiment")
def test_analyze_and_store_success(
    mock_analyze, mock_entries_col, client
):  # pylint: disable=redefined-outer-name
    """Test the /analyze route for successful sentiment analysis and DB update."""
    test_entry_id = "123"
    test_text = "I love this app!"
    mock_analyze.return_value = {
        "negative": 0.01,
        "neutral": 0.15,
        "positive": 0.84,
        "composite_score": 4.53,
    }

    response = client.post(
        "/analyze", json={"entry_id": test_entry_id, "text": test_text}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "updated"
    assert data["entry_id"] == test_entry_id

    mock_analyze.assert_called_once_with(test_text)
    mock_entries_col.update_one.assert_called_once()
