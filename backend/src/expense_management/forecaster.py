"""
Expense Forecasting Module
Predicts future expenses using historical data and statistical methods
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from statistics import mean, stdev, median
import math


class ExpenseForecaster:
    """Forecasts future expenses based on historical patterns"""

    def __init__(self, firebase_service):
        self.firebase_service = firebase_service

    def forecast_next_month(self, user_id: str, confidence: float = 0.85) -> Dict:
        """Forecast next month's expenses"""
        try:
            all_expenses = self.firebase_service.get_user_expenses(user_id)

            if not all_expenses:
                return {'error': 'No historical data'}

            # Get last 6 months of data
            monthly_data = self._get_monthly_totals(all_expenses, months=6)

            if len(monthly_data) < 2:
                return {'error': 'Insufficient data for forecasting'}

            forecast_total = self._forecast_total_expense(monthly_data)
            category_forecast = self._forecast_by_category(user_id, all_expenses, monthly_data)

            return {
                'forecast_month': self._get_next_month(),
                'forecasted_total': forecast_total,
                'confidence_level': confidence,
                'category_forecast': category_forecast,
                'forecast_range': {
                    'low': forecast_total * (1 - (1 - confidence) / 2),
                    'high': forecast_total * (1 + (1 - confidence) / 2)
                },
                'based_on_months': len(monthly_data)
            }

        except Exception as e:
            print(f"Error forecasting: {e}")
            return {'error': str(e)}

    def forecast_category(self, user_id: str, category: str, months_ahead: int = 1) -> Dict:
        """Forecast expenses for a specific category"""
        try:
            all_expenses = self.firebase_service.get_user_expenses(user_id)

            if not all_expenses:
                return {'error': 'No historical data'}

            category_history = self._get_category_history(all_expenses, category, months=6)

            if len(category_history) < 2:
                return {'error': 'Insufficient data for this category'}

            forecast = self._forecast_values(category_history, months_ahead)

            return {
                'category': category,
                'forecast_months': months_ahead,
                'forecast_values': forecast,
                'current_trend': self._get_trend_direction(category_history),
                'average_historical': mean(category_history),
                'recommendation': self._get_category_recommendation(category, forecast)
            }

        except Exception as e:
            print(f"Error forecasting category: {e}")
            return {'error': str(e)}

    def detect_anomalies(self, user_id: str) -> Dict:
        """Detect unusual spending patterns"""
        try:
            all_expenses = self.firebase_service.get_user_expenses(user_id)

            if not all_expenses:
                return {'anomalies': []}

            monthly_data = self._get_monthly_totals(all_expenses, months=6)
            category_data = self._get_all_categories_history(all_expenses, months=6)

            anomalies = []

            # Detect outliers in total spending
            if len(monthly_data) > 2:
                mean_val = mean(monthly_data)
                std_val = stdev(monthly_data)
                threshold = mean_val + (2 * std_val)

                for i, value in enumerate(monthly_data):
                    if value > threshold:
                        anomalies.append({
                            'type': 'total_spending',
                            'severity': 'high',
                            'value': value,
                            'threshold': threshold,
                            'message': f'Unusually high spending: ₹{value:.2f}'
                        })

            # Detect category anomalies
            for category, history in category_data.items():
                if len(history) > 2:
                    mean_val = mean(history)
                    std_val = stdev(history)
                    threshold = mean_val + (1.5 * std_val)

                    if history[-1] > threshold:
                        anomalies.append({
                            'type': 'category',
                            'category': category,
                            'severity': 'medium',
                            'value': history[-1],
                            'average': mean_val,
                            'message': f'High {category} spending detected'
                        })

            return {
                'user_id': user_id,
                'anomalies': anomalies,
                'anomaly_count': len(anomalies),
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {'error': str(e)}

    def get_seasonal_forecast(self, user_id: str) -> Dict:
        """Get seasonal spending patterns and forecasts"""
        try:
            all_expenses = self.firebase_service.get_user_expenses(user_id)

            if not all_expenses:
                return {'error': 'No historical data'}

            monthly_data = self._get_monthly_totals(all_expenses, months=12)

            if len(monthly_data) < 4:
                return {'warning': 'Insufficient data for seasonal analysis'}

            seasonal_pattern = self._identify_seasonal_pattern(monthly_data)

            return {
                'user_id': user_id,
                'seasonal_pattern': seasonal_pattern,
                'high_spending_months': self._get_high_spending_months(monthly_data),
                'low_spending_months': self._get_low_spending_months(monthly_data),
                'recommendation': self._get_seasonal_recommendation(seasonal_pattern)
            }

        except Exception as e:
            print(f"Error analyzing seasons: {e}")
            return {'error': str(e)}

    def _forecast_total_expense(self, monthly_data: List[float]) -> float:
        """Forecast next month's total using average and trend"""
        # Use weighted average: more recent data weighted higher
        weights = list(range(1, len(monthly_data) + 1))
        weighted_avg = sum(v * w for v, w in zip(monthly_data, weights)) / sum(weights)

        # Check trend and adjust
        trend = monthly_data[-1] - monthly_data[0]
        trend_adjustment = trend / len(monthly_data)

        forecast = weighted_avg + trend_adjustment
        return max(0, forecast)

    def _forecast_by_category(self, user_id: str, all_expenses: Dict, monthly_data: List) -> Dict:
        """Forecast by category"""
        category_forecast = {}
        last_month_key = self._get_last_month_key()
        last_month_expenses = self._get_month_expenses(all_expenses, last_month_key)

        for expense_data in last_month_expenses.values():
            category = expense_data.get('category', 'others').lower()
            amount = float(expense_data.get('amount', 0))

            if category not in category_forecast:
                history = self._get_category_history(all_expenses, category, months=6)
                if history:
                    category_forecast[category] = {
                        'forecasted': self._forecast_values(history, 1)[0] if history else 0,
                        'historical_average': mean(history) if history else 0,
                        'last_month': amount
                    }

        return category_forecast

    def _forecast_values(self, history: List[float], periods: int = 1) -> List[float]:
        """Forecast future values using exponential smoothing"""
        if not history:
            return [0] * periods

        forecast = []
        alpha = 0.3  # Smoothing factor

        # Initialize with last value
        current = history[-1]

        for _ in range(periods):
            # Simple exponential smoothing
            current = alpha * history[-1] + (1 - alpha) * mean(history)
            forecast.append(max(0, current))

        return forecast

    def _get_trend_direction(self, values: List[float]) -> str:
        """Determine if trend is increasing or decreasing"""
        if len(values) < 2:
            return 'insufficient_data'

        avg_first_half = mean(values[:len(values)//2])
        avg_second_half = mean(values[len(values)//2:])

        if avg_second_half > avg_first_half * 1.1:
            return 'increasing'
        elif avg_second_half < avg_first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'

    def _get_category_recommendation(self, category: str, forecast: List[float]) -> str:
        """Generate recommendation based on category forecast"""
        if forecast and forecast[0] > 1000:
            return f"Consider reducing {category} spending to stay within budget"
        return f"{category.capitalize()} spending is within normal range"

    def _get_monthly_totals(self, expenses: Dict, months: int = 6) -> List[float]:
        """Get total spending for last N months"""
        today = datetime.now()
        totals = []

        for i in range(months, 0, -1):
            target_date = today - timedelta(days=30 * i)
            month_key = target_date.strftime('%Y-%m')

            month_total = 0
            for exp in expenses.values():
                try:
                    exp_date = datetime.fromisoformat(exp.get('date', ''))
                    if exp_date.strftime('%Y-%m') == month_key:
                        month_total += float(exp.get('amount', 0))
                except:
                    continue

            if month_total > 0:
                totals.append(month_total)

        return totals

    def _get_category_history(self, expenses: Dict, category: str, months: int = 6) -> List[float]:
        """Get spending history for a category"""
        today = datetime.now()
        history = []

        for i in range(months, 0, -1):
            target_date = today - timedelta(days=30 * i)
            month_key = target_date.strftime('%Y-%m')

            month_total = 0
            for exp in expenses.values():
                try:
                    exp_date = datetime.fromisoformat(exp.get('date', ''))
                    if exp_date.strftime('%Y-%m') == month_key and exp.get('category', '').lower() == category.lower():
                        month_total += float(exp.get('amount', 0))
                except:
                    continue

            history.append(month_total)

        return history

    def _get_all_categories_history(self, expenses: Dict, months: int = 6) -> Dict[str, List[float]]:
        """Get history for all categories"""
        categories = {}
        today = datetime.now()

        for i in range(months, 0, -1):
            target_date = today - timedelta(days=30 * i)
            month_key = target_date.strftime('%Y-%m')

            for exp in expenses.values():
                try:
                    exp_date = datetime.fromisoformat(exp.get('date', ''))
                    if exp_date.strftime('%Y-%m') == month_key:
                        category = exp.get('category', 'others').lower()
                        amount = float(exp.get('amount', 0))

                        if category not in categories:
                            categories[category] = []

                        # Find if this month already has data
                        if len(categories[category]) <= i - 1:
                            categories[category].append(amount)
                        else:
                            categories[category][i - 1] += amount
                except:
                    continue

        return categories

    def _identify_seasonal_pattern(self, monthly_data: List[float]) -> str:
        """Identify seasonal patterns"""
        if not monthly_data or len(monthly_data) < 4:
            return 'insufficient_data'

        # Simple pattern detection
        avg = mean(monthly_data)
        high_months = sum(1 for v in monthly_data if v > avg * 1.2)

        if high_months >= len(monthly_data) * 0.3:
            return 'seasonal_variations_detected'
        return 'relatively_stable'

    def _get_high_spending_months(self, monthly_data: List[float]) -> List[str]:
        """Get months with high spending"""
        avg = mean(monthly_data)
        threshold = avg * 1.2

        high_months = []
        today = datetime.now()

        for i, value in enumerate(monthly_data):
            if value > threshold:
                target_date = today - timedelta(days=30 * (len(monthly_data) - i))
                high_months.append(target_date.strftime('%B'))

        return high_months

    def _get_low_spending_months(self, monthly_data: List[float]) -> List[str]:
        """Get months with low spending"""
        avg = mean(monthly_data)
        threshold = avg * 0.8

        low_months = []
        today = datetime.now()

        for i, value in enumerate(monthly_data):
            if value < threshold:
                target_date = today - timedelta(days=30 * (len(monthly_data) - i))
                low_months.append(target_date.strftime('%B'))

        return low_months

    def _get_seasonal_recommendation(self, pattern: str) -> str:
        """Get seasonal recommendation"""
        if pattern == 'seasonal_variations_detected':
            return 'Consider adjusting your budget for high-spending seasons'
        return 'Your spending is relatively stable throughout the year'

    def _get_next_month(self) -> str:
        """Get next month in YYYY-MM format"""
        today = datetime.now()
        if today.month == 12:
            next_month = datetime(today.year + 1, 1, 1)
        else:
            next_month = datetime(today.year, today.month + 1, 1)
        return next_month.strftime('%Y-%m')

    def _get_last_month_key(self) -> str:
        """Get last month key"""
        today = datetime.now()
        last_month = today - timedelta(days=30)
        return last_month.strftime('%Y-%m')

    def _get_month_expenses(self, expenses: Dict, month_key: str) -> Dict:
        """Get expenses for a specific month"""
        month_expenses = {}
        for exp_id, exp_data in expenses.items():
            try:
                exp_date = datetime.fromisoformat(exp_data.get('date', ''))
                if exp_date.strftime('%Y-%m') == month_key:
                    month_expenses[exp_id] = exp_data
            except:
                continue
        return month_expenses
