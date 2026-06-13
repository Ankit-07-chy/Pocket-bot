# Expense Management System 

Complete expense management system with budget planning, forecasting, trend analysis, and real-time alerts.

## Overview

The expense management system provides comprehensive functionality for:
- Managing user expenses with category support
- Analyzing spending patterns and trends
- Creating intelligent monthly budgets based on historical data
- Forecasting future expenses with confidence intervals
- Detecting anomalies and unusual spending patterns
- Real-time alerts for budget violations
- Seasonal pattern analysis

## Architecture

### Core Components

#### 1. **FirebaseExpenseService** (`firebase_service.py`)
Handles all Firebase Realtime Database operations for expense data.

**Key Methods:**
- `get_user_expenses(user_id)` - Fetch all expenses for a user
- `get_previous_month_expenses(user_id)` - Fetch previous month's expenses
- `get_current_month_expenses(user_id)` - Fetch current month's expenses
- `save_budget_plan(user_id, budget_plan)` - Save generated budget plan

---

#### 2. **ExpenseAnalyzer** (`expense_analyzer.py`)
Analyzes expense data and identifies spending patterns.

**Supported Categories:**
- Food (Groceries, restaurants, dining)
- Transport (Gas, public transit, taxi, parking)
- Entertainment (Movies, games, hobbies, subscriptions)
- Education (Books, courses, tuition)
- Health (Medical, gym, wellness)
- Utilities (Electricity, water, internet, phone)
- Others (Miscellaneous)

**Key Methods:**
- `categorize_expenses(expenses)` - Group expenses by category with totals
- `get_category_percentages(category_totals)` - Calculate spending distribution
- `analyze_previous_month(expenses)` - Generate comprehensive analysis
- `get_average_spending_per_category(expenses)` - Calculate per-category averages

---

#### 3. **BudgetPlanner** (`budget_planner.py`)
Creates intelligent monthly budget plans based on spending patterns.

**Key Methods:**
- `create_monthly_plan()` - Create proportional budget based on patterns
- `create_optimized_plan()` - Create budget with automatic savings allocation
- `_get_recommendation()` - Generate actionable budget recommendations
- `compare_with_target()` - Compare planned vs target budget

**Features:**
- ✅ Smart allocation based on historical spending
- ✅ Automatic 10% savings (customizable)
- ✅ Category-wise budget breakdown
- ✅ Budget normalization for constraints
- ✅ Intelligent recommendations

---

#### 4. **ExpenseInitializer** (`initialize_boundary.py`)
Main initialization interface for complete expense management setup.

**Key Methods:**
- `initialize_user_expenses()` - Complete initialization with budget plan
- `reinitialize_with_custom_budget()` - Adjust budget with custom amount
- `get_initialization_report()` - Retrieve detailed initialization data

**Initialization Flow:**
1. Fetches previous month expenses from Firebase
2. Analyzes spending patterns
3. Generates budget plan
4. Analyzes current month expenses
5. Saves plan to Firebase
6. Returns complete initialization data

---

#### 5. **TrendAnalyzer** (`trend_analyzer.py`) 
Analyzes spending trends over multiple months with advanced pattern detection.

**Key Methods:**
- `get_monthly_trend()` - Get spending trend over last N months
- `get_category_trend()` - Get trend for specific category
- `compare_months()` - Compare spending between two months
- `get_spending_velocity()` - Calculate daily spending rate & projections

**Features:**
- ✅ Multi-month trend analysis (configurable 1-24 months)
- ✅ Category-wise trend tracking
- ✅ Month-to-month comparison with deltas
- ✅ Spending velocity (average per day)
- ✅ Month-end projections
- ✅ Trend direction detection (increasing/decreasing/stable)
- ✅ Volatility measurement

**Algorithms:**
- Statistical mean, min, max calculations
- Standard deviation for volatility
- Trend direction determination
- Pace estimation

---

#### 6. **ExpenseForecaster** (`forecaster.py`) 
Predicts future expenses using historical data with statistical methods.

**Key Methods:**
- `forecast_next_month()` - Forecast next month's expenses
- `forecast_category()` - Forecast category-specific expenses
- `detect_anomalies()` - Detect unusual spending patterns
- `get_seasonal_forecast()` - Analyze seasonal spending patterns

