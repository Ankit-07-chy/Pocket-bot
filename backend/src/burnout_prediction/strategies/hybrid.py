"""
Tier 2 — Hybrid Strategy  (days 4-6)
Combines rule-based thresholds with lightweight statistical signals:
 - Trend direction (slope) for both financial and mental dimensions
 - Weighted composite using feature normalisation
 - Still no ML model, but smarter than pure thresholds
"""

from ..schemas import FinancialFeatures, MentalFeatures, PredictionStrategy
from .base_strategy import BaseStrategy, StrategyResult
from .rule_based import RuleBasedStrategy


class HybridStrategy(BaseStrategy):
    """
    Starts from the rule-based score, then adjusts up/down based on
    statistical signals: trends, interactions, and composite weights.
    """

    def __init__(self):
        self._rules = RuleBasedStrategy()

    def predict(
        self,
        financial_features: FinancialFeatures,
        mental_features: MentalFeatures,
        days_of_data: int,
    ) -> StrategyResult:

        # Start with rule-based foundation
        base = self._rules.predict(financial_features, mental_features, days_of_data)

        # Apply statistical adjustments
        fin_adj = self._financial_adjustment(financial_features)
        men_adj = self._mental_adjustment(mental_features)

        fin_score = max(0.0, min(1.0, base.financial_score + fin_adj))
        men_score = max(0.0, min(1.0, base.mental_score + men_adj))
        combined = round(0.35 * fin_score + 0.65 * men_score, 4)

        # Collect extra factors from statistical signals
        extra_factors = self._extra_risk_factors(
            financial_features, mental_features, fin_adj, men_adj
        )

        # Confidence is higher than rule-based but below ML
        confidence = 0.55 + (days_of_data - 4) * 0.04   # 0.55 → 0.63
        confidence = min(confidence, 0.65)

        return StrategyResult(
            financial_score=round(fin_score, 4),
            mental_score=round(men_score, 4),
            combined_score=combined,
            confidence=round(confidence, 4),
            strategy_used=PredictionStrategy.HYBRID,
            risk_factors=base.risk_factors + extra_factors,
            financial_details={**base.financial_details, "hybrid_adjustment": fin_adj},
            mental_details={**base.mental_details, "hybrid_adjustment": men_adj},
        )

    # ──────────────────────────────────────────────────────────────────
    # Financial statistical adjustment  (−0.15 … +0.20)
    # ──────────────────────────────────────────────────────────────────

    def _financial_adjustment(self, f: FinancialFeatures) -> float:
        adj = 0.0

        # If projected month-end spend > 120% of spendable budget → push up
        if f.spendable_budget > 0:
            proj_ratio = f.projected_month_end_spend / f.spendable_budget
            if proj_ratio > 1.2:
                adj += 0.10
            elif proj_ratio > 1.0:
                adj += 0.05
            elif proj_ratio < 0.75:
                adj -= 0.05   # comfortably under budget → reduce score

        # High food spend ratio (> 50%) while also skipping meals = financial stress
        if f.food_spend_ratio > 0.50 and f.skipped_meals_count >= 3:
            adj += 0.05

        # Low homemade food ratio (< 20%) signals lifestyle spending pressure
        if f.food_homemade_ratio < 0.20:
            adj += 0.05
        elif f.food_homemade_ratio > 0.70:
            adj -= 0.03   # mostly home-cooked = financially responsible

        # Negative safety margin is already captured, but amplify if very negative
        if f.budget_safety_margin < -f.spendable_budget * 0.20:
            adj += 0.05

        return round(max(-0.15, min(0.20, adj)), 4)

    # ──────────────────────────────────────────────────────────────────
    # Mental statistical adjustment  (−0.15 … +0.20)
    # ──────────────────────────────────────────────────────────────────

    def _mental_adjustment(self, m: MentalFeatures) -> float:
        adj = 0.0

        # Stress–sleep interaction amplifier
        if m.stress_sleep_interaction > 5.0:
            adj += 0.08
        elif m.stress_sleep_interaction > 3.5:
            adj += 0.04

        # Sleep consistency: very irregular sleep (std > 1.5h) worsens burnout
        if m.sleep_consistency > 2.0:
            adj += 0.05
        elif m.sleep_consistency > 1.5:
            adj += 0.03

        # Falling stress trend + good sleep = improving → reduce score
        if m.stress_trend < -0.3 and m.sleep_avg_7d >= 7.0:
            adj -= 0.05

        # Good social activity with good mood → resilience bonus
        if m.social_activity_avg_7d >= 4.0 and m.mood_score_avg >= 0.5:
            adj -= 0.04

        # Multiple missed goals compounds mental strain
        if m.missed_goals_count >= 3:
            adj += 0.04

        # Skipping meals while stressed = compounding mental drain
        if m.skipped_meals_count >= 4 and m.stress_avg_7d >= 6.0:
            adj += 0.04

        return round(max(-0.15, min(0.20, adj)), 4)

    # ──────────────────────────────────────────────────────────────────

    def _extra_risk_factors(
        self,
        f: FinancialFeatures,
        m: MentalFeatures,
        fin_adj: float,
        men_adj: float,
    ):
        extras = []
        if f.spendable_budget > 0:
            ratio = f.projected_month_end_spend / f.spendable_budget
            if ratio > 1.2:
                extras.append(
                    f"Projected to overspend by {(ratio - 1) * 100:.0f}% this month"
                )
        if m.stress_sleep_interaction > 5.0:
            extras.append("High stress combined with poor sleep — compounding effect")
        if m.sleep_consistency > 2.0:
            extras.append("Irregular sleep schedule detected")
        if fin_adj > 0.08:
            extras.append("Financial pressure is building steadily")
        if men_adj > 0.08:
            extras.append("Mental indicators are declining week-on-week")
        return extras
