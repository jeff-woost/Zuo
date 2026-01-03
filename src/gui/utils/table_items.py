"""
Custom Table Widget Items for Enhanced Data Display and Sorting
==============================================================

This module provides specialized QTableWidgetItem subclasses that enhance
table functionality in the Budget Tracker application. These custom items
provide proper sorting, formatting, and display for different data types
commonly used in financial applications.

Key Features:
- Numeric sorting for currency values (not alphabetic)
- Proper date sorting and formatting
- Consistent data type handling across tables
- Enhanced user experience with logical sorting behavior

The custom items ensure that financial data is displayed and sorted correctly,
which is crucial for accurate financial analysis and reporting.

Classes:
    CurrencyTableWidgetItem: For monetary values with proper numeric sorting
    DateTableWidgetItem: For date values with chronological sorting

Dependencies:
    - PyQt6.QtWidgets.QTableWidgetItem: Base table item class
    - PyQt6.QtCore.Qt: Core Qt constants and enums
    - re: Regular expressions for text parsing
    - datetime: Date parsing and manipulation
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt
import re
from datetime import datetime

class CurrencyTableWidgetItem(QTableWidgetItem):
    """
    Custom table widget item for currency values that sorts numerically.

    This class extends QTableWidgetItem to provide proper numeric sorting
    for currency values. Standard QTableWidgetItem sorts alphabetically,
    which would put "$1,000" before "$200". This class extracts the numeric
    value and sorts based on the actual monetary amount.

    Features:
    - Extracts numeric value from formatted currency strings
    - Handles various currency formats ($1,234.56, 1234.56, etc.)
    - Provides proper ascending/descending numeric sorting
    - Maintains original text formatting for display
    - Handles negative values correctly

    Example:
        item = CurrencyTableWidgetItem("$1,234.56")
        table.setItem(row, column, item)
        # Will sort as 1234.56, not alphabetically
    """

    def __init__(self, text):
        """
        Initialize currency table item with text and extracted numeric value.

        Args:
            text (str): Currency text to display (e.g., "$1,234.56")
        """
        super().__init__(text)
        # Extract numeric value from currency string for sorting
        self.numeric_value = self._extract_numeric_value(text)

    def _extract_numeric_value(self, text):
        """
        Extract numeric value from currency string like '$1,234.56'.

        This method removes currency symbols, commas, and spaces to
        extract the raw numeric value for sorting purposes.

        Args:
            text (str): Currency string to parse

        Returns:
            float: Numeric value extracted from the string

        Examples:
            "$1,234.56" -> 1234.56
            "($500.00)" -> -500.00
            "1,000" -> 1000.0
            "" -> 0.0
        """
        if not text:
            return 0.0

        # Convert to string to handle any input type
        text_str = str(text)

        # Check for parentheses indicating negative value (accounting format)
        is_negative = text_str.strip().startswith('(') and text_str.strip().endswith(')')

        # Remove currency symbols, commas, spaces, and parentheses
        cleaned = re.sub(r'[^\d.-]', '', text_str)

        try:
            value = float(cleaned) if cleaned else 0.0
            # Apply negative sign if parentheses were present
            return -value if is_negative else value
        except ValueError:
            # If parsing fails, return 0 for safe sorting
            return 0.0

    def __lt__(self, other):
        """
        Custom comparison for proper numeric sorting.

        This method overrides the default string comparison to use
        numeric values instead. This ensures currency values sort
        in the correct numerical order.

        Args:
            other (QTableWidgetItem): Item to compare against

        Returns:
            bool: True if this item's value is less than other's value
        """
        if isinstance(other, CurrencyTableWidgetItem):
            # Both items are currency items - compare numeric values
            return self.numeric_value < other.numeric_value
        else:
            # Fallback to default string comparison
            return super().__lt__(other)


class DateTableWidgetItem(QTableWidgetItem):
    """
    Custom table widget item for date values that sorts chronologically.

    This class extends QTableWidgetItem to provide proper chronological
    sorting for date values. Standard QTableWidgetItem sorts alphabetically,
    which doesn't work correctly for dates in various formats.

    Features:
    - Parses various date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
    - Sorts chronologically (oldest to newest or vice versa)
    - Handles invalid dates gracefully
    - Maintains original text formatting for display
    - Supports empty/null date values

    Example:
        item = DateTableWidgetItem("2024-08-15")
        table.setItem(row, column, item)
        # Will sort chronologically, not alphabetically
    """

    def __init__(self, text):
        """
        Initialize date table item with text and parsed date value.

        Args:
            text (str): Date text to display (e.g., "2024-08-15")
        """
        super().__init__(text)
        # Parse date from text for sorting
        self.date_value = self._parse_date(text)

    def _parse_date(self, text):
        """
        Parse date from text string using multiple format attempts.

        This method tries to parse the date using common formats.
        If parsing fails, it returns None, which will sort to the end.

        Args:
            text (str): Date string to parse

        Returns:
            datetime: Parsed date object, or None if parsing fails

        Supported formats:
            - YYYY-MM-DD (ISO format)
            - MM/DD/YYYY (US format)
            - DD/MM/YYYY (European format)
            - YYYY/MM/DD
        """
        if not text or not str(text).strip():
            return None

        text_str = str(text).strip()

        # List of date formats to try, in order of preference
        date_formats = [
            '%Y-%m-%d',      # 2024-08-15 (ISO format - preferred)
            '%m/%d/%Y',      # 08/15/2024 (US format)
            '%d/%m/%Y',      # 15/08/2024 (European format)
            '%Y/%m/%d',      # 2024/08/15
            '%m-%d-%Y',      # 08-15-2024
            '%d-%m-%Y',      # 15-08-2024
        ]

        # Try each format until one works
        for date_format in date_formats:
            try:
                return datetime.strptime(text_str, date_format)
            except ValueError:
                continue

        # If no format worked, return None for safe sorting
        return None

    def __lt__(self, other):
        """
        Custom comparison for proper chronological sorting.

        This method overrides the default string comparison to use
        parsed date values instead. This ensures dates sort in
        chronological order.

        Args:
            other (QTableWidgetItem): Item to compare against

        Returns:
            bool: True if this item's date is earlier than other's date
        """
        if isinstance(other, DateTableWidgetItem):
            # Both items are date items - compare date values
            # Handle None values (invalid dates sort to end)
            if self.date_value is None and other.date_value is None:
                return False  # Equal
            elif self.date_value is None:
                return False  # This item sorts after valid dates
            elif other.date_value is None:
                return True   # Other item sorts after valid dates
            else:
                return self.date_value < other.date_value
        else:
            # Fallback to default string comparison
            return super().__lt__(other)
