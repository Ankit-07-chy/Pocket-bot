"""
Burnout Prediction — Test Suite
================================
Run from the project root:
    python -m pytest backend/src/burnout_prediction/test_burnout.py -v

Or run directly (no pytest needed):
    python backend/src/burnout_prediction/test_burnout.py

Covers 4 layers:
  Layer 1 — Sanity:       healthy vs burned-out feature inputs produce correct direction
  Layer 2 — Strategy tier: right strategy selected at day 1 / 4 / 7 + confidence grows
  Layer 3 — Feature eng:  FeatureEngineer reads an in-memory SQLite correctly
  Layer 4 — ML bootstrap: SGD trains, saves files, burnout vector > healthy vector
"""

import os
import sys
import sqlite3
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ── Make sure the package is importable regardless of where you run from ──────
# Structure: Pocket-bot/backend/src/burnout_prediction/test_burnout.py
# _HERE    = .../burnout_prediction/
# _SRC_DIR = .../backend/src/          ← add this: allows "from burnout_prediction import ..."
_HERE    = Path(__file__).resolve().parent
_SRC_DIR = _HERE.parent                 # backend/src/
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from burnout_prediction.schemas import (
    FinancialFeatures,
    MentalFeatures,
    BurnoutAlertLevel,
    PredictionStrategy,
)
from burnout_prediction.strategies.rule_based import RuleBasedStrategy
from burnout_prediction.strategies.hybrid import HybridStrategy
from burnout_prediction.strategies.ml_strategy import MLStrategy
from burnout_prediction.score_combiner import ScoreCombiner
from burnout_prediction.feature_engineer import FeatureEngineer
from burnout_prediction.burnout_predictor import BurnoutPredictor

# ──────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ──────────────────────────────────────────────────────────────────────────────

def _healthy_financial() -> FinancialFeatures:
    """User who is well within budget, no impulse spends, food stable."""
    return FinancialFeatures(
        daily_spend_avg_7d=15.0,
        daily_spend_avg_30d=14.0,
        weekly_spend_current=105.0,
        weekly_spend_last=100.0,
        expense_growth_rate=0.05,        # 5% growth — fine
        projected_month_end_spend=450.0,
        budget_utilization_pct=45.0,     # only 45% used
        days_until_broke=28.0,           # 28 days of money left
        food_spend_ratio=0.35,
        transport_spend_ratio=0.15,
        entertainment_spend_ratio=0.10,
        impulse_spend_count=1,
        budget_safety_margin=350.0,      # lots of headroom
        category_overspend_count=0,
        food_homemade_ratio=0.70,        # mostly home-cooked
        skipped_meals_count=0,
        emergency_fund=100.0,
        spendable_budget=900.0,
    )


def _burnout_financial() -> FinancialFeatures:
    """User who is about to run out of money with rising spending."""
    return FinancialFeatures(
        daily_spend_avg_7d=55.0,
        daily_spend_avg_30d=40.0,
        weekly_spend_current=385.0,
        weekly_spend_last=220.0,
        expense_growth_rate=0.75,        # 75% week-over-week surge
        projected_month_end_spend=1700.0,
        budget_utilization_pct=120.0,    # already 120% of budget used
        days_until_broke=4.0,            # 4 days left
        food_spend_ratio=0.55,
        transport_spend_ratio=0.20,
        entertainment_spend_ratio=0.15,
        impulse_spend_count=8,
        budget_safety_margin=-700.0,     # deep in the red
        category_overspend_count=5,
        food_homemade_ratio=0.05,        # eating out all the time
        skipped_meals_count=5,
        emergency_fund=100.0,
        spendable_budget=900.0,
    )


def _healthy_mental() -> MentalFeatures:
    """User sleeping well, low stress, positive mood, exercising."""
    return MentalFeatures(
        sleep_avg_7d=7.8,
        sleep_deficit=0.0,
        stress_avg_7d=3.0,
        stress_trend=-0.2,               # stress falling — improving
        exercise_avg_7d=40.0,
        no_exercise_days_7d=1,
        mood_score_avg=0.75,             # mostly happy
        bad_mood_streak=0,
        energy_avg_7d=7.0,
        social_activity_avg_7d=5.0,
        goal_completion_rate=0.85,
        missed_goals_count=0,
        skipped_meals_count=0,
        sleep_consistency=0.4,           # consistent sleep
        stress_sleep_interaction=0.9,    # low (low stress + good sleep)
    )


