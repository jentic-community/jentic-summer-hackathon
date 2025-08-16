.PHONY: help setup test validate clean demo

help:
	@echo "Arazzo Runner Basics - Track 03"
	@echo ""
	@echo "Available commands:"
	@echo "  setup      - Install dependencies and configure environment"
	@echo "  test       - Test all workflows in the project"
	@echo "  validate   - Validate workflow syntax and structure"
	@echo "  demo       - Run demonstration workflows"
	@echo "  clean      - Clean up temporary files and environments"
	@echo ""
	@echo "Individual workflow commands:"
	@echo "  make run WORKFLOW=01-hello-world.arazzo.yaml ID=helloWorld"
	@echo "  make debug WORKFLOW=workflow.arazzo.yaml"

setup:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Environment setup complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "  1. Copy .env.example to .env"
	@echo "  2. Add your API credentials to .env"
	@echo "  3. Run 'make demo' to test basic workflows"

test:
	@echo "🧪 Testing all workflows..."
	@for workflow in workflows/*.arazzo.yaml; do \
		echo "Testing $$workflow..."; \
		.venv/bin/arazzo-runner list-workflows "$$workflow" || exit 1; \
	done
	@echo "✅ All workflow files are valid!"

validate:
	@echo "🔍 Validating workflow syntax..."
	@for workflow in workflows/*.arazzo.yaml; do \
		echo "Validating $$workflow..."; \
		python -c "import yaml; yaml.safe_load(open('$$workflow'))" || exit 1; \
	done
	@echo "✅ All workflows have valid syntax!"

demo:
	@echo "🎬 Running demonstration workflows..."
	@echo "1. Hello World workflow..."
	.venv/bin/arazzo-runner execute-workflow workflows/01-hello-world.arazzo.yaml --workflow-id helloWorld
	@echo ""
	@echo "2. Basic parameterized workflow..."
	.venv/bin/arazzo-runner execute-workflow workflows/02-parameterized.arazzo.yaml --workflow-id searchAndTranslate --inputs '{"search_query": "artificial intelligence"}'
	@echo "✅ Demo complete!"

run:
	@if [ -z "$(WORKFLOW)" ] || [ -z "$(ID)" ]; then \
		echo "❌ Usage: make run WORKFLOW=file.arazzo.yaml ID=workflowId"; \
		echo "   Example: make run WORKFLOW=01-hello-world.arazzo.yaml ID=helloWorld"; \
		exit 1; \
	fi
	.venv/bin/arazzo-runner execute-workflow workflows/$(WORKFLOW) --workflow-id $(ID) $(ARGS)

debug:
	@if [ -z "$(WORKFLOW)" ]; then \
		echo "❌ Usage: make debug WORKFLOW=file.arazzo.yaml"; \
		exit 1; \
	fi
	@echo "🐛 Debugging workflow: $(WORKFLOW)"
	.venv/bin/arazzo-runner --log-level DEBUG list-workflows workflows/$(WORKFLOW)
	.venv/bin/arazzo-runner show-env-mappings workflows/$(WORKFLOW)

clean:
	rm -rf .venv
	rm -f *.log
	rm -f workflows/*.log
	@echo "🧹 Cleanup complete!"