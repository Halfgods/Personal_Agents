"""
Demo mode — runs the agent system with mock responses.
No LLM backend needed. Shows the routing and agent architecture.
"""

import re
import random
from .cli import print_banner, print_agents, print_help
from .core.orchestrator import Orchestrator
from .core.agent import Agent
from .agents.general import GeneralAgent
from .agents.scheduler import ScheduleAgent
from .agents.gardener import GardenAgent
from .agents.party import PartyAgent
from .agents.medicator import MedicationAgent


class MockLLM:
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return self._mock_response(prompt)

    def chat(self, messages: list[dict]) -> str:
        last = messages[-1]["content"] if messages else ""
        return self._mock_response(last)

    def _mock_response(self, prompt: str) -> str:
        p = prompt.lower()
        if "garden" in p or "plant" in p or "crop" in p:
            return "gardener"
        if "schedule" in p or "task" in p or "calendar" in p or "remind" in p:
            return "scheduler"
        if "party" in p or "event" in p or "invite" in p or "celebration" in p:
            return "party"
        if "medic" in p or "pill" in p or "drug" in p or "prescription" in p or "health" in p:
            return "medicator"
        return "general"


class DemoOrchestrator(Orchestrator):
    def route(self, user_input: str) -> tuple[str, Agent | None]:
        p = user_input.lower()
        if any(w in p for w in ["garden", "plant", "crop", "seed", "soil", "compost"]):
            return "gardener", self.agents.get("gardener")
        if any(w in p for w in ["schedule", "task", "calendar", "remind", "todo", "deadline"]):
            return "scheduler", self.agents.get("scheduler")
        if any(w in p for w in ["party", "event", "invite", "celebration", "birthday", "guest"]):
            return "party", self.agents.get("party")
        if any(w in p for w in ["medic", "pill", "drug", "prescription", "health", "doctor"]):
            return "medicator", self.agents.get("medicator")
        return "general", self.agents.get("general")

    def process(self, user_input: str) -> str:
        agent_name, agent = self.route(user_input)
        responses = {
            "general": "Here's what I can tell you about that... " + (
                "I'm your general assistant! I can help with Q&A, writing, brainstorming, and more."
            ),
            "gardener": "Let me help with your garden! " + (
                "For a vegetable garden, I'd recommend starting with tomatoes, peppers, and basil. "
                "Make sure you have well-draining soil and at least 6 hours of sunlight. "
                "Would you like a detailed planting schedule or companion planting advice?"
            ),
            "scheduler": "I'll help organize your schedule! " + (
                "I can help you plan your day, set up task lists, set reminders, "
                "and break down big projects into manageable steps. "
                "What would you like to organize?"
            ),
            "party": "Let's plan an amazing party! " + (
                "I can help with guest lists, themes, menus, activities, and budgeting. "
                "What kind of event are you planning?"
            ),
            "medicator": "I'll help manage your medications! " + (
                "I can create medication schedules, set up refill reminders, "
                "and help organize your medication information. "
                "Please remember to consult your doctor for medical advice."
            ),
        }
        return responses.get(agent_name, responses["general"])


def main():
    print_banner()
    print("  DEMO MODE — No LLM backend required\n")

    orc = DemoOrchestrator(llm=MockLLM())
    orc.register(GeneralAgent(orc.llm))
    orc.register(ScheduleAgent(orc.llm))
    orc.register(GardenAgent(orc.llm))
    orc.register(PartyAgent(orc.llm))
    orc.register(MedicationAgent(orc.llm))

    print("  Try asking about any topic! Demo uses keyword routing.")
    print("  Type /help for commands.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input[1:].lower()
            if cmd == "exit":
                print("Goodbye!")
                break
            elif cmd == "help":
                print_help()
            elif cmd == "agents":
                print_agents(orc)
            else:
                print(f"  Unknown command: {cmd}")
            continue

        response = orc.process(user_input)
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    main()
