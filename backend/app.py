"""
FastAPI Application for Expense Management System
Main entry point for the API server
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv

from src.expense_management import (
    ExpenseInitializer,
    ExpenseAnalyzer,
    BudgetPlanner,
    FirebaseExpenseService,
    TrendAnalyzer,
    ExpenseForecaster,
    AlertSystem
)
from src.expense_management.schemas import (
    ExpenseCreate,
    ExpenseResponse,
    InitializeUserRequest,
    InitializeUserResponse,
    CustomBudgetRequest,
    BudgetPlanResponse,
    MonthlyTrendResponse,
    CategoryTrendResponse,
    ForecastResponse,
    AlertResponse,
    RemainingBudgetResponse,
    DashboardResponse,
    HealthCheckResponse,
    ErrorResponse
)

# Load environment variables
load_dotenv()

# SQLite is used — no Firebase initialization needed

# Initialize FastAPI
app = FastAPI(
    title="Poket Bot - Expense Manager",
    description="Complete expense management system with budget planning and forecasting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
firebase_service = FirebaseExpenseService()
expense_analyzer = ExpenseAnalyzer()
budget_planner = BudgetPlanner(expense_analyzer)
initializer = ExpenseInitializer()
trend_analyzer = TrendAnalyzer(firebase_service)
forecaster = ExpenseForecaster(firebase_service)
alert_system = AlertSystem(firebase_service)


# ==================== Health Check ====================
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# ==================== Initialization Endpoints ====================
@app.post("/api/users/initialize", response_model=InitializeUserResponse)
async def initialize_user(request: InitializeUserRequest):
    """Initialize user expense management and create budget plan"""
    try:
        result = initializer.initialize_user_expenses(
            user_id=request.user_id,
            current_month_budget=request.current_month_budget
        )

        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))

        return {
            "user_id": result['user_id'],
            "success": result['success'],
            "previous_month": result['previous_month'],
            "current_month": result['current_month'],
            "budget_plan": result['budget_plan']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/budget/custom", response_model=BudgetPlanResponse)
async def set_custom_budget(user_id: str, request: CustomBudgetRequest):
    """Set custom budget for user"""
    try:
        result = initializer.reinitialize_with_custom_budget(
            user_id=user_id,
            custom_budget=request.custom_budget,
            savings_target=request.savings_target
        )

        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))

        return result['budget_plan']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Expense Endpoints ====================
@app.get("/api/users/{user_id}/expenses/current-month")
async def get_current_month_expenses(user_id: str):
    """Get current month expenses"""
    try:
        expenses = firebase_service.get_current_month_expenses(user_id)
        analysis = expense_analyzer.analyze_previous_month(expenses)

        return {
            "user_id": user_id,
            "month": datetime.now().strftime('%Y-%m'),
            "total_spent": analysis['total_spent'],
            "category_breakdown": analysis['category_totals'],
            "category_percentages": analysis['category_percentages'],
            "expense_count": analysis['expense_count'],
            "expenses": expenses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/expenses/previous-month")
async def get_previous_month_expenses(user_id: str):
    """Get previous month expenses"""
    try:
        expenses = firebase_service.get_previous_month_expenses(user_id)
        analysis = expense_analyzer.analyze_previous_month(expenses)

        return {
            "user_id": user_id,
            "total_spent": analysis['total_spent'],
            "category_breakdown": analysis['category_totals'],
            "category_percentages": analysis['category_percentages'],
            "expense_count": analysis['expense_count'],
            "expenses": expenses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Budget Endpoints ====================
@app.get("/api/users/{user_id}/budget/remaining")
async def get_remaining_budget(user_id: str):
    """Get remaining budget for each category"""
    try:
        current_expenses = firebase_service.get_current_month_expenses(user_id)
        previous_expenses = firebase_service.get_previous_month_expenses(user_id)

        previous_analysis = expense_analyzer.analyze_previous_month(previous_expenses)
        budget_plan = budget_planner.create_optimized_plan(
            previous_month_analysis=previous_analysis,
            current_month_total=previous_analysis['total_spent']
        )

        remaining = alert_system.get_remaining_budget(budget_plan, current_expenses)

        return {
            "user_id": user_id,
            "month": datetime.now().strftime('%Y-%m'),
            "remaining_budget": remaining
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/budget/status")
async def get_budget_status(user_id: str):
    """Get current budget status and alerts"""
    try:
        current_expenses = firebase_service.get_current_month_expenses(user_id)
        previous_expenses = firebase_service.get_previous_month_expenses(user_id)

        previous_analysis = expense_analyzer.analyze_previous_month(previous_expenses)
        budget_plan = budget_planner.create_optimized_plan(
            previous_month_analysis=previous_analysis,
            current_month_total=previous_analysis['total_spent']
        )

        # Check alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, budget_plan, current_expenses
        )
        total_alert = alert_system.check_total_budget_status(
            user_id, budget_plan, current_expenses
        )

        remaining = alert_system.get_remaining_budget(budget_plan, current_expenses)

        return {
            "user_id": user_id,
            "month": datetime.now().strftime('%Y-%m'),
            "budget_plan": budget_plan,
            "remaining_budget": remaining,
            "category_alerts": [alert.to_dict() for alert in category_alerts],
            "total_budget_alert": total_alert.to_dict() if total_alert else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Trend Analysis Endpoints ====================
@app.get("/api/users/{user_id}/trends/monthly", response_model=MonthlyTrendResponse)
async def get_monthly_trends(user_id: str, months: int = Query(6, ge=1, le=24)):
    """Get monthly spending trends"""
    try:
        result = trend_analyzer.get_monthly_trend(user_id, months)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/trends/category/{category}", response_model=CategoryTrendResponse)
async def get_category_trends(user_id: str, category: str, months: int = Query(6, ge=1, le=24)):
    """Get spending trend for specific category"""
    try:
        result = trend_analyzer.get_category_trend(user_id, category, months)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/trends/velocity")
async def get_spending_velocity(user_id: str):
    """Get daily spending velocity and month-end forecast"""
    try:
        result = trend_analyzer.get_spending_velocity(user_id)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/trends/compare")
async def compare_months(user_id: str, month1: str, month2: str):
    """Compare spending between two months (format: YYYY-MM)"""
    try:
        result = trend_analyzer.compare_months(user_id, month1, month2)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Forecast Endpoints ====================
@app.get("/api/users/{user_id}/forecast/next-month", response_model=ForecastResponse)
async def forecast_next_month(user_id: str, confidence: float = Query(0.85, ge=0.5, le=0.99)):
    """Forecast next month's expenses"""
    try:
        result = forecaster.forecast_next_month(user_id, confidence)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/forecast/category/{category}")
