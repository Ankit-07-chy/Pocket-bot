"""
Pydantic schemas for Burnout Prediction module
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum


class BurnoutAlertLevel(str, Enum):
    GOOD = "good"
    MODERATE = "moderate"
    HIGH = "high"
    CRISIS = "crisis"


class PredictionStrategy(str, Enum):
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"
    ML = "ml"


class FinancialFeatures(BaseModel):
    daily_spend_avg_7d: float = 0.0
    daily_spend_avg_30d: float = 0.0
    weekly_spend_current: float = 0.0
    weekly_spend_last: float = 0.0
    expense_growth_rate: float = 0.0
    projected_month_end_spend: float = 0.0
    budget_utilization_pct: float = 0.0
    days_until_broke: float = 30.0
    food_spend_ratio: float = 0.0
    transport_spend_ratio: float = 0.0
    entertainment_spend_ratio: float = 0.0
    impulse_spend_count: int = 0
    budget_safety_margin: float = 0.0
    category_overspend_count: int = 0
    food_homemade_ratio: float = 0.5
    skipped_meals_count: int = 0
    emergency_fund: float = 0.0
    spendable_budget: float = 0.0

    def to_vector(self) -> List[float]:
        """Return the 16-feature vector used by the ML model (excludes derived meta-fields)."""
        return [
            self.daily_spend_avg_7d,
            self.daily_spend_avg_30d,
            self.weekly_spend_current,
            self.weekly_spend_last,
            self.expense_growth_rate,
            self.projected_month_end_spend,
            self.budget_utilization_pct,
            self.days_until_broke,
            self.food_spend_ratio,
            self.transport_spend_ratio,
            self.entertainment_spend_ratio,
            float(self.impulse_spend_count),
            self.budget_safety_margin,
            float(self.category_overspend_count),
            self.food_homemade_ratio,
            float(self.skipped_meals_count),
        ]


class MentalFeatures(BaseModel):
    sleep_avg_7d: float = 7.0
    sleep_deficit: float = 0.0
    stress_avg_7d: float = 5.0
    stress_trend: float = 0.0
    exercise_avg_7d: float = 30.0
    no_exercise_days_7d: int = 0
    mood_score_avg: float = 0.5
    bad_mood_streak: int = 0
    energy_avg_7d: float = 5.0
    social_activity_avg_7d: float = 3.0
    goal_completion_rate: float = 1.0
    missed_goals_count: int = 0
    skipped_meals_count: int = 0
    sleep_consistency: float = 0.0
    stress_sleep_interaction: float = 0.0

    def to_vector(self) -> List[float]:
        """Return the 15-feature vector used by the ML model."""
        return [
            self.sleep_avg_7d,
            self.sleep_deficit,
            self.stress_avg_7d,
            self.stress_trend,
            self.exercise_avg_7d,
            float(self.no_exercise_days_7d),
            self.mood_score_avg,
            float(self.bad_mood_streak),
            self.energy_avg_7d,
            self.social_activity_avg_7d,
            self.goal_completion_rate,
            float(self.missed_goals_count),
            float(self.skipped_meals_count),
            self.sleep_consistency,
            self.stress_sleep_interaction,
        ]


class BurnoutPredictionResponse(BaseModel):
    user_id: str
    date: str
    financial_score: float
    mental_score: float
    combined_score: float
    alert_level: BurnoutAlertLevel
    top_risk_factors: List[str]
    recommendations: List[str]
    strategy_used: PredictionStrategy
    confidence: float
    days_of_data: int
    next_upgrade_in_days: Optional[int]
    financial_details: Dict[str, Any]
    mental_details: Dict[str, Any]


class BurnoutHistoryItem(BaseModel):
    date: str
    financial_score: float
    mental_score: float
    combined_score: float
    alert_level: BurnoutAlertLevel
    strategy_used: PredictionStrategy


class BurnoutTrendResponse(BaseModel):
    user_id: str
    history: List[BurnoutHistoryItem]
    average_combined: float
    worst_day: Optional[str]
    improving: bool
    days_analyzed: int
