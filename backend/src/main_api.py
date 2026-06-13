"""
FastAPI application - Poket Bot
Production-ready version with Expense Management & Personalized Support
Organized by feature sections for better maintainability
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ==================== PRODUCTION-READY PATH HANDLING ====================
def setup_project_paths():
    """Automatically configure Python paths for production"""
    current_file = Path(__file__).resolve()

    # Walk up to find the project root (the folder that contains 'backend/')
    project_root = current_file.parent
    for _ in range(4):
        if (project_root / 'backend').exists():
            break
        project_root = project_root.parent

    # backend/src must be on sys.path so packages like
    # `personalised_support` and `expense_management` are importable directly.
    backend_src = project_root / 'backend' / 'src'
    for p in [str(project_root), str(backend_src)]:
        if p not in sys.path:
            sys.path.insert(0, p)

    # NOTE: Do NOT add the sub-package folders themselves (e.g. personalised_support/)
    # to sys.path — that breaks relative imports inside those packages.

    return project_root

# Setup paths before any other imports
PROJECT_ROOT = setup_project_paths()
print(f"✅ Project Root: {PROJECT_ROOT}")
print(f"✅ Python Path: {sys.path[0]}")

# ==================== CORE IMPORTS ====================
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ==================== EXPENSE MANAGEMENT IMPORTS ====================
expense_initializer = None
alert_system = None
trend_analyzer = None
forecaster = None
firebase_service = None
analyzer = None
planner = None

try:
    from backend.src.expense_management.initialize_boundary import ExpenseInitializer
    from backend.src.expense_management.alert_system import AlertSystem
    from backend.src.expense_management.trend_analyzer import TrendAnalyzer
    from backend.src.expense_management.forecaster import ExpenseForecaster
    from backend.src.expense_management.firebase_service import FirebaseExpenseService
    from backend.src.expense_management.expense_analyzer import ExpenseAnalyzer
    from backend.src.expense_management.budget_planner import BudgetPlanner
    from backend.src.expense_management.schemas import (
        InitializeUserRequest, InitializeUserResponse,
        CustomBudgetRequest, BudgetPlanResponse,
        MonthlyTrendResponse, CategoryTrendResponse,
        ForecastResponse, AlertResponse,
        RemainingBudgetResponse, DashboardResponse,
        HealthCheckResponse, ErrorResponse, ExpenseCreate
    )
    print("✅ Expense Management imports successful")

    firebase_service = FirebaseExpenseService()
    expense_initializer = ExpenseInitializer()
    alert_system = AlertSystem(firebase_service)
    trend_analyzer = TrendAnalyzer(firebase_service)
    forecaster = ExpenseForecaster(firebase_service)
    analyzer = ExpenseAnalyzer()
    planner = BudgetPlanner(analyzer)

except ImportError as e:
    print(f"⚠ First import attempt failed: {e}")

    try:
        expense_mgmt_path = PROJECT_ROOT / 'backend' / 'src' / 'expense_management'
        if str(expense_mgmt_path) not in sys.path:
            sys.path.insert(0, str(expense_mgmt_path))

        from expense_management.initialize_boundary import ExpenseInitializer
        from expense_management.alert_system import AlertSystem
        from expense_management.trend_analyzer import TrendAnalyzer
        from expense_management.forecaster import ExpenseForecaster
        from expense_management.firebase_service import FirebaseExpenseService
        from expense_management.expense_analyzer import ExpenseAnalyzer
        from expense_management.budget_planner import BudgetPlanner
        from expense_management.schemas import (
            InitializeUserRequest, InitializeUserResponse,
            CustomBudgetRequest, BudgetPlanResponse,
            MonthlyTrendResponse, CategoryTrendResponse,
            ForecastResponse, AlertResponse,
            RemainingBudgetResponse, DashboardResponse,
            HealthCheckResponse, ErrorResponse, ExpenseCreate
        )
        print("✅ Expense Management imports successful (direct path)")

        firebase_service = FirebaseExpenseService()
        expense_initializer = ExpenseInitializer()
        alert_system = AlertSystem(firebase_service)
        trend_analyzer = TrendAnalyzer(firebase_service)
        forecaster = ExpenseForecaster(firebase_service)
        analyzer = ExpenseAnalyzer()
        planner = BudgetPlanner(analyzer)

    except ImportError as e2:
        print(f"⚠ Expense Management services unavailable: {e2}")

        class MockService:
            def __init__(self, *args, **kwargs): pass
            def __getattr__(self, name):
                return lambda *args, **kwargs: {"mock": True, "message": f"Demo mode: {name} called"}

        firebase_service = MockService()
        expense_initializer = MockService()
        alert_system = MockService()
        trend_analyzer = MockService()
        forecaster = MockService()
        analyzer = MockService()
        planner = MockService()

        try:
            # pyrefly: ignore [missing-import]
            from schemas import (
                InitializeUserRequest, InitializeUserResponse,
                CustomBudgetRequest, BudgetPlanResponse,
                MonthlyTrendResponse, CategoryTrendResponse,
                ForecastResponse, AlertResponse,
                RemainingBudgetResponse, DashboardResponse,
                HealthCheckResponse, ErrorResponse, ExpenseCreate
            )
        except ImportError:
            class InitializeUserRequest(BaseModel): user_id: str; current_month_budget: float
            class InitializeUserResponse(BaseModel): success: bool; user_id: str
            class CustomBudgetRequest(BaseModel): user_id: str; custom_budget: float; savings_target: float = 0
            class HealthCheckResponse(BaseModel): status: str; timestamp: str; version: str
            class ExpenseCreate(BaseModel): amount: float; category: str; description: str = ""
            BudgetPlanResponse = dict
            MonthlyTrendResponse = dict
            CategoryTrendResponse = dict
            ForecastResponse = dict
            AlertResponse = dict
            RemainingBudgetResponse = dict
            DashboardResponse = dict
            ErrorResponse = dict

# ==================== PERSONALISED SUPPORT IMPORTS ====================
# The personalised_support package lives at backend/src/personalised_support/.
# backend/src is already on sys.path from setup_project_paths(), so we import
# it as a normal top-level package — no `src.` prefix needed.
support_router = None
chat_manager = None

try:
    from personalised_support.api_routes import router as support_router
    from personalised_support import chat_manager
    _llm_status = "operational" if chat_manager.ai_chatbot.llm else "limited (no LLM key)"
    print(f"✅ Personalised Support imported — AI chatbot: {_llm_status}")
except ImportError as e:
    print(f"⚠ Personalised Support not available: {e}")
    support_router = None
    chat_manager = None

# ==================== FIREBASE INITIALIZATION (removed — using SQLite) ====================
firebase_initialized = False  # kept for status endpoint compatibility

# ==================== FASTAPI APPLICATION SETUP ====================
app = FastAPI(
    title="Poket Bot API",
    description="Complete financial management system with expense tracking, budgeting, and AI-powered personalized support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Personalised Support routes (/api/support/...) ──────────────────────────
# Registered here so all 16 endpoints appear in /docs alongside the rest.
if support_router:
    app.include_router(support_router)
    print("✅ Support router attached — 16 endpoints at /api/support/*")
else:
    print("⚠ Support router not attached (import failed above)")

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║                         SYSTEM HEALTH & STATUS                                  ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "sqlite",
        "services_initialized": expense_initializer is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Poket Bot API",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "expense_management": "Track, analyze, and forecast expenses",
            "budget_planning": "Create and manage budgets with AI insights",
            "financial_alerts": "Get notified of budget overruns and anomalies",
            "personalized_support": "AI chatbot, rule-based guidance, and peer support"
        },
        "endpoints": {
            "health": "/health",
            "status": "/api/v1/status",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/api/v1/status")
async def system_status():
    """Get comprehensive system status and component information"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "components": {
            "database": {
                "status": "sqlite",
                "available": True
            },
            "expense_management": {
                "analyzer": "available" if analyzer is not None else "unavailable",
                "budget_planner": "available" if planner is not None else "unavailable",
                "alert_system": "available" if alert_system is not None else "unavailable",
                "trend_analyzer": "available" if trend_analyzer is not None else "unavailable",
                "forecaster": "available" if forecaster is not None else "unavailable"
            },
            "personalized_support": {
                "status": "available" if support_router is not None else "unavailable",
                "chat_manager": "initialized" if chat_manager is not None else "unavailable"
            }
        },
        "environment": {
            "project_root": str(PROJECT_ROOT),
            "python_path": sys.path[0]
        }
    }

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║                    EXPENSE MANAGEMENT FEATURE                                    ║
# ║        User initialization, expense tracking, budget management, alerts           ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

