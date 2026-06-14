# PocketBuddy - Full API Test Suite
# What this does:
#   1. Seeds two realistic users into pocketbuddy.db (Alice & Bob)
#   2. Inserts 6 months of dummy expenses for each user
#   3. Runs every endpoint in main_api.py (21 routes)
#   4. Runs every /api/support/* endpoint (16 routes)
#   5. Prints a colour-coded pass/fail table with response summaries
#
# Run:
#   cd poket-bot
#   .venv\Scripts\python.exe tests\seed_and_test.py

import sys, os, json, sqlite3, hashlib, textwrap, time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "pocketbuddy.db"
sys.path.insert(0, str(ROOT / "backend" / "src"))

# ── Colour helpers ───────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✔{RESET}  {msg}")
def fail(msg):  print(f"  {RED}✗{RESET}  {msg}")
def info(msg):  print(f"  {CYAN}ℹ{RESET}  {msg}")
def header(msg):print(f"\n{BOLD}{CYAN}{'━'*70}\n  {msg}\n{'━'*70}{RESET}")

# =============================================================================
# SECTION 1 — SEED DATA
# =============================================================================

CATEGORIES = ["food", "transport", "entertainment", "education", "health", "utilities", "others"]

# Two dummy users
USERS = [
    {
        "id": 901,
        "email": "alice.test@pocketbuddy.dev",
        "name": "Alice Test",
        "major": "Computer Science",
        "year": 2,
        "monthly_income": 15000.0,
        "daily_budget": 500.0,
    },
    {
        "id": 902,
        "email": "bob.test@pocketbuddy.dev",
        "name": "Bob Test",
        "major": "Business",
        "year": 3,
        "monthly_income": 12000.0,
        "daily_budget": 400.0,
    },
]

# Monthly spending profiles (category → fraction of monthly total)
# Alice: higher spender, food-heavy
ALICE_PROFILE = {
    "food": 0.32,
    "transport": 0.12,
    "entertainment": 0.18,
    "education": 0.14,
    "health": 0.06,
    "utilities": 0.09,
    "others": 0.09,
}

# Bob: balanced spender, more on education
BOB_PROFILE = {
    "food": 0.24,
    "transport": 0.10,
    "entertainment": 0.12,
    "education": 0.22,
    "health": 0.10,
    "utilities": 0.12,
    "others": 0.10,
}

# Monthly totals (6 months back → current month)
ALICE_MONTHLY_TOTALS = [11200, 11800, 10500, 12300, 11000, 10800]  # oldest → newest prev month
BOB_MONTHLY_TOTALS   = [9500,  9800,  8700,  10200, 9600,  9200]


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def seed_database():
    header("STEP 1 — Seeding Database")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    today = datetime.now()

    for idx, user in enumerate(USERS):
        # ── Upsert user ──────────────────────────────────────────────────────
        existing = conn.execute(
            "SELECT id FROM users WHERE id = ?", (user["id"],)
        ).fetchone()

        if existing:
            conn.execute(
                "DELETE FROM expenses WHERE user_id = ?", (user["id"],)
            )
            info(f"Cleared old expenses for {user['name']}")
        else:
            conn.execute(
                """
                INSERT INTO users
                  (id, email, password, name, major, year, monthly_income, daily_budget)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user["id"],
                    user["email"],
                    _hash_password("Test@1234"),
                    user["name"],
                    user["major"],
                    user["year"],
                    user["monthly_income"],
                    user["daily_budget"],
                ),
            )
            ok(f"Created user {user['name']} (id={user['id']})")

        # ── Insert 6 months of expenses ──────────────────────────────────────
        profile  = ALICE_PROFILE  if idx == 0 else BOB_PROFILE
        totals   = ALICE_MONTHLY_TOTALS if idx == 0 else BOB_MONTHLY_TOTALS
        uid      = user["id"]
        inserted = 0

        for month_offset, monthly_total in enumerate(totals, start=1):
            # month_offset=1 → 6 months ago, month_offset=6 → last month
            target_month = today - timedelta(days=30 * (len(totals) - month_offset + 1))

            for cat, fraction in profile.items():
                amount = round(monthly_total * fraction, 2)
                # Split into 3–5 transactions per category per month
                num_tx = 3 if fraction < 0.15 else 5
                per_tx = round(amount / num_tx, 2)

                for tx_num in range(num_tx):
                    tx_day = target_month.replace(day=1) + timedelta(days=tx_num * 4 + 1)
                    # Clamp to valid month days
                    try:
                        tx_date = tx_day.strftime("%Y-%m-%d")
                    except ValueError:
                        tx_date = target_month.strftime("%Y-%m-28")

                    conn.execute(
                        """
                        INSERT INTO expenses (user_id, amount, category, description, date)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (uid, per_tx, cat, f"[seed] {cat} tx#{tx_num+1}", tx_date),
                    )
                    inserted += 1

        ok(f"Inserted {inserted} expense rows for {user['name']}")

    conn.commit()
    conn.close()
    ok("Database seed complete.")


