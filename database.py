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
    # Migration-safe: add notes and position columns if missing
    cursor = conn.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    if "notes" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
    if "position" not in columns:
        conn.execute("ALTER TABLE projects ADD COLUMN position INTEGER NOT NULL DEFAULT 0")
    # Migration-safe: add description column to features if missing
    cursor2 = conn.execute("PRAGMA table_info(features)")
    feat_columns = [row[1] for row in cursor2.fetchall()]
    if "description" not in feat_columns:
        conn.execute("ALTER TABLE features ADD COLUMN description TEXT NOT NULL DEFAULT ''")
    conn.commit()
    conn.close()


# --- Project helpers ---

def create_project(name, description="", status="idea", notes=""):
    conn = get_db()
    # Set position to max+1
    row = conn.execute("SELECT COALESCE(MAX(position), -1) + 1 AS next_pos FROM projects").fetchone()
    position = row["next_pos"]
    cur = conn.execute(
        "INSERT INTO projects (name, description, status, notes, position, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, status, notes, position, datetime.utcnow().isoformat()),
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


def get_all_projects_with_feature_counts():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*,
            COUNT(f.id) AS feature_count,
            SUM(CASE WHEN f.status = 'active' THEN 1 ELSE 0 END) AS features_active,
            SUM(CASE WHEN f.status = 'developing' THEN 1 ELSE 0 END) AS features_developing,
            SUM(CASE WHEN f.status = 'idea' THEN 1 ELSE 0 END) AS features_idea
        FROM projects p
        LEFT JOIN features f ON f.project_id = p.id
        GROUP BY p.id
        ORDER BY p.position ASC, p.created_at DESC
    """).fetchall()
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
    for key in ("name", "description", "status", "notes"):
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


def reorder_projects(order_list):
    """order_list is a list of project IDs in the desired order."""
    conn = get_db()
    for position, project_id in enumerate(order_list):
        conn.execute("UPDATE projects SET position = ? WHERE id = ?", (position, project_id))
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


def create_feature(project_id, name, status="idea", description=""):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO features (project_id, name, status, description, created_at) VALUES (?, ?, ?, ?, ?)",
        (project_id, name, status, description, datetime.utcnow().isoformat()),
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
    for key in ("name", "status", "description"):
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
