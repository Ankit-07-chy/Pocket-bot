"""
firebase_service.py — backward-compatible shim.

All data is now stored in SQLite (pocketbuddy.db).
FirebaseExpenseService is an alias for SQLiteExpenseService so every
existing import continues to work unchanged.
"""

from .sqlite_service import SQLiteExpenseService

# Keep the original class name so no other file needs to change its import.
FirebaseExpenseService = SQLiteExpenseService

__all__ = ["FirebaseExpenseService"]
