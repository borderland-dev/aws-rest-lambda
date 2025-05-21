"""Main Lambda handler for the Users API."""
import json
from typing import Dict, Any, Optional, Tuple, Union, List

from flask import Flask, jsonify, request
from mangum import Mangum
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.exceptions import NotFoundError, BadRequestError, InternalServerError

from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.utils.validation import validate_model, CreateUserRequest, UpdateUserRequest, ValidationException

# Initialize AWS Lambda Powertools
logger = Logger(service="users-api")
tracer = Tracer(service="users-api")
metrics = Metrics(namespace="UsersAPI")

# Initialize the API
app = APIGatewayRestResolver()

# Initialize services
user_repository = UserRepository()
user_service = UserService(user_repository)


def format_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a successful API response.
    
    Args:
        data: The data to include in the response
        
    Returns:
        Formatted API response
    """
    return {
        "status": "success",
        "data": data
    }


def format_error_response(message: str, error_code: str, errors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format an error API response.
    
    Args:
        message: Error message
        error_code: Error code
        errors: Optional detailed errors
        
    Returns:
        Formatted error response
    """
    response = {
        "status": "error",
        "message": message,
        "error_code": error_code
    }
    
    if errors:
        response["errors"] = errors
    
    return response


@app.get("/api/v1/users")
@tracer.capture_method
def list_users():
    """
    List users with pagination and optional search.
    """
    try:
        # Extract query parameters
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        search = request.args.get("search")
        
        # Validate page and limit
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Get users from service
        users, pagination = user_service.get_users(page, limit, search)
        
        # Log the request
        logger.info("Retrieved users", extra={"page": page, "limit": limit, "search": search})
        metrics.add_metric(name="ListUsersRequests", unit="Count", value=1)
        
        return format_success_response({"users": users, "pagination": pagination})
    
    except Exception as e:
        # Log the error
        logger.exception("Failed to retrieve users")
        metrics.add_metric(name="ListUsersErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Failed to retrieve users",
            error_code="INTERNAL_ERROR"
        ), 500


@app.post("/api/v1/users")
@tracer.capture_method
def create_user():
    """
    Create a new user.
    """
    try:
        # Validate request body
        payload = request.json
        validated_data = validate_model(CreateUserRequest, payload)
        
        # Create user
        user = user_service.create_user(
            name=validated_data.name,
            email=validated_data.email
        )
        
        # Log the creation
        logger.info("User created", extra={"user_id": user["id"]})
        metrics.add_metric(name="CreateUserRequests", unit="Count", value=1)
        
        return format_success_response({"user": user}), 201
    
    except ValidationException as e:
        # Log validation error
        logger.warning("Validation error", extra={"errors": e.errors})
        metrics.add_metric(name="CreateUserValidationErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Invalid request parameters",
            error_code="VALIDATION_ERROR",
            errors=e.errors
        ), 400
    
    except Exception as e:
        # Log unexpected error
        logger.exception("Failed to create user")
        metrics.add_metric(name="CreateUserErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Failed to create user",
            error_code="INTERNAL_ERROR"
        ), 500


@app.get("/api/v1/users/<user_id>")
@tracer.capture_method
def get_user(user_id: str):
    """
    Get a user by ID.
    """
    try:
        # Get user
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            # Log not found
            logger.warning("User not found", extra={"user_id": user_id})
            metrics.add_metric(name="GetUserNotFound", unit="Count", value=1)
            
            return format_error_response(
                message="User not found",
                error_code="RESOURCE_NOT_FOUND"
            ), 404
        
        # Log success
        logger.info("User retrieved", extra={"user_id": user_id})
        metrics.add_metric(name="GetUserRequests", unit="Count", value=1)
        
        return format_success_response({"user": user})
    
    except Exception as e:
        # Log error
        logger.exception("Failed to retrieve user", extra={"user_id": user_id})
        metrics.add_metric(name="GetUserErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Failed to retrieve user",
            error_code="INTERNAL_ERROR"
        ), 500


