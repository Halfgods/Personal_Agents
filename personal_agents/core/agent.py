from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .llm import LLMBackend


@dataclass
class Tool:
    name: str
    description: str
    fn: callable


class Agent(ABC):
    name: str = "base"
    description: str = "Base agent"

    def __init__(self, llm: LLMBackend):
        self.llm = llm
        self.tools: list[Tool] = []
        self._register_tools()

    def _register_tools(self) -> None:
        pass

    @abstractmethod
    def system_prompt(self) -> str:
        ...

    def run(self, user_input: str, context: dict[str, Any] | None = None) -> str:
        ctx = context or {}
        ctx_str = ""
        if ctx:
            ctx_str = f"\nContext: {json.dumps(ctx, indent=2)}"

        tool_descs = ""
        if self.tools:
            tool_descs = "\n\nYou have access to these tools:\n"
            for t in self.tools:
                tool_descs += f"  - {t.name}: {t.description}\n"
            tool_descs += "Call a tool by writing: !tool_name(arg1=value1, arg2=value2)"

        prompt = f"""User: {user_input}{ctx_str}{tool_descs}

Respond helpfully. If you need to use a tool, include the tool call inline."""
        return self.llm.generate(prompt, system_prompt=self.system_prompt())

    def chat(self, messages: list[dict], context: dict[str, Any] | None = None) -> str:
        ctx_str = ""
        if context:
            ctx_str = f"\n\nSystem Context: {json.dumps(context, indent=2)}"
            
        sys_prompt = self.system_prompt() + ctx_str
        sys_msg = {"role": "system", "content": sys_prompt}
        return self.llm.chat([sys_msg] + messages)


import json
