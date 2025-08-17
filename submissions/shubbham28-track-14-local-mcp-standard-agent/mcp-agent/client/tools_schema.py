# Tools schema used by the NaturalLanguagePlanner
from __future__ import annotations

from typing import Dict, List, Any

TOOLS_SCHEMA: Dict[str, Any] = {
    "filesystem": {
        "endpoint_key": "filesystem",
        "actions": {
            "list": {"args": {"path": "string"}, "description": "List directory entries"},
            "read": {"args": {"path": "string"}, "description": "Read file contents"},
            "write": {"args": {"path": "string", "content": "string"}, "description": "Write file (overwrite)"},
            "append": {"args": {"path": "string", "content": "string"}, "description": "Append to file"},
            "mkdir": {"args": {"path": "string", "exist_ok": "boolean?"}, "description": "Create directory"},
            "create": {"args": {"path": "string", "content": "string?", "overwrite": "boolean?"}, "description": "Create new file"},
            "edit": {"args": {"path": "string", "content": "string"}, "description": "Overwrite file with content"},
            "delete": {"args": {"path": "string", "recursive": "boolean?"}, "description": "Delete file or directory"},
            "rename": {"args": {"path": "string", "dest": "string"}, "description": "Rename or move"},
        },
    },
    "system": {
        "endpoint_key": "system",
        "actions": {
            "exec": {"args": {"cmd": "string", "timeout_sec": "int?"}, "description": "Run allowed shell command"},
        },
    },
    "browser": {
        "endpoint_key": "browser",
        "actions": {
            "open_title": {"args": {"url": "string"}, "description": "Open a page and get title"},
            "booking_search": {"args": {"city": "string", "n": "int", "date_from": "string?", "date_to": "string?"}, "description": "Scrape booking.com results and save artifacts"},
        },
    },
}


def schema_as_prompt() -> str:
    import json
    return json.dumps(TOOLS_SCHEMA, indent=2)
