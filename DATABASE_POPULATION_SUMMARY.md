# PocketBuddy Database Population Report

## Executive Summary

Successfully populated the SQLite database (`pocketbuddy.db`) with **824 comprehensive dummy records** across 10 tables. All data is realistic, properly distributed, and ready for development and testing.

**Database Location:** `C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db`

---

## Population Results

### Overall Statistics
- **Total Records:** 824
- **Date Range:** March 1, 2026 - June 15, 2026
- **Number of Users:** 6 active test users
- **Total Expenses:** 550 transactions
- **Total Expenses Amount:** $583,451.09

---

## Table-by-Table Breakdown

### 1. Users Table (6 records)

Diverse user profiles with realistic attributes:

| User | Name | Email | Major | Year | Monthly Income | Daily Budget |
|------|------|-------|-------|------|--------|---|
| 915 | Alice Johnson | alice@email.com | Computer Science | 2 | $50,000 | $1,200 |
| 916 | Bob Smith | bob@email.com | Business | 3 | $75,000 | $1,800 |
| 917 | Carol Davis | carol@email.com | Engineering | 1 | $40,000 | $900 |
| 918 | David Wilson | david@email.com | Medicine | 4 | $100,000 | $2,500 |
| 919 | Emma Brown | emma@email.com | Arts | 2 | $30,000 | $700 |
| 920 | Frank Miller | frank@email.com | Finance | 3 | $80,000 | $2,000 |

**Key Metrics:**
- Income Range: $30,000 - $100,000
- Average Monthly Income: $62,500
- Daily Budget Range: $700 - $2,500

---

### 2. Expenses Table (550 records)

Comprehensive expense tracking spanning 3+ months:

**Summary by Category:**
- **Utilities:** 78 transactions, $185,137.24 (avg: $2,373.55)
- **Education:** 76 transactions, $132,123.32 (avg: $1,738.46)
- **Health:** 74 transactions, $94,316.31 (avg: $1,274.54)
- **Entertainment:** 77 transactions, $65,522.37 (avg: $850.94)
- **Others:** 93 transactions, $51,514.91 (avg: $553.92)
- **Food:** 70 transactions, $32,760.35 (avg: $468.00)
- **Transport:** 82 transactions, $22,076.59 (avg: $269.23)

**Monthly Distribution:**
- March 2026: 145 expenses ($138,036.51)
- April 2026: 155 expenses ($176,677.47)
- May 2026: 183 expenses ($207,821.85)
- June 2026: 67 expenses ($60,915.26)

**Expense Statistics:**
- Total Spent: $583,451.09
- Average Expense: $1,060.82
- Maximum Expense: $3,883.64
- Minimum Expense: $57.35

**Distribution by User:**
- User 915 (Alice): 97 expenses ($102,546.42)
- User 916 (Bob): 98 expenses ($111,997.56)
- User 917 (Carol): 77 expenses ($66,301.46)
- User 918 (David): 95 expenses ($98,126.84)
- User 919 (Emma): 86 expenses ($104,002.24)
- User 920 (Frank): 97 expenses ($100,476.57)

---

### 3. Health Logs Table (35 records)

Daily wellness tracking with realistic health metrics:

**Health Statistics:**
- Average Sleep: 6.5 hours
- Average Stress Level: 5.7/10
- Average Exercise: 66.2 minutes
- Date Coverage: June 2026 (comprehensive coverage)

**Tracked Metrics per Entry:**
- Sleep hours (4-10 range)
- Stress level (1-10 scale)
- Mood (happy, neutral, sad, stressed, anxious)
- Study hours
- Exercise minutes
- Social activity score
- Energy level
- Personal notes

---

### 4. Food Logs Table (50 records)

Meal and nutrition tracking across all meal types:

**Food Statistics:**
- Total Food Logs: 50 entries
- Total Food Cost: $10,247.62
- Average Food Cost: $204.95

