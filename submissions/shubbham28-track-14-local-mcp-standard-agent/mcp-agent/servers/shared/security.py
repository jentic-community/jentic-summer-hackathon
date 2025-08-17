from __future__ import annotations

import os
import re
from urllib.parse import urlparse
from pathlib import Path

"""
TODO: Security policies, permission checks, and sandboxing primitives.

No business logic yet.
"""

"""
Security helpers: sandboxed path resolution and checks.
Minimal, focused on preventing directory traversal outside a configured root.
"""


# Precompile allowlist regex for allowed shell commands
_ALLOWED_CMD_RE = re.compile(
    r"^("
    r"pytest\s+-q\b|"
    r"pip\s+install\b|"
    r"uvicorn\b|"
    r"curl\b|"
    r"playwright\s+install\b|"
    r"echo\b|"
    r"(?:python|python3)\s+(?:-c\b|-m\s+[A-Za-z0-9_.-]+\b|[\w./-]+\.py\b)"
    r")",
    re.IGNORECASE,
)


def is_allowed_command(cmd: str) -> bool:
    """Return True if the provided command string is permitted by the allowlist.

    The allowlist is intentionally narrow and matches safe prefixes only.
    """
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    return _ALLOWED_CMD_RE.match(cmd.strip()) is not None


def is_allowed_host(url: str, allowlist: list[str] | None = None) -> bool:
    """Return True if URL host is in an allowlist (exact or subdomain matches).

    allowlist items are hostnames like 'example.org' or 'localhost'.
    Subdomains are allowed (e.g., www.example.org allowed when 'example.org' is listed).
    """
    if not isinstance(url, str) or not url:
        return False
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            return False
    except Exception:
        return False

    allowed = allowlist or ["booking.com", "localhost", "google.com", "example.org"]
    host = host.lower()
    for allowed_host in allowed:
        ah = allowed_host.lower()
        if host == ah or host.endswith("." + ah):
            return True
    return False


def is_safe_path(root: Path, candidate: Path) -> bool:
    """
    Return True if 'candidate' is within 'root' after resolution.
    """
    try:
        root_resolved = root.resolve()
        cand_resolved = candidate.resolve()
    except Exception:
        return False

    try:
        # Prefer Python 3.9+'s Path.is_relative_to if available
        is_rel = getattr(cand_resolved, "is_relative_to", None)
        if callable(is_rel):
            return cand_resolved.is_relative_to(root_resolved)
    except Exception:
        pass

    # Fallback: compare common paths
    try:
        return os.path.commonpath([str(cand_resolved), str(root_resolved)]) == str(
            root_resolved
        )
    except Exception:
        return False


def resolve_in_sandbox(root: Path, user_path: str) -> Path:
    """
    Resolve a user-supplied path within the sandbox root.

    - Disallow absolute paths.
    - Normalize and collapse any '..' segments.
    - Raise ValueError if the resolved path escapes the root.
    """
    if not isinstance(user_path, str) or user_path == "":
        raise ValueError("Empty path")

    root_resolved = root.resolve()

    supplied = Path(user_path)
    if supplied.is_absolute():
        raise ValueError("Absolute paths are not allowed")

    # Join and resolve (non-strict)
    candidate = (root_resolved / supplied).resolve()

    if not is_safe_path(root_resolved, candidate):
        raise ValueError("Escapes sandbox root")

    return candidate
