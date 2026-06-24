from ..core.agent import Agent


class GardenAgent(Agent):
    name = "gardener"
    description = "Garden planning, crop management, planting schedules, and plant care"

    def system_prompt(self) -> str:
        return """You are a gardening and crop planning assistant. You help with:
- Planning vegetable and flower gardens
- Creating planting schedules based on seasons
- Diagnosing plant problems (pests, diseases, nutrients)
- Soil preparation and composting advice
- Watering and fertilization schedules
- Companion planting recommendations
- Harvest timing and storage tips

Give practical, region-aware advice. Ask about the user's location and climate when relevant."""

    def _register_tools(self) -> None:
        self.tools.append(self.make_tool(
            "save_garden_plan",
            "Save a garden plan to file",
            self._save_plan,
        ))

    def make_tool(self, name: str, desc: str, fn: callable):
        from ..core.agent import Tool
        return Tool(name=name, description=desc, fn=fn)

    def _save_plan(self, plan: str, filename: str = "garden_plan.txt") -> str:
        from pathlib import Path
        Path(filename).write_text(plan)
        return f"Saved to {filename}"
