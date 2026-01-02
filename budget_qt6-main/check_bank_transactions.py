"""
Check bank_transactions table for duplicates
"""
import sqlite3

db_path = "budget_tracker.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check for duplicates
print("Checking for duplicate transactions...")
result = cursor.execute('''
    SELECT date, description, debit, credit, account_balance, COUNT(*) as count
    FROM bank_transactions
    GROUP BY date, description, debit, credit, account_balance
    HAVING COUNT(*) > 1
''').fetchall()

if result:
    print(f"Found {len(result)} sets of duplicates:")
    for row in result:
        print(f"  Date: {row['date']}, Desc: {row['description'][:50]}, Count: {row['count']}")
else:
    print("No duplicates found!")

# Count total transactions
total = cursor.execute('SELECT COUNT(*) FROM bank_transactions').fetchone()[0]
print(f"\nTotal transactions in database: {total}")

# Check if comment column exists
try:
    cursor.execute('SELECT comment FROM bank_transactions LIMIT 1')
    print("✓ comment column exists")
except sqlite3.OperationalError:
    print("✗ comment column does NOT exist - need to run migration")

conn.close()

