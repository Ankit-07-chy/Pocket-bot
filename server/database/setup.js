// ============================================================
// DATABASE SETUP - Creates all 8 tables for PocketBuddy
// ============================================================
const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

function initializeDatabase(dbPath) {
  // Make sure the directory exists
  const dir = path.dirname(dbPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const db = new Database(dbPath);

  // Enable WAL mode for better performance
  db.pragma('journal_mode = WAL');

  // ---- TABLE 1: users ----
  // Stores student profiles with their basic info and budget
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT NOT NULL,
      major TEXT DEFAULT '',
      student_type TEXT DEFAULT '',
      year INTEGER DEFAULT 1,
      monthly_income REAL DEFAULT 0,
      daily_budget REAL DEFAULT 0,
      dietary_preferences TEXT DEFAULT '[]',
      emergency_contact TEXT DEFAULT '',
      created_at TEXT DEFAULT (datetime('now'))
    )
  `);

  // Migrate existing schema if student_type is missing
  try {
    db.exec("ALTER TABLE users ADD COLUMN student_type TEXT DEFAULT ''");
  } catch (e) {
    // Column already exists, ignore
  }

  // ---- TABLE 2: expenses ----
  // Tracks every spending entry with category
  db.exec(`
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      category TEXT NOT NULL,
      description TEXT DEFAULT '',
      date TEXT NOT NULL,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // ---- TABLE 3: health_logs ----
  // Daily wellness check-in data (sleep, stress, mood, etc.)
  db.exec(`
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
    )
  `);

  // ---- TABLE 4: travel_logs ----
  // Transport tracking - where, how, and cost
  db.exec(`
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
    )
  `);

  // ---- TABLE 5: food_logs ----
  // Meal tracking with cost and nutrition info
  db.exec(`
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
    )
  `);

  // ---- TABLE 6: burnout_scores ----
  // Calculated burnout score with baseline comparison
  db.exec(`
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
    )
  `);

  // ---- TABLE 7: recommendations ----
  // AI-generated suggestions with user feedback
  db.exec(`
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
    )
  `);

  // ---- TABLE 8: chat_history ----
  // Conversation logs between user and AI support
  db.exec(`
    CREATE TABLE IF NOT EXISTS chat_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      date TEXT NOT NULL,
      user_message TEXT NOT NULL,
      ai_response TEXT NOT NULL,
      context TEXT DEFAULT '{}',
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // ---- TABLE 9: routine_goals ----
  // Wellness goals and weekly plans
  db.exec(`
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
    )
  `);

  // ---- REFERENCE TABLE: budget_meals ----
  // Static database of 200+ budget meals for recommendations
  db.exec(`
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
    )
  `);

  return db;
}

module.exports = { initializeDatabase };
