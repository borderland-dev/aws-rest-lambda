"""Utilities for validating input data."""
from typing import Dict, Any, Optional, List, TypeVar, Type, cast
from pydantic import BaseModel, ValidationError


T = TypeVar('T', bound=BaseModel)


class ValidationException(Exception):
    """Exception raised when validation fails."""
    
    def __init__(self, errors: Dict[str, Any]):
        """Initialize the exception with validation errors."""
        self.errors = errors
        super().__init__("Validation error")


def validate_model(model_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Validate input data against a Pydantic model.
    
    Args:
        model_class: The Pydantic model class to validate against
        data: The input data to validate
        
    Returns:
        A validated instance of the model
        
    Raises:
        ValidationException: If validation fails
    """
    try:
        return model_class(**data)
    except ValidationError as e:
        # Transform Pydantic validation errors into our API format
        error_dict: Dict[str, List[str]] = {}
        for error in e.errors():
            field = error["loc"][0] if error["loc"] else "general"
            if isinstance(field, int):
                field = f"item_{field}"
            
            if field not in error_dict:
                error_dict[field] = []
            
            error_dict[field].append(error["msg"])
        
        raise ValidationException(error_dict)


class CreateUserRequest(BaseModel):
    """Schema for creating a user."""
    
    name: str
    email: str


class UpdateUserRequest(BaseModel):
    """Schema for updating a user."""
    
    name: Optional[str] = None
    email: Optional[str] = None