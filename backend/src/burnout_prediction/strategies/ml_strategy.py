"""
Tier 3 — ML Strategy  (day 7+)
Uses SGDClassifier (supports partial_fit for incremental learning).

Boot-strapping:
  On first call (no saved model yet), synthetic labels are generated from
  the rule-based logic, an initial model is fitted, and the model is cached.

Auto-refit:
  Every 7 days the model is re-fitted on a fresh 30-day sliding window,
  so it keeps improving without any manual intervention.

Persistence:
  Models are saved per-user as .pkl files using joblib.
  If the models/ directory doesn't exist it is created automatically.
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Tuple

import joblib
import numpy as np

try:
    from sklearn.linear_model import SGDClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

from ..schemas import FinancialFeatures, MentalFeatures, PredictionStrategy
from .base_strategy import BaseStrategy, StrategyResult
from .rule_based import RuleBasedStrategy

log = logging.getLogger(__name__)

# Number of classes: 0 = no burnout, 1 = burnout
_CLASSES = np.array([0, 1])

# Label thresholds for synthetic bootstrap labels
_FIN_BURNOUT_THRESHOLD = 0.50   # rule-based fin score ≥ 0.50 → label 1
_MEN_BURNOUT_THRESHOLD = 0.50   # rule-based men score ≥ 0.50 → label 1


class MLStrategy(BaseStrategy):
    """
    SGD-based incremental classifier.
    One model per user, one each for financial and mental dimensions.
    Falls back gracefully to the hybrid strategy if sklearn is missing
    or the model has not yet been fitted.
    """

    def __init__(self, model_dir: str, feature_engineer=None):
        """
        Parameters
        ----------
        model_dir       : directory where per-user .pkl files are stored
        feature_engineer: FeatureEngineer instance (needed for refit)
        """
        self.model_dir = model_dir
        self.feature_engineer = feature_engineer
        self._rules = RuleBasedStrategy()

        os.makedirs(model_dir, exist_ok=True)

        if not _SKLEARN_AVAILABLE:
            log.warning(
                "scikit-learn not installed — MLStrategy will fall back to rules"
            )

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def predict(
        self,
        financial_features: FinancialFeatures,
        mental_features: MentalFeatures,
        days_of_data: int,
        user_id: Optional[int] = None,
    ) -> StrategyResult:

        if not _SKLEARN_AVAILABLE or user_id is None:
            # Fall back: use rule-based but report as ml with lower confidence
            base = self._rules.predict(financial_features, mental_features, days_of_data)
            return StrategyResult(
                financial_score=base.financial_score,
                mental_score=base.mental_score,
                combined_score=base.combined_score,
                confidence=0.60,
                strategy_used=PredictionStrategy.ML,
                risk_factors=base.risk_factors,
                financial_details=base.financial_details,
                mental_details=base.mental_details,
            )

        fin_model, men_model = self._load_or_bootstrap(user_id, days_of_data)

        fin_vec = np.array(financial_features.to_vector()).reshape(1, -1)
        men_vec = np.array(mental_features.to_vector()).reshape(1, -1)

        # Predict probabilities (probability of burnout class = 1)
        fin_prob = self._safe_predict_proba(fin_model, fin_vec)
        men_prob = self._safe_predict_proba(men_model, men_vec)

        # Blend with rule-based scores at early ML stage
        # As days grow, ML weight increases; fully ML at 30 days
        ml_weight = min(1.0, (days_of_data - 7) / 23.0)  # 0 at day7, 1 at day30
        rule_base = self._rules.predict(financial_features, mental_features, days_of_data)

        fin_score = ml_weight * fin_prob + (1 - ml_weight) * rule_base.financial_score
        men_score = ml_weight * men_prob + (1 - ml_weight) * rule_base.mental_score
        combined = round(0.35 * fin_score + 0.65 * men_score, 4)

        # Confidence: 0.65 at day 7, grows toward 0.92 at day 60
        confidence = 0.65 + min(0.27, (days_of_data - 7) * 0.004)

        # Periodically refit (every 7 days, using last 30 days of history)
        self._maybe_refit(user_id, days_of_data)

        return StrategyResult(
            financial_score=round(fin_score, 4),
            mental_score=round(men_score, 4),
            combined_score=combined,
            confidence=round(confidence, 4),
            strategy_used=PredictionStrategy.ML,
            risk_factors=rule_base.risk_factors,  # rules still explain the why
            financial_details={
                **rule_base.financial_details,
                "ml_probability": round(fin_prob, 4),
                "ml_weight": round(ml_weight, 4),
            },
            mental_details={
                **rule_base.mental_details,
                "ml_probability": round(men_prob, 4),
                "ml_weight": round(ml_weight, 4),
            },
        )

    # ──────────────────────────────────────────────────────────────────
    # Model loading / bootstrapping
    # ──────────────────────────────────────────────────────────────────

    def _load_or_bootstrap(
        self, user_id: int, days_of_data: int
    ) -> Tuple[Pipeline, Pipeline]:
        fin_path = self._model_path(user_id, "financial")
        men_path = self._model_path(user_id, "mental")

        # Try to load existing models first
        if os.path.exists(fin_path) and os.path.exists(men_path):
            try:
                fin_model = joblib.load(fin_path)
                men_model = joblib.load(men_path)
                return fin_model, men_model
            except Exception as e:
                log.warning(f"Failed to load models for user {user_id}: {e}")

        # Need at least 5 days of data before bootstrap is meaningful
        if days_of_data < 5:
            log.info(
                f"User {user_id} has only {days_of_data} days of data — "
                "using unfitted pipelines until more data is available"
            )
            return self._make_pipeline(), self._make_pipeline()

        # Bootstrap from historical data + synthetic labels
        log.info(f"Bootstrapping ML models for user {user_id}")
        return self._bootstrap(user_id)

    def _bootstrap(self, user_id: int) -> Tuple[Pipeline, Pipeline]:
        """
        1. Fetch historical feature rows (last 30 days)
        2. Generate synthetic labels using rule-based thresholds
        3. Fit SGD classifiers
        4. Save to disk
        """
        fin_model = self._make_pipeline()
        men_model = self._make_pipeline()

        if self.feature_engineer is None:
            log.warning("No FeatureEngineer — returning unfitted pipelines")
            return fin_model, men_model

        rows = self.feature_engineer.get_historical_feature_rows(user_id, days=30)

        if len(rows) < 5:
            log.info(
                f"Only {len(rows)} historical rows for user {user_id}; "
                "bootstrapping with minimal data"
            )

        fin_X, fin_y = [], []
        men_X, men_y = [], []

        for row in rows:
            fv = row["fin_vector"]
            mv = row["men_vector"]

            if fv and len(fv) == 16:
                fin_label = self._synthetic_fin_label(fv)
                fin_X.append(fv)
                fin_y.append(fin_label)

            if mv and len(mv) == 15:
                men_label = self._synthetic_men_label(mv)
                men_X.append(mv)
                men_y.append(men_label)

        # Ensure both classes are represented (add dummy rows if not)
        fin_X, fin_y = self._ensure_both_classes(fin_X, fin_y, n_features=16)
        men_X, men_y = self._ensure_both_classes(men_X, men_y, n_features=15)

        fin_model.fit(np.array(fin_X), np.array(fin_y))
        men_model.fit(np.array(men_X), np.array(men_y))

        self._save_models(user_id, fin_model, men_model)

        # Write refit stamp so _maybe_refit doesn't immediately refit after bootstrap
        stamp_path = self._model_path(user_id, "refit_stamp")
        try:
            with open(stamp_path, "w") as fh:
                fh.write(datetime.now().isoformat())
        except Exception as e:
            log.warning(f"Failed to write refit stamp for user {user_id}: {e}")

        return fin_model, men_model

    def _maybe_refit(self, user_id: int, days_of_data: int):
        """
        Refit every 7 days using the last 30-day sliding window.
        Decision is based on a refit-stamp file.
        """
        stamp_path = self._model_path(user_id, "refit_stamp")

        should_refit = False
        if not os.path.exists(stamp_path):
            should_refit = True
        else:
            try:
                with open(stamp_path) as fh:
                    last_refit = datetime.fromisoformat(fh.read().strip())
                if (datetime.now() - last_refit).days >= 7:
                    should_refit = True
            except Exception:
                should_refit = True

        if should_refit and self.feature_engineer is not None:
            log.info(f"Refitting ML models for user {user_id}")
            try:
                self._refit(user_id)
                with open(stamp_path, "w") as fh:
                    fh.write(datetime.now().isoformat())
            except Exception as e:
                log.warning(f"Refit failed for user {user_id}: {e}")

    def _refit(self, user_id: int):
        """Full refit on fresh 30-day data using partial_fit for incremental update."""
        rows = self.feature_engineer.get_historical_feature_rows(user_id, days=30)
        if len(rows) < 5:
            return

        fin_path = self._model_path(user_id, "financial")
        men_path = self._model_path(user_id, "mental")

        if not (os.path.exists(fin_path) and os.path.exists(men_path)):
            self._bootstrap(user_id)
            return

        fin_model = joblib.load(fin_path)
        men_model = joblib.load(men_path)

        # Collect all rows first, then partial_fit in one batch (ensures both classes present)
        fin_X, fin_y = [], []
        men_X, men_y = [], []

        for row in rows:
            fv = row["fin_vector"]
            mv = row["men_vector"]
            if fv and len(fv) == 16:
                fin_X.append(fv)
                fin_y.append(self._synthetic_fin_label(fv))
            if mv and len(mv) == 15:
                men_X.append(mv)
                men_y.append(self._synthetic_men_label(mv))

        if fin_X:
            fin_X, fin_y = self._ensure_both_classes(fin_X, fin_y, n_features=16)
            self._partial_fit_pipeline(fin_model, fin_X, fin_y)

        if men_X:
            men_X, men_y = self._ensure_both_classes(men_X, men_y, n_features=15)
            self._partial_fit_pipeline(men_model, men_X, men_y)

        self._save_models(user_id, fin_model, men_model)

    # ──────────────────────────────────────────────────────────────────
    # Synthetic label generation  (rule-based → ML labels)
    # ──────────────────────────────────────────────────────────────────

    def _synthetic_fin_label(self, fv: List[float]) -> int:
        """
        Features order (matches FinancialFeatures.to_vector):
        [daily_7d, daily_30d, wk_curr, wk_last, growth, projected,
         util_pct, days_broke, food_r, transport_r, ent_r, impulse,
         safety_margin, cat_overspend, homemade_r, skip_meals]
        """
        days_broke = fv[7]
        util_pct = fv[6]
        growth = fv[4]
        safety_margin = fv[12]

        score = 0.0
        if days_broke < 7:
            score += 0.40
        elif days_broke < 14:
            score += 0.20
        if util_pct > 110:
            score += 0.30
        elif util_pct > 90:
            score += 0.15
        if growth > 0.60:
            score += 0.20
        elif growth > 0.30:
            score += 0.10
        if safety_margin < 0:
            score += 0.10

        return 1 if score >= _FIN_BURNOUT_THRESHOLD else 0

    def _synthetic_men_label(self, mv: List[float]) -> int:
        """
        Features order (matches MentalFeatures.to_vector):
        [sleep_avg, sleep_deficit, stress_avg, stress_trend, ex_avg,
         no_ex_days, mood_avg, streak, energy_avg, social_avg,
         goal_rate, missed_goals, skip_meals, sleep_cons, st_sl_inter]
        """
        sleep_avg = mv[0]
        stress_avg = mv[2]
        mood_avg = mv[6]
        streak = mv[7]
        stress_sleep = mv[14]

        score = 0.0
        if sleep_avg < 5.0:
            score += 0.35
        elif sleep_avg < 6.5:
            score += 0.15
        if stress_avg >= 8.0:
            score += 0.35
        elif stress_avg >= 6.5:
            score += 0.15
        if mood_avg <= -0.6:
            score += 0.20
        elif mood_avg <= 0.0:
            score += 0.10
        if streak >= 3:
            score += 0.15
        if stress_sleep > 5.0:
            score += 0.10

        return 1 if score >= _MEN_BURNOUT_THRESHOLD else 0

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _make_pipeline() -> Pipeline:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SGDClassifier(
                loss="log_loss",        # gives probabilities
                max_iter=1000,
                tol=1e-3,
                random_state=42,
                class_weight="balanced",  # handles imbalanced labels
            )),
        ])

    @staticmethod
    def _safe_predict_proba(model: Pipeline, X: np.ndarray) -> float:
        try:
            proba = model.predict_proba(X)[0]
            if len(proba) == 2:
                # Normal case: [p_class0, p_class1]
                return float(proba[1])
            # Edge case: model only saw one class during training.
            # We can't know if it's the burnout class or not — return neutral 0.5.
            return 0.5
        except Exception as e:
            log.warning(f"predict_proba failed: {e}")
            return 0.5

    @staticmethod
    def _partial_fit_pipeline(pipeline: Pipeline, X: List, y: List):
        """
        StandardScaler doesn't support partial_fit after initial fit in the same
        pipeline easily — we scale with the already-fitted scaler and partial_fit
        the SGD step directly.
        """
        try:
            X_arr = np.array(X)
            y_arr = np.array(y)
            X_scaled = pipeline.named_steps["scaler"].transform(X_arr)
            pipeline.named_steps["clf"].partial_fit(
                X_scaled, y_arr, classes=_CLASSES
            )
        except Exception as e:
            log.warning(f"partial_fit failed: {e}")

    @staticmethod
    def _ensure_both_classes(
        X: List, y: List, n_features: int
    ) -> Tuple[List, List]:
        """
        SGD requires both classes to be seen during fit.
        If one class is missing, add a minimal synthetic row.
        """
        if 0 not in y:
            X.append([0.0] * n_features)
            y.append(0)
        if 1 not in y:
            # A worst-case synthetic row for the burnout class
            X.append([99.0] * n_features)
            y.append(1)
        return X, y

    def _save_models(self, user_id: int, fin_model: Pipeline, men_model: Pipeline):
        try:
            joblib.dump(fin_model, self._model_path(user_id, "financial"))
            joblib.dump(men_model, self._model_path(user_id, "mental"))
        except Exception as e:
            log.warning(f"Failed to save models for user {user_id}: {e}")

    def _model_path(self, user_id: int, kind: str) -> str:
        return os.path.join(self.model_dir, f"{user_id}_{kind}.pkl")
