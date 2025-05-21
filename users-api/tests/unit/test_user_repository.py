"""Tests for the user repository."""
import pytest
from src.models.user import User
from src.repositories.user_repository import UserRepository


@pytest.fixture
def user_repository():
    """Create a test user repository."""
    return UserRepository()


@pytest.fixture
def sample_users(user_repository):
    """Create sample users for testing."""
    users = [
        User(id="1", name="John Doe", email="john@example.com"),
        User(id="2", name="Jane Smith", email="jane@example.com"),
        User(id="3", name="Alice Johnson", email="alice@example.com"),
    ]
    
    for user in users:
        user_repository.create(user)
    
    return users


def test_get_all_users(user_repository, sample_users):
    """Test retrieving all users."""
    users, pagination = user_repository.get_all()
    
    assert len(users) == len(sample_users)
    assert pagination["total"] == len(sample_users)
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["pages"] == 1


def test_get_all_users_with_pagination(user_repository, sample_users):
    """Test retrieving users with pagination."""
    users, pagination = user_repository.get_all(page=1, limit=2)
    
    assert len(users) == 2
    assert pagination["total"] == len(sample_users)
    assert pagination["page"] == 1
    assert pagination["limit"] == 2
    assert pagination["pages"] == 2


def test_get_all_users_with_search(user_repository, sample_users):
    """Test retrieving users with search."""
    # Search by name
    users, pagination = user_repository.get_all(search="John")
    assert len(users) == 1
    assert users[0].name == "John Doe"
    
    # Search by email
    users, pagination = user_repository.get_all(search="jane")
    assert len(users) == 1
    assert users[0].name == "Jane Smith"
    
    # Search with no matches
    users, pagination = user_repository.get_all(search="Unknown")
    assert len(users) == 0


def test_get_by_id(user_repository, sample_users):
    """Test retrieving a user by ID."""
    user = user_repository.get_by_id("1")
    assert user is not None
    assert user.id == "1"
    assert user.name == "John Doe"
    
    # Test non-existent ID
    user = user_repository.get_by_id("99")
    assert user is None


def test_get_by_email(user_repository, sample_users):
    """Test retrieving a user by email."""
    user = user_repository.get_by_email("john@example.com")
    assert user is not None
    assert user.id == "1"
    assert user.name == "John Doe"
    
    # Case insensitive email lookup
    user = user_repository.get_by_email("JANE@example.com")
    assert user is not None
    assert user.id == "2"
    
    # Test non-existent email
    user = user_repository.get_by_email("nonexistent@example.com")
    assert user is None


def test_create_user(user_repository):
    """Test creating a user."""
    user = User(id="4", name="Bob Brown", email="bob@example.com")
    created_user = user_repository.create(user)
    
    assert created_user.id == "4"
    assert created_user.name == "Bob Brown"
    
    # Verify user was actually stored
    retrieved_user = user_repository.get_by_id("4")
    assert retrieved_user is not None
    assert retrieved_user.id == "4"


def test_update_user(user_repository, sample_users):
    """Test updating a user."""
    # Update name
    updated_user = user_repository.update(user_id="1", name="John Doe Jr.")
    assert updated_user is not None
    assert updated_user.name == "John Doe Jr."
    assert updated_user.email == "john@example.com"  # Email should remain unchanged
    
    # Update email
    updated_user = user_repository.update(user_id="2", email="jane.smith@example.com")
    assert updated_user is not None
    assert updated_user.name == "Jane Smith"  # Name should remain unchanged
    assert updated_user.email == "jane.smith@example.com"
    
    # Update both fields
    updated_user = user_repository.update(user_id="3", name="Alice Brown", email="alice.brown@example.com")
    assert updated_user is not None
    assert updated_user.name == "Alice Brown"
    assert updated_user.email == "alice.brown@example.com"
    
    # Verify changes were stored
    retrieved_user = user_repository.get_by_id("3")
    assert retrieved_user.name == "Alice Brown"
    assert retrieved_user.email == "alice.brown@example.com"
    
    # Update non-existent user
    updated_user = user_repository.update(user_id="99", name="Nonexistent")
    assert updated_user is None


def test_delete_user(user_repository, sample_users):
    """Test deleting a user."""
    # Delete existing user
    result = user_repository.delete("1")
    assert result is True
    
    # Verify user was deleted
    user = user_repository.get_by_id("1")
    assert user is None
    
    # Delete non-existent user
    result = user_repository.delete("99")
    assert result is False