"""Tests for the user service."""
import pytest
from unittest.mock import Mock

from src.models.user import User
from src.services.user_service import UserService
from src.utils.validation import ValidationException


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    return Mock()


@pytest.fixture
def user_service(mock_user_repository):
    """Create a user service with a mock repository."""
    return UserService(mock_user_repository)


def test_get_users(user_service, mock_user_repository):
    """Test getting a list of users."""
    # Setup mock repository
    mock_users = [
        User(id="1", name="John Doe", email="john@example.com"),
        User(id="2", name="Jane Smith", email="jane@example.com")
    ]
    mock_pagination = {
        "total": 2,
        "page": 1,
        "limit": 10,
        "pages": 1
    }
    mock_user_repository.get_all.return_value = (mock_users, mock_pagination)
    
    # Call the service
    users, pagination = user_service.get_users(page=1, limit=10, search="test")
    
    # Verify repository was called with correct parameters
    mock_user_repository.get_all.assert_called_once_with(1, 10, "test")
    
    # Verify response
    assert len(users) == 2
    assert users[0]["id"] == "1"
    assert users[0]["name"] == "John Doe"
    assert users[1]["id"] == "2"
    assert users[1]["name"] == "Jane Smith"
    assert pagination == mock_pagination


def test_create_user_success(user_service, mock_user_repository):
    """Test successfully creating a user."""
    # Setup mock repository
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.create.return_value = User(
        id="1", 
        name="John Doe", 
        email="john@example.com"
    )
    
    # Call the service
    user = user_service.create_user(name="John Doe", email="john@example.com")
    
    # Verify repository was called correctly
    mock_user_repository.get_by_email.assert_called_once_with("john@example.com")
    mock_user_repository.create.assert_called_once()
    
    # Verify response
    assert user["id"] == "1"
    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"


def test_create_user_email_exists(user_service, mock_user_repository):
    """Test creating a user with an existing email."""
    # Setup mock repository to return an existing user
    mock_user_repository.get_by_email.return_value = User(
        id="1", 
        name="Existing User", 
        email="john@example.com"
    )
    
    # Call the service and expect an exception
    with pytest.raises(ValidationException) as exc_info:
        user_service.create_user(name="John Doe", email="john@example.com")
    
    # Verify the exception details
    assert "Email is already in use" in str(exc_info.value.errors)
    
    # Verify repository was called correctly
    mock_user_repository.get_by_email.assert_called_once_with("john@example.com")
    mock_user_repository.create.assert_not_called()


def test_get_user_by_id_exists(user_service, mock_user_repository):
    """Test getting a user by ID when the user exists."""
    # Setup mock repository
    mock_user_repository.get_by_id.return_value = User(
        id="1", 
        name="John Doe", 
        email="john@example.com"
    )
    
    # Call the service
    user = user_service.get_user_by_id("1")
    
    # Verify repository was called correctly
    mock_user_repository.get_by_id.assert_called_once_with("1")
    
    # Verify response
    assert user["id"] == "1"
    assert user["name"] == "John Doe"
    assert user["email"] == "john@example.com"


def test_get_user_by_id_not_exists(user_service, mock_user_repository):
    """Test getting a user by ID when the user doesn't exist."""
    # Setup mock repository
    mock_user_repository.get_by_id.return_value = None
    
    # Call the service
    user = user_service.get_user_by_id("999")
    
    # Verify repository was called correctly
    mock_user_repository.get_by_id.assert_called_once_with("999")
    
    # Verify response
    assert user is None


def test_update_user_success(user_service, mock_user_repository):
    """Test successfully updating a user."""
    # Setup mock repository
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.update.return_value = User(
        id="1", 
        name="John Doe Jr.", 
        email="john.jr@example.com"
    )
    
    # Call the service
    user = user_service.update_user("1", name="John Doe Jr.", email="john.jr@example.com")
    
    # Verify repository was called correctly
    mock_user_repository.get_by_email.assert_called_once_with("john.jr@example.com")
    mock_user_repository.update.assert_called_once_with("1", "John Doe Jr.", "john.jr@example.com")
    
    # Verify response
    assert user["id"] == "1"
    assert user["name"] == "John Doe Jr."
    assert user["email"] == "john.jr@example.com"


def test_update_user_email_exists(user_service, mock_user_repository):
    """Test updating a user with an email that's already in use by another user."""
    # Setup mock repository to return a different user with the same email
    mock_user_repository.get_by_email.return_value = User(
        id="2",  # Different ID
        name="Another User", 
        email="john.jr@example.com"
    )
    
    # Call the service and expect an exception
    with pytest.raises(ValidationException) as exc_info:
        user_service.update_user("1", email="john.jr@example.com")
    
    # Verify the exception details
    assert "Email is already in use" in str(exc_info.value.errors)
    
    # Verify repository was called correctly
    mock_user_repository.get_by_email.assert_called_once_with("john.jr@example.com")
    mock_user_repository.update.assert_not_called()


def test_update_user_not_found(user_service, mock_user_repository):
    """Test updating a user that doesn't exist."""
    # Setup mock repository
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.update.return_value = None
    
    # Call the service
    user = user_service.update_user("999", name="Nonexistent User")
    
    # Verify repository was called correctly
    mock_user_repository.update.assert_called_once_with("999", "Nonexistent User", None)
    
    # Verify response
    assert user is None


def test_delete_user(user_service, mock_user_repository):
    """Test deleting a user."""
    # Setup mock repository
    mock_user_repository.delete.return_value = True
    
    # Call the service
    result = user_service.delete_user("1")
    
    # Verify repository was called correctly
    mock_user_repository.delete.assert_called_once_with("1")
    
    # Verify response
    assert result is True


def test_delete_user_not_found(user_service, mock_user_repository):
    """Test deleting a user that doesn't exist."""
    # Setup mock repository
    mock_user_repository.delete.return_value = False
    
    # Call the service
    result = user_service.delete_user("999")
    
    # Verify repository was called correctly
    mock_user_repository.delete.assert_called_once_with("999")
    
    # Verify response
    assert result is False