"""
Database Column Migration Script
=================================

This script migrates the net_worth_snapshots table from personal column names
(jeff_total, vanessa_total) to generic column names (user_a_total, user_b_total).

This migration is safe and will:
1. Check if old columns exist
2. If they do, rename them to new generic names
3. If new columns already exist, skip migration

Run this script to upgrade existing databases.
"""

import sqlite3
import sys
import os

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def run_migration(db_path="budget_tracker.db"):
    """Execute the column name migration"""
    print("Starting net_worth_snapshots column migration...")
    print(f"Database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"✓ Database does not exist yet - no migration needed")
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='net_worth_snapshots'
        """)
        
        if not cursor.fetchone():
            print("✓ net_worth_snapshots table does not exist - no migration needed")
            conn.close()
            return True
        
        # Check which columns exist
        has_jeff_total = check_column_exists(cursor, 'net_worth_snapshots', 'jeff_total')
        has_vanessa_total = check_column_exists(cursor, 'net_worth_snapshots', 'vanessa_total')
        has_user_a_total = check_column_exists(cursor, 'net_worth_snapshots', 'user_a_total')
        has_user_b_total = check_column_exists(cursor, 'net_worth_snapshots', 'user_b_total')
        
        print(f"Column status:")
        print(f"  - jeff_total exists: {has_jeff_total}")
        print(f"  - vanessa_total exists: {has_vanessa_total}")
        print(f"  - user_a_total exists: {has_user_a_total}")
        print(f"  - user_b_total exists: {has_user_b_total}")
        
        # If new columns already exist, no migration needed
        if has_user_a_total and has_user_b_total:
            print("✓ Migration already complete - new columns exist")
            conn.close()
            return True
        
        # If old columns don't exist, no migration needed
        if not has_jeff_total and not has_vanessa_total:
            print("✓ No old columns found - no migration needed")
            conn.close()
            return True
        
        # Perform the migration using SQLite's ALTER TABLE RENAME COLUMN
        print("\nPerforming migration...")
        
        # SQLite 3.25.0+ supports ALTER TABLE RENAME COLUMN
        if has_jeff_total:
            print("  Renaming jeff_total to user_a_total...")
            cursor.execute("""
                ALTER TABLE net_worth_snapshots 
                RENAME COLUMN jeff_total TO user_a_total
            """)
            print("  ✓ Renamed jeff_total to user_a_total")
        
        if has_vanessa_total:
            print("  Renaming vanessa_total to user_b_total...")
            cursor.execute("""
                ALTER TABLE net_worth_snapshots 
                RENAME COLUMN vanessa_total TO user_b_total
            """)
            print("  ✓ Renamed vanessa_total to user_b_total")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    # Allow specifying database path as command line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else "budget_tracker.db"
    
    success = run_migration(db_path)
    sys.exit(0 if success else 1)
