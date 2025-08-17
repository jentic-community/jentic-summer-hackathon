# Track 14 – Local MCP Support in Standard Agent (Submission by @shubbham28)

This submission adds Local MCP support to a standard agent workflow with:
- Filesystem MCP (list/read/write/create/edit/delete/rename)
- System MCP (allowlisted exec, incl. running Python files/modules)
- Browser MCP (Playwright-based booking.com workflow + open_title)
- Streamlit client with Natural Language planning via OpenAI
- Unified Docker image that starts all servers + Streamlit

## Architecture
- servers/
  - filesystem_server.py (FastAPI)
  - system_server.py (FastAPI)
  - browser_server.py (FastAPI + Playwright)
  - shared/security.py (path sandboxing, exec allowlist, host allowlist)
- client/
  - streamlit_app.py (UI)
  - orchestrator.py (routing, config, workflows)
  - nl2cmd.py (OpenAI planner)
  - tools_schema.py (planner schema)
  - presenters.py (render helpers)
- configs/
  - mcp_servers.yaml (endpoints)
  - config.yaml (OpenAI config; uses `${OPENAI_API_KEY}`)
- scripts/
  - start_all.sh (start all servers + Streamlit)
  - test_booking.sh (curl-based debug for booking_search)
- docker/
  - Dockerfile (Playwright base + project + Streamlit)
  - README-docker.md

## Prerequisites
- Python 3.9+
- Playwright Chromium (installer handles it)
- OpenAI API key for NL planning (set `OPENAI_API_KEY`)

## Quickstart (Local)
```bash
# 1) Create venv
python -m venv .venv && source .venv/bin/activate

# 2) Install project (incl. browser extras)
pip install -e 'mcp-agent[browser]'
playwright install chromium

# 3) Configure OpenAI (optional; required for NL planning)
export OPENAI_API_KEY=sk-...

# 4) Start servers
uvicorn servers.filesystem_server:app --port 8001 &
uvicorn servers.system_server:app --port 8002 &
uvicorn servers.browser_server:app --port 8003 &

# 5) Start UI
streamlit run client/streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

Open http://localhost:8501

- Toggle “Use natural language planning (OpenAI)” to describe tasks in English.
- Or use direct commands like: `ls .`, `cat README.md`, `exec python script.py`, `booking Dublin 3`.

## Quickstart (Docker)
```bash
# From repo root
docker build -t local-mcp-agent -f docker/Dockerfile .

docker run --rm -it \
  -p 8501:8501 -p 8001:8001 -p 8002:8002 -p 8003:8003 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  local-mcp-agent
```

- UI: http://localhost:8501
- Filesystem: http://localhost:8001/tool/filesystem_op
- System: http://localhost:8002/tool/system_exec
- Browser: http://localhost:8003/tool/browser_op

Optional: persist artifacts
```bash
docker run --rm -it \
  -v "$(pwd)/mcp-agent/artifacts:/app/mcp-agent/artifacts" \
  -p 8501:8501 -p 8001:8001 -p 8002:8002 -p 8003:8003 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  local-mcp-agent
```

## Natural Language Planning
- Enable in the sidebar. Requires `OPENAI_API_KEY`.
- “Plan only” previews the steps without executing.
- The UI shows the plan first, then a progress bar and per-step results.

## Endpoints & Config
- Default endpoints: 8001/8002/8003. Overridables via env:
  - `FS_SERVER_ENDPOINT`, `SYSTEM_SERVER_ENDPOINT`, `BROWSER_SERVER_ENDPOINT`
- OpenAI config: `configs/config.yaml` uses `${OPENAI_API_KEY}` placeholder.

## Troubleshooting
- booking_search timeout:
  - Use `scripts/test_booking.sh` to debug curl timing and response.
  - Increase TIMEOUT: `TIMEOUT=180 ./scripts/test_booking.sh`
  - Check server logs for navigation/selector timeouts.
- zsh pip extras: always quote extras: `pip install -e 'mcp-agent[browser]'`.
- Missing Streamlit/pandas in Docker: already installed in the Dockerfile.

## Repo Links
- Main repo (suggested): https://github.com/shubbham28/track-14-local-mcp-standard-agent
- This submission folder: `submissions/shubbham28-track-14-local-mcp-standard-agent`

## License
MIT (or your preferred license).
