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
from personal_agents.demo import DemoOrchestrator, MockLLM

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backend = auto_detect_backend()
if backend == "none":
    print("Running in DEMO mode (no LLM).")
    orc = DemoOrchestrator(llm=MockLLM())
else:
    print(f"Running with backend: {backend}")
    model_default = "llama3.2:3b" if backend == "ollama" else "microsoft/Phi-3-mini-4k-instruct"
    config = LLMConfig(backend=backend, model=model_default)
    orc = Orchestrator(config=config)

orc.register(GeneralAgent(orc.llm))
orc.register(ScheduleAgent(orc.llm))
orc.register(GardenAgent(orc.llm))
orc.register(PartyAgent(orc.llm))
orc.register(MedicationAgent(orc.llm))

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent: str

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
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
    return [{"name": name, "description": agent.description} for name, agent in orc.agents.items()]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
