#!/usr/bin/env python3
"""
Fix savings goals database schema and clean up stuck goals
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def fix_savings_goals_database():
    """Fix the savings goals database schema and clean up stuck goals"""
    db = DatabaseManager()
    db.connect()

    print("=== Checking current savings_goals table schema ===")
    cursor = db.execute('PRAGMA table_info(savings_goals)')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"Current columns: {column_names}")

    # Add missing initial_amount column if it doesn't exist
    if 'initial_amount' not in column_names:
        print("Adding missing initial_amount column...")
        try:
            db.execute('ALTER TABLE savings_goals ADD COLUMN initial_amount REAL DEFAULT 0')
            db.commit()
            print("✅ Added initial_amount column")
        except Exception as e:
            print(f"❌ Error adding initial_amount column: {e}")
    else:
        print("✅ initial_amount column already exists")

    # Check for stuck goals
    print("\n=== Current savings_goals records ===")
    cursor = db.execute('SELECT * FROM savings_goals')
    goals = cursor.fetchall()

    if goals:
        print(f"Found {len(goals)} savings goals:")
        for goal in goals:
            goal_dict = dict(goal)
            print(f"  ID: {goal_dict['id']} | Name: {goal_dict['goal_name']} | Target: ${goal_dict['target_amount']:.2f}")

        # Ask user if they want to delete all stuck goals
        print(f"\nFound {len(goals)} goals that may be stuck.")
        response = input("Do you want to delete ALL existing savings goals? (yes/no): ").strip().lower()

        if response == 'yes':
            # Delete all allocations first (foreign key constraint)
            db.execute('DELETE FROM savings_allocations')
            print("Deleted all savings allocations")

            # Then delete all goals
            db.execute('DELETE FROM savings_goals')
            print("Deleted all savings goals")

            # Reset auto-increment counters
            db.execute("DELETE FROM sqlite_sequence WHERE name='savings_goals'")
            db.execute("DELETE FROM sqlite_sequence WHERE name='savings_allocations'")
            print("Reset ID counters")

            db.commit()
            print("✅ All stuck goals removed successfully")
        else:
            print("Keeping existing goals")
    else:
        print("No existing savings goals found")

    print("\n=== Final schema check ===")
    cursor = db.execute('PRAGMA table_info(savings_goals)')
    columns = cursor.fetchall()
    for col in columns:
        print(f'{col[1]}: {col[2]}')

    db.disconnect()
    print("\n✅ Database schema fix completed!")

if __name__ == "__main__":
    fix_savings_goals_database()
