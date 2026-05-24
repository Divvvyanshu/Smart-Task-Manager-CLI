from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


PRIORITIES = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}
STATUSES = {"todo": "📋 Todo", "in_progress": "⚡ In Progress", "done": "✅ Done"}


@dataclass
class Task:
    title: str
    description: str = ""
    priority: int = 2          # 1=High, 2=Medium, 3=Low
    status: str = "todo"       # todo | in_progress | done
    category: str = "General"
    due_date: Optional[str] = None
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    completed_at: Optional[str] = None

    def priority_label(self) -> str:
        return PRIORITIES.get(self.priority, "🟡 Medium")

    def status_label(self) -> str:
        return STATUSES.get(self.status, "📋 Todo")

    def is_overdue(self) -> bool:
        if not self.due_date or self.status == "done":
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            return due < datetime.now()
        except ValueError:
            return False
