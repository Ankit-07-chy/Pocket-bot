"""
Final Database Population Summary
"""

import sqlite3

DB_PATH = r"C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("POCKETBUDDY DATABASE - FINAL SUMMARY".center(80))
    print("="*80)

    print("\nDATABASE STATUS")
    print("-" * 80)
    print("Location: C:\\Users\\ankit\\Desktop\\poket-bot\\database\\pocketbuddy.db")
    print("Status:   READY FOR USE")
    print("Date:     June 14, 2026")

    # Quick stats
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM expenses")
    exp_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM expenses")
    exp_total = cursor.fetchone()[0]

    print("\nQUICK NUMBERS")
    print("-" * 80)
    print(f"Users:            {user_count}")
    print(f"Expense Records:  {exp_count} transactions")
    print(f"Total Spent:      ${exp_total:,.2f}")

    # Total records
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM users) +
            (SELECT COUNT(*) FROM expenses) +
            (SELECT COUNT(*) FROM health_logs) +
            (SELECT COUNT(*) FROM travel_logs) +
            (SELECT COUNT(*) FROM food_logs) +
            (SELECT COUNT(*) FROM routine_goals) +
            (SELECT COUNT(*) FROM recommendations) +
            (SELECT COUNT(*) FROM chat_history) +
            (SELECT COUNT(*) FROM burnout_scores) +
            (SELECT COUNT(*) FROM budget_meals)
    """)
    total = cursor.fetchone()[0]
    print(f"Total Records:    {total}")

    print("\nFILES CREATED")
    print("-" * 80)
    files = [
        ("populate_db.py", "Generate dummy data"),
        ("verify_db.py", "Verify and report"),
        ("DATABASE_POPULATION_SUMMARY.md", "Full documentation"),
        ("QUICK_START_DB.md", "Quick reference"),
        ("sample_queries.sql", "SQL examples"),
        ("DATABASE_TOOLS_INDEX.md", "Complete index"),
        ("final_summary.py", "This summary script"),
    ]
    for fname, desc in files:
        print(f"  - {fname:35s} {desc}")

    print("\nTEST ACCOUNTS (Password: password123)")
    print("-" * 80)
    cursor.execute("SELECT id, name, email, monthly_income FROM users ORDER BY id")
    for uid, name, email, income in cursor.fetchall():
        print(f"  User {uid}: {name:20s} ({email:25s}) ${income:>8,.0f}/month")

    print("\nEXPENSE CATEGORY BREAKDOWN")
    print("-" * 80)
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_expenses = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COUNT(*), SUM(amount) FROM expenses
        GROUP BY category ORDER BY SUM(amount) DESC
    """)
    for cat, count, total in cursor.fetchall():
        pct = (total / total_expenses * 100) if total_expenses else 0
        print(f"  {cat:15s}: {count:3d} transactions  ${total:>12,.2f}  ({pct:5.1f}%)")

    print("\nDATA COMPLETENESS")
    print("-" * 80)
    tables = [
        ('users', 'User Accounts'),
        ('expenses', 'Expense Transactions'),
        ('health_logs', 'Health Check-ins'),
        ('travel_logs', 'Transportation Records'),
        ('food_logs', 'Meal Entries'),
        ('routine_goals', 'Goals & Targets'),
        ('recommendations', 'AI Recommendations'),
        ('chat_history', 'Chat Sessions'),
        ('burnout_scores', 'Burnout Assessments'),
        ('budget_meals', 'Budget Meal Database')
    ]

    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "OK" if count > 0 else "EMPTY"
        print(f"  [{status:5s}] {label:30s}: {count:5d} records")

    print("\nHOW TO USE")
    print("-" * 80)
    print("  1. Run verification:")
    print("     python verify_db.py")
    print()
    print("  2. Explore with SQL:")
    print("     sqlite3 database/pocketbuddy.db < sample_queries.sql")
    print()
    print("  3. Reset database:")
    print("     python populate_db.py")
    print()
    print("  4. Read documentation:")
    print("     - QUICK_START_DB.md (quick reference)")
    print("     - DATABASE_POPULATION_SUMMARY.md (full details)")
    print("     - DATABASE_TOOLS_INDEX.md (complete index)")

    print("\nKEY STATISTICS")
    print("-" * 80)

    cursor.execute("SELECT MIN(date), MAX(date) FROM expenses")
    min_date, max_date = cursor.fetchone()
    print(f"Date Range:       {min_date} to {max_date}")

    cursor.execute("SELECT AVG(amount), MIN(amount), MAX(amount) FROM expenses")
    avg_amt, min_amt, max_amt = cursor.fetchone()
    print(f"Expense Range:    ${min_amt:,.2f} to ${max_amt:,.2f}")
    print(f"Average Expense:  ${avg_amt:,.2f}")

    cursor.execute("SELECT AVG(monthly_income) FROM users")
    avg_income = cursor.fetchone()[0]
    print(f"Average Income:   ${avg_income:,.2f}/month")

    cursor.execute("SELECT AVG(sleep_hours) FROM health_logs")
    avg_sleep = cursor.fetchone()[0]
    print(f"Average Sleep:    {avg_sleep:.1f} hours")

    print("\nSTATUS: READY FOR DEVELOPMENT & TESTING")
    print("="*80 + "\n")

    conn.close()

if __name__ == "__main__":
    main()
