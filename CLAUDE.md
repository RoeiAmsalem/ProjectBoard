# CLAUDE.md — ProjectBoard

## What is this project?
A personal web app to centralize and track all project ideas.
Built by Roei Amsalem. Runs locally on localhost:5001.

---

## Stack
- **Backend:** Python + Flask
- **Database:** SQLite (projects.db)
- **Frontend:** Plain HTML + CSS + vanilla JavaScript (no frameworks)
- **Tests:** pytest

---

## Project Structure
```
ProjectBoard/
├── app.py              ← Flask app + all routes
├── database.py         ← DB init + helper functions
├── test_app.py         ← pytest tests
├── projects.db         ← SQLite DB (auto-created)
├── templates/
│   └── index.html      ← Single-page UI
├── static/
│   └── style.css       ← All styles
└── CLAUDE.md           ← This file
```

---

## Database Schema

### projects
| Column      | Type    | Notes                          |
|-------------|---------|--------------------------------|
| id          | INTEGER | Primary key, autoincrement     |
| name        | TEXT    | Project name                   |
| description | TEXT    | One-line description           |
| status      | TEXT    | idea / developing / active     |
| created_at  | TEXT    | ISO timestamp                  |

### features
| Column     | Type    | Notes                          |
|------------|---------|--------------------------------|
| id         | INTEGER | Primary key, autoincrement     |
| project_id | INTEGER | FK → projects.id               |
| name       | TEXT    | Feature name                   |
| status     | TEXT    | idea / developing / active     |
| created_at | TEXT    | ISO timestamp                  |

---

## Status Color System
| Status     | Color  |
|------------|--------|
| idea       | Red    |
| developing | Yellow |
| active     | Green  |

This applies to both projects (squares) and features (dots).

---

## API Routes
| Method | Route                        | Description                        |
|--------|------------------------------|------------------------------------|
| GET    | /                            | Render main page                   |
| POST   | /projects                    | Create new project                 |
| PATCH  | /projects/<id>               | Edit project (name/desc/status)    |
| DELETE | /projects/<id>               | Delete project + cascade features  |
| GET    | /projects/<id>/features      | Get all features for a project     |
| POST   | /projects/<id>/features      | Add feature to project             |
| PATCH  | /features/<id>               | Edit feature (name/status)         |
| DELETE | /features/<id>               | Delete feature                     |

---

## How to Run
```bash
cd /Users/roei_amsalem/Desktop/ProjectBoard
python app.py
# App runs on http://localhost:5001
```

## How to Test
```bash
cd /Users/roei_amsalem/Desktop/ProjectBoard
pytest test_app.py -v
```

---

## Rules for Claude Code
1. Always read this file before starting any task
2. Never change the port — always localhost:5001
3. All API routes return JSON
4. Deleting a project must cascade-delete its features
5. No CSS frameworks — plain CSS only
6. Every new feature needs a test in test_app.py
7. Always commit when done with a clear message
8. Fix root causes, not symptoms
