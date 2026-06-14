"""
Comprehensive database population script for PocketBuddy
Populates SQLite database with realistic dummy data across all tables
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = r"C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db"

# Categories and sample data
EXPENSE_CATEGORIES = ['food', 'transport', 'entertainment', 'education', 'health', 'utilities', 'others']

FOOD_ITEMS = [
    'Breakfast at cafe', 'Lunch at restaurant', 'Dinner delivery', 'Coffee & snacks',
    'Grocery shopping', 'Fast food', 'Pizza', 'Burger', 'Sandwich', 'Salad',
    'Noodles', 'Rice', 'Bread', 'Milk', 'Eggs', 'Chicken', 'Fish', 'Vegetables'
]

MEAL_TYPES = ['breakfast', 'lunch', 'dinner', 'snack']

MOOD_TYPES = ['happy', 'neutral', 'sad', 'stressed', 'anxious']

ALERT_LEVELS = ['good', 'warning', 'critical']

GOAL_TYPES = ['exercise', 'sleep', 'study', 'meditation', 'budget', 'reading']

TRAVEL_MODES = ['bus', 'train', 'auto', 'bike', 'walk', 'car', 'metro']

DIETARY_PREFERENCES = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'no-preference']

USER_MAJORS = ['Computer Science', 'Business', 'Engineering', 'Medicine', 'Arts', 'Science', 'Law', 'Finance']

BUDGET_MEAL_NAMES = [
    'Dal and Rice', 'Pasta Primavera', 'Fried Rice', 'Stir-fried Vegetables',
    'Lentil Soup', 'Bean Burrito', 'Chickpea Curry', 'Egg Fried Rice',
    'Veggie Sandwich', 'Tomato Pasta', 'Cabbage Stir-fry', 'Potato Curry',
    'Black Beans Rice Bowl', 'Veggie Omelet', 'Corn Salad', 'Mixed Vegetables Curry'
]


def connect_db():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_users(conn, cursor):
    """Create 6 users with diverse profiles"""
    users = [
        ('alice@email.com', 'password123', 'Alice Johnson', 'Computer Science', 2, 50000, 1200),
        ('bob@email.com', 'password123', 'Bob Smith', 'Business', 3, 75000, 1800),
        ('carol@email.com', 'password123', 'Carol Davis', 'Engineering', 1, 40000, 900),
        ('david@email.com', 'password123', 'David Wilson', 'Medicine', 4, 100000, 2500),
        ('emma@email.com', 'password123', 'Emma Brown', 'Arts', 2, 30000, 700),
        ('frank@email.com', 'password123', 'Frank Miller', 'Finance', 3, 80000, 2000),
    ]

    user_ids = []
    for email, password, name, major, year, income, daily_budget in users:
        cursor.execute("""
            INSERT INTO users (email, password, name, major, year, monthly_income, daily_budget, dietary_preferences)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, password, name, major, year, income, daily_budget,
              json.dumps(random.sample(DIETARY_PREFERENCES, 2))))
        user_ids.append(cursor.lastrowid)

    conn.commit()
    print(f"Created {len(user_ids)} users")
    return user_ids


def create_expenses(conn, cursor, user_ids):
    """Create 500+ expense records spanning 3-4 months"""
    expenses = []
    start_date = datetime(2026, 3, 1)
    end_date = datetime(2026, 6, 15)

    # Category-based realistic amounts
    category_ranges = {
        'food': (100, 800),
        'transport': (50, 500),
        'entertainment': (200, 1500),
        'education': (500, 3000),
        'health': (200, 2000),
        'utilities': (1000, 4000),
        'others': (100, 1000)
    }

    # Generate 500+ expenses (550 to ensure we exceed 500)
    for _ in range(550):
        user_id = random.choice(user_ids)
        category = random.choice(EXPENSE_CATEGORIES)
        min_amt, max_amt = category_ranges[category]
        amount = round(random.uniform(min_amt, max_amt), 2)

        days_delta = random.randint(0, (end_date - start_date).days)
        expense_date = start_date + timedelta(days=days_delta)
        date_str = expense_date.strftime("%Y-%m-%d")

        description = f"{category.capitalize()} - {random.choice(['Personal', 'Monthly', 'Casual', 'Regular'])} expense"

        cursor.execute("""
            INSERT INTO expenses (user_id, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, amount, category, description, date_str))
        expenses.append((user_id, amount, category))

    conn.commit()
    print(f"Created {len(expenses)} expense records")
    return expenses


def create_health_logs(conn, cursor, user_ids):
    """Create 30+ health log entries"""
    start_date = datetime(2026, 5, 15)

    for _ in range(50):
        user_id = random.choice(user_ids)
        log_date = start_date + timedelta(days=random.randint(0, 13))
        date = log_date.strftime("%Y-%m-%d")

        sleep_hours = round(random.uniform(4, 10), 1)
        stress_level = random.randint(1, 10)
        mood = random.choice(MOOD_TYPES)
        study_hours = round(random.uniform(0, 8), 1)
        exercise_minutes = random.randint(0, 120)
        social_activity = random.randint(0, 5)
        energy_level = random.randint(1, 10)
        notes = random.choice(['Feeling good', 'Stressed with exams', 'Good workout', 'Relaxed day', 'Productive'])

        try:
            cursor.execute("""
                INSERT INTO health_logs
                (user_id, date, sleep_hours, stress_level, mood, study_hours, exercise_minutes, social_activity, energy_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, date, sleep_hours, stress_level, mood, study_hours, exercise_minutes, social_activity, energy_level, notes))
        except sqlite3.IntegrityError:
            # Handle duplicate date constraint
            continue

    conn.commit()
    print("Created health log entries")


