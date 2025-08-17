"""
TODO: Filesystem MCP server stub for local file operations.

No business logic yet.
"""

from __future__ import annotations

import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI  # type: ignore
from pydantic import BaseModel  # type: ignore

# Ensure project root (mcp-agent) is importable when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from servers.shared.security import (  # noqa: E402
    is_safe_path,
    resolve_in_sandbox,
)

app = FastAPI(title="Filesystem MCP Server", version="0.1.0")


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


def _sandbox_root() -> Path:
    env_root = os.environ.get("SANDBOX_ROOT")
    if env_root:
        try:
            return Path(env_root).expanduser().resolve()
        except Exception:
            pass
    # Default to project directory (the mcp-agent folder)
    return PROJECT_ROOT.resolve()


def _list_entries(directory: Path) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for p in sorted(directory.iterdir(), key=lambda x: x.name.lower()):
        entries.append({"name": p.name, "is_dir": p.is_dir()})
    return entries


def _file_ends_with_newline(p: Path) -> bool:
    """
    Efficient check for trailing newline. Non-existent or empty files are treated
    as having a trailing newline to avoid prepending a newline on first append.
    """
    try:
        if not p.exists():
            return True
        size = p.stat().st_size
        if size == 0:
            return True
        with p.open("rb") as f:
            f.seek(-1, os.SEEK_END)
            return f.read(1) == b"\n"
    except Exception:
        # Fail-safe: don't add newline if unsure
        return True


