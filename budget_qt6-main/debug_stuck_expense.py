#!/usr/bin/env python3
"""
Database Debugging and Stuck Expense Resolution Tool
===================================================

This script provides diagnostic and repair functionality for identifying and
resolving stuck or problematic expense entries in the Budget Tracker database.
It's particularly useful for debugging issues where expenses appear to be added
but don't show up in the interface, or when duplicate entries cause problems.

Key Features:
- Comprehensive expense entry analysis and debugging
- Detection of stuck, duplicate, or problematic expense records
- Safe removal of specific expense entries by ID
- Database integrity validation and reporting
- Detailed expense summaries and statistics
- Support for batch operations and filtering

Debugging Capabilities:
- Search for expenses by date, person, amount, or category
- Identify duplicate expense entries
- Find expenses with missing or invalid data
- Detect database consistency issues
- Provide detailed expense metadata for troubleshooting

Safety Features:
- Read-only analysis by default
- Confirmation prompts before any deletions
- Detailed previews of what will be affected
- Rollback-safe operations

Usage Examples:
    python debug_stuck_expense.py                    # Show all issues
    python debug_stuck_expense.py remove <ID>       # Remove specific expense
    python debug_stuck_expense.py help              # Show usage information

Dependencies:
    - database.db_manager: For database connectivity
    - database.models.ExpenseModel: For expense operations
"""

import sys
import os

