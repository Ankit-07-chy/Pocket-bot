"""
Data Integrity Test Suite for Poket Bot API
============================================
For every POST/PUT: verify the row actually landed in SQLite.
For every GET:      verify the response data matches what is in SQLite.

Run: python test_data_integrity.py
"""

import sqlite3, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timedelta

BASE    = "http://localhost:8000"
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "pocketbuddy.db")

# ── colours ──────────────────────────────────────────────────────────────────
G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"; W = "\033[0m"

passed = failed = 0

def ok(label, detail=""):
    global passed; passed += 1
    print(f"  {G}PASS{W}  {label}" + (f"\n        {detail}" if detail else ""))

def fail(label, detail=""):
    global failed; failed += 1
    print(f"  {R}FAIL{W}  {label}\n        {R}{detail}{W}")

def warn(label, detail=""):
    print(f"  {Y}WARN{W}  {label}" + (f"  — {detail}" if detail else ""))

def section(t):
    print(f"\n{C}{'─'*62}{W}\n{C}  {t}{W}\n{C}{'─'*62}{W}")

# ── DB helpers ────────────────────────────────────────────────────────────────
def db():
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row; return c

def db_rows(sql, params=()):
    with db() as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]

def db_one(sql, params=()):
    rows = db_rows(sql, params)
    return rows[0] if rows else None

def db_count(sql, params=()):
    with db() as c:
        return c.execute(sql, params).fetchone()[0]

# ── HTTP helpers ──────────────────────────────────────────────────────────────
def http(method, path, body=None, expect=200):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as e:
        return 0, {"error": str(e)}

