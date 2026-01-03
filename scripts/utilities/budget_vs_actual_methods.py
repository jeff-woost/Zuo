"""
Budget vs Actual Analysis Methods for Monthly Presentation Tab
============================================================

This module contains the enhanced implementation for category-wise budget analysis
in the Monthly Presentation tab. It provides detailed budget vs actual reporting
with visual tables showing variance analysis across all expense categories.

Key Features:
- Category-specific budget vs actual tables
- Subcategory-level detail with person breakdowns
- Visual variance indicators (over/under budget)
- Interactive category tables with summary totals
- Monthly budget estimation capabilities
- Real-time data refresh and analysis

The module implements sophisticated budget analysis that helps users understand
their spending patterns and identify areas where they're over or under budget.
Each category gets its own detailed table showing estimated vs actual spending.

Functions:
    setup_budget_vs_actual_tab(): Initialize the budget analysis interface
    refresh_budget_vs_actual_data(): Update all budget analysis data
    create_category_table(): Generate individual category analysis tables

Dependencies:
    - PyQt6: GUI framework components for table creation
    - database.db_manager: Database access for budget and expense data
    - database.category_manager: Category organization and validation
"""

from src.config import get_user_names

def setup_budget_vs_actual_tab(self, tab):
    """
    Set up the budget vs actual analysis tab with category-specific tables.

    This method initializes the budget analysis interface, creating a scrollable
    area that contains individual tables for each expense category. Each table
    shows detailed budget vs actual analysis with subcategory breakdowns.

    Args:
        tab: The QWidget tab to set up with budget analysis interface

    Interface Components:
    - Instructions and help text
    - Refresh button for data updates
    - Scrollable area for category tables
    - Individual category analysis tables
    - Summary totals and variance indicators
    """
    layout = QVBoxLayout(tab)

    # Instructions and help text for users
    instructions = QLabel(
        "This tab shows detailed budget vs actual analysis for each category. "
        "Each category displays subcategories with estimates vs actual spending by person."
    )
    instructions.setWordWrap(True)
    instructions.setStyleSheet("color: #666; margin-bottom: 10px; font-size: 12px;")
    layout.addWidget(instructions)

    # Controls section with refresh functionality
    controls_layout = QHBoxLayout()
    
    # Refresh button to update all budget analysis data
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

    # Create scroll area for category tables to handle many categories
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    
    # Widget to contain all category analysis tables
    self.categories_widget = QWidget()
    self.categories_layout = QVBoxLayout(self.categories_widget)
    self.categories_layout.setSpacing(15)  # Space between category tables

    scroll_area.setWidget(self.categories_widget)
    layout.addWidget(scroll_area)

    # Store references to category tables for dynamic updates
    self.category_tables = {}

def refresh_budget_vs_actual_data(self):
    """
    Refresh data for the budget vs actual tab with category-specific analysis.

    This method performs a complete refresh of all budget analysis data,
    rebuilding the category tables with current expense and budget information.
    It calculates variances and updates all visual indicators.

    Process:
    1. Get selected month range from interface
    2. Clear existing category tables
    3. Retrieve category and expense data
    4. Calculate budget vs actual for each category
    5. Create updated tables with current data
    6. Apply styling and variance indicators
    """
    # Get selected month range from the month selector widget
    selected_date = self.month_selector.date()
    month_start = selected_date.toString("yyyy-MM-01")
    month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

    # Clear existing category tables to prepare for refresh
    for i in reversed(range(self.categories_layout.count())):
        child = self.categories_layout.itemAt(i).widget()
        if child:
            child.setParent(None)
    self.category_tables.clear()

    # Get all categories and their subcategories from category manager
    categories_data = self.category_manager.get_categories()
    
    # Get actual expenses by category, subcategory, and person for analysis
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
    
    # Organize actual expense data for efficient lookup
    # Get user names from config
    user_a_name, user_b_name = get_user_names()
    
    actual_expenses = {}
    for row in cursor.fetchall():
        key = (row['category'], row['subcategory'])
        if key not in actual_expenses:
            actual_expenses[key] = {user_a_name: 0, user_b_name: 0}
        actual_expenses[key][row['person']] = row['total']

    # Get budget targets/estimates if they exist in the database
    year = selected_date.year()
    month = selected_date.month()
    cursor = self.db.execute('''
        SELECT category, subcategory, monthly_target
        FROM budget_targets
        WHERE year = ? AND month = ?
    ''', (year, month))
    
    # Organize budget target data for comparison
    budget_targets = {}
    for row in cursor.fetchall():
        key = (row['category'], row['subcategory'])
        budget_targets[key] = row['monthly_target']

    # Create analysis tables for each expense category
    for category, subcategories in categories_data.items():
        self.create_category_table(category, subcategories, actual_expenses, budget_targets)

    # Add stretch at the end to prevent tables from spreading
    self.categories_layout.addStretch()

