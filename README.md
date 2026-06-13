# 🎒 PocketBuddy

**Student wellness and budget companion** — tracks expenses, recommends food, suggests travel options, detects burnout, builds healthy routines, and provides personalized AI support.

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Expense Management** | Track spending, categorize, get alerts when overspending |
| 2 | **Recommended Food** | Budget meal suggestions based on your spending patterns |
| 3 | **Travel Options** | Find cheaper transport, identify patterns, calculate savings |
| 4 | **Burnout Detection** | Daily check-ins, baseline comparison, early warning system |
| 5 | **Healthy Routine** | Gradual habit building with 4-week progressive goals |
| 6 | **Personalized Support** | AI chat that knows your data and gives tailored advice |

## Tech Stack

- **Backend:** Node.js, Express, SQLite (better-sqlite3)
- **Frontend:** React, React Router
- **Auth:** JWT (JSON Web Tokens)
- **Database:** 8 core tables + 1 reference table (budget meals)

## Getting Started

### Prerequisites
- Node.js 18+ installed
- npm or yarn

### Installation

```bash
# 1. Install server dependencies
npm install

# 2. Install client dependencies
cd client && npm install && cd ..

# Or do both at once:
npm run install:all
```

### Running the App

```bash
# Start the backend server (port 5000)
npm start

# In a separate terminal, start the React frontend (port 3000)
npm run dev:client
```

Then open http://localhost:3000 in your browser.

### Environment Variables

Copy `.env.example` to `.env` and configure:

```
PORT=5000
JWT_SECRET=your_secret_key_here
DB_PATH=./database/pocketbuddy.db
```

## API Endpoints

All protected endpoints require `Authorization: Bearer <token>` header.

### Auth
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Login
- `GET /api/auth/profile` — Get profile
- `PUT /api/auth/profile` — Update profile

### Expenses
- `POST /api/expenses` — Add expense
- `GET /api/expenses` — List expenses
- `GET /api/expenses/summary` — Spending summary
- `GET /api/expenses/trends` — 7/30-day trends
- `DELETE /api/expenses/:id` — Delete expense

### Food
- `POST /api/food/log` — Log meal
- `GET /api/food/log` — Get food log
- `GET /api/food/recommendations` — Budget meal suggestions
- `GET /api/food/budget-analysis` — Spending vs budget analysis

### Travel
- `POST /api/travel/log` — Log trip
- `GET /api/travel/options` — Alternative transport options
- `GET /api/travel/savings` — Savings potential
- `GET /api/travel/patterns` — Regular route patterns

### Burnout
- `POST /api/health/checkin` — Daily wellness check-in
- `GET /api/burnout/score` — Current burnout score
- `GET /api/burnout/alert` — Active warnings
- `GET /api/burnout/trends` — 30-day trend data
- `GET /api/burnout/recommendations` — Recovery suggestions

### Routine
- `POST /api/routine/goal` — Set wellness goal
- `GET /api/routine/plan` — Get weekly plan
- `POST /api/routine/checkin` — Log routine completion
- `GET /api/routine/progress` — Track progress
- `GET /api/routine/tips` — Daily tips

### Support
- `POST /api/chat` — Send message to AI
- `GET /api/chat/history` — Chat history
- `GET /api/support/suggestions` — Personalized tips
- `GET /api/support/emergency` — Crisis resources
- `POST /api/support/feedback` — Rate advice helpfulness

## Project Structure
```
poket-bot
├─ .python-version
├─ backend
│  ├─ app.py
│  ├─ PROJECT.md
│  ├─ src
│  │  ├─ burnout_detection
│  │  ├─ expense_management
│  │  │  ├─ alert_system.py
│  │  │  ├─ budget_planner.py
│  │  │  ├─ config.py
│  │  │  ├─ expense_analyzer.py
│  │  │  ├─ firebase_service.py
│  │  │  ├─ forecaster.py
│  │  │  ├─ initialize_boundary.py
│  │  │  ├─ README.md
│  │  │  ├─ schemas.py
│  │  │  ├─ trend_analyzer.py
│  │  │  └─ __init__.py
│  │  ├─ food_recommendation
│  │  ├─ health_routine
│  │  ├─ main_api.py
│  │  ├─ personalised_support
│  │  │  ├─ api_routes.py
│  │  │  ├─ ARCHITECTURE.md
│  │  │  ├─ chat_manager.py
│  │  │  ├─ config.py
│  │  │  ├─ langchain_chatbot.py
│  │  │  ├─ llm_provider.py
│  │  │  ├─ peer_support.py
│  │  │  ├─ project.md
│  │  │  ├─ prompts.py
│  │  │  ├─ README.md
│  │  │  ├─ rule_based_support.py
│  │  │  ├─ schemas.py
│  │  │  ├─ storage.py
│  │  │  └─ __init__.py
│  │  ├─ travel_recommendation
│  │  └─ __init__.py
│  └─ __init__.py
├─ client
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ public
│  │  └─ index.html
│  └─ src
│     ├─ api.js
│     ├─ App.js
│     ├─ firebase.js
│     ├─ index.js
│     ├─ pages
│     │  ├─ BurnoutPage.js
│     │  ├─ ChatPage.js
│     │  ├─ Dashboard.js
│     │  ├─ Expenses.js
│     │  ├─ FoodPage.js
│     │  ├─ Login.js
│     │  ├─ Profile.js
│     │  ├─ Register.js
│     │  ├─ RoutinePage.js
│     │  └─ TravelPage.js
│     └─ styles.css
├─ database
├─ frontend
├─ main.py
├─ package-lock.json
├─ package.json
├─ pyproject.toml
├─ README.md
├─ server
│  ├─ database
│  │  ├─ seed.js
│  │  └─ setup.js
│  ├─ firebase
│  │  ├─ admin.js
│  │  └─ README.md
│  ├─ index.js
│  ├─ middleware
│  │  └─ auth.js
│  └─ routes
│     ├─ auth.js
│     ├─ burnout.js
│     ├─ expenses.js
│     ├─ food.js
│     ├─ routine.js
│     ├─ support.js
│     └─ travel.js
└─ uv.lock

```

## Algorithms

### Burnout Score (0-10+)
Compares current metrics to the student's personal baseline (first 7 days):
- Sleep dropped 1.5+ hrs below baseline → +2 points
- Stress rose 2+ points above baseline → +2 points
- Exercise < 2 days in last 7 → +1 point
- Mood = overwhelmed → +2 points

**Alert levels:** 0-3 Good | 4-6 Moderate | 7-9 High | 10+ Crisis

### Expense Alerts
Triggers when today's spending > 7-day daily average × 1.5

### Routine Building
Gradual 4-week progression toward goals (25% improvement per week)

## License

MIT

