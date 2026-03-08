import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects.db")

VALID_STATUSES = ("idea", "developing", "active")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'idea',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'idea',
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


# --- Project helpers ---

def create_project(name, description="", status="idea"):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO projects (name, description, status, created_at) VALUES (?, ?, ?, ?)",
        (name, description, status, datetime.utcnow().isoformat()),
    )
    project_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(row)


def get_all_projects():
    conn = get_db()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(project_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_project(project_id, **kwargs):
    conn = get_db()
    fields = []
    values = []
    for key in ("name", "description", "status"):
        if key in kwargs:
            fields.append(f"{key} = ?")
            values.append(kwargs[key])
    if not fields:
        conn.close()
        return None
    values.append(project_id)
    conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_project(project_id):
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()


# --- Feature helpers ---

def get_features(project_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM features WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_feature(project_id, name, status="idea"):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO features (project_id, name, status, created_at) VALUES (?, ?, ?, ?)",
        (project_id, name, status, datetime.utcnow().isoformat()),
    )
    feature_id = cur.lastrowid
    conn.commit()
    row = conn.execute("SELECT * FROM features WHERE id = ?", (feature_id,)).fetchone()
    conn.close()
    return dict(row)


def update_feature(feature_id, **kwargs):
    conn = get_db()
    fields = []
    values = []
    for key in ("name", "status"):
        if key in kwargs:
            fields.append(f"{key} = ?")
            values.append(kwargs[key])
    if not fields:
        conn.close()
        return None
    values.append(feature_id)
    conn.execute(f"UPDATE features SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    row = conn.execute("SELECT * FROM features WHERE id = ?", (feature_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_feature(feature_id):
    conn = get_db()
    conn.execute("DELETE FROM features WHERE id = ?", (feature_id,))
    conn.commit()
    conn.close()
