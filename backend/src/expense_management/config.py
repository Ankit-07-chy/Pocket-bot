"""
Configuration for Expense Management System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Firebase Configuration
FIREBASE_CONFIG = {
    'apiKey': os.getenv('FIREBASE_API_KEY'),
    'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
    'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
    'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': os.getenv('FIREBASE_APP_ID'),
    'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
}

# Service Account Key Path (for backend)
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH', './serviceAccountKey.json')

# Expense Categories
EXPENSE_CATEGORIES = [
    'food',
    'transport',
    'entertainment',
    'education',
    'health',
    'utilities',
    'others'
]

# Default Budget Settings
DEFAULT_SAVINGS_PERCENTAGE = 0.10  # 10% savings by default
HIGH_SPENDING_THRESHOLD = 0.30  # 30% = high spending
VERY_HIGH_SPENDING_THRESHOLD = 0.50  # 50% = very high spending

# Budget Plan Settings
ENABLE_AUTOMATIC_SAVINGS = True
ENABLE_RECOMMENDATIONS = True
MONTHLY_REVIEW_DAY = 1  # Day of month for monthly review

# Database Paths
DB_PATHS = {
    'users': 'users',
    'expenses': 'expenses',
    'budget_plans': 'budget_plan',
    'monthly_reviews': 'monthly_reviews'
}

# Validation Rules
EXPENSE_VALIDATION = {
    'min_amount': 0.01,
    'max_amount': 1000000,
    'required_fields': ['date', 'category', 'amount']
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Feature Flags
FEATURES = {
    'ENABLE_ML_PREDICTIONS': os.getenv('ENABLE_ML_PREDICTIONS', 'false').lower() == 'true',
    'ENABLE_ALERTS': os.getenv('ENABLE_ALERTS', 'true').lower() == 'true',
    'ENABLE_MULTI_CURRENCY': os.getenv('ENABLE_MULTI_CURRENCY', 'false').lower() == 'true',
}

# Currency Settings
CURRENCY_SETTINGS = {
    'default_currency': os.getenv('DEFAULT_CURRENCY', 'INR'),
    'currency_symbol': '₹'
}

# Cache Settings
CACHE_CONFIG = {
    'enable_caching': True,
    'cache_ttl_seconds': 3600  # 1 hour
}

# API Rate Limiting
RATE_LIMIT_CONFIG = {
    'requests_per_minute': 60,
    'burst_size': 10
}


def get_config(key: str, default=None):
    """Get configuration value by key"""
    config = {
        'firebase': FIREBASE_CONFIG,
        'categories': EXPENSE_CATEGORIES,
        'default_savings': DEFAULT_SAVINGS_PERCENTAGE,
        'high_spending_threshold': HIGH_SPENDING_THRESHOLD,
        'currency': CURRENCY_SETTINGS['currency_symbol']
    }
    return config.get(key, default)


if __name__ == "__main__":
    print("Expense Management Configuration")
    print("-" * 50)
    print(f"Expense Categories: {', '.join(EXPENSE_CATEGORIES)}")
    print(f"Default Savings: {DEFAULT_SAVINGS_PERCENTAGE * 100}%")
    print(f"High Spending Threshold: {HIGH_SPENDING_THRESHOLD * 100}%")
    print(f"Currency: {CURRENCY_SETTINGS['currency_symbol']}")
