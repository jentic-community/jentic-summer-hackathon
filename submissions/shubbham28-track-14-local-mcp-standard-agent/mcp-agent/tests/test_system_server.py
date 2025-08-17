import os
import uuid
from typing import Any, Dict

import pytest  # type: ignore

try:  # Ensure tests don't fail if requests isn't installed
    import requests
except Exception:  # pragma: no cover - environment dependency
    pytest.skip("requests not installed", allow_module_level=True)

pytestmark = pytest.mark.integration

ENDPOINT = os.environ.get(
    "SYS_SERVER_ENDPOINT", "http://localhost:8002/tool/system_exec"
)


def _post(action: str, args: Dict[str, Any], timeout: float = 8.0) -> Dict[str, Any]:
    payload = {"action": action, "args": args, "request_id": str(uuid.uuid4())}
    try:
        resp = requests.post(ENDPOINT, json=payload, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip(f"System server not running at {ENDPOINT}")
    resp.raise_for_status()
    return resp.json()


def test_exec_echo_hello_ok(log_response):
    data = _post("exec", {"cmd": "echo hello"})
    log_response("exec echo", data)
    assert data.get("ok") is True
    res = data.get("result") or {}
    assert isinstance(res.get("exit_code"), int)
    assert res.get("exit_code") == 0
    assert "hello" in (res.get("stdout") or "")


def test_exec_blocked_command_security_error(log_response):
    data = _post("exec", {"cmd": "rm -rf /"})
    log_response("exec blocked", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "SecurityError"


def test_exec_timeout_returns_timeout_error(log_response):
    long_cmd = 'python -c "import time; time.sleep(3)"'
    data = _post("exec", {"cmd": long_cmd, "timeout_sec": 1})
    log_response("exec timeout", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "Timeout"
