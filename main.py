#!/usr/bin/env python3
"""
╔══════════════════════════════════════╗
║        Smart Task Manager CLI        ║
║     Organize. Prioritize. Deliver.   ║
╚══════════════════════════════════════╝
"""
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

import database as db
import cli as views

console = Console()

MENU = {
    "1": ("📋  List Tasks",       views.list_tasks),
    "2": ("➕  Add Task",          views.add_task),
    "3": ("✏️   Update Task",       views.update_task),
    "4": ("✅  Mark as Done",      views.quick_done),
    "5": ("🗑️   Delete Task",       views.delete_task),
    "6": ("📊  Statistics",        views.show_stats),
    "0": ("🚪  Exit",              None),
}


def show_menu():
    lines = "\n".join(f"  [bold cyan]{k}[/]  {label}" for k, (label, _) in MENU.items())
    console.print(Panel(lines, title="[bold magenta]Smart Task Manager[/]",
                        subtitle="[dim]Your productivity hub[/]",
                        box=box.DOUBLE_EDGE, padding=(1, 4)))


def main():
    db.init_db()
    console.print("\n[bold green]Welcome to Smart Task Manager![/]\n")

    while True:
        show_menu()
        choice = Prompt.ask("[bold yellow]Choose an option[/]",
                            choices=list(MENU.keys()), default="1")

        if choice == "0":
            console.print("\n[bold cyan]Goodbye! Stay productive! 👋[/]\n")
            break

        _, action = MENU[choice]
        console.print()
        try:
            action()
        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled.[/]")
        console.print()


if __name__ == "__main__":
    main()
