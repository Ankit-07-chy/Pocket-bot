from typing import Dict, List
from datetime import datetime


class ExpenseAnalyzer:
    CATEGORIES = ['food', 'transport', 'entertainment', 'education', 'health', 'utilities', 'others']

    def __init__(self):
        self.categories = self.CATEGORIES

    def categorize_expenses(self, expenses: Dict) -> Dict[str, float]:
        """Categorize expenses and calculate total by category"""
        category_totals = {category: 0.0 for category in self.categories}

        for expense_id, expense_data in expenses.items():
            category = expense_data.get('category', 'others').lower()
            if category not in category_totals:
                category = 'others'

            amount = float(expense_data.get('amount', 0))
            category_totals[category] += amount

        return category_totals

    def get_category_percentages(self, category_totals: Dict[str, float]) -> Dict[str, float]:
        """Calculate percentage of spending per category"""
        total = sum(category_totals.values())

        if total == 0:
            return {category: 0.0 for category in self.categories}

        percentages = {}
        for category, amount in category_totals.items():
            percentages[category] = (amount / total) * 100

        return percentages

    def analyze_previous_month(self, expenses: Dict) -> Dict:
        """Analyze previous month expenses"""
        category_totals = self.categorize_expenses(expenses)
        category_percentages = self.get_category_percentages(category_totals)
        total_spent = sum(category_totals.values())

        return {
            'category_totals': category_totals,
            'category_percentages': category_percentages,
            'total_spent': total_spent,
            'expense_count': len(expenses)
        }

    def get_average_spending_per_category(self, expenses: Dict) -> Dict[str, float]:
        """Calculate average spending per category"""
        category_totals = self.categorize_expenses(expenses)
        category_counts = {category: 0 for category in self.categories}

        for expense_id, expense_data in expenses.items():
            category = expense_data.get('category', 'others').lower()
            if category not in category_counts:
                category = 'others'
            category_counts[category] += 1

        averages = {}
        for category in self.categories:
            if category_counts[category] > 0:
                averages[category] = category_totals[category] / category_counts[category]
            else:
                averages[category] = 0.0

        return averages
