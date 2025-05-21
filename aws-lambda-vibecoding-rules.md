# AWS Lambda Python Vibecoding Rules

## General Best Practices

1. **Single Responsibility**: Each Lambda function should do one thing well
2. **Stateless Design**: Never rely on the state of the execution environment between invocations
3. **Minimize Cold Starts**: Keep dependencies minimal and code efficient
4. **Error Handling**: Use proper try/except blocks to gracefully handle errors
5. **Input Validation**: Always validate incoming events/requests
6. **Utilize Layer**: Use AWS Lambda Layers for shared dependencies
7. **Environment Variables**: Store configuration in environment variables, not in code
8. **Keep Functions Small**: Aim for less than 1000 lines of code per function

## Python Code Style

1. **Follow PEP 8**: Adhere to Python's style guide
2. **Type Hints**: Use type annotations for better IDE support and documentation
3. **Docstrings**: Document functions with clear docstrings (Google or NumPy style)
4. **Linting**: Use tools like flake8, pylint, or black to maintain code quality
5. **Imports Organization**: Organize imports in groups (standard library, third-party, local)
6. **Constants**: Define constants at the top level in UPPERCASE
7. **Function Length**: Limit functions to 30-50 lines for better readability
8. **Naming Conventions**:
   - Functions: `lowercase_with_underscores()`
   - Classes: `PascalCase`
   - Constants: `UPPERCASE_WITH_UNDERSCORES`
   - Variables: `lowercase_with_underscores`

## REST API Best Practices

1. **API Gateway Integration**: Use API Gateway with Lambda for RESTful endpoints
2. **Resource-Based Paths**: Design URL paths around resources (nouns, not verbs)
3. **HTTP Methods**: Use appropriate HTTP methods (GET, POST, PUT, DELETE, etc.)
4. **Status Codes**: Return appropriate status codes (200, 201, 400, 404, 500, etc.)
5. **Response Format**: Consistently return JSON with a standard structure
6. **Pagination**: Implement pagination for resources with many items
7. **Filter and Sort**: Support filtering and sorting via query parameters
8. **Versioning**: Version your API (e.g., `/v1/resource`)
9. **Input Validation**: Validate request bodies, headers, and query parameters
10. **CORS**: Configure CORS properly for web clients

## AWS Lambda PowerTools

1. **Use AWS Lambda PowerTools**: Leverage the official library for logging, tracing, and metrics
2. **Structured Logging**: Use the Logger utility for consistent JSON-formatted logs
   ```python
   from aws_lambda_powertools import Logger
   logger = Logger(service="my-service")
   ```
3. **Tracing**: Implement X-Ray tracing with the Tracer utility
   ```python
   from aws_lambda_powertools import Tracer
   tracer = Tracer(service="my-service")
   ```
4. **Metrics**: Use the Metrics utility to collect custom metrics
   ```python
   from aws_lambda_powertools import Metrics
   metrics = Metrics(namespace="MyService")
   ```
5. **Event Handling**: Use the event parsing utilities for SQS, SNS, API Gateway, etc.
6. **Middleware Pattern**: Apply decorators for logging, tracing, and metrics
   ```python
   @logger.inject_lambda_context
   @tracer.capture_lambda_handler
   @metrics.log_metrics
   def handler(event, context):
       # Your code here
   ```
7. **Parameter Store**: Use the parameter utility to fetch config from SSM
8. **Batch Processing**: Use batch-processing utility for SQS batch handling

## Datadog Integration

1. **Datadog Lambda Library**: Include the Datadog Lambda Library in your deployment package
   ```
   pip install datadog-lambda
   ```
2. **Wrap Lambda Handler**: Use the decorator to enable tracing
   ```python
   from datadog_lambda.wrapper import datadog_lambda_wrapper
   
   @datadog_lambda_wrapper
   def handler(event, context):
       # Your code here
   ```
3. **Custom Metrics**: Send custom metrics to Datadog
   ```python
   from datadog_lambda.metric import lambda_metric
   
   lambda_metric(
       metric_name="api.requests",
       value=1,
       tags=["endpoint:/users", "method:GET"]
   )
   ```
4. **Log Correlation**: Enable log correlation with traces
   ```python
   from datadog_lambda.wrapper import datadog_lambda_wrapper
   import logging
   
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)
   
   @datadog_lambda_wrapper
   def handler(event, context):
       logger.info("This log will be correlated with traces")
   ```
5. **Custom Spans**: Create custom spans for specific operations
   ```python
   from ddtrace import tracer
   
   @tracer.wrap(service="my-lambda", resource="database-query")
   def database_operation():
       # Perform database operation
   ```
6. **Environment Tagging**: Tag all metrics with environment info
7. **Monitoring Dashboard**: Create dedicated dashboards for Lambda functions
8. **Alerts**: Set up appropriate alerts for errors, latency, and cold starts
9. **APM Integration**: Configure full APM integration for distributed tracing

## Project Structure

1. **Recommended Structure**:
   ```
   my-lambda-function/
   ├── src/
   │   ├── __init__.py
   │   ├── app.py           # Main lambda handler
   │   ├── models/          # Data models
   │   ├── services/        # Business logic
   │   ├── repositories/    # Data access
   │   └── utils/           # Helper functions
   ├── tests/
   │   ├── __init__.py
   │   ├── unit/
   │   └── integration/
   ├── requirements.txt
   ├── requirements-dev.txt
   ├── README.md
   ├── template.yaml        # SAM/CloudFormation template
   └── Makefile             # Build and deployment commands
   ```
2. **Separation of Concerns**: Keep handler, business logic, and data access separate
3. **Event Schemas**: Define schemas for events and responses

## Testing

1. **Unit Tests**: Write tests for all business logic
2. **Integration Tests**: Test the Lambda function with real AWS services
3. **Mocking**: Use moto or other tools to mock AWS services locally
4. **Test Coverage**: Aim for at least 80% code coverage
5. **Local Testing**: Use AWS SAM CLI for local testing

## CI/CD

1. **Infrastructure as Code**: Use AWS SAM, Serverless Framework, or CDK
2. **Automated Tests**: Run tests in CI pipeline
3. **Linting**: Include code quality checks
4. **Multiple Environments**: Deploy to dev/staging/prod
5. **Canary Deployments**: Use gradual traffic shifting for production

## Security

1. **IAM Roles**: Use the principle of least privilege
2. **Secret Management**: Use AWS Secrets Manager or Parameter Store
3. **Input Validation**: Validate and sanitize all inputs
4. **Dependency Scanning**: Regularly scan for vulnerable dependencies
5. **Encryption**: Encrypt data at rest and in transit
