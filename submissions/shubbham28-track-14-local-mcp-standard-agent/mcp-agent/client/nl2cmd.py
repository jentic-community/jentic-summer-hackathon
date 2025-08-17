from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional import for tests with mocks
    OpenAI = None  # type: ignore

from client.tools_schema import schema_as_prompt

_SYSTEM_PROMPT = (
    "You are a planner that converts natural language requests into a strict JSON list of MCP tool calls. "
    "Output JSON ONLY. Do not include markdown or commentary.\n\n"
    "Schema for tools/actions and required args is provided.\n\n"
    "Return a JSON array, where each item is: {\n"
    "  \"tool\": \"filesystem|system|browser\",\n"
    "  \"action\": \"<action>\",\n"
    "  \"args\": { <args per schema> }\n"
    "}.\n\n"
    "Rules:\n"
    "- Only use allowed tools/actions from the schema.\n"
    "- Ensure required args are present.\n"
    "- Keep plans minimal; combine related steps when possible.\n"
    "- If the query is unclear, propose a single clarifying step using the safest read-only action.\n"
)


class NaturalLanguagePlanner:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, temperature: Optional[float] = None) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or "gpt-3.5-turbo"
        self.temperature = 0.0 if temperature is None else float(temperature)
        self._client = None
        self._unavailable_reason: Optional[str] = None
        if OpenAI is None:
            self._unavailable_reason = "openai package not installed"
        elif not self.api_key:
            self._unavailable_reason = "OPENAI_API_KEY not provided"
        else:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                self._client = None
                self._unavailable_reason = f"OpenAI client init failed: {e}"

    def is_available(self) -> bool:
        return self._client is not None

    def unavailable_reason(self) -> Optional[str]:
        return self._unavailable_reason

    def plan(self, query: str) -> List[Dict[str, Any]]:
        schema = schema_as_prompt()
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT + "\nTOOL SCHEMA:\n" + schema},
            {"role": "user", "content": query},
        ]
        # If client not available (no key or openai not installed), return empty plan
        if self._client is None:
            return []
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
            )
        except Exception as e:
            # Capture API errors and surface as empty plan
            self._unavailable_reason = f"OpenAI chat error: {e}"
            return []
        # Extract text; handle different SDK shapes defensively
        try:
            text = resp.choices[0].message.content  # type: ignore[attr-defined]
        except Exception:
            text = getattr(resp, "choices", [{}])[0].get("message", {}).get("content", "")  # type: ignore
        if not text:
            return []
        # Some models may wrap in an object; support either array or an object with key 'plan'
        plan: Any = None
        try:
            plan = json.loads(text)
        except Exception:
            # Try to find first JSON array/object in text
            import re
            match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.S)
            if match:
                plan = json.loads(match.group(1))
        if isinstance(plan, dict) and "plan" in plan:
            plan = plan.get("plan")
        if not isinstance(plan, list):
            return []
        # Validate minimal fields
        out: List[Dict[str, Any]] = []
        for step in plan:
            if isinstance(step, dict) and "tool" in step and "action" in step and "args" in step:
                out.append({"tool": step["tool"], "action": step["action"], "args": step.get("args") or {}})
        return out
