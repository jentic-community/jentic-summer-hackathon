import os
import uuid
from typing import Any, Dict, List

import pytest  # type: ignore

try:  # Ensure tests don't fail if requests isn't installed
    import requests
except Exception:  # pragma: no cover - environment dependency
    pytest.skip("requests not installed", allow_module_level=True)

pytestmark = pytest.mark.integration

ENDPOINT = os.environ.get(
    "FS_SERVER_ENDPOINT", "http://localhost:8001/tool/filesystem_op"
)


def _post(action: str, args: Dict[str, Any], timeout: float = 5.0) -> Dict[str, Any]:
    payload = {"action": action, "args": args, "request_id": str(uuid.uuid4())}
    try:
        resp = requests.post(ENDPOINT, json=payload, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip(f"Filesystem server not running at {ENDPOINT}")
    resp.raise_for_status()
    return resp.json()


def _extract_entries(result: Any) -> List[Dict[str, Any]]:
    """
    The API may return either:
      - result: [{name,is_dir}, ...]
      - result: { entries: [{name,is_dir}, ...] }
    Normalize to a list for assertions.
    """
    if isinstance(result, dict) and "entries" in result:
        entries = result["entries"]
    else:
        entries = result
    assert isinstance(entries, list), "Result must be list or have 'entries' list"
    return entries


def test_list_current_dir_returns_entries(log_response):
    data = _post("list", {"path": "."})
    log_response("list .", data)
    assert data.get("ok") is True
    entries = _extract_entries(data.get("result"))
    assert isinstance(entries, list)
    assert len(entries) >= 1
    assert all(isinstance(e, dict) for e in entries)
    # Ensure fields exist; content specifics are server-dependent
    assert all("name" in e and "is_dir" in e for e in entries)


def test_list_nonexistent_dir_notfound(log_response):
    data = _post("list", {"path": "__does_not_exist__"})
    log_response("list missing", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "NotFound"
    # Optional: message presence
    assert "message" in err


def test_traversal_attempt_security_error(log_response):
    data = _post("list", {"path": "../"})
    log_response("list traversal", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "SecurityError"
    # Optional: message presence
    assert "message" in err


def test_write_read_roundtrip_succeeds(log_response):
    unique = f"artifacts/_tmp/fs_rw_{uuid.uuid4().hex}.txt"
    content = "hello\nworld"
    # Write
    w = _post("write", {"path": unique, "content": content})
    log_response("write", w)
    assert w.get("ok") is True
    assert isinstance((w.get("result") or {}).get("bytes_written"), int)
    # Read back
    r = _post("read", {"path": unique})
    log_response("read", r)
    assert r.get("ok") is True
    assert (r.get("result") or {}).get("content") == content


def test_append_adds_content_to_end_with_newline_if_needed(log_response):
    unique = f"artifacts/_tmp/fs_append_{uuid.uuid4().hex}.txt"
    # Start with content without trailing newline
    initial = "line1"
    append_text = "line2"
    expected = "line1\nline2"
    w = _post("write", {"path": unique, "content": initial})
    log_response("write", w)
    assert w.get("ok") is True
    a = _post("append", {"path": unique, "content": append_text})
    log_response("append", a)
    assert a.get("ok") is True
    r = _post("read", {"path": unique})
    log_response("read", r)
    assert r.get("ok") is True
    assert (r.get("result") or {}).get("content") == expected


def test_read_nonexistent_returns_notfound(log_response):
    unique = f"artifacts/_tmp/missing_{uuid.uuid4().hex}.txt"
    r = _post("read", {"path": unique})
    log_response("read missing", r)
    assert r.get("ok") is False
    err = r.get("error") or {}
    assert err.get("type") == "NotFound"


def test_write_outside_sandbox_security_error(log_response):
    w = _post("write", {"path": "../x", "content": "hello"})
    log_response("write outside", w)
    assert w.get("ok") is False
    err = w.get("error") or {}
    assert err.get("type") == "SecurityError"
