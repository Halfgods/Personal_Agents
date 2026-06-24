from ..core.agent import Agent


class MedicationAgent(Agent):
    name = "medicator"
    description = "Medication management — schedules, reminders, interactions, and tracking"

    def system_prompt(self) -> str:
        return """You are a personal medication management assistant. You help with:
- Creating medication schedules and routines
- Tracking doses and refill reminders
- Checking for potential drug interactions (general advice only)
- Organizing medication info (dosage, timing, special instructions)
- Preparing for doctor visits with medication lists

IMPORTANT: Always include a disclaimer that you are not a medical professional.
Remind users to consult their doctor or pharmacist for medical decisions."""

    def _register_tools(self) -> None:
        self.tools.append(self.make_tool(
            "save_medication_schedule",
            "Save medication schedule to file",
            self._save_schedule,
        ))

    def make_tool(self, name: str, desc: str, fn: callable):
        from ..core.agent import Tool
        return Tool(name=name, description=desc, fn=fn)

    def _save_schedule(self, schedule: str, filename: str = "medication_schedule.txt") -> str:
        from pathlib import Path
        Path(filename).write_text(schedule)
        return f"Saved to {filename}"
