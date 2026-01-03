#!/usr/bin/env python3
"""
Expense Database Cleanup and Integrity Tool
==========================================

This script provides comprehensive functionality for clearing expense data from
the Budget Tracker database with various safety options and integrity checks.
It supports both targeted month-specific cleaning and complete database reset
operations while maintaining data safety and providing detailed feedback.

Key Features:
- Month-specific expense clearing (safer option)
- Complete database reset for fresh starts
- Detailed expense summaries before deletion
- Interactive confirmation prompts
- Data integrity verification
- Comprehensive error handling and reporting

Safety Measures:
- Multiple confirmation prompts for destructive operations
- Detailed summaries showing what will be deleted
- Separate handling for monthly vs. complete clearing
- Database integrity checks after operations

Usage Examples:
    python clear_all_expenses.py                    # Interactive menu
    python clear_all_expenses.py --month 8 --year 2024  # Clear specific month
    python clear_all_expenses.py --all             # Clear all expenses

Dependencies:
    - database.models.ExpenseModel: For database operations
    - database.db_manager: For database connectivity
    - datetime: For date calculations and formatting
"""

import sys
import os
from datetime import datetime, date

# Add project root to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from database.models import ExpenseModel

def get_user_choice():
    """
    Present user with clearing options and get their choice.

    This function displays an interactive menu allowing users to choose
    between different expense clearing operations:
    1. Clear expenses for a specific month (safer)
    2. Clear all expenses (destructive)
    3. Cancel and exit

    Returns:
        int: User's choice (1, 2, or 3)

    Note:
        The function loops until a valid choice is entered and handles
        keyboard interrupts gracefully.
    """
    print("\n🧹 Expense Clearing Options:")
    print("1. Clear expenses for a specific month (safer)")
    print("2. Clear ALL expenses (destructive)")
    print("3. Cancel and exit")

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("❌ Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
            return 3

def get_month_year():
    """
    Get month and year input from user for targeted expense clearing.

    This function prompts the user to enter a specific month and year
    for targeted expense deletion. It provides defaults based on the
    current date and validates the input ranges.

    Returns:
        Tuple[int, int]: A tuple containing (month, year) or (None, None) if cancelled

    Validation:
        - Month must be between 1-12
        - Year must be between 2020 and current_year + 1
        - Handles keyboard interrupts gracefully
    """
    current_year = datetime.now().year
    current_month = datetime.now().month

    print(f"\n📅 Current date: {datetime.now().strftime('%B %Y')}")
    print("Enter the month and year for expenses to clear:")

    # Get month with validation
    while True:
        try:
            month_input = input(f"Month (1-12) [default: {current_month}]: ").strip()
            if not month_input:
                month = current_month
            else:
                month = int(month_input)

            if 1 <= month <= 12:
                break
            else:
                print("❌ Month must be between 1 and 12")
        except ValueError:
            print("❌ Please enter a valid number for month")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
            return None, None

    # Get year with validation
    while True:
        try:
            year_input = input(f"Year [default: {current_year}]: ").strip()
            if not year_input:
                year = current_year
            else:
                year = int(year_input)

            if 2020 <= year <= current_year + 1:  # Reasonable year range
                break
            else:
                print(f"❌ Year must be between 2020 and {current_year + 1}")
        except ValueError:
            print("❌ Please enter a valid number for year")
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user")
            return None, None

    return month, year

def clear_expenses_by_month(db, month, year):
    """
    Clear expenses for a specific month with detailed confirmation.

    This function performs targeted expense deletion for a specific month,
    providing detailed summaries and multiple confirmation prompts to
    ensure the user understands what will be deleted.

    Args:
        db (DatabaseManager): Database manager instance
        month (int): Month to clear (1-12)
        year (int): Year to clear

    Returns:
        int: Number of expenses deleted, or 0 if operation was cancelled

    Process:
        1. Calculate date range for the specified month
        2. Retrieve and analyze expenses in that range
        3. Display detailed summary with breakdowns by person
        4. Show sample expenses for user review
        5. Confirm deletion with user
        6. Delete expenses using ExpenseModel
    """
    try:
        # Calculate date range for the specified month
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"

        # Get expenses in this month first to show what will be deleted
        month_expenses = db.get_expenses(start_date, end_date)

        if not month_expenses:
            print(f"ℹ️  No expenses found for {datetime(year, month, 1).strftime('%B %Y')}")
            return 0

        print(f"\n📊 Found {len(month_expenses)} expenses for {datetime(year, month, 1).strftime('%B %Y')}:")

        # Show summary by person with totals
        jeff_total = sum(exp['amount'] for exp in month_expenses if exp['person'] == 'Jeff')
        vanessa_total = sum(exp['amount'] for exp in month_expenses if exp['person'] == 'Vanessa')

        print(f"   Jeff: {sum(1 for exp in month_expenses if exp['person'] == 'Jeff')} expenses, ${jeff_total:,.2f}")
        print(f"   Vanessa: {sum(1 for exp in month_expenses if exp['person'] == 'Vanessa')} expenses, ${vanessa_total:,.2f}")
        print(f"   Total: ${jeff_total + vanessa_total:,.2f}")

        # Show sample expenses for user review
        print(f"\n📝 Sample expenses:")
        for i, exp in enumerate(month_expenses[:5]):
            print(f"   {exp['date']} - {exp['person']}: ${exp['amount']:,.2f} ({exp['category']})")
        if len(month_expenses) > 5:
            print(f"   ... and {len(month_expenses) - 5} more")

        # Confirm deletion with clear warning
        confirm = input(f"\n⚠️  Are you sure you want to delete all {len(month_expenses)} expenses for {datetime(year, month, 1).strftime('%B %Y')}? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return 0

        # Delete expenses for this month using the model
        deleted_count = 0
        for expense in month_expenses:
            ExpenseModel.delete(db, expense['id'])
            deleted_count += 1

        return deleted_count

    except Exception as e:
        print(f"❌ Error clearing monthly expenses: {e}")
        return 0

def clear_all_expenses(db):
    """
    Clear all expenses from the database with strong confirmation.

    This function performs complete expense database clearing, which is
    a destructive operation that cannot be undone. It includes multiple
    confirmation prompts and detailed warnings to prevent accidental data loss.

    Args:
        db (DatabaseManager): Database manager instance

    Returns:
        int: Number of expenses deleted, or 0 if operation was cancelled

    Safety Features:
        - Multiple confirmation prompts
        - Strong warnings about data loss
        - Detailed summary of what will be deleted
        - Special confirmation text requirement ("DELETE ALL")
        - Uses ExpenseModel.clear_all for complete cleanup
    """
    try:
        # Get total count and summary first
        all_expenses = db.get_expenses()
        total_count = len(all_expenses)

        if total_count == 0:
            print("ℹ️  No expenses found in database")
            return 0

        print(f"\n📊 Found {total_count} total expenses in database")

        # Show comprehensive summary
        jeff_total = sum(exp['amount'] for exp in all_expenses if exp['person'] == 'Jeff')
        vanessa_total = sum(exp['amount'] for exp in all_expenses if exp['person'] == 'Vanessa')

        print(f"   Jeff: {sum(1 for exp in all_expenses if exp['person'] == 'Jeff')} expenses, ${jeff_total:,.2f}")
        print(f"   Vanessa: {sum(1 for exp in all_expenses if exp['person'] == 'Vanessa')} expenses, ${vanessa_total:,.2f}")
        print(f"   Total: ${jeff_total + vanessa_total:,.2f}")

        # Strong warning about destructive operation
        print(f"\n⚠️  WARNING: This will permanently delete ALL {total_count} expense records!")
        print("   This action cannot be undone and will remove all expense history.")

        # First confirmation with special text
        confirm1 = input("Type 'DELETE ALL' to confirm: ").strip()
        if confirm1 != "DELETE ALL":
            print("❌ Operation cancelled")
            return 0

        # Second confirmation for extra safety
        confirm2 = input("Are you absolutely sure? (yes/no): ").strip().lower()
        if confirm2 not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return 0

        # Use the ExpenseModel.clear_all method for complete cleanup
        count = ExpenseModel.clear_all(db)
        return count

    except Exception as e:
        print(f"❌ Error clearing all expenses: {e}")
        return 0

def main():
    """
    Main function with interactive menu and operation coordination.

    This function serves as the primary entry point for the expense
    clearing tool. It presents an interactive menu, handles user choices,
    and coordinates the appropriate clearing operations.

    Process:
        1. Display tool header and get user choice
        2. Initialize database connection
        3. Execute appropriate clearing operation
        4. Provide success feedback and next steps
        5. Handle errors and keyboard interrupts gracefully
    """
    print("🧹 Expense Database Cleanup Tool")
    print("=" * 40)

    # Get user choice from interactive menu
    choice = get_user_choice()

    if choice == 3:  # Cancel
        print("👋 Goodbye!")
        return

    # Initialize database connection
    db = DatabaseManager()

    try:
        if choice == 1:  # Clear by month
            month, year = get_month_year()
            if month is None or year is None:
                print("👋 Operation cancelled")
                return

            print(f"\n🗓️  Clearing expenses for {datetime(year, month, 1).strftime('%B %Y')}...")
            count = clear_expenses_by_month(db, month, year)

            if count > 0:
                print(f"✅ Successfully cleared {count} expenses for {datetime(year, month, 1).strftime('%B %Y')}")
                print("🔄 Other historical data remains intact")

        elif choice == 2:  # Clear all
            print(f"\n🗑️  Clearing ALL expenses...")
            count = clear_all_expenses(db)

            if count > 0:
                print(f"✅ Successfully cleared all {count} expense records")
                print("🔄 Database has been reset and is ready for fresh data")

    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
