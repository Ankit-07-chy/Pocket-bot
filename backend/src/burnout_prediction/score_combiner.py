"""
Score Combiner
Converts raw financial/mental scores into:
  - combined_score  (0.35F + 0.65M)
  - alert_level     (good / moderate / high / crisis)
  - personalised recommendations
"""

from typing import List

from .schemas import BurnoutAlertLevel
from .strategies.base_strategy import StrategyResult


# Alert level boundaries (combined score thresholds)
_THRESHOLDS = {
    BurnoutAlertLevel.CRISIS: 0.75,
    BurnoutAlertLevel.HIGH: 0.55,
    BurnoutAlertLevel.MODERATE: 0.30,
    BurnoutAlertLevel.GOOD: 0.0,
}

# Recommendation bank keyed by (alert_level, dimension)
_RECS = {
    BurnoutAlertLevel.CRISIS: {
        "general": [
            "Please reach out to someone you trust today — a friend, family member, or counsellor.",
            "Take a complete break from non-essential tasks for at least 24 hours.",
        ],
        "financial": [
            "Review every expense in the last 7 days and cut anything non-essential immediately.",
            "Contact your university's financial aid office — emergency funds may be available.",
            "Consider meal prepping at home this week to cut food costs fast.",
        ],
        "mental": [
            "Sleep is your top priority right now — nothing else matters as much tonight.",
            "Box breathing (4-4-4-4) for 5 minutes can lower acute stress quickly.",
            "Speak to a counsellor or use the in-app peer support today.",
        ],
    },
    BurnoutAlertLevel.HIGH: {
        "general": [
            "Schedule a proper rest day this week — no studying, no side projects.",
            "Write down your top 3 priorities and ignore everything else for now.",
        ],
        "financial": [
            "Set a hard daily spending limit for the rest of the month.",
            "Switch to home-cooked meals for 5+ days to save on food costs.",
            "Identify your biggest non-essential category and pause it for a week.",
        ],
        "mental": [
            "Aim for at least 7 hours of sleep tonight — set a wind-down alarm.",
            "Add one 10-minute walk to your day; it measurably reduces cortisol.",
            "Avoid screens for 30 minutes before bed to improve sleep quality.",
        ],
    },
    BurnoutAlertLevel.MODERATE: {
        "general": [
            "Small actions compound: pick one positive habit to focus on this week.",
            "Check in with yourself daily — early awareness prevents escalation.",
        ],
        "financial": [
            "Review your spending categories — one category may be creeping up.",
            "Cook at home at least 4 days this week to stay on budget.",
        ],
        "mental": [
            "Your sleep average is slightly low — try sleeping 30 minutes earlier.",
            "Even 15 minutes of movement today can improve your mood and energy.",
        ],
    },
    BurnoutAlertLevel.GOOD: {
        "general": [
            "You're doing well — keep up your current habits.",
            "Consider helping a peer who might be struggling.",
        ],
        "financial": ["Your spending is under control. Keep it consistent."],
        "mental": ["Your wellness metrics look healthy. Maintain your routine."],
    },
}


class ScoreCombiner:
    """
    Takes a StrategyResult and returns enriched alert level + recommendations.
    Keeps financial and mental recommendations separate for clarity.
    """

    def get_alert_level(self, combined_score: float) -> BurnoutAlertLevel:
        if combined_score >= _THRESHOLDS[BurnoutAlertLevel.CRISIS]:
            return BurnoutAlertLevel.CRISIS
        if combined_score >= _THRESHOLDS[BurnoutAlertLevel.HIGH]:
            return BurnoutAlertLevel.HIGH
        if combined_score >= _THRESHOLDS[BurnoutAlertLevel.MODERATE]:
            return BurnoutAlertLevel.MODERATE
        return BurnoutAlertLevel.GOOD

    def build_recommendations(
        self,
        result: StrategyResult,
        alert_level: BurnoutAlertLevel,
    ) -> List[str]:
        """
        Returns a prioritised list of ≤ 6 recommendations.
        Financial recommendations are only included if fin_score is elevated.
        Mental recommendations are always included if mental score is elevated.
        """
        recs_pool = _RECS[alert_level]
        recs: List[str] = []

        # Always include general recommendations
        recs.extend(recs_pool.get("general", []))

        # Include mental recs if mental score is significant
        if result.mental_score >= 0.30:
            recs.extend(recs_pool.get("mental", []))

        # Include financial recs if financial score is significant
        if result.financial_score >= 0.30:
            recs.extend(recs_pool.get("financial", []))

        # Deduplicate while preserving order
        seen = set()
        unique_recs = []
        for r in recs:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)

        return unique_recs[:6]   # cap at 6 to avoid overwhelming the user

    def days_until_upgrade(self, days_of_data: int) -> int:
        """
        Returns how many more check-in days until the next strategy tier.
        Returns 0 if already at the highest tier (ML, day 7+).
        """
        if days_of_data < 4:
            return 4 - days_of_data   # days until Hybrid
        if days_of_data < 7:
            return 7 - days_of_data   # days until ML
        return 0
