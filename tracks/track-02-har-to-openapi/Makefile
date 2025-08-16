.PHONY: help setup validate analyze clean

help:
	@echo "HAR to OpenAPI Conversion Toolkit"
	@echo ""
	@echo "Available commands:"
	@echo "  setup      - Set up Python environment and tools"
	@echo "  validate   - Validate OpenAPI specification"
	@echo "  analyze    - Analyze HAR file for API patterns"
	@echo "  clean      - Clean up generated files"
	@echo ""
	@echo "Usage examples:"
	@echo "  make analyze HAR=capture.har"
	@echo "  make validate SPEC=api-spec.yaml"

setup:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Environment setup complete!"

validate:
	@if [ -z "$(SPEC)" ]; then \
		echo "❌ Usage: make validate SPEC=your-spec.yaml"; \
		exit 1; \
	fi
	@echo "🧪 Validating OpenAPI specification: $(SPEC)"
	.venv/bin/python -c "
from openapi_spec_validator import validate_spec
import yaml
try:
    with open('$(SPEC)') as f:
        spec = yaml.safe_load(f)
    validate_spec(spec)
    print('✅ OpenAPI specification is valid!')
except Exception as e:
    print(f'❌ Validation failed: {e}')
    exit(1)
"

analyze:
	@if [ -z "$(HAR)" ]; then \
		echo "❌ Usage: make analyze HAR=your-file.har"; \
		exit 1; \
	fi
	@echo "🔍 Analyzing HAR file: $(HAR)"
	.venv/bin/python tools/har_analyzer.py $(HAR)

clean:
	rm -rf .venv
	rm -f *.log
	rm -f analysis-report.txt
	@echo "🧹 Cleanup complete"