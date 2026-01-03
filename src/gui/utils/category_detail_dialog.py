"""
Category Detail Popup Dialog for Monthly Presentation
Shows detailed category data in a separate resizable window
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QSplitter, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from src.config import get_user_names


class ExpenseDetailsDialog(QDialog):
    """Dialog for showing individual expenses for a specific category/subcategory"""

    def __init__(self, parent, category, subcategory, db, month_selector):
        super().__init__(parent)
        self.category = category
        self.subcategory = subcategory
        self.db = db
        self.month_selector = month_selector

        self.setup_ui()
        self.load_expenses()

    def setup_ui(self):
        """Set up the expense details dialog UI"""
        self.setWindowTitle(f"Expense Details - {self.category} / {self.subcategory}")
        self.setModal(False)
        self.resize(1000, 500)

        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(f"{self.category} → {self.subcategory}")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c5530; margin: 10px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        month_label = QLabel(f"Month: {self.month_selector.date().toString('MMMM yyyy')}")
        month_label.setFont(QFont("Arial", 12))
        month_label.setStyleSheet("color: #666; margin: 10px;")
        header_layout.addWidget(month_label)

        layout.addLayout(header_layout)

        # Expenses table
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Description", "Payment Method", "Realized"
        ])

        # Style the table
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setStyleSheet("""
            QTableWidget {
                background-color: #fffef8;
                alternate-background-color: #f8f6f0;
                selection-background-color: #e6f3ff;
                gridline-color: #e8e2d4;
                border: 2px solid #d4c5b9;
                border-radius: 4px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 12px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #2d3748;
            }
        """)

        # Set column widths
        header = self.expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)    # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Person
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Payment Method
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Realized

        self.expenses_table.setColumnWidth(0, 100)  # Date
        self.expenses_table.setColumnWidth(1, 80)   # Person
        self.expenses_table.setColumnWidth(2, 100)  # Amount
        self.expenses_table.setColumnWidth(4, 120)  # Payment Method
        self.expenses_table.setColumnWidth(5, 80)   # Realized

        layout.addWidget(self.expenses_table)

        # Summary section
        self.summary_label = QLabel()
        self.summary_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.summary_label.setStyleSheet("color: #2c5530; margin: 10px; padding: 10px; background-color: #f8f6f0; border-radius: 4px;")
        layout.addWidget(self.summary_label)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_expenses(self):
        """Load individual expenses for this category/subcategory"""
        try:
            # Get selected month range
            selected_date = self.month_selector.date()
            month_start = selected_date.toString("yyyy-MM-01")
            month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

            # Query expenses
            cursor = self.db.execute('''
                SELECT 
                    date, person, amount, description, 
                    payment_method, realized
                FROM expenses
                WHERE date >= ? AND date <= ? 
                    AND category = ? 
                    AND subcategory = ?
                ORDER BY date, person
            ''', (month_start, month_end, self.category, self.subcategory))

            expenses = cursor.fetchall()

            # Populate table
            self.expenses_table.setRowCount(len(expenses))

            total_amount = 0
            jeff_amount = 0
            vanessa_amount = 0

            for i, expense in enumerate(expenses):
                # Date
                self.expenses_table.setItem(i, 0, QTableWidgetItem(expense['date']))

                # Person
                self.expenses_table.setItem(i, 1, QTableWidgetItem(expense['person']))

                # Amount
                amount = expense['amount']
                amount_item = QTableWidgetItem(f"${amount:,.2f}")
                amount_item.setForeground(QColor(200, 50, 50))
                amount_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
                self.expenses_table.setItem(i, 2, amount_item)

                # Description
                self.expenses_table.setItem(i, 3, QTableWidgetItem(expense['description'] or ''))

                # Payment Method
                self.expenses_table.setItem(i, 4, QTableWidgetItem(expense['payment_method'] or ''))

                # Realized
                realized_text = "Yes" if expense['realized'] else "No"
                realized_item = QTableWidgetItem(realized_text)
                if expense['realized']:
                    realized_item.setForeground(QColor(50, 150, 50))
                self.expenses_table.setItem(i, 5, realized_item)

                # Calculate totals
                # Get user names from config
                user_a_name, user_b_name = get_user_names()
                
                total_amount += amount
                if expense['person'] == user_a_name:
                    jeff_amount += amount
                else:
                    vanessa_amount += amount

            # Update summary
            summary_text = (
                f"Total Expenses: ${total_amount:,.2f}  |  "
                f"{user_a_name}: ${jeff_amount:,.2f}  |  "
                f"{user_b_name}: ${vanessa_amount:,.2f}  |  "
                f"Count: {len(expenses)} expense(s)"
            )
            self.summary_label.setText(summary_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load expenses: {str(e)}")


class CategoryDetailDialog(QDialog):
    """Dialog for showing detailed category data in a popup window"""

    def __init__(self, parent, category, data_type, db, month_selector, category_manager):
        super().__init__(parent)
        self.category = category
        self.data_type = data_type  # 'budget_estimates' or 'budget_vs_actual'
        self.db = db
        self.month_selector = month_selector
        self.category_manager = category_manager
        self.parent_tab = parent  # Store reference to parent tab for refreshing

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle(f"{self.category} - {self.data_type.replace('_', ' ').title()}")
        self.setModal(False)  # Allow multiple dialogs to be open
        self.resize(900, 600)

        layout = QVBoxLayout(self)

        # Header with category name and month
        header_layout = QHBoxLayout()

        title_label = QLabel(f"{self.category}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c5530; margin: 10px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        month_label = QLabel(f"Month: {self.month_selector.date().toString('MMMM yyyy')}")
        month_label.setFont(QFont("Arial", 12))
        month_label.setStyleSheet("color: #666; margin: 10px;")
        header_layout.addWidget(month_label)

        layout.addLayout(header_layout)

        # Scroll area for the table
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create table widget
        self.table = QTableWidget()

        # Get user names from config
        user_a_name, user_b_name = get_user_names()
        
        # Configure table based on data type
        if self.data_type == 'budget_estimates':
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels([
                "Subcategory", "Budget Estimate", "Actual Spending"
            ])
        else:  # budget_vs_actual
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "Subcategory", "Estimate", f"{user_a_name}'s Expenses", f"{user_b_name}'s Expenses", "Total Actual", "Variance"
            ])

        # Style the table
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #fffef8;
                alternate-background-color: #f8f6f0;
                selection-background-color: #e6f3ff;
                gridline-color: #e8e2d4;
                border: 2px solid #d4c5b9;
                border-radius: 4px;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 12px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                color: #2d3748;
            }
        """)

        # Set column widths
        header = self.table.horizontalHeader()
        if self.data_type == 'budget_estimates':
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Budget Estimate
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Actual Spending
            self.table.setColumnWidth(1, 150)  # Budget Estimate
            self.table.setColumnWidth(2, 150)  # Actual Spending
        else:  # budget_vs_actual
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Estimate
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # User A
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # User B
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Total
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Variance
            self.table.setColumnWidth(1, 120)  # Estimate
            self.table.setColumnWidth(2, 130)  # User A
            self.table.setColumnWidth(3, 130)  # User B
            self.table.setColumnWidth(4, 120)  # Total
            self.table.setColumnWidth(5, 120)  # Variance

        scroll_area.setWidget(self.table)
        layout.addWidget(scroll_area)
        
        # Feature 3: Connect double-click handler for drill-down to individual expenses
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)

        # Summary section
        self.summary_group = QGroupBox("Summary")
        self.summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c5530;
                border: 2px solid #2c5530;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fffef8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #fffef8;
                color: #2c5530;
                font-weight: bold;
            }
        """)

        summary_layout = QHBoxLayout(self.summary_group)
        self.summary_labels = {}

        layout.addWidget(self.summary_group)

        # Buttons
        button_layout = QHBoxLayout()

        # Add save button for budget estimates
        if self.data_type == 'budget_estimates':
            save_btn = QPushButton("💾 Save Budget Estimates")
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c5530;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #38663d;
                }
            """)
            save_btn.clicked.connect(self.save_estimates)
            button_layout.addWidget(save_btn)

        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def load_data(self):
        """Load and populate data based on type"""
        try:
            # Get selected month
            selected_date = self.month_selector.date()
            year = selected_date.year()
            month = selected_date.month()
            month_start = selected_date.toString("yyyy-MM-01")
            month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

            # Get subcategories for this category
            categories_data = self.category_manager.get_categories()
            subcategories = categories_data.get(self.category, [])

            if self.data_type == 'budget_estimates':
                self.load_budget_estimates_data(year, month, month_start, month_end, subcategories)
            else:  # budget_vs_actual
                self.load_budget_vs_actual_data(year, month, month_start, month_end, subcategories)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def load_budget_estimates_data(self, year, month, month_start, month_end, subcategories):
        """Load budget estimates data"""
        # Get existing budget estimates for this month
        budget_estimates = {}
        cursor = self.db.execute('''
            SELECT subcategory, estimated_amount 
            FROM budget_estimates 
            WHERE category = ? AND year = ? AND month = ?
        ''', (self.category, year, month))

        for row in cursor.fetchall():
            budget_estimates[row['subcategory']] = row['estimated_amount']

        # Populate table
        self.table.setRowCount(len(subcategories) + 1)  # +1 for totals row
        total_estimate = 0
        total_actual = 0

        for i, subcategory in enumerate(subcategories):
            # Subcategory name
            subcategory_item = QTableWidgetItem(subcategory)
            subcategory_item.setFlags(subcategory_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, subcategory_item)

            # Budget estimate
            estimate = budget_estimates.get(subcategory, 0)
            estimate_item = QTableWidgetItem(f"${estimate:,.2f}")
            estimate_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 1, estimate_item)
            total_estimate += estimate

            # Actual spending
            cursor = self.db.execute('''
                SELECT COALESCE(SUM(amount), 0) as total
                FROM expenses
                WHERE date >= ? AND date <= ? AND category = ? AND subcategory = ?
            ''', (month_start, month_end, self.category, subcategory))
            actual_spending = cursor.fetchone()['total']

            actual_item = QTableWidgetItem(f"${actual_spending:,.2f}")
            actual_item.setFlags(actual_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            actual_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if actual_spending > 0:
                actual_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            self.table.setItem(i, 2, actual_item)
            total_actual += actual_spending

        # Add totals row
        totals_row = len(subcategories)
        total_font = QFont("Arial", -1, QFont.Weight.Bold)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(total_font)
        total_label.setBackground(QColor(230, 230, 230))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(totals_row, 0, total_label)

        estimate_total = QTableWidgetItem(f"${total_estimate:,.2f}")
        estimate_total.setFont(total_font)
        estimate_total.setBackground(QColor(230, 230, 230))
        estimate_total.setFlags(estimate_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        estimate_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(totals_row, 1, estimate_total)

        actual_total = QTableWidgetItem(f"${total_actual:,.2f}")
        actual_total.setFont(total_font)
        actual_total.setBackground(QColor(230, 230, 230))
        actual_total.setFlags(actual_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        actual_total.setForeground(QColor(200, 50, 50))
        actual_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(totals_row, 2, actual_total)

        # Update summary
        self.update_summary({
            'total_estimate': total_estimate,
            'total_actual': total_actual,
            'variance': total_estimate - total_actual,
            'subcategory_count': len(subcategories)
        })

    def load_budget_vs_actual_data(self, year, month, month_start, month_end, subcategories):
        """Load budget vs actual data"""
        # Get actual expenses by subcategory and person
        cursor = self.db.execute('''
            SELECT 
                subcategory,
                person,
                COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ? AND category = ?
            GROUP BY subcategory, person
            ORDER BY subcategory, person
        ''', (month_start, month_end, self.category))

        # Get user names from config
        user_a_name, user_b_name = get_user_names()
        
        actual_expenses = {}
        for row in cursor.fetchall():
            key = row['subcategory']
            if key not in actual_expenses:
                actual_expenses[key] = {user_a_name: 0, user_b_name: 0}
            actual_expenses[key][row['person']] = row['total']

        # Get budget estimates
        cursor = self.db.execute('''
            SELECT subcategory, estimated_amount
            FROM budget_estimates
            WHERE category = ? AND year = ? AND month = ?
        ''', (self.category, year, month))

        budget_estimates = {}
        for row in cursor.fetchall():
            budget_estimates[row['subcategory']] = row['estimated_amount']

        # Populate table
        self.table.setRowCount(len(subcategories) + 1)  # +1 for totals row
        category_totals = {'estimate': 0, 'jeff': 0, 'vanessa': 0, 'actual': 0, 'variance': 0}

        for i, subcategory in enumerate(subcategories):
            # Subcategory name
            self.table.setItem(i, 0, QTableWidgetItem(subcategory))

            # Get budget estimate (default to 0 if no budget set)
            estimate = budget_estimates.get(subcategory, 0)
            self.table.setItem(i, 1, QTableWidgetItem(f"${estimate:,.2f}"))

            # Get actual expenses
            user_a_actual = actual_expenses.get(subcategory, {}).get(user_a_name, 0)
            user_b_actual = actual_expenses.get(subcategory, {}).get(user_b_name, 0)
            total_actual = user_a_actual + user_b_actual

            # User A's expenses
            user_a_item = QTableWidgetItem(f"${user_a_actual:,.2f}")
            if user_a_actual > 0:
                user_a_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            self.table.setItem(i, 2, user_a_item)

            # User B's expenses
            user_b_item = QTableWidgetItem(f"${user_b_actual:,.2f}")
            if user_b_actual > 0:
                user_b_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            self.table.setItem(i, 3, user_b_item)

            # Total actual
            total_item = QTableWidgetItem(f"${total_actual:,.2f}")
            if total_actual > 0:
                total_item.setForeground(QColor(200, 50, 50))  # Red for expenses
                total_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            self.table.setItem(i, 4, total_item)

            # Variance (Estimate - Actual)
            variance = estimate - total_actual
            variance_item = QTableWidgetItem(f"${variance:,.2f}")
            if variance < 0:
                variance_item.setForeground(QColor(200, 50, 50))  # Red for over budget
                variance_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            else:
                variance_item.setForeground(QColor(50, 150, 50))  # Green for under budget
            self.table.setItem(i, 5, variance_item)

            # Add to category totals
            category_totals['estimate'] += estimate
            category_totals['jeff'] += jeff_actual
            category_totals['vanessa'] += vanessa_actual
            category_totals['actual'] += total_actual
            category_totals['variance'] += variance

        # Add totals row
        totals_row = len(subcategories)
        total_font = QFont("Arial", -1, QFont.Weight.Bold)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(total_font)
        total_label.setBackground(QColor(230, 230, 230))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(totals_row, 0, total_label)

        estimate_total = QTableWidgetItem(f"${category_totals['estimate']:,.2f}")
        estimate_total.setFont(total_font)
        estimate_total.setBackground(QColor(230, 230, 230))
        estimate_total.setFlags(estimate_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(totals_row, 1, estimate_total)

        jeff_total = QTableWidgetItem(f"${category_totals['jeff']:,.2f}")
        jeff_total.setFont(total_font)
        jeff_total.setBackground(QColor(230, 230, 230))
        jeff_total.setFlags(jeff_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        jeff_total.setForeground(QColor(200, 50, 50))
        self.table.setItem(totals_row, 2, jeff_total)

        vanessa_total = QTableWidgetItem(f"${category_totals['vanessa']:,.2f}")
        vanessa_total.setFont(total_font)
        vanessa_total.setBackground(QColor(230, 230, 230))
        vanessa_total.setFlags(vanessa_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        vanessa_total.setForeground(QColor(200, 50, 50))
        self.table.setItem(totals_row, 3, vanessa_total)

        actual_total = QTableWidgetItem(f"${category_totals['actual']:,.2f}")
        actual_total.setFont(total_font)
        actual_total.setBackground(QColor(230, 230, 230))
        actual_total.setFlags(actual_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        actual_total.setForeground(QColor(200, 50, 50))
        self.table.setItem(totals_row, 4, actual_total)

        variance_total = QTableWidgetItem(f"${category_totals['variance']:,.2f}")
        variance_total.setFont(total_font)
        variance_total.setBackground(QColor(230, 230, 230))
        variance_total.setFlags(variance_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if category_totals['variance'] < 0:
            variance_total.setForeground(QColor(200, 50, 50))
        else:
            variance_total.setForeground(QColor(50, 150, 50))
        self.table.setItem(totals_row, 5, variance_total)

        # Update summary
        self.update_summary(category_totals)

        # Connect row click handler to show individual expenses
        self.table.cellDoubleClicked.connect(self.show_expense_details)

    def show_expense_details(self, row, column):
        """Show individual expenses for the clicked subcategory"""
        # Don't show details for totals row
        if row >= self.table.rowCount() - 1:
            return

        # Get the subcategory for this row
        subcategory_item = self.table.item(row, 0)
        if not subcategory_item:
            return

        subcategory = subcategory_item.text()

        # Open expense details dialog
        dialog = ExpenseDetailsDialog(
            self, self.category, subcategory,
            self.db, self.month_selector
        )
        dialog.exec()

    def update_summary(self, totals):
        """Update the summary section"""
        # Clear existing summary
        for i in reversed(range(self.summary_group.layout().count())):
            child = self.summary_group.layout().itemAt(i).widget()
            if child:
                child.setParent(None)

        summary_layout = QHBoxLayout()

        if self.data_type == 'budget_estimates':
            # Budget estimates summary
            estimate_label = QLabel(f"Total Estimate: ${totals['total_estimate']:,.2f}")
            estimate_label.setStyleSheet("font-weight: bold; color: #2c5530; font-size: 14px;")
            summary_layout.addWidget(estimate_label)

            actual_label = QLabel(f"Total Actual: ${totals['total_actual']:,.2f}")
            actual_label.setStyleSheet("font-weight: bold; color: #d32f2f; font-size: 14px;")
            summary_layout.addWidget(actual_label)

            variance_label = QLabel(f"Variance: ${totals['variance']:,.2f}")
            variance_color = "#4caf50" if totals['variance'] >= 0 else "#d32f2f"
            variance_label.setStyleSheet(f"font-weight: bold; color: {variance_color}; font-size: 14px;")
            summary_layout.addWidget(variance_label)

        else:  # budget_vs_actual
            estimate_label = QLabel(f"Total Estimate: ${totals['estimate']:,.2f}")
            estimate_label.setStyleSheet("font-weight: bold; color: #2c5530; font-size: 14px;")
            summary_layout.addWidget(estimate_label)

            jeff_label = QLabel(f"Jeff: ${totals['jeff']:,.2f}")
            jeff_label.setStyleSheet("font-weight: bold; color: #ff9800; font-size: 14px;")
            summary_layout.addWidget(jeff_label)

            vanessa_label = QLabel(f"Vanessa: ${totals['vanessa']:,.2f}")
            vanessa_label.setStyleSheet("font-weight: bold; color: #9c27b0; font-size: 14px;")
            summary_layout.addWidget(vanessa_label)

            actual_label = QLabel(f"Total Actual: ${totals['actual']:,.2f}")
            actual_label.setStyleSheet("font-weight: bold; color: #d32f2f; font-size: 14px;")
            summary_layout.addWidget(actual_label)

            variance_label = QLabel(f"Variance: ${totals['variance']:,.2f}")
            variance_color = "#4caf50" if totals['variance'] >= 0 else "#d32f2f"
            variance_label.setStyleSheet(f"font-weight: bold; color: {variance_color}; font-size: 14px;")
            summary_layout.addWidget(variance_label)

        summary_layout.addStretch()
        self.summary_group.setLayout(summary_layout)

    def save_estimates(self):
        """Save budget estimates from the popup dialog"""
        if self.data_type != 'budget_estimates':
            return

        try:
            # Get selected month
            selected_date = self.month_selector.date()
            year = selected_date.year()
            month = selected_date.month()

            saved_count = 0
            failed_count = 0

            # Loop through table rows and save estimates (exclude totals row)
            for row in range(self.table.rowCount() - 1):  # Exclude totals row
                subcategory_item = self.table.item(row, 0)
                estimate_item = self.table.item(row, 1)

                if subcategory_item and estimate_item:
                    subcategory = subcategory_item.text()
                    estimate_text = estimate_item.text().replace("$", "").replace(",", "")

                    try:
                        estimate_amount = float(estimate_text) if estimate_text else 0.0

                        # Save to database using the BudgetEstimateModel
                        from src.database.models import BudgetEstimateModel
                        if BudgetEstimateModel.save(self.db, self.category, subcategory, estimate_amount, year, month):
                            saved_count += 1
                        else:
                            failed_count += 1

                    except ValueError:
                        # Skip invalid amounts but log the failure
                        failed_count += 1
                        continue

            # Show success message
            if saved_count > 0:
                message = f"Successfully saved {saved_count} budget estimates for {self.category} in {selected_date.toString('MMMM yyyy')}!"
                if failed_count > 0:
                    message += f"\n\n{failed_count} estimates failed to save (invalid amounts)."

                QMessageBox.information(self, "Success", message)

                # Refresh this dialog's data
                self.load_data()

                # Refresh the parent tab's data if possible
                if hasattr(self.parent_tab, 'refresh_budget_estimates_data'):
                    self.parent_tab.refresh_budget_estimates_data()
                if hasattr(self.parent_tab, 'refresh_budget_vs_actual_data'):
                    self.parent_tab.refresh_budget_vs_actual_data()

            else:
                QMessageBox.warning(self, "Warning",
                    f"No estimates were saved. {failed_count} estimates had invalid amounts.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save budget estimates: {str(e)}")
            print(f"Debug - Save error details: {e}")  # For debugging

    def on_cell_double_clicked(self, row, column):
        """
        Handle double-click on a subcategory row to show individual expenses.
        Feature 3: Double-click drill-down functionality
        """
        # Get subcategory name from the clicked row
        subcategory_item = self.table.item(row, 0)
        if not subcategory_item:
            return
        
        subcategory = subcategory_item.text()
        
        # Open expense details dialog
        expense_dialog = ExpenseDetailsDialog(
            self, 
            self.category, 
            subcategory, 
            self.db, 
            self.month_selector
        )
        expense_dialog.exec()