**Distribution by Meal Type:**
- Breakfast: 18 entries (avg cost: $210.72)
- Lunch: 6 entries (avg cost: $186.52)
- Dinner: 12 entries (avg cost: $193.33)
- Snack: 14 entries (avg cost: $215.39)

**Data Points per Entry:**
- User ID
- Date
- Meal type (breakfast, lunch, dinner, snack)
- Food name
- Cost
- Calories
- Homemade flag (0/1)

---

### 5. Travel Logs Table (40 records)

Transportation and mobility tracking:

**Travel Statistics:**
- Total Travel Logs: 40 entries
- Total Travel Cost: $6,254.24
- Average Trip Cost: $156.36

**Distribution by Mode:**
- Bike: 10 trips ($1,421.09)
- Auto: 8 trips ($1,220.93)
- Car: 5 trips ($1,137.92)
- Train: 6 trips ($1,073.76)
- Walk: 6 trips ($729.51)
- Metro: 5 trips ($671.03)

**Data Points per Entry:**
- Origin and destination locations
- Transportation mode
- Date
- Cost
- Duration in minutes

---

### 6. Routine Goals Table (25 records)

Personal wellness and productivity goals:

**Distribution by Goal Type:**
- Exercise: 8 goals (avg current: 63.54, target: 101.14)
- Study: 4 goals (avg current: 36.56, target: 90.01)
- Sleep: 4 goals (avg current: 64.96, target: 89.78)
- Budget: 5 goals (avg current: 66.50, target: 115.29)
- Reading: 2 goals (avg current: 31.37, target: 114.63)
- Meditation: 2 goals (avg current: 64.24, target: 104.05)

**Status Distribution:**
- Active goals
- Completed goals
- Paused goals

**Tracking Features:**
- Week-by-week progress
- Current vs. target values
- Weekly targets

---

### 7. Recommendations Table (20 records)

AI-generated advice and budgeting plans:

**Distribution by Type:**
- Budget Plans: 5 records
- Spending Alerts: 5 records
- Goal Suggestions: 5 records
- Health Tips: 5 records

**Data Structure:**
- JSON-formatted recommendations
- User feedback tracking
- Helpfulness rating (0/1/NULL)
- Creation date and timestamp

---

### 8. Chat History Table (40 records)

AI support interactions and conversations:

**Chat Statistics:**
- Total Chat Sessions: 40
- Users with Chat: 6 (100% coverage)
- Date Coverage: 90 days span

**Sample Conversation Topics:**
- Expense reduction strategies
- Budget tracking questions
- Spending pattern analysis
- Goal progress inquiries
- Health and wellness advice
- Sleep and stress management

**Data per Session:**
- User message (question)
- AI response (advice)
- Context JSON (session info, priority)
- Timestamp

---

### 9. Burnout Scores Table (26 records)

Wellness assessment and burnout detection:

**Alert Level Distribution:**
- Critical: 14 assessments (avg score: 12.1)
- Warning: 10 assessments (avg score: 46.1)
- Good: 2 assessments (avg score: 66.5)

**Baseline Metrics:**
- Baseline Sleep: 7-8 hours
- Baseline Stress: 3-5/10
- Baseline Exercise: 30-60 minutes

**Current Metrics:**
- Current Sleep: 4-8 hours
- Current Stress: 3-8/10
- Current Exercise: 0-60 minutes

**Score Calculation:**
- Based on deviation from baseline
- Range: 0-100
- Auto-generated alert levels based on score

---

### 10. Budget Meals Table (32 records)

Reference database of affordable meal options:

**Budget Meal Statistics:**
- Total Meal Records: 32
- Average Cost: $163.40
- Average Calories: 576

**Meal Categories:**
- Breakfast options
- Lunch options
- Dinner options
- Snack options

**Sample Meals:**
- Dal and Rice
- Pasta Primavera
- Fried Rice
- Stir-fried Vegetables
- Lentil Soup
- Bean Burrito
- Chickpea Curry
- Egg Fried Rice
- And 24 more options

