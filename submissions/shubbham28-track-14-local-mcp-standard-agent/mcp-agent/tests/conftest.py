import os
import uuid
import json
from typing import Optional, Callable, Any

import pytest  # type: ignore


def _endpoint() -> str:
    return os.environ.get(
        "FS_SERVER_ENDPOINT", "http://localhost:8001/tool/filesystem_op"
    )


@pytest.fixture
def log_response(request) -> Callable[[str, Any], None]:
    """Record a short, printable snippet per test to show in terminal summary.

    Usage in tests:
        log_response("write", resp_json)
    """
    def _log(name: str, data: Any) -> None:
        try:
            snippet = json.dumps(data, ensure_ascii=False)
        except Exception:
            snippet = str(data)
        # Truncate to keep output readable
        snippet = snippet[:600]
        request.node.user_properties.append(("out", f"{name}: {snippet}"))
    return _log


def pytest_collection_finish(session: pytest.Session) -> None:
    # Show which tests were collected
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if not tr:
        return
    tr.write_line("Collected tests:")
    for item in session.items:
        tr.write_line(f" - {item.nodeid}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    # Record duration for the call phase
    if getattr(report, "when", "call") == "call":
        try:
            report.user_properties.append(("dur", f"{report.duration:.3f}s"))
        except Exception:
            pass


def pytest_report_header(config: pytest.Config) -> Optional[str]:
    # Always show which endpoint tests will target
    return f"MCP Filesystem endpoint: {_endpoint()}"


def pytest_terminal_summary(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    # Provide a quick reachability note so `-q` runs still print something useful.
    endpoint = _endpoint()
    try:
        import requests  # noqa: WPS433
    except Exception:
        terminalreporter.write_line(
            "Note: python-requests not installed; integration tests will be skipped.",
        )
        return

    payload = {"action": "list", "args": {"path": "."}, "request_id": str(uuid.uuid4())}
    try:
        resp = requests.post(endpoint, json=payload, timeout=0.5)
        ok = None
        try:
            data = resp.json()
            ok = data.get("ok")
        except Exception:
            pass
        terminalreporter.write_line(
            f"Filesystem server reachability: HTTP {resp.status_code}; ok={ok}")
    except Exception as exc:
        terminalreporter.write_line(
            f"Filesystem server not reachable at {endpoint}: {type(exc).__name__}: {exc}")

    # Summarize per-test recorded outputs
    terminalreporter.write_line("Test outputs (per test):")
    all_reports = []
    for key in ("passed", "failed", "error", "skipped"):
        reports = terminalreporter.getreports(key) or []
        all_reports.extend(reports)
    # Only show the call phase
    for rep in all_reports:
        if getattr(rep, "when", "call") != "call":
            continue
        outs = [v for (k, v) in getattr(rep, "user_properties", []) if k == "out"]
        durs = [v for (k, v) in getattr(rep, "user_properties", []) if k == "dur"]
        if outs or durs:
            suffix = f" (duration {durs[0]})" if durs else ""
            terminalreporter.write_line(f" - {rep.nodeid}{suffix}")
            for o in outs:
                terminalreporter.write_line(f"    {o}")