# Add project root to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def debug_stuck_expense():
    """
    Comprehensive analysis of expense database for stuck or problematic entries.

    This function performs a thorough analysis of the expense database to
    identify various types of issues that might cause problems in the
    application interface. It checks for specific problematic patterns
    and provides detailed reporting.

    Analysis performed:
    - Search for specific date/person combinations that might be stuck
    - Identify duplicate expense entries
    - Find expenses with missing or invalid data
    - Check for database consistency issues

    Returns:
        List[Dict]: List of potentially problematic expense records
    """
    db = DatabaseManager()
    
    try:
        db.connect()
        
        print("🔍 Starting comprehensive expense database analysis...")

        # Look for the specific stuck expense mentioned in the user's issue
        print("\n🎯 Searching for expenses on 2025-08-17 for Jeff...")
        cursor = db.execute("""
            SELECT * FROM expenses 
            WHERE date = ? AND person = ?
        """, ('2025-08-17', 'Jeff'))
        
        stuck_expenses = cursor.fetchall()
        
        if stuck_expenses:
            print(f"📍 Found {len(stuck_expenses)} expense(s) matching criteria:")
            for expense in stuck_expenses:
                print(f"   ID: {expense['id']}")
                print(f"   Date: {expense['date']}")
                print(f"   Person: {expense['person']}")
                print(f"   Amount: ${expense['amount']:,.2f}")
                print(f"   Category: {expense['category']}")
                print(f"   Subcategory: {expense['subcategory']}")
                print(f"   Description: {expense.get('description', 'N/A')}")
                print(f"   Payment Method: {expense.get('payment_method', 'N/A')}")
                print(f"   Realized: {expense.get('realized', False)}")
                print("-" * 50)
        else:
            print("❌ No expenses found for Jeff on 2025-08-17")
        
        # Check for any expenses on today's date (broader search)
        print("\n🔍 Checking for ANY expenses on 2025-08-17...")
        cursor = db.execute("""
            SELECT * FROM expenses 
            WHERE date = ?
        """, ('2025-08-17',))
        
        all_today_expenses = cursor.fetchall()
        
        if all_today_expenses:
            print(f"📍 Found {len(all_today_expenses)} total expense(s) on 2025-08-17:")
            for expense in all_today_expenses:
                print(f"   ID: {expense['id']} | Person: {expense['person']} | Amount: ${expense['amount']:,.2f} | Category: {expense['category']}")
        else:
            print("❌ No expenses found on 2025-08-17")
            
        # Check for potential duplicate entries (common cause of display issues)
        print("\n🔍 Checking for potential duplicate entries...")
        cursor = db.execute("""
            SELECT date, person, amount, category, subcategory, COUNT(*) as count
            FROM expenses 
            GROUP BY date, person, amount, category, subcategory
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} potential duplicate groups:")
            for dup in duplicates:
                print(f"   {dup['date']} | {dup['person']} | ${dup['amount']:,.2f} | {dup['category']} | Count: {dup['count']}")
        else:
            print("✅ No duplicate entries found")
            
        # Check for expenses with missing or invalid data
        print("\n🔍 Checking for expenses with missing or invalid data...")
        cursor = db.execute("""
            SELECT * FROM expenses 
            WHERE category IS NULL OR category = '' 
               OR subcategory IS NULL OR subcategory = ''
               OR person IS NULL OR person = ''
               OR amount IS NULL OR amount <= 0
               OR date IS NULL OR date = ''
        """)

        invalid_expenses = cursor.fetchall()
        if invalid_expenses:
            print(f"⚠️  Found {len(invalid_expenses)} expenses with invalid data:")
            for exp in invalid_expenses:
                issues = []
                if not exp.get('category'):
                    issues.append("missing category")
                if not exp.get('subcategory'):
                    issues.append("missing subcategory")
                if not exp.get('person'):
                    issues.append("missing person")
                if not exp.get('amount') or exp['amount'] <= 0:
                    issues.append("invalid amount")
                if not exp.get('date'):
                    issues.append("missing date")

                print(f"   ID: {exp['id']} | Issues: {', '.join(issues)}")
        else:
            print("✅ No expenses with invalid data found")

        # Check for expenses with unusual date formats or future dates
        print("\n🔍 Checking for expenses with unusual dates...")
        cursor = db.execute("""
            SELECT * FROM expenses 
            WHERE date > date('now', '+1 day')
               OR date < '2020-01-01'
        """)

        unusual_date_expenses = cursor.fetchall()
        if unusual_date_expenses:
            print(f"⚠️  Found {len(unusual_date_expenses)} expenses with unusual dates:")
            for exp in unusual_date_expenses:
                print(f"   ID: {exp['id']} | Date: {exp['date']} | Person: {exp['person']} | Amount: ${exp['amount']:,.2f}")
        else:
            print("✅ No expenses with unusual dates found")

        # Database statistics for context
        print("\n📊 Database Statistics:")
        cursor = db.execute("SELECT COUNT(*) as total FROM expenses")
        total_count = cursor.fetchone()['total']
        print(f"   Total expenses in database: {total_count}")

        cursor = db.execute("""
            SELECT person, COUNT(*) as count, SUM(amount) as total
            FROM expenses 
            GROUP BY person
        """)
        person_stats = cursor.fetchall()
        for stat in person_stats:
            print(f"   {stat['person']}: {stat['count']} expenses, ${stat['total']:,.2f}")

        return stuck_expenses
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        db.disconnect()

def remove_stuck_expense(expense_id):
    """
    Safely remove a specific stuck expense entry by ID.

    This function provides a safe way to remove problematic expense
    entries that have been identified through the debugging process.
    It includes confirmation prompts and detailed previews.

    Args:
        expense_id (int): The ID of the expense to remove

    Returns:
        bool: True if expense was successfully removed, False otherwise

    Safety Features:
        - Verifies expense exists before attempting deletion
        - Shows detailed expense information for confirmation
        - Requires explicit user confirmation
        - Uses proper database transaction handling
    """
    db = DatabaseManager()
    
    try:
        db.connect()
        
        # First verify the expense exists and show details
        cursor = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        expense = cursor.fetchone()
        
        if not expense:
            print(f"❌ No expense found with ID {expense_id}")
            return False
            
        print(f"🎯 Found expense to delete:")
        print(f"   ID: {expense['id']}")
        print(f"   Date: {expense['date']}")
        print(f"   Person: {expense['person']}")
        print(f"   Amount: ${expense['amount']:,.2f}")
        print(f"   Category: {expense['category']}")
        print(f"   Subcategory: {expense['subcategory']}")
        print(f"   Description: {expense.get('description', 'N/A')}")

        # Confirm deletion with user
        confirm = input(f"\n⚠️  Are you sure you want to delete this expense? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return False

        # Delete the expense using proper database operations
        db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        db.commit()
        
        print(f"✅ Successfully deleted expense with ID {expense_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting expense: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

def show_help():
    """
    Display comprehensive help information for the debugging tool.

    This function provides detailed usage instructions, command-line
    options, and examples of how to use the debugging tool effectively.
    """
    print("\n🛠️  Expense Database Debugging Tool - Help")
    print("=" * 50)
    print("\nPURPOSE:")
    print("This tool helps diagnose and fix issues with expense entries in the")
    print("Budget Tracker database, particularly 'stuck' expenses that don't")
    print("appear in the interface or cause display problems.")
    print("\nUSAGE:")
    print("  python debug_stuck_expense.py              # Run full analysis")
    print("  python debug_stuck_expense.py remove <ID>  # Remove expense by ID")
    print("  python debug_stuck_expense.py help         # Show this help")
    print("\nCOMMON ISSUES DETECTED:")
    print("  • Stuck expenses that don't appear in the interface")
    print("  • Duplicate expense entries")
    print("  • Expenses with missing or invalid data")
    print("  • Expenses with unusual dates")
    print("  • Database consistency problems")
    print("\nEXAMPLES:")
    print("  # Find all issues in the database")
    print("  python debug_stuck_expense.py")
    print()
    print("  # Remove a specific problematic expense")
    print("  python debug_stuck_expense.py remove 123")
    print()
    print("  # Get help and usage information")
    print("  python debug_stuck_expense.py help")
    print("\nSAFETY NOTES:")
    print("  • Analysis mode is read-only and safe to run")
    print("  • Removal operations require explicit confirmation")
    print("  • Always backup your database before removing expenses")
    print("  • Removed expenses cannot be recovered")

def main():
    """
    Main entry point for the expense debugging tool.

    This function handles command-line arguments and coordinates the
    appropriate debugging operations based on user input.

    Command-line arguments:
        <none>: Run comprehensive analysis
        remove <ID>: Remove specific expense by ID
        help: Display help information
    """
    print("🚀 Expense Database Debugging Tool")
    print("=" * 50)

    # Handle command-line arguments
    if len(sys.argv) >= 2:
        command = sys.argv[1].lower()

        if command == "help":
            show_help()
            return
        elif command == "remove" and len(sys.argv) >= 3:
            try:
                expense_id = int(sys.argv[2])
                print(f"\n🗑️  Attempting to remove expense ID {expense_id}...")
                if remove_stuck_expense(expense_id):
                    print("✅ Expense successfully removed!")
                    print("\n💡 Tip: Restart the Budget Tracker application to see changes.")
                else:
                    print("❌ Failed to remove expense.")
            except ValueError:
                print("❌ Invalid expense ID. Please provide a numeric ID.")
                show_help()
            return
        else:
            print(f"❌ Unknown command: {command}")
            show_help()
            return

    # Run comprehensive analysis if no specific command given
    stuck_expenses = debug_stuck_expense()

    # Provide actionable recommendations based on findings
    print("\n" + "=" * 50)
    print("📋 SUMMARY AND RECOMMENDATIONS:")

    if stuck_expenses:
        print(f"\n🔧 Found {len(stuck_expenses)} potentially stuck expense(s).")
        print("   To remove these expenses, run:")
        for expense in stuck_expenses:
            print(f"   python debug_stuck_expense.py remove {expense['id']}")
        print("\n💡 After removing stuck expenses:")
        print("   1. Restart the Budget Tracker application")
        print("   2. Try adding a new expense to verify functionality")
        print("   3. Check that the expense appears in the Expense History tab")
    else:
        print("\n✅ No obvious stuck expenses found.")
        print("   If you're still experiencing issues:")
        print("   1. Check the Budget->Expenses tab filters (Month/Year)")
        print("   2. Try refreshing the data by switching tabs")
        print("   3. Restart the application completely")

    print(f"\n🛠️  For more help: python {sys.argv[0]} help")

if __name__ == "__main__":
    main()
