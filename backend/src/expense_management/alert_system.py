"""
Alert System for Expense Management
Handles alerts for category overspending and budget violations
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    def __init__(self, alert_id: str, user_id: str, category: str,
                 message: str, severity: AlertSeverity,
                 current_amount: float, budget_limit: float,
                 percentage_exceeded: float):
        self.alert_id = alert_id
        self.user_id = user_id
        self.category = category
        self.message = message
        self.severity = severity
        self.current_amount = current_amount
        self.budget_limit = budget_limit
        self.percentage_exceeded = percentage_exceeded
        self.created_at = datetime.now().isoformat()
        self.acknowledged = False

    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'user_id': self.user_id,
            'category': self.category,
            'message': self.message,
            'severity': self.severity.value,
            'current_amount': self.current_amount,
            'budget_limit': self.budget_limit,
            'percentage_exceeded': self.percentage_exceeded,
            'created_at': self.created_at,
            'acknowledged': self.acknowledged
        }


class AlertSystem:
    """Manages expense alerts and notifications"""

    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.OVERSPEND_THRESHOLD_HIGH = 0.20  # 20% over budget = high alert
        self.OVERSPEND_THRESHOLD_CRITICAL = 0.50  # 50% over budget = critical

    def check_category_overspending(self,
                                   user_id: str,
                                   budget_plan: Dict,
                                   current_expenses: Dict) -> List[Alert]:
        """Check if any category has exceeded budget"""
        alerts = []

        # Get current category totals
        category_totals = self._categorize_expenses(current_expenses)

        for category, budget_amount in budget_plan['budget_breakdown'].items():
            current_amount = category_totals.get(category, 0.0)

            if current_amount > budget_amount:
                percentage_exceeded = ((current_amount - budget_amount) / budget_amount) * 100

                # Determine severity
                if percentage_exceeded >= 50:
                    severity = AlertSeverity.CRITICAL
                    message = f"CRITICAL: {category.capitalize()} spending exceeded by {percentage_exceeded:.1f}%"
                elif percentage_exceeded >= 20:
                    severity = AlertSeverity.HIGH
                    message = f"HIGH: {category.capitalize()} spending exceeded by {percentage_exceeded:.1f}%"
                elif percentage_exceeded >= 10:
                    severity = AlertSeverity.MEDIUM
                    message = f"MEDIUM: {category.capitalize()} approaching budget limit (+{percentage_exceeded:.1f}%)"
                else:
                    severity = AlertSeverity.LOW
                    message = f"LOW: {category.capitalize()} slightly over budget (+{percentage_exceeded:.1f}%)"

                alert = Alert(
                    alert_id=f"alert_{user_id}_{category}_{datetime.now().timestamp()}",
                    user_id=user_id,
                    category=category,
                    message=message,
                    severity=severity,
                    current_amount=current_amount,
                    budget_limit=budget_amount,
                    percentage_exceeded=percentage_exceeded
                )
                alerts.append(alert)

        return alerts

    def check_total_budget_status(self,
                                 user_id: str,
                                 budget_plan: Dict,
                                 current_expenses: Dict) -> Optional[Alert]:
        """Check if total spending has exceeded total budget"""
        total_spent = sum(self._categorize_expenses(current_expenses).values())
        spending_budget = budget_plan['spending_budget']

        if total_spent > spending_budget:
            percentage_exceeded = ((total_spent - spending_budget) / spending_budget) * 100

            if percentage_exceeded >= 50:
                severity = AlertSeverity.CRITICAL
            elif percentage_exceeded >= 20:
                severity = AlertSeverity.HIGH
            elif percentage_exceeded >= 10:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW

            return Alert(
                alert_id=f"alert_{user_id}_total_{datetime.now().timestamp()}",
                user_id=user_id,
                category="total_budget",
                message=f"{severity.value.upper()}: Total budget exceeded by {percentage_exceeded:.1f}%",
                severity=severity,
                current_amount=total_spent,
                budget_limit=spending_budget,
                percentage_exceeded=percentage_exceeded
            )

        return None

    def get_remaining_budget(self,
                            budget_plan: Dict,
                            current_expenses: Dict) -> Dict:
        """Calculate remaining budget for each category"""
        category_totals = self._categorize_expenses(current_expenses)
        remaining = {}

        for category, budget_amount in budget_plan['budget_breakdown'].items():
            spent = category_totals.get(category, 0.0)
            remaining[category] = {
                'budget': budget_amount,
                'spent': spent,
                'remaining': budget_amount - spent,
                'percentage_used': (spent / budget_amount * 100) if budget_amount > 0 else 0
            }

        return remaining

    def save_alerts(self, user_id: str, alerts: List[Alert]) -> bool:
        """Save alerts to Firebase"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/alerts')
            alert_data = {alert.alert_id: alert.to_dict() for alert in alerts}
            ref.set(alert_data)
            return True
        except Exception as e:
            print(f"Error saving alerts: {e}")
            return False

    def get_user_alerts(self, user_id: str) -> List[Dict]:
        """Retrieve user's active alerts"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/alerts')
            alerts = ref.get()
            return list(alerts.values()) if alerts else []
        except Exception as e:
            print(f"Error retrieving alerts: {e}")
            return []

    def acknowledge_alert(self, user_id: str, alert_id: str) -> bool:
        """Mark alert as acknowledged"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/alerts/{alert_id}')
            ref.update({'acknowledged': True})
            return True
        except Exception as e:
            print(f"Error acknowledging alert: {e}")
            return False

    def _categorize_expenses(self, expenses: Dict) -> Dict[str, float]:
        """Helper to categorize expenses"""
        categories = {}
        for expense_id, expense_data in expenses.items():
            category = expense_data.get('category', 'others').lower()
            amount = float(expense_data.get('amount', 0))
            categories[category] = categories.get(category, 0) + amount
        return categories
