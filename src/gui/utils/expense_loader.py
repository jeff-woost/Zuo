"""
Expense Loader Utility for Budget Tracker
========================================

This module provides comprehensive file loading capabilities for importing expense
data from various sources into the Budget Tracker application. It handles both
CSV files from credit card statements and TXT files with manual entries.

Key Features:
- Supports multiple file formats (CSV, TXT)
- Intelligent category mapping and auto-assignment
- Handles various date formats and currency representations
- Provides data validation and error reporting
- Integrates with the centralized category management system
- Supports bulk import operations with preview functionality

The loader uses pattern matching and keyword detection to automatically assign
appropriate categories to imported expenses, reducing manual categorization work.

Classes:
    ExpenseLoader: Main utility class for loading and processing expense files

Dependencies:
    - csv: For reading CSV files from financial institutions
    - datetime: For date parsing and validation
    - re: For pattern matching and text processing
    - database.category_manager: For category validation and assignment
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re
from src.database.category_manager import get_category_manager
from src.config import get_user_names

class ExpenseLoader:
    """
    Utility class for loading expenses from various file formats.

    This class provides comprehensive functionality for importing expense data
    from CSV files (typically from credit card statements) and TXT files
    (manual entry format). It includes intelligent category assignment,
    data validation, and error handling.

    Features:
    - Auto-detection of file formats and structures
    - Intelligent category mapping based on merchant names
    - Support for multiple date and currency formats
    - Comprehensive error reporting and validation
    - Integration with category management system

    Attributes:
        category_manager: Reference to the centralized category manager
        categories_data: Current category/subcategory mappings
        category_mappings: Predefined merchant-to-category mappings
    """

    def __init__(self):
        """
        Initialize the expense loader with category management integration.

        This constructor sets up the category manager connection and
        initializes the predefined merchant-to-category mappings that
        help automatically categorize imported expenses.
        """
        # Use centralized category manager for consistent categorization
        self.category_manager = get_category_manager()
        self.categories_data = self.category_manager.get_categories()

        # Enhanced category mappings using correct categories from system
        # These mappings help automatically assign categories based on merchant names
        self.category_mappings = {
            # Healthcare and pharmacy
            'WALGREENS': ('Healthcare', 'Prescriptions'),
            'CVS': ('Healthcare', 'Prescriptions'),
            'RITE AID': ('Healthcare', 'Prescriptions'),
            'PHARMACY': ('Healthcare', 'Prescriptions'),
            'DOCTOR': ('Healthcare', 'Doctor Visits'),
            'MEDICAL': ('Healthcare', 'Doctor Visits'),
            'DENTAL': ('Healthcare', 'Dental'),

            # Technology and entertainment
            'APPLE.COM': ('Entertainment', 'Gaming'),
            'AMAZON': ('Miscellaneous', 'Other'),
            'NETFLIX': ('Entertainment', 'Streaming Services'),
            'SPOTIFY': ('Entertainment', 'Streaming Services'),
            'HULU': ('Entertainment', 'Streaming Services'),

            # Retail stores
            'TARGET': ('Miscellaneous', 'Other'),
            'WALMART': ('Miscellaneous', 'Other'),
            'COSTCO': ('Miscellaneous', 'Other'),
            'EBAY': ('Miscellaneous', 'Other'),

            # Grocery stores
            'WHOLEFDS': ('Food & Dining', 'Groceries'),
            'WHOLE FOODS': ('Food & Dining', 'Groceries'),
            'TRADER JOE': ('Food & Dining', 'Groceries'),
            'SAFEWAY': ('Food & Dining', 'Groceries'),
            'KROGER': ('Food & Dining', 'Groceries'),
            'GROCERY': ('Food & Dining', 'Groceries'),
            'SUPERMARKET': ('Food & Dining', 'Groceries'),

            # Restaurants and dining
            'RESTAURANT': ('Food & Dining', 'Restaurants'),
            'MCDONALD': ('Food & Dining', 'Restaurants'),
            'BURGER': ('Food & Dining', 'Restaurants'),
            'PIZZA': ('Food & Dining', 'Restaurants'),
            'STARBUCKS': ('Food & Dining', 'Coffee Shops'),
            'DUNKIN': ('Food & Dining', 'Coffee Shops'),

            # Gas stations and automotive
            'SHELL': ('Transportation', 'Gas/Fuel'),
            'EXXON': ('Transportation', 'Gas/Fuel'),
            'BP': ('Transportation', 'Gas/Fuel'),
            'MOBIL': ('Transportation', 'Gas/Fuel'),
            'CHEVRON': ('Transportation', 'Gas/Fuel'),
            'GAS STATION': ('Transportation', 'Gas/Fuel'),
            'AUTO REPAIR': ('Transportation', 'Repairs'),
            'JIFFY LUBE': ('Transportation', 'Oil Changes'),

            # Utilities and services
            'ELECTRIC': ('Utilities', 'Electric'),
            'GAS COMPANY': ('Utilities', 'Gas'),
            'INTERNET': ('Utilities', 'Internet'),
            'PHONE': ('Utilities', 'Phone'),
            'CELL PHONE': ('Utilities', 'Cell Phone'),
            'INSURANCE': ('Insurance', 'Life Insurance'),

            # Home improvement and supplies
            'HOME DEPOT': ('Home & Garden', 'Tools/Hardware'),
            'LOWES': ('Home & Garden', 'Tools/Hardware'),
            'HARDWARE': ('Home & Garden', 'Tools/Hardware'),
            'FURNITURE': ('Home & Garden', 'Home Décor'),
            'IKEA': ('Home & Garden', 'Home Décor'),

            # Travel and transportation
            'AIRLINE': ('Vacation & Travel', 'Flights/Travel'),
            'HOTEL': ('Vacation & Travel', 'Lodging'),
            'RENTAL CAR': ('Vacation & Travel', 'Rental Car'),
            'UBER': ('Transportation', 'Rideshare'),
            'LYFT': ('Transportation', 'Rideshare'),
            'TAXI': ('Transportation', 'Rideshare'),
            'PARKING': ('Transportation', 'Parking'),
            'TOLL': ('Transportation', 'Tolls'),

            # General categories
            'ATM': ('Miscellaneous', 'Fees'),
            'BANK FEE': ('Other', 'Fees'),
            'INTEREST': ('Other', 'Fees'),
            'LATE FEE': ('Other', 'Stupid Tax'),
        }

    def load_csv_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Load and parse expenses from a CSV file.

        This method handles CSV files typically exported from credit card
        statements or banking systems. It attempts to auto-detect the format
        and parse the data accordingly.

        Args:
            file_path (str): Path to the CSV file to load

        Returns:
            Tuple[List[Dict], List[str]]: A tuple containing:
                - List of parsed expense dictionaries
                - List of error messages encountered during parsing

        Supported CSV formats:
        - Credit card statements (date, description, amount)
        - Bank exports (various column arrangements)
        - Manual CSV files with custom formats
        """
        expenses = []
        errors = []

        try:
            # Try different encodings for CSV files
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        # Detect delimiter by examining first few lines
                        sample = file.read(1024)
                        file.seek(0)

                        # Common delimiters in order of preference
                        delimiters = [',', '\t', ';', '|']
                        delimiter = ','

                        for delim in delimiters:
                            if sample.count(delim) > sample.count(delimiter):
                                delimiter = delim

                        # Read CSV with detected delimiter
                        reader = csv.DictReader(file, delimiter=delimiter)

                        # Process each row in the CSV
                        for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                            try:
                                expense = self._parse_csv_row(row, row_num)
                                if expense:
                                    expenses.append(expense)
                            except Exception as e:
                                errors.append(f"Row {row_num}: {str(e)}")

                        break  # Success - exit encoding loop

                except UnicodeDecodeError:
                    continue  # Try next encoding

        except Exception as e:
            errors.append(f"Failed to read CSV file: {str(e)}")

        return expenses, errors

    def _parse_csv_row(self, row: Dict, row_num: int) -> Optional[Dict]:
        """
        Parse a single CSV row into an expense dictionary.

        This method handles the conversion of CSV row data into a standardized
        expense format. It attempts to map common column names to expense fields
        and validates the data.

        Args:
            row (Dict): Dictionary representing a CSV row
            row_num (int): Row number for error reporting

        Returns:
            Optional[Dict]: Parsed expense dictionary or None if invalid

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Common column name mappings for different CSV formats
        date_columns = ['date', 'Date', 'Transaction Date', 'Posted Date', 'trans_date']
        description_columns = ['description', 'Description', 'Merchant', 'memo', 'Transaction']
        amount_columns = ['amount', 'Amount', 'Debit', 'Credit', 'Transaction Amount']

        # Extract date
        date_str = None
        for col in date_columns:
            if col in row and row[col]:
                date_str = row[col].strip()
                break

        if not date_str:
            raise ValueError("No date column found")

        # Parse date using multiple formats
        parsed_date = self._parse_date(date_str)
        if not parsed_date:
            raise ValueError(f"Could not parse date: {date_str}")

        # Extract description
        description = None
        for col in description_columns:
            if col in row and row[col]:
                description = row[col].strip()
                break

        if not description:
            raise ValueError("No description found")

        # Extract amount
        amount_str = None
        for col in amount_columns:
            if col in row and row[col]:
                amount_str = row[col].strip()
                break

        if not amount_str:
            raise ValueError("No amount found")

        # Parse amount
        amount = self._parse_amount(amount_str)
        if amount == 0:
            return None  # Skip zero amounts

        # Assign category based on description
        category, subcategory = self._assign_category(description)
        
        # Get default user name
        user_a_name, _ = get_user_names()

        return {
            'date': parsed_date.strftime('%Y-%m-%d'),
            'person': user_a_name,  # Default person - can be changed in preview
            'amount': abs(amount),  # Always positive for expenses
            'description': description,
            'category': category,
            'subcategory': subcategory,
            'payment_method': 'Credit Card'  # Default payment method
        }

    def load_txt_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Load and parse expenses from a TXT file.

        This method handles text files with manual expense entries.
        It supports various text formats and attempts to parse
        structured data from free-form text.

        Args:
            file_path (str): Path to the TXT file to load

        Returns:
            Tuple[List[Dict], List[str]]: A tuple containing:
                - List of parsed expense dictionaries
                - List of error messages encountered during parsing

        Supported TXT formats:
        - Tab-delimited lines
        - Comma-separated lines
        - Structured text with keywords
        """
        expenses = []
        errors = []

        try:
            # Try different encodings for text files
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        lines = file.readlines()

                        for line_num, line in enumerate(lines, start=1):
                            line = line.strip()
                            if not line or line.startswith('#'):  # Skip empty lines and comments
                                continue

                            try:
                                expense = self._parse_txt_line(line, line_num)
                                if expense:
                                    expenses.append(expense)
                            except Exception as e:
                                errors.append(f"Line {line_num}: {str(e)}")

                        break  # Success - exit encoding loop

                except UnicodeDecodeError:
                    continue  # Try next encoding

        except Exception as e:
            errors.append(f"Failed to read TXT file: {str(e)}")

        return expenses, errors

    def _infer_year_for_date(self, month: int) -> int:
        """
        Intelligently infer the year for a date based on context.

        When importing expenses with short dates (MM/DD format), we need to
        determine the correct year. If we're in January and working with
        expenses from November or December, those are likely from the
        previous year.

        Args:
            month (int): The month number (1-12)

        Returns:
            int: The inferred year
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # If we're in January or February and the expense is from a late month
        # (October, November, December), assume it's from the previous year
        if current_month <= 2 and month >= 10:
            return current_year - 1

        # If the expense month is significantly in the future (more than 2 months ahead),
        # it's probably from the previous year
        if month > current_month + 2:
            return current_year - 1

        return current_year

    def _parse_txt_line(self, line: str, line_num: int) -> Optional[Dict]:
        """
        Parse a single text line into an expense dictionary.

        This method handles various text line formats and attempts to
        extract expense information from structured text entries.

        Args:
            line (str): Text line to parse
            line_num (int): Line number for error reporting

        Returns:
            Optional[Dict]: Parsed expense dictionary or None if invalid

        Supported formats:
        - "Date|Amount|Description"
        - "Date,Amount,Description"
        - "Date\tAmount\tDescription"
        - "MM/DD/YYYY description amount" (e.g., "11/01/2025 the village 1406.26")
        - "MM/DD description amount" (e.g., "09/01 the village 1406.26")
        """
        # First, try the format with full year: "MM/DD/YYYY description amount"
        # Pattern: starts with date (MM/DD/YYYY), ends with amount, everything in between is description
        full_date_pattern = r'^(\d{1,2}/\d{1,2}/\d{4})\s+(.+?)\s+([\d.]+)$'
        match = re.match(full_date_pattern, line)

        if match:
            date_str = match.group(1)
            description = match.group(2).strip()
            amount_str = match.group(3)
            # Get default user name
            user_a_name, _ = get_user_names()
            person = user_a_name  # Default person

            # Parse date directly (already has year)
            parsed_date = self._parse_date(date_str)
            if not parsed_date:
                raise ValueError(f"Could not parse date: {date_str}")

            # Parse amount
            amount = self._parse_amount(amount_str)
            if amount == 0:
                return None  # Skip zero amounts

            # Assign category
            category, subcategory = self._assign_category(description)

            return {
                'date': parsed_date.strftime('%Y-%m-%d'),
                'person': person,
                'amount': abs(amount),
                'description': description,
                'category': category,
                'subcategory': subcategory,
                'payment_method': 'Credit Card'
            }

        # Try the simple format without year: "MM/DD description amount"
        # Pattern: starts with date (MM/DD), ends with amount, everything in between is description
        simple_pattern = r'^(\d{1,2}/\d{1,2})\s+(.+?)\s+([\d.]+)$'
        match = re.match(simple_pattern, line)

        if match:
            date_str = match.group(1)
            description = match.group(2).strip()
            amount_str = match.group(3)
            # Get default user name
            user_a_name, _ = get_user_names()
            person = user_a_name  # Default person

            # Extract month to intelligently infer the year
            month_str = date_str.split('/')[0]
            try:
                month = int(month_str)
            except ValueError:
                month = datetime.now().month

            # Intelligently infer the year based on context
            inferred_year = self._infer_year_for_date(month)
            date_str_with_year = f"{date_str}/{inferred_year}"

            # Parse date
            parsed_date = self._parse_date(date_str_with_year)
            if not parsed_date:
                raise ValueError(f"Could not parse date: {date_str}")

            # Parse amount
            amount = self._parse_amount(amount_str)
            if amount == 0:
                return None  # Skip zero amounts

            # Assign category
            category, subcategory = self._assign_category(description)

            return {
                'date': parsed_date.strftime('%Y-%m-%d'),
                'person': person,
                'amount': abs(amount),
                'description': description,
                'category': category,
                'subcategory': subcategory,
                'payment_method': 'Credit Card'
            }

        # Try different separators for delimited format
        separators = ['|', '\t', ',', ';']
        parts = None

        for sep in separators:
            test_parts = line.split(sep)
            if len(test_parts) >= 3:  # Need at least date, amount, description
                parts = [part.strip() for part in test_parts]
                break

        if not parts or len(parts) < 3:
            raise ValueError(f"Could not parse line format: {line}")

        # Extract components
        date_str = parts[0]
        amount_str = parts[1]
        description = parts[2]
        
        # Get user names
        user_a_name, user_b_name = get_user_names()

        # Optional person in 4th column
        person = parts[3] if len(parts) > 3 else user_a_name

        # Parse date
        parsed_date = self._parse_date(date_str)
        if not parsed_date:
            raise ValueError(f"Could not parse date: {date_str}")

        # Parse amount
        amount = self._parse_amount(amount_str)
        if amount == 0:
            return None  # Skip zero amounts

        # Assign category
        category, subcategory = self._assign_category(description)
        
        # Validate person - use user_a_name as default if not valid
        valid_persons = [user_a_name, user_b_name]
        if person not in valid_persons:
            person = user_a_name

        return {
            'date': parsed_date.strftime('%Y-%m-%d'),
            'person': person,
            'amount': abs(amount),
            'description': description,
            'category': category,
            'subcategory': subcategory,
            'payment_method': 'Credit Card'
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string using multiple format attempts.

        This method tries various common date formats to parse
        date strings from different file sources.

        Args:
            date_str (str): Date string to parse

        Returns:
            Optional[datetime]: Parsed date or None if parsing fails
        """
        if not date_str:
            return None

        # List of date formats to try
        date_formats = [
            '%Y-%m-%d',      # 2024-08-15
            '%m/%d/%Y',      # 08/15/2024
            '%m/%d/%y',      # 08/15/24
            '%d/%m/%Y',      # 15/08/2024
            '%Y/%m/%d',      # 2024/08/15
            '%m-%d-%Y',      # 08-15-2024
            '%d-%m-%Y',      # 15-08-2024
            '%B %d, %Y',     # August 15, 2024
            '%b %d, %Y',     # Aug 15, 2024
            '%d %B %Y',      # 15 August 2024
            '%d %b %Y',      # 15 Aug 2024
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue

        return None

    def _parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string into float value.

        This method handles various currency formats and extracts
        the numeric value for monetary amounts.

        Args:
            amount_str (str): Amount string to parse

        Returns:
            float: Parsed amount value
        """
        if not amount_str:
            return 0.0

        # Remove currency symbols, commas, and spaces
        cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())

        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def _assign_category(self, description: str) -> Tuple[str, str]:
        """
        Assign category and subcategory based on expense description.

        This method uses keyword matching and predefined mappings to
        automatically assign appropriate categories to expenses based
        on merchant names and description text.

        Args:
            description (str): Expense description to analyze

        Returns:
            Tuple[str, str]: Assigned (category, subcategory) pair
        """
        if not description:
            return ('Other', 'Other')

        # Convert to uppercase for case-insensitive matching
        desc_upper = description.upper()

        # Check direct mappings first
        for keyword, (category, subcategory) in self.category_mappings.items():
            if keyword.upper() in desc_upper:
                return (category, subcategory)

        # Fallback pattern matching for common scenarios
        if any(word in desc_upper for word in ['GROCERY', 'FOOD', 'MARKET']):
            return ('Food', 'Food (Groceries)')
        elif any(word in desc_upper for word in ['GAS', 'FUEL', 'STATION']):
            return ('Vehicles', 'Gas')
        elif any(word in desc_upper for word in ['RESTAURANT', 'CAFE', 'DINER']):
            return ('Food', 'Food (Dining Out)')
        elif any(word in desc_upper for word in ['PHARMACY', 'DRUG', 'MEDICAL']):
            return ('Healthcare', 'Misc Healthcare')
        elif any(word in desc_upper for word in ['INTERNET', 'CABLE', 'PHONE']):
            return ('Utilities', 'Internet')
        elif any(word in desc_upper for word in ['INSURANCE']):
            return ('Utilities', 'Insurance')

        # Default category for unmatched items
        return ('Other', 'Other')

    def validate_expenses(self, expenses: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate parsed expenses and filter out invalid entries.

        This method performs comprehensive validation on parsed expense
        data to ensure data quality and consistency.

        Args:
            expenses (List[Dict]): List of expense dictionaries to validate

        Returns:
            Tuple[List[Dict], List[str]]: A tuple containing:
                - List of valid expense dictionaries
                - List of validation error messages
        """
        valid_expenses = []
        errors = []
        
        # Get valid user names
        user_a_name, user_b_name = get_user_names()
        valid_persons = [user_a_name, user_b_name]

        for i, expense in enumerate(expenses):
            expense_errors = []

            # Validate required fields
            if not expense.get('date'):
                expense_errors.append("Missing date")
            if not expense.get('description'):
                expense_errors.append("Missing description")
            if not expense.get('amount') or expense['amount'] <= 0:
                expense_errors.append("Invalid amount")
            if not expense.get('person') or expense['person'] not in valid_persons:
                expense_errors.append("Invalid person")
            if not expense.get('category'):
                expense_errors.append("Missing category")
            if not expense.get('subcategory'):
                expense_errors.append("Missing subcategory")

            # Validate category exists
            if expense.get('category') and expense.get('subcategory'):
                if not self.category_manager.is_valid_category(
                    expense['category'], expense['subcategory']
                ):
                    expense_errors.append(f"Invalid category/subcategory: {expense['category']}/{expense['subcategory']}")

            if expense_errors:
                errors.append(f"Expense {i+1}: {', '.join(expense_errors)}")
            else:
                valid_expenses.append(expense)

        return valid_expenses, errors

    def get_available_categories(self) -> Dict[str, List[str]]:
        """
        Get available categories for import validation.

        Returns:
            Dict[str, List[str]]: Dictionary of categories and their subcategories
        """
        return self.categories_data.copy()
