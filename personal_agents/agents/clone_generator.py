import json
import re
from pathlib import Path
from ..core.agent import Agent
from ..core.llm import LLMBackend

class CloneGenerator(Agent):
    name: str = "creator"
    description: str = "Generates and deploys specialized AI clones for repetitive tasks."

    def __init__(self, llm: LLMBackend):
        super().__init__(llm)
        self.dynamic_dir = Path("personal_agents/agents/dynamic")
        self.dynamic_dir.mkdir(parents=True, exist_ok=True)

    def system_prompt(self) -> str:
        return """You are JARVIS's Clone Generator. 
Your sole purpose is to create new, highly specialized AI agents to help the user.
When the user asks you to create an agent or automate a new repetitive task, you design an agent.
You MUST reply with a JSON object wrapped in ```json ... ``` that contains:
{
  "name": "a single lowercase word identifier (e.g. finance, researcher, fitness)",
  "description": "Short summary of what this agent does",
  "system_prompt": "The extremely detailed persona and precise instructions for the agent."
}
You should also provide a brief confirmation message outside the JSON block."""

    def chat(self, messages: list[dict], context: dict | None = None) -> str:
        response = super().chat(messages, context)
        
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            try:
                json_str = response[start:end+1]
                config = json.loads(json_str)
                agent_name = config.get("name", "unknown")
                if agent_name == "unknown":
                    return "Error: Could not determine clone name."
                
                # Format name safely
                agent_name = re.sub(r'[^a-z0-9_]', '', agent_name.lower())
                
                file_path = self.dynamic_dir / f"{agent_name}.json"
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=2)
                
                # Remove the JSON block from the output to show to the user
                clean_response = response[:start] + response[end+1:]
                clean_response = clean_response.replace("```json", "").replace("```", "").strip()
                
                if not clean_response:
                    clean_response = f"Successfully generated and deployed the {agent_name} clone!"
                else:
                    clean_response += f"\n\n*(System Note: Clone '{agent_name}' has been successfully deployed and loaded!)*"
                
                return clean_response
            except Exception as e:
                return f"Error parsing clone configuration: {e}\nRaw output: {response}"
        
        return response
