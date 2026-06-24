from ..core.agent import Agent


class PartyAgent(Agent):
    name = "party"
    description = "Party and event planning — invites, guest lists, themes, menus, and activities"

    def system_prompt(self) -> str:
        return """You are a party and event planning assistant. You help with:
- Guest lists and invite management
- Party themes and decoration ideas
- Menu planning (including dietary restrictions)
- Activity and entertainment coordination
- Budget planning and tracking
- Timeline and preparation checklists
- Venue selection and setup

Be creative and organized. Help the user think through all the details."""

    def _register_tools(self) -> None:
        self.tools.append(self.make_tool(
            "save_party_plan",
            "Save a party plan to file",
            self._save_plan,
        ))

    def make_tool(self, name: str, desc: str, fn: callable):
        from ..core.agent import Tool
        return Tool(name=name, description=desc, fn=fn)

    def _save_plan(self, plan: str, filename: str = "party_plan.txt") -> str:
        from pathlib import Path
        Path(filename).write_text(plan)
        return f"Saved to {filename}"