def create_category_table(self, category, subcategories, actual_expenses, budget_targets):
    """
    Create a detailed analysis table for a specific expense category.

    This method generates a comprehensive table showing budget vs actual
    analysis for a single category, including all its subcategories
    with person-level breakdowns and variance calculations.

    Args:
        category (str): The main category name (e.g., "Food", "Housing")
        subcategories (list): List of subcategory names for this category
        actual_expenses (dict): Actual expense data organized by category/subcategory
        budget_targets (dict): Budget target data for comparison

    Table Structure:
    - Subcategory names in first column
    - Budget estimate in second column
    - User A's actual expenses in third column
    - User B's actual expenses in fourth column
    - Total actual expenses in fifth column
    - Variance (budget - actual) in sixth column
    - Summary totals row at bottom
    """
    # Get user names from config
    user_a_name, user_b_name = get_user_names()
    
    # Create group box container for the category with styling
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
    
    # Create table for this category's analysis
    table = QTableWidget()
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels([
        "Subcategory", "Estimate", f"{user_a_name}'s Expenses", f"{user_b_name}'s Expenses", "Total Actual", "Variance"
    ])
    
    # Set column widths for optimal display
    header = table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory - flexible
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Estimate - fixed width
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # User A - fixed width
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # User B - fixed width
    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Total - fixed width
    header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Variance - fixed width

    # Set specific column widths for consistent appearance
    table.setColumnWidth(1, 100)  # Estimate
    table.setColumnWidth(2, 120)  # User A
    table.setColumnWidth(3, 120)  # User B
    table.setColumnWidth(4, 100)  # Total
    table.setColumnWidth(5, 100)  # Variance
    
    # Style the table with professional appearance
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
    
    # Populate table with subcategory data and calculations
    table.setRowCount(len(subcategories))
    category_totals = {'estimate': 0, 'user_a': 0, 'user_b': 0, 'actual': 0, 'variance': 0}
    
    for i, subcategory in enumerate(subcategories):
        # Subcategory name in first column
        table.setItem(i, 0, QTableWidgetItem(subcategory))
        
        # Get budget estimate (default to 0 if no budget set)
        key = (category, subcategory)
        estimate = budget_targets.get(key, 0)
        table.setItem(i, 1, QTableWidgetItem(f"${estimate:,.2f}"))
        
        # Get actual expenses for user A and user B
        user_a_actual = actual_expenses.get(key, {}).get(user_a_name, 0)
        user_b_actual = actual_expenses.get(key, {}).get(user_b_name, 0)
        total_actual = user_a_actual + user_b_actual
        
        # User A's expenses with red color for expense amounts
        user_a_item = QTableWidgetItem(f"${user_a_actual:,.2f}")
        if user_a_actual > 0:
            user_a_item.setForeground(QColor(200, 50, 50))  # Red for expenses
        table.setItem(i, 2, user_a_item)
        
        # User B's expenses with red color for expense amounts
        user_b_item = QTableWidgetItem(f"${user_b_actual:,.2f}")
        if user_b_actual > 0:
            user_b_item.setForeground(QColor(200, 50, 50))  # Red for expenses
        table.setItem(i, 3, user_b_item)
        
        # Total actual expenses (bold and red)
        total_item = QTableWidgetItem(f"${total_actual:,.2f}")
        if total_actual > 0:
            total_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            total_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
        table.setItem(i, 4, total_item)
        
        # Variance calculation (Estimate - Actual)
        variance = estimate - total_actual
        variance_item = QTableWidgetItem(f"${variance:,.2f}")
        if variance < 0:
            # Red for over budget (negative variance)
            variance_item.setForeground(QColor(200, 50, 50))
            variance_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
        else:
            # Green for under budget (positive variance)
            variance_item.setForeground(QColor(50, 150, 50))
        table.setItem(i, 5, variance_item)
        
        # Add to category totals for summary row
        category_totals['estimate'] += estimate
        category_totals['user_a'] += user_a_actual
        category_totals['user_b'] += user_b_actual
        category_totals['actual'] += total_actual
        category_totals['variance'] += variance
    
    # Add summary totals row at the bottom
    totals_row = table.rowCount()
    table.insertRow(totals_row)
    
    # Style totals row to stand out
    total_font = QFont("Arial", -1, QFont.Weight.Bold)
    
    # Total label
    total_label = QTableWidgetItem("TOTAL")
    total_label.setFont(total_font)
    total_label.setBackground(QColor(230, 230, 230))
    table.setItem(totals_row, 0, total_label)
    
    # Total estimate
    estimate_total = QTableWidgetItem(f"${category_totals['estimate']:,.2f}")
    estimate_total.setFont(total_font)
    estimate_total.setBackground(QColor(230, 230, 230))
    table.setItem(totals_row, 1, estimate_total)
    
    # User A's total
    user_a_total = QTableWidgetItem(f"${category_totals['user_a']:,.2f}")
    user_a_total.setFont(total_font)
    user_a_total.setBackground(QColor(230, 230, 230))
    user_a_total.setForeground(QColor(200, 50, 50))
    table.setItem(totals_row, 2, user_a_total)
    
    # User B's total
    user_b_total = QTableWidgetItem(f"${category_totals['user_b']:,.2f}")
    user_b_total.setFont(total_font)
    vanessa_total.setBackground(QColor(230, 230, 230))
    vanessa_total.setForeground(QColor(200, 50, 50))
    table.setItem(totals_row, 3, vanessa_total)
    
    # Actual total
    actual_total = QTableWidgetItem(f"${category_totals['actual']:,.2f}")
    actual_total.setFont(total_font)
    actual_total.setBackground(QColor(230, 230, 230))
    actual_total.setForeground(QColor(200, 50, 50))
    table.setItem(totals_row, 4, actual_total)
    
    # Variance total with appropriate color coding
    variance_total = QTableWidgetItem(f"${category_totals['variance']:,.2f}")
    variance_total.setFont(total_font)
    variance_total.setBackground(QColor(230, 230, 230))
    if category_totals['variance'] < 0:
        variance_total.setForeground(QColor(200, 50, 50))  # Red for over budget
    else:
        variance_total.setForeground(QColor(50, 150, 50))  # Green for under budget
    table.setItem(totals_row, 5, variance_total)
    
    # Set table height based on content to avoid excessive scrolling
    table.resizeRowsToContents()
    table_height = table.verticalHeader().length() + table.horizontalHeader().height() + 20
    table.setMaximumHeight(min(table_height, 300))  # Cap at 300px
    table.setMinimumHeight(min(table_height, 150))  # Minimum 150px
    
    category_layout.addWidget(table)
    
    # Store table reference for potential future updates
    self.category_tables[category] = table
    
    # Add the category group to the main layout
    self.categories_layout.addWidget(category_group)
