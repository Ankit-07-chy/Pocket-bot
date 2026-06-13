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
Pocket-bot/
├── server/
│   ├── index.js              # Express server entry point
│   ├── database/
│   │   ├── setup.js          # Database schema (9 tables)
│   │   └── seed.js           # Budget meals seed data (40+ meals)
│   ├── middleware/
│   │   └── auth.js           # JWT authentication middleware
│   └── routes/
│       ├── auth.js           # Register, login, profile
│       ├── expenses.js       # Feature 1: Expense tracking
│       ├── food.js           # Feature 2: Food recommendations
│       ├── travel.js         # Feature 3: Travel options
│       ├── burnout.js        # Feature 4: Burnout detection
│       ├── routine.js        # Feature 5: Healthy routine
│       └── support.js        # Feature 6: AI support chat
├── client/
│   ├── public/index.html
│   └── src/
│       ├── index.js          # React entry point
│       ├── App.js            # Router + sidebar layout
│       ├── api.js            # API helper functions
│       ├── styles.css        # Global styles
│       └── pages/
│           ├── Login.js
│           ├── Register.js
│           ├── Dashboard.js
│           ├── Expenses.js
│           ├── FoodPage.js
│           ├── TravelPage.js
│           ├── BurnoutPage.js
│           ├── RoutinePage.js
│           ├── ChatPage.js
│           └── Profile.js
├── .env
├── .env.example
└── package.json
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
