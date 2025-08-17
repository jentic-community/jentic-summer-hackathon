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
    "BROWSER_SERVER_ENDPOINT", "http://localhost:8003/tool/browser_op"
)


def _post(action: str, args: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
    payload = {"action": action, "args": args, "request_id": str(uuid.uuid4())}
    try:
        resp = requests.post(ENDPOINT, json=payload, timeout=timeout)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip(f"Browser server not running at {ENDPOINT}")
    resp.raise_for_status()
    return resp.json()


def test_open_title_example_org_ok(log_response):
    data = _post("open_title", {"url": "https://example.org"})
    log_response("open_title example.org", data)
    assert data.get("ok") is True
    res = data.get("result") or {}
    title = (res.get("title") or "").lower()
    assert "example" in title


def test_open_title_disallowed_host_security_error(log_response):
    data = _post("open_title", {"url": "https://non-allowed.example"})
    log_response("open_title disallowed", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "SecurityError"


def test_open_title_invalid_url_validation_error(log_response):
    data = _post("open_title", {"url": "not-a-url"})
    log_response("open_title invalid", data)
    assert data.get("ok") is False
    err = data.get("error") or {}
    assert err.get("type") == "ValidationError"


def test_booking_search_artifacts_and_rows(log_response):
    # Skip if playwright not installed
    try:
        import playwright  # type: ignore
    except Exception:
        pytest.skip("Playwright not installed; skipping booking_search test")

    data = _post("booking_search", {"city": "Dublin", "n": 3})
    log_response("booking_search", data)
    assert data.get("ok") is True
    res = data.get("result") or {}
    csv_path = res.get("csv_path")
    screenshot_path = res.get("screenshot_path")
    assert csv_path and os.path.exists(csv_path)
    assert screenshot_path and os.path.exists(screenshot_path)
    rows = res.get("rows") or []
    assert isinstance(rows, list)
    assert len(rows) <= 5 and len(rows) >= 0
    # If rows present, validate keys
    if rows:
        for r in rows:
            assert set(["name", "price", "rating", "link"]).issubset(set(r.keys()))
