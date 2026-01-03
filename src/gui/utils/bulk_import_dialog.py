"""
Bulk Import Preview Dialog for Expense Management
================================================

This module provides a sophisticated preview dialog for bulk importing expenses
from CSV and text files. It allows users to review, edit, and validate expense
data before committing it to the database, ensuring data quality and accuracy.

Key Features:
- Preview and edit imported data before saving
- Category validation and dynamic addition
- Custom sorting and filtering of import data
- Real-time validation feedback
- User-friendly import summary and statistics
- Support for multiple file formats (CSV, TXT)

The dialog serves as a crucial quality control step in the import process,
allowing users to catch and correct issues before they affect the database.

Classes:
    CustomComboBox: Enhanced combo box for adding new categories
    SortableTableWidget: Table widget with improved sorting capabilities
    BulkImportPreviewDialog: Main dialog for import preview and editing

Dependencies:
    - PyQt6: GUI framework components
    - database.category_manager: Category management system
    - typing: Type hints for better code documentation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QDialogButtonBox, QMessageBox, QCheckBox, QGroupBox,
    QInputDialog, QLineEdit, QWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict
from src.database.category_manager import get_category_manager

class CustomComboBox(QComboBox):
    """
    Custom ComboBox that allows adding new items dynamically.

    This enhanced combo box enables users to add new categories or subcategories
    directly from the import dialog by typing and pressing Enter. It integrates
    with the category manager to persist new items to the database.

    Features:
    - Editable combo box for custom input
    - Enter key support for adding new items
    - Automatic category/subcategory creation
    - Real-time feedback for successful additions
    - Integration with category management system

    Attributes:
        category_manager: Reference to the category management system
        is_subcategory (bool): Whether this combo handles subcategories
        category_combo: Reference to parent category combo (for subcategories)
    """

    def __init__(self, parent=None, category_manager=None, is_subcategory=False, category_combo=None):
        """
        Initialize the custom combo box with enhanced functionality.

        Args:
            parent: Parent widget
            category_manager: Category management system instance
            is_subcategory (bool): True if this combo handles subcategories
            category_combo: Parent category combo reference (for subcategories)
        """
        super().__init__(parent)
        self.category_manager = category_manager
        self.is_subcategory = is_subcategory
        self.category_combo = category_combo
        self.setEditable(True)

        # Connect Enter key press to add new item functionality
        self.lineEdit().returnPressed.connect(self.add_new_item)

        # Improve styling for better visibility and user experience
        self.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
                color: #2d3748;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #007bff;
                background-color: white;
                color: #2d3748;
            }
            QComboBox:focus {
                border-color: #007bff;
                background-color: white;
                color: #2d3748;
            }
            QComboBox:editable {
                background-color: white;
                color: #2d3748;
            }
            QComboBox:editable:focus {
                background-color: white;
                color: #2d3748;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2d3748;
                selection-background-color: #e3f2fd;
                selection-color: #1a202c;
                border: 1px solid #ccc;
                outline: none;
                show-decoration-selected: 1;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #2d3748;
                padding: 4px 8px;
                min-height: 20px;
                border: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f0f8ff;
                color: #1a202c;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e3f2fd;
                color: #1a202c;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #f8f9fa;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
                margin: 0px;
            }
        """)

    def add_new_item(self):
        """
        Add a new item when user presses Enter.

        This method handles adding new categories or subcategories to the
        system when the user types a new value and presses Enter. It
        validates the input and provides feedback to the user.
        """
        new_text = self.lineEdit().text().strip()
        if not new_text:
            return

        if self.is_subcategory and self.category_combo:
            # Adding new subcategory to existing category
            category = self.category_combo.currentText()
            if category and self.category_manager:
                if self.category_manager.add_subcategory(category, new_text):
                    self.addItem(new_text)
                    self.setCurrentText(new_text)
                    QMessageBox.information(self, "Success", f"Added new subcategory '{new_text}' to '{category}'")
                else:
                    QMessageBox.warning(self, "Error", f"Could not add subcategory '{new_text}' (may already exist)")
        else:
            # Adding new main category
            if self.category_manager and self.category_manager.add_category(new_text):
                self.addItem(new_text)
                self.setCurrentText(new_text)
                QMessageBox.information(self, "Success", f"Added new category '{new_text}'")
            else:
                QMessageBox.warning(self, "Error", f"Could not add category '{new_text}' (may already exist)")

