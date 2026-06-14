import sqlite3

# Connect to the database
conn = sqlite3.connect('database/pocketbuddy.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('=== TABLES IN DATABASE ===')
for table in tables:
    print(table[0])
print()

# Distinct user_ids from expenses table
print('=== DISTINCT USER IDS FROM EXPENSES TABLE ===')
try:
    cursor.execute('SELECT DISTINCT user_id FROM expenses;')
    user_ids_expenses = cursor.fetchall()
    if user_ids_expenses:
        for uid in user_ids_expenses:
            print(uid[0])
    else:
        print('No data in expenses table')
except Exception as e:
    print(f'Error: {e}')
print()

# User data from users table
print('=== ALL USERS (ID, NAME, EMAIL) ===')
try:
    cursor.execute('SELECT * FROM users;')
    users = cursor.fetchall()
    if users:
        for user in users:
            print(user)
    else:
        print('No data in users table')
except Exception as e:
    print(f'Error: {e}')
print()

# Check recommendations table
print('=== BUDGET PLANS FROM RECOMMENDATIONS TABLE ===')
try:
    cursor.execute('SELECT * FROM recommendations;')
    recs = cursor.fetchall()
    if recs:
        for rec in recs:
            print(rec)
    else:
        print('No data in recommendations table')
except Exception as e:
    print(f'Recommendations table does not exist or error: {e}')

conn.close()
