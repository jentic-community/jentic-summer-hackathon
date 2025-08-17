import os
import time
import pytest  # type: ignore

from client.orchestrator import (
    load_client_config,
    fs_write,
    start_background_process,
    stop_background_process,
    health_check,
    system_exec,
)


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("SYSTEM_SERVER_ENDPOINT") is None or os.environ.get("FS_SERVER_ENDPOINT") is None,
    reason="Requires filesystem and system servers to be running",
)
def test_workflow_fastapi_health():
    cfg = load_client_config()

    # 1) Create FastAPI app files
    app_code = (
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/health')\n"
        "def health():\n"
        "    return {'status': 'ok'}\n"
    )
    fs_write("app/__init__.py", "", cfg)
    fs_write("app/main.py", app_code, cfg)

    # 2) Ensure deps present (idempotent)
    prep = system_exec("pip install -q fastapi uvicorn httpx pytest", timeout_sec=180, cfg=cfg)
    assert prep.get("ok"), f"pip install failed: {prep}"

    # 3) Start uvicorn in background
    handle = start_background_process("uvicorn app.main:app --port 8000 --log-level warning", cfg)
    assert handle.get("ok"), f"failed to start server: {handle}"

    # Give server a moment
    time.sleep(1.0)

    # 4) Verify health endpoint
    assert health_check("http://localhost:8000/health", cfg, timeout_sec=10)

    # 5) Add and run a simple pytest
    test_code = (
        "def test_health_status():\n"
        "    import requests\n"
        "    r = requests.get('http://localhost:8000/health', timeout=2)\n"
        "    assert r.status_code == 200 and r.json().get('status') == 'ok'\n"
    )
    fs_write("tests/test_health.py", test_code, cfg)
    run = system_exec("pytest -q tests/test_health.py", timeout_sec=120, cfg=cfg)
    assert run.get("ok"), f"pytest run failed: {run}"
    out = str((run.get("result") or {}).get("stdout") or "")
    assert "1 passed" in out

    # 6) Stop server
    stop = stop_background_process(handle, cfg)
    assert stop.get("ok"), f"failed to stop server: {stop}"
