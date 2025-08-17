"""
TODO: Streamlit UI placeholder for interacting with local MCP agents.

No business logic yet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st  # type: ignore

# Ensure project root is importable when running directly via Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from client.orchestrator import load_client_config, orchestrate_message  # type: ignore  # noqa: E402
from client.orchestrator import _post_json  # type: ignore  # noqa: E402
from client.nl2cmd import NaturalLanguagePlanner  # type: ignore  # noqa: E402
from client.tools_schema import TOOLS_SCHEMA  # type: ignore  # noqa: E402
from client.presenters import (
    render_logs_panel,
    render_fs_entries_table,
    render_help,
    render_system_exec,
    render_booking_result,
    render_fs_op_result,
    render_fs_read,
)  # type: ignore  # noqa: E402


st.set_page_config(page_title="MCP Agent Client", layout="wide")

st.title("MCP Agent — Local Client")

cfg = load_client_config()

with st.sidebar:
    st.subheader("Endpoints")
    st.code(json.dumps(cfg.endpoints, indent=2))
    st.subheader("Natural language")
    use_nl = st.checkbox("Use natural language planning (OpenAI)", value=False, help="Convert your input to a plan of tool calls using OpenAI, then execute it.")
    plan_only = st.checkbox("Plan only (don't execute)", value=False)
    if use_nl and not cfg.openai_api_key:
        st.warning("OPENAI_API_KEY not configured. Set env var or use ${OPENAI_API_KEY} in configs/config.yaml.")
    with st.expander("Supported tools and actions"):
        for tool, spec in (TOOLS_SCHEMA or {}).items():
            actions = list((spec or {}).get("actions", {}).keys())
            st.markdown(f"- {tool}: {', '.join(actions)}")

# Contextual instructions based on mode
if use_nl:
    st.info(
        "Natural language mode: describe your task and the agent will plan tool calls.\n\n"
        "Examples:\n"
        "- List the current folder and then create a folder name presentation\n"
        "- Create notes.txt in presentation with 'Hello' and then read it and then update it to \"It's a good day\" and show it and then delete it\n"
        "- Create a python script.py to multiply three numbers and test it with 4,5,6.\n"
        "- Create a python file to fibonacci series and execute for first 10 numbers.\n"
        "- Search Booking for Dublin, for 2 people from 9th sep 2025 to 15th sep 2025\n\n"
        "Tip: Enable 'Plan only' to preview steps before executing."
    )
else:
    st.write("Type a command. Examples: 'ls .', 'cat README.md', 'mkdir tmp', 'create notes.txt Hello', 'edit notes.txt Updated', 'delete tmp recursive', 'rename a b', 'exec echo hello', 'exec python script.py', 'booking Dublin 3  2025-09-10 2025-09-12'")

message = st.text_input("Message", value="ls ." if not use_nl else "List the current folder", key="message_input")
submit = st.button("Run", type="primary")

if submit and message.strip():
    with st.spinner("Running..."):
        if use_nl:
            planner = NaturalLanguagePlanner(
                api_key=cfg.openai_api_key,
                model=cfg.openai_model or None,
                temperature=cfg.openai_temperature if cfg.openai_temperature is not None else 0.0,
            )
            plan = planner.plan(message)
            # Show the plan immediately so users can see it before execution
            st.markdown("### Natural Language Plan")
            st.json({"plan": plan})
            # Combine logs from steps, and prepend a synthetic nl.plan log
            combined_logs = [{
                "ts": "",
                "level": "INFO",
                "message": "nl.plan",
                "context": {"plan": plan},
            }]
            # If no plan, surface reason in logs to help debugging
            if not plan:
                reason = getattr(planner, "unavailable_reason", lambda: None)()
                if reason:
                    combined_logs.append({"ts": "", "level": "WARN", "message": "nl.plan.unavailable", "context": {"reason": reason}})
                else:
                    combined_logs.append({"ts": "", "level": "WARN", "message": "nl.plan.empty", "context": {"hint": "Check OPENAI_API_KEY and that 'openai' package is installed"}})
            results = []
            if not plan_only and plan:
                # Progress indicators for long-running plans
                total = len(plan)
                progress = st.progress(0)
                step_status = st.empty()
                run_log = st.container()
                for step in plan:
                    tool = step.get("tool")
                    action = step.get("action")
                    args = step.get("args") or {}
                    ep_key = TOOLS_SCHEMA.get(tool, {}).get("endpoint_key", tool)
                    url = cfg.endpoints.get(ep_key)
                    # Choose sensible timeouts per tool/action
                    timeout = 15.0
                    if tool == "browser":
                        timeout = 90.0
                    elif tool == "system" and action == "exec":
                        timeout = 60.0
                    # Update status before starting the step
                    idx = len(results) + 1
                    step_status.info(f"Running step {idx}/{total}: {tool}.{action}…")
                    ok, data = _post_json(url, {"action": action, "args": args}, timeout=timeout)
                    results.append(data)
                    # Update progress and per-step result summary inline
                    progress.progress(int((idx / total) * 100))
                    with run_log:
                        if ok and isinstance(data, dict) and data.get("ok"):
                            st.success(f"Step {idx} completed: {tool}.{action}")
                        else:
                            st.error(f"Step {idx} failed: {tool}.{action}")
                    step_logs = data.get("logs") if isinstance(data, dict) else None
                    if isinstance(step_logs, list):
                        combined_logs.extend(step_logs)
                step_status.success("Plan execution finished")
            resp = {
                "ok": True,
                "kind": "nl_plan" if plan_only else "nl_execute",
                "result": {"plan": plan, "results": results},
                "logs": combined_logs,
            }
        else:
            resp = orchestrate_message(message, cfg)

    col_main, col_logs = st.columns([3, 2])

    with col_main:
        kind = resp.get("kind")
        if kind in {"nl_plan", "nl_execute"}:
            data = resp.get("result") or {}
            plan = data.get("plan") or []
            if kind == "nl_execute" and plan:
                st.markdown("### Results")
                results = data.get("results") or []
                for idx, (step, step_data) in enumerate(zip(plan, results), start=1):
                    tool = (step or {}).get("tool")
                    action = (step or {}).get("action")
                    st.markdown(f"#### Step {idx}: {tool}.{action}")
                    d = step_data or {}
                    if not isinstance(d, dict) or not d.get("ok"):
                        err = (d.get("error") or {}).get("message") if isinstance(d, dict) else None
                        st.error(err or "Step failed")
                        continue
                    result_obj = d.get("result") or {}
                    if tool == "filesystem":
                        if action == "list":
                            render_fs_entries_table((result_obj or {}).get("entries") or [])
                        elif action == "read":
                            render_fs_read(result_obj)
                        else:
                            render_fs_op_result(result_obj)
                    elif tool == "system" and action == "exec":
                        render_system_exec(result_obj)
                    elif tool == "browser" and action == "booking_search":
                        render_booking_result(result_obj)
                    else:
                        st.json(d)
        elif kind == "fs_list" and resp.get("ok"):
            result = resp.get("result") or {}
            render_fs_entries_table(result.get("entries") or [])
        elif kind == "fs_read" and resp.get("ok"):
            render_fs_read(resp.get("result") or {})
        elif kind == "fs_op" and resp.get("ok"):
            render_fs_op_result(resp.get("result") or {})
        elif kind == "system_exec" and resp.get("ok"):
            render_system_exec(resp.get("result") or {})
        elif kind == "booking_search" and resp.get("ok"):
            render_booking_result(resp.get("result") or {})
        elif kind == "help":
            render_help(resp.get("result") or {})
        else:
            st.error((resp.get("error") or {}).get("message") or "Request failed")

    with col_logs:
        render_logs_panel(resp.get("logs") or [])
else:
    # Initial help
    if use_nl:
        st.markdown("### Supported tools and actions")
        for tool, spec in (TOOLS_SCHEMA or {}).items():
            actions = ", ".join(list((spec or {}).get("actions", {}).keys()))
            st.markdown(f"- **{tool}**: {actions}")
    else:
        render_help({"help": [
            "Commands:",
            " - ls <path>",
            " - cat <path>",
            " - mkdir <path>",
            " - create <path> [content] [--overwrite]",
            " - edit <path> <content>",
            " - delete <path> [recursive]",
            " - rename <src> <dest>",
            " - exec <command> (e.g., python script.py, python -m module)",
            " - booking <city> [n] [YYYY-MM-DD YYYY-MM-DD]",
        ]})