**Features:**
- ✅ Next month expense prediction
- ✅ Confidence intervals (configurable 0.5-0.99)
- ✅ Category-level forecasts
- ✅ Anomaly detection (2σ threshold)
- ✅ Seasonal pattern identification
- ✅ Trend-adjusted predictions

**Algorithms:**
- Exponential smoothing (α=0.3)
- Weighted average (recent data weighted higher)
- Standard deviation anomaly detection
- Seasonal pattern analysis

---

#### 7. **AlertSystem** (`alert_system.py`) 
Real-time alerts for budget violations and overspending.

**Key Methods:**
- `check_category_overspending()` - Check category budget violations
- `check_total_budget_status()` - Check overall budget status
- `get_remaining_budget()` - Calculate remaining by category
- `save_alerts()` - Persist alerts to Firebase
- `acknowledge_alert()` - Mark alert as acknowledged

**Alert Severity Levels:**
- 🟢 LOW: 0-10% over budget
- 🟡 MEDIUM: 10-20% over budget
- 🔴 HIGH: 20-50% over budget
- ⛔ CRITICAL: 50%+ over budget

**Features:**
- ✅ Real-time budget monitoring
- ✅ Category-wise overspending detection
- ✅ Automatic alert generation
- ✅ Percentage exceeded calculation
- ✅ Alert acknowledgment tracking
- ✅ Firebase persistence

---

### Supporting Files

#### **schemas.py**
Pydantic models for request/response validation (15+ models)
- ✅ ExpenseCreate, ExpenseResponse
- ✅ BudgetPlanResponse
- ✅ InitializeUserRequest/Response
- ✅ MonthlyTrendResponse, CategoryTrendResponse
- ✅ ForecastResponse
- ✅ AlertResponse
- ✅ DashboardResponse
- ✅ HealthCheckResponse

#### **config.py**
Configuration management
- ✅ Firebase settings
- ✅ Expense categories
- ✅ Alert thresholds
- ✅ Feature flags
- ✅ Currency settings

#### **__init__.py**
Package initialization with proper exports
- ✅ All 7 components exported
- ✅ Proper relative imports

---

## Data Flow

### Complete Initialization Process

```
1. User Registration/Login
        ↓
2. ExpenseInitializer.initialize_user_expenses()
        ↓
3. Fetch Firebase Data
   ├─ Previous Month Expenses
   ├─ Current Month Expenses (so far)
   └─ Existing budget plans
        ↓
4. Analyze Spending Patterns
   ├─ Categorize by expense type
   ├─ Calculate percentages
   ├─ Identify trends
   └─ Calculate averages
        ↓
5. Generate Budget Plan
   ├─ Allocate budget based on patterns
   ├─ Set savings target (default 10%)
   ├─ Generate recommendations
   └─ Calculate remaining budget
        ↓
6. Detect Alerts
   ├─ Check category overspending
   ├─ Check total budget status
   └─ Generate alerts by severity
        ↓
7. Analyze Trends
   ├─ Get monthly trends
   ├─ Category trends
   └─ Calculate spending velocity
        ↓
8. Create Forecast
   ├─ Predict next month expenses
   ├─ Category forecasts
   └─ Detect anomalies
        ↓
9. Save to Firebase
   └─ Budget plan & alerts
        ↓
10. Return Complete Dashboard Data
```

## Usage Examples

### 1. Basic Initialization
```python
from src.expense_management import ExpenseInitializer

initializer = ExpenseInitializer()
result = initializer.initialize_user_expenses(
    user_id="user_123",
    current_month_budget=50000
)

print(result['budget_plan']['budget_breakdown'])
# Output: {'food': 14850, 'transport': 8900, ...}
```

### 2. Analyze Spending Patterns
```python
from src.expense_management import ExpenseAnalyzer, FirebaseExpenseService

firebase = FirebaseExpenseService()
analyzer = ExpenseAnalyzer()

expenses = firebase.get_previous_month_expenses("user_123")
analysis = analyzer.analyze_previous_month(expenses)

print(f"Total Spent: ₹{analysis['total_spent']}")
print(f"Category Breakdown: {analysis['category_totals']}")
print(f"Spending %: {analysis['category_percentages']}")
```