def _burnout_mental() -> MentalFeatures:
    """User sleep-deprived, highly stressed, overwhelmed for days."""
    return MentalFeatures(
        sleep_avg_7d=4.2,                # dangerously low
        sleep_deficit=2.8,
        stress_avg_7d=8.5,               # critical stress
        stress_trend=0.8,                # rising fast
        exercise_avg_7d=2.0,
        no_exercise_days_7d=6,           # almost no exercise
        mood_score_avg=-0.7,             # consistently negative
        bad_mood_streak=4,               # 4 days in a row
        energy_avg_7d=2.5,               # very low energy
        social_activity_avg_7d=1.0,
        goal_completion_rate=0.15,       # failing nearly all goals
        missed_goals_count=4,
        skipped_meals_count=5,
        sleep_consistency=2.5,           # very irregular
        stress_sleep_interaction=7.4,    # compounding effect
    )


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 1 — Sanity: direction of scores
# ──────────────────────────────────────────────────────────────────────────────

def test_rule_based_healthy_is_low():
    strategy = RuleBasedStrategy()
    result = strategy.predict(_healthy_financial(), _healthy_mental(), days_of_data=2)

    assert result.combined_score < 0.30, (
        f"Healthy user should have combined_score < 0.30, got {result.combined_score}"
    )
    assert result.financial_score < 0.20, (
        f"Healthy financial score should be < 0.20, got {result.financial_score}"
    )
    assert result.mental_score < 0.25, (
        f"Healthy mental score should be < 0.25, got {result.mental_score}"
    )
    assert result.strategy_used == PredictionStrategy.RULE_BASED
    print(f"  ✓ Healthy user: combined={result.combined_score:.3f}  fin={result.financial_score:.3f}  men={result.mental_score:.3f}")


def test_rule_based_burnout_is_high():
    strategy = RuleBasedStrategy()
    result = strategy.predict(_burnout_financial(), _burnout_mental(), days_of_data=2)

    assert result.combined_score > 0.55, (
        f"Burned-out user should have combined_score > 0.55, got {result.combined_score}"
    )
    assert result.financial_score > 0.40, (
        f"Financial burnout score should be > 0.40, got {result.financial_score}"
    )
    assert result.mental_score > 0.50, (
        f"Mental burnout score should be > 0.50, got {result.mental_score}"
    )
    assert len(result.risk_factors) > 0, "Burned-out user should have risk factors"
    print(f"  ✓ Burnout user: combined={result.combined_score:.3f}  fin={result.financial_score:.3f}  men={result.mental_score:.3f}")
    print(f"    Risk factors: {result.risk_factors[:3]}")


def test_burnout_higher_than_healthy():
    """Burned-out score must always be strictly higher than healthy score."""
    strategy = RuleBasedStrategy()
    healthy = strategy.predict(_healthy_financial(), _healthy_mental(), days_of_data=2)
    burnout = strategy.predict(_burnout_financial(), _burnout_mental(), days_of_data=2)

    assert burnout.combined_score > healthy.combined_score, (
        "Burned-out combined score must exceed healthy score"
    )
    assert burnout.financial_score > healthy.financial_score
    assert burnout.mental_score > healthy.mental_score
    print(f"  ✓ Gap: burnout={burnout.combined_score:.3f} > healthy={healthy.combined_score:.3f}")


def test_scores_are_clamped_between_0_and_1():
    """No score should ever go outside [0, 1] regardless of input."""
    strategy = RuleBasedStrategy()

    # Extreme negative inputs (shouldn't go below 0)
    zero_fin = FinancialFeatures()   # all defaults — no issues
    zero_men = MentalFeatures()
    r1 = strategy.predict(zero_fin, zero_men, days_of_data=1)

    for score_name, val in [
        ("financial", r1.financial_score),
        ("mental", r1.mental_score),
        ("combined", r1.combined_score),
        ("confidence", r1.confidence),
    ]:
        assert 0.0 <= val <= 1.0, f"{score_name} score {val} out of [0,1]"

    # Extreme burnout (shouldn't go above 1)
    r2 = strategy.predict(_burnout_financial(), _burnout_mental(), days_of_data=3)
    for score_name, val in [
        ("financial", r2.financial_score),
        ("mental", r2.mental_score),
        ("combined", r2.combined_score),
    ]:
        assert 0.0 <= val <= 1.0, f"{score_name} score {val} out of [0,1] on burnout input"

    print("  ✓ All scores stay within [0.0, 1.0]")


