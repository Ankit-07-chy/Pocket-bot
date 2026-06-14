"""
Abstract base strategy — all three tiers implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

from ..schemas import PredictionStrategy


@dataclass
class StrategyResult:
    """Unified result container returned by every strategy."""

    financial_score: float          # 0.0 – 1.0
    mental_score: float             # 0.0 – 1.0
    combined_score: float           # 0.65M + 0.35F
    confidence: float               # 0.0 – 1.0
    strategy_used: PredictionStrategy
    risk_factors: List[str] = field(default_factory=list)
    financial_details: dict = field(default_factory=dict)
    mental_details: dict = field(default_factory=dict)

    def __post_init__(self):
        # Clamp all scores to [0, 1]
        self.financial_score = max(0.0, min(1.0, self.financial_score))
        self.mental_score = max(0.0, min(1.0, self.mental_score))
        self.combined_score = max(0.0, min(1.0, self.combined_score))
        self.confidence = max(0.0, min(1.0, self.confidence))


class BaseStrategy(ABC):
    """
    Every prediction strategy must implement `predict`.
    It receives pre-built feature objects and returns a StrategyResult.
    """

    @abstractmethod
    def predict(
        self,
        financial_features,   # FinancialFeatures
        mental_features,      # MentalFeatures
        days_of_data: int,
    ) -> StrategyResult:
        ...
