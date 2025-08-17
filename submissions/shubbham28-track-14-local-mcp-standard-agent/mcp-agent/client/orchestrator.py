"""
TODO: Orchestration layer to coordinate MCP servers and client UI.

No business logic yet.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests  # type: ignore

# Expand values like ${OPENAI_API_KEY} from environment
from typing import Optional as _Optional  # alias to avoid clashes in helpers
import re as _re

def _expand_env_placeholders(value: _Optional[str]) -> _Optional[str]:
    if not isinstance(value, str):
        return value
    m = _re.fullmatch(r"\$\{([A-Z0-9_]+)\}", value)
    if m:
        return os.environ.get(m.group(1))
    return value

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional in non-client contexts
    yaml = None  # type: ignore

# Defaults for local dev
DEFAULT_ENDPOINTS = {
    "filesystem": "http://localhost:8001/tool/filesystem_op",
    "system": "http://localhost:8002/tool/system_exec",
    "browser": "http://localhost:8003/tool/browser_op",
}


@dataclass
class ClientConfig:
    openai_api_key: Optional[str]
    endpoints: Dict[str, str]
    openai_model: Optional[str] = None
    openai_temperature: Optional[float] = None


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        if yaml is None:
            # Minimal fallback: try to load JSON-in-YAML files
            return json.loads(path.read_text(encoding="utf-8"))
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _env_override(endpoints: Dict[str, str]) -> Dict[str, str]:
    overridden = dict(endpoints)
    if os.environ.get("FS_SERVER_ENDPOINT"):
        overridden["filesystem"] = os.environ["FS_SERVER_ENDPOINT"]
    if os.environ.get("SYSTEM_SERVER_ENDPOINT"):
        overridden["system"] = os.environ["SYSTEM_SERVER_ENDPOINT"]
    if os.environ.get("BROWSER_SERVER_ENDPOINT"):
        overridden["browser"] = os.environ["BROWSER_SERVER_ENDPOINT"]
    return overridden


def load_client_config(repo_root: Optional[Path] = None) -> ClientConfig:
    """Load client config and endpoints from configs/.

    Order of precedence (highest first):
    - Environment variables FS_SERVER_ENDPOINT, SYSTEM_SERVER_ENDPOINT, BROWSER_SERVER_ENDPOINT
    - configs/mcp_servers.yaml -> servers[].endpoint
    - hardcoded DEFAULT_ENDPOINTS
    """
    root = repo_root or Path(__file__).resolve().parents[1]
    cfg_dir = root / "configs"

    base_cfg = _read_yaml(cfg_dir / "config.yaml")
    servers_cfg = _read_yaml(cfg_dir / "mcp_servers.yaml")

    endpoints: Dict[str, str] = dict(DEFAULT_ENDPOINTS)

    # Try to read endpoints from YAML if present
    servers = servers_cfg.get("servers") if isinstance(servers_cfg, dict) else None
    if isinstance(servers, list):
        for s in servers:
            try:
                name = s.get("name")
                enabled = s.get("enabled", True)
                endpoint = s.get("endpoint") or (s.get("config", {}) or {}).get("endpoint")
                if enabled and isinstance(name, str) and isinstance(endpoint, str) and endpoint:
                    endpoints[name] = endpoint
            except Exception:
                continue

    endpoints = _env_override(endpoints)

    openai_api_key = None
    openai_model = None
    openai_temperature = None
    if isinstance(base_cfg, dict):
        # Support either top-level openai_api_key or agent.openai_api_key
        openai_api_key = _expand_env_placeholders(base_cfg.get("openai_api_key")) or (
             (base_cfg.get("agent") or {}).get("openai_api_key") if isinstance(base_cfg.get("agent"), dict) else None
         )
        # New-style nested openai config
        if isinstance(base_cfg.get("openai"), dict):
            oi = base_cfg.get("openai") or {}
            openai_api_key = _expand_env_placeholders(oi.get("api_key")) or openai_api_key
            openai_model = oi.get("model")
            try:
                openai_temperature = float(oi.get("temperature")) if oi.get("temperature") is not None else None
            except Exception:
                openai_temperature = None

    return ClientConfig(openai_api_key=openai_api_key, endpoints=endpoints, openai_model=openai_model, openai_temperature=openai_temperature)


def _post_json(url: str, payload: Dict[str, Any], timeout: float = 15.0) -> Tuple[bool, Dict[str, Any]]:
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        data = resp.json()
        ok = bool(data.get("ok")) and resp.status_code == 200
        return ok, data
    except Exception as e:
        return False, {"ok": False, "error": {"type": "NetworkError", "message": str(e)}, "logs": []}


def _parse_ls(message: str) -> Optional[str]:
    parts = message.strip().split()
    if len(parts) >= 1 and parts[0] in {"ls", "list"}:
        # default path '.' if not provided
        return parts[1] if len(parts) > 1 else "."
    return None


def _parse_exec(message: str) -> Optional[str]:
    msg = message.strip()
    if msg.startswith("exec "):
        cmd = msg[len("exec "):].strip()
        return cmd if cmd else None
    if msg == "exec":
        return ""
    return None


def _parse_booking(message: str) -> Optional[Tuple[str, int, Optional[str], Optional[str]]]:
    parts = message.strip().split()
    if not parts or parts[0] != "booking":
        return None
    if len(parts) < 2:
        return None
    # Detect optional trailing dates YYYY-MM-DD YYYY-MM-DD
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    def _is_date(tok: str) -> bool:
        if len(tok) != 10:
            return False
        try:
            y, m, d = tok.split("-")
            return len(y) == 4 and len(m) == 2 and len(d) == 2 and all(t.isdigit() for t in (y, m, d))
        except Exception:
            return False
    tokens = parts[1:]
    if len(tokens) >= 2 and _is_date(tokens[-1]) and _is_date(tokens[-2]):
        date_to = tokens[-1]
        date_from = tokens[-2]
        tokens = tokens[:-2]
    # If last token is int, use as n
    n = 5
    if tokens and tokens[-1].isdigit():
        try:
            n = max(1, int(tokens[-1]))
            tokens = tokens[:-1]
        except Exception:
            pass
    city = " ".join(tokens).strip()
    if not city:
        return None
    return city, n, date_from, date_to


def _parse_mkdir(message: str) -> Optional[str]:
    parts = message.strip().split()
    if len(parts) >= 2 and parts[0] == "mkdir":
        return " ".join(parts[1:]).strip()
    return None


def _parse_delete(message: str) -> Optional[Tuple[str, bool]]:
    parts = message.strip().split()
    if len(parts) >= 2 and parts[0] == "delete":
        # If last token is 'recursive', enable recursive
        recursive = False
        if parts[-1].lower() in {"recursive", "-r", "--recursive"}:
            recursive = True
            path = " ".join(parts[1:-1]).strip()
        else:
            path = " ".join(parts[1:]).strip()
        if path:
            return path, recursive
    return None


def _parse_rename(message: str) -> Optional[Tuple[str, str]]:
    parts = message.strip().split()
    if len(parts) >= 3 and parts[0] == "rename":
        src = parts[1]
        dest = " ".join(parts[2:]).strip()
        if src and dest:
            return src, dest
    return None


def _parse_create(message: str) -> Optional[Tuple[str, str, bool]]:
    parts = message.strip().split()
    if len(parts) >= 2 and parts[0] == "create":
        # create <path> [--overwrite] [content...]
        tokens = parts[1:]
        overwrite = False
        tokens_wo_flags = []
        for t in tokens:
            if t in {"--overwrite", "overwrite"}:
                overwrite = True
            else:
                tokens_wo_flags.append(t)
        if not tokens_wo_flags:
            return None
        path = tokens_wo_flags[0]
        content = " ".join(tokens_wo_flags[1:]) if len(tokens_wo_flags) > 1 else ""
        return path, content, overwrite
    return None


def _parse_edit(message: str) -> Optional[Tuple[str, str]]:
    parts = message.strip().split()
    if len(parts) >= 2 and parts[0] == "edit":
        # edit <path> <content...>
        path = parts[1]
        content = " ".join(parts[2:]) if len(parts) > 2 else ""
        return path, content
    return None


def _parse_cat(message: str) -> Optional[str]:
    parts = message.strip().split()
    if len(parts) >= 2 and parts[0] == "cat":
        return " ".join(parts[1:]).strip()
    return None


def orchestrate_message(message: str, cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    """Route a user message to the appropriate MCP server.

    Supported:
    - "ls <path>": list directory via filesystem server
    - "cat <path>": read file via filesystem server
    - "exec <cmd>": execute allowlisted command via system server
    - "booking <city> [n]": headless scrape via browser server
    - Filesystem ops: mkdir, create, edit, delete, rename

    Returns a dict:
    { ok: bool, kind: 'fs_list'|'fs_read'|'fs_op'|'system_exec'|'booking_search'|'help'|'error', result: {...}?, logs: [...]?, error?:{...} }
    """
    cfg = cfg or load_client_config()

    # Filesystem list
    path = _parse_ls(message)
    if path is not None and path != "__NO_MATCH__":
        payload = {"action": "list", "args": {"path": path}}
        ok, data = _post_json(cfg.endpoints["filesystem"], payload)
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_list", "result": data.get("result"), "logs": data.get("logs", [])}
        else:
            return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # Filesystem read (cat)
    cat_path = _parse_cat(message)
    if cat_path is not None:
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "read", "args": {"path": cat_path}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_read", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # mkdir
    mk = _parse_mkdir(message)
    if mk is not None:
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "mkdir", "args": {"path": mk}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_op", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # delete
    dele = _parse_delete(message)
    if dele is not None:
        d_path, recursive = dele
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "delete", "args": {"path": d_path, "recursive": recursive}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_op", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # rename
    rn = _parse_rename(message)
    if rn is not None:
        src, dest = rn
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "rename", "args": {"path": src, "dest": dest}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_op", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # create
    cr = _parse_create(message)
    if cr is not None:
        c_path, content, overwrite = cr
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "create", "args": {"path": c_path, "content": content, "overwrite": overwrite}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_op", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # edit
    ed = _parse_edit(message)
    if ed is not None:
        e_path, content = ed
        ok, data = _post_json(cfg.endpoints["filesystem"], {"action": "edit", "args": {"path": e_path, "content": content}})
        if ok and data.get("ok"):
            return {"ok": True, "kind": "fs_op", "result": data.get("result"), "logs": data.get("logs", [])}
        return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # System exec
    cmd = _parse_exec(message)
    if cmd is not None:
        if not cmd:
            return {
                "ok": True,
                "kind": "help",
                "result": {"help": ["Usage:", " - exec <command>"]},
                "logs": [],
            }
        payload = {"action": "exec", "args": {"cmd": cmd}}
        ok, data = _post_json(cfg.endpoints["system"], payload, timeout=60.0)
        if ok and data.get("ok"):
            return {"ok": True, "kind": "system_exec", "result": data.get("result"), "logs": data.get("logs", [])}
        else:
            return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # Booking search
    booking = _parse_booking(message)
    if booking is not None:
        city, n, date_from, date_to = booking
        args: Dict[str, Any] = {"city": city, "n": n}
        if date_from and date_to:
            args.update({"date_from": date_from, "date_to": date_to})
        payload = {"action": "booking_search", "args": args}
        ok, data = _post_json(cfg.endpoints["browser"], payload, timeout=90.0)
        if ok and data.get("ok"):
            return {"ok": True, "kind": "booking_search", "result": data.get("result"), "logs": data.get("logs", [])}
        else:
            return {"ok": False, "kind": "error", "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}, "logs": data.get("logs", [])}

    # Fallback: help
    return {
        "ok": True,
        "kind": "help",
        "result": {
            "help": [
                "Commands:",
                " - ls <path>           List directory entries",
                " - cat <path>          Show file contents",
                " - mkdir <path>        Create directory",
                " - create <path> [content] [--overwrite]",
                " - edit <path> <content>",
                " - delete <path> [recursive]",
                " - rename <src> <dest>",
                " - exec <command>      Run allowlisted system command",
                " - booking <city> [n] [YYYY-MM-DD YYYY-MM-DD]",
            ]
        },
        "logs": [],
    }


def _fs_op(cfg: ClientConfig, action: str, args: Dict[str, Any]) -> Dict[str, Any]:
    ok, data = _post_json(cfg.endpoints["filesystem"], {"action": action, "args": args})
    return data


def fs_write(path: str, content: str, cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    cfg = cfg or load_client_config()
    return _fs_op(cfg, "write", {"path": path, "content": content})


def fs_read(path: str, cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    cfg = cfg or load_client_config()
    return _fs_op(cfg, "read", {"path": path})


def system_exec(cmd: str, timeout_sec: Optional[int] = None, cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    cfg = cfg or load_client_config()
    args: Dict[str, Any] = {"cmd": cmd}
    if isinstance(timeout_sec, int):
        args["timeout_sec"] = timeout_sec
    ok, data = _post_json(cfg.endpoints["system"], {"action": "exec", "args": args}, timeout=60.0)
    return data


def _parse_pytest_summary(stdout: str, stderr: str) -> Dict[str, int]:
    import re
    text = f"{stdout}\n{stderr}"
    passed = 0
    failed = 0
    m = re.search(r"(\d+)\s+passed", text)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", text)
    if m:
        failed = int(m.group(1))
    return {"passed": passed, "failed": failed}


def run_workflow_create_and_test(cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    """Create a module with a bug, a failing test, fix it, and re-run tests.

    Returns: {before_failures, after_failures, edited_files:[...]}"""
    cfg = cfg or load_client_config()

    edited: List[str] = []

    # 1) Create utils package and math_fix stub
    fs_write("utils/__init__.py", "", cfg)
    edited.append("utils/__init__.py")

    math_stub = """
