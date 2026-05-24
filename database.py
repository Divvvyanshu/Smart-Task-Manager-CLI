import sqlite3
from typing import List, Optional
from models import Task


DB_PATH = "tasks.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                description  TEXT DEFAULT '',
                priority     INTEGER DEFAULT 2,
                status       TEXT DEFAULT 'todo',
                category     TEXT DEFAULT 'General',
                due_date     TEXT,
                created_at   TEXT,
                completed_at TEXT
            )
        """)
        conn.commit()


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        priority=row["priority"],
        status=row["status"],
        category=row["category"],
        due_date=row["due_date"],
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


def add_task(task: Task) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO tasks (title, description, priority, status, category, due_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (task.title, task.description, task.priority,
             task.status, task.category, task.due_date, task.created_at),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_tasks(status: Optional[str] = None, category: Optional[str] = None) -> List[Task]:
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY priority ASC, created_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_task(r) for r in rows]


def get_task(task_id: int) -> Optional[Task]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_task(row) if row else None


def update_task(task: Task):
    with get_connection() as conn:
        conn.execute(
            """UPDATE tasks SET title=?, description=?, priority=?, status=?,
               category=?, due_date=?, completed_at=? WHERE id=?""",
            (task.title, task.description, task.priority, task.status,
             task.category, task.due_date, task.completed_at, task.id),
        )
        conn.commit()


def delete_task(task_id: int) -> bool:
    with get_connection() as conn:
        result = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return result.rowcount > 0


def get_categories() -> List[str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM tasks ORDER BY category").fetchall()
    return [r["category"] for r in rows]


def get_stats() -> dict:
    with get_connection() as conn:
        total     = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        done      = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='done'").fetchone()[0]
        in_prog   = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='in_progress'").fetchone()[0]
        todo      = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='todo'").fetchone()[0]
        high      = conn.execute("SELECT COUNT(*) FROM tasks WHERE priority=1 AND status!='done'").fetchone()[0]
        overdue   = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE due_date < date('now') AND status != 'done'"
        ).fetchone()[0]
        by_cat    = conn.execute(
            "SELECT category, COUNT(*) as cnt FROM tasks GROUP BY category ORDER BY cnt DESC"
        ).fetchall()
    return {
        "total": total, "done": done, "in_progress": in_prog,
        "todo": todo, "high_priority": high, "overdue": overdue,
        "by_category": [(r["category"], r["cnt"]) for r in by_cat],
    }
