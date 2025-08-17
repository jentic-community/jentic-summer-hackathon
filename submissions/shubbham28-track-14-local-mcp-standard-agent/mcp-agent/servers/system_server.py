"""
TODO: System MCP server stub for command/process/system info operations.

No business logic yet.
"""

from __future__ import annotations

import sys
import time
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI  # type: ignore
from pydantic import BaseModel  # type: ignore

# Ensure project root (mcp-agent) is importable when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from servers.shared.security import is_allowed_command  # noqa: E402

app = FastAPI(title="System MCP Server", version="0.1.0")


class ToolRequest(BaseModel):
    action: str
    args: Dict[str, Any] = {}
    request_id: Optional[str] = None


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(level: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    entry = {"ts": _ts(), "level": level, "message": message}
    if context:
        entry["context"] = context
    return entry


@app.post("/tool/system_exec")
def system_exec(req: ToolRequest) -> Dict[str, Any]:
    logs = [_log("INFO", "request.received", {"action": req.action})]

    if req.action != "exec":
        logs.append(_log("ERROR", "validation.unsupported_action", {"action": req.action}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Unsupported action"}, "logs": logs}

    cmd = req.args.get("cmd")
    timeout_sec = req.args.get("timeout_sec")
    if not isinstance(cmd, str) or not cmd.strip():
        logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'cmd'"}, "logs": logs}

    if timeout_sec is not None and not isinstance(timeout_sec, int):
        logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "'timeout_sec' must be int"}, "logs": logs}

    if not is_allowed_command(cmd):
        logs.append(_log("ERROR", "security.command_blocked", {"cmd": cmd}))
        return {"ok": False, "error": {"type": "SecurityError", "message": "Command not allowed"}, "logs": logs}

    try:
        start = time.perf_counter()
        completed = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_sec or None,
        )
        duration = time.perf_counter() - start
        result = {
            "exit_code": int(completed.returncode),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "duration_sec": round(duration, 3),
        }
        logs.append(_log("INFO", "system.exec.ok", {"exit_code": result["exit_code"], "duration_sec": result["duration_sec"]}))
        return {"ok": True, "result": result, "logs": logs}
    except subprocess.TimeoutExpired:
        logs.append(_log("ERROR", "system.exec.timeout", {"timeout_sec": timeout_sec}))
        return {"ok": False, "error": {"type": "Timeout", "message": "Command timed out"}, "logs": logs}
    except Exception as e:
        logs.append(_log("ERROR", "system.exec.failed", {"error": str(e)}))
        return {"ok": False, "error": {"type": "ExecutionError", "message": str(e)}, "logs": logs}


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(app, host="0.0.0.0", port=8002)
