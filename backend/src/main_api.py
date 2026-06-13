"""
FastAPI application for Expense Management System
Production-ready version with automatic path handling
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

# ==================== PRODUCTION-READY PATH HANDLING ====================
def setup_project_paths():
    """Automatically configure Python paths for production"""
    # Get the absolute path of the current file
    current_file = Path(__file__).resolve()
    
    # Find the project root (where 'backend' folder exists)
    project_root = current_file.parent
    
    # If backend folder is in current directory, we're in root
    if not (project_root / 'backend').exists():
        # Try parent directory
        project_root = current_file.parent.parent
    
    # Try grandparent directory (if in deep nesting)
    if not (project_root / 'backend').exists():
        project_root = current_file.parent.parent.parent
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Also add backend/src to path for direct imports
    backend_src = project_root / 'backend' / 'src'
    if backend_src.exists() and str(backend_src) not in sys.path:
        sys.path.insert(0, str(backend_src))
    
    # Add expense_management to path as well
    expense_mgmt = backend_src / 'expense_management'
    if expense_mgmt.exists() and str(expense_mgmt) not in sys.path:
        sys.path.insert(0, str(expense_mgmt))
    
    return project_root

# Setup paths before any other imports
PROJECT_ROOT = setup_project_paths()
print(f"✅ Project Root: {PROJECT_ROOT}")
print(f"✅ Python Path: {sys.path[0]}")

# ==================== IMPORTS ====================
# Import FastAPI and related
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Try multiple import strategies
expense_initializer = None
alert_system = None
trend_analyzer = None
forecaster = None
firebase_service = None
analyzer = None
planner = None

# Import from backend package
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
    print("✅ Imports successful from backend.src.expense_management")
    
    # Initialize services
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
        # Alternative: Add expense_management directly to path
        expense_mgmt_path = PROJECT_ROOT / 'backend' / 'src' / 'expense_management'
        if str(expense_mgmt_path) not in sys.path:
            sys.path.insert(0, str(expense_mgmt_path))
        
        from initialize_boundary import ExpenseInitializer
        from alert_system import AlertSystem
        from trend_analyzer import TrendAnalyzer
        from forecaster import ExpenseForecaster
        from firebase_service import FirebaseExpenseService
        from expense_analyzer import ExpenseAnalyzer
        from budget_planner import BudgetPlanner
        from schemas import (
            InitializeUserRequest, InitializeUserResponse,
            CustomBudgetRequest, BudgetPlanResponse,
            MonthlyTrendResponse, CategoryTrendResponse,
            ForecastResponse, AlertResponse,
            RemainingBudgetResponse, DashboardResponse,
            HealthCheckResponse, ErrorResponse, ExpenseCreate
        )
        print("✅ Imports successful from direct path")
        
        # Initialize services
        firebase_service = FirebaseExpenseService()
        expense_initializer = ExpenseInitializer()
        alert_system = AlertSystem(firebase_service)
        trend_analyzer = TrendAnalyzer(firebase_service)
        forecaster = ExpenseForecaster(firebase_service)
        analyzer = ExpenseAnalyzer()
        planner = BudgetPlanner(analyzer)
        
    except ImportError as e2:
        print(f"⚠ Second import attempt failed: {e2}")
        print("⚠ Running in demo mode with mock services")
        
        # Create mock classes for demo mode
        class MockService:
            def __init__(self, *args, **kwargs):
                pass
            def __getattr__(self, name):
                return lambda *args, **kwargs: {"mock": True, "message": f"Demo mode: {name} called"}
        
        firebase_service = MockService()
        expense_initializer = MockService()
        alert_system = MockService()
        trend_analyzer = MockService()
        forecaster = MockService()
        analyzer = MockService()
        planner = MockService()
        
        # Still need schemas - try to import them
        try:
            from schemas import (
                InitializeUserRequest, InitializeUserResponse,
                CustomBudgetRequest, BudgetPlanResponse,
                MonthlyTrendResponse, CategoryTrendResponse,
                ForecastResponse, AlertResponse,
                RemainingBudgetResponse, DashboardResponse,
                HealthCheckResponse, ErrorResponse, ExpenseCreate
            )
        except ImportError:
            # Create dummy schemas if not available
            from pydantic import BaseModel
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

# ==================== FIREBASE INITIALIZATION ====================
import firebase_admin
from firebase_admin import db

# Initialize Firebase (works without service account credentials)
firebase_initialized = False
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app(options={
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL', 'https://your-database.firebaseio.com/')
        })
    firebase_initialized = True
    print(f"✅ Firebase initialized with Realtime Database")
except Exception as e:
    print(f"⚠ Firebase Realtime Database error: {e}")
    print("⚠ Services will run in mock mode")

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="Expense Management API",
    description="Complete expense management system with budgeting, forecasting, and alerts",
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

# ==================== HEALTH & STATUS ====================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "firebase_initialized": firebase_initialized,
        "services_initialized": expense_initializer is not None
    }

@app.get("/api/v1/status")
async def system_status():
    """Get detailed system status"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "firebase": firebase_initialized,
            "expense_analyzer": analyzer is not None,
            "budget_planner": planner is not None,
            "alert_system": alert_system is not None,
            "trend_analyzer": trend_analyzer is not None,
            "forecaster": forecaster is not None
        },
        "project_root": str(PROJECT_ROOT),
        "python_path": sys.path[0]
    }