# Auto-generated by workflow

def add(a, b):
    # TODO: implement
    pass
""".strip() + "\n"
    fs_write("utils/math_fix.py", math_stub, cfg)
    edited.append("utils/math_fix.py")

    # 2) Create failing test
    test_body = """
# Auto-generated by workflow

def test_add():
    from utils.math_fix import add
    assert add(1, 2) == 3
""".strip() + "\n"
    fs_write("tests/test_math_fix.py", test_body, cfg)
    edited.append("tests/test_math_fix.py")

    # 3) Run pytest on our test file only
    first = system_exec("pytest -q tests/test_math_fix.py", timeout_sec=60, cfg=cfg)
    if not first.get("ok"):
        # Map error to failed=1 to ensure we try to fix
        before = 1
    else:
        res = first.get("result") or {}
        counts = _parse_pytest_summary(str(res.get("stdout") or ""), str(res.get("stderr") or ""))
        before = counts.get("failed", 0)

    # 4) Inject minimal fix
    math_fixed = """
# Auto-generated by workflow

def add(a, b):
    return a + b
""".strip() + "\n"
    fs_write("utils/math_fix.py", math_fixed, cfg)
    edited.append("utils/math_fix.py")

    # 5) Re-run pytest
    second = system_exec("pytest -q tests/test_math_fix.py", timeout_sec=60, cfg=cfg)
    if not second.get("ok"):
        after = 1
    else:
        res2 = second.get("result") or {}
        counts2 = _parse_pytest_summary(str(res2.get("stdout") or ""), str(res2.get("stderr") or ""))
        after = counts2.get("failed", 0)

    return {"before_failures": before, "after_failures": after, "edited_files": edited}


def start_background_process(cmd: str, cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    """Start an allowed process in background via system server and return handle with pid.

    Implementation: use shell background '&' and echo $! to capture PID. The command must
    start with an allowlisted prefix (e.g., 'uvicorn').
    """
    cfg = cfg or load_client_config()
    # Append backgrounding and echo PID; ensure it starts with an allowed prefix.
    bg_cmd = f"{cmd} & echo $!"
    data = system_exec(bg_cmd, timeout_sec=10, cfg=cfg)
    if not data.get("ok"):
        return {"ok": False, "error": data.get("error")}
    pid_str = str((data.get("result") or {}).get("stdout") or "").strip().splitlines()[-1].strip()
    try:
        pid = int(pid_str)
    except Exception:
        return {"ok": False, "error": {"type": "ExecutionError", "message": f"Could not parse PID from stdout: {pid_str}"}}
    return {"ok": True, "pid": pid, "cmd": cmd}


def stop_background_process(handle: Dict[str, Any], cfg: Optional[ClientConfig] = None) -> Dict[str, Any]:
    """Stop a background process by PID using python -c to send SIGTERM."""
    cfg = cfg or load_client_config()
    pid = handle.get("pid")
    if not isinstance(pid, int):
        return {"ok": False, "error": {"type": "ValidationError", "message": "Invalid PID"}}
    kill_cmd = f"python -c \"import os,signal,time; os.kill({pid}, signal.SIGTERM); time.sleep(0.2)\""
    data = system_exec(kill_cmd, timeout_sec=10, cfg=cfg)
    if not data.get("ok"):
        return {"ok": False, "error": data.get("error")}
    return {"ok": True}


def health_check(url: str, cfg: Optional[ClientConfig] = None, timeout_sec: int = 10) -> bool:
    """Return True if GET url returns 200 and contains 'status":"ok"'."""
    cfg = cfg or load_client_config()
    code = system_exec(f"curl -s -o /dev/null -w \"%{{http_code}}\" {url}", timeout_sec=timeout_sec, cfg=cfg)
    if not code.get("ok"):
        return False
    status_code = str((code.get("result") or {}).get("stdout") or "").strip()
    if status_code != "200":
        return False
    body = system_exec(f"curl -s {url}", timeout_sec=timeout_sec, cfg=cfg)
    if not body.get("ok"):
        return False
    text = str((body.get("result") or {}).get("stdout") or "")
    return ('"status"' in text and '"ok"' in text)


def run_booking_search(
    city: str,
    n: int = 5,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    cfg: Optional[ClientConfig] = None,
) -> Dict[str, Any]:
    cfg = cfg or load_client_config()
    args: Dict[str, Any] = {"city": city, "n": int(n)}
    if date_from and date_to:
        args.update({"date_from": date_from, "date_to": date_to})
    ok, data = _post_json(cfg.endpoints["browser"], {"action": "booking_search", "args": args}, timeout=90.0)
    if not ok or not data.get("ok"):
        return {"ok": False, "error": data.get("error") or {"type": "Unknown", "message": "Request failed"}}
    res = data.get("result") or {}
    rows = res.get("rows") or []
    return {
        "ok": True,
        "row_count": len(rows),
        "csv_path": res.get("csv_path"),
        "screenshot_path": res.get("screenshot_path"),
        "rows": rows,
    }