# =============================================================================
# SECTION 2 — START FASTAPI IN-PROCESS (TestClient)
# =============================================================================

def get_test_client():
    """Boot the FastAPI app and return a TestClient."""
    header("STEP 2 — Booting FastAPI App")
    try:
        from fastapi.testclient import TestClient
        # Ensure imports resolve
        os.chdir(str(ROOT))

        # main_api.py calls setup_project_paths() at module level; we mimic that
        backend_src = str(ROOT / "backend" / "src")
        if backend_src not in sys.path:
            sys.path.insert(0, backend_src)

        # Import the app
        spec_path = str(ROOT / "backend" / "src")
        if spec_path not in sys.path:
            sys.path.insert(0, spec_path)

        # We import main_api from its actual location
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "main_api",
            str(ROOT / "backend" / "src" / "main_api.py"),
        )
        main_api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_api)

        client = TestClient(main_api.app, raise_server_exceptions=False)
        ok("FastAPI TestClient ready.")
        return client, main_api
    except Exception as e:
        fail(f"Could not boot FastAPI app: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


# =============================================================================
# SECTION 3 — TEST RUNNER
# =============================================================================

RESULTS = []   # (section, method, url, status_code, passed, note)

def run(client, method: str, url: str, section: str,
        body=None, params=None, expected=(200, 201, 207),
        note: str = ""):
    """Execute one HTTP call and record the result."""
    try:
        kwargs = {}
        if params:
            kwargs["params"] = params
        if body:
            kwargs["json"] = body

        resp = getattr(client, method.lower())(url, **kwargs)
        sc   = resp.status_code
        passed = sc in expected

        # Try to pretty-print a short summary from the JSON body
        try:
            data = resp.json()
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                summary = f"keys={keys}"
            elif isinstance(data, list):
                summary = f"list[{len(data)}]"
            else:
                summary = str(data)[:60]
        except Exception:
            summary = resp.text[:60]

        tag = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        flag = "" if passed else f"  ← expected {expected}"
        print(f"  {tag}  [{sc}]  {method.upper():6} {url}{flag}")
        if not passed:
            print(f"         response: {summary}")

        RESULTS.append((section, method.upper(), url, sc, passed, note or summary))
        return resp

    except Exception as e:
        print(f"  {RED}ERR {RESET}       {method.upper():6} {url}  → {e}")
        RESULTS.append((section, method.upper(), url, 0, False, str(e)))
        return None


# =============================================================================
# SECTION 4 — ALL TEST CASES
# =============================================================================

def run_all_tests(client, mod):
    """Run every endpoint, for both users."""

    U1 = str(USERS[0]["id"])   # "901"
    U2 = str(USERS[1]["id"])   # "902"

    # ─────────────────────────────────────────────────────────────────────────
    # 4-A  SYSTEM / HEALTH
    # ─────────────────────────────────────────────────────────────────────────
    header("4-A  System & Health")

    run(client, "GET",  "/",              "system")
    run(client, "GET",  "/health",        "system")
    run(client, "GET",  "/api/v1/status", "system")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-B  USER ONBOARDING  (new endpoint)
    # ─────────────────────────────────────────────────────────────────────────
    header("4-B  User Onboarding  POST /api/v1/onboard")

    onboard_alice = {
        "user_id": U1,
        "last_month_total": 10800,
        "last_month_category_expenses": {
            "food": 3456,
            "transport": 1296,
            "entertainment": 1944,
            "education": 1512,
            "health": 648,
            "utilities": 972,
            "others": 972,
        },
        "this_month_budget": 12000,
        "savings_target": 1200,
    }
    onboard_bob = {
        "user_id": U2,
        "last_month_total": 9200,
        "last_month_category_expenses": {
            "food": 2208,
            "transport": 920,
            "entertainment": 1104,
            "education": 2024,
            "health": 920,
            "utilities": 1104,
            "others": 920,
        },
        "this_month_budget": 10000,
        "savings_target": 0,
    }

    r_oa = run(client, "POST", "/api/v1/onboard", "onboard", body=onboard_alice)
    r_ob = run(client, "POST", "/api/v1/onboard", "onboard", body=onboard_bob)

    # Print budget plan from Alice's onboard
    if r_oa and r_oa.status_code == 200:
        plan = r_oa.json().get("budget_plan", {}).get("budget_breakdown", {})
        info(f"Alice's category budget plan → {json.dumps(plan, indent=2)}")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-C  INITIALIZE (legacy endpoint)
    # ─────────────────────────────────────────────────────────────────────────
    header("4-C  Initialize  POST /api/v1/initialize")

    run(client, "POST", "/api/v1/initialize", "initialize",
        body={"user_id": U1, "current_month_budget": 12000})
    run(client, "POST", "/api/v1/initialize", "initialize",
        body={"user_id": U2})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-D  REINITIALIZE BUDGET
    # ─────────────────────────────────────────────────────────────────────────
    header("4-D  Reinitialize Budget  POST /api/v1/reinitialize-budget")

    run(client, "POST", "/api/v1/reinitialize-budget", "reinit",
        body={"user_id": U1, "custom_budget": 13000, "savings_target": 1500})
    run(client, "POST", "/api/v1/reinitialize-budget", "reinit",
        body={"user_id": U2, "custom_budget": 9500, "savings_target": 500})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-E  EXPENSE TRACKING
    # ─────────────────────────────────────────────────────────────────────────
    header("4-E  Expense Tracking")

    today_str = datetime.now().strftime("%Y-%m-%d")

    # Add expenses for current month for both users
    expense_rows = [
        (U1, {"amount": 450.0,  "category": "food",          "description": "Grocery run",       "date": today_str}),
        (U1, {"amount": 120.0,  "category": "transport",     "description": "Metro monthly pass", "date": today_str}),
        (U1, {"amount": 800.0,  "category": "entertainment", "description": "Netflix + Spotify",  "date": today_str}),
        (U1, {"amount": 1500.0, "category": "education",     "description": "Course fee",         "date": today_str}),
        (U1, {"amount": 200.0,  "category": "health",        "description": "Pharmacy",           "date": today_str}),
        (U1, {"amount": 600.0,  "category": "utilities",     "description": "Electricity bill",   "date": today_str}),
        (U1, {"amount": 350.0,  "category": "others",        "description": "Misc",               "date": today_str}),
        (U2, {"amount": 380.0,  "category": "food",          "description": "Canteen",            "date": today_str}),
        (U2, {"amount": 90.0,   "category": "transport",     "description": "Bus pass",           "date": today_str}),
        (U2, {"amount": 500.0,  "category": "education",     "description": "Textbooks",          "date": today_str}),
        (U2, {"amount": 250.0,  "category": "health",        "description": "Doctor visit",       "date": today_str}),
        (U2, {"amount": 400.0,  "category": "utilities",     "description": "Rent share",         "date": today_str}),
    ]

    created_expense_id = None
    for uid, body in expense_rows:
        r = run(client, "POST", f"/api/v1/expenses?user_id={uid}", "expense",
                body=body, expected=(200, 201))
        if r and r.status_code in (200, 201) and created_expense_id is None and uid == U1:
            try:
                created_expense_id = r.json().get("expense_id")
            except Exception:
                pass

    # Get expenses for both users
    run(client, "GET",  f"/api/v1/expenses/{U1}", "expense")
    run(client, "GET",  f"/api/v1/expenses/{U2}", "expense")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-F  BUDGET PLAN & REMAINING
    # ─────────────────────────────────────────────────────────────────────────
    header("4-F  Budget Plan & Remaining")

    run(client, "GET",  f"/api/v1/budget-plan/{U1}",       "budget")
    run(client, "GET",  f"/api/v1/budget-plan/{U2}",       "budget")
    run(client, "GET",  f"/api/v1/remaining-budget/{U1}",  "budget")
    run(client, "GET",  f"/api/v1/remaining-budget/{U2}",  "budget")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-G  ALERTS
    # ─────────────────────────────────────────────────────────────────────────
    header("4-G  Alerts")

    r_alerts = run(client, "GET",  f"/api/v1/alerts/{U1}", "alerts")
    run(client,             "GET",  f"/api/v1/alerts/{U2}", "alerts")

    # Try to acknowledge the first alert if any exist
    if r_alerts and r_alerts.status_code == 200:
        alert_list = r_alerts.json().get("alerts", [])
        if alert_list:
            aid = alert_list[0].get("alert_id", "test-id")
            run(client, "POST", f"/api/v1/alerts/{U1}/{aid}/acknowledge", "alerts")
        else:
            info("No alerts generated yet for Alice (all within budget).")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-H  ANOMALY DETECTION
    # ─────────────────────────────────────────────────────────────────────────
    header("4-H  Anomaly Detection")

    run(client, "GET",  f"/api/v1/anomalies/{U1}", "anomalies")
    run(client, "GET",  f"/api/v1/anomalies/{U2}", "anomalies")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-I  TREND ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    header("4-I  Trend Analysis")

    run(client, "GET",  f"/api/v1/trends/monthly/{U1}",           "trends",  params={"months": 6})
    run(client, "GET",  f"/api/v1/trends/monthly/{U2}",           "trends",  params={"months": 6})
    run(client, "GET",  f"/api/v1/trends/category/{U1}/food",     "trends")
    run(client, "GET",  f"/api/v1/trends/category/{U1}/transport","trends")
    run(client, "GET",  f"/api/v1/trends/category/{U2}/education","trends")
    run(client, "GET",  f"/api/v1/trends/velocity/{U1}",          "trends")
    run(client, "GET",  f"/api/v1/trends/velocity/{U2}",          "trends")

    # Compare months (last 2 months for each user)
    now    = datetime.now()
    m_curr = now.strftime("%Y-%m")
    m_prev = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    m_prev2= (now.replace(day=1) - timedelta(days=32)).strftime("%Y-%m")

    run(client, "GET",  f"/api/v1/trends/compare",  "trends",
        params={"user_id": U1, "month1": m_prev2, "month2": m_prev})
    run(client, "GET",  f"/api/v1/trends/compare",  "trends",
        params={"user_id": U2, "month1": m_prev2, "month2": m_prev})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-J  FORECASTING
    # ─────────────────────────────────────────────────────────────────────────
    header("4-J  Forecasting")

    r_fc1 = run(client, "GET", f"/api/v1/forecast/next-month/{U1}", "forecast",
                params={"confidence": 0.85})
    r_fc2 = run(client, "GET", f"/api/v1/forecast/next-month/{U2}", "forecast",
                params={"confidence": 0.85})

    if r_fc1 and r_fc1.status_code == 200:
        fc = r_fc1.json()
        info(f"Alice forecast → total=₹{fc.get('forecasted_total',0):,.0f}  "
             f"range=[₹{fc.get('forecast_range',{}).get('low',0):,.0f} – "
             f"₹{fc.get('forecast_range',{}).get('high',0):,.0f}]")

    for cat in ["food", "transport", "education"]:
        run(client, "GET", f"/api/v1/forecast/category/{U1}/{cat}", "forecast",
            params={"months_ahead": 1})

    run(client, "GET",  f"/api/v1/forecast/seasonal/{U1}", "forecast",
        expected=(200, 201, 400))   # 400 is ok if < 4 months data
    run(client, "GET",  f"/api/v1/forecast/seasonal/{U2}", "forecast",
        expected=(200, 201, 400))

    # ─────────────────────────────────────────────────────────────────────────
    # 4-K  DASHBOARD
    # ─────────────────────────────────────────────────────────────────────────
    header("4-K  Dashboard")

    r_dash1 = run(client, "GET", f"/api/v1/dashboard/{U1}", "dashboard")
    r_dash2 = run(client, "GET", f"/api/v1/dashboard/{U2}", "dashboard")

    if r_dash1 and r_dash1.status_code == 200:
        d = r_dash1.json()
        info(f"Alice dashboard → prev_total=₹{d.get('previous_month_summary',{}).get('total_spent',0):,.0f}  "
             f"curr_total=₹{d.get('current_month_summary',{}).get('total_spent_so_far',0):,.0f}  "
             f"alerts={d.get('alert_count',0)}")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-L  PERSONALISED SUPPORT — Chat
    # ─────────────────────────────────────────────────────────────────────────
    header("4-L  Personalised Support — Chat")

    chat_msg_alice = {
        "user_id": U1,
        "message": "I've been spending a lot on food lately. What should I do?",
        "support_type": "auto",
    }
    chat_msg_bob = {
        "user_id": U2,
        "message": "How can I reduce my entertainment budget?",
        "support_type": "rule_based",
    }

    r_chat1 = run(client, "POST", "/api/support/chat", "support",
                  body=chat_msg_alice)
    r_chat2 = run(client, "POST", "/api/support/chat", "support",
                  body=chat_msg_bob)

    if r_chat1 and r_chat1.status_code == 200:
        msg = r_chat1.json().get("message", "")
        info(f"Alice chatbot reply → \"{msg[:120]}...\"" if len(msg) > 120 else f"Alice chatbot reply → \"{msg}\"")

    # Follow-up question (tests conversation memory)
    run(client, "POST", "/api/support/chat", "support", body={
        "user_id": U1,
        "message": "Can you give me 3 specific tips to save ₹500 this month on food?",
        "support_type": "ai",
    })

    # ─────────────────────────────────────────────────────────────────────────
    # 4-M  PERSONALISED SUPPORT — Context
    # ─────────────────────────────────────────────────────────────────────────
    header("4-M  Personalised Support — Context Push")

    ctx_alice = {
        "current_month_total": 4020.0,
        "previous_month_total": 10800.0,
        "budget": 12000.0,
        "budget_status": "within budget (33% used)",
        "category_spending": {"food": 450, "transport": 120, "entertainment": 800,
                               "education": 1500, "health": 200, "utilities": 600, "others": 350},
        "biggest_category": "education",
        "trend": "decreasing (-6.5% vs last month)",
    }
    run(client, "POST", f"/api/support/chat/context/{U1}", "support", body=ctx_alice)
    run(client, "POST", f"/api/support/chat/context/{U2}", "support",
        body={"current_month_total": 1620, "budget": 10000, "budget_status": "within budget (16% used)"})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-N  PERSONALISED SUPPORT — History
    # ─────────────────────────────────────────────────────────────────────────
    header("4-N  Personalised Support — Conversation History")

    run(client, "GET",  f"/api/support/chat/history/{U1}", "support", params={"limit": 20})
    run(client, "GET",  f"/api/support/chat/history/{U2}", "support", params={"limit": 20})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-O  PERSONALISED SUPPORT — Analysis & Recommendations
    # ─────────────────────────────────────────────────────────────────────────
    header("4-O  Personalised Support — Analysis & Recommendations")

    r_ana = run(client, "GET",  f"/api/support/analysis/{U1}", "support")
    run(client,         "GET",  f"/api/support/analysis/{U2}", "support")

    if r_ana and r_ana.status_code == 200:
        a = r_ana.json()
        info(f"Alice analysis → urgency={a.get('urgency_level')}  "
             f"type={a.get('recommended_support_type')}  "
             f"issues={a.get('identified_issues')}")

    run(client, "POST", f"/api/support/recommendations/{U1}", "support",
        body={"current_month_total": 4020, "budget": 12000, "trend": "decreasing"})
    run(client, "POST", f"/api/support/recommendations/{U2}", "support")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-P  PERSONALISED SUPPORT — Knowledge Base
    # ─────────────────────────────────────────────────────────────────────────
    header("4-P  Personalised Support — Knowledge Base")

    run(client, "GET",  "/api/support/knowledge/search",     "support", params={"query": "budget"})
    run(client, "GET",  "/api/support/knowledge/search",     "support", params={"query": "food spending"})
    run(client, "GET",  "/api/support/knowledge/categories", "support")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-Q  PERSONALISED SUPPORT — Peer Support
    # ─────────────────────────────────────────────────────────────────────────
    header("4-Q  Personalised Support — Peer Support")

    # Register two peers first
    run(client, "POST", "/api/support/peer/register", "support", body={
        "peer_id": "peer_001",
        "expertise_areas": ["budget", "food", "savings"],
        "languages": ["en", "hi"],
    })
    run(client, "POST", "/api/support/peer/register", "support", body={
        "peer_id": "peer_002",
        "expertise_areas": ["education", "transport", "debt"],
        "languages": ["en"],
    })

    run(client, "GET",  "/api/support/peer/available",           "support")
    run(client, "GET",  "/api/support/peer/available",           "support", params={"category": "budget"})

    run(client, "POST", "/api/support/peer/connect", "support", body={
        "user_id": U1,
        "issue_category": "budget",
        "description": "Need help managing food budget",
    })
    run(client, "POST", "/api/support/peer/connect", "support", body={
        "user_id": U2,
        "issue_category": "education",
        "description": "Trying to reduce education costs",
    })

    run(client, "GET",  "/api/support/peer/peer_001/profile",    "support")
    run(client, "GET",  "/api/support/peer/leaderboard",         "support", params={"limit": 5})

    # ─────────────────────────────────────────────────────────────────────────
    # 4-R  PERSONALISED SUPPORT — System Info
    # ─────────────────────────────────────────────────────────────────────────
    header("4-R  Personalised Support — System Info")

    run(client, "GET",  "/api/support/types",  "support")
    run(client, "GET",  "/api/support/status", "support")
    run(client, "GET",  "/api/support/health", "support")

    # ─────────────────────────────────────────────────────────────────────────
    # 4-S  DELETE (chat history cleanup)
    # ─────────────────────────────────────────────────────────────────────────
    header("4-S  Chat History Cleanup")
    run(client, "DELETE", f"/api/support/chat/history/{U1}", "support")
    run(client, "DELETE", f"/api/support/chat/history/{U2}", "support")
    # Verify history is now empty
    r_hist = run(client, "GET", f"/api/support/chat/history/{U1}", "support")
    if r_hist and r_hist.status_code == 200:
        msgs = r_hist.json().get("messages", [])
        info(f"Alice history after clear → {len(msgs)} messages (expected 0)")


# =============================================================================
# SECTION 5 — SUMMARY TABLE
# =============================================================================

def print_summary():
    header("FINAL SUMMARY")

    passed  = [r for r in RESULTS if r[4]]
    failed  = [r for r in RESULTS if not r[4]]
    total   = len(RESULTS)
    pct     = (len(passed) / total * 100) if total else 0

    # Group by section
    sections = {}
    for (sec, method, url, sc, ok_flag, note) in RESULTS:
        sections.setdefault(sec, []).append((method, url, sc, ok_flag))

    for sec, items in sections.items():
        sec_pass = sum(1 for i in items if i[3])
        sec_fail = len(items) - sec_pass
        tag = f"{GREEN}✔{RESET}" if sec_fail == 0 else f"{RED}✗{RESET}"
        print(f"  {tag}  {sec:<16}  {sec_pass}/{len(items)} passed")

    print()
    colour = GREEN if pct == 100 else (YELLOW if pct >= 70 else RED)
    print(f"  {BOLD}Total: {colour}{len(passed)}/{total}{RESET}{BOLD} passed ({pct:.1f}%){RESET}")

    if failed:
        print(f"\n  {RED}Failed endpoints:{RESET}")
        for (sec, method, url, sc, _, note) in failed:
            print(f"    [{sc}] {method:6} {url}")
            if note:
                print(f"           {note[:100]}")

    print()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(f"\n{BOLD}{CYAN}{'═'*70}")
    print("  PocketBuddy — Seed & API Test Suite")
    print(f"{'═'*70}{RESET}")
    print(f"  DB   : {DB_PATH}")
    print(f"  Users: Alice (id=901)  Bob (id=902)")
    print(f"  Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    seed_database()

    client, mod = get_test_client()

    header("STEP 3 — Running API Tests")
    run_all_tests(client, mod)

    print_summary()