# ==================== INITIALIZATION ====================

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
    """Reinitialize budget with custom amount"""
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

# ==================== EXPENSES ====================

@app.post("/api/v1/expenses")
async def create_expense(user_id: str, expense: ExpenseCreate):
    """Create a new expense"""
    try:
        if firebase_service is None:
            raise HTTPException(status_code=503, detail="Firebase service not available")
        
        expense_ref = firebase_service.db.reference(f'users/{user_id}/expenses')
        new_expense = {
            **expense.dict(),
            'created_at': datetime.now().isoformat()
        }
        new_key = expense_ref.push().key
        expense_ref.child(new_key).set(new_expense)

        return {
            'success': True,
            'expense_id': new_key,
            'data': new_expense
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/expenses/{user_id}")
async def get_user_expenses(user_id: str):
    """Get all expenses for a user"""
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

# ==================== BUDGET PLANNING ====================

@app.get("/api/v1/budget-plan/{user_id}")
async def get_budget_plan(user_id: str):
    """Get current budget plan for user"""
    try:
        if firebase_service is None:
            raise HTTPException(status_code=503, detail="Firebase service not available")
        
        ref = firebase_service.db.reference(f'users/{user_id}/budget_plan')
        plan = ref.get()

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
    """Get remaining budget by category"""
    try:
        if firebase_service is None or alert_system is None:
            raise HTTPException(status_code=503, detail="Service not available")
        
        budget_plan = firebase_service.db.reference(f'users/{user_id}/budget_plan').get()
        current_expenses = firebase_service.get_current_month_expenses(user_id)

        if not budget_plan:
            raise HTTPException(status_code=404, detail="Budget plan not found")

        remaining = alert_system.get_remaining_budget(budget_plan['plan'], current_expenses)

        return {
            'user_id': user_id,
            'remaining_budget': remaining,
            'total_budget': budget_plan['plan']['total_budget']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ALERTS ====================

@app.get("/api/v1/alerts/{user_id}")
async def get_user_alerts(user_id: str):
    """Get active alerts for user"""
    try:
        if firebase_service is None or alert_system is None:
            raise HTTPException(status_code=503, detail="Service not available")
        
        budget_plan = firebase_service.db.reference(f'users/{user_id}/budget_plan').get()
        current_expenses = firebase_service.get_current_month_expenses(user_id)

        if not budget_plan:
            raise HTTPException(status_code=404, detail="Budget plan not found")

        # Check for alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, budget_plan['plan'], current_expenses
        )
        total_alert = alert_system.check_total_budget_status(
            user_id, budget_plan['plan'], current_expenses
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
    """Mark alert as acknowledged"""
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
    """Detect unusual spending patterns"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=503, detail="Forecaster service not available")
        
        anomalies = forecaster.detect_anomalies(user_id)
        return anomalies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRENDS ====================

@app.get("/api/v1/trends/monthly/{user_id}")
async def get_monthly_trends(user_id: str, months: int = 6):
    """Get monthly spending trends"""
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
async def get_category_trends(user_id: str, category: str, months: int = 6):
    """Get spending trends for a specific category"""
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
    """Compare spending between two months"""
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
    """Get current spending velocity"""
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

# ==================== FORECASTING ====================

@app.get("/api/v1/forecast/next-month/{user_id}")
async def forecast_next_month(user_id: str, confidence: float = 0.85):
    """Forecast next month's expenses"""
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
async def forecast_category(user_id: str, category: str, months_ahead: int = 1):
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
    """Get seasonal spending patterns"""
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

# ==================== DASHBOARD ====================

@app.get("/api/v1/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get comprehensive dashboard data"""
    try:
        if firebase_service is None or alert_system is None or trend_analyzer is None or forecaster is None or analyzer is None:
            raise HTTPException(status_code=503, detail="One or more services not available")
        
        # Fetch all data
        budget_plan = firebase_service.db.reference(f'users/{user_id}/budget_plan').get()
        current_expenses = firebase_service.get_current_month_expenses(user_id)
        previous_expenses = firebase_service.get_previous_month_expenses(user_id)

        if not budget_plan:
            raise HTTPException(status_code=404, detail="User not initialized")

        # Get alerts
        category_alerts = alert_system.check_category_overspending(
            user_id, budget_plan['plan'], current_expenses
        )
        alerts = [alert.to_dict() for alert in category_alerts]

        # Get remaining budget
        remaining = alert_system.get_remaining_budget(budget_plan['plan'], current_expenses)

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
            'budget_plan': budget_plan.get('plan', budget_plan),
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

# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
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
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': str(exc),
            'status_code': 500,
            'timestamp': datetime.now().isoformat()
        }
    )

# ==================== ROOT ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        'message': 'Expense Management API',
        'version': '1.0.0',
        'docs': '/docs',
        'status': 'active',
        'endpoints': {
            'health': '/health',
            'status': '/api/v1/status',
            'docs': '/docs',
            'redoc': '/redoc'
        }
    }

# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("ENV", "development") == "development"
    
    print("=" * 60)
    print("🚀 Expense Management API Starting...")
    print("=" * 60)
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"🌐 Host: {host}:{port}")
    print(f"🔄 Auto-reload: {reload}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main_api:app" if __name__ == "__main__" else app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )