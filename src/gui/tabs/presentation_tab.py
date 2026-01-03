"""
Monthly Presentation Tab
Shows monthly spending breakdown by category and unrealized expenses tracking
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *

from src.database.models import IncomeModel, ExpenseModel, BudgetEstimateModel
from src.database.category_manager import get_category_manager
from src.gui.utils.category_detail_dialog import CategoryDetailDialog
from src.config import get_user_names

class PresentationTab(QWidget):
    """Monthly presentation tab with subtabs"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.category_manager = get_category_manager()
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        """Set up the UI with tab widget"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Monthly Presentation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Month selector (shared across all tabs)
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Select Month:"))
        self.month_selector = QDateEdit()
        self.month_selector.setDisplayFormat("MMMM yyyy")
        self.month_selector.setDate(QDate.currentDate())
        self.month_selector.setCalendarPopup(True)
        self.month_selector.dateChanged.connect(self.refresh_data)
        month_layout.addWidget(self.month_selector)
        month_layout.addStretch()
        layout.addLayout(month_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Overview tab (existing functionality)
        overview_tab = QWidget()
        self.setup_overview_tab(overview_tab)
        self.tab_widget.addTab(overview_tab, "Overview")

        # Budget Estimates tab (NEW)
        budget_estimates_tab = QWidget()
        self.setup_budget_estimates_tab(budget_estimates_tab)
        self.tab_widget.addTab(budget_estimates_tab, "📊 Budget Estimates")

        # Budget vs Actual tab (existing functionality)
        budget_vs_actual_tab = QWidget()
        self.setup_budget_vs_actual_tab(budget_vs_actual_tab)
        self.tab_widget.addTab(budget_vs_actual_tab, "Budget vs Actual")

        # Unrealized expenses tab (existing functionality)
        unrealized_tab = QWidget()
        self.setup_unrealized_tab(unrealized_tab)
        self.tab_widget.addTab(unrealized_tab, "Unrealized Expenses")

        layout.addWidget(self.tab_widget)

    def setup_overview_tab(self, tab):
        """Set up the overview tab with existing functionality"""
        layout = QVBoxLayout(tab)

        # Summary section
        summary_layout = QHBoxLayout()
        
        # Get user names from config
        user_a_name, user_b_name = get_user_names()

        # Income summary
        income_group = QGroupBox("Income Summary")
        income_layout = QVBoxLayout()
        self.user_a_income_label = QLabel(f"{user_a_name}: $0.00")
        self.user_b_income_label = QLabel(f"{user_b_name}: $0.00")
        self.total_income_label = QLabel("Total: $0.00")
        self.total_income_label.setStyleSheet("font-weight: bold;")
        income_layout.addWidget(self.user_a_income_label)
        income_layout.addWidget(self.user_b_income_label)
        income_layout.addWidget(self.total_income_label)
        income_group.setLayout(income_layout)
        summary_layout.addWidget(income_group)

        # Expense summary
        expense_group = QGroupBox("Expense Summary")
        expense_layout = QVBoxLayout()
        self.user_a_expense_label = QLabel(f"{user_a_name}: $0.00")
        self.user_b_expense_label = QLabel(f"{user_b_name}: $0.00")
        self.total_expense_label = QLabel("Total: $0.00")
        self.total_expense_label.setStyleSheet("font-weight: bold;")
        expense_layout.addWidget(self.user_a_expense_label)
        expense_layout.addWidget(self.user_b_expense_label)
        expense_layout.addWidget(self.total_expense_label)
        expense_group.setLayout(expense_layout)
        summary_layout.addWidget(expense_group)

        layout.addLayout(summary_layout)

        # Category breakdown table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "Subcategory", "Budgeted", "Actual", "Variance"
        ])
        self.category_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.category_table)
        
        # Spending summary table (replacing chart)
        spending_group = QGroupBox("Monthly Spending Summary")
        spending_layout = QVBoxLayout()

        self.spending_table = QTableWidget()
        self.spending_table.setColumnCount(3)
        self.spending_table.setHorizontalHeaderLabels([
            "Category", "Amount", "Percentage"
        ])
        self.spending_table.horizontalHeader().setStretchLastSection(True)
        self.spending_table.setMaximumHeight(300)
        spending_layout.addWidget(self.spending_table)

        spending_group.setLayout(spending_layout)
        layout.addWidget(spending_group)

        # Spending chart
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        layout.addWidget(self.chart_view)

    def setup_budget_estimates_tab(self, tab):
        """Set up the budget estimates tab"""
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "This tab allows you to set and adjust budget estimates for each category and subcategory. "
            "Enter your desired budget amounts and click 'Save Budgets' to apply the changes."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px; font-size: 12px;")
        layout.addWidget(instructions)

        # Controls section
        controls_layout = QHBoxLayout()

        # Save budgets button
        save_budgets_btn = QPushButton("Save Budgets")
        save_budgets_btn.clicked.connect(self.save_budget_estimates)
        save_budgets_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5530;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #38663d;
            }
        """)
        controls_layout.addWidget(save_budgets_btn)
        
        # Feature 4: Copy from Previous Month button
        copy_prev_btn = QPushButton("📋 Copy from Previous Month")
        copy_prev_btn.clicked.connect(self.copy_from_previous_month)
        copy_prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
        """)
        controls_layout.addWidget(copy_prev_btn)
        
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Create scroll area for budget tables
        self.budget_scroll_area = QScrollArea()
        self.budget_scroll_area.setWidgetResizable(True)
        self.budget_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.budget_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget to contain all budget tables
        self.budgets_widget = QWidget()
        self.budgets_layout = QVBoxLayout(self.budgets_widget)
        self.budgets_layout.setSpacing(15)

        self.budget_scroll_area.setWidget(self.budgets_widget)
        layout.addWidget(self.budget_scroll_area)

        # Store references to budget tables for updates
        self.budget_tables = {}

    def setup_budget_vs_actual_tab(self, tab):
        """Set up the budget vs actual tab with category-specific tables"""
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "This tab shows detailed budget vs actual analysis for each category. "
            "Each category displays subcategories with estimates vs actual spending by person."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px; font-size: 12px;")
        layout.addWidget(instructions)

        # Controls section
        controls_layout = QHBoxLayout()

        # Refresh button
        refresh_btn = QPushButton("Refresh Analysis")
        refresh_btn.clicked.connect(self.refresh_budget_vs_actual_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5530;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #38663d;
            }
        """)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Create scroll area for category tables
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget to contain all category tables
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(15)

        scroll_area.setWidget(self.categories_widget)
        layout.addWidget(scroll_area)

        # Store references to category tables for updates
        self.category_tables = {}

    def setup_unrealized_tab(self, tab):
        """Set up the unrealized expenses tab"""
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel("This shows expenses that haven't been taken out of the joint checking account yet.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Summary section for unrealized expenses
        summary_layout = QHBoxLayout()
        
        # Get user names from config
        user_a_name, user_b_name = get_user_names()

        # Unrealized expenses summary
        unrealized_group = QGroupBox("Unrealized Expenses to Withdraw")
        unrealized_layout = QVBoxLayout()
        self.user_a_unrealized_label = QLabel(f"{user_a_name}: $0.00")
        self.user_b_unrealized_label = QLabel(f"{user_b_name}: $0.00")
        self.total_unrealized_label = QLabel("Total to Withdraw: $0.00")
        self.total_unrealized_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f;")
        unrealized_layout.addWidget(self.user_a_unrealized_label)
        unrealized_layout.addWidget(self.user_b_unrealized_label)
        unrealized_layout.addWidget(QLabel(""))  # Spacer
        unrealized_layout.addWidget(self.total_unrealized_label)
        unrealized_group.setLayout(unrealized_layout)
        summary_layout.addWidget(unrealized_group)
        summary_layout.addStretch()

        layout.addLayout(summary_layout)

        # Unrealized expenses table
        self.unrealized_table = QTableWidget()
        self.unrealized_table.setColumnCount(7)
        self.unrealized_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Category", "Subcategory", "Description", "Actions"
        ])
        self.unrealized_table.horizontalHeader().setStretchLastSection(True)
        self.unrealized_table.setAlternatingRowColors(True)
        layout.addWidget(self.unrealized_table)

    def refresh_data(self):
        """Refresh presentation data for all tabs"""
        self.refresh_overview_data()
        self.refresh_budget_estimates_data()
        self.refresh_budget_vs_actual_data()
        self.refresh_unrealized_data()

    def refresh_overview_data(self):
        """Refresh data for the overview tab"""
        # Get selected month range - always use first day of month to avoid issues
        selected_date = self.month_selector.date()
        # Force to first day of month to ensure correct range calculation
        first_of_month = QDate(selected_date.year(), selected_date.month(), 1)
        month_start = first_of_month.toString("yyyy-MM-dd")
        # Calculate end as first day of next month minus 1 day
        month_end = first_of_month.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Get income by person
        cursor = self.db.execute('''
            SELECT person, COALESCE(SUM(amount), 0) as total
            FROM income
            WHERE date >= ? AND date <= ?
            GROUP BY person
        ''', (month_start, month_end))

        # Get user names from config
        user_a_name, user_b_name = get_user_names()
        
        income_by_person = {row['person']: row['total'] for row in cursor.fetchall()}
        user_a_income = income_by_person.get(user_a_name, 0)
        user_b_income = income_by_person.get(user_b_name, 0)
        total_income = user_a_income + user_b_income

        self.user_a_income_label.setText(f"{user_a_name}: ${user_a_income:,.2f}")
        self.user_b_income_label.setText(f"{user_b_name}: ${user_b_income:,.2f}")
        self.total_income_label.setText(f"Total: ${total_income:,.2f}")

        # Get expenses by person
        cursor = self.db.execute('''
            SELECT person, COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY person
        ''', (month_start, month_end))

        expenses_by_person = {row['person']: row['total'] for row in cursor.fetchall()}
        user_a_expenses = expenses_by_person.get(user_a_name, 0)
        user_b_expenses = expenses_by_person.get(user_b_name, 0)
        total_expenses = user_a_expenses + user_b_expenses

        self.user_a_expense_label.setText(f"{user_a_name}: ${user_a_expenses:,.2f}")
        self.user_b_expense_label.setText(f"{user_b_name}: ${user_b_expenses:,.2f}")
        self.total_expense_label.setText(f"Total: ${total_expenses:,.2f}")

        # Update category table
        categories = ExpenseModel.get_by_category(self.db, month_start, month_end)

        self.category_table.setRowCount(len(categories))
        for i, cat in enumerate(categories):
            self.category_table.setItem(i, 0, QTableWidgetItem(cat['category']))
            self.category_table.setItem(i, 1, QTableWidgetItem(cat['subcategory'] or ""))
            self.category_table.setItem(i, 2, QTableWidgetItem("$0.00"))  # Budgeted placeholder
            self.category_table.setItem(i, 3, QTableWidgetItem(f"${cat['total']:.2f}"))

            variance = 0 - cat['total']  # Since no budget set
            variance_item = QTableWidgetItem(f"${variance:.2f}")
            if variance < 0:
                variance_item.setForeground(QColor(244, 67, 54))
            else:
                variance_item.setForeground(QColor(76, 175, 80))
            self.category_table.setItem(i, 4, variance_item)

        # Update spending summary table
        self.update_spending_summary(month_start, month_end)

        # Update spending chart
        self.update_spending_chart(month_start, month_end)

    def update_spending_summary(self, month_start, month_end):
        """Update spending summary table for overview tab"""
        # Get category data
        categories = ExpenseModel.get_by_category(self.db, month_start, month_end)

        if not categories:
            # Clear table if no data
            self.spending_table.setRowCount(0)
            return

        # Calculate total expenses for percentage calculations
        total_expenses = sum(cat['total'] for cat in categories)

        # Update table rows
        self.spending_table.setRowCount(len(categories))

        for i, cat in enumerate(categories):
            category_name = cat['category']
            if cat['subcategory']:
                category_name += f" - {cat['subcategory']}"

            self.spending_table.setItem(i, 0, QTableWidgetItem(category_name))
            self.spending_table.setItem(i, 1, QTableWidgetItem(f"${cat['total']:.2f}"))

            # Calculate percentage of total expenses
            percentage = (cat['total'] / total_expenses * 100) if total_expenses > 0 else 0
            self.spending_table.setItem(i, 2, QTableWidgetItem(f"{percentage:.1f}%"))

        # Add totals row
        totals_row = self.spending_table.rowCount()
        self.spending_table.insertRow(totals_row)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(QFont("Arial", -1, QFont.Weight.Bold))
        total_label.setBackground(QColor(230, 230, 230))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.spending_table.setItem(totals_row, 0, total_label)

        amount_total = QTableWidgetItem(f"${total_expenses:,.2f}")
        amount_total.setFont(QFont("Arial", -1, QFont.Weight.Bold))
        amount_total.setBackground(QColor(230, 230, 230))
        amount_total.setFlags(amount_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.spending_table.setItem(totals_row, 1, amount_total)

        # Total percentage should be 100%
        percentage_total = QTableWidgetItem("100.0%")
        percentage_total.setFont(QFont("Arial", -1, QFont.Weight.Bold))
        percentage_total.setBackground(QColor(230, 230, 230))
        percentage_total.setFlags(percentage_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.spending_table.setItem(totals_row, 2, percentage_total)

    def refresh_budget_estimates_data(self):
        """Refresh the budget estimates tab"""
        # Feature 4: Auto-populate from defaults if no estimates exist
        selected_date = self.month_selector.date()
        year = selected_date.year()
        month = selected_date.month()
        
        # Check if this month has any estimates
        existing = self.db.execute('''
            SELECT COUNT(*) as count FROM budget_estimates
            WHERE year = ? AND month = ?
        ''', (year, month)).fetchone()
        
        if existing and existing['count'] == 0:
            # Try to apply defaults first
            applied = BudgetEstimateModel.apply_defaults_to_month(self.db, year, month)
            if applied == 0:
                # No defaults found, try copying from previous month
                copied = BudgetEstimateModel.copy_from_previous_month(self.db, year, month)
                if copied > 0:
                    QMessageBox.information(
                        self, "Auto-Populated",
                        f"Copied {copied} estimates from the previous month."
                    )
            else:
                QMessageBox.information(
                    self, "Auto-Populated",
                    f"Applied {applied} default estimates to this month."
                )
        
        # Clear existing tables
        for i in reversed(range(self.budgets_layout.count())):
            child = self.budgets_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.budget_tables.clear()

        # Get all categories and their subcategories
        categories_data = self.category_manager.get_categories()

        # Create budget tables for each category
        for category, subcategories in categories_data.items():
            if subcategories:  # Only create table if category has subcategories
                self.create_budget_table(category, subcategories)

        # Add stretch at the end
        self.budgets_layout.addStretch()

    def save_budget_estimates(self):
        """Save all budget estimates to the database"""
        try:
            # Get selected month
            selected_date = self.month_selector.date()
            year = selected_date.year()
            month = selected_date.month()

            saved_count = 0
            failed_count = 0

            # Loop through all budget tables and save estimates
            for category, table_data in self.budget_tables.items():
                # Get the actual table from the dictionary
                table = table_data['table'] if isinstance(table_data, dict) else table_data

                for row in range(table.rowCount() - 1):  # Exclude totals row
                    subcategory_item = table.item(row, 0)
                    estimate_item = table.item(row, 1)
                    
                    # Feature 4: Get the default checkbox state
                    checkbox_widget = table.cellWidget(row, 3)
                    is_default = False
                    if checkbox_widget:
                        checkbox = checkbox_widget.findChild(QCheckBox)
                        if checkbox:
                            is_default = checkbox.isChecked()

                    if subcategory_item and estimate_item:
                        subcategory = subcategory_item.text()
                        estimate_text = estimate_item.text().replace("$", "").replace(",", "")

                        try:
                            estimate_amount = float(estimate_text) if estimate_text else 0.0

                            # Feature 4: Save with default flag using new method
                            if BudgetEstimateModel.save_with_default(
                                self.db, category, subcategory, estimate_amount, 
                                year, month, is_default
                            ):
                                saved_count += 1
                            else:
                                failed_count += 1

                        except ValueError:
                            # Skip invalid amounts but log the failure
                            failed_count += 1
                            continue

            # Show success message
            if saved_count > 0:
                message = f"Successfully saved {saved_count} budget estimates for {selected_date.toString('MMMM yyyy')}!"
                if failed_count > 0:
                    message += f"\n\n{failed_count} estimates failed to save (invalid amounts)."

                QMessageBox.information(self, "Success", message)

                # Refresh the budget vs actual tab to show new estimates
                self.refresh_budget_vs_actual_data()
            else:
                QMessageBox.warning(self, "Warning",
                    f"No estimates were saved. {failed_count} estimates had invalid amounts.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save budget estimates: {str(e)}")
            print(f"Debug - Save error details: {e}")  # For debugging

    def copy_from_previous_month(self):
        """
        Feature 4: Copy budget estimates from the previous month
        """
        try:
            selected_date = self.month_selector.date()
            year = selected_date.year()
            month = selected_date.month()
            
            # Ask for confirmation
            reply = QMessageBox.question(
                self, "Copy from Previous Month",
                f"This will copy all budget estimates from the previous month to {selected_date.toString('MMMM yyyy')}. "
                "Any existing estimates for this month will be overwritten. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                copied = BudgetEstimateModel.copy_from_previous_month(self.db, year, month)
                
                if copied > 0:
                    QMessageBox.information(
                        self, "Success",
                        f"Copied {copied} budget estimates from the previous month!"
                    )
                    # Refresh the display
                    self.refresh_budget_estimates_data()
                else:
                    QMessageBox.warning(
                        self, "No Data",
                        "No budget estimates found in the previous month to copy."
                    )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy estimates: {str(e)}")

    def create_budget_table(self, category, subcategories):
        """Create a budget table for a specific category"""
        # Get selected month - always use first day of month
        selected_date = self.month_selector.date()
        year = selected_date.year()
        month = selected_date.month()
        first_of_month = QDate(year, month, 1)
        month_start = first_of_month.toString("yyyy-MM-dd")
        month_end = first_of_month.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Get existing budget estimates for this month
        budget_estimates = {}
        default_flags = {}  # Feature 4: Track which estimates are defaults
        cursor = self.db.execute('''
            SELECT subcategory, estimated_amount, is_default
            FROM budget_estimates 
            WHERE category = ? AND year = ? AND month = ?
        ''', (category, year, month))

        for row in cursor.fetchall():
            budget_estimates[row['subcategory']] = row['estimated_amount']
            default_flags[row['subcategory']] = bool(row['is_default'])

        # Create group box for the category
        category_group = QGroupBox(f"{category} - Budget Estimates")
        category_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c5530;
                border: 3px solid #2c5530;
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
                font-size: 14px;
            }
        """)

        category_layout = QVBoxLayout(category_group)

        # Add resize controls
        resize_controls = QHBoxLayout()

        # Collapse/Expand button
        collapse_btn = QPushButton("⬆ Collapse")
        collapse_btn.setMaximumWidth(100)
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        # Show All Rows button
        show_all_btn = QPushButton("📋 Show All Rows")
        show_all_btn.setMaximumWidth(120)
        show_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5530;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #38663d;
            }
        """)

        resize_controls.addWidget(collapse_btn)
        resize_controls.addWidget(show_all_btn)
        resize_controls.addStretch()

        category_layout.addLayout(resize_controls)

        # Create splitter for resizable table
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2c5530;
                border: 1px solid #1e3d24;
                border-radius: 2px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #38663d;
            }
        """)

        # Create table for this category
        table = QTableWidget()
        table.setColumnCount(4)  # Feature 4: Added column for "Set as Default"
        table.setHorizontalHeaderLabels([
            "Subcategory", "Budget Estimate", "Actual Spending", "Default"
        ])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Budget Estimate
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Actual Spending
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Default checkbox

        table.setColumnWidth(1, 140)  # Budget Estimate
        table.setColumnWidth(2, 120)  # Actual Spending
        table.setColumnWidth(3, 70)   # Default checkbox

        # Style the table
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #fffef8;
                alternate-background-color: #f8f6f0;
                selection-background-color: #e6f3ff;
                gridline-color: #e8e2d4;
                border: 2px solid #d4c5b9;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 8px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
                color: #2d3748;
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 4px;
                border-radius: 2px;
            }
        """)

        # Populate table with subcategories
        table.setRowCount(len(subcategories))
        total_estimate = 0
        total_actual = 0

        for i, subcategory in enumerate(subcategories):
            # Subcategory name
            subcategory_item = QTableWidgetItem(subcategory)
            subcategory_item.setFlags(subcategory_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(i, 0, subcategory_item)

            # Budget estimate (editable)
            estimate = budget_estimates.get(subcategory, 0)
            estimate_item = QTableWidgetItem(f"{estimate:,.2f}")
            estimate_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(i, 1, estimate_item)
            total_estimate += estimate

            # Actual spending (read-only)
            cursor = self.db.execute('''
                SELECT COALESCE(SUM(amount), 0) as total
                FROM expenses
                WHERE date >= ? AND date <= ? AND category = ? AND subcategory = ?
            ''', (month_start, month_end, category, subcategory))
            actual_spending = cursor.fetchone()['total']

            actual_item = QTableWidgetItem(f"${actual_spending:,.2f}")
            actual_item.setFlags(actual_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            actual_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if actual_spending > 0:
                actual_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            table.setItem(i, 2, actual_item)
            total_actual += actual_spending
            
            # Feature 4: Add "Set as Default" checkbox
            is_default = default_flags.get(subcategory, False)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            default_checkbox = QCheckBox()
            default_checkbox.setChecked(is_default)
            default_checkbox.setToolTip("Check to use this as default for future months")
            checkbox_layout.addWidget(default_checkbox)
            
            table.setCellWidget(i, 3, checkbox_widget)

        # Add totals row
        totals_row = table.rowCount()
        table.insertRow(totals_row)

        # Style totals row
        total_font = QFont("Arial", -1, QFont.Weight.Bold)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(total_font)
        total_label.setBackground(QColor(230, 230, 230))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(totals_row, 0, total_label)

        estimate_total = QTableWidgetItem(f"{total_estimate:,.2f}")
        estimate_total.setFont(total_font)
        estimate_total.setBackground(QColor(230, 230, 230))
        estimate_total.setFlags(estimate_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        estimate_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        table.setItem(totals_row, 1, estimate_total)

        actual_total = QTableWidgetItem(f"${total_actual:,.2f}")
        actual_total.setFont(total_font)
        actual_total.setBackground(QColor(230, 230, 230))
        actual_total.setFlags(actual_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
        actual_total.setForeground(QColor(200, 50, 50))
        actual_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        table.setItem(totals_row, 2, actual_total)

        # Set initial table height based on content with better sizing
        table.resizeRowsToContents()
        row_height = table.rowHeight(0) if table.rowCount() > 0 else 30
        header_height = table.horizontalHeader().height()
        total_height = (row_height * table.rowCount()) + header_height + 40

        # Set more flexible sizing - start collapsed but allow expansion
        initial_height = min(total_height, 200)  # Start with reasonable size
        table.setMinimumHeight(100)  # Allow smaller collapse
        table.setMaximumHeight(16777215)  # Remove height restriction (Qt max)
        table.resize(table.width(), initial_height)

        # Add table to splitter
        splitter.addWidget(table)
        splitter.setSizes([initial_height])

        # Connect resize buttons
        def toggle_collapse():
            current_size = splitter.sizes()[0]
            if current_size <= 120:  # Currently collapsed
                # Expand to show all rows
                splitter.setSizes([total_height])
                collapse_btn.setText("⬆ Collapse")
            else:
                # Collapse to minimal size
                splitter.setSizes([100])
                collapse_btn.setText("⬇ Expand")

        def show_all_rows():
            # Open popup dialog with all category data
            dialog = CategoryDetailDialog(
                self, category, 'budget_estimates',
                self.db, self.month_selector, self.category_manager
            )
            dialog.show()

        collapse_btn.clicked.connect(toggle_collapse)
        show_all_btn.clicked.connect(show_all_rows)

        category_layout.addWidget(splitter)

        # Store table reference with splitter info
        self.budget_tables[category] = {
            'table': table,
            'splitter': splitter,
            'collapse_btn': collapse_btn,
            'total_height': total_height
        }

        # Add to main layout
        self.budgets_layout.addWidget(category_group)

    def refresh_budget_vs_actual_data(self):
        """Refresh data for the budget vs actual tab with category-specific tables"""
        # Get selected month range - always use first day of month
        selected_date = self.month_selector.date()
        first_of_month = QDate(selected_date.year(), selected_date.month(), 1)
        month_start = first_of_month.toString("yyyy-MM-dd")
        month_end = first_of_month.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Clear existing tables
        for i in reversed(range(self.categories_layout.count())):
            child = self.categories_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.category_tables.clear()

        # Get all categories and their subcategories
        categories_data = self.category_manager.get_categories()

        # Get actual expenses by category, subcategory, and person
        cursor = self.db.execute('''
            SELECT 
                category,
                subcategory,
                person,
                COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category, subcategory, person
            ORDER BY category, subcategory, person
        ''', (month_start, month_end))

        actual_expenses = {}
        for row in cursor.fetchall():
            key = (row['category'], row['subcategory'])
            if key not in actual_expenses:
                actual_expenses[key] = {'Jeff': 0, 'Vanessa': 0}
            actual_expenses[key][row['person']] = row['total']

        # Get budget estimates instead of budget targets
        year = selected_date.year()
        month = selected_date.month()
        cursor = self.db.execute('''
            SELECT category, subcategory, estimated_amount
            FROM budget_estimates
            WHERE year = ? AND month = ?
        ''', (year, month))

        budget_estimates = {}
        for row in cursor.fetchall():
            key = (row['category'], row['subcategory'])
            budget_estimates[key] = row['estimated_amount']

        # Create tables for each category that has either expenses or budget
        all_category_keys = set(actual_expenses.keys()) | set(budget_estimates.keys())
        categories_with_data = {}

        for key in all_category_keys:
            category = key[0]
            if category not in categories_with_data:
                categories_with_data[category] = []
            categories_with_data[category].append(key[1])

        # Add categories from category manager that don't have data but should be shown
        for category, subcategories in categories_data.items():
            if category not in categories_with_data:
                categories_with_data[category] = subcategories
            else:
                # Add any missing subcategories
                for subcat in subcategories:
                    if subcat not in categories_with_data[category]:
                        categories_with_data[category].append(subcat)

        # Create tables for each category
        for category, subcategories in categories_with_data.items():
            self.create_category_table(category, subcategories, actual_expenses, budget_estimates)

        # Add stretch at the end
        self.categories_layout.addStretch()

    def create_category_table(self, category, subcategories, actual_expenses, budget_estimates):
        """Create a table for a specific category"""
        # Create group box for the category
        category_group = QGroupBox(f"{category} - Budget vs Actual")
        category_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c5530;
                border: 3px solid #2c5530;
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
                font-size: 14px;
            }
        """)

        category_layout = QVBoxLayout(category_group)

        # Add resize controls
        resize_controls = QHBoxLayout()

        # Collapse/Expand button
        collapse_btn = QPushButton("⬆ Collapse")
        collapse_btn.setMaximumWidth(100)
        collapse_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)

        # Show All Rows button
        show_all_btn = QPushButton("📊 Show All Data")
        show_all_btn.setMaximumWidth(120)
        show_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5530;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #38663d;
            }
        """)

        resize_controls.addWidget(collapse_btn)
        resize_controls.addWidget(show_all_btn)
        resize_controls.addStretch()

        category_layout.addLayout(resize_controls)

        # Create splitter for resizable table
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(5)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2c5530;
                border: 1px solid #1e3d24;
                border-radius: 2px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #38663d;
            }
        """)

        # Create table for this category
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Subcategory", "Estimate", "Jeff's Expenses", "Vanessa's Expenses", "Total Actual", "Variance"
        ])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Estimate
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Jeff
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Vanessa
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Total
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Variance

        table.setColumnWidth(1, 100)  # Estimate
        table.setColumnWidth(2, 120)  # Jeff
        table.setColumnWidth(3, 120)  # Vanessa
        table.setColumnWidth(4, 100)  # Total
        table.setColumnWidth(5, 100)  # Variance

        # Style the table
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #fffef8;
                alternate-background-color: #f8f6f0;
                selection-background-color: #e6f3ff;
                gridline-color: #e8e2d4;
                border: 2px solid #d4c5b9;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 8px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
                color: #2d3748;
            }
        """)

        # Populate table with subcategories
        table.setRowCount(len(subcategories))
        category_totals = {'estimate': 0, 'jeff': 0, 'vanessa': 0, 'actual': 0, 'variance': 0}

        for i, subcategory in enumerate(subcategories):
            # Subcategory name
            table.setItem(i, 0, QTableWidgetItem(subcategory))

            # Get budget estimate (default to 0 if no budget set)
            key = (category, subcategory)
            estimate = budget_estimates.get(key, 0)
            table.setItem(i, 1, QTableWidgetItem(f"${estimate:,.2f}"))

            # Get actual expenses
            jeff_actual = actual_expenses.get(key, {}).get('Jeff', 0)
            vanessa_actual = actual_expenses.get(key, {}).get('Vanessa', 0)
            total_actual = jeff_actual + vanessa_actual

            # Jeff's expenses
            jeff_item = QTableWidgetItem(f"${jeff_actual:,.2f}")
            if jeff_actual > 0:
                jeff_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            table.setItem(i, 2, jeff_item)

            # Vanessa's expenses
            vanessa_item = QTableWidgetItem(f"${vanessa_actual:,.2f}")
            if vanessa_actual > 0:
                vanessa_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            table.setItem(i, 3, vanessa_item)

            # Total actual
            total_item = QTableWidgetItem(f"${total_actual:,.2f}")
            if total_actual > 0:
                total_item.setForeground(QColor(200, 50, 50))  # Red for expenses
                total_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            table.setItem(i, 4, total_item)

            # Variance (Estimate - Actual)
            variance = estimate - total_actual
            variance_item = QTableWidgetItem(f"${variance:,.2f}")
            if variance < 0:
                variance_item.setForeground(QColor(200, 50, 50))  # Red for over budget
                variance_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            else:
                variance_item.setForeground(QColor(50, 150, 50))  # Green for under budget
            table.setItem(i, 5, variance_item)

            # Add to category totals
            category_totals['estimate'] += estimate
            category_totals['jeff'] += jeff_actual
            category_totals['vanessa'] += vanessa_actual
            category_totals['actual'] += total_actual
            category_totals['variance'] += variance

        # Add totals row
        totals_row = table.rowCount()
        table.insertRow(totals_row)

        # Style totals row
        total_font = QFont("Arial", -1, QFont.Weight.Bold)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(total_font)
        total_label.setBackground(QColor(230, 230, 230))
        total_label.setFlags(total_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(totals_row, 0, total_label)

        estimate_total = QTableWidgetItem(f"${category_totals['estimate']:,.2f}")
        estimate_total.setFont(total_font)
        estimate_total.setBackground(QColor(230, 230, 230))
        table.setItem(totals_row, 1, estimate_total)

        jeff_total = QTableWidgetItem(f"${category_totals['jeff']:,.2f}")
        jeff_total.setFont(total_font)
        jeff_total.setBackground(QColor(230, 230, 230))
        jeff_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 2, jeff_total)

        vanessa_total = QTableWidgetItem(f"${category_totals['vanessa']:,.2f}")
        vanessa_total.setFont(total_font)
        vanessa_total.setBackground(QColor(230, 230, 230))
        vanessa_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 3, vanessa_total)

        actual_total = QTableWidgetItem(f"${category_totals['actual']:,.2f}")
        actual_total.setFont(total_font)
        actual_total.setBackground(QColor(230, 230, 230))
        actual_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 4, actual_total)

        variance_total = QTableWidgetItem(f"${category_totals['variance']:,.2f}")
        variance_total.setFont(total_font)
        variance_total.setBackground(QColor(230, 230, 230))
        if category_totals['variance'] < 0:
            variance_total.setForeground(QColor(200, 50, 50))
        else:
            variance_total.setForeground(QColor(50, 150, 50))
        table.setItem(totals_row, 5, variance_total)

        # Set initial table height based on content with better sizing
        table.resizeRowsToContents()
        row_height = table.rowHeight(0) if table.rowCount() > 0 else 30
        header_height = table.horizontalHeader().height()
        total_height = (row_height * table.rowCount()) + header_height + 40

        # Set more flexible sizing - start collapsed but allow expansion
        initial_height = min(total_height, 200)  # Start with reasonable size
        table.setMinimumHeight(100)  # Allow smaller collapse
        table.setMaximumHeight(16777215)  # Remove height restriction (Qt max)
        table.resize(table.width(), initial_height)

        # Add table to splitter
        splitter.addWidget(table)
        splitter.setSizes([initial_height])

        # Connect resize buttons
        def toggle_collapse():
            current_size = splitter.sizes()[0]
            if current_size <= 120:  # Currently collapsed
                # Expand to show all rows
                splitter.setSizes([total_height])
                collapse_btn.setText("⬆ Collapse")
            else:
                # Collapse to minimal size
                splitter.setSizes([100])
                collapse_btn.setText("⬇ Expand")

        def show_all_data():
            # Open popup dialog with all category data
            dialog = CategoryDetailDialog(
                self, category, 'budget_vs_actual',
                self.db, self.month_selector, self.category_manager
            )
            dialog.show()

        collapse_btn.clicked.connect(toggle_collapse)
        show_all_btn.clicked.connect(show_all_data)

        category_layout.addWidget(splitter)

        # Store table reference with splitter info
        self.category_tables[category] = {
            'table': table,
            'splitter': splitter,
            'collapse_btn': collapse_btn,
            'total_height': total_height
        }

        # Add to main layout
        self.categories_layout.addWidget(category_group)

    def refresh_unrealized_data(self):
        """Refresh data for the unrealized expenses tab"""
        # Get selected month range - always use first day of month
        selected_date = self.month_selector.date()
        first_of_month = QDate(selected_date.year(), selected_date.month(), 1)
        month_start = first_of_month.toString("yyyy-MM-dd")
        month_end = first_of_month.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Get user names from config
        user_a_name, user_b_name = get_user_names()
        
        # Get unrealized expenses by person
        unrealized_by_person = ExpenseModel.get_unrealized_by_person(self.db, month_start, month_end)
        unrealized_dict = {row['person']: row['total'] for row in unrealized_by_person}

        user_a_unrealized = unrealized_dict.get(user_a_name, 0)
        user_b_unrealized = unrealized_dict.get(user_b_name, 0)
        total_unrealized = user_a_unrealized + user_b_unrealized

        self.user_a_unrealized_label.setText(f"{user_a_name}: ${user_a_unrealized:,.2f}")
        self.user_b_unrealized_label.setText(f"{user_b_name}: ${user_b_unrealized:,.2f}")
        self.total_unrealized_label.setText(f"Total to Withdraw: ${total_unrealized:,.2f}")

        # Get all unrealized expenses
        unrealized_expenses = ExpenseModel.get_unrealized_expenses(self.db, month_start, month_end)

        self.unrealized_table.setRowCount(len(unrealized_expenses))
        for i, expense in enumerate(unrealized_expenses):
            self.unrealized_table.setItem(i, 0, QTableWidgetItem(expense['date']))
            self.unrealized_table.setItem(i, 1, QTableWidgetItem(expense['person']))
            self.unrealized_table.setItem(i, 2, QTableWidgetItem(f"${expense['amount']:.2f}"))
            self.unrealized_table.setItem(i, 3, QTableWidgetItem(expense['category']))
            self.unrealized_table.setItem(i, 4, QTableWidgetItem(expense['subcategory'] or ""))
            self.unrealized_table.setItem(i, 5, QTableWidgetItem(expense['description'] or ""))

            # Add "Mark as Realized" button
            mark_button = QPushButton("Mark as Realized")
            mark_button.clicked.connect(lambda checked, exp_id=expense['id']: self.mark_expense_realized(exp_id))
            mark_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 5px; }")
            self.unrealized_table.setCellWidget(i, 6, mark_button)

    def update_spending_chart(self, month_start, month_end):
        """Update spending chart for overview tab"""
        try:
            # Get category data
            categories = ExpenseModel.get_by_category(self.db, month_start, month_end)

            if not categories:
                # Clear chart if no data
                self.chart_view.setChart(QChart())
                return

            # Create pie series
            series = QPieSeries()

            # Add data to series
            for cat in categories:
                category_name = cat['category']
                if cat['subcategory']:
                    category_name += f" - {cat['subcategory']}"

                series.append(category_name, cat['total'])

            # Create chart
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Monthly Spending by Category")
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

            # Set chart to view
            self.chart_view.setChart(chart)
        except Exception as e:
            print(f"Error updating spending chart: {e}")
            # Show empty chart on error
            self.chart_view.setChart(QChart())

    def mark_expense_realized(self, expense_id):
        """Mark an expense as realized (withdrawn from joint account)"""
        try:
            # Update the expense to mark it as realized
            cursor = self.db.execute('''
                UPDATE expenses 
                SET realized = 1 
                WHERE id = ?
            ''', (expense_id,))

            self.db.commit()

            if cursor.rowcount > 0:
                QMessageBox.information(self, "Success", "Expense marked as realized!")
                # Refresh the unrealized expenses data
                self.refresh_unrealized_data()
            else:
                QMessageBox.warning(self, "Warning", "Could not find expense to update.")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to mark expense as realized: {str(e)}")
            print(f"Debug - Mark realized error: {e}")  # For debugging
