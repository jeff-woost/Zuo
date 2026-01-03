"""
Database connection and initialization
"""

import sqlite3
from datetime import datetime

class DatabaseConnection:
    """Manages database connection and initialization"""
    
    def __init__(self, db_path='budget.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def init_database(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        # Create income table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                source TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                description TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create net worth table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS net_worth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                asset_type TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                value REAL NOT NULL,
                person TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create savings goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL UNIQUE,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                initial_amount REAL DEFAULT 0,
                target_date DATE,
                priority INTEGER DEFAULT 5,
                is_completed BOOLEAN DEFAULT 0,
                completion_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create savings allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                goal_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES savings_goals(id) ON DELETE CASCADE
            )
        ''')
        
        # Create budgets table for future use
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                amount REAL NOT NULL,
                month DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def execute(self, query, params=None):
        """Execute a query and return cursor"""
        cursor = self.conn.cursor()
        if params:
            return cursor.execute(query, params)
        return cursor.execute(query)
        
    def commit(self):
        """Commit current transaction"""
        self.conn.commit()
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()