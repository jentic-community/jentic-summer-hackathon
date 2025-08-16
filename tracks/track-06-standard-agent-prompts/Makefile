.PHONY: setup test clean verify run-example

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

# Verify setup is working
verify:
	@echo "🔍 Verifying setup..."
	python verify_setup.py

# Test all prompts
test:
	@echo "🧪 Testing prompts..."
	python test_all_prompts.py

# Run example prompt
run-example:
	@echo "🚀 Running example prompt..."
	python test_prompt.py "What's the weather in San Francisco?"

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -f test_results.json

# Generate performance report
report:
	@echo "📊 Generating performance report..."
	python prompt_performance_report.py

# Help
help:
	@echo "Available commands:"
	@echo "  make setup     - Create virtual environment"
	@echo "  make install   - Install dependencies"
	@echo "  make verify    - Check setup is working"
	@echo "  make test      - Test all prompts"
	@echo "  make run-example - Run example prompt"
	@echo "  make report    - Generate performance report"
	@echo "  make clean     - Remove temporary files"