### 3. Get Spending Trends
```python
from src.expense_management import TrendAnalyzer, FirebaseExpenseService

firebase = FirebaseExpenseService()
trends = TrendAnalyzer(firebase)

# Get 6-month trend
monthly_trend = trends.get_monthly_trend("user_123", months=6)
print(f"Trend: {monthly_trend['analysis']['trend']}")  # 'increasing'/'decreasing'

# Compare two months
comparison = trends.compare_months("user_123", "2024-01", "2024-02")
print(f"Difference: {comparison['comparison']['total_difference']}")

# Spending velocity
velocity = trends.get_spending_velocity("user_123")
print(f"Daily Average: ₹{velocity['daily_average']:.2f}")
print(f"Est. Month Total: ₹{velocity['estimated_month_total']:.2f}")
```

### 4. Forecast Future Expenses
```python
from src.expense_management import ExpenseForecaster, FirebaseExpenseService

firebase = FirebaseExpenseService()
forecaster = ExpenseForecaster(firebase)

# Next month forecast
forecast = forecaster.forecast_next_month("user_123", confidence=0.85)
print(f"Predicted Expense: ₹{forecast['forecasted_total']:.2f}")
print(f"Confidence: {forecast['confidence_level']*100}%")
print(f"Range: ₹{forecast['forecast_range']['low']:.2f} - ₹{forecast['forecast_range']['high']:.2f}")

# Category forecast
cat_forecast = forecaster.forecast_category("user_123", "food", months_ahead=3)
print(f"Food Forecast: {cat_forecast['forecast_values']}")

# Detect anomalies
anomalies = forecaster.detect_anomalies("user_123")
for anomaly in anomalies['anomalies']:
    print(f"{anomaly['type']}: {anomaly['message']}")

# Seasonal analysis
seasonal = forecaster.get_seasonal_forecast("user_123")
print(f"High Spending Months: {seasonal['high_spending_months']}")
```

### 5. Alert Management
```python
from src.expense_management import AlertSystem, FirebaseExpenseService

firebase = FirebaseExpenseService()
alert_sys = AlertSystem(firebase)

# Get budget status with alerts
budget_plan = {...}  # Get from firebase
current_expenses = firebase.get_current_month_expenses("user_123")

# Check for overspending
alerts = alert_sys.check_category_overspending("user_123", budget_plan, current_expenses)
for alert in alerts:
    print(f"[{alert.severity.upper()}] {alert.message}")

# Get remaining budget
remaining = alert_sys.get_remaining_budget(budget_plan, current_expenses)
for category, data in remaining.items():
    print(f"{category}: ₹{data['remaining']} (Used: {data['percentage_used']:.1f}%)")
```

### 6. Complete Dashboard
```python
from src.expense_management import (
    ExpenseInitializer, TrendAnalyzer, ExpenseForecaster, 
    AlertSystem, FirebaseExpenseService
)

firebase = FirebaseExpenseService()
initializer = ExpenseInitializer()
trends = TrendAnalyzer(firebase)
forecaster = ExpenseForecaster(firebase)
alerts = AlertSystem(firebase)

user_id = "user_123"

# Get all data
init_data = initializer.initialize_user_expenses(user_id)
trend_data = trends.get_monthly_trend(user_id)
forecast_data = forecaster.forecast_next_month(user_id)
alert_data = alerts.get_user_alerts(user_id)

dashboard = {
    'budget': init_data['budget_plan'],
    'previous_month': init_data['previous_month'],
    'current_month': init_data['current_month'],
    'trends': trend_data,
    'forecast': forecast_data,
    'alerts': alert_data
}
```

---

## Firebase Data Structure

Expected Firebase Realtime Database structure:

```
users/
  {user_id}/
    expenses/
      {expense_id_1}/
        date: "2024-01-15T10:30:00"
        category: "food"
        amount: 500
        description: "Lunch"
      {expense_id_2}/
        date: "2024-01-15T14:00:00"
        category: "transport"
        amount: 100
        description: "Bus fare"
    
    budget_plan/
      plan:
        food: 14850
        transport: 8900
        entertainment: 4500
        education: 9000
        health: 2850
        utilities: 4000
        others: 900
      total_budget: 50000
      spending_budget: 45000
      savings: 5000
      created_date: "2024-01-15T10:30:00"
      month: "2024-01"
    
    alerts/
      {alert_id}/
        alert_id: "alert_user_123_food_..."
        category: "food"
        message: "HIGH: food spending exceeded by 25.5%"
        severity: "high"
        current_amount: 18625
        budget_limit: 14850
        percentage_exceeded: 25.5
        created_at: "2024-01-15T10:30:00"
        acknowledged: false
```

