"""User model definition."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model representing a user in the system."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            uuid.UUID: lambda id: str(id)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from a dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    def update(self, name: Optional[str] = None, email: Optional[str] = None) -> None:
        """Update user fields and set updated_at to current time."""
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        self.updated_at = datetime.utcnow()