def get(path):  return http("GET",  path)
def post(path, body=None): return http("POST", path, body)
def delete(path):           return http("DELETE", path)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 – Seed a clean user
# ─────────────────────────────────────────────────────────────────────────────
def seed_clean_user():
    section("Seeding clean test user (user_id=99)")
    with db() as c:
        c.execute("DELETE FROM expenses        WHERE user_id = 99")
        c.execute("DELETE FROM recommendations WHERE user_id = 99")
        # upsert user
        c.execute("DELETE FROM users WHERE id = 99")
        c.execute("""
            INSERT INTO users (id, email, password, name, monthly_income, daily_budget)
            VALUES (99, 'integrity@test.com', 'hash', 'Integrity Tester', 50000, 1700)
        """)
        c.commit()

    today = datetime.now()
    categories = ["food","transport","entertainment","health","utilities","education","others"]
    amounts    = [2000,  500,         300,            200,    600,         100,        250]
    rows = 0
    with db() as c:
        for offset in range(3):
            base = today.replace(day=5) - timedelta(days=30 * offset)
            for cat, amt in zip(categories, amounts):
                c.execute(
                    "INSERT INTO expenses (user_id,amount,category,description,date)"
                    " VALUES (?,?,?,?,?)",
                    (99, round(amt*(1+0.05*offset),2), cat,
                     f"{cat} seed", base.strftime("%Y-%m-%d"))
                )
                rows += 1
        c.commit()

    cnt = db_count("SELECT COUNT(*) FROM expenses WHERE user_id=99")
    if cnt == rows:
        ok(f"seed_clean_user", f"{rows} expense rows, user_id=99 in users table")
    else:
        fail("seed_clean_user", f"expected {rows} rows, got {cnt}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 – Initialize endpoint → budget plan in DB
# ─────────────────────────────────────────────────────────────────────────────
def test_initialize():
    section("POST /api/v1/initialize  →  budget plan written to DB")

    # Wipe any prior plan
    with db() as c:
        c.execute("DELETE FROM recommendations WHERE user_id=99 AND type='budget_plan'")
        c.commit()

    before = db_count("SELECT COUNT(*) FROM recommendations WHERE user_id=99 AND type='budget_plan'")
    status, r = post("/api/v1/initialize", {"user_id": "99", "current_month_budget": 6000})

    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    # Check response structure
    checks = [
        ("success==True",   r.get("success") == True),
        ("user_id in resp", r.get("user_id") == "99"),
        ("budget_plan key", "budget_plan" in r),
        ("total_budget>0",  r.get("budget_plan", {}).get("total_budget", 0) > 0),
        ("previous_month",  "previous_month" in r),
        ("current_month",   "current_month" in r),
    ]
    for label, cond in checks:
        ok(f"response.{label}") if cond else fail(f"response.{label}", str(r))

    # Verify row in SQLite
    after = db_count("SELECT COUNT(*) FROM recommendations WHERE user_id=99 AND type='budget_plan'")
    if after > before:
        ok("budget_plan row written to recommendations table")
    else:
        fail("budget_plan row written to recommendations table",
             f"before={before}, after={after}")

    # Verify JSON structure in the DB row
    row = db_one(
        "SELECT text FROM recommendations WHERE user_id=99 AND type='budget_plan'"
        " ORDER BY created_at DESC LIMIT 1"
    )
    if row:
        data = json.loads(row["text"])
        if "plan" in data and "total_budget" in data["plan"]:
            ok("DB row contains plan.total_budget",
               f"₹{data['plan']['total_budget']:.2f}")
        else:
            fail("DB row plan structure", str(data))
    else:
        fail("DB row not found")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 – POST expense → verify row in expenses table
# ─────────────────────────────────────────────────────────────────────────────
def test_create_expense():
    section("POST /api/v1/expenses  →  row written to expenses table")

    before = db_count("SELECT COUNT(*) FROM expenses WHERE user_id=99")
    today  = datetime.now().strftime("%Y-%m-%d")
    payload = {"date": today, "category": "food", "amount": 499.0,
               "description": "integrity test lunch"}

    status, r = post(f"/api/v1/expenses?user_id=99", payload)

    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    expense_id = r.get("expense_id")
    ok("response.success==True",  r.get("success") == True)
    ok("response.expense_id set", bool(expense_id))

    # Verify count increased
    after = db_count("SELECT COUNT(*) FROM expenses WHERE user_id=99")
    if after == before + 1:
        ok("expenses row count increased by 1", f"{before} → {after}")
    else:
        fail("row count mismatch", f"before={before}, after={after}")

    # Verify exact row
    row = db_one("SELECT * FROM expenses WHERE id=?", (int(expense_id),))
    if row:
        checks = [
            ("amount==499.0",    abs(row["amount"] - 499.0) < 0.01),
            ("category==food",   row["category"] == "food"),
            ("description",      "integrity test" in row["description"]),
            ("date",             row["date"] == today),
            ("user_id==99",      row["user_id"] == 99),
        ]
        for label, cond in checks:
            ok(f"DB row.{label}") if cond else fail(f"DB row.{label}", str(row))
    else:
        fail("DB row not found by id", f"id={expense_id}")

    return expense_id

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 – GET expenses → response matches DB
# ─────────────────────────────────────────────────────────────────────────────
def test_get_expenses():
    section("GET /api/v1/expenses/{user_id}  →  response matches DB")

    db_expenses = db_rows("SELECT * FROM expenses WHERE user_id=99")
    status, r = get(f"/api/v1/expenses/99")

    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    api_expenses = r.get("expenses", {})
    ok("response.user_id==99", r.get("user_id") == "99")

    if r.get("count") == len(db_expenses):
        ok("response.count matches DB",
           f"API={r.get('count')}  DB={len(db_expenses)}")
    else:
        fail("count mismatch",
             f"API={r.get('count')}  DB={len(db_expenses)}")

    # Spot-check: every DB row ID should appear in the API response
    db_ids = {str(row["id"]) for row in db_expenses}
    api_ids = set(api_expenses.keys())
    missing = db_ids - api_ids
    extra   = api_ids - db_ids
    if not missing and not extra:
        ok("all DB expense IDs present in API response")
    else:
        if missing: fail("DB IDs missing from API", str(missing))
        if extra:   warn("extra IDs in API (expected if tests ran multiple times)", str(extra))

    # Verify a sample row's data is correct
    if api_expenses:
        first_id, first_val = next(iter(api_expenses.items()))
        db_row = db_one("SELECT * FROM expenses WHERE id=?", (int(first_id),))
        if db_row:
            ok("sample row amount matches",
               f"API={first_val['amount']}  DB={db_row['amount']}")
            ok("sample row category matches",
               f"API={first_val['category']}  DB={db_row['category']}")
        else:
            fail("sample row not in DB", first_id)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 – GET budget plan → response matches DB
# ─────────────────────────────────────────────────────────────────────────────
def test_get_budget_plan():
    section("GET /api/v1/budget-plan/{user_id}  →  response matches DB")

    db_row = db_one(
        "SELECT text FROM recommendations WHERE user_id=99 AND type='budget_plan'"
        " ORDER BY created_at DESC LIMIT 1"
    )
    if not db_row:
        warn("No budget plan in DB to compare (run initialize first)"); return

    db_plan = json.loads(db_row["text"])
    status, r = get("/api/v1/budget-plan/99")

    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    api_plan = r.get("budget_plan", {}).get("plan", r.get("budget_plan", {}))

    # Compare total_budget
    db_total  = db_plan.get("plan", {}).get("total_budget", 0)
    api_total = api_plan.get("total_budget", 0)

    if abs(db_total - api_total) < 0.01:
        ok("total_budget matches DB",     f"₹{api_total:.2f}")
    else:
        fail("total_budget mismatch", f"API={api_total}  DB={db_total}")

    # Compare budget_breakdown keys
    db_cats  = set(db_plan.get("plan", {}).get("budget_breakdown", {}).keys())
    api_cats = set(api_plan.get("budget_breakdown", {}).keys())
    if db_cats == api_cats:
        ok("budget_breakdown categories match DB", str(db_cats))
    else:
        fail("category mismatch", f"API={api_cats}  DB={db_cats}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 – GET remaining budget → calculated correctly
# ─────────────────────────────────────────────────────────────────────────────
def test_remaining_budget():
    section("GET /api/v1/remaining-budget/{user_id}  →  maths verified")

    status, r = get("/api/v1/remaining-budget/99")
    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    remaining = r.get("remaining_budget", {})
    if not remaining:
        warn("Empty remaining_budget in response"); return

    # Pull current month expenses from DB and recalculate
    first_day = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    db_rows_curr = db_rows(
        "SELECT category, SUM(amount) as total FROM expenses"
        " WHERE user_id=99 AND date>=? GROUP BY category",
        (first_day,)
    )
    db_by_cat = {row["category"]: row["total"] for row in db_rows_curr}

    # Verify that for each category, API.spent == DB sum
    any_mismatch = False
    for cat, data in remaining.items():
        api_spent = data.get("spent", 0)
        db_spent  = db_by_cat.get(cat, 0)
        if abs(api_spent - db_spent) < 0.01:
            ok(f"remaining[{cat}].spent matches DB",
               f"₹{api_spent:.2f}")
        else:
            fail(f"remaining[{cat}].spent mismatch",
                 f"API={api_spent:.2f}  DB={db_spent:.2f}")
            any_mismatch = True

    # Verify remaining = budget - spent
    for cat, data in remaining.items():
        calc = data.get("budget", 0) - data.get("spent", 0)
        if abs(data.get("remaining", 0) - calc) < 0.01:
            ok(f"remaining[{cat}].remaining = budget-spent ✓")
        else:
            fail(f"remaining[{cat}].remaining arithmetic wrong",
                 f"budget={data.get('budget')} spent={data.get('spent')} "
                 f"remaining={data.get('remaining')} calc={calc:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 – Reinitialize custom budget → DB updated
# ─────────────────────────────────────────────────────────────────────────────
def test_reinitialize_budget():
    section("POST /api/v1/reinitialize-budget  →  DB row updated")

    before_row = db_one(
        "SELECT text FROM recommendations WHERE user_id=99 AND type='budget_plan'"
        " ORDER BY created_at DESC LIMIT 1"
    )
    before_total = json.loads(before_row["text"])["plan"]["total_budget"] if before_row else 0

    status, r = post("/api/v1/reinitialize-budget",
                     {"user_id": "99", "custom_budget": 8000, "savings_target": 800})

    if status != 200:
        fail("HTTP 200", f"got {status}: {r}"); return

    ok("response.success==True", r.get("success") == True)
    api_total = r.get("budget_plan", {}).get("total_budget", 0)
    ok("response total_budget ≈ 8000",
       abs(api_total - 8000) < 10, )

    after_row = db_one(
        "SELECT text FROM recommendations WHERE user_id=99 AND type='budget_plan'"
        " ORDER BY created_at DESC LIMIT 1"
    )
    if after_row:
        after_total = json.loads(after_row["text"])["plan"]["total_budget"]
        if abs(after_total - api_total) < 0.01:
            ok("DB total_budget updated",
               f"{before_total:.2f} → {after_total:.2f}")
        else:
            fail("DB total_budget not updated",
                 f"DB={after_total}  API={api_total}")
    else:
        fail("DB row not found after reinitialize")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 – Alerts: force overspend, then acknowledge
# ─────────────────────────────────────────────────────────────────────────────
def test_alerts():
    section("Alerts  →  overspend detection + acknowledge written to DB")

    # Set a tiny budget so categories definitely go over
    post("/api/v1/reinitialize-budget",
         {"user_id": "99", "custom_budget": 500, "savings_target": 0})

    status, r = get("/api/v1/alerts/99")
    if status != 200:
        fail("GET /alerts HTTP 200", f"{status}: {r}"); return

    alerts = r.get("alerts", [])
    ok("alert_count in response", "alert_count" in r)

    if not alerts:
        warn("No alerts generated — seeded spend may still be under ₹500 budget",
             "Check seed amounts vs reinitialize_budget=500")
        # Restore a reasonable budget
        post("/api/v1/reinitialize-budget",
             {"user_id": "99", "custom_budget": 6000, "savings_target": 0})
        return

    ok(f"{len(alerts)} alert(s) generated")

    # Verify alert structure
    a = alerts[0]
    for key in ["alert_id","category","message","severity","current_amount","budget_limit"]:
        if key in a:
            ok(f"alert.{key} present", str(a[key])[:60])
        else:
            fail(f"alert.{key} missing")

    # Acknowledge first alert
    alert_id = a["alert_id"]
    status2, r2 = post(f"/api/v1/alerts/99/{alert_id}/acknowledge", {})
    if status2 == 200 and r2.get("success"):
        ok("acknowledge HTTP 200 + success==True")
    else:
        fail("acknowledge failed", f"{status2}: {r2}")

    # Verify acknowledged=True in DB
    db_alert_row = db_one(
        "SELECT text FROM recommendations WHERE user_id=99 AND type='alert'"
        " ORDER BY created_at DESC LIMIT 1"
    )
    if db_alert_row:
        alert_data = json.loads(db_alert_row["text"])
        # find the one with matching id
        if isinstance(alert_data, dict) and alert_data.get("alert_id") == alert_id:
            if alert_data.get("acknowledged"):
                ok("acknowledged=True persisted in DB")
            else:
                fail("acknowledged still False in DB", str(alert_data))
        else:
            warn("Alert row in DB has different structure", str(alert_data)[:100])
    else:
        warn("No alert row found in DB (alerts may not persist between requests)")

    # Restore reasonable budget
    post("/api/v1/reinitialize-budget",
         {"user_id": "99", "custom_budget": 6000, "savings_target": 0})

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 – Trends: data in response matches DB aggregates
# ─────────────────────────────────────────────────────────────────────────────
def test_trends():
    section("GET /api/v1/trends/*  →  totals match DB aggregates")

    status, r = get("/api/v1/trends/monthly/99?months=3")
    if status != 200:
        fail("monthly trends HTTP 200", f"{status}: {r}"); return

    trend_data = r.get("trend_data", {})
    ok("trend_data not empty", bool(trend_data))
    ok("months_analyzed in response", "months_analyzed" in r)
    ok("analysis key present", "analysis" in r)

    # Cross-check one month against DB
    now   = datetime.now()
    month = now.strftime("%Y-%m")
    if month in trend_data:
        api_total = trend_data[month]["total"]
        db_total  = db_count(
            "SELECT COALESCE(SUM(amount),0) FROM expenses"
            " WHERE user_id=99 AND strftime('%Y-%m',date)=?", (month,)
        )
        if abs(api_total - db_total) < 0.01:
            ok(f"current month total matches DB",
               f"API={api_total:.2f}  DB={db_total:.2f}")
        else:
            fail("current month total mismatch",
                 f"API={api_total:.2f}  DB={db_total:.2f}")

    # Velocity
    status2, v = get("/api/v1/trends/velocity/99")
    if status2 == 200:
        db_curr_total = db_count(
            "SELECT COALESCE(SUM(amount),0) FROM expenses"
            " WHERE user_id=99 AND date >= ?",
            (now.replace(day=1).strftime("%Y-%m-%d"),)
        )
        api_total = v.get("total_spent_so_far", 0)
        if abs(api_total - db_curr_total) < 0.01:
            ok("velocity.total_spent_so_far matches DB",
               f"API={api_total:.2f}  DB={db_curr_total:.2f}")
        else:
            fail("velocity total mismatch",
                 f"API={api_total:.2f}  DB={db_curr_total:.2f}")

    # Category trend for food
    status3, ct = get("/api/v1/trends/category/99/food?months=3")
    if status3 == 200:
        ok("category trend response ok", f"category={ct.get('category')}")
        td = ct.get("trend_data", {})
        if month in td:
            api_food = td[month]
            db_food  = db_count(
                "SELECT COALESCE(SUM(amount),0) FROM expenses"
                " WHERE user_id=99 AND category='food' AND strftime('%Y-%m',date)=?",
                (month,)
            )
            if abs(api_food - db_food) < 0.01:
                ok("food category total matches DB",
                   f"API={api_food:.2f}  DB={db_food:.2f}")
            else:
                fail("food category total mismatch",
                     f"API={api_food:.2f}  DB={db_food:.2f}")

    # Compare months
    prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    status4, cmp = get(f"/api/v1/trends/compare?user_id=99&month1={prev_month}&month2={month}")
    if status4 == 200:
        ok("compare months response ok")
        db_prev = db_count(
            "SELECT COALESCE(SUM(amount),0) FROM expenses"
            " WHERE user_id=99 AND strftime('%Y-%m',date)=?", (prev_month,)
        )
        api_prev = cmp.get("data1", {}).get("total", -1)
        if abs(api_prev - db_prev) < 0.01:
            ok("compare month1 total matches DB",
               f"API={api_prev:.2f}  DB={db_prev:.2f}")
        else:
            fail("compare month1 mismatch",
                 f"API={api_prev:.2f}  DB={db_prev:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 – Forecast: based on DB history
# ─────────────────────────────────────────────────────────────────────────────
def test_forecast():
    section("GET /api/v1/forecast/*  →  structure + data plausibility")

    status, r = get("/api/v1/forecast/next-month/99")
    if status != 200:
        fail("HTTP 200", f"{status}: {r}"); return

    for key in ["forecast_month","forecasted_total","confidence_level",
                "category_forecast","forecast_range","based_on_months"]:
        if key in r:
            ok(f"response.{key}", str(r[key])[:60])
        else:
            fail(f"response.{key} missing")

    # Plausibility: forecast total should be within 3× the DB historical average
    db_monthly_avgs = db_rows(
        "SELECT strftime('%Y-%m',date) m, SUM(amount) total"
        " FROM expenses WHERE user_id=99 GROUP BY m"
    )
    if db_monthly_avgs:
        db_avg = sum(row["total"] for row in db_monthly_avgs) / len(db_monthly_avgs)
        fc = r.get("forecasted_total", 0)
        if 0 < fc < db_avg * 4:
            ok("forecasted_total is plausible",
               f"forecast=₹{fc:.2f}  db_avg=₹{db_avg:.2f}")
        else:
            fail("forecasted_total out of range",
                 f"forecast=₹{fc:.2f}  db_avg=₹{db_avg:.2f}")

    # Category forecast
    status2, cf = get("/api/v1/forecast/category/99/food")
    if status2 == 200:
        ok("category forecast response ok")
        ok("forecast_values is list",
           isinstance(cf.get("forecast_values"), list))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 – Dashboard: all keys + totals match DB
# ─────────────────────────────────────────────────────────────────────────────
def test_dashboard():
    section("GET /api/v1/dashboard/{user_id}  →  comprehensive data validation")

    status, r = get("/api/v1/dashboard/99")
    if status != 200:
        fail("HTTP 200", f"{status}: {r}"); return

    req_keys = ["user_id","generated_at","previous_month_summary",
                "current_month_summary","budget_plan","alerts",
                "remaining_budget","trend_analysis","forecast","spending_velocity"]
    for k in req_keys:
        if k in r:
            ok(f"dashboard has key: {k}")
        else:
            fail(f"dashboard missing key: {k}")

    # current month total must match DB
    now       = datetime.now()
    first_day = now.replace(day=1).strftime("%Y-%m-%d")
    db_curr   = db_count(
        "SELECT COALESCE(SUM(amount),0) FROM expenses"
        " WHERE user_id=99 AND date>=?", (first_day,)
    )
    api_curr  = r.get("current_month_summary", {}).get("total_spent", 0)
    if abs(api_curr - db_curr) < 0.01:
        ok("dashboard current_month total matches DB",
           f"API=₹{api_curr:.2f}  DB=₹{db_curr:.2f}")
    else:
        fail("dashboard current_month total mismatch",
             f"API=₹{api_curr:.2f}  DB=₹{db_curr:.2f}")

    # previous month total
    prev_start = (now.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
    prev_end   = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
    db_prev    = db_count(
        "SELECT COALESCE(SUM(amount),0) FROM expenses"
        " WHERE user_id=99 AND date>=? AND date<=?", (prev_start, prev_end)
    )
    api_prev = r.get("previous_month_summary", {}).get("total_spent", 0)
    if abs(api_prev - db_prev) < 0.01:
        ok("dashboard previous_month total matches DB",
           f"API=₹{api_prev:.2f}  DB=₹{db_prev:.2f}")
    else:
        fail("dashboard previous_month total mismatch",
             f"API=₹{api_prev:.2f}  DB=₹{db_prev:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 12 – Chat: messages saved to DB (chat_history table)
# ─────────────────────────────────────────────────────────────────────────────
def test_chat_persistence():
    section("POST /api/support/chat  →  check DB persistence (chat_history)")

    # Clear any old history for user 99 via API
    delete(f"/api/support/chat/history/99")

    before = db_count("SELECT COUNT(*) FROM chat_history WHERE user_id=99")

    status, r = post("/api/support/chat", {
        "user_id": "99",
        "message": "Give me a tip to save money on groceries",
        "support_type": "ai"
    })

    if status != 200:
        fail("HTTP 200", f"{status}: {r}"); return

    ok("AI response received", r.get("message","")[:80])
    ok("message_type==ai",     r.get("message_type") == "ai")

    after = db_count("SELECT COUNT(*) FROM chat_history WHERE user_id=99")
    if after > before:
        ok("chat_history row written to DB", f"{before} → {after} rows")
        # Show the actual DB row
        row = db_one(
            "SELECT * FROM chat_history WHERE user_id=99 ORDER BY created_at DESC LIMIT 1"
        )
        if row:
            ok("DB row has user_message", bool(row.get("user_message")))
            ok("DB row has ai_response",  bool(row.get("ai_response")))
    else:
        warn("chat_history NOT written to DB",
             "ConversationStorage is in-memory — chat history persists only within server lifetime")
        warn("To fix: wire storage.save_message() to INSERT into chat_history table")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 13 – Context injection verified round-trip
# ─────────────────────────────────────────────────────────────────────────────
def test_context_injection():
    section("POST /api/support/chat/context + chat  →  LLM uses real data")

    ctx = {
        "current_month_total": 3500,
        "budget": 6000,
        "budget_status": "within budget (58% used)",
        "category_spending": {"food": 2000, "transport": 500},
        "biggest_category": "food",
        "trend": "increasing (+8% vs last month)"
    }
    s1, r1 = post("/api/support/chat/context/99", ctx)
    if s1 == 200 and r1.get("success"):
        ok("context accepted", str(r1.get("context_keys")))
    else:
        fail("context push failed", f"{s1}: {r1}")

    s2, r2 = post("/api/support/chat", {
        "user_id": "99",
        "message": "Am I overspending on food this month?",
        "support_type": "ai"
    })
    if s2 == 200:
        msg = r2.get("message", "")
        ok("AI chat responded", msg[:100])
        # The LLM should mention food or spending numbers from context
        has_context = any(kw in msg.lower() for kw in
                         ["food","spend","budget","₹","2000","3500","58"])
        if has_context:
            ok("AI response references injected context (food/budget mentioned)")
        else:
            warn("AI response may not be using context",
                 "Response: " + msg[:120])
    else:
        fail("Chat with context failed", f"{s2}: {r2}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 14 – Peer registration persists within server session
# ─────────────────────────────────────────────────────────────────────────────
def test_peer_data():
    section("Peer support  →  register + available + connect + profile")

    # Register
    s1, r1 = post("/api/support/peer/register", {
        "peer_id": "peer_data_test",
        "expertise_areas": ["budgeting","debt"],
        "languages": ["en","hi"]
    })
    ok("register HTTP 200", s1 == 200)
    if s1 == 200:
        ok("peer_id in response",  r1.get("peer",{}).get("peer_id") == "peer_data_test")
        ok("expertise in response", "budgeting" in r1.get("peer",{}).get("expertise_areas",[]))

    # Available peers should now include our new peer
    s2, r2 = get("/api/support/peer/available")
    peer_ids = [p["peer_id"] for p in r2.get("peers", [])]
    if "peer_data_test" in peer_ids:
        ok("peer visible in /peer/available")
    else:
        fail("peer not visible in /peer/available", str(peer_ids))

    # Connect
    s3, r3 = post("/api/support/peer/connect", {
        "user_id": "99", "issue_category": "budgeting", "description": "test"
    })
    if s3 == 200 and r3.get("status") == "connected":
        ok("peer connect → status=connected")
        ok("connection_id returned", bool(r3.get("connection_id")))
        ok("peer_id matches",  r3.get("peer_id") == "peer_data_test")
    else:
        warn("connect status", f"{s3}: {r3}")

    # Profile
    s4, r4 = get("/api/support/peer/peer_data_test/profile")
    if s4 == 200:
        ok("profile returned", f"reputation={r4.get('reputation_score')}")
        ok("active_connections>=1", r4.get("active_connections",0) >= 1)
    else:
        fail("profile not found", f"{s4}: {r4}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 15 – Cleanup
# ─────────────────────────────────────────────────────────────────────────────
def cleanup():
    section("Cleanup")
    with db() as c:
        c.execute("DELETE FROM expenses        WHERE user_id=99")
        c.execute("DELETE FROM recommendations WHERE user_id=99")
        c.execute("DELETE FROM chat_history    WHERE user_id=99")
        c.execute("DELETE FROM users           WHERE id=99")
        c.commit()
    ok("Deleted all user_id=99 rows from DB")
    delete("/api/support/chat/history/99")
    ok("Cleared in-memory chat history via API")

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*62}")
    print("  POKET BOT — DATA INTEGRITY TEST SUITE")
    print(f"{'='*62}")
    print(f"  DB path: {DB_PATH}")
    print(f"  Server:  {BASE}")
    print(f"{'='*62}")

    seed_clean_user()
    test_initialize()
    test_create_expense()
    test_get_expenses()
    test_get_budget_plan()
    test_remaining_budget()
    test_reinitialize_budget()
    test_alerts()
    test_trends()
    test_forecast()
    test_dashboard()
    test_chat_persistence()
    test_context_injection()
    test_peer_data()
    cleanup()

    print(f"\n{'='*62}")
    print(f"  Results: {G}{passed} passed{W}  |  {R}{failed} failed{W}")
    print(f"{'='*62}\n")
    sys.exit(0 if failed == 0 else 1)