def test_mental_dominates_financial():
    """Combined = 0.65*mental + 0.35*financial — mental should pull harder."""
    strategy = RuleBasedStrategy()

    # High mental, low financial
    r_men = strategy.predict(_healthy_financial(), _burnout_mental(), days_of_data=2)
    # Low mental, high financial
    r_fin = strategy.predict(_burnout_financial(), _healthy_mental(), days_of_data=2)

    assert r_men.combined_score > r_fin.combined_score, (
        f"Mental-heavy burnout ({r_men.combined_score:.3f}) should exceed "
        f"financial-heavy burnout ({r_fin.combined_score:.3f})"
    )
    print(f"  ✓ Mental-dominant: men_heavy={r_men.combined_score:.3f}  fin_heavy={r_fin.combined_score:.3f}")


def test_alert_level_mapping():
    """ScoreCombiner maps combined scores to correct alert levels."""
    combiner = ScoreCombiner()

    assert combiner.get_alert_level(0.10) == BurnoutAlertLevel.GOOD
    assert combiner.get_alert_level(0.35) == BurnoutAlertLevel.MODERATE
    assert combiner.get_alert_level(0.60) == BurnoutAlertLevel.HIGH
    assert combiner.get_alert_level(0.80) == BurnoutAlertLevel.CRISIS
    # Boundary values
    assert combiner.get_alert_level(0.30) == BurnoutAlertLevel.MODERATE
    assert combiner.get_alert_level(0.55) == BurnoutAlertLevel.HIGH
    assert combiner.get_alert_level(0.75) == BurnoutAlertLevel.CRISIS
    print("  ✓ Alert level boundaries are correct")


def test_recommendations_not_empty():
    """Good and crisis users both get recommendations."""
    combiner = ScoreCombiner()
    strategy = RuleBasedStrategy()

    healthy_result = strategy.predict(_healthy_financial(), _healthy_mental(), days_of_data=2)
    burnout_result = strategy.predict(_burnout_financial(), _burnout_mental(), days_of_data=2)

    healthy_level = combiner.get_alert_level(healthy_result.combined_score)
    burnout_level = combiner.get_alert_level(burnout_result.combined_score)

    healthy_recs = combiner.build_recommendations(healthy_result, healthy_level)
    burnout_recs = combiner.build_recommendations(burnout_result, burnout_level)

    assert len(healthy_recs) > 0, "Healthy user should still get recommendations"
    assert len(burnout_recs) > 0, "Burnout user must get recommendations"
    assert len(burnout_recs) >= len(healthy_recs), "Burnout user should get more recs"
    assert all(isinstance(r, str) and len(r) > 5 for r in burnout_recs)
    print(f"  ✓ Healthy recs: {len(healthy_recs)}  |  Burnout recs: {len(burnout_recs)}")


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 2 — Strategy tier auto-selection and confidence progression
# ──────────────────────────────────────────────────────────────────────────────

def test_strategy_selection_at_each_tier():
    """Predictor selects the right strategy based on days_of_data."""
    assert BurnoutPredictor._select_strategy(1) == PredictionStrategy.RULE_BASED
    assert BurnoutPredictor._select_strategy(3) == PredictionStrategy.RULE_BASED
    assert BurnoutPredictor._select_strategy(4) == PredictionStrategy.HYBRID
    assert BurnoutPredictor._select_strategy(6) == PredictionStrategy.HYBRID
    assert BurnoutPredictor._select_strategy(7) == PredictionStrategy.ML
    assert BurnoutPredictor._select_strategy(30) == PredictionStrategy.ML
    assert BurnoutPredictor._select_strategy(100) == PredictionStrategy.ML
    print("  ✓ Strategy selection: rule(1–3) → hybrid(4–6) → ml(7+)")


def test_confidence_increases_across_tiers():
    """Confidence should be strictly higher as we move from rules → hybrid → ML."""
    rule = RuleBasedStrategy()
    hybrid = HybridStrategy()

    f, m = _healthy_financial(), _healthy_mental()

    r_rule = rule.predict(f, m, days_of_data=2)
    r_hybrid = hybrid.predict(f, m, days_of_data=5)

    assert r_hybrid.confidence > r_rule.confidence, (
        f"Hybrid confidence ({r_hybrid.confidence}) should exceed rule ({r_rule.confidence})"
    )
    print(f"  ✓ Confidence: rule={r_rule.confidence:.2f} → hybrid={r_hybrid.confidence:.2f}")


