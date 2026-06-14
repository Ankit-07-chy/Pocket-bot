# PocketBuddy Database Tools & Documentation Index

## Overview

Complete toolkit for managing and analyzing the PocketBuddy SQLite database with 824+ dummy records across 10 tables.

**Database Location:** `C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db`

---

## Files Created

### 1. Python Scripts

#### `populate_db.py`
**Purpose:** Generate and insert comprehensive dummy data into the database

**Features:**
- Creates 6 users with realistic profiles
- Generates 550+ expense transactions
- Populates all 10 tables with related data
- Automatic data validation
- Summary statistics display

**Usage:**
```bash
python populate_db.py
```

**Output:**
- 824 total records across all tables
- Data summary with counts by table
- Statistical analysis of expenses
- Health metrics average
- User income statistics

**Runtime:** ~5-10 seconds

---

#### `verify_db.py`
**Purpose:** Comprehensive database verification and reporting

**Features:**
- Detailed user profiles (6 users)
- Expense analysis by category and user
- Health and wellness metrics
- Food and nutrition statistics
- Travel and transportation summary
- Routine goals tracking
- Burnout assessment distribution
- Chat history activity
- Budget meal database stats
- Complete database statistics

**Usage:**
```bash
python verify_db.py
```

**Output:**
- 13-section comprehensive report
- User-by-user breakdown
- Category-wise spending analysis
- Monthly distribution
- Meal type breakdown
- Transportation mode analysis
- Alert level distribution
- 824 total records summary

**Runtime:** ~2-3 seconds

---

### 2. Documentation Files

#### `DATABASE_POPULATION_SUMMARY.md`
**Purpose:** Complete documentation of what was populated

**Sections:**
1. Executive Summary
2. Overall Statistics
3. Table-by-Table Breakdown (all 10 tables)
4. Data Quality Features
5. Scripts and Files
6. How to Use
7. Validation Checklist
8. Performance Notes
9. Next Steps

**Read this when:** You need complete details on what data exists and how to use it

**Length:** ~500 lines, comprehensive reference

---

#### `QUICK_START_DB.md`
**Purpose:** Quick reference guide for immediate use

**Sections:**
1. Database Location
2. What's Been Populated (summary)
3. Test User Accounts (table with IDs/passwords)
4. Expense Categories (breakdown)
5. Usage Scenarios (7 different scenarios)
6. Quick Database Queries (8 SQL examples)
7. Regenerating Data (instructions)
8. Data Characteristics (dates, amounts, income)
9. Troubleshooting (FAQ)
10. Performance Notes

**Read this when:** You need quick answers and immediate setup

**Length:** ~200 lines, concise reference

---

#### `sample_queries.sql`
**Purpose:** Collection of 50+ SQL queries for data exploration

**Query Categories:**
1. User Management (4 queries)
2. Expense Tracking (8 queries)
3. Health & Wellness (5 queries)
4. Food & Nutrition (6 queries)
5. Travel & Transportation (4 queries)
6. Routine Goals (4 queries)
7. Burnout Assessment (4 queries)
8. Recommendations & AI (3 queries)
9. Chat History (3 queries)
10. Budget Meals (5 queries)
11. Cross-Table Analysis (3 queries)

**Use Case:** Copy-paste queries to explore and analyze data

**Example Queries:**
- View all expenses for a user
- Category breakdown
- Monthly trends
- Health metrics
- Travel patterns
- User summaries

---

#### `DATABASE_TOOLS_INDEX.md`
**Purpose:** This file - index of all tools and documentation

**Sections:**
- File descriptions
- Quick command reference
- Data structure overview
- Common tasks and how to do them
- Troubleshooting guide

---

## Data Structure Overview

### 10 Tables

| Table | Records | Key Fields | Purpose |
|-------|---------|-----------|---------|
| users | 6 | id, name, email, monthly_income | User profiles |
| expenses | 550 | id, user_id, amount, category, date | Spending tracking |
| health_logs | 35 | id, user_id, sleep_hours, stress_level | Wellness data |
| travel_logs | 40 | id, user_id, origin, destination, mode | Transportation |
| food_logs | 50 | id, user_id, meal_type, food_name, cost | Nutrition tracking |
| routine_goals | 25 | id, user_id, goal_type, current_value | Goal tracking |
| recommendations | 20 | id, user_id, type, text, feedback | AI suggestions |
| chat_history | 40 | id, user_id, user_message, ai_response | Chat logs |
| burnout_scores | 26 | id, user_id, score, alert_level | Burnout assessment |
| budget_meals | 32 | id, name, cost, calories | Meal reference |

**Total: 824 records**

---

## Quick Command Reference

### View Data
```bash
# Run verification and see all data
python verify_db.py

# Or run a specific SQL query
sqlite3 database/pocketbuddy.db "SELECT * FROM users;"
```

### Regenerate Data
```bash
# Clear everything and repopulate
python populate_db.py
```

### Explore Data
```bash
# Open SQLite interactive shell
sqlite3 database/pocketbuddy.db

# Inside shell, run sample queries from sample_queries.sql
.read sample_queries.sql
```

---

## Test User Accounts

All test users have password: `password123`

