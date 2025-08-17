"""
TODO: LLM abstraction stubs for the client.

No business logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    api_key: Optional[str] = None


class EchoLLM:
    def __init__(self, cfg: LLMConfig | None = None) -> None:
        self.cfg = cfg or LLMConfig()

    def complete(self, prompt: str) -> str:
        return prompt