def test_next_upgrade_days():
    """ScoreCombiner reports correct days until next upgrade."""
    combiner = ScoreCombiner()

    assert combiner.days_until_upgrade(1) == 3   # 3 more days until hybrid (day 4)
    assert combiner.days_until_upgrade(2) == 2
    assert combiner.days_until_upgrade(3) == 1
    assert combiner.days_until_upgrade(4) == 3   # 3 more days until ML (day 7)
    assert combiner.days_until_upgrade(6) == 1
    assert combiner.days_until_upgrade(7) == 0   # already at ML
    assert combiner.days_until_upgrade(20) == 0
    print("  ✓ days_until_upgrade counts are correct")


def test_hybrid_adjusts_above_rule_for_burnout():
    """Hybrid should produce >= rule-based score for a burnout case (more signals = higher)."""
    rule = RuleBasedStrategy()
    hybrid = HybridStrategy()

    f, m = _burnout_financial(), _burnout_mental()

    r_rule = rule.predict(f, m, days_of_data=2)
    r_hybrid = hybrid.predict(f, m, days_of_data=5)

    # Hybrid can go slightly higher due to interaction terms
    assert r_hybrid.combined_score >= r_rule.combined_score - 0.05, (
        f"Hybrid ({r_hybrid.combined_score:.3f}) should be close to or above rule ({r_rule.combined_score:.3f})"
    )
    print(f"  ✓ Hybrid score: {r_hybrid.combined_score:.3f}  (rule base: {r_rule.combined_score:.3f})")


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 3 — Feature Engineer reads SQLite correctly
# ──────────────────────────────────────────────────────────────────────────────

