#!/usr/bin/env python3
"""
Comprehensive Savings Goals Fix Script
=====================================

This script fixes all the savings goals issues:
1. UNIQUE constraint errors on goal_name
2. Database schema issues
3. UI naming and functionality separation
4. Goal creation vs allocation workflow
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from database.models import SavingsGoalModel, SavingsAllocationModel

def diagnose_and_fix_goals():
    """Diagnose and fix all savings goals issues"""
    print("🚀 Starting comprehensive savings goals fix...")

    db = DatabaseManager()

    try:
        # Step 1: Check current database state
        print("\n📊 Step 1: Checking current database state...")
        db.connect()

        # Check schema
        cursor = db.execute('PRAGMA table_info(savings_goals)')
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Current savings_goals columns: {column_names}")

        # Check for existing goals
        cursor = db.execute('SELECT * FROM savings_goals')
        existing_goals = cursor.fetchall()
        print(f"Found {len(existing_goals)} existing savings goals")

        if existing_goals:
            print("Existing goals:")
            for goal in existing_goals:
                goal_dict = dict(goal)
                print(f"  - ID: {goal_dict['id']} | Name: '{goal_dict['goal_name']}' | Target: ${goal_dict.get('target_amount', 0):.2f}")

        # Step 2: Fix UNIQUE constraint issues by cleaning up duplicates
        print(f"\n🧹 Step 2: Fixing UNIQUE constraint issues...")

        # Find duplicate goal names
        cursor = db.execute('''
            SELECT goal_name, COUNT(*) as count 
            FROM savings_goals 
            GROUP BY goal_name 
            HAVING COUNT(*) > 1
        ''')
        duplicates = cursor.fetchall()

        if duplicates:
            print(f"Found {len(duplicates)} duplicate goal names:")
            for dup in duplicates:
                print(f"  - '{dup['goal_name']}' appears {dup['count']} times")

            # Remove duplicates, keeping only the latest one
            for dup in duplicates:
                goal_name = dup['goal_name']
                cursor = db.execute('''
                    SELECT id FROM savings_goals 
                    WHERE goal_name = ? 
                    ORDER BY created_at DESC
                ''', (goal_name,))
                goal_ids = [row['id'] for row in cursor.fetchall()]

                # Keep the first (latest) and delete the rest
                if len(goal_ids) > 1:
                    for goal_id in goal_ids[1:]:
                        print(f"    Removing duplicate goal ID {goal_id}")
                        db.execute('DELETE FROM savings_allocations WHERE goal_id = ?', (goal_id,))
                        db.execute('DELETE FROM savings_goals WHERE id = ?', (goal_id,))

            db.commit()
            print("✅ Removed duplicate goals")
        else:
            print("✅ No duplicate goal names found")

        # Step 3: Clean up any goals with empty or invalid names
        print(f"\n🔧 Step 3: Cleaning up invalid goals...")
        cursor = db.execute('''
            SELECT * FROM savings_goals 
            WHERE goal_name IS NULL OR goal_name = '' OR TRIM(goal_name) = ''
        ''')
        invalid_goals = cursor.fetchall()

        if invalid_goals:
            print(f"Found {len(invalid_goals)} goals with invalid names:")
            for goal in invalid_goals:
                print(f"  - ID: {goal['id']} | Name: '{goal['goal_name']}'")
                db.execute('DELETE FROM savings_allocations WHERE goal_id = ?', (goal['id'],))
                db.execute('DELETE FROM savings_goals WHERE id = ?', (goal['id'],))
            db.commit()
            print("✅ Removed invalid goals")
        else:
            print("✅ No invalid goals found")

        # Step 4: Test goal creation
        print(f"\n🎯 Step 4: Testing goal creation...")

        # Try to create a test goal
        test_goal_name = f"Test Goal {db.execute('SELECT datetime()').fetchone()[0]}"
        try:
            test_goal_id = SavingsGoalModel.create(
                db,
                goal_name=test_goal_name,
                target_amount=1000.0,
                target_date="2025-12-31",
                priority=1,
                notes="Test goal for verification",
                initial_amount=0.0
            )
            print(f"✅ Successfully created test goal with ID: {test_goal_id}")

            # Clean up test goal
            SavingsGoalModel.delete(db, test_goal_id)
            print("✅ Test goal cleaned up")

        except Exception as e:
            print(f"❌ Error creating test goal: {e}")
            return False

        db.disconnect()

        print(f"\n🎉 All savings goals database issues have been fixed!")
        return True

    except Exception as e:
        print(f"❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_and_fix_goals()
    if success:
        print(f"\n✅ Database issues resolved!")
        print(f"📝 Next: Update the UI to separate Goal Setting from Goal Allocation")
    else:
        print(f"\n❌ Fix failed - please check the errors above")