def create_food_logs(conn, cursor, user_ids):
    """Create 30+ food log entries"""
    start_date = datetime(2026, 5, 15)

    for _ in range(50):
        user_id = random.choice(user_ids)
        food_date = start_date + timedelta(days=random.randint(0, 13))
        date = food_date.strftime("%Y-%m-%d")
        meal_type = random.choice(MEAL_TYPES)
        food_name = random.choice(FOOD_ITEMS)
        cost = round(random.uniform(50, 400), 2)
        calories = random.randint(200, 1200)
        is_homemade = random.randint(0, 1)

        cursor.execute("""
            INSERT INTO food_logs (user_id, date, meal_type, food_name, cost, calories, is_homemade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, meal_type, food_name, cost, calories, is_homemade))

    conn.commit()
    print("Created food log entries")


def create_travel_logs(conn, cursor, user_ids):
    """Create 20+ travel log entries"""
    start_date = datetime(2026, 6, 1)
    locations = [
        ('Home', 'Office'), ('Office', 'Home'), ('Home', 'Mall'),
        ('Mall', 'Home'), ('Campus', 'Library'), ('Library', 'Campus'),
        ('Home', 'Gym'), ('Gym', 'Home'), ('Office', 'Restaurant')
    ]

    for _ in range(40):
        user_id = random.choice(user_ids)
        origin, destination = random.choice(locations)
        travel_date = start_date + timedelta(days=random.randint(0, 30))
        date = travel_date.strftime("%Y-%m-%d")
        mode = random.choice(TRAVEL_MODES)
        cost = round(random.uniform(30, 300), 2)
        duration_minutes = random.randint(10, 120)

        cursor.execute("""
            INSERT INTO travel_logs (user_id, date, origin, destination, mode, cost, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, origin, destination, mode, cost, duration_minutes))

    conn.commit()
    print("Created travel log entries")


def create_routine_goals(conn, cursor, user_ids):
    """Create 15+ routine goals"""
    for _ in range(25):
        user_id = random.choice(user_ids)
        goal_type = random.choice(GOAL_TYPES)
        current_value = round(random.uniform(0, 100), 2)
        target_value = round(random.uniform(current_value, 150), 2)
        weekly_target = round(target_value / 4, 2)
        week_number = random.randint(1, 4)
        status = random.choice(['active', 'completed', 'paused'])

        cursor.execute("""
            INSERT INTO routine_goals
            (user_id, goal_type, current_value, target_value, weekly_target, week_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, goal_type, current_value, target_value, weekly_target, week_number, status))

    conn.commit()
    print("Created routine goal entries")


def create_recommendations(conn, cursor, user_ids):
    """Create 10-15 recommendation entries"""
    rec_types = ['budget_plan', 'spending_alert', 'goal_suggestion', 'health_tip']

    for _ in range(20):
        user_id = random.choice(user_ids)
        rec_date = datetime.now() - timedelta(days=random.randint(0, 30))
        date = rec_date.strftime("%Y-%m-%d")
        rec_type = random.choice(rec_types)

        if rec_type == 'budget_plan':
            text = json.dumps({
                'plan': {
                    'food': 5000,
                    'transport': 2000,
                    'entertainment': 3000,
                    'education': 2000,
                    'health': 1500,
                    'utilities': 2000,
                    'others': 1000,
                    'savings': 5000
                },
                'month': date[:7],
                'created_date': datetime.now().isoformat()
            })
        else:
            text = json.dumps({
                'type': rec_type,
                'message': f"Sample recommendation for {rec_type}",
                'priority': random.choice(['high', 'medium', 'low'])
            })

        feedback = random.choice([None, 'helpful', 'not helpful'])
        was_helpful = random.choice([None, 0, 1]) if feedback else None

        cursor.execute("""
            INSERT INTO recommendations (user_id, date, type, text, feedback, was_helpful)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, date, rec_type, text, feedback, was_helpful))

    conn.commit()
    print("Created recommendation entries")


