.PHONY: install test lint format deploy local-api clean

# Default Python interpreter
PYTHON := python

# Virtual environment
VENV := venv
VENV_ACTIVATE := $(VENV)/Scripts/activate

# Package and distribution directories
DIST_DIR := dist
BUILD_DIR := build

# App-specific configuration
STACK_NAME := users-api
REGION := us-east-1
PROFILE := default

install:
	pip install -r requirements.txt

clean:
	rm -rf $(VENV) $(DIST_DIR) $(BUILD_DIR) *.egg-info .pytest_cache __pycache__ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name *.egg-info -exec rm -rf {} +

test:
	pytest -xvs tests/

lint:
	flake8 src/ tests/
	pylint src/ tests/
	mypy src/ tests/

format:
	black src/ tests/
	isort src/ tests/

sam-build:
	sam build --use-container

sam-package:
	sam package --output-template-file packaged.yaml --s3-bucket $(BUCKET_NAME)

sam-deploy:
	sam deploy --template-file packaged.yaml --stack-name $(STACK_NAME) --capabilities CAPABILITY_IAM --region $(REGION) --profile $(PROFILE)

local-api:
	python -m src.app