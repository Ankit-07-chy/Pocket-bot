import firebase_admin # used for initializing Firebase app
from firebase_admin import db, credentials # used for database operations and credentials management
from datetime import datetime, timedelta # used for date calculations
from typing import Dict, List, Optional # used for type hinting


class FirebaseExpenseService:
    def __init__(self):
        self.db = db

    def get_user_expenses(self, user_id: str) -> Dict:
        """Fetch all expenses for a user from Firebase"""
        try:
            ref = self.db.reference(f'users/{user_id}/expenses')
            expenses = ref.get()
            return expenses if expenses else {}
        except Exception as e:
            print(f"Error fetching user expenses: {e}")
            return {}

    def get_previous_month_expenses(self, user_id: str) -> Dict:
        """Fetch previous month expenses for a user"""
        try:
            today = datetime.now()
            first_day_current = today.replace(day=1)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = last_day_previous.replace(day=1)

            ref = self.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {}

            previous_month_expenses = {}
            for expense_id, expense_data in all_expenses.items():
                expense_date = datetime.fromisoformat(expense_data.get('date', ''))
                if first_day_previous <= expense_date <= last_day_previous:
                    previous_month_expenses[expense_id] = expense_data

            return previous_month_expenses
        except Exception as e:
            print(f"Error fetching previous month expenses: {e}")
            return {}

    def get_current_month_expenses(self, user_id: str) -> Dict:
        """Fetch current month expenses for a user"""
        try:
            today = datetime.now()
            first_day_current = today.replace(day=1)

            ref = self.db.reference(f'users/{user_id}/expenses')
            all_expenses = ref.get()

            if not all_expenses:
                return {}

            current_month_expenses = {}
            for expense_id, expense_data in all_expenses.items():
                expense_date = datetime.fromisoformat(expense_data.get('date', ''))
                if expense_date >= first_day_current:
                    current_month_expenses[expense_id] = expense_data

            return current_month_expenses
        except Exception as e:
            print(f"Error fetching current month expenses: {e}")
            return {}

    def save_budget_plan(self, user_id: str, budget_plan: Dict) -> bool:
        """Save the generated budget plan to Firebase"""
        try:
            ref = self.db.reference(f'users/{user_id}/budget_plan')
            ref.set({
                'plan': budget_plan,
                'created_date': datetime.now().isoformat(),
                'month': datetime.now().strftime('%Y-%m')
            })
            return True
        except Exception as e:
            print(f"Error saving budget plan: {e}")
            return False
