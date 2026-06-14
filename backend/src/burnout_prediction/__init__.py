"""
Burnout Prediction Module
Auto-upgrading prediction system:
  Tier 1 (days 1-3):  Rule-based thresholds
  Tier 2 (days 4-6):  Hybrid statistical
  Tier 3 (days 7+):   ML with SGD incremental learning
"""

from .burnout_predictor import BurnoutPredictor
from .schemas import (
    BurnoutPredictionResponse,
    BurnoutAlertLevel,
    BurnoutTrendResponse,
    BurnoutHistoryItem,
    PredictionStrategy,
    FinancialFeatures,
    MentalFeatures,
)
from .feature_engineer import FeatureEngineer
from .model_store import resolve_model_dir, delete_user_models, list_trained_users

__all__ = [
    "BurnoutPredictor",
    "BurnoutPredictionResponse",
    "BurnoutAlertLevel",
    "BurnoutTrendResponse",
    "BurnoutHistoryItem",
    "PredictionStrategy",
    "FinancialFeatures",
    "MentalFeatures",
    "FeatureEngineer",
    "resolve_model_dir",
    "delete_user_models",
    "list_trained_users",
]
