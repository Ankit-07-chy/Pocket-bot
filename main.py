"""
Entry point for Poket Bot Expense Management System
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("Poket Bot - Expense Management System")
    print("=" * 60)

    try:
        # Change to backend directory
        os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

        # Run FastAPI with uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
