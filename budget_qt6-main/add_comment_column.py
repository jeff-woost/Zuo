"""
Add comment column to bank_transactions table
"""
import sqlite3

db_path = "budget_tracker.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE bank_transactions ADD COLUMN comment TEXT')
    conn.commit()
    print("✓ comment column added to bank_transactions")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠ comment column already exists in bank_transactions")
    else:
        print(f"Error: {e}")
finally:
    conn.close()

