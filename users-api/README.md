# Users API

A RESTful API for managing user data, implemented as an AWS Lambda function using Flask, AWS Lambda Powertools, and Mangum.

## Project Overview

This project implements a Users API as specified in the requirements. It's built as a serverless application using:

- **Flask**: Web framework for the API
- **AWS Lambda**: Serverless compute
- **AWS Lambda Powertools**: For structured logging, tracing, and metrics
- **Mangum**: Adapter for running Flask applications in AWS Lambda

The API follows RESTful principles and provides endpoints for creating, reading, updating, and deleting user records.

## Features

- Complete CRUD operations for user management
- Pagination for list endpoints
- Search functionality
- Input validation
- Error handling with consistent response formats
- Mock in-memory data store (for demonstration purposes)
- Integration with AWS Lambda Powertools for observability
- Local development support
- Comprehensive test suite

## Project Structure

```
users-api/
├── src/
│   ├── __init__.py
│   ├── app.py                  # Main Lambda handler and API routes
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   └── user.py             # User data model
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py     # User service layer
│   ├── repositories/           # Data access
│   │   ├── __init__.py
│   │   └── user_repository.py  # In-memory user repository
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       └── validation.py       # Input validation utilities
├── tests/
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── test_user_repository.py
│   │   └── test_user_service.py
│   └── integration/            # Integration tests
│       ├── __init__.py
│       └── test_api.py         # API endpoint tests
├── http-tests/                 # HTTP files for manual testing
│   └── users-api.http          # HTTP requests for VSCode REST Client
├── requirements.txt            # Dependencies
├── Makefile                    # Build and deployment commands
├── template.yaml               # SAM/CloudFormation template
└── README.md                   # Project documentation
```

## Prerequisites

- Python 3.9+
- AWS CLI (for deployment)
- AWS SAM CLI (for local testing and deployment)
- pip (Python package manager)

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Development

To run the API locally:

```bash
python -m src.app
```

Or use the Makefile:

```bash
make local-api
```

The API will be available at http://localhost:5000/api/v1/users

## Testing

### Running Tests

To run the complete test suite:

```bash
pytest -xvs tests/
```

Or use the Makefile:

```bash
make test
```

### Manual Testing

For manual testing, you can use the HTTP files in the `http-tests` directory with the REST Client extension in VS Code or a tool like Postman.

## API Endpoints

### List Users

```
GET /api/v1/users
```

Query Parameters:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Number of users per page (default: 10)
- `search` (optional): Search term to filter by name or email

### Create User

```
POST /api/v1/users
```

Request Body:
```json
{
  "name": "Alice Johnson",
  "email": "alice.johnson@example.com"
}
```

### Get User by ID

```
GET /api/v1/users/{id}
```

### Update User

```
PUT /api/v1/users/{id}
```

Request Body:
```json
{
  "name": "Alice Smith",
  "email": "alice.smith@example.com"
}
```

### Delete User

```
DELETE /api/v1/users/{id}
```

## Deployment

### Building the Lambda Package

```bash
make sam-build
```

### Package the Application

```bash
make sam-package
```

You'll need to specify an S3 bucket where the deployment package will be uploaded:

```bash
sam package --output-template-file packaged.yaml --s3-bucket YOUR_BUCKET_NAME
```

### Deploy to AWS

```bash
make sam-deploy
```

Or manually:

```bash
sam deploy --template-file packaged.yaml --stack-name users-api --capabilities CAPABILITY_IAM
```

## Environment Variables

The application uses the following environment variables:

- `LOG_LEVEL`: Set the logging level (default: INFO)
- `POWERTOOLS_SERVICE_NAME`: Service name for AWS Lambda Powertools (default: users-api)
- `POWERTOOLS_METRICS_NAMESPACE`: Metrics namespace (default: UsersAPI)

## License

This project is licensed under the MIT License - see the LICENSE file for details.