from ..core.agent import Agent


class GeneralAgent(Agent):
    name = "general"
    description = "General purpose assistant for Q&A, brainstorming, writing, and everyday tasks"

    def system_prompt(self) -> str:
        return """You are a helpful personal AI assistant. You help with:
- Answering questions and explaining concepts
- Brainstorming ideas
- Writing and editing text
- Planning and organizing
- Problem solving

Be concise, practical, and friendly. If the user asks something outside your knowledge, say so clearly."""
