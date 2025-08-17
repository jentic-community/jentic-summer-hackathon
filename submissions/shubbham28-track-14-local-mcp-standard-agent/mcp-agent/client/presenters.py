"""
TODO: Presentation helpers for formatting data for the client.

No business logic yet.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore


def render_logs_panel(logs: List[Dict[str, Any]]) -> None:
    # Show all logs without filtering
    with st.expander("Logs", expanded=False):
        if not logs:
            st.caption("No logs")
            return
        st.json(logs)


def render_fs_entries_table(entries: List[Dict[str, Any]]) -> None:
    if not entries:
        st.info("No entries")
        return
    df = pd.DataFrame(entries)
    # Ensure predictable column order
    cols = [c for c in ["name", "is_dir"] if c in df.columns] + [c for c in df.columns if c not in {"name", "is_dir"}]
    st.dataframe(df[cols], use_container_width=True)


def render_help(data: Dict[str, Any]) -> None:
    lines = data.get("help") if isinstance(data, dict) else None
    st.markdown("### Help")
    if isinstance(lines, list):
        for l in lines:
            st.write(l)
    else:
        st.write("Commands:")
        st.write(" - ls <path>")
        st.write(" - exec <command>")
        st.write(" - booking <city> [n]")


essential_exec_fields = ["exit_code", "stdout", "stderr", "duration_sec"]

def render_system_exec(result: Dict[str, Any]) -> None:
    st.markdown("### System Exec Result")
    # show essential fields if present
    for key in essential_exec_fields:
        if key in result:
            if key in {"stdout", "stderr"}:
                st.subheader(key)
                content = result.get(key) or ""
                if content.strip():
                    st.code(content)
                else:
                    st.caption("<empty>")
            else:
                st.write(f"{key}: {result.get(key)}")


def render_booking_result(result: Dict[str, Any]) -> None:
    st.markdown("### Booking Search Result")
    rows = result.get("rows") or []
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    csv_path = result.get("csv_path")
    screenshot_path = result.get("screenshot_path")
    if csv_path:
        st.caption(f"CSV: {csv_path}")
    if screenshot_path:
        try:
            st.image(screenshot_path, caption="Screenshot", use_column_width=True)
        except Exception:
            st.caption(f"Screenshot: {screenshot_path}")


def render_fs_op_result(result: Dict[str, Any]) -> None:
    st.markdown("### Filesystem Operation Result")
    if not isinstance(result, dict):
        st.write(result)
        return
    # Common fields to show if present
    for key in ("created", "deleted", "moved", "bytes_written", "path", "src", "dst"):
        if key in result:
            st.write(f"{key}: {result.get(key)}")


def render_fs_read(result: Dict[str, Any]) -> None:
    st.markdown("### File Contents")
    content = result.get("content")
    if isinstance(content, str):
        if content.strip():
            st.code(content)
        else:
            st.caption("<empty>")
    else:
        st.write(result)