---

## Features Overview

### ✅ Budget Management
- Smart allocation based on previous spending
- Automatic 10% savings (customizable)
- Category-wise budget breakdown
- Budget normalization for constraints
- Intelligent recommendations
- Custom budget support

### ✅ Expense Tracking
- 7 expense categories
- Real-time categorization
- Previous & current month tracking
- Category breakdown & percentages
- Average spending calculations

### ✅ Trend Analysis
- Multi-month analysis (1-24 months configurable)
- Category-wise trends
- Month-to-month comparison
- Spending velocity calculations
- Trend direction detection (↑/↓/→)
- Volatility measurement

### ✅ Forecasting
- Next month prediction
- Category-level forecasts
- Anomaly detection (2σ threshold)
- Seasonal pattern analysis
- Confidence intervals
- Trend-adjusted predictions

### ✅ Alert System
- Real-time budget monitoring
- 4 severity levels (Low/Medium/High/Critical)
- Category-wise overspending alerts
- Percentage exceeded calculation
- Alert persistence
- Acknowledgment tracking

### ✅ Error Handling
- Firebase connection failures
- Missing or invalid data
- Division by zero protection
- Category fallback to 'others'
- Graceful error messages
- Detailed error logging

---

```

---

## Integration

### FastAPI Application (main_api.py)

The module is integrated in `main_api.py` with 25+ REST API endpoints:

```
Health:         GET /health
                GET /api/v1/status

Initialize:     POST /api/v1/initialize
                POST /api/v1/reinitialize-budget

Expenses:       POST /api/v1/expenses
                GET /api/v1/expenses/{user_id}

Budget:         GET /api/v1/budget-plan/{user_id}
                GET /api/v1/remaining-budget/{user_id}

Alerts:         GET /api/v1/alerts/{user_id}
                POST /api/v1/alerts/{user_id}/{alert_id}/acknowledge
                GET /api/v1/anomalies/{user_id}

Trends:         GET /api/v1/trends/monthly/{user_id}
                GET /api/v1/trends/category/{user_id}/{category}
                GET /api/v1/trends/compare
                GET /api/v1/trends/velocity/{user_id}

Forecast:       GET /api/v1/forecast/next-month/{user_id}
                GET /api/v1/forecast/category/{user_id}/{category}
                GET /api/v1/forecast/seasonal/{user_id}

Dashboard:      GET /api/v1/dashboard/{user_id}
```

---

## Configuration

### Environment Variables
```env
FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=serviceAccountKey.json
LOG_LEVEL=INFO
DEFAULT_CURRENCY=INR
```

### Feature Flags (config.py)
```python
ENABLE_ALERTS = True
ENABLE_RECOMMENDATIONS = True
ENABLE_ML_PREDICTIONS = False  # Future
ENABLE_MULTI_CURRENCY = False  # Future
```

---

## Performance Characteristics

### Response Times (Typical)
- Expense analysis: < 100ms
- Budget planning: < 50ms
- Trend analysis (6 months): < 200ms
- Forecasting: < 150ms
- Full dashboard: < 500ms

### Memory Efficient
- Lazy initialization
- Generator-based iterations
- Minimal data copies
- Firebase streaming ready

### Scalable Design
- Independent components
- No circular dependencies
- Factory-based initialization
- Mock-able services

---

## Security & Best Practices

### ✅ Implemented
- Firebase authentication support
- Input validation via Pydantic
- No hardcoded secrets
- Environment variable configuration
- Error message filtering
- Secure data handling

### 📋 Recommended
- Add user authentication layer
- Configure Firebase security rules
- Enable request logging
- Add rate limiting
- Implement audit trails
- Use HTTPS in production

---

## Future Enhancements

- [ ] Machine learning-based budget optimization
- [ ] Multi-currency support
- [ ] Recurring expense tracking
- [ ] Budget goal setting & tracking
- [ ] Receipt scanning & OCR
- [ ] Mobile app integration
- [ ] Email/SMS notifications
- [ ] Advanced reporting & analytics
- [ ] Budget sharing for families
- [ ] Integration with banking APIs

---

**Last Updated**: 13 June 2026
**Version**: 1.0.0
