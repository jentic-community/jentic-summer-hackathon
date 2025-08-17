# MCP Agent

Minimal scaffold for local MCP-enabled agent components.

## Prerequisites
- Python 3.11+
- Optional: virtualenv or uv

## Setup (placeholder)
1) Create and activate a virtual environment
2) Install dependencies (to be added)
3) Configure settings in `configs/config.yaml` and `configs/mcp_servers.yaml`

## Development (placeholder)
- Format: black .
- Lint: ruff check .
- Sort imports: isort .
- Tests: pytest -q

## Install (editable)
```
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Run (placeholder)
- Filesystem Server:
```
uvicorn servers.filesystem_server:app --host 0.0.0.0 --port 8001
```
- System Server:
```
uvicorn servers.system_server:app --host 0.0.0.0 --port 8002
```
- Browser Server (requires Playwright):
```
pip install -e .[browser]
python -m playwright install --with-deps chromium
uvicorn servers.browser_server:app --host 0.0.0.0 --port 8003
```
- Client UI (Streamlit):
```
pip install streamlit pandas pyyaml
streamlit run client/streamlit_app.py
```

### Endpoint configuration
Endpoints are discovered from `configs/mcp_servers.yaml` when present, with env overrides:
- FS_SERVER_ENDPOINT (default http://localhost:8001/tool/filesystem_op)
- SYSTEM_SERVER_ENDPOINT (default http://localhost:8002/tool/system_exec)
- BROWSER_SERVER_ENDPOINT (default http://localhost:8003/tool/browser_op)

Example:
```
export FS_SERVER_ENDPOINT=http://127.0.0.1:8001/tool/filesystem_op
```

## Natural Language → MCP command planning

This project can turn a natural-language query into a sequence of MCP tool calls using OpenAI.

1. Set your API key in the environment (or configs/config.yaml):

```bash
export OPENAI_API_KEY=sk-...  # your key
```

2. Run the CLI with a natural-language query:

```bash
python -m client.cli --nl "list the current folder and then say hello"
```

Add `--print-plan` to print only the JSON plan without executing.

Config in `configs/config.yaml`:

```yaml
openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-3.5-turbo
  temperature: 0.0
```

In Streamlit, the logs panel shows how NL was converted into concrete tool calls (plan and results) when using the CLI or future UI wiring.

## Structure
- configs/: runtime and server configuration
- servers/: MCP servers (filesystem, system, browser) and shared stubs
- client/: UI/orchestration placeholders
- artifacts/: outputs like screenshots, CSVs
- tests/: reserved for tests (currently empty)
- docker/: container scaffolding

## Notes
- This scaffold contains no business logic yet.
- Pytest is configured to collect tests from `tests/`; currently there are none.
- Fill TODOs incrementally and keep security in mind.