# ==================== USER INITIALIZATION ====================

@app.post("/api/v1/initialize", response_model=InitializeUserResponse)
async def initialize_user(request: InitializeUserRequest):
    """
    Initialize expense management for a new user.
    Fetches historical data and creates budget plan.
    """
    try:
        if expense_initializer is None:
            raise HTTPException(status_code=503, detail="ExpenseInitializer service not available")

        result = expense_initializer.initialize_user_expenses(
            user_id=request.user_id,
            current_month_budget=request.current_month_budget
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reinitialize-budget")
async def reinitialize_with_custom_budget(request: CustomBudgetRequest):
    """Reinitialize budget with custom amount and savings target"""
    try:
        if expense_initializer is None:
            raise HTTPException(status_code=503, detail="ExpenseInitializer service not available")

        result = expense_initializer.reinitialize_with_custom_budget(
            user_id=request.user_id,
            custom_budget=request.custom_budget,
            savings_target=request.savings_target
        )

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== EXPENSE TRACKING ====================

@app.post("/api/v1/expenses")
async def create_expense(user_id: str, expense: ExpenseCreate):
    """Create a new expense record"""
    try:
        if firebase_service is None:
            raise HTTPException(status_code=503, detail="Expense service not available")

        expense_id = firebase_service.add_expense(
            user_id=user_id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description or "",
            date=expense.date,
        )

        return {
            'success': True,
            'expense_id': expense_id,
            'data': {**expense.dict(), 'created_at': datetime.now().isoformat()}
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/expenses/{user_id}")
async def get_user_expenses(user_id: str):
    """Retrieve all expenses for a user"""
    try:
        if firebase_service is None:
            raise HTTPException(status_code=503, detail="Firebase service not available")

        expenses = firebase_service.get_user_expenses(user_id)
        return {
            'user_id': user_id,
            'expenses': expenses,
            'count': len(expenses) if expenses else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BUDGET PLANNING & MANAGEMENT ====================

@app.get("/api/v1/budget-plan/{user_id}")
async def get_budget_plan(user_id: str):
    """Retrieve the current budget plan for a user"""
    try:
        if firebase_service is None:
            raise HTTPException(status_code=503, detail="Expense service not available")

        plan = firebase_service.get_budget_plan(user_id)

        if not plan:
            raise HTTPException(status_code=404, detail="Budget plan not found")

        return {
            'user_id': user_id,
            'budget_plan': plan
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/remaining-budget/{user_id}")
async def get_remaining_budget(user_id: str):
    """Get remaining budget amount by category"""
    try:
        if firebase_service is None or alert_system is None:
            raise HTTPException(status_code=503, detail="Service not available")

        budget_data = firebase_service.get_budget_plan(user_id)
        current_expenses = firebase_service.get_current_month_expenses(user_id)

        if not budget_data:
            raise HTTPException(status_code=404, detail="Budget plan not found")

        plan = budget_data.get('plan', budget_data)
        remaining = alert_system.get_remaining_budget(plan, current_expenses)

        return {
            'user_id': user_id,
            'remaining_budget': remaining,
            'total_budget': plan.get('total_budget', 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ALERTS & ANOMALY DETECTION ====================

@app.get("/api/v1/alerts/{user_id}")
async def get_user_alerts(user_id: str):
    """Get all active alerts for a user"""
    try:
        if firebase_service is None or alert_system is None:
            raise HTTPException(status_code=503, detail="Service not available")

        budget_data = firebase_service.get_budget_plan(user_id)
        current_expenses = firebase_service.get_current_month_expenses(user_id)

        if not budget_data:
            raise HTTPException(status_code=404, detail="Budget plan not found")

        plan = budget_data.get('plan', budget_data)

        # Check for alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, plan, current_expenses
        )
        total_alert = alert_system.check_total_budget_status(
            user_id, plan, current_expenses
        )

        alerts = [alert.to_dict() for alert in category_alerts]
        if total_alert:
            alerts.append(total_alert.to_dict())

        return {
            'user_id': user_id,
            'alerts': alerts,
            'alert_count': len(alerts),
            'critical_alerts': sum(1 for a in alerts if a.get('severity') == 'critical')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/alerts/{user_id}/{alert_id}/acknowledge")
async def acknowledge_alert(user_id: str, alert_id: str):
    """Mark an alert as acknowledged by the user"""
    try:
        if alert_system is None:
            raise HTTPException(status_code=503, detail="Alert system not available")

        result = alert_system.acknowledge_alert(user_id, alert_id)

        if not result:
            raise HTTPException(status_code=500, detail="Failed to acknowledge alert")

        return {
            'success': True,
            'alert_id': alert_id,
            'acknowledged': True
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/anomalies/{user_id}")
async def detect_anomalies(user_id: str):
    """Detect unusual spending patterns and anomalies"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=503, detail="Forecaster service not available")

        anomalies = forecaster.detect_anomalies(user_id)
        return anomalies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TREND ANALYSIS ====================

@app.get("/api/v1/trends/monthly/{user_id}")
async def get_monthly_trends(user_id: str, months: int = Query(6, ge=1, le=24)):
    """Get monthly spending trends for analysis"""
    try:
        if trend_analyzer is None:
            raise HTTPException(status_code=503, detail="Trend analyzer not available")

        trend = trend_analyzer.get_monthly_trend(user_id, months)

        if isinstance(trend, dict) and 'error' in trend:
            raise HTTPException(status_code=404, detail=trend['error'])

        return trend

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trends/category/{user_id}/{category}")
async def get_category_trends(user_id: str, category: str, months: int = Query(6, ge=1, le=24)):
    """Get spending trends for a specific expense category"""
    try:
        if trend_analyzer is None:
            raise HTTPException(status_code=503, detail="Trend analyzer not available")

        trend = trend_analyzer.get_category_trend(user_id, category, months)

        if isinstance(trend, dict) and 'error' in trend:
            raise HTTPException(status_code=404, detail=trend['error'])

        return trend

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trends/compare")
async def compare_months(user_id: str, month1: str, month2: str):
    """Compare spending between two months (format: YYYY-MM)"""
    try:
        if trend_analyzer is None:
            raise HTTPException(status_code=503, detail="Trend analyzer not available")

        comparison = trend_analyzer.compare_months(user_id, month1, month2)

        if isinstance(comparison, dict) and 'error' in comparison:
            raise HTTPException(status_code=404, detail=comparison['error'])

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trends/velocity/{user_id}")
async def get_spending_velocity(user_id: str):
    """Get current spending velocity and burn rate"""
    try:
        if trend_analyzer is None:
            raise HTTPException(status_code=503, detail="Trend analyzer not available")

        velocity = trend_analyzer.get_spending_velocity(user_id)

        if isinstance(velocity, dict) and 'error' in velocity:
            raise HTTPException(status_code=404, detail=velocity['error'])

        return velocity

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== EXPENSE FORECASTING ====================

@app.get("/api/v1/forecast/next-month/{user_id}")
async def forecast_next_month(user_id: str, confidence: float = Query(0.85, ge=0.5, le=0.99)):
    """Forecast next month's expenses with confidence interval"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=503, detail="Forecaster service not available")

        forecast = forecaster.forecast_next_month(user_id, confidence)

        if isinstance(forecast, dict) and 'error' in forecast:
            raise HTTPException(status_code=404, detail=forecast['error'])

        return forecast

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/forecast/category/{user_id}/{category}")
async def forecast_category(user_id: str, category: str, months_ahead: int = Query(1, ge=1, le=12)):
    """Forecast expenses for a specific category"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=503, detail="Forecaster service not available")

        forecast = forecaster.forecast_category(user_id, category, months_ahead)

        if isinstance(forecast, dict) and 'error' in forecast:
            raise HTTPException(status_code=404, detail=forecast['error'])

        return forecast

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/forecast/seasonal/{user_id}")
async def get_seasonal_forecast(user_id: str):
    """Get seasonal spending patterns and predictions"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=503, detail="Forecaster service not available")

        seasonal = forecaster.get_seasonal_forecast(user_id)

        if isinstance(seasonal, dict) and 'error' in seasonal:
            raise HTTPException(status_code=404, detail=seasonal['error'])

        return seasonal

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== DASHBOARD & SUMMARY ====================

@app.get("/api/v1/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get comprehensive dashboard with all financial data"""
    try:
        if firebase_service is None or alert_system is None or trend_analyzer is None or forecaster is None or analyzer is None:
            raise HTTPException(status_code=503, detail="One or more services not available")

        # Fetch all data
        budget_data = firebase_service.get_budget_plan(user_id)
        current_expenses = firebase_service.get_current_month_expenses(user_id)
        previous_expenses = firebase_service.get_previous_month_expenses(user_id)

        if not budget_data:
            raise HTTPException(status_code=404, detail="User not initialized")

        plan = budget_data.get('plan', budget_data)

        # Get alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, plan, current_expenses
        )
        alerts = [alert.to_dict() for alert in category_alerts]

        # Get remaining budget
        remaining = alert_system.get_remaining_budget(plan, current_expenses)

        # Get trends
        trends = trend_analyzer.get_monthly_trend(user_id, months=6)

        # Get forecast
        forecast = forecaster.forecast_next_month(user_id)

        # Get velocity
        velocity = trend_analyzer.get_spending_velocity(user_id)

        # Analyze previous and current
        prev_analysis = analyzer.analyze_previous_month(previous_expenses) if previous_expenses else {}
        curr_analysis = analyzer.analyze_previous_month(current_expenses) if current_expenses else {}

        return {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'previous_month_summary': prev_analysis,
            'current_month_summary': curr_analysis,
            'budget_plan': plan,
            'alerts': alerts,
            'alert_count': len(alerts),
            'remaining_budget': remaining,
            'trend_analysis': trends.get('analysis', {}) if isinstance(trends, dict) else {},
            'forecast': forecast if isinstance(forecast, dict) else {},
            'spending_velocity': velocity if isinstance(velocity, dict) else {}
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║                           ERROR HANDLING                                         ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with standardized format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': exc.detail,
            'status_code': exc.status_code,
            'timestamp': datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with standardized format"""
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': str(exc),
            'status_code': 500,
            'timestamp': datetime.now().isoformat()
        }
    )

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║                         APPLICATION ENTRY POINT                                  ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("ENV", "development") == "development"

    print("\n" + "=" * 80)
    print("🚀 POKET BOT - FINANCIAL MANAGEMENT API".center(80))
    print("=" * 80)
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"🌐 Host: {host}:{port}")
    print(f"🔄 Auto-reload: {reload}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f" ReDoc:     http://{host}:{port}/redoc")
    print("\n✅ Features Enabled:")
    print(f"   • Expense Management : {'✓' if expense_initializer else '✗'}")
    print(f"   • Budget Planning    : {'✓' if planner else '✗'}")
    print(f"   • Alert System       : {'✓' if alert_system else '✗'}")
    print(f"   • Trend Analysis     : {'✓' if trend_analyzer else '✗'}")
    print(f"   • Forecasting        : {'✓' if forecaster else '✗'}")
    print(f"   • Personalised Chat  : {'✓' if support_router else '✗'}")
    if support_router:
        print("\n📡 Support endpoints (prefix: /api/support):")
        support_paths = [
            "POST /chat                    — send message to chatbot",
            "GET  /chat/history/{user_id}  — conversation history",
            "POST /chat/context/{user_id}  — push expense context",
            "GET  /analysis/{user_id}      — analyse user needs",
            "POST /recommendations/{user_id} — personalised tips",
            "GET  /knowledge/search        — search knowledge base",
            "GET  /knowledge/categories    — list categories",
            "POST /peer/connect            — connect with peer",
            "GET  /peer/available          — list available peers",
            "POST /peer/register           — register peer",
            "GET  /peer/{peer_id}/profile  — peer stats",
            "GET  /peer/leaderboard        — top peers",
            "GET  /types                   — support modes",
            "GET  /status                  — system stats",
            "GET  /health                  — health check",
        ]
        for ep in support_paths:
            print(f"     {ep}")
    print("=" * 80 + "\n")

    uvicorn.run(
        "main_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )