"""
Comprehensive database verification report
"""

import sqlite3

DB_PATH = r"C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("COMPREHENSIVE DATABASE VERIFICATION REPORT")
    print("="*80)

    print("\n[1] USER DETAILS")
    print("-" * 80)
    cursor.execute("SELECT id, email, name, major, year, monthly_income, daily_budget FROM users ORDER BY id")
    users = cursor.fetchall()
    for row in users:
        print(f"  User {row[0]:2d}: {row[2]:20s} | {row[1]:25s} | Income: {row[5]:>8,.0f} | Daily Budget: {row[6]:>8,.0f}")

    print("\n[2] EXPENSE SUMMARY BY USER")
    print("-" * 80)
    cursor.execute("""
        SELECT u.id, u.name, COUNT(e.id) as count, ROUND(SUM(e.amount), 2) as total
        FROM users u
        LEFT JOIN expenses e ON u.id = e.user_id
        GROUP BY u.id
        ORDER BY u.id
    """)
    for row in cursor.fetchall():
        print(f"  User {row[0]:2d} ({row[1]:20s}): {row[2]:4d} expenses, Total: {row[3]:>12,.2f}")

    print("\n[3] EXPENSE BREAKDOWN BY CATEGORY")
    print("-" * 80)
    cursor.execute("""
        SELECT category, COUNT(*) as count, ROUND(SUM(amount), 2) as total, ROUND(AVG(amount), 2) as avg
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:15s}: {row[1]:4d} transactions | Total: {row[2]:>12,.2f} | Avg: {row[3]:>10,.2f}")

    print("\n[4] EXPENSE DATE RANGE & DISTRIBUTION")
    print("-" * 80)
    cursor.execute("""
        SELECT MIN(date) as min_date, MAX(date) as max_date,
               ROUND(COUNT(*), 0) as total_count
        FROM expenses
    """)
    min_date, max_date, count = cursor.fetchone()
    print(f"  Date Range: {min_date} to {max_date}")
    print(f"  Total Expenses: {int(count)}")

    # Monthly distribution
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, COUNT(*) as count, ROUND(SUM(amount), 2) as total
        FROM expenses
        GROUP BY month
        ORDER BY month
    """)
    print(f"\n  Monthly Distribution:")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]:4d} expenses, {row[2]:>12,.2f}")

    print("\n[5] HEALTH & WELLNESS DATA")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM health_logs")
    health_count = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(AVG(sleep_hours), 1), ROUND(AVG(stress_level), 1), ROUND(AVG(exercise_minutes), 1) FROM health_logs")
    sleep, stress, exercise = cursor.fetchone()
    print(f"  Health Log Entries: {health_count}")
    print(f"  Average Sleep: {sleep} hours")
    print(f"  Average Stress Level: {stress}/10")
    print(f"  Average Exercise: {exercise} minutes")

    print("\n[6] FOOD & NUTRITION LOGS")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM food_logs")
    food_count = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(SUM(cost), 2), ROUND(AVG(cost), 2) FROM food_logs")
    total_food_cost, avg_food_cost = cursor.fetchone()
    cursor.execute("""
        SELECT meal_type, COUNT(*) as count, ROUND(AVG(cost), 2) as avg_cost
        FROM food_logs
        GROUP BY meal_type
    """)
    print(f"  Food Log Entries: {food_count}")
    print(f"  Total Food Cost: {total_food_cost:,.2f}")
    print(f"  Average Food Cost: {avg_food_cost:,.2f}")
    print(f"\n  By Meal Type:")
    for row in cursor.fetchall():
        print(f"    {row[0]:10s}: {row[1]:4d} entries | Avg Cost: {row[2]:>8,.2f}")

    print("\n[7] TRAVEL & TRANSPORTATION")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM travel_logs")
    travel_count = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(SUM(cost), 2), ROUND(AVG(cost), 2) FROM travel_logs")
    total_travel, avg_travel = cursor.fetchone()
    cursor.execute("""
        SELECT mode, COUNT(*) as count, ROUND(SUM(cost), 2) as total
        FROM travel_logs
        GROUP BY mode
        ORDER BY total DESC
    """)
    print(f"  Travel Log Entries: {travel_count}")
    print(f"  Total Travel Cost: {total_travel:,.2f}")
    print(f"  Average Trip Cost: {avg_travel:,.2f}")
    print(f"\n  By Mode of Transport:")
    for row in cursor.fetchall():
        print(f"    {row[0]:10s}: {row[1]:4d} trips | Total Cost: {row[2]:>10,.2f}")

    print("\n[8] ROUTINE GOALS TRACKING")
    print("-" * 80)
    cursor.execute("""
        SELECT goal_type, COUNT(*) as count,
               ROUND(AVG(current_value), 2) as avg_current,
               ROUND(AVG(target_value), 2) as avg_target
        FROM routine_goals
        GROUP BY goal_type
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:15s}: {row[1]:2d} goals | Current Avg: {row[2]:>8,.2f} | Target Avg: {row[3]:>8,.2f}")

    print("\n[9] RECOMMENDATIONS & ADVICE")
    print("-" * 80)
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM recommendations
        GROUP BY type
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:2d} records")

    print("\n[10] CHAT HISTORY & AI INTERACTIONS")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    chat_count = cursor.fetchone()[0]
    print(f"  Chat Sessions: {chat_count}")
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM chat_history")
    chat_users = cursor.fetchone()[0]
    print(f"  Users with Chat: {chat_users}")

    print("\n[11] BURNOUT ASSESSMENT SCORES")
    print("-" * 80)
    cursor.execute("""
        SELECT alert_level, COUNT(*) as count, ROUND(AVG(score), 1) as avg_score
        FROM burnout_scores
        GROUP BY alert_level
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]:10s}: {row[1]:2d} assessments | Avg Score: {row[2]:>6.1f}")

    print("\n[12] BUDGET MEAL REFERENCE DATABASE")
    print("-" * 80)
    cursor.execute("SELECT COUNT(*) FROM budget_meals")
    meal_count = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(AVG(cost), 2), ROUND(AVG(calories), 0) FROM budget_meals")
    avg_cost, avg_cal = cursor.fetchone()
    print(f"  Budget Meals: {meal_count}")
    print(f"  Average Cost: {avg_cost:,.2f}")
    print(f"  Average Calories: {int(avg_cal)}")

    print("\n[13] OVERALL DATABASE STATISTICS")
    print("-" * 80)
    tables_info = [
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

    total_records = 0
    for table_name, table_label in tables_info:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"  {table_label:30s}: {count:5d} records")

    print(f"\n  {'TOTAL RECORDS':30s}: {total_records:5d} records")
    print("="*80)

    conn.close()
    print("\nDatabase verification complete!")

if __name__ == "__main__":
    main()