async def forecast_category(user_id: str, category: str, months_ahead: int = Query(1, ge=1, le=12)):
    """Forecast expenses for specific category"""
    try:
        result = forecaster.forecast_category(user_id, category, months_ahead)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/forecast/anomalies")
async def detect_anomalies(user_id: str):
    """Detect unusual spending patterns"""
    try:
        result = forecaster.detect_anomalies(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/forecast/seasonal")
async def get_seasonal_forecast(user_id: str):
    """Get seasonal spending patterns"""
    try:
        result = forecaster.get_seasonal_forecast(user_id)

        if 'error' in result or 'warning' in result:
            raise HTTPException(status_code=400, detail=result.get('error') or result.get('warning'))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Alert Endpoints ====================
@app.get("/api/users/{user_id}/alerts")
async def get_user_alerts(user_id: str):
    """Get all active alerts for user"""
    try:
        alerts = alert_system.get_user_alerts(user_id)
        return {
            "user_id": user_id,
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/users/{user_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(user_id: str, alert_id: str):
    """Mark alert as acknowledged"""
    try:
        success = alert_system.acknowledge_alert(user_id, alert_id)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to acknowledge alert")

        return {"success": True, "message": "Alert acknowledged"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Dashboard Endpoint ====================
@app.get("/api/users/{user_id}/dashboard")
async def get_dashboard(user_id: str):
    """Get comprehensive dashboard with all data"""
    try:
        # Fetch data
        current_expenses = firebase_service.get_current_month_expenses(user_id)
        previous_expenses = firebase_service.get_previous_month_expenses(user_id)

        # Analyze
        current_analysis = expense_analyzer.analyze_previous_month(current_expenses)
        previous_analysis = expense_analyzer.analyze_previous_month(previous_expenses)

        # Budget plan
        budget_plan = budget_planner.create_optimized_plan(
            previous_month_analysis=previous_analysis,
            current_month_total=previous_analysis['total_spent']
        )

        # Alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, budget_plan, current_expenses
        )
        total_alert = alert_system.check_total_budget_status(
            user_id, budget_plan, current_expenses
        )

        all_alerts = [alert.to_dict() for alert in category_alerts]
        if total_alert:
            all_alerts.append(total_alert.to_dict())

        # Remaining budget
        remaining = alert_system.get_remaining_budget(budget_plan, current_expenses)

        # Trends
        trends = trend_analyzer.get_monthly_trend(user_id, 6)

        # Forecast
        forecast = forecaster.forecast_next_month(user_id, 0.85)

        # Velocity
        velocity = trend_analyzer.get_spending_velocity(user_id)

        return {
            "user_id": user_id,
            "previous_month_summary": {
                "total_spent": previous_analysis['total_spent'],
                "category_breakdown": previous_analysis['category_totals'],
                "expense_count": previous_analysis['expense_count']
            },
            "current_month_summary": {
                "total_spent_so_far": current_analysis['total_spent'],
                "category_breakdown": current_analysis['category_totals'],
                "category_percentages": current_analysis['category_percentages'],
                "expense_count": current_analysis['expense_count']
            },
            "budget_plan": budget_plan,
            "alerts": all_alerts,
            "remaining_budget": remaining,
            "trend_analysis": trends.get('analysis', {}),
            "forecast": forecast,
            "spending_velocity": velocity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Error Handler ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
