"""
Full endpoint test suite for Poket Bot API.
Run: python test_endpoints.py
"""
import sqlite3, json, os, sys
from datetime import datetime, timedelta
import urllib.request
import urllib.error

BASE = "http://localhost:8000"
USER_ID = "1"  # integer FK in SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "pocketbuddy.db")

# ─── colours ────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

pass_count = fail_count = 0

def ok(label, detail=""):
    global pass_count
    pass_count += 1
    print(f"  {GREEN}PASS{RESET}  {label}" + (f"  →  {detail}" if detail else ""))

def fail(label, detail=""):
    global fail_count
    fail_count += 1
    print(f"  {RED}FAIL{RESET}  {label}" + (f"  →  {detail}" if detail else ""))

def warn(label, detail=""):
    print(f"  {YELLOW}WARN{RESET}  {label}" + (f"  →  {detail}" if detail else ""))

def section(title):
    print(f"\n{CYAN}{'─'*60}{RESET}")
    print(f"{CYAN}  {title}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")

# ─── HTTP helpers ────────────────────────────────────────────────────────────

def get(path, label=None, expect=200):
    url = BASE + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read())
            if r.status == expect:
                ok(label or path, str(body)[:120])
            else:
                fail(label or path, f"HTTP {r.status}")
            return body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        if e.code == expect:
            ok(label or path, str(body)[:120])
            return body
        fail(label or path, f"HTTP {e.code}: {body}")
        return body
    except Exception as e:
        fail(label or path, str(e))
        return {}

