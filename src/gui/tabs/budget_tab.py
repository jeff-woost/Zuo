"""
Budget Tab - Manages income and expenses with two sub-tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QDateEdit, QTabWidget,
    QHeaderView, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import csv
import os
from src.database.db_manager import DatabaseManager
from src.database.category_manager import get_category_manager
from src.gui.utils.expense_loader import ExpenseLoader
from src.gui.utils.table_items import CurrencyTableWidgetItem, DateTableWidgetItem
from src.gui.utils.advanced_filter_dialog import AdvancedFilterDialog
from src.gui.utils.checkbox_styles import create_form_checkbox, create_table_checkbox
from src.config import get_user_names

class BudgetTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.category_manager = get_category_manager()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with Income and Expenses sub-tabs"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Budget Management")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add Manage Categories button
        manage_categories_btn = QPushButton("⚙️ Manage Categories")
        manage_categories_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c5282;
            }
        """)
        manage_categories_btn.clicked.connect(self.show_category_management)
        header_layout.addWidget(manage_categories_btn)
        
        layout.addLayout(header_layout)
        
        # Create sub-tabs for Income and Expenses
        self.sub_tabs = QTabWidget()
        
        # Income Tab
        self.income_tab = IncomeSubTab()
        self.sub_tabs.addTab(self.income_tab, "💵 Income")
        
        # Expenses Tab
        self.expenses_tab = ExpensesSubTab()
        self.sub_tabs.addTab(self.expenses_tab, "💳 Expenses")
        
        layout.addWidget(self.sub_tabs)
        self.setLayout(layout)
    
    def show_category_management(self):
        """Show the category management dialog"""
        from src.gui.utils.category_management_dialog import CategoryManagementDialog
        
        dialog = CategoryManagementDialog(self)
        dialog.categoriesChanged.connect(self.on_categories_changed)
        dialog.exec()
    
    def on_categories_changed(self):
        """Handle categories being changed"""
        # Reload categories in both sub-tabs
        self.income_tab.load_categories()
        self.expenses_tab.load_categories()
        
        # Refresh the data to show any changes
        self.refresh_data()
        
    def refresh_data(self):
        """Refresh data in both sub-tabs"""
        self.income_tab.refresh_data()
        self.expenses_tab.refresh_data()


