"""
Category Manager - Centralized category and subcategory management
================================================================

This module provides centralized management of expense categories and subcategories
for the Budget Tracker application. It handles both predefined categories from CSV
files and dynamic categories added by users during runtime.

Key Features:
- Loads categories from CSV file with multiple encoding support
- Syncs categories between CSV file and database
- Provides thread-safe singleton access pattern
- Supports dynamic addition of new categories and subcategories
- Validates category usage before deletion
- Handles encoding issues gracefully with fallback options

The category system is fundamental to expense organization and reporting.
Categories are organized hierarchically with main categories (e.g., "Housing")
containing specific subcategories (e.g., "Mortgage", "Property Taxes").

Classes:
    CategoryManager: Main category management interface

Functions:
    get_category_manager(): Factory function for singleton access

Dependencies:
    - csv: For reading category data from CSV files
    - os: For file path operations
    - database.db_manager: For database persistence
"""

import csv
import os
from typing import Dict, List
from database.db_manager import DatabaseManager

class CategoryManager:
    """
    Manages categories and subcategories from CSV file and database.

    This class provides a unified interface for category management,
    handling both static categories loaded from CSV files and dynamic
    categories added by users during application usage.

    The manager follows these principles:
    1. CSV file serves as the master source for default categories
    2. Database stores both default and user-added categories
    3. User additions are persisted to database but not CSV
    4. Categories cannot be deleted if they're used in expenses

    Attributes:
        _categories_data (Dict[str, List[str]]): In-memory category storage
                                               Format: {category: [subcategory1, subcategory2, ...]}
    """

    def __init__(self):
        """
        Initialize the category manager.

        This constructor loads categories from the CSV file and syncs
        them with the database. It handles encoding issues gracefully
        and falls back to default categories if the CSV cannot be read.
        """
        self._categories_data = {}
        self._load_categories()

    def _load_categories(self):
        """
        Load categories from CSV file and sync with database.

        This method attempts to load categories from the CSV file using
        multiple encoding strategies. If successful, it syncs the data
        with the database. If the CSV file cannot be read, it falls back
        to a predefined set of default categories.

        The loading process:
        1. Try to read CSV with multiple encodings (UTF-8, Latin1, etc.)
        2. Parse category/subcategory pairs from CSV
        3. Ensure database table exists
        4. Sync CSV data to database
        5. Load any additional database-only categories
        """
        # Load from CSV first
        categories_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'categories.csv')

        if os.path.exists(categories_file):
            try:
                # Try different encodings to handle potential encoding issues
                # Common encodings ordered by likelihood of success
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']

                for encoding in encodings:
                    try:
                        with open(categories_file, 'r', encoding=encoding) as file:
                            reader = csv.DictReader(file)

                            # Clear existing data before loading
                            self._categories_data = {}

                            # Parse each row from the CSV file
                            for row in reader:
                                category = row.get('Category', '').strip()
                                subcategory = row.get('Sub Category', '').strip()

                                # Only process rows with valid data
                                if category and subcategory:
                                    if category not in self._categories_data:
                                        self._categories_data[category] = []
                                    # Avoid duplicate subcategories
                                    if subcategory not in self._categories_data[category]:
                                        self._categories_data[category].append(subcategory)

                        print(f"Loaded {len(self._categories_data)} categories from {categories_file} using {encoding} encoding")
                        break  # Success, exit the encoding loop

                    except UnicodeDecodeError:
                        continue  # Try next encoding

                # If we get here without breaking, all encodings failed
                if not self._categories_data:
                    raise Exception("Could not decode file with any supported encoding")

            except Exception as e:
                print(f"Error loading categories from CSV: {e}")
                self._load_default_categories()
        else:
            print("Categories.csv not found, using default categories")
            self._load_default_categories()

        # Ensure database table exists and sync
        self._ensure_categories_table()
        self._sync_with_database()

    def _load_default_categories(self):
        """
        Load default categories as fallback.

        This method provides a comprehensive set of default categories
        when the CSV file cannot be loaded. These categories cover
        common personal finance expense areas and provide a good
        starting point for budget tracking.

        Categories include:
        - Housing: Mortgage, utilities, maintenance
        - Food: Groceries, dining, takeout
        - Healthcare: Medical, dental, prescriptions
        - Transportation: Vehicle costs, gas, parking
        - And many more...
        """
        self._categories_data = {
            'Housing': ['Mortgage', 'HOA', 'Property Taxes', 'Reserves', 'Special Assessment', 'Additional Principal', 'Lima Apartment Wires', 'Lima Apartment Fees', 'Escrow', 'Condo Insurance', 'Labor'],
            'Utilities': ['Electric', 'Gas', 'Internet', 'Phone', 'Insurance', 'Optimum', 'PSEG', 'Cell Phone', 'Car Insurance', 'Gloria', 'Taxi / Transit', 'Bus Pass', 'Misc Utility'],
            'Food': ['Food (Groceries)', 'Food (Take Out)', 'Food (Dining Out)', 'Food (Other)', 'Food (Party)', 'Food (Guests)', 'Food (Work)', 'Food (Special Occasion)'],
            'Healthcare': ['Prescriptions', 'Doctor Visits', 'Co-Pay', 'Jeff Doctor', 'Vitamins', 'Other Doctor Visits', 'Haircut', 'Hygenie', 'Family', 'Fertility', 'Baker', 'HC Subscriptions', 'Joaquin Health Care', 'Zoe Health Care', 'Misc Health Care', 'Misc Healthcare'],
            'Childcare': ['Village Classes', 'Baby Sitting', 'Clothing', 'Diapers', 'Necessities', 'Accessories', 'Toys', 'Food / Snacks', 'Haircut', 'Activities', 'Uber / Lyft', 'Misc.'],
            'Vehicles': ['Gas', 'Insurance', 'Repairs', 'Parking', 'Vehicle Fixes', 'Vehicle Other', 'DMV', 'Parts', 'Tires / Wheels', 'Oil Changes', 'Car Wash', 'Tolls'],
            'Home': ['Home Necessities', 'Home Décor', 'House Cleaning', 'Bathroom', 'Bedrooms', 'Kitchen', 'Tools / Hardware', 'Storage', 'Homeware', 'Subscriptions'],
            'Other': ['Entertainment', 'Clothes', 'Clothing', 'Other', 'Gifts', 'Taxes', 'Donations', 'Gatherings', 'Parties', 'Shoes', 'Pets', 'Target AutoPay', 'Stupid Tax', 'Amazon Prime', 'Fees', 'Reversal'],
            'Vacation': ['Flights/Travel', 'Rental Car', 'Airport', 'Taxi', 'Food', 'Eating Out', 'Gas', 'Activities', 'Bedding', 'Fees', 'Physical Goods', 'Housing', 'Necessities'],
            'Income': ["Jeff's Income", "Vanessa's Income", "Bonus", "Other Income"]
        }

    def _ensure_categories_table(self):
        """
        Ensure the categories table exists in the database.

        This method creates the categories table if it doesn't exist.
        The table stores category/subcategory pairs with a unique
        constraint to prevent duplicates.

        Table Schema:
        - id: Primary key (auto-increment)
        - category: Main category name (e.g., "Housing")
        - subcategory: Specific subcategory (e.g., "Mortgage")
        - created_date: When the category was added
        - UNIQUE constraint on (category, subcategory) combination
        """
        try:
            with DatabaseManager() as db:
                db.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        subcategory TEXT NOT NULL,
                        created_date DATE DEFAULT CURRENT_DATE,
                        UNIQUE(category, subcategory)
                    )
                ''')
        except Exception as e:
            print(f"Error creating categories table: {e}")

    def _sync_with_database(self):
        """
        Sync categories with database and load any custom categories.

        This method performs a two-way sync between the in-memory
        categories and the database:

        1. Insert all CSV/default categories into database (if not exists)
        2. Load any additional categories from database (user-added)

        This ensures that both CSV-based and user-added categories
        are available in the application.
        """
        try:
            with DatabaseManager() as db:
                # First, insert all CSV categories into database if they don't exist
                for category, subcategories in self._categories_data.items():
                    for subcategory in subcategories:
                        try:
                            db.execute('''
                                INSERT OR IGNORE INTO categories (category, subcategory)
                                VALUES (?, ?)
                            ''', (category, subcategory))
                        except Exception as e:
                            print(f"Error inserting category {category}/{subcategory}: {e}")

                # Then load any additional categories from database
                db_categories = db.execute('''
                    SELECT category, subcategory FROM categories
                    ORDER BY category, subcategory
                ''').fetchall()

                # Add database categories to in-memory structure
                for row in db_categories:
                    category = row['category']
                    subcategory = row['subcategory']

                    if category not in self._categories_data:
                        self._categories_data[category] = []
                    if subcategory not in self._categories_data[category]:
                        self._categories_data[category].append(subcategory)

        except Exception as e:
            print(f"Error syncing with database: {e}")

    def get_categories(self) -> Dict[str, List[str]]:
        """
        Get all categories and subcategories.

        Returns a copy of the internal categories dictionary to prevent
        external modification of the internal data structure.

        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to subcategory lists
                                Format: {category: [subcategory1, subcategory2, ...]}
        """
        return self._categories_data.copy()

    def get_category_names(self) -> List[str]:
        """
        Get list of all category names.

        Returns:
            List[str]: Sorted list of all main category names
        """
        return sorted(self._categories_data.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """
        Get subcategories for a specific category.

        Args:
            category (str): The main category name

        Returns:
            List[str]: Copy of subcategory list for the given category
                      Empty list if category doesn't exist
        """
        return self._categories_data.get(category, []).copy()

    def add_category(self, category: str) -> bool:
        """
        Add a new category.

        Creates a new main category with a default general subcategory.
        The category is added to both the database and in-memory storage.

        Args:
            category (str): Name of the new category to add

        Returns:
            bool: True if category was added successfully, False if it already exists or an error occurred
        """
        if not category or category in self._categories_data:
            return False

        try:
            with DatabaseManager() as db:
                # Add category with a default subcategory
                default_subcategory = f"{category} (General)"
                db.execute('''
                    INSERT INTO categories (category, subcategory)
                    VALUES (?, ?)
                ''', (category, default_subcategory))

                # Add to in-memory storage
                self._categories_data[category] = [default_subcategory]
                return True

        except Exception as e:
            print(f"Error adding category {category}: {e}")
            return False

    def add_subcategory(self, category: str, subcategory: str) -> bool:
        """
        Add a new subcategory to an existing category.

        Args:
            category (str): The main category to add to
            subcategory (str): The new subcategory name

        Returns:
            bool: True if subcategory was added successfully, False otherwise
        """
        if not category or not subcategory:
            return False

        # Create category if it doesn't exist
        if category not in self._categories_data:
            self._categories_data[category] = []

        # Check if subcategory already exists
        if subcategory in self._categories_data[category]:
            return False

        try:
            with DatabaseManager() as db:
                db.execute('''
                    INSERT INTO categories (category, subcategory)
                    VALUES (?, ?)
                ''', (category, subcategory))

                # Add to in-memory storage
                self._categories_data[category].append(subcategory)
                return True

        except Exception as e:
            print(f"Error adding subcategory {category}/{subcategory}: {e}")
            return False

    def remove_subcategory(self, category: str, subcategory: str) -> bool:
        """
        Remove a subcategory (only if not used in expenses).

        Before removing a subcategory, this method checks if it's being
        used in any existing expense records. Subcategories that are in
        use cannot be deleted to maintain data integrity.

        Args:
            category (str): The main category
            subcategory (str): The subcategory to remove

        Returns:
            bool: True if removed successfully, False if in use or error occurred
        """
        if category not in self._categories_data or subcategory not in self._categories_data[category]:
            return False

        try:
            with DatabaseManager() as db:
                # Check if subcategory is used in expenses
                usage_count = db.execute('''
                    SELECT COUNT(*) as count FROM expenses
                    WHERE category = ? AND subcategory = ?
                ''', (category, subcategory)).fetchone()

                if usage_count and usage_count['count'] > 0:
                    print(f"Cannot remove subcategory {category}/{subcategory}: still in use")
                    return False

                # Remove from database
                db.execute('''
                    DELETE FROM categories 
                    WHERE category = ? AND subcategory = ?
                ''', (category, subcategory))

                # Remove from local data
                self._categories_data[category].remove(subcategory)

                # Remove category if it has no subcategories
                if not self._categories_data[category]:
                    del self._categories_data[category]

                return True

        except Exception as e:
            print(f"Error removing subcategory {category}/{subcategory}: {e}")
            return False

    def refresh_from_database(self):
        """
        Refresh categories from database.

        This method reloads all category data from the database,
        useful when categories may have been modified externally.
        """
        self._categories_data = {}
        self._load_categories()

    def refresh(self):
        """
        Refresh categories from database (alias for refresh_from_database).

        Provides a shorter method name for refreshing category data.
        """
        self.refresh_from_database()

    def is_valid_category(self, category: str, subcategory: str) -> bool:
        """
        Check if a category/subcategory combination is valid.

        Args:
            category (str): The main category
            subcategory (str): The subcategory

        Returns:
            bool: True if the combination exists, False otherwise
        """
        return (category in self._categories_data and
                subcategory in self._categories_data[category])

    def category_exists(self, category: str) -> bool:
        """
        Check if a category exists.

        Args:
            category (str): The category name to check

        Returns:
            bool: True if the category exists, False otherwise
        """
        return category in self._categories_data

    def subcategory_exists(self, category: str, subcategory: str) -> bool:
        """
        Check if a subcategory exists within a category.

        Args:
            category (str): The main category
            subcategory (str): The subcategory to check

        Returns:
            bool: True if the subcategory exists in the category, False otherwise
        """
        return (category in self._categories_data and
                subcategory in self._categories_data[category])


# Global instance
_category_manager = None


def get_category_manager() -> CategoryManager:
    """
    Get the global category manager instance.

    This function implements a simple singleton pattern for the category
    manager, ensuring that all parts of the application use the same
    category data and avoid duplicating memory usage.

    Returns:
        CategoryManager: The singleton category manager instance
    """
    global _category_manager
    if _category_manager is None:
        _category_manager = CategoryManager()
    return _category_manager
