"""Business logic for user operations."""
from typing import Dict, List, Optional, Any, Tuple

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.utils.validation import ValidationException


class UserService:
    """Service for handling user-related operations."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize the service with a user repository."""
        self.user_repository = user_repository
    
    def get_users(self, page: int = 1, limit: int = 10, search: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get a paginated list of users with optional search.
        
        Args:
            page: Page number (default: 1)
            limit: Items per page (default: 10)
            search: Optional search term
            
        Returns:
            Tuple of (users list, pagination data)
        """
        users, pagination = self.user_repository.get_all(page, limit, search)
        return [user.to_dict() for user in users], pagination
    
    def create_user(self, name: str, email: str) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            name: User's full name
            email: User's email
            
        Returns:
            Created user data
            
        Raises:
            ValidationException: If email is already in use
        """
        # Check if email is already in use
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValidationException({"email": "Email is already in use"})
        
        user = User(name=name, email=email)
        created_user = self.user_repository.create(user)
        return created_user.to_dict()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User data if found, None otherwise
        """
        user = self.user_repository.get_by_id(user_id)
        return user.to_dict() if user else None
    
    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a user.
        
        Args:
            user_id: The user's ID
            name: New name (optional)
            email: New email (optional)
            
        Returns:
            Updated user data if found, None otherwise
            
        Raises:
            ValidationException: If email is already in use by another user
        """
        # Check if email is already in use by another user
        if email:
            existing_user = self.user_repository.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValidationException({"email": "Email is already in use"})
        
        updated_user = self.user_repository.update(user_id, name, email)
        return updated_user.to_dict() if updated_user else None
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.user_repository.delete(user_id)