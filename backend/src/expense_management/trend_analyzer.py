"""
Monthly Trend Analysis for Expense Management
Analyzes spending trends over multiple months
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from statistics import mean, stdev


class TrendAnalyzer:
    """Analyzes spending trends and patterns"""

    def __init__(self, firebase_service):
        self.firebase_service = firebase_service

    def get_monthly_trend(self, user_id: str, months: int = 6) -> Dict:
        """Get spending trend over last N months"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {'error': 'No expenses found'}

            monthly_data = self._group_expenses_by_month(all_expenses, months)

            trend_data = {}
            for month_key, expenses in monthly_data.items():
                category_totals = self._categorize_expenses(expenses)
                total = sum(category_totals.values())

                trend_data[month_key] = {
                    'total': total,
                    'category_breakdown': category_totals,
                    'expense_count': len(expenses)
                }

            return {
                'user_id': user_id,
                'trend_data': trend_data,
                'months_analyzed': len(trend_data),
                'analysis': self._analyze_trend(trend_data)
            }

        except Exception as e:
            print(f"Error getting monthly trend: {e}")
            return {'error': str(e)}

    def get_category_trend(self, user_id: str, category: str, months: int = 6) -> Dict:
        """Get spending trend for a specific category"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {'error': 'No expenses found'}

            monthly_data = self._group_expenses_by_month(all_expenses, months)

            category_trend = {}
            for month_key, expenses in monthly_data.items():
                category_total = sum(
                    float(exp.get('amount', 0))
                    for exp in expenses.values()
                    if exp.get('category', '').lower() == category.lower()
                )
                category_trend[month_key] = category_total

            return {
                'user_id': user_id,
                'category': category,
                'trend_data': category_trend,
                'analysis': self._analyze_category_trend(category_trend)
            }

        except Exception as e:
            print(f"Error getting category trend: {e}")
            return {'error': str(e)}

    def compare_months(self, user_id: str, month1: str, month2: str) -> Dict:
        """Compare spending between two months (format: 'YYYY-MM')"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {'error': 'No expenses found'}

            expenses1 = self._get_month_expenses(all_expenses, month1)
            expenses2 = self._get_month_expenses(all_expenses, month2)

            data1 = self._get_month_summary(expenses1)
            data2 = self._get_month_summary(expenses2)

            comparison = {
                'month1': month1,
                'month2': month2,
                'data1': data1,
                'data2': data2,
                'comparison': {
                    'total_difference': data2['total'] - data1['total'],
                    'percentage_change': ((data2['total'] - data1['total']) / data1['total'] * 100) if data1['total'] > 0 else 0,
                    'category_changes': self._compare_categories(data1['category_breakdown'], data2['category_breakdown'])
                }
            }

            return comparison

        except Exception as e:
            print(f"Error comparing months: {e}")
            return {'error': str(e)}

    def get_spending_velocity(self, user_id: str) -> Dict:
        """Calculate spending velocity (avg spending per day)"""
        try:
            ref = self.firebase_service.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {'error': 'No expenses found'}

            # Get current month expenses
            current_month_expenses = self._get_current_month_expenses(all_expenses)

            if not current_month_expenses:
                return {'velocity': 0, 'warning': 'No expenses in current month'}

            # Calculate days elapsed in current month
            today = datetime.now()
            days_elapsed = today.day

            total_spent = sum(
                float(exp.get('amount', 0))
                for exp in current_month_expenses.values()
            )

            daily_average = total_spent / days_elapsed

            # Estimate month-end total
            days_in_month = self._get_days_in_current_month()
            estimated_total = daily_average * days_in_month

            return {
                'current_month': today.strftime('%Y-%m'),
                'days_elapsed': days_elapsed,
                'days_in_month': days_in_month,
                'total_spent_so_far': total_spent,
                'daily_average': daily_average,
                'estimated_month_total': estimated_total,
                'pace': 'on track' if estimated_total <= total_spent else 'under budget'
            }

        except Exception as e:
            print(f"Error calculating spending velocity: {e}")
            return {'error': str(e)}

    def _group_expenses_by_month(self, expenses: Dict, months: int) -> Dict:
        """Group expenses by month"""
        today = datetime.now()
        monthly_data = {}

        for i in range(months):
            # Go back N months
            target_date = today - timedelta(days=30 * i)
            month_key = target_date.strftime('%Y-%m')

            month_expenses = self._get_month_expenses(expenses, month_key)
            if month_expenses:
                monthly_data[month_key] = month_expenses

        return dict(sorted(monthly_data.items()))

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

    def _get_current_month_expenses(self, expenses: Dict) -> Dict:
        """Get expenses from current month"""
        today = datetime.now()
        month_key = today.strftime('%Y-%m')
        return self._get_month_expenses(expenses, month_key)

    def _get_month_summary(self, expenses: Dict) -> Dict:
        """Get summary for a month of expenses"""
        category_breakdown = self._categorize_expenses(expenses)
        total = sum(category_breakdown.values())

        return {
            'total': total,
            'category_breakdown': category_breakdown,
            'expense_count': len(expenses)
        }

    def _categorize_expenses(self, expenses: Dict) -> Dict[str, float]:
        """Categorize expenses"""
        categories = {}
        for expense_data in expenses.values():
            category = expense_data.get('category', 'others').lower()
            amount = float(expense_data.get('amount', 0))
            categories[category] = categories.get(category, 0) + amount
        return categories

    def _compare_categories(self, cat1: Dict, cat2: Dict) -> Dict:
        """Compare categories between two periods"""
        comparison = {}
        all_categories = set(list(cat1.keys()) + list(cat2.keys()))

        for category in all_categories:
            val1 = cat1.get(category, 0)
            val2 = cat2.get(category, 0)
            difference = val2 - val1
            pct_change = (difference / val1 * 100) if val1 > 0 else 0

            comparison[category] = {
                'previous': val1,
                'current': val2,
                'difference': difference,
                'percentage_change': pct_change
            }

        return comparison

    def _analyze_trend(self, trend_data: Dict) -> Dict:
        """Analyze overall trend"""
        totals = [data['total'] for data in trend_data.values()]

        if len(totals) < 2:
            return {'warning': 'Insufficient data for trend analysis'}

        avg = mean(totals)
        trend = 'increasing' if totals[-1] > avg else 'decreasing'

        return {
            'average': avg,
            'min': min(totals),
            'max': max(totals),
            'current': totals[-1],
            'trend': trend,
            'volatility': stdev(totals) if len(totals) > 1 else 0
        }

    def _analyze_category_trend(self, category_trend: Dict) -> Dict:
        """Analyze category trend"""
        values = list(category_trend.values())

        if len(values) < 2:
            return {'warning': 'Insufficient data'}

        avg = mean(values)
        trend = 'increasing' if values[-1] > avg else 'decreasing'

        return {
            'average': avg,
            'current': values[-1],
            'trend': trend,
            'consistency': 'stable' if stdev(values) < avg * 0.2 else 'volatile'
        }

    def _get_days_in_current_month(self) -> int:
        """Get number of days in current month"""
        today = datetime.now()
        if today.month == 12:
            next_month = datetime(today.year + 1, 1, 1)
        else:
            next_month = datetime(today.year, today.month + 1, 1)
        return (next_month - datetime(today.year, today.month, 1)).days
