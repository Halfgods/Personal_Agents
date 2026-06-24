import json
from pathlib import Path
from ..core.agent import Agent
from ..core.llm import LLMBackend

class DynamicAgent(Agent):
    def __init__(self, llm: LLMBackend, config_path: str | Path):
        self._config_path = Path(config_path)
        with open(self._config_path, "r") as f:
            self._config = json.load(f)
        
        self.name = self._config.get("name", "unknown")
        self.description = self._config.get("description", "A dynamically generated clone.")
        self._system_prompt = self._config.get("system_prompt", "You are a helpful assistant.")
        super().__init__(llm)

    def system_prompt(self) -> str:
        return self._system_prompt