**Data per Meal:**
- Name
- Cost
- Calories
- Category (meal type)
- Dietary tags (vegetarian, vegan, etc.)
- Prep time in minutes
- Recipe instructions
- Vegetarian/Vegan flags

---

## Data Quality Features

### Realistic Distribution
- Expense amounts vary by category (food: $100-800, utilities: $1000-4000)
- Dates span 3+ months with monthly distribution
- Multiple transactions per user per category
- Mixed user activity patterns

### Referential Integrity
- All expenses linked to valid users
- All health/food/travel logs reference existing users
- Proper date ranges and timestamps
- No orphaned records

### Diverse Content
- Multiple majors and user types
- Various meal types and transportation modes
- Different goal types and categories
- Mix of alert levels and assessment scores

### Volume Requirements Met
- **Expenses:** 550 records (exceeds 500+ requirement)
- **Users:** 6 users as specified
- **Health Logs:** 35 records
- **Food Logs:** 50 records
- **Travel Logs:** 40 records
- **Recommendations:** 20 records
- **Chat History:** 40 records
- **Routine Goals:** 25 records
- **Burnout Scores:** 26 records
- **Budget Meals:** 32 records

---

## Scripts and Files

### Population Script
- **File:** `populate_db.py`
- **Location:** Project root directory
- **Features:**
  - Automatic user creation
  - Bulk expense generation
  - Realistic data distribution
  - Comprehensive verification

### Verification Script
- **File:** `verify_db.py`
- **Location:** Project root directory
- **Features:**
  - Complete data inventory
  - Statistical analysis
  - Category breakdown
  - User-level reporting

---

## How to Use

### Running the Population Script
```bash
python populate_db.py
```

The script will:
1. Create 6 users with diverse profiles
2. Generate 550+ expense records
3. Populate all supplementary tables
4. Verify data integrity
5. Display summary statistics

### Running Verification
```bash
python verify_db.py
```

Generates a comprehensive report including:
- User details and counts
- Expense analysis by category and user
- Health and wellness metrics
- Food and travel statistics
- Goal progress tracking
- Overall database statistics

### Clearing Data for Rerun
```python
import sqlite3
conn = sqlite3.connect('database/pocketbuddy.db')
cursor = conn.cursor()

tables = ['expenses', 'health_logs', 'travel_logs', 'food_logs', 
          'routine_goals', 'recommendations', 'chat_history', 
          'burnout_scores', 'users', 'budget_meals']

for table in tables:
    cursor.execute(f'DELETE FROM {table}')
    conn.commit()
```

---

## Validation Checklist

- [x] Database file exists and is accessible
- [x] All 10 tables created with correct schema
- [x] 500+ expense records generated (550 created)
- [x] 6 users with realistic attributes
- [x] 3-4 month date span (March-June 2026)
- [x] Multiple categories per user
- [x] Realistic amount ranges by category
- [x] Health logs with complete metrics
- [x] Food logs with meal tracking
- [x] Travel logs with transportation modes
- [x] Routine goals with progress tracking
- [x] Recommendations with feedback
- [x] Chat history with Q&A pairs
- [x] Burnout scores with alert levels
- [x] Budget meals reference data
- [x] All referential constraints satisfied
- [x] Data verification completed
- [x] Summary statistics generated

---

## Performance Notes

- **Database Size:** Optimized SQLite with WAL mode enabled
- **Insert Speed:** ~8-10 records per second
- **Query Performance:** Indexes on user_id and date fields
- **Scalability:** Can easily handle 10x-100x more records

---

## Next Steps

1. **Development:** Use this data for API testing and feature development
2. **Testing:** Run integration tests against the populated database
3. **Demonstrations:** Show realistic data in UI mockups and demos
4. **Analysis:** Run analytics to verify forecasting and trend detection
5. **Reproduction:** Re-run `populate_db.py` anytime to reset with fresh data

---

**Generation Date:** June 14, 2026
**Database Path:** `C:\Users\ankit\Desktop\poket-bot\database\pocketbuddy.db`
**Status:** ✓ Complete and Verified
