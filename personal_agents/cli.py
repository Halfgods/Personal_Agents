#!/usr/bin/env python3
import sys
from pathlib import Path

from .core.llm import LLMConfig, check_ollama, auto_detect_backend
from .core.orchestrator import Orchestrator
from .agents.general import GeneralAgent
from .agents.scheduler import ScheduleAgent
from .agents.gardener import GardenAgent
from .agents.party import PartyAgent
from .agents.medicator import MedicationAgent


def print_banner():
    print("""
  ╔══════════════════════════════════════╗
  ║     Personal AI Agent System v0.1    ║
  ║   Your personal task force of bots   ║
  ╚══════════════════════════════════════╝
    """)


def print_help():
    print("""
Commands:
  /agents      - List available agents
  /context     - Show current user context
  /context set <key>=<value> - Set context
  /model       - Show current model
  /save <file> - Save conversation to file
  /clear       - Clear conversation history
  /help        - Show this help
  /exit        - Exit

Agents:
  general    - General Q&A and everyday tasks
  scheduler  - Schedule, tasks, and calendar
  gardener   - Garden and crop planning
  party      - Party and event planning
  medicator  - Medication management

Just type your question and the system routes it to the right agent!
    """)


def print_agents(orc: Orchestrator):
    print("\nAvailable agents:")
    for name, agent in orc.agents.items():
        print(f"  {name:12s} - {agent.description}")
    print()


def save_conversation(orc: Orchestrator, filepath: str):
    lines = []
    for msg in orc.conversation_history:
        role = msg["role"].upper()
        content = msg["content"]
        lines.append(f"[{role}]")
        lines.append(content)
        lines.append("")
    Path(filepath).write_text("\n".join(lines))
    print(f"  Saved to {filepath}\n")


def main():
    print_banner()

    backend = auto_detect_backend()
    if backend == "none":
        print("  No LLM backend detected.")
        print("  Install Ollama (recommended): https://ollama.ai")
        print("  Or run: pip install transformers torch\n")
        return

    model_default = "llama3.2:3b" if backend == "ollama" else "microsoft/Phi-3-mini-4k-instruct"
    print(f"  Backend: {backend}")
    print(f"  Model:   {model_default}")
    print(f"  Type /help for commands, or start chatting!\n")

    config = LLMConfig(
        backend=backend,
        model=model_default,
    )

    orc = Orchestrator(config=config)
    orc.register(GeneralAgent(orc.llm))
    orc.register(ScheduleAgent(orc.llm))
    orc.register(GardenAgent(orc.llm))
    orc.register(PartyAgent(orc.llm))
    orc.register(MedicationAgent(orc.llm))

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
            elif cmd == "context":
                print(f"  Context: {orc.user_context}")
            elif cmd.startswith("context set "):
                rest = cmd[len("context set "):].strip()
                if "=" in rest:
                    key, val = rest.split("=", 1)
                    orc.set_context(key.strip(), val.strip())
                    print(f"  Set {key} = {val}")
                else:
                    print("  Usage: /context set key=value")
            elif cmd == "model":
                print(f"  Backend: {config.backend}, Model: {config.model}")
            elif cmd == "clear":
                orc.conversation_history = []
                print("  Conversation cleared.")
            elif cmd.startswith("save "):
                save_conversation(orc, cmd[5:].strip())
            else:
                print(f"  Unknown command: {cmd}")
            continue

        try:
            print("  Thinking...", end=" ", flush=True)
            response = orc.process(user_input)
            print("\r", end="")
            print(f"Bot: {response}\n")
        except Exception as e:
            print(f"\r  Error: {e}\n")


if __name__ == "__main__":
    main()
