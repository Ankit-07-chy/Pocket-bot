"""
Pytest configuration and fixtures for Poket Bot
"""

import sys
import os
from pathlib import Path

# Add src to Python path for proper module discovery
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / 'src'))

import pytest


@pytest.fixture
def mock_expenses():
    """Fixture providing mock expense data"""
    from datetime import datetime, timedelta

    return {
        "exp_001": {
            "date": (datetime.now().replace(day=1) - timedelta(days=15)).isoformat(),
            "category": "food",
            "amount": 500,
            "description": "Groceries"
        },
        "exp_002": {
            "date": (datetime.now().replace(day=1) - timedelta(days=14)).isoformat(),
            "category": "food",
            "amount": 800,
            "description": "Restaurant"
        },
        "exp_003": {
            "date": (datetime.now().replace(day=1) - timedelta(days=12)).isoformat(),
            "category": "transport",
            "amount": 500,
            "description": "Fuel"
        },
        "exp_004": {
            "date": (datetime.now().replace(day=1) - timedelta(days=10)).isoformat(),
            "category": "entertainment",
            "amount": 1000,
            "description": "Movie tickets"
        },
        "exp_005": {
            "date": (datetime.now().replace(day=1) - timedelta(days=8)).isoformat(),
            "category": "utilities",
            "amount": 2000,
            "description": "Electricity bill"
        },
        "exp_006": {
            "date": (datetime.now().replace(day=1) - timedelta(days=5)).isoformat(),
            "category": "health",
            "amount": 1500,
            "description": "Gym membership"
        },
        "exp_007": {
            "date": (datetime.now().replace(day=1) - timedelta(days=3)).isoformat(),
            "category": "education",
            "amount": 5000,
            "description": "Course fees"
        },
    }


@pytest.fixture
def current_month_expenses():
    """Fixture providing current month expenses"""
    from datetime import datetime, timedelta

    return {
        "exp_008": {
            "date": datetime.now().isoformat(),
            "category": "food",
            "amount": 300,
            "description": "Lunch"
        },
        "exp_009": {
            "date": (datetime.now() - timedelta(days=1)).isoformat(),
            "category": "transport",
            "amount": 100,
            "description": "Bus fare"
        }
    }


@pytest.fixture
def expense_analyzer():
    """Fixture providing ExpenseAnalyzer instance"""
    from src.expense_management.expense_analyzer import ExpenseAnalyzer
    return ExpenseAnalyzer()


@pytest.fixture
def budget_planner(expense_analyzer):
    """Fixture providing BudgetPlanner instance"""
    from src.expense_management.budget_planner import BudgetPlanner
    return BudgetPlanner(expense_analyzer)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
