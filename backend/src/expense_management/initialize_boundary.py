from .firebase_service import FirebaseExpenseService
from .expense_analyzer import ExpenseAnalyzer
from .budget_planner import BudgetPlanner
from .config import EXPENSE_CATEGORIES
from typing import Dict, Optional
from datetime import datetime, timedelta


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

    def onboard_user_with_expense_data(
        self,
        user_id: str,
        last_month_total: float,
        last_month_category_expenses: Dict[str, float],
        this_month_budget: float,
        savings_target: float = 0.0,
    ) -> Dict:
        """
        First-time onboarding when the user manually provides their
        last month's expense data at registration.

        This is the primary entry point called right after a user signs up.
        It:
          1. Persists synthetic "last month" expense rows to SQLite so
             all analytics modules have real data to work with.
          2. Builds a category-wise budget plan for the current month
             based on the user-supplied breakdown.
          3. Saves the plan to SQLite.

        Args:
            user_id: User ID (string — will be cast to int if numeric)
            last_month_total: Total amount the user spent last month
            last_month_category_expenses: Dict of {category: amount}
            this_month_budget: Total budget for the current month
            savings_target: Optional fixed savings amount (default 0 = auto 10%)

        Returns:
            Dict with budget_plan and summary fields
        """
        try:
            uid = int(user_id) if str(user_id).isdigit() else user_id

            # ── Step 1: Persist last-month expenses to SQLite ──────────────
            # We store one synthetic row per category so forecaster/trend
            # analyzer can use real category-level history from day one.
            last_month_date = (
                datetime.now().replace(day=1) - timedelta(days=1)
            ).strftime("%Y-%m-%d")

            valid_categories = set(EXPENSE_CATEGORIES)
            for category, amount in last_month_category_expenses.items():
                cat = category.lower()
                if cat not in valid_categories:
                    cat = "others"
                if amount > 0:
                    self.firebase_service.add_expense(
                        user_id=str(uid),
                        amount=float(amount),
                        category=cat,
                        description=f"[onboarding] last month {cat}",
                        date=last_month_date,
                    )

            # ── Step 2: Build previous-month analysis from supplied data ───
            # Normalise to what ExpenseAnalyzer.analyze_previous_month returns
            # so BudgetPlanner works without touching the DB again.
            category_totals = {c: 0.0 for c in EXPENSE_CATEGORIES}
            for cat, amt in last_month_category_expenses.items():
                key = cat.lower() if cat.lower() in category_totals else "others"
                category_totals[key] += float(amt)

            total_spent = sum(category_totals.values())
            # Guard: if totals don't match last_month_total, normalise
            if total_spent > 0 and abs(total_spent - last_month_total) > 1:
                scale = last_month_total / total_spent
                category_totals = {k: round(v * scale, 2) for k, v in category_totals.items()}
                total_spent = last_month_total

            category_percentages = {
                cat: round((amt / total_spent * 100), 2) if total_spent > 0 else 0.0
                for cat, amt in category_totals.items()
            }

            previous_month_analysis = {
                "category_totals": category_totals,
                "category_percentages": category_percentages,
                "total_spent": total_spent,
                "expense_count": len(
                    [v for v in last_month_category_expenses.values() if v > 0]
                ),
            }

            # ── Step 3: Create optimized budget plan ───────────────────────
            budget_plan = self.budget_planner.create_optimized_plan(
                previous_month_analysis=previous_month_analysis,
                current_month_total=this_month_budget,
                savings_target=savings_target,
            )

            # ── Step 4: Save plan to SQLite ────────────────────────────────
            self.firebase_service.save_budget_plan(str(uid), budget_plan)

            return {
                "user_id": user_id,
                "success": True,
                "budget_plan": budget_plan,
                "summary": {
                    "last_month_total": last_month_total,
                    "this_month_budget": this_month_budget,
                    "savings_allocated": budget_plan.get("savings", 0),
                    "spending_budget": budget_plan.get("spending_budget", this_month_budget),
                    "top_category": max(
                        category_totals, key=lambda c: category_totals[c]
                    ) if category_totals else None,
                    "category_budget_breakdown": budget_plan.get("budget_breakdown", {}),
                },
            }

        except Exception as e:
            print(f"Error in onboard_user_with_expense_data: {e}")
            return {"user_id": user_id, "success": False, "error": str(e)}
