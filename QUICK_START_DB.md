# PocketBuddy Database Quick Start Guide

## Database Location
```
C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db
```

## What's Been Populated

### Data Summary
- **Total Records:** 824
- **Users:** 6 test accounts
- **Expenses:** 550+ transactions ($583K+ total)
- **Health Logs:** 35 wellness entries
- **Food Logs:** 50 meal records
- **Travel Logs:** 40 trip records
- **Chat History:** 40 conversations
- **Routine Goals:** 25 goal entries
- **Burnout Scores:** 26 assessments
- **Budget Meals:** 32 meal options
- **Recommendations:** 20 AI suggestions

## Test User Accounts

| ID | Name | Email | Income | Budget |
|----|------|-------|--------|--------|
| 915 | Alice Johnson | alice@email.com | $50K | $1,200/day |
| 916 | Bob Smith | bob@email.com | $75K | $1,800/day |
| 917 | Carol Davis | carol@email.com | $40K | $900/day |
| 918 | David Wilson | david@email.com | $100K | $2,500/day |
| 919 | Emma Brown | emma@email.com | $30K | $700/day |
| 920 | Frank Miller | frank@email.com | $80K | $2,000/day |

**Password for all accounts:** `password123`

## Expense Categories

- **Food** (70 transactions): $32,760
- **Transport** (82 transactions): $22,077
- **Entertainment** (77 transactions): $65,522
- **Education** (76 transactions): $132,123
- **Health** (74 transactions): $94,316
- **Utilities** (78 transactions): $185,137
- **Others** (93 transactions): $51,515

## Usage Scenarios

### Scenario 1: Test Expense Tracking
Use User 918 (David Wilson) - has highest income and most expenses
- Date Range: March 1 - June 15, 2026
- 95 transactions
- All 7 expense categories covered

### Scenario 2: Test Health & Wellness
Check health logs and burnout scores
- 35 health check-ins with sleep, stress, exercise data
- 26 burnout assessments with alert levels
- Users show varied wellness patterns

### Scenario 3: Test Food & Nutrition
Use food logs for meal planning features
- 50 meal entries across breakfast, lunch, dinner, snacks
- Average meal cost: $205
- Mix of homemade and external food

### Scenario 4: Test Travel Tracking
Review transportation patterns
- 40 travel entries with various modes
- Bike: $1,421, Auto: $1,221, Train: $1,074
- Mix of local and longer commutes

### Scenario 5: Test Goal Tracking
Review routine goals across categories
- Exercise: 8 goals (avg progress 63%)
- Sleep: 4 goals (avg progress 72%)
- Study: 4 goals (avg progress 41%)
- Budget: 5 goals (avg progress 58%)

### Scenario 6: Test AI Chat
Review 40 chat conversations
- Budget questions
- Expense analysis
- Wellness advice
- Goal tracking help

### Scenario 7: Test Recommendations
Check budget plans and alerts
- 5 budget plans per user/month
- 5 spending alerts
- 5 goal suggestions
- 5 health tips

## Quick Database Queries

### See all expenses for User 915
```sql
SELECT * FROM expenses WHERE user_id = 915;
```

### Category breakdown
```sql
SELECT category, COUNT(*), SUM(amount) FROM expenses GROUP BY category;
```

### Monthly expense trend
```sql
SELECT strftime('%Y-%m', date), SUM(amount) FROM expenses GROUP BY strftime('%Y-%m', date);
```

### Health status
```sql
SELECT user_id, AVG(sleep_hours), AVG(stress_level), AVG(exercise_minutes) 
FROM health_logs 
GROUP BY user_id;
```

### Burnout assessment
```sql
SELECT alert_level, COUNT(*), AVG(score) FROM burnout_scores GROUP BY alert_level;
```

### Chat activity
```sql
SELECT COUNT(*), COUNT(DISTINCT user_id) FROM chat_history;
```

## Regenerating Data

### Clear all data
```bash
python -c "
import sqlite3
conn = sqlite3.connect('database/pocketbuddy.db')
for table in ['expenses', 'health_logs', 'travel_logs', 'food_logs', 'routine_goals', 'recommendations', 'chat_history', 'burnout_scores', 'users', 'budget_meals']:
    conn.execute(f'DELETE FROM {table}')
conn.commit()
print('Database cleared')
"
```

### Repopulate with new data
```bash
python populate_db.py
```

### Verify data
```bash
python verify_db.py
```

## Data Characteristics

### Dates
- **Range:** March 1, 2026 - June 15, 2026
- **Distribution:** 145 (Mar), 155 (Apr), 183 (May), 67 (Jun)
- **Format:** YYYY-MM-DD ISO format

### Amounts (USD)
- **Expense Range:** $57 - $3,884
- **Average:** $1,061
- **Totals:** $583,451

### User Income
- **Range:** $30,000 - $100,000 monthly
- **Average:** $62,500
- **Realistic** for student/young professional scenarios

## Troubleshooting

### Database not found
- Check path: `C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db`
- Ensure database was initialized by Node.js setup

### Data seems outdated
- Run `python populate_db.py` to regenerate
- All dates are relative to June 2026

### Connection issues
- Ensure database isn't locked by another process
- WAL mode enabled for concurrent access

## Performance Notes

- **Total Records:** 824
- **Largest Table:** Expenses (550 rows)
- **Query Speed:** Milliseconds for typical queries
- **Index Status:** User_id and date indexed

## Files for Reference

- `populate_db.py` - Data generation script
- `verify_db.py` - Verification and reporting
- `DATABASE_POPULATION_SUMMARY.md` - Full documentation
- `QUICK_START_DB.md` - This file

---

**Last Updated:** June 14, 2026
**Status:** Ready for Development & Testing
