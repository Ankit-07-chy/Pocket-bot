"""
Tier 1 — Rule-Based Strategy  (days 1-3)
Pure threshold logic.  No ML, no training data needed.
Gives the user a meaningful score from day 1.
"""

from ..schemas import FinancialFeatures, MentalFeatures, PredictionStrategy
from .base_strategy import BaseStrategy, StrategyResult


class RuleBasedStrategy(BaseStrategy):
    """
    Scores are produced by checking each feature against hard thresholds.
    Each triggered rule adds a penalty to a raw score (0–10), which is
    then normalised to [0, 1].
    """

    # ── Financial thresholds ──────────────────────────────────────────
    DAYS_BROKE_DANGER = 7       # less than 7 days of money left → critical
    DAYS_BROKE_WARNING = 14     # 7-14 days → warning
    BUDGET_UTIL_DANGER = 110    # 110%+ of spendable budget used → critical
    BUDGET_UTIL_WARNING = 90    # 90-110% → warning
    GROWTH_RATE_HIGH = 0.30     # 30%+ week-over-week spend growth → warning
    GROWTH_RATE_EXTREME = 0.60  # 60%+ → critical
    IMPULSE_MODERATE = 3        # 3+ impulse spends → warning
    IMPULSE_HIGH = 6            # 6+ → critical
    CAT_OVERSPEND_WARNING = 2   # 2+ categories over budget → warning
    CAT_OVERSPEND_HIGH = 4      # 4+ categories over budget → critical

    # ── Mental thresholds ─────────────────────────────────────────────
    SLEEP_DANGER = 5.0          # < 5 hours → critical
    SLEEP_WARNING = 6.5         # 6.5–5 hours → warning
    STRESS_DANGER = 8.0         # 8+ /10 → critical
    STRESS_WARNING = 6.5        # 6.5–8 → warning
    MOOD_DANGER = -0.6          # avg mood below -0.6 → critical
    MOOD_WARNING = 0.0          # avg mood below 0 → warning
    STREAK_DANGER = 3           # 3+ consecutive bad mood days → critical
    STREAK_WARNING = 2          # 2 days → warning
    NO_EXERCISE_HIGH = 6        # 6+ days without exercise in last 7 → warning
    ENERGY_LOW = 3.0            # energy avg ≤ 3 → warning
    GOAL_FAIL_HEAVY = 0.3       # completing < 30% of goals → warning

    # Max possible raw score — used for normalisation
    _MAX_FIN_RAW = 10.0
    _MAX_MEN_RAW = 10.0

    def predict(
        self,
        financial_features: FinancialFeatures,
        mental_features: MentalFeatures,
        days_of_data: int,
    ) -> StrategyResult:

        fin_score, fin_factors, fin_details = self._score_financial(financial_features)
        men_score, men_factors, men_details = self._score_mental(mental_features)
        combined = self._combine(fin_score, men_score)

        # Confidence grows with days of data; rule-based tops out at 0.55
        confidence = 0.30 + (days_of_data / 3) * 0.08
        confidence = min(confidence, 0.55)

        return StrategyResult(
            financial_score=fin_score,
            mental_score=men_score,
            combined_score=combined,
            confidence=confidence,
            strategy_used=PredictionStrategy.RULE_BASED,
            risk_factors=fin_factors + men_factors,
            financial_details=fin_details,
            mental_details=men_details,
        )

    # ──────────────────────────────────────────────────────────────────
    # Financial scoring
    # ──────────────────────────────────────────────────────────────────

    def _score_financial(self, f: FinancialFeatures):
        raw = 0.0
        factors = []
        details = {}

        # 1. Days until broke
        if f.days_until_broke < self.DAYS_BROKE_DANGER:
            raw += 3.0
            factors.append(
                f"Critical: Only {f.days_until_broke:.1f} days of budget remaining"
            )
        elif f.days_until_broke < self.DAYS_BROKE_WARNING:
            raw += 1.5
            factors.append(
                f"Warning: {f.days_until_broke:.1f} days of budget remaining"
            )
        details["days_until_broke"] = f.days_until_broke

        # 2. Budget utilisation
        if f.budget_utilization_pct >= self.BUDGET_UTIL_DANGER:
            raw += 2.5
            factors.append(
                f"Critical: Spent {f.budget_utilization_pct:.1f}% of monthly budget"
            )
        elif f.budget_utilization_pct >= self.BUDGET_UTIL_WARNING:
            raw += 1.0
            factors.append(
                f"Warning: {f.budget_utilization_pct:.1f}% of budget used"
            )
        details["budget_utilization_pct"] = f.budget_utilization_pct

        # 3. Expense growth rate (week-over-week)
        if f.expense_growth_rate >= self.GROWTH_RATE_EXTREME:
            raw += 2.0
            factors.append(
                f"Spending surged {f.expense_growth_rate * 100:.0f}% vs last week"
            )
        elif f.expense_growth_rate >= self.GROWTH_RATE_HIGH:
            raw += 1.0
            factors.append(
                f"Spending up {f.expense_growth_rate * 100:.0f}% vs last week"
            )
        details["expense_growth_rate"] = f.expense_growth_rate

        # 4. Impulse spends
        if f.impulse_spend_count >= self.IMPULSE_HIGH:
            raw += 1.5
            factors.append(f"{f.impulse_spend_count} impulse purchases detected")
        elif f.impulse_spend_count >= self.IMPULSE_MODERATE:
            raw += 0.5
            factors.append(f"{f.impulse_spend_count} above-average purchases")
        details["impulse_spend_count"] = f.impulse_spend_count

        # 5. Category overspend count
        if f.category_overspend_count >= self.CAT_OVERSPEND_HIGH:
            raw += 1.0
            factors.append(
                f"{f.category_overspend_count} categories over budget"
            )
        elif f.category_overspend_count >= self.CAT_OVERSPEND_WARNING:
            raw += 0.5
            factors.append(
                f"{f.category_overspend_count} categories approaching limit"
            )
        details["category_overspend_count"] = f.category_overspend_count

        # 6. Skipped meals (financial pressure indicator)
        if f.skipped_meals_count >= 4:
            raw += 0.5
            factors.append("Skipping meals frequently — possible budget pressure")
        details["skipped_meals_count"] = f.skipped_meals_count

        score = min(raw / self._MAX_FIN_RAW, 1.0)
        return round(score, 4), factors, details

    # ──────────────────────────────────────────────────────────────────
    # Mental scoring
    # ──────────────────────────────────────────────────────────────────

    def _score_mental(self, m: MentalFeatures):
        raw = 0.0
        factors = []
        details = {}

        # 1. Sleep
        if m.sleep_avg_7d < self.SLEEP_DANGER:
            raw += 2.5
            factors.append(
                f"Critical: Avg sleep {m.sleep_avg_7d:.1f}h (< 5h)"
            )
        elif m.sleep_avg_7d < self.SLEEP_WARNING:
            raw += 1.0
            factors.append(f"Low sleep average: {m.sleep_avg_7d:.1f}h/night")
        details["sleep_avg_7d"] = m.sleep_avg_7d

        # 2. Sleep deficit from personal baseline
        if m.sleep_deficit > 2.0:
            raw += 1.0
            factors.append(
                f"Sleeping {m.sleep_deficit:.1f}h less than your personal baseline"
            )
        details["sleep_deficit"] = m.sleep_deficit

        # 3. Stress
        if m.stress_avg_7d >= self.STRESS_DANGER:
            raw += 2.5
            factors.append(
                f"Critical: Stress avg {m.stress_avg_7d:.1f}/10"
            )
        elif m.stress_avg_7d >= self.STRESS_WARNING:
            raw += 1.0
            factors.append(f"Elevated stress: {m.stress_avg_7d:.1f}/10")
        details["stress_avg_7d"] = m.stress_avg_7d

        # 4. Stress trend (rising fast)
        if m.stress_trend > 0.5:
            raw += 1.0
            factors.append("Stress is rising sharply over the past week")
        details["stress_trend"] = m.stress_trend

        # 5. Mood
        if m.mood_score_avg <= self.MOOD_DANGER:
            raw += 2.0
            factors.append("Consistently negative mood this week")
        elif m.mood_score_avg <= self.MOOD_WARNING:
            raw += 1.0
            factors.append("Mood trending negative")
        details["mood_score_avg"] = m.mood_score_avg

        # 6. Bad mood streak
        if m.bad_mood_streak >= self.STREAK_DANGER:
            raw += 1.5
            factors.append(
                f"{m.bad_mood_streak} consecutive days of negative mood"
            )
        elif m.bad_mood_streak >= self.STREAK_WARNING:
            raw += 0.5
            factors.append(
                f"{m.bad_mood_streak} days of negative mood in a row"
            )
        details["bad_mood_streak"] = m.bad_mood_streak

        # 7. Exercise
        if m.no_exercise_days_7d >= self.NO_EXERCISE_HIGH:
            raw += 1.0
            factors.append("Little to no exercise this week")
        details["no_exercise_days_7d"] = m.no_exercise_days_7d

        # 8. Energy
        if m.energy_avg_7d <= self.ENERGY_LOW:
            raw += 0.5
            factors.append(f"Low energy levels (avg {m.energy_avg_7d:.1f}/10)")
        details["energy_avg_7d"] = m.energy_avg_7d

        # 9. Goal completion
        if m.goal_completion_rate <= self.GOAL_FAIL_HEAVY:
            raw += 0.5
            factors.append(
                f"Only {m.goal_completion_rate * 100:.0f}% of weekly goals met"
            )
        details["goal_completion_rate"] = m.goal_completion_rate

        score = min(raw / self._MAX_MEN_RAW, 1.0)
        return round(score, 4), factors, details

    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _combine(fin: float, men: float) -> float:
        return round(0.35 * fin + 0.65 * men, 4)
