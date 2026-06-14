"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class ExpenseCreate(BaseModel):
    """Request model for creating an expense"""
    date: str = Field(..., description="Expense date in ISO format")
    category: str = Field(..., description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount")
    description: Optional[str] = Field(None, description="Expense description")


class ExpenseResponse(BaseModel):
    """Response model for expense"""
    expense_id: str
    user_id: str
    date: str
    category: str
    amount: float
    description: Optional[str]


class BudgetBreakdown(BaseModel):
    """Budget breakdown model"""
    food: float
    transport: float
    entertainment: float
    education: float
    health: float
    utilities: float
    others: float


class BudgetPlanResponse(BaseModel):
    """Response model for budget plan"""
    budget_breakdown: Dict[str, float]
    total_budget: float
    spending_budget: float
    savings: float
    recommendation: str


class InitializeUserRequest(BaseModel):
    """Request model for user initialization"""
    user_id: str
    current_month_budget: Optional[float] = None


class InitializeUserResponse(BaseModel):
    """Response model for user initialization"""
    user_id: str
    success: bool
    previous_month: Dict
    current_month: Dict
    budget_plan: BudgetPlanResponse
    error: Optional[str] = None


class OnboardUserRequest(BaseModel):
    """
    Request model for first-time user onboarding.

    Collected at registration/login when the user tells us their
    last month's spending and this month's budget so the system can
    immediately produce a category-wise budget plan.
    """
    user_id: str = Field(..., description="User ID (integer or Firebase UID as string)")
    last_month_total: float = Field(..., gt=0, description="Total amount spent last month")
    last_month_category_expenses: Dict[str, float] = Field(
        ...,
        description=(
            "Category-wise breakdown of last month's spending. "
            "Keys must be one of: food, transport, entertainment, "
            "education, health, utilities, others. "
            "Example: {\"food\": 3000, \"transport\": 800}"
        )
    )
    this_month_budget: float = Field(..., gt=0, description="Total budget the user wants for this month")
    savings_target: Optional[float] = Field(0.0, ge=0, description="Optional savings target amount")


class OnboardUserResponse(BaseModel):
    """Response model for user onboarding"""
    user_id: str
    success: bool
    budget_plan: Dict  # full optimized plan with category breakdown
    summary: Dict      # quick-glance numbers
    error: Optional[str] = None


class CustomBudgetRequest(BaseModel):
    """Request model for custom budget"""
    user_id: str
    custom_budget: float = Field(..., gt=0)
    savings_target: Optional[float] = Field(0, ge=0)


class MonthlyTrendResponse(BaseModel):
    """Response model for monthly trends"""
    user_id: str
    trend_data: Dict
    months_analyzed: int
    analysis: Dict


class CategoryTrendResponse(BaseModel):
    """Response model for category trends"""
    user_id: str
    category: str
    trend_data: Dict
    analysis: Dict


class ForecastResponse(BaseModel):
    """Response model for expense forecast"""
    forecast_month: str
    forecasted_total: float
    confidence_level: float
    category_forecast: Dict
    forecast_range: Dict
    based_on_months: int


class AlertResponse(BaseModel):
    """Response model for alerts"""
    alert_id: str
    user_id: str
    category: str
    message: str
    severity: str
    current_amount: float
    budget_limit: float
    percentage_exceeded: float
    created_at: str
    acknowledged: bool


class RemainingBudgetResponse(BaseModel):
    """Response model for remaining budget"""
    budget: float
    spent: float
    remaining: float
    percentage_used: float


class DashboardResponse(BaseModel):
    """Comprehensive dashboard response"""
    user_id: str
    previous_month_summary: Dict
    current_month_summary: Dict
    budget_plan: BudgetPlanResponse
    alerts: List[AlertResponse]
    remaining_budget: Dict[str, RemainingBudgetResponse]
    trend_analysis: Dict
    forecast: Dict
    spending_velocity: Dict


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    status_code: int
    timestamp: str
