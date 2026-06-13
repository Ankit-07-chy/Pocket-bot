from .firebase_service import FirebaseExpenseService
from .expense_analyzer import ExpenseAnalyzer
from .budget_planner import BudgetPlanner
from typing import Dict, Optional


class ExpenseInitializer:
    """Handles expense management initialization for users"""

    def __init__(self):
        self.firebase_service = FirebaseExpenseService()
        self.analyzer = ExpenseAnalyzer()
        self.budget_planner = BudgetPlanner(self.analyzer)

    def initialize_user_expenses(self,
                                 user_id: str,
                                 current_month_budget: float = None) -> Dict:
        """
        Initialize expense management for a user.

        Fetches previous month expenses, analyzes spending patterns,
        and creates a budget breakdown plan for the current month.

        Args:
            user_id: User ID to initialize
            current_month_budget: Total budget for current month (optional)

        Returns:
            Complete initialization data with budget plan
        """
        try:
            # Fetch historical data
            previous_month_expenses = self.firebase_service.get_previous_month_expenses(user_id)
            current_month_expenses = self.firebase_service.get_current_month_expenses(user_id)

            # Analyze previous month
            previous_month_analysis = self.analyzer.analyze_previous_month(previous_month_expenses)

            # Get current month total if not provided
            if current_month_budget is None:
                current_month_budget = previous_month_analysis['total_spent']

            # Create budget plan
            budget_plan = self.budget_planner.create_optimized_plan(
                previous_month_analysis=previous_month_analysis,
                current_month_total=current_month_budget,
                savings_target=0  # Default: 10% savings automatically added
            )

            # Calculate current month analysis
            current_month_analysis = self.analyzer.analyze_previous_month(current_month_expenses)

            initialization_data = {
                'user_id': user_id,
                'previous_month': {
                    'total_spent': previous_month_analysis['total_spent'],
                    'category_breakdown': previous_month_analysis['category_totals'],
                    'category_percentages': previous_month_analysis['category_percentages'],
                    'expense_count': previous_month_analysis['expense_count']
                },
                'current_month': {
                    'total_spent_so_far': current_month_analysis['total_spent'],
                    'category_breakdown': current_month_analysis['category_totals'],
                    'expense_count': current_month_analysis['expense_count']
                },
                'budget_plan': budget_plan,
                'success': True
            }

            # Save budget plan to Firebase
            self.firebase_service.save_budget_plan(user_id, budget_plan)

            return initialization_data

        except Exception as e:
            print(f"Error initializing user expenses: {e}")
            return {
                'user_id': user_id,
                'success': False,
                'error': str(e)
            }

    def reinitialize_with_custom_budget(self,
                                        user_id: str,
                                        custom_budget: float,
                                        savings_target: float = 0) -> Dict:
        """
        Reinitialize with a custom budget amount.

        Args:
            user_id: User ID
            custom_budget: Custom budget for current month
            savings_target: Custom savings target amount

        Returns:
            Updated initialization data
        """
        try:
            previous_month_expenses = self.firebase_service.get_previous_month_expenses(user_id)
            previous_month_analysis = self.analyzer.analyze_previous_month(previous_month_expenses)

            budget_plan = self.budget_planner.create_optimized_plan(
                previous_month_analysis=previous_month_analysis,
                current_month_total=custom_budget,
                savings_target=savings_target
            )

            result = {
                'user_id': user_id,
                'custom_budget': custom_budget,
                'budget_plan': budget_plan,
                'success': True
            }

            # Save updated plan
            self.firebase_service.save_budget_plan(user_id, budget_plan)

            return result

        except Exception as e:
            print(f"Error reinitializing with custom budget: {e}")
            return {
                'user_id': user_id,
                'success': False,
                'error': str(e)
            }

    def get_initialization_report(self, user_id: str) -> Dict:
        """Get detailed report of initialization data"""
        return self.initialize_user_expenses(user_id)
