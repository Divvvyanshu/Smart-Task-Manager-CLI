from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box

import database as db
from models import Task, PRIORITIES, STATUSES

console = Console()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _header(title: str):
    console.print(Panel(f"[bold cyan]{title}[/]", box=box.DOUBLE_EDGE, style="cyan"))


def _success(msg: str):
    console.print(f"\n[bold green]✔  {msg}[/]\n")


def _error(msg: str):
    console.print(f"\n[bold red]✘  {msg}[/]\n")


def _task_table(tasks, title="Tasks") -> Table:
    table = Table(title=title, box=box.ROUNDED, header_style="bold magenta",
                  show_lines=True, expand=True)
    table.add_column("ID",       style="dim",         width=5)
    table.add_column("Title",    style="bold white",  min_width=20)
    table.add_column("Priority", width=14)
    table.add_column("Status",   width=16)
    table.add_column("Category", style="cyan",        width=12)
    table.add_column("Due Date", width=12)

    for t in tasks:
        due_str = t.due_date or "-"
        due_style = "red bold" if t.is_overdue() else "white"
        if t.is_overdue():
            due_str += " ⚠"

        table.add_row(
            str(t.id),
            t.title,
            t.priority_label(),
            t.status_label(),
            t.category,
            Text(due_str, style=due_style),
        )
    return table


# ── Views ─────────────────────────────────────────────────────────────────────

def list_tasks():
    _header("📋  All Tasks")
    status_choice = Prompt.ask(
        "Filter by status",
        choices=["all", "todo", "in_progress", "done"],
        default="all",
    )
    cat_choice = None
    cats = db.get_categories()
    if cats:
        console.print(f"Available categories: {', '.join(cats)}")
        cat_input = Prompt.ask("Filter by category (leave blank for all)", default="")
        cat_choice = cat_input.strip() or None

    tasks = db.get_all_tasks(
        status=None if status_choice == "all" else status_choice,
        category=cat_choice,
    )
    if not tasks:
        console.print("[yellow]No tasks found.[/]")
        return
    console.print(_task_table(tasks))


def add_task():
    _header("➕  Add New Task")
    title = Prompt.ask("[bold]Title[/]")
    if not title.strip():
        _error("Title cannot be empty.")
        return
    description = Prompt.ask("Description (optional)", default="")
    priority    = IntPrompt.ask("Priority  1=High  2=Medium  3=Low", default=2)
    category    = Prompt.ask("Category", default="General")
    due_date    = Prompt.ask("Due date (YYYY-MM-DD, leave blank to skip)", default="")

    if priority not in (1, 2, 3):
        _error("Priority must be 1, 2, or 3.")
        return
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            _error("Invalid date format. Use YYYY-MM-DD.")
            return

    task = Task(
        title=title.strip(),
        description=description.strip(),
        priority=priority,
        category=category.strip(),
        due_date=due_date.strip() or None,
    )
    new_id = db.add_task(task)
    _success(f"Task #{new_id} '{task.title}' added!")


def update_task():
    _header("✏️   Update Task")
    tasks = db.get_all_tasks()
    if not tasks:
        console.print("[yellow]No tasks to update.[/]")
        return
    console.print(_task_table(tasks))

    task_id = IntPrompt.ask("Enter Task ID to update")
    task = db.get_task(task_id)
    if not task:
        _error(f"Task #{task_id} not found.")
        return

    console.print(f"\nEditing: [bold]{task.title}[/]  (press Enter to keep current value)\n")

    new_title = Prompt.ask("Title", default=task.title)
    new_desc  = Prompt.ask("Description", default=task.description or "")
    new_pri   = IntPrompt.ask("Priority  1=High  2=Medium  3=Low", default=task.priority)
    new_status = Prompt.ask(
        "Status", choices=["todo", "in_progress", "done"], default=task.status
    )
    new_cat  = Prompt.ask("Category", default=task.category)
    new_due  = Prompt.ask("Due date (YYYY-MM-DD)", default=task.due_date or "")

    if new_due:
        try:
            datetime.strptime(new_due, "%Y-%m-%d")
        except ValueError:
            _error("Invalid date format.")
            return

    task.title       = new_title.strip()
    task.description = new_desc.strip()
    task.priority    = new_pri
    task.status      = new_status
    task.category    = new_cat.strip()
    task.due_date    = new_due.strip() or None
    if new_status == "done" and not task.completed_at:
        task.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    elif new_status != "done":
        task.completed_at = None

    db.update_task(task)
    _success(f"Task #{task_id} updated!")


def delete_task():
    _header("🗑️   Delete Task")
    tasks = db.get_all_tasks()
    if not tasks:
        console.print("[yellow]No tasks to delete.[/]")
        return
    console.print(_task_table(tasks))

    task_id = IntPrompt.ask("Enter Task ID to delete")
    task = db.get_task(task_id)
    if not task:
        _error(f"Task #{task_id} not found.")
        return

    if Confirm.ask(f"Delete '[bold]{task.title}[/]'?", default=False):
        db.delete_task(task_id)
        _success(f"Task #{task_id} deleted.")
    else:
        console.print("[dim]Cancelled.[/]")


def show_stats():
    _header("📊  Statistics")
    s = db.get_stats()

    # Summary panel
    summary = (
        f"[bold]Total tasks:[/]    {s['total']}\n"
        f"[green]✅ Done:[/]          {s['done']}\n"
        f"[yellow]⚡ In Progress:[/]  {s['in_progress']}\n"
        f"[blue]📋 Todo:[/]          {s['todo']}\n"
        f"[red]🔴 High Priority:[/] {s['high_priority']}\n"
        f"[red]⚠  Overdue:[/]       {s['overdue']}\n"
    )
    console.print(Panel(summary, title="Summary", border_style="green"))

    # Completion bar
    if s["total"] > 0:
        pct = int((s["done"] / s["total"]) * 100)
        bar_len = 30
        filled  = int(bar_len * pct / 100)
        bar     = "█" * filled + "░" * (bar_len - filled)
        console.print(f"\n  Progress: [green]{bar}[/] [bold]{pct}%[/] complete\n")

    # By category
    if s["by_category"]:
        cat_table = Table(title="Tasks by Category", box=box.SIMPLE_HEAD)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Count",    style="bold white")
        for cat, cnt in s["by_category"]:
            cat_table.add_row(cat, str(cnt))
        console.print(cat_table)


def quick_done():
    """Mark a task done in one step."""
    _header("✅  Mark Task as Done")
    tasks = db.get_all_tasks()
    pending = [t for t in tasks if t.status != "done"]
    if not pending:
        console.print("[yellow]No pending tasks.[/]")
        return
    console.print(_task_table(pending, title="Pending Tasks"))

    task_id = IntPrompt.ask("Enter Task ID to mark as done")
    task = db.get_task(task_id)
    if not task:
        _error(f"Task #{task_id} not found.")
        return

    task.status       = "done"
    task.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    db.update_task(task)
    _success(f"'{task.title}' marked as done! 🎉")
