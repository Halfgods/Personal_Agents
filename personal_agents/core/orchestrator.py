import json
from typing import Any

from .llm import LLMBackend, create_llm, LLMConfig, auto_detect_backend
from .agent import Agent


class Orchestrator:
    def __init__(self, llm: LLMBackend | None = None, config: LLMConfig | None = None):
        if llm is None:
            if config is None:
                backend = auto_detect_backend()
                if backend == "none":
                    raise RuntimeError(
                        "No LLM backend available. Install Ollama or `pip install transformers`"
                    )
                config = LLMConfig(backend=backend)
            llm = create_llm(config)
        self.llm = llm
        self.agents: dict[str, Agent] = {}
        self.conversation_history: list[dict] = []
        self.user_context: dict[str, Any] = {}

    def register(self, agent: Agent) -> None:
        self.agents[agent.name] = agent

    def route(self, user_input: str) -> tuple[str, Agent | None]:
        agent_list = "\n".join(
            f"  - {name}: {agent.description}"
            for name, agent in self.agents.items()
        )
        route_prompt = f"""Available agents:
{agent_list}

User message: {user_input}

Which agent should handle this? Reply with just the agent name, or "general" if unsure."""

        agent_name = self.llm.generate(
            route_prompt,
            system_prompt="You route user requests to the best agent. Reply with only the agent name.",
        ).strip().lower()

        for name in self.agents:
            if name in agent_name:
                return name, self.agents[name]
        return "general", self.agents.get("general")

    def process(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})

        agent_name, agent = self.route(user_input)
        if agent is None:
            response = self.llm.chat(self.conversation_history[-10:])
        else:
            response = agent.chat(self.conversation_history[-10:], self.user_context)

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def set_context(self, key: str, value: Any) -> None:
        self.user_context[key] = value

    def get_context(self, key: str) -> Any | None:
        return self.user_context.get(key)
