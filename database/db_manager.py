"""
Database Management Module
==========================

This module provides centralized database operations for the Budget Tracker application.
It implements a singleton pattern to ensure consistent database access across the entire
application and provides comprehensive methods for all financial data operations.

Key Features:
- Singleton pattern for consistent database connections
- Thread-safe operations with proper locking
- Context manager support for transaction handling
- Comprehensive CRUD operations for all financial entities
- Automatic table creation and schema management
- Data integrity and validation

Database Schema:
- income: Personal income tracking
- expenses: Detailed expense categorization and tracking
- net_worth_assets: Asset and liability management
- savings_goals: Goal setting and progress tracking
- budget_estimates: Monthly budget planning
- categories: Expense categorization system

Classes:
    DatabaseManager: Primary database interface with singleton pattern

Dependencies:
    - sqlite3: Built-in Python SQLite database interface
    - threading: Thread synchronization for singleton pattern
    - datetime: Date/time handling for financial records
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import json
import threading
import sys

# Add config module to path if not already there
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
if config_path not in sys.path:
    sys.path.insert(0, config_path)

from config import load_defaults

class DatabaseManager:
    """
    Singleton database manager for centralized data operations.

    This class provides a unified interface for all database operations in the
    Budget Tracker application. It implements the singleton pattern to ensure
    only one database connection exists at any time, preventing conflicts and
    ensuring data consistency.

    Key Design Patterns:
    - Singleton: Only one instance exists per application
    - Context Manager: Automatic transaction handling
    - Thread-Safe: Multiple tabs can safely access data

    Attributes:
        _instance (DatabaseManager): Singleton instance reference
        _lock (threading.Lock): Thread synchronization lock
        db_path (str): Path to SQLite database file
        conn (sqlite3.Connection): Database connection object
        cursor (sqlite3.Cursor): Database cursor for operations
        initialized (bool): Tracks if instance is fully initialized
    """

    # Class-level attributes for singleton pattern
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "budget_tracker.db"):
        """
        Singleton constructor ensuring only one database instance.

        This method implements the singleton pattern using thread-safe
        double-checked locking to ensure only one DatabaseManager
        instance exists per application lifecycle.

        Args:
            db_path (str): Path to SQLite database file

        Returns:
            DatabaseManager: The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check pattern: verify instance is still None
                # after acquiring the lock (another thread might have
                # created it while we were waiting)
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "budget_tracker.db"):
        """
        Initialize database connection and settings.

        This method sets up the database connection parameters and
        initializes the SQLite database with proper settings for
        concurrent access and performance.

        Args:
            db_path (str): Path to SQLite database file (default: "budget_tracker.db")

        Note:
            Due to singleton pattern, this only runs once per application.
        """
        # Prevent re-initialization of singleton instance
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.conn = None
            self.cursor = None
            self.initialized = True

    def connect(self):
        """
        Establish database connection with optimized settings.

        This method creates a connection to the SQLite database with
        settings optimized for concurrent access and performance:
        - WAL mode: Allows concurrent reads during writes
        - Busy timeout: Handles database locking gracefully
        - Row factory: Enables dictionary-style result access
        """
        if self.conn is None:
            # Create connection with timeout and threading support
            self.conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30 second timeout for busy database
                check_same_thread=False  # Allow use across threads
            )

            # Enable dictionary-style row access (row['column_name'])
            self.conn.row_factory = sqlite3.Row

            # Enable WAL (Write-Ahead Logging) mode for better concurrency
            # This allows multiple readers while one writer is active
            self.conn.execute("PRAGMA journal_mode=WAL")

            # Set busy timeout to handle locked database gracefully
            self.conn.execute("PRAGMA busy_timeout=30000")  # 30 seconds

            # Create cursor for executing SQL commands
            self.cursor = self.conn.cursor()

    def disconnect(self):
        """
        Safely close database connection and cleanup resources.

        This method properly closes the database connection and
        resets connection objects to None for garbage collection.
        """
        if self.conn:
            try:
                self.conn.close()
            except:
                # Ignore errors during connection closure
                pass
            finally:
                # Always reset connection objects
                self.conn = None
                self.cursor = None

    def execute(self, query, params=None):
        """
        Execute SQL query with automatic connection management.

        This method handles SQL execution with automatic connection
        establishment and basic retry logic for database locking issues.

        Args:
            query (str): SQL query string to execute
            params (tuple, optional): Query parameters for safe execution

        Returns:
            sqlite3.Cursor: Cursor with query results

        Raises:
            sqlite3.OperationalError: For database access errors
        """
        # Ensure we have an active database connection
        self.connect()
        
        try:
            # Execute query with or without parameters
            if params:
                result = self.cursor.execute(query, params)
            else:
                result = self.cursor.execute(query)
            return result
        except sqlite3.OperationalError as e:
            # Handle database locking with simple retry
            if "database is locked" in str(e):
                # Wait briefly and retry once
                import time
                time.sleep(0.1)
                if params:
                    result = self.cursor.execute(query, params)
                else:
                    result = self.cursor.execute(query)
                return result
            else:
                # Re-raise other operational errors
                raise

    def commit(self):
        """
        Commit current transaction to database.

        This method saves all pending changes to the database.
        Should be called after INSERT, UPDATE, or DELETE operations.
        """
        if self.conn:
            self.conn.commit()
            
    def __enter__(self):
        """
        Context manager entry - establish connection.

        This enables usage like:
        with DatabaseManager() as db:
            db.execute("SELECT * FROM expenses")

        Returns:
            DatabaseManager: Self reference for context operations
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - handle transaction completion.

        This automatically commits transactions on successful completion
        and maintains the singleton connection for reuse.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        if exc_type is None:
            # No exception occurred - commit the transaction
            self.commit()
        # Note: Don't disconnect here to maintain singleton connection

    def initialize_database(self):
        """
        Create all necessary database tables and initial data.

        This method sets up the complete database schema for the
        Budget Tracker application. It creates all required tables
        with proper constraints and relationships, then loads
        default category data.

        Tables Created:
        - categories: Expense categorization system
        - income: Income tracking records
        - expenses: Detailed expense records
        - net_worth_assets: Asset and liability tracking
        - savings_goals: Savings goal definitions
        - savings_allocations: Goal funding records
        - budget_targets: Monthly budget targets
        - budget_estimates: Budget planning estimates
        - net_worth_snapshots: Historical net worth data
        """
        self.connect()
        
        # Categories table: Master list of expense categories and subcategories
        # This provides the foundation for expense organization
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                UNIQUE(category, subcategory)
            )
        ''')
        
        # Income table: Track all sources of income
        # Supports multiple people and detailed descriptions
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table: Detailed expense tracking with categorization
        # Core table for expense management with payment tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                description TEXT,
                payment_method TEXT,
                realized BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add realized column to existing expenses table if missing
        # This supports tracking whether expenses have been paid
        try:
            self.cursor.execute('ALTER TABLE expenses ADD COLUMN realized BOOLEAN DEFAULT 0')
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists - ignore error
            pass

        # Net worth assets table: Track assets and liabilities over time
        # Supports historical tracking of financial position
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS net_worth_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                value REAL NOT NULL,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Savings goals table: Define and track savings objectives
        # Supports prioritization and progress tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL UNIQUE,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                initial_amount REAL DEFAULT 0,
                target_date DATE,
                priority INTEGER DEFAULT 1,
                notes TEXT,
                is_completed BOOLEAN DEFAULT 0,
                completion_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add initial_amount column to existing savings_goals table if missing
        try:
            self.cursor.execute('ALTER TABLE savings_goals ADD COLUMN initial_amount REAL DEFAULT 0')
            self.conn.commit()
            print("Added missing initial_amount column to savings_goals table")
        except sqlite3.OperationalError:
            # Column already exists - ignore error
            pass

        # Savings allocations table: Track contributions to goals
        # Links to savings_goals table via foreign key
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES savings_goals (id)
            )
        ''')
        
        # Budget targets table: Set spending targets by category
        # Supports monthly budget planning and variance analysis
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                monthly_target REAL NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                UNIQUE(category, subcategory, year, month)
            )
        ''')
        
        # Budget estimates table: Detailed monthly budget planning
        # More granular than targets, supports category-level planning
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_estimates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                estimated_amount REAL NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, subcategory, year, month)
            )
        ''')

        # Net worth snapshots table: Historical net worth tracking
        # Enables trend analysis and financial progress monitoring
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS net_worth_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                user_a_total REAL,
                user_b_total REAL,
                joint_total REAL,
                total_net_worth REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Commit all table creation changes
        self.conn.commit()

        # Load default categories from predefined list
        self.load_default_categories()

        # Close connection to free resources
        self.disconnect()

    def load_default_categories(self):
        """
        Load predefined expense categories and subcategories from config.
        
        This method populates the categories table with categories
        loaded from the config/defaults.json file, providing flexibility
        and easy customization of expense categories.
        """
        # Load categories from JSON configuration
        defaults = load_defaults()
        categories_dict = defaults.get("categories", {})
        
        # Convert dictionary to list of tuples for insertion
        categories = []
        for category, subcategories in categories_dict.items():
            for subcategory in subcategories:
                categories.append((category, subcategory))
        
        # Insert categories using INSERT OR IGNORE to prevent duplicates
        for category, subcategory in categories:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO categories (category, subcategory) VALUES (?, ?)",
                    (category, subcategory)
                )
            except Exception as e:
                print(f"Error inserting category {category}/{subcategory}: {e}")

        # Commit all category insertions
        self.conn.commit()

    # Income Management Methods
    # ========================

    def add_income(self, person: str, amount: float, date: str, description: str = None):
        """
        Add a new income entry to the database.

        Args:
            person (str): Name of person receiving income ("Jeff" or "Vanessa")
            amount (float): Income amount in dollars
            date (str): Date in YYYY-MM-DD format
            description (str, optional): Description of income source
        """
        self.connect()
        self.cursor.execute(
            "INSERT INTO income (person, amount, date, description) VALUES (?, ?, ?, ?)",
            (person, amount, date, description)
        )
        self.conn.commit()
        self.disconnect()

    def get_income(self, start_date: str = None, end_date: str = None, person: str = None):
        """
        Retrieve income entries with optional filtering.

        Args:
            start_date (str, optional): Filter start date (YYYY-MM-DD)
            end_date (str, optional): Filter end date (YYYY-MM-DD)
            person (str, optional): Filter by person name

        Returns:
            List[Dict]: List of income records as dictionaries
        """
        self.connect()
        query = "SELECT * FROM income WHERE 1=1"
        params = []

        # Build dynamic query based on provided filters
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            # Use strictly less than to exclude the end_date itself
            # This prevents including income from the first day of the next month
            query += " AND date < ?"
            params.append(end_date)
        if person:
            query += " AND person = ?"
            params.append(person)

        # Order by date descending (most recent first)
        query += " ORDER BY date DESC"

        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    # Expense Management Methods
    # ==========================

    def add_expense(self, person: str, amount: float, date: str, category: str,
                   subcategory: str, description: str = None, payment_method: str = None, realized: bool = False):
        """
        Add a new expense entry to the database.

        Args:
            person (str): Name of person making expense
            amount (float): Expense amount in dollars
            date (str): Date in YYYY-MM-DD format
            category (str): Primary expense category
            subcategory (str): Specific subcategory
            description (str, optional): Expense description
            payment_method (str, optional): How expense was paid
            realized (bool): Whether expense has been paid from joint account
        """
        self.connect()
        self.cursor.execute(
            """INSERT INTO expenses (person, amount, date, category, subcategory, 
               description, payment_method, realized) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (person, amount, date, category, subcategory, description, payment_method, realized)
        )
        self.conn.commit()
        self.disconnect()

    def get_expenses(self, start_date: str = None, end_date: str = None,
                    person: str = None, category: str = None):
        """
        Retrieve expense entries with optional filtering.

        Args:
            start_date (str, optional): Filter start date
            end_date (str, optional): Filter end date
            person (str, optional): Filter by person
            category (str, optional): Filter by category

        Returns:
            List[Dict]: List of expense records
        """
        self.connect()
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []

        # Build dynamic query with filters
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            # Use strictly less than to exclude the end_date itself
            # This prevents including expenses from the first day of the next month
            query += " AND date < ?"
            params.append(end_date)
        if person:
            query += " AND person = ?"
            params.append(person)
        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY date DESC"

        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def bulk_add_expenses(self, expenses: List[Dict]):
        """
        Add multiple expense entries in a single transaction.

        This method is optimized for importing large numbers of expenses
        from CSV files or other bulk operations.

        Args:
            expenses (List[Dict]): List of expense dictionaries with required fields
        """
        self.connect()
        for expense in expenses:
            self.cursor.execute(
                """INSERT INTO expenses (person, amount, date, category, subcategory, 
                   description, payment_method, realized) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (expense['person'], expense['amount'], expense['date'],
                 expense['category'], expense['subcategory'],
                 expense.get('description'), expense.get('payment_method'),
                 expense.get('realized', False))
            )
        self.conn.commit()
        self.disconnect()

    # Net worth methods
    def add_asset(self, person: str, asset_type: str, asset_name: str,
                 value: float, date: str, notes: str = None, category: str = None):
        """Feature 6: Add or update net worth asset with category and last_updated"""
        self.connect()
        
        # Auto-categorize if not provided
        if not category:
            # Simple auto-categorization logic
            category_map = {
                '401(k)': 'Retirement (Traditional)',
                'Traditional IRA': 'Retirement (Traditional)',
                'Roth 401(k)': 'Retirement (Roth)',
                'Roth IRA': 'Retirement (Roth)',
                'Real Estate': 'Real Estate',
                'Checking Account': 'Liquid Cash',
                'Savings Account': 'Liquid Cash',
                'Brokerage Account': 'Investments',
                'Vehicle': 'Vehicles',
                'Debt/Liability': 'Liabilities',
            }
            category = category_map.get(asset_type, 'Other Assets')
        
        # Get current timestamp for last_updated
        from datetime import datetime
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute(
            """INSERT INTO net_worth_assets (person, asset_type, asset_name, 
               value, date, notes, category, last_updated) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (person, asset_type, asset_name, value, date, notes, category, last_updated)
        )
        self.conn.commit()
        self.disconnect()

    def get_assets(self, date: str = None, person: str = None):
        """Get net worth assets"""
        self.connect()

        if date:
            # Get most recent values for each asset up to the specified date
            query = """
                SELECT * FROM net_worth_assets 
                WHERE id IN (
                    SELECT MAX(id) FROM net_worth_assets 
                    WHERE date <= ? 
                    GROUP BY person, asset_type, asset_name
                )
            """
            params = [date]
        else:
            # Get most recent values for all assets
            query = """
                SELECT * FROM net_worth_assets 
                WHERE id IN (
                    SELECT MAX(id) FROM net_worth_assets 
                    GROUP BY person, asset_type, asset_name
                )
            """
            params = []

        if person:
            query += " AND person = ?"
            params.append(person)

        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def add_asset_extended(self, person: str, asset_type: str, asset_name: str,
                           value: float, date: str, notes: str = None,
                           category: str = None, subcategory: str = None, liquidity: int = 5):
        """Add an asset with extended fields (category, subcategory, liquidity)"""
        self.connect()

        # Ensure columns exist
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN subcategory TEXT')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN liquidity INTEGER DEFAULT 5')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN category TEXT')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN last_updated TIMESTAMP')
        except:
            pass

        from datetime import datetime
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute('''
            INSERT INTO net_worth_assets 
            (person, asset_type, asset_name, value, date, notes, category, subcategory, liquidity, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (person, asset_type, asset_name, value, date, notes,
              category or asset_type, subcategory or '', liquidity, last_updated))
        self.conn.commit()
        self.disconnect()

    def get_assets_extended(self, date: str = None, person: str = None, category: str = None):
        """Get net worth assets with extended fields, deduplicated to most recent per asset"""
        self.connect()

        # Ensure columns exist for older databases
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN subcategory TEXT')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN liquidity INTEGER DEFAULT 5')
        except:
            pass

        # Get most recent values for all assets
        query = '''
            SELECT *, 
                   COALESCE(category, asset_type) as category,
                   COALESCE(subcategory, '') as subcategory,
                   COALESCE(liquidity, 5) as liquidity
            FROM net_worth_assets 
            WHERE id IN (
                SELECT MAX(id) FROM net_worth_assets 
                GROUP BY person, asset_name
            )
        '''
        params = []

        conditions = []
        if person:
            conditions.append("person = ?")
            params.append(person)
        if category:
            conditions.append("(category = ? OR asset_type = ?)")
            params.extend([category, category])

        if conditions:
            query = f'''
                SELECT * FROM ({query}) AS subq
                WHERE {' AND '.join(conditions)}
            '''

        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def update_asset(self, asset_id: int, person: str = None, asset_type: str = None,
                     asset_name: str = None, value: float = None, date: str = None,
                     notes: str = None, category: str = None, subcategory: str = None,
                     liquidity: int = None):
        """Update an existing asset"""
        self.connect()

        from datetime import datetime
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        updates = ['last_updated = ?']
        params = [last_updated]

        if person is not None:
            updates.append('person = ?')
            params.append(person)
        if asset_type is not None:
            updates.append('asset_type = ?')
            params.append(asset_type)
        if asset_name is not None:
            updates.append('asset_name = ?')
            params.append(asset_name)
        if value is not None:
            updates.append('value = ?')
            params.append(value)
        if date is not None:
            updates.append('date = ?')
            params.append(date)
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)
        if category is not None:
            updates.append('category = ?')
            params.append(category)
        if subcategory is not None:
            updates.append('subcategory = ?')
            params.append(subcategory)
        if liquidity is not None:
            updates.append('liquidity = ?')
            params.append(liquidity)

        params.append(asset_id)

        self.cursor.execute(f'''
            UPDATE net_worth_assets 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        self.conn.commit()
        self.disconnect()

    def delete_asset(self, asset_id: int):
        """Delete an asset by ID - also deletes all records with the same asset_name"""
        self.connect()

        # First get the asset name for this ID
        self.cursor.execute('SELECT asset_name FROM net_worth_assets WHERE id = ?', (asset_id,))
        result = self.cursor.fetchone()

        if result:
            asset_name = result['asset_name']
            # Delete ALL records with this asset name (removes history too)
            self.cursor.execute('DELETE FROM net_worth_assets WHERE asset_name = ?', (asset_name,))
        else:
            # Fallback: just delete by ID if name not found
            self.cursor.execute('DELETE FROM net_worth_assets WHERE id = ?', (asset_id,))

        self.conn.commit()
        self.disconnect()

    def delete_asset_by_name(self, asset_name: str):
        """Delete all records for an asset by name"""
        self.connect()
        self.cursor.execute('DELETE FROM net_worth_assets WHERE asset_name = ?', (asset_name,))
        self.conn.commit()
        self.disconnect()

    def get_current_assets(self):
        """
        Get the current list of assets (most recent value for each unique asset).
        This is the mutable list that users interact with.
        """
        self.connect()

        # Ensure required columns exist
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN subcategory TEXT')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN liquidity INTEGER DEFAULT 5')
        except:
            pass
        try:
            self.cursor.execute('ALTER TABLE net_worth_assets ADD COLUMN category TEXT')
        except:
            pass

        # Get one record per unique asset (by name), with the most recent ID
        query = '''
            SELECT id, person, asset_type, asset_name, value, date, notes,
                   COALESCE(category, asset_type) as category,
                   COALESCE(subcategory, '') as subcategory,
                   COALESCE(liquidity, 5) as liquidity,
                   last_updated
            FROM net_worth_assets
            WHERE id IN (
                SELECT MAX(id) FROM net_worth_assets
                GROUP BY asset_name
            )
            ORDER BY COALESCE(category, asset_type), asset_name
        '''
        self.cursor.execute(query)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def upsert_asset(self, asset_name: str, person: str, category: str, subcategory: str,
                     value: float, liquidity: int = 5, notes: str = ""):
        """
        Insert or update an asset. If asset with same name exists, update it.
        Otherwise insert a new asset.
        """
        self.connect()

        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if asset exists
        self.cursor.execute('SELECT id FROM net_worth_assets WHERE asset_name = ?', (asset_name,))
        existing = self.cursor.fetchone()

        if existing:
            # Update existing asset
            self.cursor.execute('''
                UPDATE net_worth_assets
                SET value = ?, person = ?, category = ?, subcategory = ?, 
                    liquidity = ?, notes = ?, date = ?, last_updated = ?, asset_type = ?
                WHERE asset_name = ?
            ''', (value, person, category, subcategory, liquidity, notes,
                  current_date, last_updated, category, asset_name))
        else:
            # Insert new asset
            self.cursor.execute('''
                INSERT INTO net_worth_assets 
                (asset_name, person, asset_type, category, subcategory, value, 
                 liquidity, notes, date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (asset_name, person, category, category, subcategory, value,
                  liquidity, notes, current_date, last_updated))

        self.conn.commit()
        self.disconnect()

    def update_asset_value(self, asset_id: int, value: float):
        """Quick update just the value of an asset"""
        self.connect()
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cursor.execute('''
            UPDATE net_worth_assets
            SET value = ?, date = ?, last_updated = ?
            WHERE id = ?
        ''', (value, current_date, last_updated, asset_id))
        self.conn.commit()
        self.disconnect()

    def update_asset_full(self, asset_id: int, value: float = None, liquidity: int = None, notes: str = None):
        """Update multiple fields of an asset"""
        self.connect()
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        updates = ['date = ?', 'last_updated = ?']
        params = [current_date, last_updated]

        if value is not None:
            updates.append('value = ?')
            params.append(value)
        if liquidity is not None:
            updates.append('liquidity = ?')
            params.append(liquidity)
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)

        params.append(asset_id)

        self.cursor.execute(f'''
            UPDATE net_worth_assets
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        self.conn.commit()
        self.disconnect()

    def update_asset_all_fields(self, asset_id: int, asset_name: str = None, person: str = None,
                                 category: str = None, subcategory: str = None, value: float = None,
                                 liquidity: int = None, notes: str = None):
        """Update ALL fields of an asset including name, person, category, subcategory"""
        self.connect()
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        updates = ['date = ?', 'last_updated = ?']
        params = [current_date, last_updated]

        if asset_name is not None:
            updates.append('asset_name = ?')
            params.append(asset_name)
        if person is not None:
            updates.append('person = ?')
            params.append(person)
        if category is not None:
            updates.append('category = ?')
            params.append(category)
            updates.append('asset_type = ?')  # Keep asset_type in sync
            params.append(category)
        if subcategory is not None:
            updates.append('subcategory = ?')
            params.append(subcategory)
        if value is not None:
            updates.append('value = ?')
            params.append(value)
        if liquidity is not None:
            updates.append('liquidity = ?')
            params.append(liquidity)
        if notes is not None:
            updates.append('notes = ?')
            params.append(notes)

        params.append(asset_id)

        self.cursor.execute(f'''
            UPDATE net_worth_assets
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)
        self.conn.commit()
        self.disconnect()

    def save_net_worth_snapshot(self, assets_list: list):
        """
        Save a snapshot of current asset values to history table.
        This creates a point-in-time record for historical tracking.
        """
        self.connect()
        from datetime import datetime
        snapshot_date = datetime.now().strftime('%Y-%m-%d')

        # Create history table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS net_worth_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date DATE NOT NULL,
                category TEXT,
                total_value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Calculate totals by category
        category_totals = {}
        total = 0
        for asset in assets_list:
            category = asset.get('category', 'Other')
            value = asset.get('value', 0) or 0
            category_totals[category] = category_totals.get(category, 0) + value
            total += value

        # Insert category totals
        for category, cat_total in category_totals.items():
            self.cursor.execute('''
                INSERT INTO net_worth_history (snapshot_date, category, total_value)
                VALUES (?, ?, ?)
            ''', (snapshot_date, category, cat_total))

        # Insert total
        self.cursor.execute('''
            INSERT INTO net_worth_history (snapshot_date, category, total_value)
            VALUES (?, ?, ?)
        ''', (snapshot_date, 'Total Net Worth', total))

        self.conn.commit()
        self.disconnect()

    def get_net_worth_history(self, category: str = None):
        """Get historical net worth data for charting"""
        self.connect()

        # Try to use history table first
        try:
            if category and category != "Total Net Worth":
                query = '''
                    SELECT snapshot_date as date, total_value
                    FROM net_worth_history
                    WHERE category = ?
                    ORDER BY snapshot_date ASC
                '''
                self.cursor.execute(query, (category,))
            else:
                query = '''
                    SELECT snapshot_date as date, total_value
                    FROM net_worth_history
                    WHERE category = 'Total Net Worth'
                    ORDER BY snapshot_date ASC
                '''
                self.cursor.execute(query)

            results = [dict(row) for row in self.cursor.fetchall()]

            if results:
                self.disconnect()
                return results
        except:
            pass

        # Fall back to asset table dates
        if category and category != "Total Net Worth":
            query = '''
                SELECT date, SUM(value) as total_value
                FROM net_worth_assets
                WHERE category = ? OR asset_type = ?
                GROUP BY date
                ORDER BY date ASC
            '''
            self.cursor.execute(query, (category, category))
        else:
            query = '''
                SELECT date, SUM(value) as total_value
                FROM net_worth_assets
                GROUP BY date
                ORDER BY date ASC
            '''
            self.cursor.execute(query)

        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def get_asset_history(self, category: str = None):
        """Get historical asset values for charting, grouped by date"""
        self.connect()

        if category and category != "Total Net Worth":
            # Get history for specific category
            query = '''
                SELECT date, SUM(value) as total_value
                FROM net_worth_assets
                WHERE category = ? OR asset_type = ?
                GROUP BY date
                ORDER BY date ASC
            '''
            self.cursor.execute(query, (category, category))
        else:
            # Get total net worth history
            query = '''
                SELECT date, SUM(value) as total_value
                FROM net_worth_assets
                GROUP BY date
                ORDER BY date ASC
            '''
            self.cursor.execute(query)

        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    # Savings goals methods
    def add_savings_goal(self, goal_name: str, target_amount: float,
                        target_date: str = None, priority: int = 1, notes: str = None, initial_amount: float = 0):
        """Add a new savings goal"""
        self.connect()
        self.cursor.execute(
            """INSERT INTO savings_goals (goal_name, target_amount, target_date, 
               priority, notes, initial_amount, current_amount) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (goal_name, target_amount, target_date, priority, notes, initial_amount, initial_amount)
        )
        self.conn.commit()
        self.disconnect()

    def get_savings_goals(self, include_completed=False):
        """Get all savings goals"""
        self.connect()
        query = "SELECT * FROM savings_goals"
        if not include_completed:
            query += " WHERE is_completed = 0"
        query += " ORDER BY priority, goal_name"

        self.cursor.execute(query)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def update_savings_goal(self, goal_id: int, goal_name: str, target_amount: float,
                           target_date: str = None, priority: int = 1, notes: str = None, initial_amount: float = None):
        """Update an existing savings goal"""
        self.connect()
        if initial_amount is not None:
            self.cursor.execute(
                """UPDATE savings_goals SET goal_name = ?, target_amount = ?, target_date = ?, 
                   priority = ?, notes = ?, initial_amount = ? WHERE id = ?""",
                (goal_name, target_amount, target_date, priority, notes, initial_amount, goal_id)
            )
        else:
            self.cursor.execute(
                """UPDATE savings_goals SET goal_name = ?, target_amount = ?, target_date = ?, 
                   priority = ?, notes = ? WHERE id = ?""",
                (goal_name, target_amount, target_date, priority, notes, goal_id)
            )
        self.conn.commit()
        self.disconnect()

    def complete_savings_goal(self, goal_id: int):
        """Mark a savings goal as completed"""
        self.connect()
        self.cursor.execute(
            """UPDATE savings_goals SET is_completed = 1, completion_date = DATE('now') 
               WHERE id = ?""",
            (goal_id,)
        )
        self.conn.commit()
        self.disconnect()

    def delete_savings_goal(self, goal_id: int):
        """Delete a savings goal and its allocations"""
        self.connect()
        self.cursor.execute("DELETE FROM savings_goals WHERE id = ?", (goal_id,))
        self.conn.commit()
        self.disconnect()

    def get_completed_goals(self):
        """Get all completed savings goals"""
        self.connect()
        self.cursor.execute(
            """SELECT * FROM savings_goals WHERE is_completed = 1 
               ORDER BY completion_date DESC"""
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def get_goal_allocations(self, goal_id: int):
        """Get all allocations for a specific goal"""
        self.connect()
        self.cursor.execute(
            """SELECT * FROM savings_allocations WHERE goal_id = ? 
               ORDER BY date DESC""",
            (goal_id,)
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def get_monthly_goal_allocations(self, year: int, month: int):
        """Get all goal allocations for a specific month"""
        self.connect()
        self.cursor.execute(
            """SELECT sa.*, sg.goal_name 
               FROM savings_allocations sa
               JOIN savings_goals sg ON sa.goal_id = sg.id
               WHERE strftime('%Y', sa.date) = ? AND strftime('%m', sa.date) = ?
               ORDER BY sa.date DESC""",
            (str(year), f"{month:02d}")
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results

    def get_monthly_summary(self, year: int, month: int):
        """Get monthly income and expense summary"""
        self.connect()

        # Get income for the month
        income_query = """
            SELECT person, SUM(amount) as total 
            FROM income 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY person
        """
        self.cursor.execute(income_query, (str(year), f"{month:02d}"))
        income_results = self.cursor.fetchall()

        # Get expenses for the month
        expense_query = """
            SELECT person, SUM(amount) as total 
            FROM expenses 
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY person
        """
        self.cursor.execute(expense_query, (str(year), f"{month:02d}"))
        expense_results = self.cursor.fetchall()

        self.disconnect()

        # Format results
        income_dict = {row[0]: row[1] for row in income_results}
        expense_dict = {row[0]: row[1] for row in expense_results}

        return {
            'income': income_dict,
            'expenses': expense_dict
        }

    def allocate_to_goal(self, goal_id: int, amount: float, date: str, notes: str = None):
        """Allocate money to a savings goal"""
        self.connect()

        # Add allocation record
        self.cursor.execute(
            """INSERT INTO savings_allocations (goal_id, amount, date, notes) 
               VALUES (?, ?, ?, ?)""",
            (goal_id, amount, date, notes)
        )

        # Update current amount in goals table
        self.cursor.execute(
            "UPDATE savings_goals SET current_amount = current_amount + ? WHERE id = ?",
            (amount, goal_id)
        )

        self.conn.commit()
        self.disconnect()

    # ===== Category Learning Methods (Feature 2) =====
    
    def save_category_mapping(self, description: str, category: str, subcategory: str):
        """
        Save or update a category mapping for future auto-suggestions.
        
        Args:
            description (str): Expense description pattern
            category (str): Category to map to
            subcategory (str): Subcategory to map to
        """
        self.connect()
        
        # Clean description for pattern matching
        description_pattern = description.lower().strip()
        
        try:
            # Try to update existing mapping
            result = self.cursor.execute('''
                SELECT id, usage_count FROM expense_category_history
                WHERE description_pattern = ? AND category = ? AND subcategory = ?
            ''', (description_pattern, category, subcategory)).fetchone()
            
            if result:
                # Update usage count and last_used timestamp
                self.cursor.execute('''
                    UPDATE expense_category_history
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (result['id'],))
            else:
                # Insert new mapping
                self.cursor.execute('''
                    INSERT INTO expense_category_history 
                    (description_pattern, category, subcategory, usage_count, last_used)
                    VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ''', (description_pattern, category, subcategory))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error saving category mapping: {e}")
            if self.conn:
                self.conn.rollback()
    
    def get_suggested_category(self, description: str):
        """
        Get suggested category and subcategory based on description.
        
        Uses fuzzy matching to find the most similar description pattern
        from the history and existing expenses, returning the most frequently used category.

        Feature 2 Enhancement: Also searches existing expenses table for keyword matches.
        For example, if "ACME" appears in the description and there's an existing expense
        with "ACME" that was categorized as "Food - Food (Groceries)", this will suggest
        that category.

        Args:
            description (str): Expense description to match
            
        Returns:
            dict or None: {'category': str, 'subcategory': str, 'confidence': float}
                         or None if no match found
        """
        self.connect()
        
        # Clean description for matching
        description_pattern = description.lower().strip()
        
        # First, try exact match in category history
        result = self.cursor.execute('''
            SELECT category, subcategory, usage_count
            FROM expense_category_history
            WHERE description_pattern = ?
            ORDER BY usage_count DESC, last_used DESC
            LIMIT 1
        ''', (description_pattern,)).fetchone()
        
        if result:
            return {
                'category': result['category'],
                'subcategory': result['subcategory'],
                'confidence': 1.0
            }
        
        # Try partial matching in category history
        all_patterns = self.cursor.execute('''
            SELECT description_pattern, category, subcategory, usage_count
            FROM expense_category_history
            ORDER BY usage_count DESC, last_used DESC
        ''').fetchall()
        
        # Simple fuzzy matching: look for common words
        description_words = set(description_pattern.split())
        best_match = None
        best_score = 0
        
        for pattern in all_patterns:
            pattern_words = set(pattern['description_pattern'].split())
            
            # Calculate similarity score (Jaccard similarity)
            if len(pattern_words) > 0:
                intersection = description_words.intersection(pattern_words)
                union = description_words.union(pattern_words)
                score = len(intersection) / len(union) if len(union) > 0 else 0
                
                # Boost score by usage count
                score = score * (1 + min(pattern['usage_count'] / 10, 0.5))
                
                if score > best_score and score > 0.3:  # Minimum threshold
                    best_score = score
                    best_match = pattern
        
        if best_match:
            return {
                'category': best_match['category'],
                'subcategory': best_match['subcategory'],
                'confidence': best_score
            }
        
        # Feature 2 Enhancement: Search existing expenses table for keyword matches
        # This allows matching descriptions like "ACME" to historical expenses
        suggestion = self._search_expenses_for_category(description_pattern)
        if suggestion:
            return suggestion

        return None

    def _search_expenses_for_category(self, description: str):
        """
        Search existing expenses for matching descriptions and return the most common category.

        This method looks for keywords in the description that match existing expense
        descriptions (case-insensitive). It returns the category/subcategory that has
        been used most frequently for similar descriptions.

        Args:
            description (str): Expense description to match (already lowercase)

        Returns:
            dict or None: {'category': str, 'subcategory': str, 'confidence': float}
                         or None if no match found
        """
        # Extract significant words (skip very short words and common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'for', 'to', 'in', 'on', 'at', 'of', 'by',
                       'with', 'from', 'as', 'is', 'it', 'was', 'are', 'were', 'be', 'been',
                       'payment', 'purchase', 'card', 'debit', 'credit', 'pos', 'transaction'}

        description_words = [word for word in description.split()
                            if len(word) >= 3 and word not in common_words]

        if not description_words:
            return None

        best_category = None
        best_subcategory = None
        best_count = 0
        best_confidence = 0

        for word in description_words:
            # Search for expenses with this word in the description (case-insensitive)
            # Use LIKE with wildcards for partial matching
            pattern = f'%{word}%'

            try:
                results = self.cursor.execute('''
                    SELECT category, subcategory, COUNT(*) as count
                    FROM expenses
                    WHERE LOWER(description) LIKE ?
                    GROUP BY category, subcategory
                    ORDER BY count DESC
                    LIMIT 1
                ''', (pattern,)).fetchone()

                if results and results['count'] > best_count:
                    best_count = results['count']
                    best_category = results['category']
                    best_subcategory = results['subcategory']
                    # Confidence based on how many times this was used
                    best_confidence = min(0.5 + (results['count'] / 20), 0.9)
            except Exception as e:
                print(f"Error searching expenses for category: {e}")
                continue

        if best_category and best_subcategory and best_count >= 1:
            return {
                'category': best_category,
                'subcategory': best_subcategory,
                'confidence': best_confidence
            }

        return None
    
    def get_category_history(self):
        """
        Get all learned category mappings.
        
        Returns:
            list: List of all category mappings ordered by usage
        """
        self.connect()
        
        return self.cursor.execute('''
            SELECT * FROM expense_category_history
            ORDER BY usage_count DESC, last_used DESC
        ''').fetchall()
