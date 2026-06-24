import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from personal_agents.core.llm import LLMConfig, auto_detect_backend
from personal_agents.core.orchestrator import Orchestrator
from personal_agents.agents.general import GeneralAgent
from personal_agents.agents.scheduler import ScheduleAgent
from personal_agents.agents.gardener import GardenAgent
from personal_agents.agents.party import PartyAgent
from personal_agents.agents.medicator import MedicationAgent
from personal_agents.agents.clone_generator import CloneGenerator
from personal_agents.agents.dynamic_agent import DynamicAgent
from personal_agents.agents.system_agent import SystemAgent
from pathlib import Path
from personal_agents.demo import DemoOrchestrator, MockLLM

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import urllib.request
import json

backend = auto_detect_backend()
use_demo = False

if backend == "none":
    use_demo = True
elif backend == "ollama":
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        resp = urllib.request.urlopen(req, timeout=2)
        data = json.loads(resp.read())
        if not data.get("models"):
            print("Ollama is running but no models are found. Falling back to DEMO mode.")
            use_demo = True
    except Exception:
        use_demo = True

if use_demo:
    print("Running in DEMO mode (no LLM).")
    orc = DemoOrchestrator(llm=MockLLM())
else:
    print(f"Running with backend: {backend}")
    model_default = "llama3.2:3b" if backend == "ollama" else "microsoft/Phi-3-mini-4k-instruct"
    config = LLMConfig(backend=backend, model=model_default)
    orc = Orchestrator(config=config)

def load_agents():
    orc.agents.clear()
    orc.register(GeneralAgent(orc.llm))
    orc.register(ScheduleAgent(orc.llm))
    orc.register(GardenAgent(orc.llm))
    orc.register(PartyAgent(orc.llm))
    orc.register(MedicationAgent(orc.llm))
    orc.register(CloneGenerator(orc.llm))
    orc.register(SystemAgent(orc.llm))
    
    dynamic_dir = Path("personal_agents/agents/dynamic")
    if dynamic_dir.exists():
        for config_file in dynamic_dir.glob("*.json"):
            try:
                orc.register(DynamicAgent(orc.llm, config_file))
            except Exception as e:
                print(f"Error loading {config_file}: {e}")

load_agents()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        load_agents()
        agent_name, _ = orc.route(req.message)
        response_text = orc.process(req.message)
        return ChatResponse(response=response_text, agent=agent_name)
    except Exception as e:
        return ChatResponse(response=f"Error: {str(e)}", agent="system")

@app.post("/clear")
def clear_history():
    orc.conversation_history = []
    return {"status": "cleared"}

@app.get("/agents")
def get_agents():
    load_agents()
    return [{"name": name, "description": agent.description} for name, agent in orc.agents.items()]

import subprocess

class CommandRequest(BaseModel):
    command: str

@app.post("/execute")
def execute_command(req: CommandRequest):
    try:
        # Clean the command: LLMs often hallucinate '$ ' or '> ' prompts
        lines = req.command.strip().split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith("$ "):
                line = line[2:]
            elif line.startswith("> "):
                line = line[2:]
            cleaned_lines.append(line)
        cmd = "\n".join(cleaned_lines)

        # Run command locally. User must approve via frontend before this hits.
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        return {"output": output.strip() or "Command executed successfully (no output)."}
    except Exception as e:
        return {"output": f"Execution failed: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
