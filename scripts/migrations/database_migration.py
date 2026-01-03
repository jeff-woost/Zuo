"""
Database Migration Script
========================

This script adds new tables and columns for the 6 major feature enhancements:
1. Bank reconciliation transactions table
2. Expense category history for smart suggestions
3. Status column for savings goals
4. is_default column for budget estimates
5. Category column for net worth assets

Run this script to upgrade the database schema.
"""

import sqlite3
from datetime import datetime

def run_migration(db_path="budget_tracker.db"):
    """Execute database migrations"""
    print("Starting database migration...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Feature 1: Bank Reconciliation - Create bank_transactions table
        print("Creating bank_transactions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                bank_rtn TEXT,
                account_number TEXT,
                transaction_type TEXT NOT NULL,
                description TEXT,
                debit REAL,
                credit REAL,
                check_number TEXT,
                account_balance REAL,
                reconciled BOOLEAN DEFAULT 0,
                imported_to_budget BOOLEAN DEFAULT 0,
                budget_entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, description, debit, credit, account_balance)
            )
        ''')
        print("✓ bank_transactions table created")
        
        # Feature 2: Smart Category Dictionary - Create expense_category_history table
        print("Creating expense_category_history table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_category_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description_pattern TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(description_pattern, category, subcategory)
            )
        ''')
        print("✓ expense_category_history table created")
        
        # Feature 4: Persistent Budget Estimates - Add is_default column
        print("Adding is_default column to budget_estimates...")
        try:
            cursor.execute('ALTER TABLE budget_estimates ADD COLUMN is_default BOOLEAN DEFAULT 0')
            print("✓ is_default column added to budget_estimates")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ is_default column already exists in budget_estimates")
            else:
                raise
        
        # Feature 5: Enhanced Savings Goals - Add status column
        print("Adding status column to savings_goals...")
        try:
            cursor.execute("ALTER TABLE savings_goals ADD COLUMN status TEXT DEFAULT 'active'")
            print("✓ status column added to savings_goals")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ status column already exists in savings_goals")
            else:
                raise
        
        # Feature 6: Improved Net Worth - Add category column to net_worth_assets
        print("Adding category column to net_worth_assets...")
        try:
            cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN category TEXT')
            print("✓ category column added to net_worth_assets")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ category column already exists in net_worth_assets")
            else:
                raise
        
        # Add comment column to bank_transactions for reconciliation notes
        print("Adding comment column to bank_transactions...")
        try:
            cursor.execute('ALTER TABLE bank_transactions ADD COLUMN comment TEXT')
            print("✓ comment column added to bank_transactions")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ comment column already exists in bank_transactions")
            else:
                raise

        # Add last_updated column to net_worth_assets for tracking
        print("Adding last_updated column to net_worth_assets...")
        try:
            cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN last_updated TIMESTAMP')
            print("✓ last_updated column added to net_worth_assets")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("⚠ last_updated column already exists in net_worth_assets")
            else:
                raise
        
        # Commit all changes
        conn.commit()
        print("\n✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
