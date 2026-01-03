#!/usr/bin/env python3
"""
Emergency fix: Add comment column to bank_transactions table
"""
import sqlite3
import os

# Get the correct path - script is in budget_qt6 directory
db_path = os.path.join(os.path.dirname(__file__), "budget_tracker.db")

if not os.path.exists(db_path):
    print(f"❌ Database not found at: {db_path}")
    exit(1)

print("Connecting to database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding comment column to bank_transactions...")
    cursor.execute('ALTER TABLE bank_transactions ADD COLUMN comment TEXT')
    conn.commit()
    print("✅ SUCCESS: comment column added!")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("✅ comment column already exists - you're good to go!")
    else:
        print(f"❌ ERROR: {e}")
        exit(1)
finally:
    conn.close()

print("\n✓ Database is ready. You can now use the comment feature.")

