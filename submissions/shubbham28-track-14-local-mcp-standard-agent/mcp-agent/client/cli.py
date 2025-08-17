from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from client.orchestrator import load_client_config, orchestrate_message, _post_json  # type: ignore
from client.nl2cmd import NaturalLanguagePlanner  # type: ignore
from client.tools_schema import TOOLS_SCHEMA  # type: ignore


def _execute_plan(steps: List[Dict[str, Any]], cfg) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for step in steps:
        tool = step.get("tool")
        action = step.get("action")
        args = step.get("args") or {}
        ep_key = TOOLS_SCHEMA.get(tool, {}).get("endpoint_key")
        if not ep_key:
            results.append({"ok": False, "error": {"type": "ValidationError", "message": f"Unknown tool: {tool}"}})
            continue
        url = cfg.endpoints.get(ep_key)
        ok, data = _post_json(url, {"action": action, "args": args})
        results.append(data if ok else {"ok": False, "error": data.get("error") if isinstance(data, dict) else {"type": "Unknown"}})
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP Agent CLI")
    parser.add_argument("message", nargs="?", help="Direct command (e.g., ls .)")
    parser.add_argument("--nl", dest="nl", help="Natural language query", default=None)
    parser.add_argument("--print-plan", dest="print_plan", action="store_true", help="Print planned JSON only")
    args = parser.parse_args()

    cfg = load_client_config()

    if args.nl:
        planner = NaturalLanguagePlanner(api_key=cfg.openai_api_key)
        plan = planner.plan(args.nl)
        if args.print_plan:
            print(json.dumps(plan, indent=2))
            return
        results = _execute_plan(plan, cfg)
        print(json.dumps({"plan": plan, "results": results}, indent=2))
        return

    if not args.message:
        parser.print_help()
        return

    resp = orchestrate_message(args.message, cfg)
    print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    main()
