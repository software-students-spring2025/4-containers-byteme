"""Unit tests for the Flask application."""

from unittest.mock import patch
import pytest
from bson.objectid import ObjectId
from flask_login import UserMixin
from app import app


class MockUser(UserMixin):
    """Mock user class to simulate a user object."""

    def __init__(self, user_id):
        self.user_id = user_id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.user_id)


@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client_fixture:
        yield client_fixture


@patch("app.users")
@patch("app.bcrypt")
def test_login_success(mock_bcrypt, mock_users, test_client):
    """Test successful login."""
    mock_users.find_one.return_value = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "hashed_password",
    }
    mock_bcrypt.check_password_hash.return_value = True

    response = test_client.post(
        "/login-signup",
        data={"username": "testuser", "password": "password", "submit": "Login"},
    )
    assert response.status_code == 302
    assert response.location.endswith("/")


@patch("app.users")
def test_login_failure(mock_users, client):
    """Test failed login."""
    mock_users.find_one.return_value = None

    response = client.post(
        "/login-signup",
        data={"username": "testuser", "password": "password", "submit": "Login"},
    )
    assert response.status_code == 400
    assert b"Invalid credentials" in response.data


@patch("app.users")
@patch("app.bcrypt")
def test_signup_success(mock_bcrypt, mock_users, client):
    """Test successful signup."""
    mock_users.find_one.return_value = None
    mock_bcrypt.generate_password_hash.return_value = b"hashed_password"

    response = client.post(
        "/login-signup",
        data={"username": "newuser", "password": "password", "submit": "Sign Up"},
    )
    assert response.status_code == 302
    assert response.location.endswith("/login-signup")


@patch("app.users")
def test_signup_failure(mock_users, client):
    """Test signup failure when user already exists."""
    mock_users.find_one.return_value = {
        "_id": ObjectId(),
        "username": "existinguser",
    }

    response = client.post(
        "/login-signup",
        data={"username": "existinguser", "password": "password", "submit": "Sign Up"},
    )
    assert response.status_code == 400
    assert b"User already exists" in response.data


@patch("app.render_template")
@patch("app.entries")
@patch("app.current_user")
def test_home_authenticated(mock_current_user, mock_entries, mock_render_template, client):
    """Test the home route for authenticated users."""
    mock_current_user.is_authenticated = True
    mock_current_user.id = "test_user_id"

    fake_entries = [{"_id": 1, "text": "Test entry"}]
    mock_entries.find.return_value.sort.return_value = fake_entries

    response = client.get("/")

    assert response.status_code == 200
    mock_entries.find.assert_called_once_with({"user_id": "test_user_id"})
    mock_render_template.assert_called_once_with("index.html", entries=fake_entries)


@patch("app.current_user")
def test_home_unauthenticated(mock_current_user, client):
    """Test the home route for unauthenticated users."""
    mock_current_user.is_authenticated = False

    response = client.get("/")
    assert response.status_code == 302
    assert "/login-signup" in response.location


@patch("app.render_template")
@patch("app.current_user")
@patch("app.users")
def test_add_entry(mock_users, mock_current_user, mock_render_template, client):
    """Test the add-entry page for an authenticated user."""
    user = MockUser(user_id=ObjectId())
    mock_users.find_one.return_value = {
        "_id": user.user_id,
        "username": "testuser",
        "password": "hashed_password",
    }

    mock_current_user.is_authenticated = True
    mock_current_user.get_id.return_value = str(user.user_id)

    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)

    response = client.get("/add-entry")
    assert response.status_code == 200
    mock_render_template.assert_called_once_with("new_entry.html")


@patch("app.requests.post")
@patch("app.entries")
@patch("app.current_user")
@patch("app.users")
def test_submit_entry(mock_users, mock_current_user, mock_entries, mock_requests, client):
    """Test submitting a journal entry."""
    test_entry_id = ObjectId("67f6d1236aaf92738f8f8855")
    mock_entries.insert_one.return_value.inserted_id = test_entry_id
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {
        "status": "updated",
        "entry_id": str(test_entry_id),
    }

    user = MockUser(user_id=ObjectId("67f5ea3b20185e29bd744a71"))
    mock_users.find_one.return_value = {
        "_id": user.user_id,
        "username": "testuser",
        "password": "hashed_password",
    }

    mock_current_user.is_authenticated = True
    mock_current_user.get_id.return_value = str(user.user_id)

    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)

    response = client.post(
        "/submit-entry",
        data={"date": "2023-01-01", "entry": "Test entry"},
    )

    assert response.status_code == 302
    assert response.location.endswith(f"/entry/{test_entry_id}")
    mock_entries.insert_one.assert_called_once_with(
        {
            "user_id": ObjectId("67f5ea3b20185e29bd744a71"),
            "journal_date": "2023-01-01",
            "text": "Test entry",
        }
    )
    mock_requests.assert_called_once()


@patch("app.entries")
@patch("app.render_template")
@patch("app.current_user")
@patch("app.users")
def test_view_entry_found(mock_users, mock_current_user, 
                          mock_render_template, mock_entries, client):
    """Test rendering a journal entry page when the entry is found."""
    test_entry = {
        "_id": ObjectId("67f6d1236aaf92738f8f8855"),
        "user_id": "12345",
        "journal_date": "2023-01-01",
        "text": "Test entry",
        "sentiment": {
            "positive": 0.9,
            "neutral": 0.1,
            "negative": 0.0,
            "composite_score": 4.8,
        },
    }

    user = MockUser(user_id=ObjectId())
    mock_users.find_one.return_value = {
        "_id": user.user_id,
        "username": "testuser",
        "password": "hashed_password",
    }

    mock_current_user.is_authenticated = True
    mock_current_user.get_id.return_value = str(user.user_id)

    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)

    mock_entries.find_one.return_value = test_entry

    response = client.get("/entry/67f6d1236aaf92738f8f8855")
    assert response.status_code == 200
    mock_render_template.assert_called_once_with(
        "page.html", entry=test_entry, sentiment_score=4.8
    )


@patch("app.entries")
@patch("app.current_user")
@patch("app.users")
def test_view_entry_not_found(mock_users, mock_current_user, mock_entries, client):
    """Test rendering a journal entry page when the entry is not found."""
    mock_entries.find_one.return_value = None

    user = MockUser(user_id=ObjectId())
    mock_users.find_one.return_value = {
        "_id": user.user_id,
        "username": "testuser",
        "password": "hashed_password",
    }

    mock_current_user.is_authenticated = True
    mock_current_user.get_id.return_value = str(user.user_id)

    with client.session_transaction() as session:
        session["_user_id"] = str(user.user_id)

    response = client.get("/entry/67f6d1236aaf92738f8f8855")
    assert response.status_code == 404
    assert b"Entry not found" in response.data
