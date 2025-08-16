.PHONY: setup install test clean validate-examples demo help

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

# Create test specification examples
create-test-specs:
	@echo "📁 Creating test specification directories..."
	mkdir -p test-specs/valid/
	mkdir -p test-specs/invalid/
	mkdir -p test-specs/edge-cases/
	mkdir -p test-specs/real-world/
	@echo "✅ Test directories created"
	@echo ""
	@echo "💡 Now create OpenAPI specs in each directory:"
	@echo "  - test-specs/valid/ - Correct specifications"
	@echo "  - test-specs/invalid/ - Specifications with errors"
	@echo "  - test-specs/edge-cases/ - Boundary conditions"
	@echo "  - test-specs/real-world/ - Complex real examples"

# Test the validator implementation
test:
	@echo "🧪 Running validator tests..."
	pytest tests/ -v

# Test with coverage
test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=validator --cov-report=html --cov-report=term

# Validate example specifications
validate-examples:
	@echo "🔍 Validating example specifications..."
	@echo "Testing valid specs (should pass):"
	@for file in test-specs/valid/*.yaml test-specs/valid/*.json; do \
		if [ -f "$$file" ]; then \
			echo "  Validating $$file..."; \
			python validator.py "$$file" || echo "  ❌ Unexpected failure"; \
		fi \
	done
	@echo ""
	@echo "Testing invalid specs (should fail):"
	@for file in test-specs/invalid/*.yaml test-specs/invalid/*.json; do \
		if [ -f "$$file" ]; then \
			echo "  Validating $$file..."; \
			python validator.py "$$file" && echo "  ❌ Should have failed" || echo "  ✅ Failed as expected"; \
		fi \
	done

# Run demo with different validation levels
demo:
	@echo "🚀 Running validator demo..."
	@echo "Creating a simple test spec..."
	@echo 'openapi: 3.0.0\ninfo:\n  title: Demo API\n  version: 1.0.0\npaths: {}' > demo-spec.yaml
	@echo ""
	@echo "1. Basic syntax validation:"
	python validator.py demo-spec.yaml --level syntax
	@echo ""
	@echo "2. Semantic validation:"
	python validator.py demo-spec.yaml --level semantic
	@echo ""
	@echo "3. Agent-ready validation:"
	python validator.py demo-spec.yaml --level agent-ready
	@echo ""
	@echo "4. JSON output format:"
	python validator.py demo-spec.yaml --format json
	@rm demo-spec.yaml

# Lint and format code
lint:
	@echo "🔍 Linting code..."
	flake8 validator/ tests/ --max-line-length=100
	mypy validator/ --ignore-missing-imports

format:
	@echo "✨ Formatting code..."
	black validator/ tests/
	isort validator/ tests/

# Test with real-world specifications
test-real-world:
	@echo "🌐 Testing with real-world OpenAPI specifications..."
	@echo "Testing GitHub API..."
	python validator.py https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml --level syntax
	@echo ""
	@echo "💡 Add more real-world API tests as you build your validator"

# Create example specifications for testing
create-examples:
	@echo "📝 Creating example specifications..."
	
	# Valid example
	@echo 'openapi: 3.0.0\ninfo:\n  title: Valid API\n  version: 1.0.0\n  description: A properly formed API specification\nservers:\n  - url: https://api.example.com\npaths:\n  /users:\n    get:\n      operationId: getUsers\n      summary: List users\n      responses:\n        "200":\n          description: List of users\n          content:\n            application/json:\n              schema:\n                type: array\n                items:\n                  type: object' > test-specs/valid/simple-valid.yaml
	
	# Invalid example - missing required fields
	@echo 'openapi: 3.0.0\ninfo:\n  title: Invalid API\n  # Missing version field\npaths: {}' > test-specs/invalid/missing-version.yaml
	
	# Invalid example - wrong OpenAPI version
	@echo 'openapi: 2.0\ninfo:\n  title: Old API\n  version: 1.0.0\npaths: {}' > test-specs/invalid/old-version.yaml
	
	@echo "✅ Example specifications created"

# Performance testing
test-performance:
	@echo "⚡ Running performance tests..."
	@echo "Testing with large specification..."
	# TODO: Add performance testing commands
	@echo "💡 Implement performance tests for large OpenAPI specs"

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf *.egg-info/
	rm -f demo-spec.yaml

# Generate documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "💡 TODO: Add documentation generation"
	@echo "Consider using Sphinx or mkdocs for documentation"

# Package for distribution
package:
	@echo "📦 Packaging validator..."
	python setup.py sdist bdist_wheel
	@echo "✅ Package created in dist/"

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install black flake8 mypy isort pytest-cov
	pip install build twine  # For packaging

# Validate validator implementation
validate-validator:
	@echo "🔍 Validating the validator implementation..."
	@echo "Checking required files exist..."
	@[ -f validator.py ] && echo "✅ validator.py exists" || echo "❌ validator.py missing"
	@[ -f validator/__init__.py ] && echo "✅ validator package exists" || echo "❌ validator package missing"
	@[ -d tests/ ] && echo "✅ tests directory exists" || echo "❌ tests directory missing"
	@echo ""
	@echo "Testing basic imports..."
	@python -c "import validator; print('✅ Validator imports successfully')" 2>/dev/null || echo "❌ Validator import failed"

# Help
help:
	@echo "Available commands:"
	@echo "  make setup              - Create virtual environment"
	@echo "  make install            - Install dependencies"
	@echo "  make create-test-specs  - Create test directories"
	@echo "  make create-examples    - Create example specifications"
	@echo "  make test              - Run tests"
	@echo "  make test-coverage     - Run tests with coverage"
	@echo "  make validate-examples - Test validator on examples"
	@echo "  make demo              - Run validation demo"
	@echo "  make lint              - Check code style"
	@echo "  make format            - Format code"
	@echo "  make test-real-world   - Test with real API specs"
	@echo "  make clean             - Remove generated files"
	@echo "  make validate-validator- Check validator implementation"