def create_chat_history(conn, cursor, user_ids):
    """Create 20-30 chat history entries"""
    user_questions = [
        "How can I reduce my food expenses?",
        "What's my spending pattern this month?",
        "How much should I save?",
        "Am I on track with my budget?",
        "What meals are budget-friendly?",
        "How's my exercise routine?",
        "Any tips for better sleep?",
        "Show me my expense breakdown",
        "How stressed am I lately?",
        "What's my monthly budget?"
    ]

    ai_responses = [
        "Based on your data, you can reduce expenses by focusing on these categories...",
        "Your spending has increased by 15% this month...",
        "I recommend saving at least 10% of your income...",
        "You're 5% over budget this month. Let me help you adjust...",
        "These meals are affordable and nutritious...",
        "Your exercise routine is improving! Keep it up...",
        "You need more sleep. Aim for 7-8 hours...",
        "Here's your expense breakdown for this month...",
        "Your stress levels are higher than usual. Try relaxation...",
        "Your budget allocation looks good this month..."
    ]

    for _ in range(40):
        user_id = random.choice(user_ids)
        chat_date = datetime.now() - timedelta(days=random.randint(0, 90))
        date = chat_date.strftime("%Y-%m-%d")
        user_message = random.choice(user_questions)
        ai_response = random.choice(ai_responses)
        context = json.dumps({'session': 'user_inquiry', 'priority': random.choice(['high', 'normal'])})

        cursor.execute("""
            INSERT INTO chat_history (user_id, date, user_message, ai_response, context)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, date, user_message, ai_response, context))

    conn.commit()
    print("Created chat history entries")


def create_burnout_scores(conn, cursor, user_ids):
    """Create 20 burnout score entries"""
    start_date = datetime(2026, 5, 1)

    for _ in range(30):
        user_id = random.choice(user_ids)
        burnout_date = start_date + timedelta(days=random.randint(0, 30))
        date = burnout_date.strftime("%Y-%m-%d")

        baseline_sleep = round(random.uniform(7, 8), 1)
        baseline_stress = round(random.uniform(3, 5), 1)
        baseline_exercise = round(random.uniform(30, 60), 1)

        current_sleep = round(random.uniform(4, 8), 1)
        current_stress = round(random.uniform(3, 8), 1)
        current_exercise = round(random.uniform(0, 60), 1)

        score = max(0, min(100, int(
            (current_sleep / baseline_sleep) * 30 +
            ((baseline_stress - current_stress) / baseline_stress) * 40 +
            (current_exercise / baseline_exercise) * 30
        )))

        if score < 30:
            alert_level = 'critical'
        elif score < 60:
            alert_level = 'warning'
        else:
            alert_level = 'good'

        try:
            cursor.execute("""
                INSERT INTO burnout_scores
                (user_id, date, baseline_sleep, baseline_stress, baseline_exercise,
                 current_sleep, current_stress, current_exercise, score, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, date, baseline_sleep, baseline_stress, baseline_exercise,
                  current_sleep, current_stress, current_exercise, score, alert_level))
        except sqlite3.IntegrityError:
            continue

    conn.commit()
    print("Created burnout score entries")