@app.put("/api/v1/users/<user_id>")
@tracer.capture_method
def update_user(user_id: str):
    """
    Update an existing user.
    """
    try:
        # Validate request body
        payload = request.json
        validated_data = validate_model(UpdateUserRequest, payload)
        
        # Update user
        user = user_service.update_user(
            user_id=user_id,
            name=validated_data.name,
            email=validated_data.email
        )
        
        if not user:
            # Log not found
            logger.warning("User not found for update", extra={"user_id": user_id})
            metrics.add_metric(name="UpdateUserNotFound", unit="Count", value=1)
            
            return format_error_response(
                message="User not found",
                error_code="RESOURCE_NOT_FOUND"
            ), 404
        
        # Log success
        logger.info("User updated", extra={"user_id": user_id})
        metrics.add_metric(name="UpdateUserRequests", unit="Count", value=1)
        
        return format_success_response({"user": user})
    
    except ValidationException as e:
        # Log validation error
        logger.warning("Validation error on update", extra={"user_id": user_id, "errors": e.errors})
        metrics.add_metric(name="UpdateUserValidationErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Invalid request parameters",
            error_code="VALIDATION_ERROR",
            errors=e.errors
        ), 400
    
    except Exception as e:
        # Log unexpected error
        logger.exception("Failed to update user", extra={"user_id": user_id})
        metrics.add_metric(name="UpdateUserErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Failed to update user",
            error_code="INTERNAL_ERROR"
        ), 500


@app.delete("/api/v1/users/<user_id>")
@tracer.capture_method
def delete_user(user_id: str):
    """
    Delete a user.
    """
    try:
        # Delete user
        deleted = user_service.delete_user(user_id)
        
        if not deleted:
            # Log not found
            logger.warning("User not found for deletion", extra={"user_id": user_id})
            metrics.add_metric(name="DeleteUserNotFound", unit="Count", value=1)
            
            return format_error_response(
                message="User not found",
                error_code="RESOURCE_NOT_FOUND"
            ), 404
        
        # Log success
        logger.info("User deleted", extra={"user_id": user_id})
        metrics.add_metric(name="DeleteUserRequests", unit="Count", value=1)
        
        # Return 204 No Content
        return "", 204
    
    except Exception as e:
        # Log error
        logger.exception("Failed to delete user", extra={"user_id": user_id})
        metrics.add_metric(name="DeleteUserErrors", unit="Count", value=1)
        
        return format_error_response(
            message="Failed to delete user",
            error_code="INTERNAL_ERROR"
        ), 500


# Create Flask app for local development and Mangum handler for Lambda
flask_app = Flask(__name__)

@flask_app.route("/api/v1/users", methods=["GET"])
def flask_list_users():
    return list_users()

@flask_app.route("/api/v1/users", methods=["POST"])
def flask_create_user():
    return create_user()

@flask_app.route("/api/v1/users/<user_id>", methods=["GET"])
def flask_get_user(user_id):
    return get_user(user_id)

@flask_app.route("/api/v1/users/<user_id>", methods=["PUT"])
def flask_update_user(user_id):
    return update_user(user_id)

@flask_app.route("/api/v1/users/<user_id>", methods=["DELETE"])
def flask_delete_user(user_id):
    return delete_user(user_id)


# Lambda handler
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    """AWS Lambda handler."""
    try:
        # Use Mangum to convert API Gateway events to ASGI
        return Mangum(app, lifespan="off")(event, context)
    except Exception as e:
        logger.exception("Unhandled exception")
        metrics.add_metric(name="UnhandledExceptions", unit="Count", value=1)
        
        return {
            "statusCode": 500,
            "body": json.dumps(format_error_response(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            ))
        }


# Local development entry point
if __name__ == "__main__":
    flask_app.run(debug=True)