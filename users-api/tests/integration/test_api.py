"""Integration tests for the Users API."""
import json
import pytest
from flask.testing import FlaskClient

from src.app import flask_app
from src.repositories.user_repository import UserRepository
from src.models.user import User


@pytest.fixture
def client() -> FlaskClient:
    """Create a test client for the Flask app."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def setup_test_data(monkeypatch):
    """Set up test data in the repository."""
    # Create a repository with test data
    repo = UserRepository()
    
    # Add some test users
    users = [
        User(id="test-id-1", name="Test User 1", email="test1@example.com"),
        User(id="test-id-2", name="Test User 2", email="test2@example.com"),
        User(id="test-id-3", name="Different User", email="different@example.com"),
    ]
    
    for user in users:
        repo.create(user)
    
    # Monkeypatch the repository in the app
    from src import app
    monkeypatch.setattr(app, "user_repository", repo)
    
    return users


def test_list_users(client, setup_test_data):
    """Test listing users."""
    # Make the request
    response = client.get("/api/v1/users")
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "success"
    assert "users" in data["data"]
    assert "pagination" in data["data"]
    
    # Verify users data
    users = data["data"]["users"]
    assert len(users) == 3
    
    # Verify pagination
    pagination = data["data"]["pagination"]
    assert pagination["total"] == 3
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["pages"] == 1


def test_list_users_with_pagination(client, setup_test_data):
    """Test listing users with pagination."""
    # Make the request
    response = client.get("/api/v1/users?page=1&limit=2")
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify users data
    users = data["data"]["users"]
    assert len(users) == 2
    
    # Verify pagination
    pagination = data["data"]["pagination"]
    assert pagination["total"] == 3
    assert pagination["page"] == 1
    assert pagination["limit"] == 2
    assert pagination["pages"] == 2


def test_list_users_with_search(client, setup_test_data):
    """Test listing users with search."""
    # Make the request with search
    response = client.get("/api/v1/users?search=Different")
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify users data
    users = data["data"]["users"]
    assert len(users) == 1
    assert users[0]["name"] == "Different User"
    assert users[0]["email"] == "different@example.com"


def test_create_user(client):
    """Test creating a user."""
    # Make the request
    response = client.post(
        "/api/v1/users",
        json={
            "name": "New User",
            "email": "new.user@example.com"
        },
        content_type="application/json"
    )
    
    # Check status code
    assert response.status_code == 201
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "success"
    assert "user" in data["data"]
    
    # Verify user data
    user = data["data"]["user"]
    assert user["name"] == "New User"
    assert user["email"] == "new.user@example.com"
    assert "id" in user
    assert "created_at" in user
    assert "updated_at" in user


def test_create_user_validation_error(client, setup_test_data):
    """Test creating a user with validation errors."""
    # Make the request with an email that's already in use
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Duplicate Email",
            "email": "test1@example.com"  # This email is already used
        },
        content_type="application/json"
    )
    
    # Check status code
    assert response.status_code == 400
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "error"
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "errors" in data
    assert "email" in data["errors"]


def test_get_user(client, setup_test_data):
    """Test getting a user by ID."""
    # Make the request
    response = client.get("/api/v1/users/test-id-1")
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "success"
    assert "user" in data["data"]
    
    # Verify user data
    user = data["data"]["user"]
    assert user["id"] == "test-id-1"
    assert user["name"] == "Test User 1"
    assert user["email"] == "test1@example.com"


def test_get_user_not_found(client):
    """Test getting a non-existent user."""
    # Make the request
    response = client.get("/api/v1/users/nonexistent-id")
    
    # Check status code
    assert response.status_code == 404
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "error"
    assert data["error_code"] == "RESOURCE_NOT_FOUND"


def test_update_user(client, setup_test_data):
    """Test updating a user."""
    # Make the request
    response = client.put(
        "/api/v1/users/test-id-1",
        json={
            "name": "Updated Name",
            "email": "updated.email@example.com"
        },
        content_type="application/json"
    )
    
    # Check status code
    assert response.status_code == 200
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "success"
    assert "user" in data["data"]
    
    # Verify user data
    user = data["data"]["user"]
    assert user["id"] == "test-id-1"
    assert user["name"] == "Updated Name"
    assert user["email"] == "updated.email@example.com"


def test_update_user_email_conflict(client, setup_test_data):
    """Test updating a user with an email that's already in use."""
    # Make the request
    response = client.put(
        "/api/v1/users/test-id-1",
        json={
            "email": "test2@example.com"  # This email is used by test-id-2
        },
        content_type="application/json"
    )
    
    # Check status code
    assert response.status_code == 400
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "error"
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "errors" in data
    assert "email" in data["errors"]


def test_update_user_not_found(client):
    """Test updating a non-existent user."""
    # Make the request
    response = client.put(
        "/api/v1/users/nonexistent-id",
        json={"name": "New Name"},
        content_type="application/json"
    )
    
    # Check status code
    assert response.status_code == 404
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "error"
    assert data["error_code"] == "RESOURCE_NOT_FOUND"


def test_delete_user(client, setup_test_data):
    """Test deleting a user."""
    # Make the request
    response = client.delete("/api/v1/users/test-id-1")
    
    # Check status code
    assert response.status_code == 204
    assert response.data == b""  # No content
    
    # Verify user was deleted by trying to get it
    get_response = client.get("/api/v1/users/test-id-1")
    assert get_response.status_code == 404


def test_delete_user_not_found(client):
    """Test deleting a non-existent user."""
    # Make the request
    response = client.delete("/api/v1/users/nonexistent-id")
    
    # Check status code
    assert response.status_code == 404
    
    # Parse response
    data = json.loads(response.data)
    
    # Verify response format
    assert data["status"] == "error"
    assert data["error_code"] == "RESOURCE_NOT_FOUND"