```
ID  | Name           | Email                | Income  | Major
----|----------------|----------------------|---------|------------------
915 | Alice Johnson  | alice@email.com      | $50K    | Computer Science
916 | Bob Smith      | bob@email.com        | $75K    | Business
917 | Carol Davis    | carol@email.com      | $40K    | Engineering
918 | David Wilson   | david@email.com      | $100K   | Medicine
919 | Emma Brown     | emma@email.com       | $30K    | Arts
920 | Frank Miller   | frank@email.com      | $80K    | Finance
```

---

## Common Tasks

### Task 1: See expense data for a specific user
```bash
# Use User ID 915 (Alice Johnson)
sqlite3 database/pocketbuddy.db "SELECT * FROM expenses WHERE user_id = 915;"
```

### Task 2: Analyze spending by category
```bash
# Run the query from sample_queries.sql under "EXPENSE TRACKING"
sqlite3 database/pocketbuddy.db < sample_queries.sql | grep -A10 "category breakdown"
```

### Task 3: Check health metrics
```bash
python verify_db.py | grep -A10 "HEALTH"
```

### Task 4: See monthly trends
```bash
sqlite3 database/pocketbuddy.db "SELECT strftime('%Y-%m', date) as month, COUNT(*), SUM(amount) FROM expenses GROUP BY month;"
```

### Task 5: Get user summary
```bash
python verify_db.py | grep -A6 "USER DETAILS"
```

### Task 6: View chat conversations
```bash
sqlite3 database/pocketbuddy.db "SELECT u.name, c.date, c.user_message FROM chat_history c JOIN users u ON c.user_id = u.id LIMIT 5;"
```

### Task 7: Reset database for testing
```bash
# Clear all data
python -c "
import sqlite3
conn = sqlite3.connect('database/pocketbuddy.db')
tables = ['expenses', 'health_logs', 'travel_logs', 'food_logs', 'routine_goals', 'recommendations', 'chat_history', 'burnout_scores', 'users', 'budget_meals']
for table in tables:
    conn.execute(f'DELETE FROM {table}')
conn.commit()
print('Cleared')
"

# Repopulate with fresh data
python populate_db.py
```

---

## Data Characteristics

### Dates
- **Range:** March 1, 2026 - June 15, 2026
- **Format:** YYYY-MM-DD
- **Distribution:** ~4 months of data

### Expenses
- **Count:** 550 transactions
- **Total:** $583,451.09
- **Range:** $57.35 - $3,883.64
- **Average:** $1,060.82
- **Categories:** 7 (food, transport, entertainment, education, health, utilities, others)

### Users
- **Count:** 6
- **Income Range:** $30,000 - $100,000
- **Average Income:** $62,500
- **Daily Budgets:** $700 - $2,500

### Health Data
- **Log Entries:** 35
- **Average Sleep:** 6.5 hours
- **Average Stress:** 5.7/10
- **Average Exercise:** 66 minutes

### Food Data
- **Meal Entries:** 50
- **Average Cost:** $205
- **Meal Types:** 4 (breakfast, lunch, dinner, snack)

---

## Troubleshooting

### Q: I can't find the database file
**A:** Check path: `C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db`

### Q: I want to reset the database with new data
**A:** Run: `python populate_db.py`

### Q: The data looks old/different
**A:** All dates are relative to June 2026. Run `python verify_db.py` to see current state.

### Q: How do I run SQL queries?
**A:** Use: `sqlite3 database/pocketbuddy.db "YOUR_QUERY_HERE;"`
Or see `sample_queries.sql` for examples.

### Q: Can I modify the scripts?
**A:** Yes! Edit `populate_db.py` to change:
- Number of users
- Number of expenses
- Date ranges
- Amount ranges
- Data distribution

### Q: Is the data realistic?
**A:** Yes! Amounts vary by category, dates span months, users have diverse profiles, and relationships are consistent across tables.

### Q: Can I add more data without clearing?
**A:** Yes! The scripts insert data, they don't clear first. But you may get duplicates. Clear first if needed.

---

## Quick Stats

- **Total Records:** 824
- **Largest Table:** expenses (550 rows)
- **Database Size:** ~500KB
- **Generation Time:** ~5 seconds
- **Verification Time:** ~2 seconds
- **Query Speed:** Milliseconds for typical queries

---

## File Locations

All files in project root:
- `populate_db.py` - Data generation
- `verify_db.py` - Data verification
- `DATABASE_POPULATION_SUMMARY.md` - Full docs
- `QUICK_START_DB.md` - Quick reference
- `sample_queries.sql` - SQL examples
- `DATABASE_TOOLS_INDEX.md` - This file

Database:
- `database/pocketbuddy.db` - SQLite database file

---

## Documentation Map

```
START HERE
    |
    +-- Need quick answers? --> QUICK_START_DB.md
    |
    +-- Need full details? --> DATABASE_POPULATION_SUMMARY.md
    |
    +-- Need SQL examples? --> sample_queries.sql
    |
    +-- Need to generate data? --> python populate_db.py
    |
    +-- Need verification? --> python verify_db.py
    |
    +-- Need complete index? --> This file
```

---

## Next Steps

1. **Run verification:** `python verify_db.py`
2. **Explore data:** Open `sample_queries.sql` and run queries
3. **Test features:** Use test user accounts with password `password123`
4. **Analyze trends:** Check expense reports and health metrics
5. **Build features:** Use this data to test your application

---

**Status:** Ready for Development & Testing
**Last Updated:** June 14, 2026
**All Scripts Tested:** Yes
**Data Verified:** Yes
