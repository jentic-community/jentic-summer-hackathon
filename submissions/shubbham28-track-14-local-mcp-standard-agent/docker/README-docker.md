# Docker: Unified MCP servers + Streamlit client

## Build

```bash
docker build -t local-mcp-agent -f docker/Dockerfile .
```

## Run

```bash
docker run --rm -it \
  -p 8501:8501 -p 8001:8001 -p 8002:8002 -p 8003:8003 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  local-mcp-agent
```

- Streamlit UI: http://localhost:8501
- Filesystem server: http://localhost:8001/tool/filesystem_op
- System server: http://localhost:8002/tool/system_exec
- Browser server: http://localhost:8003/tool/browser_op

## Notes
- Uses Playwright base image with Chromium preinstalled.
- You can override ports via env vars FS_PORT, SYS_PORT, BR_PORT, STREAMLIT_PORT.
- Mount a volume to persist `artifacts/` if desired:

```bash
docker run --rm -it \
  -v "$(pwd)/mcp-agent/artifacts:/app/mcp-agent/artifacts" \
  -p 8501:8501 -p 8001:8001 -p 8002:8002 -p 8003:8003 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  local-mcp-agent
```
