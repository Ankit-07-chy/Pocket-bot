"""
SQLite-backed expense service.
Replaces firebase_service.py — all reads and writes go through the
pocketbuddy.db SQLite database used by the Node.js server.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path


def _get_db_path() -> str:
    """Locate pocketbuddy.db relative to the project root."""
    here = Path(__file__).resolve()
    # Walk up from backend/src/expense_management/ to the project root
    for _ in range(5):
        candidate = here / "database" / "pocketbuddy.db"
        if candidate.exists():
            return str(candidate)
        here = here.parent
    # Fallback: env var or hard-coded default
    return os.getenv("SQLITE_DB_PATH", str(Path(__file__).resolve().parents[4] / "database" / "pocketbuddy.db"))


DB_PATH = _get_db_path()


def _connect() -> sqlite3.Connection:
    """Return a connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _row_to_dict(row: sqlite3.Row) -> Dict:
    return dict(row)


class SQLiteExpenseService:
    """
    Drop-in replacement for FirebaseExpenseService.

    The public interface is identical so every caller (TrendAnalyzer,
    ExpenseForecaster, AlertSystem, ExpenseInitializer, main_api) keeps
    working without further changes.
    """

    # ------------------------------------------------------------------
    # Expense reads
    # ------------------------------------------------------------------

    def get_user_expenses(self, user_id: str) -> Dict:
        """Fetch all expenses for a user, keyed by row id (str)."""
        try:
            with _connect() as conn:
                rows = conn.execute(
                    "SELECT * FROM expenses WHERE user_id = ?",
                    (user_id,)
                ).fetchall()
            return {str(r["id"]): _row_to_dict(r) for r in rows}
        except Exception as e:
            print(f"SQLite error in get_user_expenses: {e}")
            return {}

    def get_previous_month_expenses(self, user_id: str) -> Dict:
        """Fetch last month's expenses."""
        try:
            today = datetime.now()
            first_day_current = today.replace(day=1)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = last_day_previous.replace(day=1)

            with _connect() as conn:
                rows = conn.execute(
                    """
                    SELECT * FROM expenses
                    WHERE user_id = ?
                      AND date >= ?
                      AND date <= ?
                    """,
                    (user_id,
                     first_day_previous.strftime("%Y-%m-%d"),
                     last_day_previous.strftime("%Y-%m-%d"))
                ).fetchall()
            return {str(r["id"]): _row_to_dict(r) for r in rows}
        except Exception as e:
            print(f"SQLite error in get_previous_month_expenses: {e}")
            return {}

    def get_current_month_expenses(self, user_id: str) -> Dict:
        """Fetch this month's expenses."""
        try:
            first_day = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            with _connect() as conn:
                rows = conn.execute(
                    """
                    SELECT * FROM expenses
                    WHERE user_id = ?
                      AND date >= ?
                    """,
                    (user_id, first_day)
                ).fetchall()
            return {str(r["id"]): _row_to_dict(r) for r in rows}
        except Exception as e:
            print(f"SQLite error in get_current_month_expenses: {e}")
            return {}

    # ------------------------------------------------------------------
    # Expense writes
    # ------------------------------------------------------------------

    def add_expense(self, user_id: str, amount: float, category: str,
                    description: str = "", date: Optional[str] = None) -> Optional[str]:
        """Insert a new expense row. Returns the new row id as string."""
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            with _connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO expenses (user_id, amount, category, description, date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, amount, category, description, date)
                )
                conn.commit()
            return str(cur.lastrowid)
        except Exception as e:
            print(f"SQLite error in add_expense: {e}")
            return None

    # ------------------------------------------------------------------
    # Budget plan
    # ------------------------------------------------------------------

    def save_budget_plan(self, user_id: str, budget_plan: Dict) -> bool:
        """
        Persist a budget plan.
        We store it as a JSON blob in the 'recommendations' table under
        type='budget_plan', so we don't need a schema change.
        """
        try:
            import json
            payload = json.dumps({
                "plan": budget_plan,
                "created_date": datetime.now().isoformat(),
                "month": datetime.now().strftime("%Y-%m")
            })
            with _connect() as conn:
                # Upsert: delete old plan for this user-month then insert
                conn.execute(
                    """
                    DELETE FROM recommendations
                    WHERE user_id = ? AND type = 'budget_plan'
                      AND date LIKE ?
                    """,
                    (user_id, datetime.now().strftime("%Y-%m") + "%")
                )
                conn.execute(
                    """
                    INSERT INTO recommendations (user_id, date, type, text)
                    VALUES (?, ?, 'budget_plan', ?)
                    """,
                    (user_id, datetime.now().strftime("%Y-%m-%d"), payload)
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"SQLite error in save_budget_plan: {e}")
            return False

    def get_budget_plan(self, user_id: str) -> Optional[Dict]:
        """Retrieve the most recent budget plan for a user."""
        try:
            import json
            with _connect() as conn:
                row = conn.execute(
                    """
                    SELECT text FROM recommendations
                    WHERE user_id = ? AND type = 'budget_plan'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (user_id,)
                ).fetchone()
            if row:
                return json.loads(row["text"])
            return None
        except Exception as e:
            print(f"SQLite error in get_budget_plan: {e}")
            return None

    # ------------------------------------------------------------------
    # Alerts (stored in recommendations table as type='alert')
    # ------------------------------------------------------------------

    def save_alerts(self, user_id: str, alerts_dict: Dict) -> bool:
        """Persist a dict of alert objects (keyed by alert_id)."""
        try:
            import json
            with _connect() as conn:
                # Remove today's unseen alerts first
                conn.execute(
                    """
                    DELETE FROM recommendations
                    WHERE user_id = ? AND type = 'alert'
                      AND date = ?
                    """,
                    (user_id, datetime.now().strftime("%Y-%m-%d"))
                )
                for alert_id, alert_data in alerts_dict.items():
                    conn.execute(
                        """
                        INSERT INTO recommendations (user_id, date, type, text)
                        VALUES (?, ?, 'alert', ?)
                        """,
                        (user_id,
                         datetime.now().strftime("%Y-%m-%d"),
                         json.dumps({**alert_data, "alert_id": alert_id}))
                    )
                conn.commit()
            return True
        except Exception as e:
            print(f"SQLite error in save_alerts: {e}")
            return False

    def get_user_alerts(self, user_id: str) -> list:
        """Return list of alert dicts for the user."""
        try:
            import json
            with _connect() as conn:
                rows = conn.execute(
                    """
                    SELECT text FROM recommendations
                    WHERE user_id = ? AND type = 'alert'
                    ORDER BY created_at DESC
                    """,
                    (user_id,)
                ).fetchall()
            return [json.loads(r["text"]) for r in rows]
        except Exception as e:
            print(f"SQLite error in get_user_alerts: {e}")
            return []

    def acknowledge_alert(self, user_id: str, alert_id: str) -> bool:
        """Mark a specific alert as acknowledged."""
        try:
            import json
            with _connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, text FROM recommendations
                    WHERE user_id = ? AND type = 'alert'
                    """,
                    (user_id,)
                ).fetchall()
                for row in rows:
                    data = json.loads(row["text"])
                    if data.get("alert_id") == alert_id:
                        data["acknowledged"] = True
                        conn.execute(
                            "UPDATE recommendations SET text = ? WHERE id = ?",
                            (json.dumps(data), row["id"])
                        )
                conn.commit()
            return True
        except Exception as e:
            print(f"SQLite error in acknowledge_alert: {e}")
            return False