class IncomeSubTab(QWidget):
    """Sub-tab for managing income entries"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the Income UI"""
        layout = QVBoxLayout()
        
        # Get user names from config
        user_a, user_b = get_user_names()
        
        # Top section - Add Income Form
        form_group = QGroupBox("Add Income")
        form_layout = QGridLayout()
        
        # Person selector
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems([user_a, user_b])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        # Amount
        form_layout.addWidget(QLabel("Amount:"), 0, 2)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter income amount")
        form_layout.addWidget(self.amount_input, 0, 3)
        
        # Date
        form_layout.addWidget(QLabel("Date:"), 1, 0)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 1, 1)
        
        # Description
        form_layout.addWidget(QLabel("Description:"), 1, 2)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Monthly Salary, Bonus, etc.")
        form_layout.addWidget(self.description_input, 1, 3)
        
        # Add button
        add_btn = QPushButton("Add Income")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        add_btn.clicked.connect(self.add_income)
        form_layout.addWidget(add_btn, 2, 0, 1, 4)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Monthly Summary Section
        summary_layout = QHBoxLayout()
        
        # User A's Income Summary
        self.user_a_summary = self.create_summary_card(f"{user_a}'s Monthly Income", "$0.00")
        summary_layout.addWidget(self.user_a_summary)
        
        # User B's Income Summary
        self.user_b_summary = self.create_summary_card(f"{user_b}'s Monthly Income", "$0.00")
        summary_layout.addWidget(self.user_b_summary)
        
        # Total Income Summary
        self.total_summary = self.create_summary_card("Total Monthly Income", "$0.00")
        summary_layout.addWidget(self.total_summary)
        
        layout.addLayout(summary_layout)
        
        # Income History Table
        history_group = QGroupBox("Income History")
        history_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_person = QComboBox()
        self.filter_person.addItems(["All", user_a, user_b])
        self.filter_person.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_person)
        
        filter_layout.addWidget(QLabel("Month:"))
        self.filter_month = QComboBox()
        self.filter_month.addItems([
            "All", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        # FIXED: Set to "All" by default instead of current month
        self.filter_month.setCurrentIndex(0)  # "All" is at index 0
        self.filter_month.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_month)
        
        filter_layout.addWidget(QLabel("Year:"))
        self.filter_year = QComboBox()
        current_year = datetime.now().year
        self.filter_year.addItems(["All"] + [str(year) for year in range(current_year - 2, current_year + 2)])
        # FIXED: Set to "All" by default instead of current year
        self.filter_year.setCurrentText("All")
        self.filter_year.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_year)
        
        filter_layout.addStretch()
        
        # Advanced Filter button
        advanced_filter_btn = QPushButton("Advanced Filters")
        advanced_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        advanced_filter_btn.clicked.connect(self.show_advanced_filter)
        filter_layout.addWidget(advanced_filter_btn)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_income)
        filter_layout.addWidget(delete_btn)
        
        history_layout.addLayout(filter_layout)
        
        # Income table
        self.income_table = QTableWidget()
        self.income_table.setColumnCount(5)
        self.income_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Description", "ID"
        ])
        self.income_table.hideColumn(4)  # Hide ID column
        
        # Enable sorting and alternating row colors
        self.income_table.setSortingEnabled(True)
        self.income_table.setAlternatingRowColors(True)
        self.income_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.income_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Set column widths
        header = self.income_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        history_layout.addWidget(self.income_table)
        history_group.setLayout(history_layout)
        
        layout.addWidget(history_group)
        self.setLayout(layout)
    
    def load_categories(self):
        """Stub method - Income tab doesn't use categories"""
        pass
        
    def create_summary_card(self, title, value):
        """Create a summary card widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2a82da;")
        layout.addWidget(value_label)
        
        group.setLayout(layout)
        group.value_label = value_label  # Store reference for updating
        return group
        
    def add_income(self):
        """Add income entry to database"""
        try:
            person = self.person_combo.currentText()
            amount_text = self.amount_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            description = self.description_input.text().strip()
            
            # Validate amount
            if not amount_text:
                QMessageBox.warning(self, "Warning", "Please enter an amount")
                return
                
            try:
                amount = float(amount_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for amount")
                return
            
            # Add to database
            self.db.add_income(person, amount, date, description)
            
            # Clear form
            self.amount_input.clear()
            self.description_input.clear()
            
            # Refresh display
            self.refresh_data()
            
            QMessageBox.information(self, "Success", "Income added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add income: {str(e)}")
            
    def delete_selected_income(self):
        """Delete selected income entries"""
        selected_rows = []
        for row in range(self.income_table.rowCount()):
            if self.income_table.item(row, 0) and self.income_table.item(row, 0).isSelected():
                selected_rows.append(row)
            elif any(self.income_table.item(row, col) and self.income_table.item(row, col).isSelected()
                    for col in range(self.income_table.columnCount())):
                selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select one or more income entries to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_rows)} income entr{'y' if len(selected_rows) == 1 else 'ies'}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Delete each selected income entry
            deleted_count = 0
            for row in reversed(selected_rows):  # Reverse to maintain row indices
                income_id_item = self.income_table.item(row, 4)  # ID is in column 4
                if income_id_item:
                    income_id = int(income_id_item.text())

                    # Delete from database using the model's delete method
                    from src.database.models import IncomeModel
                    IncomeModel.delete(self.db, income_id)
                    deleted_count += 1

            # Refresh the table
            self.refresh_data()

            QMessageBox.information(
                self,
                "Success",
                f"Successfully deleted {deleted_count} income entr{'y' if deleted_count == 1 else 'ies'}."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete income entries: {str(e)}")

    def refresh_data(self):
        """Refresh the income data display"""
        try:
            # CRITICAL FIX: Disable sorting during table population to prevent data loss
            self.income_table.setSortingEnabled(False)

            # Build filter parameters
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            
            # Date filters
            start_date = None
            end_date = None
            
            if self.filter_month.currentIndex() > 0 and self.filter_year.currentText() != "All":
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"
            
            # Get income data
            income_data = self.db.get_income(start_date, end_date, person_filter)
            
            # Clear and populate table
            self.income_table.setRowCount(0)
            
            user_a, user_b = get_user_names()
            user_a_total = 0
            user_b_total = 0
            
            for income in income_data:
                row = self.income_table.rowCount()
                self.income_table.insertRow(row)
                
                self.income_table.setItem(row, 0, DateTableWidgetItem(income['date']))
                self.income_table.setItem(row, 1, QTableWidgetItem(income['person']))
                
                amount = income['amount']
                amount_item = CurrencyTableWidgetItem(f"${amount:,.2f}")
                amount_item.setForeground(Qt.GlobalColor.darkGreen)
                self.income_table.setItem(row, 2, amount_item)
                self.income_table.setItem(row, 3, QTableWidgetItem(income.get('description', '')))
                self.income_table.setItem(row, 4, QTableWidgetItem(str(income['id'])))
                
                # Calculate totals
                if income['person'] == user_a:
                    user_a_total += amount
                else:
                    user_b_total += amount
            
            # Update summary cards
            self.user_a_summary.value_label.setText(f"${user_a_total:,.2f}")
            self.user_b_summary.value_label.setText(f"${user_b_total:,.2f}")
            self.total_summary.value_label.setText(f"${user_a_total + user_b_total:,.2f}")
            
        except Exception as e:
            print(f"Error refreshing income data: {e}")
        finally:
            # CRITICAL FIX: Re-enable sorting after table is fully populated
            self.income_table.setSortingEnabled(True)

    def show_advanced_filter(self):
        """Show the advanced filter dialog for income"""
        dialog = AdvancedFilterDialog(self, "income")

        # Connect the filter signal
        dialog.filtersApplied.connect(self.apply_advanced_filters)

        dialog.exec()

    def apply_advanced_filters(self, filters):
        """Apply advanced filters to income data"""
        try:
            # Extract filter parameters
            start_date = filters.get('start_date')
            end_date = filters.get('end_date')

            # Person filter
            person_filter = None
            if 'persons' in filters:
                if len(filters['persons']) == 1:
                    person_filter = filters['persons'][0]
                # If multiple persons selected, we'll handle in the query

            # Get income data with filters
            income_data = self.db.get_income(start_date, end_date, person_filter)

            # Apply additional filters
            filtered_data = []
            for income in income_data:
                # Amount filter
                if 'min_amount' in filters or 'max_amount' in filters:
                    amount = income['amount']
                    if 'min_amount' in filters and amount < filters['min_amount']:
                        continue
                    if 'max_amount' in filters and amount > filters['max_amount']:
                        continue

                # Text search filter
                if 'search_text' in filters:
                    search_text = filters['search_text']
                    search_field = filters.get('search_field', 'All Fields')
                    case_sensitive = filters.get('case_sensitive', False)

                    if not case_sensitive:
                        search_text = search_text.lower()

                    found = False
                    if search_field == 'Description' or search_field == 'All Fields':
                        desc = income.get('description', '')
                        if not case_sensitive:
                            desc = desc.lower()
                        if search_text in desc:
                            found = True

                    if search_field == 'All Fields' and not found:
                        # Search in person name
                        person = income.get('person', '')
                        if not case_sensitive:
                            person = person.lower()
                        if search_text in person:
                            found = True

                    if not found:
                        continue

                # Person filter (for multiple persons)
                if 'persons' in filters and len(filters['persons']) > 1:
                    if income['person'] not in filters['persons']:
                        continue

                filtered_data.append(income)

            # Update the table with filtered data
            self.update_income_table(filtered_data)

        except Exception as e:
            print(f"Error applying advanced filters: {e}")

    def update_income_table(self, income_data):
        """Update the income table with filtered data"""
        try:
            # CRITICAL FIX: Disable sorting during table population
            self.income_table.setSortingEnabled(False)

            # Clear and populate table
            self.income_table.setRowCount(0)

            user_a, user_b = get_user_names()
            user_a_total = 0
            user_b_total = 0

            for income in income_data:
                row = self.income_table.rowCount()
                self.income_table.insertRow(row)

                self.income_table.setItem(row, 0, DateTableWidgetItem(income['date']))
                self.income_table.setItem(row, 1, QTableWidgetItem(income['person']))

                amount = income['amount']
                amount_item = CurrencyTableWidgetItem(f"${amount:,.2f}")
                amount_item.setForeground(Qt.GlobalColor.darkGreen)
                self.income_table.setItem(row, 2, amount_item)
                self.income_table.setItem(row, 3, QTableWidgetItem(income.get('description', '')))
                self.income_table.setItem(row, 4, QTableWidgetItem(str(income['id'])))

                # Calculate totals
                if income['person'] == user_a:
                    user_a_total += amount
                else:
                    user_b_total += amount

            # Update summary cards
            self.user_a_summary.value_label.setText(f"${user_a_total:,.2f}")
            self.user_b_summary.value_label.setText(f"${user_b_total:,.2f}")
            self.total_summary.value_label.setText(f"${user_a_total + user_b_total:,.2f}")

        except Exception as e:
            print(f"Error updating income table: {e}")
        finally:
            # CRITICAL FIX: Re-enable sorting after table population
            self.income_table.setSortingEnabled(True)

    def show_advanced_filter(self):
        """Show the advanced filter dialog"""
        dialog = AdvancedFilterDialog(self)
        dialog.setWindowTitle("Advanced Income Filter")

        # Set initial filter values
        dialog.person_filter = self.filter_person.currentText()
        dialog.month_filter = self.filter_month.currentText()
        dialog.year_filter = self.filter_year.currentText()

        # Accept and apply filters
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.filter_person.setCurrentText(dialog.person_filter)
            self.filter_month.setCurrentText(dialog.month_filter)
            self.filter_year.setCurrentText(dialog.year_filter)

            self.refresh_data()


class ExpensesSubTab(QWidget):
    """Sub-tab for managing expense entries"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.category_manager = get_category_manager()
        self.categories_data = self.category_manager.get_categories()
        self.init_ui()
        self.load_categories()  # Add this line to populate category dropdowns
        self.refresh_data()

    def init_ui(self):
        """Initialize the Expenses UI"""
        layout = QVBoxLayout()
        
        # Get user names from config
        user_a, user_b = get_user_names()
        
        # Top section - Add Expense Form
        form_group = QGroupBox("Add Expense")
        form_layout = QGridLayout()
        
        # Row 1
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems([user_a, user_b])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        form_layout.addWidget(QLabel("Amount:"), 0, 2)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter expense amount")
        form_layout.addWidget(self.amount_input, 0, 3)
        
        form_layout.addWidget(QLabel("Date:"), 0, 4)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 0, 5)
        
        # Row 2
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        form_layout.addWidget(self.category_combo, 1, 1)
        
        form_layout.addWidget(QLabel("Subcategory:"), 1, 2)
        self.subcategory_combo = QComboBox()
        form_layout.addWidget(self.subcategory_combo, 1, 3)
        
        form_layout.addWidget(QLabel("Payment Method:"), 1, 4)
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Check", "Transfer", "Other"])
        form_layout.addWidget(self.payment_combo, 1, 5)
        
        # Row 3
        form_layout.addWidget(QLabel("Description:"), 2, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Optional description - will suggest category based on history")
        # Connect to smart category suggestion when user finishes typing
        self.description_input.editingFinished.connect(self.suggest_category_from_description)
        form_layout.addWidget(self.description_input, 2, 1, 1, 4)

        # Add realized checkbox using centralized styling
        self.realized_checkbox = create_form_checkbox(
            "Already taken from joint checking",
            "Check if this expense has already been paid from the joint checking account"
        )
        form_layout.addWidget(self.realized_checkbox, 2, 5)

        # Row 4 - Buttons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Add Expense")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        add_btn.clicked.connect(self.add_expense)
        button_layout.addWidget(add_btn)
        
        import_btn = QPushButton("Import from File")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
        """)
        import_btn.clicked.connect(self.import_expenses)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        form_layout.addLayout(button_layout, 3, 0, 1, 6)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Monthly Summary Section
        summary_layout = QHBoxLayout()
        
        # User A's Expenses Summary
        self.user_a_summary = self.create_summary_card(f"{user_a}'s Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.user_a_summary)
        
        # User B's Expenses Summary
        self.user_b_summary = self.create_summary_card(f"{user_b}'s Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.user_b_summary)
        
        # Total Expenses Summary
        self.total_summary = self.create_summary_card("Total Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.total_summary)
        
        # Top Category Summary
        self.top_category_summary = self.create_summary_card("Top Category", "None")
        summary_layout.addWidget(self.top_category_summary)
        
        layout.addLayout(summary_layout)
        
        # Expense History Table
        history_group = QGroupBox("Expense History")
        history_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_person = QComboBox()
        self.filter_person.addItems(["All", user_a, user_b])
        self.filter_person.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_person)
        
        self.filter_category = QComboBox()
        self.filter_category.addItems(["All Categories"])
        self.filter_category.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_category)
        
        filter_layout.addWidget(QLabel("Month:"))
        self.filter_month = QComboBox()
        self.filter_month.addItems([
            "All", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        # FIXED: Set to "All" by default instead of current month
        self.filter_month.setCurrentIndex(0)  # "All" is at index 0
        self.filter_month.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_month)
        
        filter_layout.addWidget(QLabel("Year:"))
        self.filter_year = QComboBox()
        current_year = datetime.now().year
        self.filter_year.addItems(["All"] + [str(year) for year in range(current_year - 2, current_year + 2)])
        # FIXED: Set to "All" by default instead of current year
        self.filter_year.setCurrentText("All")
        self.filter_year.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_year)
        
        filter_layout.addStretch()
        
        # Bulk selection controls
        bulk_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #5bc0de;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #46b8da;
            }
        """)
        select_all_btn.clicked.connect(self.select_all_expenses)
        bulk_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        select_none_btn.clicked.connect(self.select_none_expenses)
        bulk_layout.addWidget(select_none_btn)

        # Selected count label
        self.selected_count_label = QLabel("Selected: 0")
        self.selected_count_label.setStyleSheet("font-weight: bold; color: #555;")
        bulk_layout.addWidget(self.selected_count_label)

        bulk_layout.addStretch()

        # Export and Delete buttons
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_expenses)
        bulk_layout.addWidget(export_btn)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_expenses)
        bulk_layout.addWidget(delete_btn)

        # Add Clear All Expenses button
        clear_all_btn = QPushButton("Clear All Expenses")
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                border: 2px solid #c9302c;
            }
            QPushButton:hover {
                background-color: #c9302c;
                border-color: #ac2925;
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_expenses)
        bulk_layout.addWidget(clear_all_btn)

        history_layout.addLayout(filter_layout)
        history_layout.addLayout(bulk_layout)

        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(10)  # Added column for realized status
        self.expense_table.setHorizontalHeaderLabels([
            "Select", "Date", "Person", "Amount", "Category", "Subcategory",
            "Description", "Payment", "Joint Account", "ID"
        ])
        self.expense_table.hideColumn(9)  # Hide ID column (moved to position 9)

        # Set column widths
        header = self.expense_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)      # Select checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Person
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Subcategory
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)           # Description
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Payment
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)      # Joint Account checkbox

        self.expense_table.setColumnWidth(0, 80)  # Select column width
        self.expense_table.setColumnWidth(8, 100)  # Joint Account column width

        # Enable sorting and alternating row colors
        self.expense_table.setSortingEnabled(True)
        self.expense_table.setAlternatingRowColors(True)
        self.expense_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.expense_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Connect cell click to handle checkbox selection
        self.expense_table.cellClicked.connect(self.on_cell_clicked)

        history_layout.addWidget(self.expense_table)
        history_group.setLayout(history_layout)

        layout.addWidget(history_group)
        self.setLayout(layout)

    def create_summary_card(self, title, value):
        """Create a summary card widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 150px;
            }
        """)

        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #d9534f;")
        layout.addWidget(value_label)

        group.setLayout(layout)
        group.value_label = value_label  # Store reference for updating
        return group

    def load_categories(self):
        """Load categories from the centralized category manager"""
        try:
            # Get categories from centralized manager
            self.categories_data = self.category_manager.get_categories()

            # Populate category combo
            self.category_combo.clear()
            self.category_combo.addItems(sorted(self.categories_data.keys()))

            # Populate filter category combo
            self.filter_category.clear()
            self.filter_category.addItems(["All Categories"] + sorted(self.categories_data.keys()))

        except Exception as e:
            print(f"Error loading categories: {e}")

    def on_category_changed(self, category):
        """Update subcategories when category changes"""
        self.subcategory_combo.clear()
        if category in self.categories_data:
            self.subcategory_combo.addItems(self.categories_data[category])

    def suggest_category_from_description(self):
        """Suggest category and subcategory based on description using learned patterns"""
        description = self.description_input.text().strip()
        if not description:
            return

        try:
            # Get suggested category from database
            suggestion = self.db.get_suggested_category(description)

            if suggestion and suggestion.get('confidence', 0) > 0.3:
                category = suggestion['category']
                subcategory = suggestion['subcategory']
                confidence = suggestion['confidence']

                # Only auto-fill if category combo is at default or first item
                current_category = self.category_combo.currentText()

                # Check if the suggested category exists in our categories
                if category in self.categories_data:
                    # Set the category
                    category_index = self.category_combo.findText(category)
                    if category_index >= 0:
                        self.category_combo.setCurrentIndex(category_index)

                        # Wait for subcategory combo to update, then set subcategory
                        if subcategory in self.categories_data.get(category, []):
                            subcategory_index = self.subcategory_combo.findText(subcategory)
                            if subcategory_index >= 0:
                                self.subcategory_combo.setCurrentIndex(subcategory_index)

                        # Show confidence indicator in status or tooltip
                        confidence_pct = int(confidence * 100)
                        self.description_input.setToolTip(
                            f"Auto-suggested: {category} → {subcategory} ({confidence_pct}% match)"
                        )
                        print(f"DEBUG: Suggested category '{category}/{subcategory}' with {confidence_pct}% confidence")

        except Exception as e:
            print(f"Error suggesting category: {e}")

    def add_expense(self):
        """Add expense entry to database"""
        try:
            person = self.person_combo.currentText()
            amount_text = self.amount_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            category = self.category_combo.currentText()
            subcategory = self.subcategory_combo.currentText()
            description = self.description_input.text().strip()
            payment_method = self.payment_combo.currentText()
            realized = self.realized_checkbox.isChecked()  # Get realized status

            # Validate inputs
            if not amount_text:
                QMessageBox.warning(self, "Warning", "Please enter an amount")
                return

            if not category or not subcategory:
                QMessageBox.warning(self, "Warning", "Please select category and subcategory")
                return

            try:
                amount = float(amount_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for amount")
                return

            # Debug: Print what we're trying to add
            print(f"DEBUG: Adding expense - Person: {person}, Amount: {amount}, Date: {date}, Category: {category}, Subcategory: {subcategory}")

            # Use database context manager to ensure proper transaction handling
            with self.db as db:
                # Add to database using the ExpenseModel.add method
                from src.database.models import ExpenseModel
                ExpenseModel.add(db, date, person, amount, category, subcategory,
                               description, payment_method, realized)

                # Force commit within the transaction
                db.commit()

                # Save category mapping for smart inference if description is provided
                if description:
                    try:
                        db.save_category_mapping(description, category, subcategory)
                    except Exception as e:
                        print(f"DEBUG: Could not save category mapping: {e}")

                # Verify the expense was added by checking the database immediately
                verify_expenses = db.get_expenses()
                print(f"DEBUG: Total expenses in database after add: {len(verify_expenses)}")

                # Check if our specific expense is there
                our_expense = [exp for exp in verify_expenses if
                              exp['date'] == date and
                              exp['person'] == person and
                              abs(exp['amount'] - amount) < 0.01]
                print(f"DEBUG: Found our expense: {len(our_expense) > 0}")

            # Clear form
            self.amount_input.clear()
            self.description_input.clear()
            self.realized_checkbox.setChecked(False)  # Reset checkbox

            # Add a longer delay to ensure database consistency across all connections
            import time
            time.sleep(0.2)  # Increase delay

            # Debug: Check what filters are currently set
            print(f"DEBUG: Current filters - Person: {self.filter_person.currentText()}, "
                  f"Month: {self.filter_month.currentText()}, Year: {self.filter_year.currentText()}, "
                  f"Category: {self.filter_category.currentText()}")

            # Refresh display
            self.refresh_data()

            # Debug: Check table count after refresh
            print(f"DEBUG: Table rows after refresh: {self.expense_table.rowCount()}")

            QMessageBox.information(self, "Success", "Expense added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add expense: {str(e)}")
            print(f"Detailed error: {e}")  # For debugging
            import traceback
            traceback.print_exc()

    def import_expenses(self):
        """Import expenses from CSV or TXT file using ExpenseLoader"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Import Expenses", 
                "", 
                "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if not file_path:
                return
            
            # Use ExpenseLoader to parse the file
            loader = ExpenseLoader()
            expenses = []
            errors = []

            if file_path.lower().endswith('.csv'):
                expenses, errors = loader.load_csv_file(file_path)
            elif file_path.lower().endswith('.txt'):
                expenses, errors = loader.load_txt_file(file_path)
            else:
                # Try CSV first, then TXT
                expenses, errors = loader.load_csv_file(file_path)
                if not expenses and not errors:
                    expenses, errors = loader.load_txt_file(file_path)

            # Show errors if any
            if errors:
                error_dialog = QMessageBox()
                error_dialog.setWindowTitle("Import Warnings")
                error_dialog.setIcon(QMessageBox.Icon.Warning)
                error_dialog.setText(f"Found {len(errors)} issues while parsing the file:")
                error_dialog.setDetailedText("\n".join(errors))
                error_dialog.exec()

            if not expenses:
                QMessageBox.warning(self, "Warning", "No valid expenses found in the file")
                return

            # Validate expenses
            valid_expenses, validation_errors = loader.validate_expenses(expenses)

            if validation_errors:
                error_dialog = QMessageBox()
                error_dialog.setWindowTitle("Validation Errors")
                error_dialog.setIcon(QMessageBox.Icon.Warning)
                error_dialog.setText(f"Found {len(validation_errors)} validation issues:")
                error_dialog.setDetailedText("\n".join(validation_errors))
                error_dialog.exec()

            if not valid_expenses:
                QMessageBox.warning(self, "Warning", "No valid expenses after validation")
                return

            # Feature 1: Prompt user for who these expenses are for
            from PyQt6.QtWidgets import QInputDialog
            user_a_name, user_b_name = get_user_names()
            persons = [user_a_name, user_b_name]
            default_person, ok = QInputDialog.getItem(
                self,
                "Who are these expenses for?",
                "Select the person these expenses belong to:",
                persons,
                0,  # Default selection index
                False  # Not editable
            )

            if not ok:
                return  # User cancelled

            # Use the new BulkImportPreviewDialog with proper category handling
            from src.gui.utils.bulk_import_dialog import BulkImportPreviewDialog

            # Get categories from the loader to ensure they match
            loader_categories = loader.get_available_categories()

            # Show preview dialog with loader categories and pre-populated person
            preview_dialog = BulkImportPreviewDialog(valid_expenses, loader_categories, self, default_person=default_person)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                final_expenses = preview_dialog.get_selected_expenses()

                if final_expenses:
                    # Add to database
                    self.db.bulk_add_expenses(final_expenses)
                    self.refresh_data()

                    QMessageBox.information(
                        self,
                        "Success", 
                        f"Successfully imported {len(final_expenses)} expenses!\n\n"
                        f"Parsing errors: {len(errors)}\n"
                        f"Validation errors: {len(validation_errors)}\n"
                        f"Successfully imported: {len(final_expenses)}"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import expenses: {str(e)}")
            print(f"Import error details: {e}")  # For debugging

    def export_expenses(self):
        """Export expenses to CSV file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Expenses",
                f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
                
            # Get current filter settings
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            category_filter = None if self.filter_category.currentText() == "All Categories" else self.filter_category.currentText()
            
            # Build date filters
            start_date = None
            end_date = None
            
            if self.filter_month.currentIndex() > 0 and self.filter_year.currentText() != "All":
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"
            
            # Get expense data
            expenses = self.db.get_expenses(start_date, end_date, person_filter, category_filter)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['date', 'person', 'amount', 'category', 'subcategory', 
                            'description', 'payment_method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for expense in expenses:
                    writer.writerow({
                        'date': expense['date'],
                        'person': expense['person'],
                        'amount': expense['amount'],
                        'category': expense['category'],
                        'subcategory': expense['subcategory'],
                        'description': expense.get('description', ''),
                        'payment_method': expense.get('payment_method', '')
                    })
            
            QMessageBox.information(self, "Success", f"Expenses exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export expenses: {str(e)}")
            
    def delete_selected_expenses(self):
        """Delete selected expense entries"""
        selected_rows = []

        # Check which rows have their checkboxes selected
        for row in range(self.expense_table.rowCount()):
            checkbox_widget = self.expense_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select one or more expense entries to delete using the checkboxes.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_rows)} expense entr{'y' if len(selected_rows) == 1 else 'ies'}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Delete each selected expense entry
            deleted_count = 0
            for row in reversed(selected_rows):  # Reverse to maintain row indices
                expense_id_item = self.expense_table.item(row, 9)  # ID is in column 9 (the last column)
                if expense_id_item:
                    expense_id = int(expense_id_item.text())
                    print(f"DEBUG: Attempting to delete expense ID {expense_id}")

                    # Delete from database using the model's delete method
                    from src.database.models import ExpenseModel
                    ExpenseModel.delete(self.db, expense_id)
                    deleted_count += 1
                    print(f"DEBUG: Successfully deleted expense ID {expense_id}")

            # Refresh the table
            self.refresh_data()

            QMessageBox.information(
                self,
                "Success",
                f"Successfully deleted {deleted_count} expense entr{'y' if deleted_count == 1 else 'ies'}."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete expense entries: {str(e)}")
            print(f"DEBUG: Delete error details: {e}")  # For debugging
            import traceback
            traceback.print_exc()

    def clear_all_expenses(self):
        """Clear expenses with options for specific month or all expenses"""
        try:
            # Create a custom dialog for clearing options
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QComboBox, QLabel, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle("Clear Expenses Options")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout(dialog)

            # Title
            title = QLabel("Choose how to clear expenses:")
            title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(title)

            # Radio button group
            radio_group = QButtonGroup(dialog)

            # Option 1: Clear specific month
            month_radio = QRadioButton("Clear expenses for a specific month (safer)")
            month_radio.setChecked(True)  # Default to safer option
            radio_group.addButton(month_radio, 1)
            layout.addWidget(month_radio)

            # Month/Year selection
            month_layout = QHBoxLayout()
            month_layout.addWidget(QLabel("Month:"))

            month_combo = QComboBox()
            month_combo.addItems([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ])
            # Set to current month
            current_month = datetime.now().month - 1  # 0-based for combo
            month_combo.setCurrentIndex(current_month)
            month_layout.addWidget(month_combo)

            month_layout.addWidget(QLabel("Year:"))
            year_combo = QComboBox()
            current_year = datetime.now().year
            year_combo.addItems([str(year) for year in range(current_year - 2, current_year + 6)])
            year_combo.setCurrentText(str(current_year))
            month_layout.addWidget(year_combo)

            layout.addLayout(month_layout)

            # Option 2: Clear all
            all_radio = QRadioButton("Clear ALL expenses (destructive - removes all history)")
            all_radio.setStyleSheet("color: red; font-weight: bold;")
            radio_group.addButton(all_radio, 2)
            layout.addWidget(all_radio)

            # Warning text
            warning = QLabel("⚠️ Warning: Clearing all expenses will permanently delete all expense history and cannot be undone!")
            warning.setWordWrap(True)
            warning.setStyleSheet("color: red; font-style: italic; margin: 10px;")
            layout.addWidget(warning)

            # Buttons
            button_layout = QHBoxLayout()

            proceed_btn = QPushButton("Proceed")
            proceed_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #666;
                }
            """)

            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(proceed_btn)
            layout.addLayout(button_layout)

            # Connect buttons
            proceed_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)

            # Show dialog
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return

            # Get selected option
            selected_option = radio_group.checkedId()

            if selected_option == 1:  # Clear specific month
                month = month_combo.currentIndex() + 1  # Convert to 1-based
                year = int(year_combo.currentText())
                month_name = month_combo.currentText()

                # Calculate date range
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"

                # Get expenses for this month
                month_expenses = self.db.get_expenses(start_date, end_date)

                if not month_expenses:
                    QMessageBox.information(
                        self,
                        "No Expenses Found",
                        f"No expenses found for {month_name} {year}."
                    )
                    return

                # Show summary and confirm
                user_a, user_b = get_user_names()
                user_a_count = sum(1 for exp in month_expenses if exp['person'] == user_a)
                user_b_count = sum(1 for exp in month_expenses if exp['person'] == user_b)
                user_a_total = sum(exp['amount'] for exp in month_expenses if exp['person'] == user_a)
                user_b_total = sum(exp['amount'] for exp in month_expenses if exp['person'] == user_b)

                confirmation_msg = (
                    f"Found {len(month_expenses)} expenses for {month_name} {year}:\n\n"
                    f"{user_a}: {user_a_count} expenses, ${user_a_total:,.2f}\n"
                    f"{user_b}: {user_b_count} expenses, ${user_b_total:,.2f}\n"
                    f"Total: ${user_a_total + user_b_total:,.2f}\n\n"
                    f"Are you sure you want to delete these expenses?\n"
                    f"This action cannot be undone."
                )

                reply = QMessageBox.question(
                    self,
                    f"Confirm Clear {month_name} {year}",
                    confirmation_msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply != QMessageBox.StandardButton.Yes:
                    return

                # Delete expenses for this month
                from src.database.models import ExpenseModel
                deleted_count = 0
                for expense in month_expenses:
                    ExpenseModel.delete(self.db, expense['id'])
                    deleted_count += 1

                # Refresh the table
                self.refresh_data()

                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ Successfully cleared {deleted_count} expenses for {month_name} {year}!\n\n"
                    f"All other historical data remains intact."
                )

            elif selected_option == 2:  # Clear all expenses
                # Strong confirmation for clearing all
                reply = QMessageBox.question(
                    self,
                    "Confirm Clear All Expenses",
                    "⚠️ WARNING: This will permanently delete ALL expense records from the database.\n\n"
                    "This action cannot be undone and will:\n"
                    "• Remove all expense history\n"
                    "• Reset the expense ID counter\n"
                    "• Clear any stuck or incomplete expense records\n\n"
                    "Are you sure you want to proceed?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )

                if reply != QMessageBox.StandardButton.Yes:
                    return

                # Use the ExpenseModel.clear_all method to completely clear expenses
                from src.database.models import ExpenseModel
                count = ExpenseModel.clear_all(self.db)

                # Refresh the table to show empty state
                self.refresh_data()

                QMessageBox.information(
                    self,
                    "Success",
                    f"✅ Successfully cleared all expense records!\n\n"
                    f"Deleted {count} expense entries.\n"
                    f"Database is now clean and ready for fresh data."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear expenses: {str(e)}")

    def on_cell_clicked(self, row, column):
        """Handle cell clicks to toggle checkboxes when clicking anywhere in the row"""
        if column == 0:
            # Direct checkbox click - let it handle itself
            return

        # For clicks on other columns, toggle the checkbox in column 0
        checkbox_widget = self.expense_table.cellWidget(row, 0)
        if checkbox_widget:
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox:
                checkbox.setChecked(not checkbox.isChecked())
                self.update_selected_count()

    def select_all_expenses(self):
        """Select all expense entries"""
        for row in range(self.expense_table.rowCount()):
            checkbox_widget = self.expense_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)
        self.update_selected_count()

    def select_none_expenses(self):
        """Deselect all expense entries"""
        for row in range(self.expense_table.rowCount()):
            checkbox_widget = self.expense_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(False)
        self.update_selected_count()

    def update_selected_count(self):
        """Update the selected count label"""
        selected_count = 0
        for row in range(self.expense_table.rowCount()):
            checkbox_widget = self.expense_table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    selected_count += 1

        self.selected_count_label.setText(f"Selected: {selected_count}")

    def refresh_data(self):
        """Refresh the expense data display"""
        try:
            print("DEBUG: Starting refresh_data")

            # CRITICAL FIX: Disable sorting during table population to prevent column disappearing
            self.expense_table.setSortingEnabled(False)

            # Build filter parameters
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            category_filter = None if self.filter_category.currentText() == "All Categories" else self.filter_category.currentText()

            # Date filters - Show all expenses when filters are "All"
            start_date = None
            end_date = None

            # Only apply date filtering if BOTH month AND year are explicitly selected (not "All")
            if (self.filter_month.currentIndex() > 0 and
                self.filter_year.currentText() != "All"):
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"

            print(f"DEBUG: Filter parameters - Person: {person_filter}, Category: {category_filter}, "
                  f"Start Date: {start_date}, End Date: {end_date}")

            # Get expense data using the standard database method
            expense_data = self.db.get_expenses(start_date, end_date, person_filter, category_filter)

            print(f"DEBUG: Retrieved {len(expense_data)} expenses from database")
            if expense_data:
                print(f"DEBUG: First expense has fields: {list(expense_data[0].keys())}")

            # Clear and populate table
            self.expense_table.setRowCount(0)
            print(f"DEBUG: Cleared table, now has {self.expense_table.rowCount()} rows")

            # Calculate totals from ALL filtered data (not just visible)
            user_a, user_b = get_user_names()
            user_a_total = 0
            user_b_total = 0
            category_totals = {}

            # IMPORTANT: Calculate summary totals from the SAME filtered data that populates the table
            for expense in expense_data:
                amount = expense['amount']

                # Calculate totals for summary cards
                if expense['person'] == user_a:
                    user_a_total += amount
                else:
                    user_b_total += amount

                # Track category totals for top category
                category = expense['category']
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount

            # Update summary cards FIRST with calculated totals
            self.user_a_summary.value_label.setText(f"${user_a_total:,.2f}")
            self.user_b_summary.value_label.setText(f"${user_b_total:,.2f}")
            self.total_summary.value_label.setText(f"${user_a_total + user_b_total:,.2f}")

            # Find and display top category
            if category_totals:
                top_category = max(category_totals, key=category_totals.get)
                self.top_category_summary.value_label.setText(
                    f"{top_category}\n${category_totals[top_category]:,.2f}"
                )
            else:
                self.top_category_summary.value_label.setText("None")

            # Now populate the table with the same data
            for i, expense in enumerate(expense_data):
                row = self.expense_table.rowCount()
                self.expense_table.insertRow(row)

                # Add checkbox in first column using centralized styling
                checkbox = create_table_checkbox("Click to select this expense for deletion")
                checkbox.setObjectName("table-select")
                checkbox.stateChanged.connect(self.update_selected_count)

                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.expense_table.setCellWidget(row, 0, checkbox_widget)

                # Date
                self.expense_table.setItem(row, 1, DateTableWidgetItem(expense['date']))

                # Person
                self.expense_table.setItem(row, 2, QTableWidgetItem(expense['person']))

                # Amount
                amount = expense['amount']
                amount_item = CurrencyTableWidgetItem(f"${amount:,.2f}")
                amount_item.setForeground(Qt.GlobalColor.red)
                self.expense_table.setItem(row, 3, amount_item)

                # Category
                self.expense_table.setItem(row, 4, QTableWidgetItem(expense['category']))

                # Subcategory
                self.expense_table.setItem(row, 5, QTableWidgetItem(expense['subcategory']))

                # Description
                self.expense_table.setItem(row, 6, QTableWidgetItem(expense.get('description', '')))

                # Payment Method
                self.expense_table.setItem(row, 7, QTableWidgetItem(expense.get('payment_method', 'Credit Card')))

                # Joint Account (realized) checkbox
                realized_checkbox = QCheckBox()
                realized_checkbox.setChecked(expense.get('realized', False))
                realized_checkbox.setToolTip("Click to toggle if this expense has been paid from joint account")
                # Store expense ID in the checkbox for easy access
                realized_checkbox.setProperty("expense_id", expense['id'])
                realized_checkbox.stateChanged.connect(self.on_realized_checkbox_changed)

                realized_widget = QWidget()
                realized_layout = QHBoxLayout(realized_widget)
                realized_layout.addWidget(realized_checkbox)
                realized_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                realized_layout.setContentsMargins(0, 0, 0, 0)
                self.expense_table.setCellWidget(row, 8, realized_widget)

                # ID (hidden)
                self.expense_table.setItem(row, 9, QTableWidgetItem(str(expense['id'])))

                # Debug first few rows
                if i < 3:
                    print(f"DEBUG: Added row {row} - {expense['date']} | {expense['person']} | ${expense['amount']:.2f} | "
                          f"{expense['category']} | {expense['subcategory']} | {expense['description']} | "
                          f"{expense['payment_method']} | Joint: {expense['realized']}")

            print(f"DEBUG: Final table row count: {self.expense_table.rowCount()}")
            print(f"DEBUG: Summary totals - {user_a}: ${user_a_total:,.2f}, {user_b}: ${user_b_total:,.2f}, Total: ${user_a_total + user_b_total:,.2f}")

            # CRITICAL FIX: Re-enable sorting AFTER table population is complete
            self.expense_table.setSortingEnabled(True)

            # Force column width refresh to ensure all columns are visible
            self.expense_table.resizeColumnsToContents()

            # Restore specific column widths that might have been lost
            self.expense_table.setColumnWidth(0, 80)   # Select column
            self.expense_table.setColumnWidth(8, 100)  # Joint Account column

            # Update selected count
            self.update_selected_count()

            print("DEBUG: refresh_data completed successfully")

        except Exception as e:
            print(f"Error refreshing expense data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Ensure sorting is always re-enabled even if there's an error
            self.expense_table.setSortingEnabled(True)

    def on_realized_checkbox_changed(self, state):
        """Handle changes to the realized checkbox (joint account status)"""
        checkbox = self.sender()
        if checkbox and checkbox.property("expense_id"):
            expense_id = checkbox.property("expense_id")
            realized = state == Qt.CheckState.Checked.value

            try:
                # Update the expense in the database
                from src.database.models import ExpenseModel
                if realized:
                    ExpenseModel.mark_as_realized(self.db, expense_id)
                else:
                    ExpenseModel.mark_as_unrealized(self.db, expense_id)

                # Optional: Show a brief notification (you can remove this if it's too noisy)
                # QMessageBox.information(
                #     self,
                #     "Updated",
                #     f"Expense marked as {'realized' if realized else 'unrealized'}"
                # )

            except Exception as e:
                # Revert the checkbox state if the database update failed
                checkbox.setChecked(not realized)
                QMessageBox.critical(self, "Error", f"Failed to update expense: {str(e)}")
                print(f"Error updating expense {expense_id}: {e}")