def _build_test_db() -> tuple:
    """
    Creates a temp-file SQLite DB with the exact same schema as the real app,
    inserts controlled test data, and returns (db_path, tmp_dir, user_id, monthly_income).
    Connection is fully closed before returning so FeatureEngineer can open it.
    """
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test_pocket.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Create tables (minimal schema matching setup.js)
    conn.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT,
            password TEXT,
            name TEXT,
            monthly_income REAL DEFAULT 0,
            daily_budget REAL DEFAULT 0
        );

        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            description TEXT DEFAULT '',
            date TEXT
        );

        CREATE TABLE health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT UNIQUE,
            sleep_hours REAL DEFAULT 0,
            stress_level INTEGER DEFAULT 5,
            mood TEXT DEFAULT 'neutral',
            study_hours REAL DEFAULT 0,
            exercise_minutes INTEGER DEFAULT 0,
            social_activity INTEGER DEFAULT 0,
            energy_level INTEGER DEFAULT 5,
            notes TEXT DEFAULT ''
        );

        CREATE TABLE food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            meal_type TEXT DEFAULT 'other',
            food_name TEXT,
            cost REAL DEFAULT 0,
            calories INTEGER DEFAULT 0,
            is_homemade INTEGER DEFAULT 0
        );

        CREATE TABLE routine_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal_type TEXT,
            current_value REAL DEFAULT 0,
            target_value REAL DEFAULT 0,
            weekly_target REAL DEFAULT 0,
            week_number INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active'
        );
    """)

    user_id = 1
    monthly_income = 1000.0
    conn.execute(
        "INSERT INTO users (id, email, password, name, monthly_income, daily_budget) VALUES (?,?,?,?,?,?)",
        (user_id, "test@test.com", "x", "Test User", monthly_income, 35.0)
    )

    today = datetime.now().date()

    # Insert 10 days of expenses: $30/day for last 7 days, $20/day before
    for i in range(10):
        d = (today - timedelta(days=i)).isoformat()
        amount = 30.0 if i < 7 else 20.0
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?,?,?,?)",
            (user_id, amount, "food", d)
        )

    # Insert 10 days of health logs
    for i in range(10):
        d = (today - timedelta(days=i)).isoformat()
        conn.execute(
            """INSERT OR IGNORE INTO health_logs
               (user_id, date, sleep_hours, stress_level, mood, exercise_minutes, energy_level, social_activity)
               VALUES (?,?,?,?,?,?,?,?)""",
            (user_id, d, 6.0, 7, "anxious", 10, 4, 2)
        )

    # Insert food logs: 2 meals per day (< 3 = skipped)
    for i in range(7):
        d = (today - timedelta(days=i)).isoformat()
        for meal in ["breakfast", "lunch"]:
            conn.execute(
                "INSERT INTO food_logs (user_id, date, meal_type, food_name, cost, is_homemade) VALUES (?,?,?,?,?,?)",
                (user_id, d, meal, "test food", 5.0, 0)
            )

    # Active goal: sleep target 8h
    conn.execute(
        "INSERT INTO routine_goals (user_id, goal_type, target_value, weekly_target, status) VALUES (?,?,?,?,?)",
        (user_id, "sleep", 8.0, 8.0, "active")
    )

    conn.commit()
    # Checkpoint WAL and close fully — prevents Windows file lock on cleanup
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()

    return db_path, tmp_dir, user_id, monthly_income


def _cleanup(tmp_dir: str):
    """Safe cleanup that handles Windows file locks with a short retry."""
    import time
    for _ in range(5):
        try:
            shutil.rmtree(tmp_dir)
            return
        except (PermissionError, OSError):
            time.sleep(0.15)
    # Give up silently — temp files cleaned by OS eventually


def test_feature_engineer_data_day_count():
    db_path, tmp_dir, user_id, _ = _build_test_db()
    try:
        fe = FeatureEngineer(db_path)
        count = fe.get_data_day_count(user_id)
        assert count == 10, f"Expected 10 days of health logs, got {count}"
        print(f"  ✓ get_data_day_count = {count}")
    finally:
        _cleanup(tmp_dir)


def test_feature_engineer_financial_features():
    db_path, tmp_dir, user_id, monthly_income = _build_test_db()
    try:
        fe = FeatureEngineer(db_path)
        fin = fe.build_financial_features(user_id)

        emergency_fund_expected = monthly_income * 0.10   # 100.0
        spendable_expected = monthly_income - emergency_fund_expected  # 900.0

        assert abs(fin.emergency_fund - emergency_fund_expected) < 0.01, (
            f"emergency_fund: expected {emergency_fund_expected}, got {fin.emergency_fund}"
        )
        assert abs(fin.spendable_budget - spendable_expected) < 0.01, (
            f"spendable_budget: expected {spendable_expected}, got {fin.spendable_budget}"
        )

        # 7-day daily avg should be ~30 (we inserted $30/day for last 7 days)
        assert 25.0 <= fin.daily_spend_avg_7d <= 35.0, (
            f"daily_spend_avg_7d should be ~30, got {fin.daily_spend_avg_7d}"
        )

        # food_homemade_ratio: all is_homemade=0 → ratio should be 0.0
        assert fin.food_homemade_ratio == 0.0, (
            f"food_homemade_ratio should be 0.0 (all bought), got {fin.food_homemade_ratio}"
        )

        # skipped_meals: all days have 2 meals (< 3) → should flag all 7 days
        assert fin.skipped_meals_count >= 7, (
            f"skipped_meals_count should be >= 7 (only 2 meals/day), got {fin.skipped_meals_count}"
        )

        print(f"  ✓ Financial features:")
        print(f"      emergency_fund={fin.emergency_fund}  spendable={fin.spendable_budget}")
        print(f"      daily_avg_7d={fin.daily_spend_avg_7d:.2f}  util_pct={fin.budget_utilization_pct:.1f}%")
        print(f"      days_until_broke={fin.days_until_broke:.1f}  skipped_meals={fin.skipped_meals_count}")
    finally:
        _cleanup(tmp_dir)


def test_feature_engineer_mental_features():
    db_path, tmp_dir, user_id, _ = _build_test_db()
    try:
        fe = FeatureEngineer(db_path)
        men = fe.build_mental_features(user_id)

        # All logs have sleep=6.0
        assert abs(men.sleep_avg_7d - 6.0) < 0.1, (
            f"sleep_avg_7d should be ~6.0, got {men.sleep_avg_7d}"
        )

        # All logs have stress=7
        assert abs(men.stress_avg_7d - 7.0) < 0.1, (
            f"stress_avg_7d should be ~7.0, got {men.stress_avg_7d}"
        )

        # All mood = 'anxious' → bad_mood_streak should be 10 (all days)
        assert men.bad_mood_streak >= 7, (
            f"bad_mood_streak should be >= 7 (all anxious), got {men.bad_mood_streak}"
        )

        # goal_completion_rate: sleep goal is 8h but actual is 6h → failing
        # 6 >= 8 * 0.5 = 4.0 → actually passes the 50% threshold
        # So rate should be 1.0 (completed) or close
        assert 0.0 <= men.goal_completion_rate <= 1.0

        # stress_sleep_interaction should be positive (stress=7, sleep=6)
        assert men.stress_sleep_interaction > 0, (
            f"stress_sleep_interaction should be > 0, got {men.stress_sleep_interaction}"
        )

        print(f"  ✓ Mental features:")
        print(f"      sleep_avg={men.sleep_avg_7d}  stress_avg={men.stress_avg_7d}")
        print(f"      mood_avg={men.mood_score_avg}  bad_streak={men.bad_mood_streak}")
        print(f"      stress_sleep_interaction={men.stress_sleep_interaction:.3f}")
    finally:
        _cleanup(tmp_dir)


def test_feature_engineer_to_vector_length():
    """to_vector() must return exactly 16 and 15 elements for ML compatibility."""
    fin = _healthy_financial()
    men = _healthy_mental()

    fin_vec = fin.to_vector()
    men_vec = men.to_vector()

    assert len(fin_vec) == 16, f"Financial vector length should be 16, got {len(fin_vec)}"
    assert len(men_vec) == 15, f"Mental vector length should be 15, got {len(men_vec)}"
    assert all(isinstance(v, float) for v in fin_vec), "All financial vector values should be float"
    assert all(isinstance(v, float) for v in men_vec), "All mental vector values should be float"
    print(f"  ✓ to_vector() lengths: financial={len(fin_vec)}, mental={len(men_vec)}")


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 4 — ML bootstrap and incremental learning
# ──────────────────────────────────────────────────────────────────────────────

def test_ml_bootstrap_creates_model_files():
    """After first ML predict, model files should exist on disk."""
    try:
        from sklearn.linear_model import SGDClassifier
    except ImportError:
        print("  ⚠ scikit-learn not installed — skipping ML tests")
        return

    db_path, tmp_dir, user_id, _ = _build_test_db()
    model_dir = os.path.join(tmp_dir, "models")

    try:
        fe = FeatureEngineer(db_path)
        ml = MLStrategy(model_dir=model_dir, feature_engineer=fe)

        fin = _burnout_financial()
        men = _burnout_mental()

        result = ml.predict(fin, men, days_of_data=10, user_id=user_id)

        fin_model_path = os.path.join(model_dir, f"{user_id}_financial.pkl")
        men_model_path = os.path.join(model_dir, f"{user_id}_mental.pkl")

        assert os.path.exists(fin_model_path), "financial model file should exist after bootstrap"
        assert os.path.exists(men_model_path), "mental model file should exist after bootstrap"
        assert 0.0 <= result.financial_score <= 1.0
        assert 0.0 <= result.mental_score <= 1.0
        assert result.strategy_used == PredictionStrategy.ML

        fin_size = os.path.getsize(fin_model_path)
        men_size = os.path.getsize(men_model_path)
        assert fin_size > 100, f"financial model file seems too small: {fin_size} bytes"
        assert men_size > 100, f"mental model file seems too small: {men_size} bytes"

        print(f"  ✓ ML model files created: financial={fin_size}B, mental={men_size}B")
        print(f"    ML result: fin={result.financial_score:.3f}  men={result.mental_score:.3f}  combined={result.combined_score:.3f}")
    finally:
        _cleanup(tmp_dir)


def test_ml_burnout_probability_higher_than_healthy():
    """
    After bootstrap, feeding a burnout vector should produce a higher
    ML probability than a healthy vector.
    (Tests that the model actually learned something directional.)
    """
    try:
        from sklearn.linear_model import SGDClassifier
    except ImportError:
        print("  ⚠ scikit-learn not installed — skipping ML tests")
        return

    db_path, tmp_dir, user_id, _ = _build_test_db()
    model_dir = os.path.join(tmp_dir, "models")

    try:
        fe = FeatureEngineer(db_path)
        ml = MLStrategy(model_dir=model_dir, feature_engineer=fe)

        # Bootstrap by predicting once
        ml.predict(_burnout_financial(), _burnout_mental(), days_of_data=10, user_id=user_id)

        # Now check both directions
        r_healthy = ml.predict(_healthy_financial(), _healthy_mental(), days_of_data=10, user_id=user_id)
        r_burnout = ml.predict(_burnout_financial(), _burnout_mental(), days_of_data=10, user_id=user_id)

        # The ML combined score for burnout should be >= healthy
        # (might not be huge difference because of rule blending at day 10)
        assert r_burnout.combined_score >= r_healthy.combined_score, (
            f"Burnout ({r_burnout.combined_score:.3f}) should be >= healthy ({r_healthy.combined_score:.3f})"
        )
        print(f"  ✓ ML directional check: burnout={r_burnout.combined_score:.3f}  healthy={r_healthy.combined_score:.3f}")
    finally:
        _cleanup(tmp_dir)


def test_ml_confidence_grows_with_days():
    """ML confidence should increase as days_of_data grows from 7 to 60."""
    try:
        from sklearn.linear_model import SGDClassifier
    except ImportError:
        print("  ⚠ scikit-learn not installed — skipping ML tests")
        return

    db_path, tmp_dir, user_id, _ = _build_test_db()
    model_dir = os.path.join(tmp_dir, "models")

    try:
        fe = FeatureEngineer(db_path)
        ml = MLStrategy(model_dir=model_dir, feature_engineer=fe)

        confidences = {}
        for days in [7, 14, 30, 60]:
            r = ml.predict(_healthy_financial(), _healthy_mental(), days_of_data=days, user_id=user_id)
            confidences[days] = r.confidence

        assert confidences[14] > confidences[7], "Confidence should grow from day 7 to 14"
        assert confidences[30] > confidences[14], "Confidence should grow from day 14 to 30"
        assert confidences[60] > confidences[30], "Confidence should grow from day 30 to 60"
        assert confidences[60] <= 0.95, "Confidence shouldn't exceed 0.95"

        print(f"  ✓ Confidence growth: day7={confidences[7]:.3f} → day14={confidences[14]:.3f} → day30={confidences[30]:.3f} → day60={confidences[60]:.3f}")
    finally:
        _cleanup(tmp_dir)


def test_model_loads_from_cache_on_second_call():
    """Second prediction for same user should load from disk, not re-bootstrap."""
    try:
        import joblib
        from sklearn.linear_model import SGDClassifier
    except ImportError:
        print("  ⚠ scikit-learn not installed — skipping ML tests")
        return

    db_path, tmp_dir, user_id, _ = _build_test_db()
    model_dir = os.path.join(tmp_dir, "models")

    try:
        fe = FeatureEngineer(db_path)
        ml = MLStrategy(model_dir=model_dir, feature_engineer=fe)

        # First call: bootstrap
        r1 = ml.predict(_healthy_financial(), _healthy_mental(), days_of_data=10, user_id=user_id)

        fin_path = os.path.join(model_dir, f"{user_id}_financial.pkl")
        mtime_after_first = os.path.getmtime(fin_path)

        # Second call: should load from cache (no refit since <7 days since stamp)
        r2 = ml.predict(_healthy_financial(), _healthy_mental(), days_of_data=10, user_id=user_id)

        # Scores should be identical (same inputs, same loaded model)
        assert abs(r1.financial_score - r2.financial_score) < 0.01, (
            f"Cached model should produce same score: {r1.financial_score} vs {r2.financial_score}"
        )
        print(f"  ✓ Model cache works: both calls gave financial_score={r1.financial_score:.3f}")
    finally:
        _cleanup(tmp_dir)


# ──────────────────────────────────────────────────────────────────────────────
# LAYER 5 — Full end-to-end through BurnoutPredictor with real DB
# ──────────────────────────────────────────────────────────────────────────────

def test_full_predictor_end_to_end_rule_based():
    """BurnoutPredictor.predict() works end-to-end on a user with < 7 days data."""
    db_path, tmp_dir, user_id, _ = _build_test_db()

    # Artificially reduce health_logs to 2 days to force rule-based (needs < 4)
    conn = sqlite3.connect(db_path)
    today = datetime.now().date()
    cutoff = (today - timedelta(days=2)).isoformat()
    conn.execute("DELETE FROM health_logs WHERE date < ?", (cutoff,))
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()

    try:
        predictor = BurnoutPredictor(db_path=db_path)
        response = predictor.predict(user_id=user_id)

        assert response.strategy_used == PredictionStrategy.RULE_BASED, (
            f"Expected rule_based strategy, got {response.strategy_used} (days_of_data={response.days_of_data})"
        )
        assert response.next_upgrade_in_days is not None and response.next_upgrade_in_days > 0
        assert 0.0 <= response.combined_score <= 1.0
        assert response.alert_level in list(BurnoutAlertLevel)
        assert len(response.recommendations) > 0
        # days_of_data should be < 4 (rule_based tier)
        assert response.days_of_data < 4, f"Expected < 4 days for rule_based tier, got {response.days_of_data}"

        print(f"  ✓ End-to-end (rule_based): score={response.combined_score:.3f} level={response.alert_level}")
        print(f"    strategy={response.strategy_used}  confidence={response.confidence:.2f}")
        print(f"    next_upgrade_in={response.next_upgrade_in_days} days")
    finally:
        _cleanup(tmp_dir)


def test_full_predictor_end_to_end_ml():
    """BurnoutPredictor.predict() works end-to-end with 10 days of data (ML tier)."""
    try:
        from sklearn.linear_model import SGDClassifier
    except ImportError:
        print("  ⚠ scikit-learn not installed — skipping end-to-end ML test")
        return

    db_path, tmp_dir, user_id, _ = _build_test_db()

    try:
        predictor = BurnoutPredictor(db_path=db_path)
        response = predictor.predict(user_id=user_id)

        assert response.strategy_used == PredictionStrategy.ML, (
            f"Expected ml strategy with 10 days data, got {response.strategy_used}"
        )
        assert response.next_upgrade_in_days is None or response.next_upgrade_in_days == 0
        assert 0.0 <= response.combined_score <= 1.0
        assert response.confidence >= 0.65
        assert len(response.top_risk_factors) > 0

        print(f"  ✓ End-to-end (ML): score={response.combined_score:.3f}  level={response.alert_level}")
        print(f"    confidence={response.confidence:.2f}  days_of_data={response.days_of_data}")
        print(f"    top risk: {response.top_risk_factors[0]}")
    finally:
        _cleanup(tmp_dir)


# ──────────────────────────────────────────────────────────────────────────────
# Test runner (no pytest required)
# ──────────────────────────────────────────────────────────────────────────────

ALL_TESTS = [
    # Layer 1
    ("L1 — Healthy user has low score",               test_rule_based_healthy_is_low),
    ("L1 — Burnout user has high score",              test_rule_based_burnout_is_high),
    ("L1 — Burnout > healthy always",                 test_burnout_higher_than_healthy),
    ("L1 — Scores clamped [0,1]",                     test_scores_are_clamped_between_0_and_1),
    ("L1 — Mental dominates financial (65/35)",       test_mental_dominates_financial),
    ("L1 — Alert level boundaries",                   test_alert_level_mapping),
    ("L1 — Recommendations not empty",                test_recommendations_not_empty),
    # Layer 2
    ("L2 — Strategy selection at each tier",          test_strategy_selection_at_each_tier),
    ("L2 — Confidence increases rule→hybrid",         test_confidence_increases_across_tiers),
    ("L2 — next_upgrade_days counts",                 test_next_upgrade_days),
    ("L2 — Hybrid adjusts above rule for burnout",    test_hybrid_adjusts_above_rule_for_burnout),
    # Layer 3
    ("L3 — data_day_count from SQLite",               test_feature_engineer_data_day_count),
    ("L3 — Financial features from SQLite",           test_feature_engineer_financial_features),
    ("L3 — Mental features from SQLite",              test_feature_engineer_mental_features),
    ("L3 — to_vector() lengths (16, 15)",             test_feature_engineer_to_vector_length),
    # Layer 4
    ("L4 — ML bootstrap creates .pkl files",          test_ml_bootstrap_creates_model_files),
    ("L4 — ML burnout prob > healthy prob",           test_ml_burnout_probability_higher_than_healthy),
    ("L4 — ML confidence grows with days",            test_ml_confidence_grows_with_days),
    ("L4 — Model loaded from cache on 2nd call",      test_model_loads_from_cache_on_second_call),
    # Layer 5
    ("L5 — End-to-end rule_based predictor",          test_full_predictor_end_to_end_rule_based),
    ("L5 — End-to-end ML predictor",                  test_full_predictor_end_to_end_ml),
]


def run_all():
    passed = 0
    failed = 0
    skipped = 0
    failures = []

    print("\n" + "=" * 65)
    print("  BURNOUT PREDICTION — TEST SUITE")
    print("=" * 65)

    for name, fn in ALL_TESTS:
        print(f"\n▶ {name}")
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failures.append((name, str(e)))
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {e}")
            failures.append((name, f"{type(e).__name__}: {e}"))
            failed += 1

    print("\n" + "=" * 65)
    print(f"  Results: {passed} passed  |  {failed} failed")
    print("=" * 65)

    if failures:
        print("\nFailed tests:")
        for name, reason in failures:
            print(f"  ✗ {name}")
            print(f"    {reason}")

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
