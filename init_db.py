"""One-time script to initialise the SQLite database tables."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "pocketbuddy.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA journal_mode=WAL")

conn.executescript("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL,
  major TEXT DEFAULT '',
  year INTEGER DEFAULT 1,
  monthly_income REAL DEFAULT 0,
  daily_budget REAL DEFAULT 0,
  dietary_preferences TEXT DEFAULT '[]',
  emergency_contact TEXT DEFAULT '',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  description TEXT DEFAULT '',
  date TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS health_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  sleep_hours REAL DEFAULT 0,
  stress_level INTEGER DEFAULT 5,
  mood TEXT DEFAULT 'neutral',
  study_hours REAL DEFAULT 0,
  exercise_minutes INTEGER DEFAULT 0,
  social_activity INTEGER DEFAULT 0,
  energy_level INTEGER DEFAULT 5,
  notes TEXT DEFAULT '',
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE(user_id, date)
);

CREATE TABLE IF NOT EXISTS travel_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  origin TEXT NOT NULL,
  destination TEXT NOT NULL,
  mode TEXT NOT NULL,
  cost REAL DEFAULT 0,
  duration_minutes INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS food_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  meal_type TEXT DEFAULT 'other',
  food_name TEXT NOT NULL,
  cost REAL DEFAULT 0,
  calories INTEGER DEFAULT 0,
  is_homemade INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS burnout_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  baseline_sleep REAL DEFAULT 0,
  baseline_stress REAL DEFAULT 0,
  baseline_exercise REAL DEFAULT 0,
  current_sleep REAL DEFAULT 0,
  current_stress REAL DEFAULT 0,
  current_exercise REAL DEFAULT 0,
  score INTEGER DEFAULT 0,
  alert_level TEXT DEFAULT 'good',
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE(user_id, date)
);

CREATE TABLE IF NOT EXISTS recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  type TEXT NOT NULL,
  text TEXT NOT NULL,
  feedback TEXT DEFAULT NULL,
  was_helpful INTEGER DEFAULT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  date TEXT NOT NULL,
  user_message TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  context TEXT DEFAULT '{}',
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS routine_goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  goal_type TEXT NOT NULL,
  current_value REAL DEFAULT 0,
  target_value REAL DEFAULT 0,
  weekly_target REAL DEFAULT 0,
  week_number INTEGER DEFAULT 1,
  status TEXT DEFAULT 'active',
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS budget_meals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  cost REAL NOT NULL,
  calories INTEGER DEFAULT 0,
  category TEXT DEFAULT 'other',
  dietary_tags TEXT DEFAULT '[]',
  prep_time_minutes INTEGER DEFAULT 0,
  instructions TEXT DEFAULT '',
  is_vegetarian INTEGER DEFAULT 0,
  is_vegan INTEGER DEFAULT 0
);
""")

conn.commit()
rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables created:", [r[0] for r in rows])
conn.close()
print("Database initialised at:", DB_PATH)
