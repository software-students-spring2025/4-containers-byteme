import pytest
from app import app
from flask_login import current_user
from unittest.mock import patch
from bson.objectid import ObjectId


class MockUser:
    """Mock user class to simulate a user object."""
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True  # Simulating an authenticated user
        self.is_active = True  # Active user
        self.is_anonymous = False  # Not an anonymous user
    
    def get_id(self):
        return self.id
    

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("app.users")
@patch("app.bcrypt")
def test_login_success(mock_bcrypt, mock_users, client):
    """Test successful login."""
    mock_users.find_one.return_value = {"_id": ObjectId(), "username": "testuser", "password": "hashed_password"}
    mock_bcrypt.check_password_hash.return_value = True

    response = client.post("/login-signup", data={"username": "testuser", "password": "password", "submit": "Login"})
    assert response.status_code == 302
    assert response.location.endswith("/")


@patch("app.users")
def test_login_failure(mock_users, client):
    """Test failed login."""
    mock_users.find_one.return_value = None

    response = client.post("/login-signup", data={"username": "testuser", "password": "password", "submit": "Login"})
    assert response.status_code == 400
    assert b"Invalid credentials" in response.data


@patch("app.users")
@patch("app.bcrypt")
def test_signup_success(mock_bcrypt, mock_users, client):
    """Test successful signup."""
    mock_users.find_one.return_value = None
    mock_bcrypt.generate_password_hash.return_value = b"hashed_password"

    response = client.post("/login-signup", data={"username": "newuser", "password": "password", "submit": "Sign Up"})
    assert response.status_code == 302
    assert response.location.endswith("/login-signup")


@patch("app.users")
def test_signup_failure(mock_users, client):
    """Test signup failure when user already exists."""
    mock_users.find_one.return_value = {"_id": ObjectId(), "username": "existinguser"}

    response = client.post("/login-signup", data={"username": "existinguser", "password": "password", "submit": "Sign Up"})
    assert response.status_code == 400
    assert b"User already exists" in response.data


# @patch("app.logout_user")
# @patch("app.current_user")
# def test_logout(mock_current_user, mock_logout_user, client):
#     """Test the logout route for an authenticated user."""
#     mock_current_user.is_authenticated = True
#     response = client.get("/logout")

#     mock_logout_user.assert_called_once()
#     assert response.status_code == 302
#     assert response.location.endswith("/login-signup")



@patch("app.render_template")
@patch("app.entries")
@patch("app.current_user")
def test_home_authenticated(mock_current_user, mock_entries, mock_render_template, client):
    """Test the home route for authenticated users."""
    mock_current_user.is_authenticated = True
    mock_current_user.id = "test_user_id"

    # Mock database return value
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

    assert response.status_code == 302  # Check redirect occurred
    assert "/login-signup" in response.location


import pytest
from unittest.mock import patch, MagicMock
from flask_login import login_user, current_user
from app import app
from bson import ObjectId  # Import ObjectId to create a valid ObjectId
from flask import session

# Mock user class to simulate a user object
class MockUser:
    def __init__(self, id):
        self.id = id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)  # Ensure the get_id method returns a string of the user id

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("app.render_template")
@patch("app.current_user")
@patch("app.users")  # Mocking the users database
def test_add_entry(mock_users, mock_current_user, mock_render_template, client):
    """Test the add-entry page for an authenticated user."""
    
    # Mock the user object
    user = MockUser(id=ObjectId())  # Using a valid ObjectId here

    # Mock the database call (users.find_one) to return the mock user when queried by ObjectId
    mock_users.find_one.return_value = {"_id": user.id, "username": "testuser", "password": "hashed_password"}

    # Set up the mock for current_user
    mock_current_user.is_authenticated = True
    mock_current_user.id = user.get_id()  # Set current_user.id to the mock user's id
    mock_current_user.get_id = user.get_id  # This ensures current_user.get_id() works as expected

    # Simulate a user being logged in by manually setting the session
    with client.session_transaction() as session:
        session['_user_id'] = str(user.id)  # Set the user ID in the session as a string

    # Now, make the request to the /add-entry route
    response = client.get("/add-entry")

    assert response.status_code == 200
    mock_render_template.assert_called_once_with("new_entry.html")



# @patch("app.requests.post")
# @patch("app.current_user")
# @patch("app.entries")
# def test_submit_entry(mock_entries, client):
#     """Test submitting a journal entry."""
#     with patch("app.current_user") as mock_user, patch("app.requests.post") as mock_requests:
#         mock_user.is_authenticated = True
#         mock_user.id = "12345"
#         test_entry_id = ObjectId("67f6d1236aaf92738f8f8855")
#         mock_entries.insert_one.return_value.inserted_id = test_entry_id
#         mock_requests.return_value.status_code = 200
#         mock_requests.return_value.json.return_value = {
#             "status": "updated",
#             "entry_id": str(test_entry_id),
#         }

#         response = client.post("/submit-entry", data={
#             "date": "2023-01-01",
#             "entry": "Test entry"
#         })

#         assert response.status_code == 302
#         assert response.location.endswith(f"/entry/{test_entry_id}")
#         mock_entries.insert_one.assert_called_once_with({
#             "user_id": "12345",
#             "journal_date": "2023-01-01",
#             "text": "Test entry",
#         })
#         mock_requests.assert_called_once()


@patch("app.entries")
@patch("app.render_template")
@patch("app.current_user")
def test_view_entry_found(mock_current_user, mock_render_template, mock_entries, client):
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
            "composite_score": 4.8
        }
    }

    mock_current_user.is_authenticated = True
    mock_current_user.id = "12345"
    mock_entries.find_one.return_value = test_entry

    response = client.get("/entry/67f6d1236aaf92738f8f8855")

    assert response.status_code == 200
    mock_render_template.assert_called_once_with(
        "page.html",
        entry=test_entry,
        sentiment_score=4.8
    )


@patch("app.entries")
@patch("app.current_user")
def test_view_entry_not_found(mock_current_user, mock_entries, client):
    """Test rendering a journal entry page when the entry is not found."""
    mock_current_user.is_authenticated = True
    mock_current_user.id = "12345"
    mock_entries.find_one.return_value = None

    response = client.get("/entry/67f6d1236aaf92738f8f8855")

    assert response.status_code == 404
    assert b"Entry not found" in response.data
