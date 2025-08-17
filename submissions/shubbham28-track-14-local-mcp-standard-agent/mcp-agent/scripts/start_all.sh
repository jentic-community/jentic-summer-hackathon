#!/usr/bin/env bash
set -euo pipefail

# Start Filesystem, System, Browser servers and Streamlit client
# Uses background processes and waits for readiness.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Defaults (can be overridden)
export FS_PORT="${FS_PORT:-8001}"
export SYS_PORT="${SYS_PORT:-8002}"
export BR_PORT="${BR_PORT:-8003}"
export STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

# Background start functions
start_fs() {
  echo "Starting filesystem server on :$FS_PORT" >&2
  uvicorn servers.filesystem_server:app --host 0.0.0.0 --port "$FS_PORT" &
}

start_sys() {
  echo "Starting system server on :$SYS_PORT" >&2
  uvicorn servers.system_server:app --host 0.0.0.0 --port "$SYS_PORT" &
}

start_browser() {
  echo "Starting browser server on :$BR_PORT" >&2
  uvicorn servers.browser_server:app --host 0.0.0.0 --port "$BR_PORT" &
}

start_client() {
  echo "Starting Streamlit client on :$STREAMLIT_PORT" >&2
  STREAMLIT_SERVER_PORT="$STREAMLIT_PORT" streamlit run client/streamlit_app.py --server.address 0.0.0.0 &
}

# Wait for a port to be ready using bash /dev/tcp (no nc dependency)
wait_port() {
  local port="$1"; local retries="${2:-50}"; local delay="${3:-0.2}"; local host="localhost"
  for i in $(seq 1 "$retries"); do
    if (echo > "/dev/tcp/${host}/${port}") >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

start_fs
start_sys
start_browser

# Wait for servers
wait_port "$FS_PORT" || echo "filesystem not detected yet"
wait_port "$SYS_PORT" || echo "system not detected yet"
wait_port "$BR_PORT" || echo "browser not detected yet"

# Configure client endpoints via env for inside-container access
export FS_SERVER_ENDPOINT="http://localhost:${FS_PORT}/tool/filesystem_op"
export SYSTEM_SERVER_ENDPOINT="http://localhost:${SYS_PORT}/tool/system_exec"
export BROWSER_SERVER_ENDPOINT="http://localhost:${BR_PORT}/tool/browser_op"

start_client

# Wait forever while background jobs run
wait -n || true
while true; do sleep 3600; done
