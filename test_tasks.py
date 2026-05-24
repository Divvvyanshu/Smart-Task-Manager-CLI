"""
Unit tests for Smart Task Manager.
Run with: python -m pytest test_tasks.py -v
"""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(__file__))

import database
from models import Task
import database as db

_tmp_file = None


@pytest.fixture(autouse=True)
def fresh_db():
    """Use a temp file DB and re-create schema before every test."""
    global _tmp_file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database.DB_PATH = path
    db.init_db()
    yield
    os.unlink(path)


# ── Model tests ───────────────────────────────────────────────────────────────

def test_task_defaults():
    t = Task(title="Buy milk")
    assert t.priority == 2
    assert t.status == "todo"
    assert t.category == "General"
    assert t.description == ""


def test_task_overdue_no_due_date():
    t = Task(title="No due date")
    assert t.is_overdue() is False


def test_task_overdue_past_date():
    t = Task(title="Old task", due_date="2000-01-01")
    assert t.is_overdue() is True


def test_task_overdue_done_task():
    t = Task(title="Done task", due_date="2000-01-01", status="done")
    assert t.is_overdue() is False


def test_priority_label():
    t = Task(title="X", priority=1)
    assert "High" in t.priority_label()
    t.priority = 3
    assert "Low" in t.priority_label()


def test_status_label():
    t = Task(title="X", status="in_progress")
    assert "In Progress" in t.status_label()


# ── Database tests ────────────────────────────────────────────────────────────

def test_add_and_get_task():
    task = Task(title="Write tests", priority=1)
    new_id = db.add_task(task)
    assert isinstance(new_id, int)
    fetched = db.get_task(new_id)
    assert fetched is not None
    assert fetched.title == "Write tests"
    assert fetched.priority == 1


def test_get_nonexistent_task():
    assert db.get_task(9999) is None


def test_get_all_tasks_empty():
    assert db.get_all_tasks() == []


def test_get_all_tasks():
    db.add_task(Task(title="Task A", priority=1))
    db.add_task(Task(title="Task B", priority=3))
    tasks = db.get_all_tasks()
    assert len(tasks) == 2


def test_filter_by_status():
    db.add_task(Task(title="Todo task",    status="todo"))
    db.add_task(Task(title="Done task",    status="done"))
    db.add_task(Task(title="Another done", status="done"))

    done_tasks = db.get_all_tasks(status="done")
    assert len(done_tasks) == 2

    todo_tasks = db.get_all_tasks(status="todo")
    assert len(todo_tasks) == 1


def test_filter_by_category():
    db.add_task(Task(title="Work task",    category="Work"))
    db.add_task(Task(title="Home task",    category="Home"))
    db.add_task(Task(title="Work task 2",  category="Work"))

    work_tasks = db.get_all_tasks(category="Work")
    assert len(work_tasks) == 2


def test_update_task():
    task_id = db.add_task(Task(title="Original"))
    task = db.get_task(task_id)
    task.title    = "Updated"
    task.status   = "done"
    task.priority = 1
    db.update_task(task)

    updated = db.get_task(task_id)
    assert updated.title    == "Updated"
    assert updated.status   == "done"
    assert updated.priority == 1


def test_delete_task():
    task_id = db.add_task(Task(title="To delete"))
    assert db.delete_task(task_id) is True
    assert db.get_task(task_id) is None


def test_delete_nonexistent_task():
    assert db.delete_task(9999) is False


def test_get_categories():
    db.add_task(Task(title="X", category="Alpha"))
    db.add_task(Task(title="Y", category="Beta"))
    db.add_task(Task(title="Z", category="Alpha"))
    cats = db.get_categories()
    assert "Alpha" in cats
    assert "Beta" in cats
    assert len(cats) == 2


def test_stats():
    db.add_task(Task(title="T1", status="done",        priority=1))
    db.add_task(Task(title="T2", status="todo",        priority=2))
    db.add_task(Task(title="T3", status="in_progress", priority=1))
    db.add_task(Task(title="T4", status="todo",        priority=3, category="Work"))

    s = db.get_stats()
    assert s["total"]       == 4
    assert s["done"]        == 1
    assert s["in_progress"] == 1
    assert s["todo"]        == 2
    assert s["high_priority"] == 1   # Only T3 (priority=1, not done); T1 done