class SortableTableWidget(QTableWidget):
    """
    Custom table widget with improved sorting for mixed data types.

    This enhanced table widget provides better sorting capabilities for
    import data that contains various data types (dates, currencies, text).
    It maintains the original data for proper sorting while supporting
    widget-based cells.

    Features:
    - Improved sorting algorithm for mixed data types
    - Original data preservation for accurate sorting
    - Support for widget-based table cells
    - Custom column-specific sorting logic
    - Better handling of empty/null values
    """

    def __init__(self, parent=None):
        """
        Initialize the sortable table widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Store original data for sorting with widgets
        self.original_data = []

    def set_original_data(self, data):
        """
        Store original data for proper sorting.

        This method stores the original data structure to enable proper
        sorting when table cells contain widgets rather than simple text.

        Args:
            data: List of dictionaries containing the original import data
        """
        self.original_data = data

    def sort_by_column(self, column, order):
        """
        Custom sorting that handles both widgets and text items.

        This method provides enhanced sorting that works correctly with
        tables containing widgets in cells, which standard sorting doesn't
        handle properly.

        Args:
            column (int): Column index to sort by
            order (Qt.SortOrder): Ascending or descending sort order
        """
        if not self.original_data:
            return

        # Get current state of all widgets before sorting
        current_data = []
        for row in range(self.rowCount()):
            row_data = self.original_data[row].copy() if row < len(self.original_data) else {}

            # Extract current widget values for accurate sorting
            # Import checkbox
            checkbox_widget = self.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    row_data['import_checked'] = checkbox.isChecked()

            # Person combo box
            person_combo = self.cellWidget(row, 2)
            if person_combo:
                row_data['person'] = person_combo.currentText()

            # Category combo box
            category_combo = self.cellWidget(row, 5)
            if category_combo:
                row_data['category'] = category_combo.currentText()

            # Subcategory combo box
            subcategory_combo = self.cellWidget(row, 6)
            if subcategory_combo:
                row_data['subcategory'] = subcategory_combo.currentText()

            # Payment method combo box
            payment_combo = self.cellWidget(row, 7)
            if payment_combo:
                row_data['payment_method'] = payment_combo.currentText()

            current_data.append(row_data)

        # Sort the data based on the specified column
        reverse = (order == Qt.SortOrder.DescendingOrder)

        # Column-specific sorting logic
        if column == 0:  # Import checkbox
            current_data.sort(key=lambda x: x.get('import_checked', True), reverse=reverse)
        elif column == 1:  # Date
            current_data.sort(key=lambda x: x.get('date', ''), reverse=reverse)
        elif column == 2:  # Person
            current_data.sort(key=lambda x: x.get('person', ''), reverse=reverse)
        elif column == 3:  # Amount (numeric sorting)
            current_data.sort(key=lambda x: x.get('amount', 0), reverse=reverse)
        elif column == 4:  # Description
            current_data.sort(key=lambda x: x.get('description', ''), reverse=reverse)
        elif column == 5:  # Category
            current_data.sort(key=lambda x: x.get('category', ''), reverse=reverse)
        elif column == 6:  # Subcategory
            current_data.sort(key=lambda x: x.get('subcategory', ''), reverse=reverse)
        elif column == 7:  # Payment Method
            current_data.sort(key=lambda x: x.get('payment_method', ''), reverse=reverse)

        # Update the original data order and repopulate table
        self.original_data = current_data
        self.parent().populate_table_with_data(current_data)

class BulkImportPreviewDialog(QDialog):
    """
    Dialog for previewing and editing bulk import data.

    This dialog provides a comprehensive interface for reviewing expense
    data before importing it into the database. Users can validate categories,
    edit individual entries, and control which items to import.

    Features:
    - Interactive preview table with editable cells
    - Category validation and dynamic addition
    - Import selection with checkboxes
    - Real-time import statistics
    - Column sorting and data validation
    - Integration with category management system

    The dialog ensures data quality by allowing users to review and correct
    any issues before the data is committed to the database.
    """

    def __init__(self, expenses: List[Dict], categories_data: Dict[str, List[str]], parent=None, default_person: str = None):
        """
        Initialize the bulk import preview dialog.

        Args:
            expenses: List of expense dictionaries to preview
            categories_data: Available categories and subcategories
            parent: Parent widget
            default_person: Default person to pre-populate for all expenses (Feature 1)
        """
        super().__init__(parent)
        self.expenses = expenses
        self.default_person = default_person  # Store default person for pre-population
        self.category_manager = get_category_manager()
        # Import database manager for category learning
        from database.db_manager import DatabaseManager
        self.db = DatabaseManager()
        # Refresh categories to get latest data
        self.categories_data = self.category_manager.get_categories()
        self.init_ui()
        self.populate_table()

    def init_ui(self):
        """
        Initialize the user interface.

        This method creates and configures all UI elements for the dialog,
        including the preview table, summary information, and control buttons.
        """
        self.setWindowTitle("Import Preview - Review Categories")
        self.setModal(True)
        # Increase dialog size for better visibility of import data
        self.resize(1400, 700)

        layout = QVBoxLayout()

        # Header section with title and instructions
        header_label = QLabel("Review and Edit Categories Before Import")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Detailed instructions for users
        instructions = QLabel(
            "📝 Review the automatically assigned categories below. "
            "Click column headers to sort data. "
            "Click on category or subcategory cells to change them. "
            "Type new categories/subcategories and press Enter to add them. "
            "Uncheck items you don't want to import."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 10px; font-size: 12px; background-color: #f8f9fa; border-radius: 5px; margin: 5px;")
        layout.addWidget(instructions)

        # Summary section with import statistics
        summary_group = QGroupBox("Import Summary")
        summary_layout = QHBoxLayout()

        self.total_label = QLabel(f"Total Items: {len(self.expenses)}")
        self.selected_label = QLabel(f"Selected: {len(self.expenses)}")
        self.amount_label = QLabel(f"Total Amount: ${sum(exp['amount'] for exp in self.expenses):,.2f}")

        # Style the summary labels for better visibility
        for label in [self.total_label, self.selected_label, self.amount_label]:
            label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px;")

        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.selected_label)
        summary_layout.addWidget(self.amount_label)
        summary_layout.addStretch()

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Main preview table with improved sorting
        self.table = SortableTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Import", "Date", "Person", "Amount", "Description",
            "Category", "Subcategory", "Payment Method"
        ])

        # Improve table appearance with better visibility
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: #f5f5f5;
                alternate-background-color: #ebebeb;
                selection-background-color: #e3f2fd;
                font-size: 12px;
                border: 1px solid #ddd;
                color: #2d3748;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #2d3748;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1a202c;
            }
            QTableWidget::item:hover {
                background-color: #f0f8ff;
                color: #1a202c;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 10px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background-color: #38663d;
            }
        """)

        # Set improved column widths for better visibility
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # Import checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)      # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)      # Person
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)      # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)    # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)      # Category
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)      # Subcategory
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)      # Payment Method

        # Optimized column widths for better user experience
        self.table.setColumnWidth(0, 70)   # Import - wider for checkbox
        self.table.setColumnWidth(1, 110)  # Date - wider to show full date
        self.table.setColumnWidth(2, 100)  # Person - wider to show full name
        self.table.setColumnWidth(3, 120)  # Amount - wider for larger amounts
        self.table.setColumnWidth(5, 150)  # Category - wider for full category names
        self.table.setColumnWidth(6, 180)  # Subcategory - wider for full subcategory names
        self.table.setColumnWidth(7, 130)  # Payment Method - wider

        # Set minimum row height for better visibility of dropdowns
        self.table.verticalHeader().setDefaultSectionSize(35)

        # Connect sorting signal for custom sorting behavior
        header.sortIndicatorChanged.connect(self.table.sort_by_column)

        layout.addWidget(self.table)

        # Bottom button section with various controls
        button_layout = QHBoxLayout()

        # Selection control buttons
        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        select_none_btn.clicked.connect(self.select_none)
        button_layout.addWidget(select_none_btn)

        # Add refresh categories button for dynamic category management
        refresh_btn = QPushButton("Refresh Categories")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_categories)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()

        # Main action buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Import Selected")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_table(self):
        """
        Populate the table with expense data.

        This method fills the preview table with the imported expense data,
        creating interactive controls for editing categories and selections.
        """
        self.populate_table_with_data(self.expenses)

    def populate_table_with_data(self, expenses_data):
        """Populate table with given data (used for sorting)"""
        self.table.set_original_data(expenses_data)
        self.table.setRowCount(len(expenses_data))

        for row, expense in enumerate(expenses_data):
            # Import checkbox with better styling
            checkbox = QCheckBox()
            checkbox.setChecked(expense.get('import_checked', True))
            checkbox.stateChanged.connect(self.update_summary)
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 3px;
                    border: 2px solid #666;
                }
                QCheckBox::indicator:checked {
                    background-color: #28a745;
                    border-color: #28a745;
                }
            """)

            # Center the checkbox in a widget
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)

            # Date
            date_item = QTableWidgetItem(expense['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, date_item)

            # Person with improved styling for better visibility
            person_combo = QComboBox()
            person_combo.addItems(["Jeff", "Vanessa"])
            # Feature 1: Use default_person if provided (always override loader default)
            # The expense loader defaults to 'Jeff', so we override when user selected someone else
            if self.default_person:
                person_to_set = self.default_person
            else:
                person_to_set = expense.get('person', 'Jeff')
            person_combo.setCurrentText(person_to_set)
            person_combo.setStyleSheet("""
                QComboBox {
                    padding: 4px 8px;
                    font-size: 12px;
                    font-weight: bold;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background-color: white;
                    color: #2d3748;
                }
                QComboBox:focus {
                    border-color: #007bff;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #2d3748;
                    selection-background-color: #e3f2fd;
                    selection-color: #1a202c;
                }
            """)
            self.table.setCellWidget(row, 2, person_combo)

            # Amount
            amount_item = QTableWidgetItem(f"${expense['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            amount_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.table.setItem(row, 3, amount_item)

            # Description
            desc_item = QTableWidgetItem(expense['description'])
            desc_item.setToolTip(expense['description'])  # Show full text on hover
            self.table.setItem(row, 4, desc_item)

            # Smart category suggestion - Feature 2
            suggested_category = None
            suggested_subcategory = None
            
            # Try to get smart suggestion based on description
            suggestion = self.db.get_suggested_category(expense['description'])
            if suggestion and suggestion['confidence'] > 0.5:
                # Use suggestion if confidence is high enough
                suggested_category = suggestion['category']
                suggested_subcategory = suggestion['subcategory']
                # Override the expense category/subcategory if not already set
                if expense['category'] == '' or expense['category'] not in self.categories_data:
                    expense['category'] = suggested_category
                if expense['subcategory'] == '':
                    expense['subcategory'] = suggested_subcategory

            # Category (with ability to add new ones)
            category_combo = CustomComboBox(self, self.category_manager, False)
            category_combo.addItems(sorted(self.categories_data.keys()))
            category_combo.setCurrentText(expense['category'])
            category_combo.currentTextChanged.connect(lambda cat, r=row: self.on_category_changed(r, cat))
            # Highlight suggested categories
            if suggested_category and suggested_category == expense['category']:
                category_combo.setStyleSheet("""
                    QComboBox {
                        padding: 4px 8px;
                        font-size: 12px;
                        border: 2px solid #4CAF50;
                        border-radius: 3px;
                        background-color: #e8f5e9;
                        color: #2d3748;
                    }
                """)
            self.table.setCellWidget(row, 5, category_combo)

            # Subcategory (with ability to add new ones)
            subcategory_combo = CustomComboBox(self, self.category_manager, True, category_combo)
            if expense['category'] in self.categories_data:
                subcategory_combo.addItems(self.categories_data[expense['category']])
                if expense['subcategory'] in self.categories_data[expense['category']]:
                    subcategory_combo.setCurrentText(expense['subcategory'])
            # Highlight suggested subcategories
            if suggested_subcategory and suggested_subcategory == expense['subcategory']:
                subcategory_combo.setStyleSheet("""
                    QComboBox {
                        padding: 4px 8px;
                        font-size: 12px;
                        border: 2px solid #4CAF50;
                        border-radius: 3px;
                        background-color: #e8f5e9;
                        color: #2d3748;
                    }
                """)
            self.table.setCellWidget(row, 6, subcategory_combo)

            # Payment Method with improved styling and Credit Card as default
            payment_combo = QComboBox()
            payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Check", "Transfer", "Other"])
            payment_combo.setCurrentText(expense.get('payment_method', 'Credit Card'))
            payment_combo.setStyleSheet("""
                QComboBox {
                    padding: 4px 8px;
                    font-size: 12px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background-color: white;
                    color: #2d3748;
                }
                QComboBox:focus {
                    border-color: #007bff;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    color: #2d3748;
                    selection-background-color: #e3f2fd;
                    selection-color: #1a202c;
                }
            """)
            self.table.setCellWidget(row, 7, payment_combo)

    def on_category_changed(self, row: int, category: str):
        """Update subcategory options when category changes"""
        subcategory_combo = self.table.cellWidget(row, 6)
        category_combo = self.table.cellWidget(row, 5)

        if subcategory_combo and category in self.categories_data:
            subcategory_combo.clear()
            subcategory_combo.addItems(self.categories_data[category])
            # Update the category combo reference for the subcategory combo
            subcategory_combo.category_combo = category_combo

    def select_all(self):
        """Select all items for import"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)

    def select_none(self):
        """Deselect all items"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)

    def update_summary(self):
        """Update the summary labels"""
        selected_count = 0
        selected_amount = 0.0

        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
                    # Get amount from original data
                    if row < len(self.table.original_data):
                        selected_amount += self.table.original_data[row]['amount']

        self.selected_label.setText(f"Selected: {selected_count}")
        self.amount_label.setText(f"Total Amount: ${selected_amount:,.2f}")

    def get_selected_expenses(self) -> List[Dict]:
        """Get the list of selected and edited expenses"""
        selected_expenses = []

        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = None
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)

            if checkbox and checkbox.isChecked():
                # Get updated values from the UI
                person_combo = self.table.cellWidget(row, 2)
                category_combo = self.table.cellWidget(row, 5)
                subcategory_combo = self.table.cellWidget(row, 6)
                payment_combo = self.table.cellWidget(row, 7)

                # Use original data as base if available
                if row < len(self.table.original_data):
                    expense = self.table.original_data[row].copy()
                else:
                    expense = self.expenses[row].copy()

                expense['person'] = person_combo.currentText()
                expense['category'] = category_combo.currentText()
                expense['subcategory'] = subcategory_combo.currentText()
                expense['payment_method'] = payment_combo.currentText()

                # Feature 2: Save category mapping for smart suggestions
                # Learn the user's category choice for this description
                if expense.get('description') and expense.get('category') and expense.get('subcategory'):
                    try:
                        self.db.save_category_mapping(
                            expense['description'],
                            expense['category'],
                            expense['subcategory']
                        )
                    except Exception as e:
                        print(f"Error saving category mapping: {e}")

                selected_expenses.append(expense)

        return selected_expenses

    def refresh_categories(self):
        """Refresh categories from the category manager"""
        self.category_manager.refresh()
        self.categories_data = self.category_manager.get_categories()

        # Update all category combos
        for row in range(self.table.rowCount()):
            category_combo = self.table.cellWidget(row, 5)
            subcategory_combo = self.table.cellWidget(row, 6)

            if category_combo:
                current_category = category_combo.currentText()
                category_combo.clear()
                category_combo.addItems(sorted(self.categories_data.keys()))
                if current_category in self.categories_data:
                    category_combo.setCurrentText(current_category)

            if subcategory_combo and current_category in self.categories_data:
                current_subcategory = subcategory_combo.currentText()
                subcategory_combo.clear()
                subcategory_combo.addItems(self.categories_data[current_category])
                if current_subcategory in self.categories_data[current_category]:
                    subcategory_combo.setCurrentText(current_subcategory)

        QMessageBox.information(self, "Success", "Categories refreshed successfully!")
