"""
SQLite database management module.
Uses parameterized queries to prevent SQL injection vulnerabilities.
Provides clean context manager and CRUD helper operations for events, budget, tasks, and vendors.
"""
import sqlite3
import os
from contextlib import contextmanager

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    event_date TEXT NOT NULL,
    location TEXT NOT NULL,
    guests INTEGER NOT NULL,
    budget INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'INR',
    theme TEXT,
    priorities TEXT,
    venue_type TEXT DEFAULT 'indoor',
    dietary TEXT,
    accessibility TEXT,
    notes TEXT,
    ai_source TEXT NOT NULL DEFAULT 'fallback_planner',
    plan_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    estimated_amount INTEGER NOT NULL DEFAULT 0,
    actual_amount INTEGER NOT NULL DEFAULT 0,
    priority TEXT DEFAULT 'essential',
    notes TEXT,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    is_completed INTEGER NOT NULL DEFAULT 0,
    category TEXT,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vendor_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'not_contacted',
    notes TEXT,
    estimated_cost INTEGER DEFAULT 0,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS personalized_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    rationale TEXT,
    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_budget_event ON budget_items(event_id);
CREATE INDEX IF NOT EXISTS idx_tasks_event ON tasks(event_id);
CREATE INDEX IF NOT EXISTS idx_vendors_event ON vendor_items(event_id);
CREATE INDEX IF NOT EXISTS idx_ideas_event ON personalized_ideas(event_id);
"""

class Database:
    def __init__(self, db_path="events.db"):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager providing a safe, parameterized SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initializes database schema if tables do not exist."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)

    def create_event(self, event_data):
        """Inserts a new event record using parameterized SQL."""
        query = """
        INSERT INTO events (
            name, category, event_date, location, guests, budget, currency,
            theme, priorities, venue_type, dietary, accessibility, notes,
            ai_source, plan_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            event_data.get("name", "").strip(),
            event_data.get("category", "").strip().lower(),
            event_data.get("event_date", "").strip(),
            event_data.get("location", "").strip(),
            int(event_data.get("guests", 1)),
            int(event_data.get("budget", 0)),
            event_data.get("currency", "INR").strip().upper(),
            event_data.get("theme", "").strip(),
            event_data.get("priorities", "").strip(),
            event_data.get("venue_type", "indoor").strip().lower(),
            event_data.get("dietary", "").strip(),
            event_data.get("accessibility", "").strip(),
            event_data.get("notes", "").strip(),
            event_data.get("ai_source", "fallback_planner"),
            event_data.get("plan_summary", "")
        )
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid

    def get_event(self, event_id):
        """Retrieves an event by its ID."""
        query = "SELECT * FROM events WHERE id = ?"
        with self.get_connection() as conn:
            row = conn.execute(query, (event_id,)).fetchone()
            return dict(row) if row else None

    def list_events(self):
        """Lists all events ordered by created_at desc."""
        query = "SELECT * FROM events ORDER BY created_at DESC"
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def update_event(self, event_id, event_data):
        """Updates essential and personalization fields of an event."""
        query = """
        UPDATE events SET
            name = ?, category = ?, event_date = ?, location = ?,
            guests = ?, budget = ?, currency = ?, theme = ?,
            priorities = ?, venue_type = ?, dietary = ?, accessibility = ?,
            notes = ?, plan_summary = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        params = (
            event_data.get("name", "").strip(),
            event_data.get("category", "").strip().lower(),
            event_data.get("event_date", "").strip(),
            event_data.get("location", "").strip(),
            int(event_data.get("guests", 1)),
            int(event_data.get("budget", 0)),
            event_data.get("currency", "INR").strip().upper(),
            event_data.get("theme", "").strip(),
            event_data.get("priorities", "").strip(),
            event_data.get("venue_type", "indoor").strip().lower(),
            event_data.get("dietary", "").strip(),
            event_data.get("accessibility", "").strip(),
            event_data.get("notes", "").strip(),
            event_data.get("plan_summary", ""),
            event_id
        )
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

    def delete_event(self, event_id):
        """Deletes an event and its cascaded children."""
        query = "DELETE FROM events WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.execute(query, (event_id,))
            return cursor.rowcount > 0

    # --- Budget Items CRUD ---
    def set_budget_items(self, event_id, items):
        """Replaces or initializes all budget items for an event."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM budget_items WHERE event_id = ?", (event_id,))
            for item in items:
                conn.execute("""
                INSERT INTO budget_items (event_id, category, estimated_amount, actual_amount, priority, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    item.get("category", "").strip(),
                    int(item.get("estimated_amount", 0)),
                    int(item.get("actual_amount", 0)),
                    item.get("priority", "essential"),
                    item.get("notes", "")
                ))

    def get_budget_items(self, event_id):
        """Retrieves all budget items for an event."""
        query = "SELECT * FROM budget_items WHERE event_id = ? ORDER BY id ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, (event_id,)).fetchall()
            return [dict(r) for r in rows]

    def update_budget_item(self, item_id, estimated_amount=None, actual_amount=None, notes=None):
        """Updates amounts and notes for a specific budget item."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM budget_items WHERE id = ?", (item_id,)).fetchone()
            if not row:
                return False
            curr = dict(row)
            new_est = int(estimated_amount) if estimated_amount is not None else curr["estimated_amount"]
            new_act = int(actual_amount) if actual_amount is not None else curr["actual_amount"]
            new_notes = notes if notes is not None else curr["notes"]
            conn.execute("""
            UPDATE budget_items SET estimated_amount = ?, actual_amount = ?, notes = ?
            WHERE id = ?
            """, (new_est, new_act, new_notes, item_id))
            return True

    def add_budget_item(self, event_id, category, estimated_amount=0, actual_amount=0, priority="essential", notes=""):
        """Adds a single custom budget category."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
            INSERT INTO budget_items (event_id, category, estimated_amount, actual_amount, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (event_id, category.strip(), int(estimated_amount), int(actual_amount), priority, notes))
            return cursor.lastrowid

    def delete_budget_item(self, item_id):
        """Deletes a budget item."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM budget_items WHERE id = ?", (item_id,))
            return cursor.rowcount > 0

    # --- Tasks CRUD ---
    def set_tasks(self, event_id, tasks):
        """Replaces or initializes all tasks for an event."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE event_id = ?", (event_id,))
            for t in tasks:
                conn.execute("""
                INSERT INTO tasks (event_id, title, description, due_date, priority, is_completed, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    t.get("title", "").strip(),
                    t.get("description", "").strip(),
                    t.get("due_date", "").strip(),
                    t.get("priority", "medium").lower(),
                    1 if t.get("is_completed") else 0,
                    t.get("category", "")
                ))

    def get_tasks(self, event_id):
        """Retrieves all tasks for an event ordered by due_date."""
        query = "SELECT * FROM tasks WHERE event_id = ? ORDER BY due_date ASC, id ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, (event_id,)).fetchall()
            return [dict(r) for r in rows]

    def update_task_status(self, task_id, is_completed):
        """Toggles or sets the completion status of a task."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
            UPDATE tasks SET is_completed = ? WHERE id = ?
            """, (1 if is_completed else 0, task_id))
            return cursor.rowcount > 0

    def add_task(self, event_id, title, description, due_date, priority="medium", category=""):
        """Adds a single task."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
            INSERT INTO tasks (event_id, title, description, due_date, priority, is_completed, category)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (event_id, title.strip(), description.strip(), due_date.strip(), priority.lower(), category.strip()))
            return cursor.lastrowid

    def delete_task(self, task_id):
        """Deletes a task."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    # --- Vendor Checklist CRUD ---
    def set_vendor_items(self, event_id, items):
        """Replaces or initializes vendor checklist items."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM vendor_items WHERE event_id = ?", (event_id,))
            for v in items:
                conn.execute("""
                INSERT INTO vendor_items (event_id, category, title, description, status, notes, estimated_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    v.get("category", "").strip(),
                    v.get("title", "").strip(),
                    v.get("description", "").strip(),
                    v.get("status", "not_contacted").strip().lower(),
                    v.get("notes", "").strip(),
                    int(v.get("estimated_cost", 0))
                ))

    def get_vendor_items(self, event_id):
        """Retrieves all vendor items for an event."""
        query = "SELECT * FROM vendor_items WHERE event_id = ? ORDER BY id ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, (event_id,)).fetchall()
            return [dict(r) for r in rows]

    def update_vendor_item(self, vendor_id, status=None, notes=None, estimated_cost=None):
        """Updates vendor status, notes or estimated cost."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM vendor_items WHERE id = ?", (vendor_id,)).fetchone()
            if not row:
                return False
            curr = dict(row)
            new_status = status.strip().lower() if status is not None else curr["status"]
            new_notes = notes.strip() if notes is not None else curr["notes"]
            new_cost = int(estimated_cost) if estimated_cost is not None else curr["estimated_cost"]
            conn.execute("""
            UPDATE vendor_items SET status = ?, notes = ?, estimated_cost = ?
            WHERE id = ?
            """, (new_status, new_notes, new_cost, vendor_id))
            return True

    def add_vendor_item(self, event_id, category, title, description="", status="not_contacted", notes="", estimated_cost=0):
        """Adds a custom vendor checklist item."""
        with self.get_connection() as conn:
            cursor = conn.execute("""
            INSERT INTO vendor_items (event_id, category, title, description, status, notes, estimated_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (event_id, category.strip(), title.strip(), description.strip(), status.strip().lower(), notes.strip(), int(estimated_cost)))
            return cursor.lastrowid

    def delete_vendor_item(self, vendor_id):
        """Deletes a vendor item."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM vendor_items WHERE id = ?", (vendor_id,))
            return cursor.rowcount > 0

    # --- Personalized Ideas CRUD ---
    def set_personalized_ideas(self, event_id, ideas):
        """Replaces or initializes personalized ideas."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM personalized_ideas WHERE event_id = ?", (event_id,))
            for idea in ideas:
                conn.execute("""
                INSERT INTO personalized_ideas (event_id, category, title, description, rationale)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    event_id,
                    idea.get("category", "idea").strip(),
                    idea.get("title", "").strip(),
                    idea.get("description", "").strip(),
                    idea.get("rationale", "").strip()
                ))

    def get_personalized_ideas(self, event_id):
        """Retrieves all personalized ideas for an event."""
        query = "SELECT * FROM personalized_ideas WHERE event_id = ? ORDER BY id ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, (event_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_complete_event_plan(self, event_id):
        """Retrieves full event details including budget, tasks, vendors, and ideas."""
        event = self.get_event(event_id)
        if not event:
            return None
        return {
            "event": event,
            "budget": self.get_budget_items(event_id),
            "tasks": self.get_tasks(event_id),
            "vendors": self.get_vendor_items(event_id),
            "ideas": self.get_personalized_ideas(event_id)
        }