def create_budget_meals(conn, cursor):
    """Create 20+ budget meal entries"""
    # Extend meal names for more records
    extended_meals = BUDGET_MEAL_NAMES * 2  # Double the list
    for i, meal_name in enumerate(extended_meals):
        cost = round(random.uniform(50, 300), 2)
        calories = random.randint(300, 800)
        category = random.choice(['breakfast', 'lunch', 'dinner', 'snack'])
        dietary_tags = json.dumps(random.sample(['vegetarian', 'vegan', 'dairy-free', 'gluten-free'], 1))
        prep_time = random.randint(10, 60)
        instructions = f"Recipe instructions for {meal_name} (mock data)"
        is_vegetarian = 1 if 'vegetarian' in dietary_tags.lower() else 0
        is_vegan = 1 if 'vegan' in dietary_tags.lower() else 0

        cursor.execute("""
            INSERT INTO budget_meals
            (name, cost, calories, category, dietary_tags, prep_time_minutes, instructions, is_vegetarian, is_vegan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (meal_name, cost, calories, category, dietary_tags, prep_time, instructions, is_vegetarian, is_vegan))

    conn.commit()
    print("Created budget meal entries")


def verify_data(conn, cursor):
    """Verify all data was inserted and display summary statistics"""
    print("\n" + "="*60)
    print("DATABASE POPULATION SUMMARY")
    print("="*60)

    tables = ['users', 'expenses', 'health_logs', 'travel_logs', 'food_logs',
              'routine_goals', 'recommendations', 'chat_history', 'burnout_scores', 'budget_meals']

    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"{table:20s}: {count:5d} records")

    print("="*60)
    print(f"{'TOTAL':20s}: {total_records:5d} records")
    print("="*60)

    # Sample statistics
    print("\nSAMPLE STATISTICS:")
    print("-" * 60)

    # User statistics
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Total Users: {user_count}")

    # Expense statistics
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0] or 0
    cursor.execute("SELECT AVG(amount) FROM expenses")
    avg_expense = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MAX(amount) FROM expenses")
    max_expense = cursor.fetchone()[0] or 0
    cursor.execute("SELECT MIN(amount) FROM expenses")
    min_expense = cursor.fetchone()[0] or 0

    print(f"\nExpense Statistics:")
    print(f"  Total Spent: {total_spent:,.2f}")
    print(f"  Average Expense: {avg_expense:,.2f}")
    print(f"  Max Expense: {max_expense:,.2f}")
    print(f"  Min Expense: {min_expense:,.2f}")

    # Category breakdown
    cursor.execute("""
        SELECT category, COUNT(*) as count, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)
    print(f"\nExpense by Category:")
    for category, count, total in cursor.fetchall():
        print(f"  {category:15s}: {count:4d} transactions, {total:10,.2f}")

    # Date range
    cursor.execute("SELECT MIN(date), MAX(date) FROM expenses")
    min_date, max_date = cursor.fetchone()
    print(f"\nExpense Date Range: {min_date} to {max_date}")

    # User income statistics
    cursor.execute("SELECT MIN(monthly_income), AVG(monthly_income), MAX(monthly_income) FROM users")
    min_income, avg_income, max_income = cursor.fetchone()
    print(f"\nUser Income Statistics:")
    print(f"  Min Monthly Income: {min_income:,.2f}")
    print(f"  Avg Monthly Income: {avg_income:,.2f}")
    print(f"  Max Monthly Income: {max_income:,.2f}")

    # Health stats
    cursor.execute("SELECT AVG(sleep_hours), AVG(stress_level), AVG(exercise_minutes) FROM health_logs")
    avg_sleep, avg_stress, avg_exercise = cursor.fetchone()
    print(f"\nHealth Statistics:")
    print(f"  Average Sleep: {avg_sleep:.1f} hours")
    print(f"  Average Stress Level: {avg_stress:.1f}/10")
    print(f"  Average Exercise: {avg_exercise:.0f} minutes")

    print("\n" + "="*60)
    print("DATABASE POPULATION COMPLETE!")
    print("="*60)


def main():
    """Main execution function"""
    try:
        # Check if database file exists
        if not Path(DB_PATH).exists():
            print(f"Error: Database file not found at {DB_PATH}")
            print("Please run the database setup first.")
            return

        conn = connect_db()
        cursor = conn.cursor()

        print("Starting database population...")
        print("="*60)

        # Create data in order
        user_ids = create_users(conn, cursor)
        expenses = create_expenses(conn, cursor, user_ids)
        create_food_logs(conn, cursor, user_ids)
        create_health_logs(conn, cursor, user_ids)
        create_travel_logs(conn, cursor, user_ids)
        create_routine_goals(conn, cursor, user_ids)
        create_recommendations(conn, cursor, user_ids)
        create_chat_history(conn, cursor, user_ids)
        create_burnout_scores(conn, cursor, user_ids)
        create_budget_meals(conn, cursor)

        # Verify data
        verify_data(conn, cursor)

        conn.close()
        print("\nDatabase population successful!")

    except Exception as e:
        print(f"Error during database population: {e}")
        raise


if __name__ == "__main__":
    main()
