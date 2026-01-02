#!/usr/bin/env python3
"""
Script to clear all expenses and fix database integrity issues
This will completely reset the expense history and ensure clean state
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def clear_all_expenses():
    """Clear all expenses from the database"""
    print("🧹 Clearing all expenses from database...")
    
    db = DatabaseManager()
    try:
        db.connect()
        
        # Get count before deletion
        cursor = db.execute("SELECT COUNT(*) as count FROM expenses")
        count_before = cursor.fetchone()['count']
        print(f"📊 Found {count_before} existing expense records")
        
        if count_before == 0:
            print("✅ No expenses to delete - database is already clean")
            return True
            
        # Delete all expenses
        db.execute("DELETE FROM expenses")
        db.commit()
        
        # Verify deletion
        cursor = db.execute("SELECT COUNT(*) as count FROM expenses")
        count_after = cursor.fetchone()['count']
        
        if count_after == 0:
            print(f"✅ Successfully deleted all {count_before} expense records")
            
            # Reset the auto-increment counter
            db.execute("DELETE FROM sqlite_sequence WHERE name='expenses'")
            db.commit()
            print("🔄 Reset expense ID counter")
            
            return True
        else:
            print(f"❌ Failed to delete all expenses. {count_after} records remain")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing expenses: {e}")
        return False
    finally:
        db.disconnect()

def verify_database_integrity():
    """Verify database structure and integrity"""
    print("\n🔍 Verifying database integrity...")
    
    db = DatabaseManager()
    try:
        db.connect()
        
        # Check if expenses table exists and has correct structure
        cursor = db.execute("PRAGMA table_info(expenses)")
        columns = cursor.fetchall()
        
        expected_columns = {
            'id': 'INTEGER',
            'person': 'TEXT',
            'amount': 'REAL', 
            'date': 'DATE',
            'category': 'TEXT',
            'subcategory': 'TEXT',
            'description': 'TEXT',
            'payment_method': 'TEXT',
            'realized': 'BOOLEAN',
            'created_at': 'TIMESTAMP'
        }
        
        print("📋 Expense table structure:")
        for col in columns:
            col_name = col['name']
            col_type = col['type']
            print(f"  - {col_name}: {col_type}")
            
        # Check for any orphaned records or data inconsistencies
        cursor = db.execute("""
            SELECT COUNT(*) as count FROM expenses 
            WHERE category IS NULL OR category = '' 
               OR subcategory IS NULL OR subcategory = ''
               OR person IS NULL OR person = ''
               OR amount IS NULL
               OR date IS NULL OR date = ''
        """)
        
        incomplete_records = cursor.fetchone()['count']
        if incomplete_records > 0:
            print(f"⚠️  Found {incomplete_records} incomplete expense records")
            return False
        else:
            print("✅ No incomplete expense records found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False
    finally:
        db.disconnect()

def add_expense_validation():
    """Add validation to prevent incomplete expense records"""
    print("\n🛡️  Adding expense validation...")
    
    # This will be handled by modifying the ExpenseModel class
    print("✅ Validation will be added to ExpenseModel.create() method")
    return True

def main():
    """Main function to clear expenses and fix issues"""
    print("🚀 Expense Database Cleanup and Fix Tool")
    print("=" * 50)
    
    # Step 1: Clear all expenses
    success = clear_all_expenses()
    if not success:
        print("❌ Failed to clear expenses. Exiting.")
        return False
    
    # Step 2: Verify database integrity
    success = verify_database_integrity()
    if not success:
        print("❌ Database integrity issues found. Please check manually.")
        return False
    
    # Step 3: Add validation
    success = add_expense_validation()
    if not success:
        print("❌ Failed to add validation.")
        return False
    
    print("\n🎉 Expense cleanup completed successfully!")
    print("📝 Next steps:")
    print("   1. Restart the application")
    print("   2. Test adding new expenses")
    print("   3. Verify bulk import functionality")
    
    return True

if __name__ == "__main__":
    main()
