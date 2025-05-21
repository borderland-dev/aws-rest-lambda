"""User repository implementation with in-memory storage."""
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.models.user import User


class UserRepository:
    """In-memory implementation of a user repository."""
    
    def __init__(self):
        """Initialize the in-memory store."""
        self._users: Dict[str, User] = {}
    
    def get_all(self, 
                page: int = 1, 
                limit: int = 10, 
                search: Optional[str] = None) -> tuple[List[User], Dict[str, Any]]:
        """
        Retrieve all users with pagination and optional search.
        
        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            search: Optional search term to filter by name or email
            
        Returns:
            Tuple containing a list of users and pagination info
        """
        filtered_users = list(self._users.values())
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            filtered_users = [
                user for user in filtered_users
                if search_lower in user.name.lower() or search_lower in user.email.lower()
            ]
        
        # Calculate pagination
        total_users = len(filtered_users)
        total_pages = (total_users + limit - 1) // limit if total_users > 0 else 1
        page = max(1, min(page, total_pages))  # Ensure page is within bounds
        
        # Slice the results for the requested page
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paged_users = filtered_users[start_idx:end_idx]
        
        pagination = {
            "total": total_users,
            "page": page,
            "limit": limit,
            "pages": total_pages
        }
        
        return paged_users, pagination
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id: Unique identifier of the user
            
        Returns:
            User if found, None otherwise
        """
        return self._users.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.
        
        Args:
            email: Email address to search for
            
        Returns:
            User if found, None otherwise
        """
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User instance to create
            
        Returns:
            Created user
        """
        self._users[user.id] = user
        return user
    
    def update(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """
        Update an existing user.
        
        Args:
            user_id: ID of the user to update
            name: New name (if provided)
            email: New email (if provided)
            
        Returns:
            Updated user if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if user:
            user.update(name=name, email=email)
            return user
        return None
    
    def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: ID of the user to delete
            
        Returns:
            True if user was deleted, False otherwise
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False