def post(path, data, label=None, expect=200):
    url = BASE + path
    payload = json.dumps(data).encode()
    try:
        req = urllib.request.Request(url, data=payload,
                                      headers={"Content-Type": "application/json"},
                                      method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.loads(r.read())
            if r.status == expect:
                ok(label or path, str(body)[:120])
            else:
                fail(label or path, f"HTTP {r.status}")
            return body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        if e.code == expect:
            ok(label or path, str(body)[:120])
            return body
        fail(label or path, f"HTTP {e.code}: {body}")
        return body
    except Exception as e:
        fail(label or path, str(e))
        return {}

# ─── seed data ───────────────────────────────────────────────────────────────

def seed_db():
    """Insert a test user + expenses across 3 months so all analytics work."""
    section("Seeding SQLite database")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Upsert user
    conn.execute("DELETE FROM users WHERE id = 1")
    conn.execute("""
        INSERT INTO users (id, email, password, name, monthly_income, daily_budget)
        VALUES (1, 'test@example.com', 'hashed', 'Test User', 50000, 1700)
    """)

    # Drop previous test expenses
    conn.execute("DELETE FROM expenses WHERE user_id = 1")

    today = datetime.now()
    categories = ["food", "transport", "entertainment", "health", "utilities", "education", "others"]
    amounts     = [  1200,       400,            300,     200,         500,         100,       150]

    inserted = 0
    for month_offset in range(3):          # current, -1, -2
        base = today.replace(day=1) - timedelta(days=30 * month_offset)
        for cat, amt in zip(categories, amounts):
            # Slightly vary amounts so trend/forecast have real data
            varied = round(amt * (1 + 0.05 * month_offset), 2)
            expense_date = (base + timedelta(days=5)).strftime("%Y-%m-%d")
            conn.execute(
                "INSERT INTO expenses (user_id, amount, category, description, date)"
                " VALUES (?,?,?,?,?)",
                (1, varied, cat, f"{cat} expense", expense_date)
            )
            inserted += 1

    conn.commit()
    conn.close()
    ok("seed_db", f"{inserted} expenses across 3 months")

# ─── test groups ─────────────────────────────────────────────────────────────

def test_system():
    section("System / Health")
    get("/health",        "GET /health")
    get("/",              "GET /  (root info)")
    get("/api/v1/status", "GET /api/v1/status")

def test_init():
    section("Expense Initialisation")
    r = post("/api/v1/initialize",
             {"user_id": USER_ID, "current_month_budget": 5000},
             "POST /api/v1/initialize")
    if r.get("success"):
        ok("init returned success=True")
    else:
        fail("init returned success=True", str(r))

    r2 = post("/api/v1/reinitialize-budget",
              {"user_id": USER_ID, "custom_budget": 6000, "savings_target": 500},
              "POST /api/v1/reinitialize-budget")

def test_expenses():
    section("Expense CRUD")
    r = post(f"/api/v1/expenses?user_id={USER_ID}",
             {"date": datetime.now().strftime("%Y-%m-%d"),
              "category": "food", "amount": 250, "description": "Lunch"},
             "POST /api/v1/expenses")
    get(f"/api/v1/expenses/{USER_ID}", "GET /api/v1/expenses/{user_id}")

def test_budget():
    section("Budget plan & remaining")
    get(f"/api/v1/budget-plan/{USER_ID}",     "GET /api/v1/budget-plan/{user_id}")
    get(f"/api/v1/remaining-budget/{USER_ID}", "GET /api/v1/remaining-budget/{user_id}")

def test_alerts():
    section("Alerts")
    r = get(f"/api/v1/alerts/{USER_ID}", "GET /api/v1/alerts/{user_id}")
    alerts = r.get("alerts", [])
    if alerts:
        alert_id = alerts[0].get("alert_id", "dummy")
        post(f"/api/v1/alerts/{USER_ID}/{alert_id}/acknowledge",
             {},
             "POST /api/v1/alerts/{user_id}/{alert_id}/acknowledge")
    else:
        warn("No alerts to acknowledge (spending is within budget)")

def test_trends():
    section("Trend Analysis")
    get(f"/api/v1/trends/monthly/{USER_ID}",      "GET /api/v1/trends/monthly/{user_id}")
    get(f"/api/v1/trends/category/{USER_ID}/food","GET /api/v1/trends/category/food")
    get(f"/api/v1/trends/velocity/{USER_ID}",     "GET /api/v1/trends/velocity/{user_id}")

    # compare needs ?user_id as query param
    now    = datetime.now().strftime("%Y-%m")
    prev   = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    get(f"/api/v1/trends/compare?user_id={USER_ID}&month1={prev}&month2={now}",
        "GET /api/v1/trends/compare")

def test_forecast():
    section("Forecasting")
    get(f"/api/v1/forecast/next-month/{USER_ID}",          "GET /api/v1/forecast/next-month")
    get(f"/api/v1/forecast/category/{USER_ID}/food",        "GET /api/v1/forecast/category/food")
    get(f"/api/v1/forecast/seasonal/{USER_ID}",             "GET /api/v1/forecast/seasonal")
    get(f"/api/v1/anomalies/{USER_ID}",                     "GET /api/v1/anomalies")

def test_dashboard():
    section("Dashboard")
    r = get(f"/api/v1/dashboard/{USER_ID}", "GET /api/v1/dashboard/{user_id}")
    expected_keys = ["previous_month_summary","current_month_summary",
                     "budget_plan","alerts","remaining_budget"]
    missing = [k for k in expected_keys if k not in r]
    if not missing:
        ok("dashboard has all expected keys")
    else:
        fail("dashboard missing keys", str(missing))

def test_support_system():
    section("Personalised Support — system")
    get("/api/support/health",   "GET /api/support/health")
    get("/api/support/status",   "GET /api/support/status")
    get("/api/support/types",    "GET /api/support/types")

def test_support_knowledge():
    section("Personalised Support — knowledge base")
    get("/api/support/knowledge/categories",           "GET /api/support/knowledge/categories")
    get("/api/support/knowledge/search?query=budget",  "GET /api/support/knowledge/search")

def test_support_chat():
    section("Personalised Support — chat (LLM)")
    # Push context first
    ctx = {
        "current_month_total": 2800,
        "previous_month_total": 2600,
        "budget": 5000,
        "budget_status": "within budget (56% used)",
        "category_spending": {"food": 1200, "transport": 400, "entertainment": 300},
        "biggest_category": "food",
        "trend": "stable (+7.7% vs last month)"
    }
    post(f"/api/support/chat/context/{USER_ID}", ctx,
         "POST /api/support/chat/context/{user_id}")

    # AI chat
    r = post("/api/support/chat",
             {"user_id": USER_ID,
              "message": "I spend a lot on food. Any tips to reduce it?",
              "support_type": "ai"},
             "POST /api/support/chat (AI)")
    if r.get("message"):
        ok("AI response received", r["message"][:100])
    else:
        fail("AI response empty", str(r))

    # Rule-based chat
    r2 = post("/api/support/chat",
              {"user_id": USER_ID,
               "message": "How do I create a budget?",
               "support_type": "rule_based"},
              "POST /api/support/chat (rule-based)")

    # Auto mode
    post("/api/support/chat",
         {"user_id": USER_ID,
          "message": "What is the 50/30/20 budget rule?",
          "support_type": "auto"},
         "POST /api/support/chat (auto)")

def test_support_history():
    section("Personalised Support — history & analysis")
    get(f"/api/support/chat/history/{USER_ID}",  "GET /api/support/chat/history")
    get(f"/api/support/analysis/{USER_ID}",       "GET /api/support/analysis")
    post(f"/api/support/recommendations/{USER_ID}",
         {"current_month_total": 2800, "budget": 5000},
         "POST /api/support/recommendations")

def test_peer_support():
    section("Personalised Support — peer support")
    # Register a peer (JSON body)
    r = post("/api/support/peer/register",
             {"peer_id": "peer_001",
              "expertise_areas": ["budgeting", "savings"],
              "languages": ["en"]},
             "POST /api/support/peer/register")

    get("/api/support/peer/available",         "GET /api/support/peer/available")
    get("/api/support/peer/leaderboard",        "GET /api/support/peer/leaderboard")

    r2 = post("/api/support/peer/connect",
              {"user_id": USER_ID, "issue_category": "budgeting", "description": "Need help"},
              "POST /api/support/peer/connect")

    get("/api/support/peer/peer_001/profile",  "GET /api/support/peer/{peer_id}/profile")

# ─── main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(" POKET BOT — FULL API TEST SUITE")
    print(f"{'='*60}")

    seed_db()
    test_system()
    test_init()
    test_expenses()
    test_budget()
    test_alerts()
    test_trends()
    test_forecast()
    test_dashboard()
    test_support_system()
    test_support_knowledge()
    test_support_chat()
    test_support_history()
    test_peer_support()

    # Clean up history
    section("Cleanup")
    req = urllib.request.Request(
        f"{BASE}/api/support/chat/history/{USER_ID}",
        method="DELETE"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            ok("DELETE /api/support/chat/history")
    except Exception as e:
        warn("DELETE /api/support/chat/history", str(e))

    print(f"\n{'='*60}")
    print(f"  Results: {GREEN}{pass_count} passed{RESET}  |  {RED}{fail_count} failed{RESET}")
    print(f"{'='*60}\n")

    sys.exit(0 if fail_count == 0 else 1)
