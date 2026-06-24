from datetime import datetime

from ..core.agent import Agent


class ScheduleAgent(Agent):
    name = "scheduler"
    description = "Manages schedules, tasks, reminders, and calendar planning"

    def system_prompt(self) -> str:
        return f"""You are a personal schedule and task management assistant.
Current date and time: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}

You help users:
- Plan their day/week/month
- Create and organize to-do lists
- Set priorities and deadlines
- Manage appointments and events
- Break down large projects into steps

Give clear, structured responses. Use bullet points and tables when helpful."""

    def _register_tools(self) -> None:
        self.tools.append(self.make_tool(
            "save_tasks",
            "Save a task list to a file",
            self._save_tasks,
        ))

    def make_tool(self, name: str, desc: str, fn: callable):
        from ..core.agent import Tool
        return Tool(name=name, description=desc, fn=fn)

    def _save_tasks(self, tasks: str, filename: str = "tasks.txt") -> str:
        from pathlib import Path
        path = Path(filename)
        path.write_text(tasks)
        return f"Saved to {path.resolve()}"