@app.post("/tool/filesystem_op")
def filesystem_op(req: ToolRequest) -> Dict[str, Any]:
    logs: List[Dict[str, Any]] = []
    logs.append(_log("INFO", "request.received", {"action": req.action}))

    allowed_actions = {"list", "read", "write", "append", "mkdir", "create", "edit", "delete", "rename"}
    if req.action not in allowed_actions:
        logs.append(_log("ERROR", "validation.unsupported_action", {"action": req.action}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Unsupported action"}, "logs": logs}

    rel_path = req.args.get("path")
    if not isinstance(rel_path, str) or not rel_path:
        logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
        return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'path'"}, "logs": logs}

    root = _sandbox_root()
    try:
        target = resolve_in_sandbox(root, rel_path)
    except ValueError as e:
        logs.append(_log("ERROR", "security.path_violation", {"path": rel_path, "reason": str(e)}))
        return {"ok": False, "error": {"type": "SecurityError", "message": "Path traversal blocked"}, "logs": logs}

    if not is_safe_path(root, target):
        logs.append(_log("ERROR", "security.path_outside_root", {"path": str(target)}))
        return {"ok": False, "error": {"type": "SecurityError", "message": "Path outside sandbox root"}, "logs": logs}

    # list
    if req.action == "list":
        if not target.exists() or not target.is_dir():
            logs.append(_log("WARN", "fs.not_found_or_not_dir", {"path": str(target)}))
            return {"ok": False, "error": {"type": "NotFound", "message": "Directory not found"}, "logs": logs}
        entries = _list_entries(target)
        logs.append(_log("INFO", "fs.list.ok", {"count": len(entries)}))
        return {"ok": True, "result": {"entries": entries}, "logs": logs}

    # read
    if req.action == "read":
        if not target.exists() or not target.is_file():
            logs.append(_log("WARN", "fs.not_found_or_not_file", {"path": str(target)}))
            return {"ok": False, "error": {"type": "NotFound", "message": "File not found"}, "logs": logs}
        try:
            content = target.read_text(encoding="utf-8")
            logs.append(_log("INFO", "fs.read.ok", {"bytes": len(content.encode("utf-8"))}))
            return {"ok": True, "result": {"content": content}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.read.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # write
    if req.action == "write":
        content = req.args.get("content")
        if not isinstance(content, str):
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'content'"}, "logs": logs}
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            bytes_written = len(content.encode("utf-8"))
            logs.append(_log("INFO", "fs.write.ok", {"bytes": bytes_written}))
            return {"ok": True, "result": {"bytes_written": bytes_written}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.write.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # append
    if req.action == "append":
        content = req.args.get("content")
        if not isinstance(content, str):
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'content'"}, "logs": logs}
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            need_nl = (_file_ends_with_newline(target) is False)
            bytes_written = 0
            with target.open("a", encoding="utf-8") as f:
                if need_nl:
                    f.write("\n")
                    bytes_written += 1
                f.write(content)
                bytes_written += len(content.encode("utf-8"))
            logs.append(_log("INFO", "fs.append.ok", {"bytes": bytes_written, "added_newline": need_nl}))
            return {"ok": True, "result": {"bytes_written": bytes_written}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.append.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # mkdir (create directory)
    if req.action == "mkdir":
        exist_ok = bool(req.args.get("exist_ok", True))
        try:
            target.mkdir(parents=True, exist_ok=exist_ok)
            logs.append(_log("INFO", "fs.mkdir.ok", {"path": str(target), "exist_ok": exist_ok}))
            return {"ok": True, "result": {"created": True, "path": str(target)}, "logs": logs}
        except FileExistsError as e:
            logs.append(_log("ERROR", "fs.mkdir.exists", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "AlreadyExists", "message": str(e)}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.mkdir.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # create (new file, optional content, optional overwrite)
    if req.action == "create":
        content = req.args.get("content", "")
        overwrite = bool(req.args.get("overwrite", False))
        if not isinstance(content, str):
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "'content' must be a string"}, "logs": logs}
        try:
            if target.exists() and not overwrite:
                raise FileExistsError(f"File exists: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            logs.append(_log("INFO", "fs.create.ok", {"path": str(target), "bytes": len(content.encode("utf-8")), "overwrite": overwrite}))
            return {"ok": True, "result": {"created": True, "bytes_written": len(content.encode("utf-8"))}, "logs": logs}
        except FileExistsError as e:
            logs.append(_log("ERROR", "fs.create.exists", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "AlreadyExists", "message": str(e)}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.create.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # edit (overwrite entire file)
    if req.action == "edit":
        content = req.args.get("content")
        if not isinstance(content, str):
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'content'"}, "logs": logs}
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            bytes_written = len(content.encode("utf-8"))
            logs.append(_log("INFO", "fs.edit.ok", {"bytes": bytes_written}))
            return {"ok": True, "result": {"bytes_written": bytes_written}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.edit.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # delete (file or directory)
    if req.action == "delete":
        recursive = bool(req.args.get("recursive", False))
        if not target.exists():
            logs.append(_log("WARN", "fs.delete.not_found", {"path": str(target)}))
            return {"ok": False, "error": {"type": "NotFound", "message": "Path not found"}, "logs": logs}
        try:
            if target.is_dir():
                if recursive:
                    shutil.rmtree(target)
                else:
                    target.rmdir()
            else:
                target.unlink()
            logs.append(_log("INFO", "fs.delete.ok", {"path": str(target), "recursive": recursive}))
            return {"ok": True, "result": {"deleted": True, "path": str(target)}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.delete.failed", {"path": str(target), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # rename/move
    if req.action == "rename":
        src_rel = rel_path
        dst_rel = req.args.get("dest")
        if not isinstance(dst_rel, str) or not dst_rel:
            logs.append(_log("ERROR", "validation.invalid_args", {"args": req.args}))
            return {"ok": False, "error": {"type": "ValidationError", "message": "Missing or invalid 'dest'"}, "logs": logs}
        try:
            src = resolve_in_sandbox(root, src_rel)
            dst = resolve_in_sandbox(root, dst_rel)
        except ValueError as e:
            logs.append(_log("ERROR", "security.path_violation", {"reason": str(e)}))
            return {"ok": False, "error": {"type": "SecurityError", "message": "Path traversal blocked"}, "logs": logs}
        if not src.exists():
            logs.append(_log("WARN", "fs.rename.src_missing", {"src": str(src)}))
            return {"ok": False, "error": {"type": "NotFound", "message": "Source not found"}, "logs": logs}
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
            logs.append(_log("INFO", "fs.rename.ok", {"src": str(src), "dst": str(dst)}))
            return {"ok": True, "result": {"moved": True, "src": str(src), "dst": str(dst)}, "logs": logs}
        except Exception as e:
            logs.append(_log("ERROR", "fs.rename.failed", {"src": str(src), "error": str(e)}))
            return {"ok": False, "error": {"type": "IOError", "message": str(e)}, "logs": logs}

    # Unreachable due to allowed_actions check
    logs.append(_log("ERROR", "internal.unreachable"))
    return {"ok": False, "error": {"type": "InternalError", "message": "Unreachable state"}, "logs": logs}


if __name__ == "__main__":
    # Convenience for local dev: python servers/filesystem_server.py
    import uvicorn # type: ignore

    uvicorn.run(app, host="0.0.0.0", port=8001)
