from typing import Dict


class BudgetPlanner:
    """Creates budget breakdown plans based on historical spending patterns"""

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def create_monthly_plan(self,
                           previous_month_analysis: Dict,
                           current_month_total: float,
                           adjustment_factor: float = 1.0) -> Dict:
        """
        Create a budget breakdown for current month based on previous month patterns.

        Args:
            previous_month_analysis: Analysis of previous month's spending
            current_month_total: Total budget available for current month
            adjustment_factor: Multiplier to adjust budget up/down (e.g., 1.1 = 10% increase)

        Returns:
            Budget breakdown plan by category
        """
        category_percentages = previous_month_analysis['category_percentages']
        previous_total = previous_month_analysis['total_spent']

        # Calculate budget allocation based on previous spending patterns
        budget_plan = {}
        total_allocated = 0

        for category, percentage in category_percentages.items():
            allocated = (percentage / 100) * current_month_total
            adjusted_allocated = allocated * adjustment_factor
            budget_plan[category] = round(adjusted_allocated, 2)
            total_allocated += adjusted_allocated

        # If adjustments caused overspending, normalize proportionally
        if total_allocated > current_month_total:
            scale_factor = current_month_total / total_allocated
            for category in budget_plan:
                budget_plan[category] = round(budget_plan[category] * scale_factor, 2)

        return {
            'budget_breakdown': budget_plan,
            'total_budget': current_month_total,
            'previous_month_total': previous_total,
            'recommendation': self._get_recommendation(category_percentages, previous_total)
        }

    def create_optimized_plan(self,
                             previous_month_analysis: Dict,
                             current_month_total: float,
                             savings_target: float = 0) -> Dict:
        """
        Create an optimized budget plan that includes savings target.

        Args:
            previous_month_analysis: Analysis of previous month
            current_month_total: Total budget for current month
            savings_target: Amount to save (0 means proportional savings)

        Returns:
            Optimized budget breakdown with savings allocation
        """
        category_percentages = previous_month_analysis['category_percentages']
        previous_total = previous_month_analysis['total_spent']

        # Calculate spending amount after savings
        if savings_target > 0:
            spending_budget = current_month_total - savings_target
            savings_amount = savings_target
        else:
            # Default: save 10% of budget
            savings_amount = current_month_total * 0.1
            spending_budget = current_month_total - savings_amount

        # Allocate remaining budget based on previous patterns
        budget_plan = {}
        for category, percentage in category_percentages.items():
            allocated = (percentage / 100) * spending_budget
            budget_plan[category] = round(allocated, 2)

        return {
            'budget_breakdown': budget_plan,
            'savings': round(savings_amount, 2),
            'total_budget': current_month_total,
            'spending_budget': round(spending_budget, 2),
            'previous_month_total': previous_total,
            'previous_month_percentages': category_percentages,
            'recommendation': self._get_recommendation(category_percentages, previous_total)
        }

    def _get_recommendation(self, category_percentages: Dict, previous_total: float) -> str:
        """Generate budget recommendation based on spending patterns"""
        recommendations = []

        # Check for high spending categories
        for category, percentage in category_percentages.items():
            if percentage > 30:
                recommendations.append(f"High spending in {category} ({percentage:.1f}%). Consider reducing.")
            elif percentage > 50:
                recommendations.append(f"Very high spending in {category} ({percentage:.1f}%). Urgent reduction needed.")

        if not recommendations:
            recommendations.append("Your spending is well balanced. Maintain current habits.")

        return " ".join(recommendations)

    def compare_with_target(self,
                           budget_plan: Dict,
                           target_budget: float) -> Dict:
        """Compare current plan with a target budget"""
        total_allocated = sum(budget_plan['budget_breakdown'].values())
        difference = target_budget - total_allocated

        return {
            'planned_spending': total_allocated,
            'target_budget': target_budget,
            'difference': round(difference, 2),
            'status': 'within budget' if difference >= 0 else 'exceeds budget',
            'variance_percentage': round((difference / target_budget) * 100, 2) if target_budget > 0 else 0
        }
