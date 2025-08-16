.PHONY: setup install test clean demo validate examples help

# Setup development environment
setup:
	python -m venv .venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source .venv/bin/activate  # Linux/macOS"
	@echo "  .venv\\Scripts\\activate     # Windows"
	@echo ""
	@echo "Then run: make install"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Test with coverage
test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=scorecard --cov-report=html

# Run demo with example APIs
demo:
	@echo "🚀 Running scorecard demo..."
	python scorecard.py examples/simple-api.yaml
	@echo ""
	python scorecard.py examples/complex-api.yaml --detailed

# Validate scorecard logic
validate:
	@echo "🔍 Validating scorecard logic..."
	python validate_scoring.py

# Generate example reports
examples:
	@echo "📊 Generating example reports..."
	python scorecard.py examples/simple-api.yaml --output reports/simple-report.html
	python scorecard.py examples/complex-api.yaml --output reports/complex-report.html --detailed
	python scorecard.py examples/github-api.yaml --output reports/github-report.json --format json

# Batch test with all examples
batch-test:
	@echo "📦 Running batch tests..."
	python batch_test.py examples/

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf reports/*.html
	rm -rf reports/*.json
	rm -rf reports/*.md

# Lint code
lint:
	@echo "🔍 Linting code..."
	flake8 scorecard/ tests/ --max-line-length=100
	black --check scorecard/ tests/

# Format code
format:
	@echo "✨ Formatting code..."
	black scorecard/ tests/
	isort scorecard/ tests/

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install flake8 black isort pytest-cov

# Quick test with a real API
test-real:
	@echo "🌐 Testing with a real API spec..."
	python scorecard.py https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml --output test-real-api.html

# Help
help:
	@echo "Available commands:"
	@echo "  make setup       - Create virtual environment"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make demo        - Run demo with examples"
	@echo "  make validate    - Validate scorecard logic"
	@echo "  make examples    - Generate example reports"
	@echo "  make batch-test  - Test all example APIs"
	@echo "  make clean       - Remove generated files"
	@echo "  make lint        - Check code style"
	@echo "  make format      - Format code"
	@echo "  make test-real   - Test with real API spec"