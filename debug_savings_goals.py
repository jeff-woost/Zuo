#!/usr/bin/env python3
"""
Debug script to examine savings goals issues
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def debug_savings_goals():
    db = DatabaseManager()
    db.connect()

    print("=== Current savings_goals table schema ===")
    cursor = db.execute('PRAGMA table_info(savings_goals)')
    columns = cursor.fetchall()
    for col in columns:
        print(f'{col[1]}: {col[2]}')

    print("\n=== Current savings_goals records ===")
    cursor = db.execute('SELECT * FROM savings_goals')
    goals = cursor.fetchall()
    for goal in goals:
        print(dict(goal))

    print(f"\nTotal goals: {len(goals)}")

    print("\n=== Current savings_allocations records ===")
    cursor = db.execute('SELECT * FROM savings_allocations')
    allocations = cursor.fetchall()
    for allocation in allocations:
        print(dict(allocation))

    print(f"Total allocations: {len(allocations)}")

    db.disconnect()

if __name__ == "__main__":
    debug_savings_goals()
