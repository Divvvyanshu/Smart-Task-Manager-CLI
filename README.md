# 📋 Smart Task Manager CLI

![CI](https://github.com/YOUR_USERNAME/task-manager-cli/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen)

A feature-rich, production-quality task manager that runs entirely in your terminal. Built with clean architecture, SQLite persistence, and a beautiful UI powered by [`rich`](https://github.com/Textualize/rich).

---

## ✨ Features

- **Add / Edit / Delete** tasks with title, description, priority, category, and due date
- **Priority levels** — 🔴 High · 🟡 Medium · 🟢 Low
- **Status tracking** — 📋 Todo → ⚡ In Progress → ✅ Done
- **Overdue detection** with visual ⚠ warnings
- **Category filtering** to focus on what matters
- **Statistics dashboard** with completion progress bar
- **SQLite persistence** — tasks survive restarts, no setup required
- **17 unit tests** covering models, CRUD, filtering, and stats

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/task-manager-cli.git
cd task-manager-cli

# 2. Install the one dependency
pip install rich

# 3. Run
python main.py
```

---

## 🎮 Menu

| Key | Action             |
|-----|--------------------|
| `1` | 📋 List all tasks  |
| `2` | ➕ Add a task       |
| `3` | ✏️ Edit a task      |
| `4` | ✅ Mark as done    |
| `5` | 🗑️ Delete a task   |
| `6` | 📊 Statistics      |
| `0` | 🚪 Exit            |

---

## 🧪 Tests

```bash
pip install pytest
pytest test_tasks.py -v
```

```
17 passed in 0.17s ✔
```

---

## 📁 Project Structure

```
task-manager-cli/
├── main.py          # Entry point & menu loop
├── cli.py           # All terminal views (Rich UI)
├── database.py      # SQLite CRUD operations
├── models.py        # Task dataclass + helpers
├── test_tasks.py    # 17 unit tests
├── requirements.txt
├── .gitignore
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml   # GitHub Actions (Python 3.9–3.12)
```

---

## 🛠 Requirements

- Python 3.9+
- [`rich`](https://pypi.org/project/rich/) >= 13.0.0

---

## 📄 License

[MIT](LICENSE)
