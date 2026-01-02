"""
Trends Tab - Shows spending trends and habits over time
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Enable QtCharts - properly import the modules
try:
    from PyQt6.QtCharts import (
        QChart, QChartView, QLineSeries, QPieSeries,
        QCategoryAxis, QValueAxis, QStackedBarSeries,
        QBarSet, QBarCategoryAxis, QDateTimeAxis
    )
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    QChart = QChartView = QLineSeries = QPieSeries = QCategoryAxis = QValueAxis = type(None)
    QStackedBarSeries = QBarSet = QBarCategoryAxis = QDateTimeAxis = type(None)

from datetime import datetime, timedelta
from collections import defaultdict

from database.db_manager import DatabaseManager

class TrendsTab(QWidget):
    """Trends and analytics tab"""
    
    def __init__(self, db=None):
        super().__init__()
        # Handle both DatabaseManager and direct connection
        if isinstance(db, DatabaseManager):
            self.db_manager = db
            self.db = None
        else:
            self.db = db
            self.db_manager = DatabaseManager()
            
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Spending Trends & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Time period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Time Period:"))
        
        self.period_selector = QComboBox()
        self.period_selector.addItems([
            "Last 6 Months",
            "Last 12 Months", 
            "Last 2 Years",
            "All Time"
        ])
        self.period_selector.setCurrentText("Last 12 Months")
        self.period_selector.currentTextChanged.connect(self.refresh_data)
        period_layout.addWidget(self.period_selector)
        
        period_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Trends Report")
        export_btn.clicked.connect(self.export_trends_report)
        period_layout.addWidget(export_btn)
        
        layout.addLayout(period_layout)
        
        # Create main content area with tabs
        self.content_tabs = QTabWidget()
        
        # Monthly trends tab
        self.monthly_tab = self.create_monthly_trends_tab()
        self.content_tabs.addTab(self.monthly_tab, "Monthly Trends")
        
        # Category trends tab
        self.category_tab = self.create_category_trends_tab()
        self.content_tabs.addTab(self.category_tab, "Category Analysis")
        
        # Spending habits tab
        self.habits_tab = self.create_spending_habits_tab()
        self.content_tabs.addTab(self.habits_tab, "Spending Habits")
        
        # Net worth trends tab
        self.networth_tab = self.create_networth_trends_tab()
        self.content_tabs.addTab(self.networth_tab, "Net Worth Growth")
        
        # Budget Estimates trends tab
        self.budget_estimates_tab = self.create_budget_estimates_trends_tab()
        self.content_tabs.addTab(self.budget_estimates_tab, "📊 Budget Estimates Trends")

        layout.addWidget(self.content_tabs)
        
    def create_monthly_trends_tab(self):
        """Create monthly trends visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary metrics
        metrics_layout = QHBoxLayout()
        
        # Income trend metric
        income_frame = QFrame()
        income_frame.setFrameStyle(QFrame.Shape.Box)
        income_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        income_layout = QVBoxLayout(income_frame)
        
        self.avg_income_label = QLabel("$0")
        self.avg_income_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        self.income_trend_label = QLabel("Avg Monthly Income")
        self.income_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        income_layout.addWidget(self.avg_income_label)
        income_layout.addWidget(self.income_trend_label)
        metrics_layout.addWidget(income_frame)
        
        # Expense trend metric
        expense_frame = QFrame()
        expense_frame.setFrameStyle(QFrame.Shape.Box)
        expense_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        expense_layout = QVBoxLayout(expense_frame)
        
        self.avg_expense_label = QLabel("$0")
        self.avg_expense_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
        self.expense_trend_label = QLabel("Avg Monthly Expenses")
        self.expense_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        expense_layout.addWidget(self.avg_expense_label)
        expense_layout.addWidget(self.expense_trend_label)
        metrics_layout.addWidget(expense_frame)
        
        # Savings trend metric
        savings_frame = QFrame()
        savings_frame.setFrameStyle(QFrame.Shape.Box)
        savings_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        savings_layout = QVBoxLayout(savings_frame)
        
        self.avg_savings_label = QLabel("$0")
        self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        self.savings_trend_label = QLabel("Avg Monthly Savings")
        self.savings_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        savings_layout.addWidget(self.avg_savings_label)
        savings_layout.addWidget(self.savings_trend_label)
        metrics_layout.addWidget(savings_frame)
        
        layout.addLayout(metrics_layout)
        
        # Monthly trend chart
        if CHARTS_AVAILABLE:
            self.monthly_chart_view = QChartView()
            self.monthly_chart_view.setMinimumHeight(400)
        else:
            self.monthly_chart_view = QLabel("Charts not available - PyQt6.QtCharts not installed")
            self.monthly_chart_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_chart_view.setMinimumHeight(400)
            self.monthly_chart_view.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        layout.addWidget(self.monthly_chart_view)
        
        return widget
        
    def create_category_trends_tab(self):
        """Create category analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Category comparison controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Compare Categories:"))
        
        self.category_selector = QComboBox()
        self.category_selector.addItem("All Categories")
        self.category_selector.currentTextChanged.connect(self.refresh_category_trends)
        controls_layout.addWidget(self.category_selector)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Split layout for charts
        charts_layout = QHBoxLayout()
        
        # Category trend over time (left)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Category Spending Over Time"))
        if CHARTS_AVAILABLE:
            self.category_trend_chart = QChartView()
            self.category_trend_chart.setMinimumHeight(300)
        else:
            self.category_trend_chart = QLabel("Charts not available")
            self.category_trend_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_trend_chart.setMinimumHeight(300)
            self.category_trend_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        left_layout.addWidget(self.category_trend_chart)
        charts_layout.addWidget(left_widget)
        
        # Category distribution pie chart (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Category Distribution"))
        if CHARTS_AVAILABLE:
            self.category_pie_chart = QChartView()
            self.category_pie_chart.setMinimumHeight(300)
        else:
            self.category_pie_chart = QLabel("Charts not available")
            self.category_pie_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_pie_chart.setMinimumHeight(300)
            self.category_pie_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        right_layout.addWidget(self.category_pie_chart)
        charts_layout.addWidget(right_widget)
        
        layout.addLayout(charts_layout)
        
        # Category details table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(6)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "This Month", "Last Month", "Change", "6-Month Avg", "Trend"
        ])
        self.category_table.horizontalHeader().setStretchLastSection(True)
        self.category_table.setMaximumHeight(200)
        layout.addWidget(self.category_table)
        
        return widget
        
    def create_spending_habits_tab(self):
        """Create spending habits analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Spending patterns section - Stacked bar chart showing category trends over time
        patterns_group = QGroupBox("Category Spending Trends Over Time")
        patterns_layout = QVBoxLayout(patterns_group)
        
        # Category stacked bar chart showing month-over-month changes
        if CHARTS_AVAILABLE:
            self.category_trends_chart = QChartView()
            self.category_trends_chart.setMinimumHeight(400)
        else:
            self.category_trends_chart = QLabel("Charts not available")
            self.category_trends_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_trends_chart.setMinimumHeight(400)
            self.category_trends_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        patterns_layout.addWidget(self.category_trends_chart)

        layout.addWidget(patterns_group)

        # Split layout for two charts side by side
        charts_layout = QHBoxLayout()

        # Left side - Spending totals pie chart
        pie_group = QGroupBox("Current Period Spending Distribution")
        pie_layout = QVBoxLayout(pie_group)

        if CHARTS_AVAILABLE:
            self.spending_pie_chart = QChartView()
            self.spending_pie_chart.setMinimumHeight(300)
        else:
            self.spending_pie_chart = QLabel("Charts not available")
            self.spending_pie_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.spending_pie_chart.setMinimumHeight(300)
            self.spending_pie_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        pie_layout.addWidget(self.spending_pie_chart)
        charts_layout.addWidget(pie_group)

        # Right side - Day of week spending
        day_group = QGroupBox("Spending by Day of Week")
        day_layout = QVBoxLayout(day_group)

        if CHARTS_AVAILABLE:
            self.day_chart = QChartView()
            self.day_chart.setMinimumHeight(300)
        else:
            self.day_chart = QLabel("Charts not available")
            self.day_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.day_chart.setMinimumHeight(300)
            self.day_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        day_layout.addWidget(self.day_chart)
        charts_layout.addWidget(day_group)

        layout.addLayout(charts_layout)

        # Insights section
        insights_group = QGroupBox("Spending Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)
        
        layout.addWidget(insights_group)
        
        return widget
        
    def create_networth_trends_tab(self):
        """Create net worth trends tab with retirement savings breakdown"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Net worth summary
        summary_layout = QHBoxLayout()
        
        # Current net worth
        current_frame = QFrame()
        current_frame.setFrameStyle(QFrame.Shape.Box)
        current_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        current_layout = QVBoxLayout(current_frame)
        
        self.current_networth_label = QLabel("$0")
        self.current_networth_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        current_layout.addWidget(QLabel("Current Net Worth"))
        current_layout.addWidget(self.current_networth_label)
        summary_layout.addWidget(current_frame)
        
        # Monthly change
        change_frame = QFrame()
        change_frame.setFrameStyle(QFrame.Shape.Box)
        change_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        change_layout = QVBoxLayout(change_frame)
        
        self.networth_change_label = QLabel("$0")
        self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        change_layout.addWidget(QLabel("Monthly Change"))
        change_layout.addWidget(self.networth_change_label)
        summary_layout.addWidget(change_frame)
        
        # Total Retirement Savings
        retirement_frame = QFrame()
        retirement_frame.setFrameStyle(QFrame.Shape.Box)
        retirement_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        retirement_layout = QVBoxLayout(retirement_frame)

        self.total_retirement_label = QLabel("$0")
        self.total_retirement_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        retirement_layout.addWidget(QLabel("Total Retirement"))
        retirement_layout.addWidget(self.total_retirement_label)
        summary_layout.addWidget(retirement_frame)

        layout.addLayout(summary_layout)
        
        # Net worth chart
        if CHARTS_AVAILABLE:
            self.networth_chart = QChartView()
            self.networth_chart.setMinimumHeight(400)
        else:
            self.networth_chart = QLabel("Charts not available")
            self.networth_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.networth_chart.setMinimumHeight(400)
            self.networth_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        layout.addWidget(self.networth_chart)
        
        # Retirement savings breakdown chart
        retirement_group = QGroupBox("Retirement Savings: Roth vs Non-Roth")
        retirement_chart_layout = QVBoxLayout(retirement_group)

        if CHARTS_AVAILABLE:
            self.retirement_chart = QChartView()
            self.retirement_chart.setMinimumHeight(300)
        else:
            self.retirement_chart = QLabel("Charts not available")
            self.retirement_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.retirement_chart.setMinimumHeight(300)
            self.retirement_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        retirement_chart_layout.addWidget(self.retirement_chart)

        layout.addWidget(retirement_group)

        return widget

    def create_budget_estimates_trends_tab(self):
        """Create budget estimates trends tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Instructions
        instructions = QLabel(
            "This chart shows how your budget estimates by category have changed over time, "
            "helping you track your budgeting accuracy and planning improvements."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px; font-size: 12px;")
        layout.addWidget(instructions)

        # Controls section
        controls_layout = QHBoxLayout()

        # Category selector for budget estimates
        controls_layout.addWidget(QLabel("Category:"))
        self.budget_category_selector = QComboBox()
        self.budget_category_selector.addItem("All Categories")
        self.budget_category_selector.currentTextChanged.connect(self.refresh_budget_estimates_trends)
        controls_layout.addWidget(self.budget_category_selector)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Budget estimates chart
        if CHARTS_AVAILABLE:
            self.budget_estimates_chart = QChartView()
            self.budget_estimates_chart.setMinimumHeight(400)
        else:
            self.budget_estimates_chart = QLabel("Charts not available - PyQt6.QtCharts not installed")
            self.budget_estimates_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.budget_estimates_chart.setMinimumHeight(400)
            self.budget_estimates_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        layout.addWidget(self.budget_estimates_chart)

        # Summary table showing estimate vs actual by category
        summary_group = QGroupBox("Budget Estimates Summary (Last 6 Months)")
        summary_layout = QVBoxLayout(summary_group)

        self.budget_summary_table = QTableWidget()
        self.budget_summary_table.setColumnCount(5)
        self.budget_summary_table.setHorizontalHeaderLabels([
            "Category", "Avg Estimate", "Avg Actual", "Accuracy %", "Trend"
        ])
        self.budget_summary_table.horizontalHeader().setStretchLastSection(True)
        self.budget_summary_table.setMaximumHeight(200)
        summary_layout.addWidget(self.budget_summary_table)

        layout.addWidget(summary_group)

        return widget

    def refresh_data(self):
        """Refresh all trend data"""
        self.refresh_monthly_trends()
        self.refresh_category_trends()
        self.refresh_spending_habits()
        self.refresh_networth_trends()
        self.refresh_budget_estimates_trends()

    def refresh_monthly_trends(self):
        """Refresh monthly trends data"""
        # Get date range based on selection
        end_date = datetime.now()
        
        period = self.period_selector.currentText()
        if period == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif period == "Last 12 Months":
            start_date = end_date - timedelta(days=365)
        elif period == "Last 2 Years":
            start_date = end_date - timedelta(days=730)
        else:  # All Time
            start_date = datetime(2020, 1, 1)
            
        # Get monthly data
        monthly_data = self.get_monthly_summary(start_date, end_date)
        
        # Update metrics
        if monthly_data:
            avg_income = sum(month['income'] for month in monthly_data) / len(monthly_data)
            avg_expense = sum(month['expenses'] for month in monthly_data) / len(monthly_data)
            avg_savings = avg_income - avg_expense
            
            self.avg_income_label.setText(f"${avg_income:,.2f}")
            self.avg_expense_label.setText(f"${avg_expense:,.2f}")
            self.avg_savings_label.setText(f"${avg_savings:,.2f}")
            
            # Update color based on savings trend
            if avg_savings > 0:
                self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
            else:
                self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
        
        # Create monthly trends chart
        self.create_monthly_trends_chart(monthly_data)
        
    def refresh_category_trends(self):
        """Refresh category trends"""
        # Get categories for selector
        categories = self.get_categories()
        
        # Temporarily disconnect to avoid recursion
        self.category_selector.currentTextChanged.disconnect()
        
        current_text = self.category_selector.currentText()
        self.category_selector.clear()
        self.category_selector.addItem("All Categories")
        self.category_selector.addItems(categories)
        
        # Restore selection if it still exists
        index = self.category_selector.findText(current_text)
        if index >= 0:
            self.category_selector.setCurrentIndex(index)
            
        # Reconnect the signal
        self.category_selector.currentTextChanged.connect(self.refresh_category_trends)
            
        # Update charts and table
        self.create_category_charts()
        self.update_category_table()
        
    def refresh_spending_habits(self):
        """Refresh spending habits analysis"""
        self.create_category_stacked_bar_chart()
        self.create_spending_pie_chart()
        self.create_day_of_week_chart()
        self.update_spending_insights()
        
    def refresh_networth_trends(self):
        """Refresh net worth trends"""
        try:
            # Get current net worth using database manager
            current_networth = self.get_current_networth()
            self.current_networth_label.setText(f"${current_networth:,.2f}")
            
            # Create net worth chart with historical data
            self.create_networth_chart()
            
            # Create retirement savings chart
            self.create_retirement_chart()

        except Exception as e:
            print(f"Error refreshing net worth trends: {e}")
            
    def refresh_budget_estimates_trends(self):
        """Refresh budget estimates trends"""
        try:
            # Get categories for budget selector
            categories = self.get_categories()

            # Update budget category selector
            if hasattr(self, 'budget_category_selector'):
                # Temporarily disconnect to avoid recursion
                self.budget_category_selector.currentTextChanged.disconnect()

                current_text = self.budget_category_selector.currentText()
                self.budget_category_selector.clear()
                self.budget_category_selector.addItem("All Categories")
                self.budget_category_selector.addItems(categories)

                # Restore selection if it still exists
                index = self.budget_category_selector.findText(current_text)
                if index >= 0:
                    self.budget_category_selector.setCurrentIndex(index)

                # Reconnect the signal
                self.budget_category_selector.currentTextChanged.connect(self.refresh_budget_estimates_trends)

            # Get budget estimates data from database
            estimates_data = self.get_budget_estimates_history()

            # Create budget estimates chart
            self.create_budget_estimates_chart(estimates_data)

            # Update summary table
            self.update_budget_summary_table(estimates_data)

        except Exception as e:
            print(f"Error refreshing budget estimates trends: {e}")

    # Data retrieval methods
    def get_monthly_summary(self, start_date, end_date):
        """Get monthly income and expense summary"""
        try:
            monthly_data = []
            current_date = start_date.replace(day=1)
            
            while current_date <= end_date:
                month_start = current_date.strftime('%Y-%m-01')
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1)
                month_end = next_month.strftime('%Y-%m-01')
                
                # Get income for this month
                income_data = self.db_manager.get_income(month_start, month_end)
                total_income = sum(income['amount'] for income in income_data)
                
                # Get expenses for this month
                expense_data = self.db_manager.get_expenses(month_start, month_end)
                total_expenses = sum(expense['amount'] for expense in expense_data)
                
                monthly_data.append({
                    'month': current_date.strftime('%Y-%m'),
                    'income': total_income,
                    'expenses': total_expenses
                })
                
                # Move to next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
                    
            return monthly_data
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return []

    def get_categories(self):
        """Get list of expense categories"""
        try:
            categories_data = self.db_manager.get_categories()
            categories = set()
            for cat_data in categories_data:
                categories.add(cat_data['category'])
            return sorted(list(categories))
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def get_current_networth(self):
        """Get current net worth"""
        try:
            # Get current assets
            assets = self.db_manager.get_assets()
            total = sum(asset['value'] for asset in assets)
            return total
        except Exception as e:
            print(f"Error getting current net worth: {e}")
            return 0

    def get_category_spending_by_month(self, start_date, end_date):
        """Get category spending organized by month"""
        try:
            spending_by_month = defaultdict(lambda: defaultdict(float))
            
            # Get all expenses in the date range
            expense_data = self.db_manager.get_expenses(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            for expense in expense_data:
                expense_date = datetime.strptime(expense['date'], '%Y-%m-%d')
                month_key = expense_date.strftime('%Y-%m')
                category = expense['category']
                spending_by_month[month_key][category] += expense['amount']
            
            return dict(spending_by_month)
        except Exception as e:
            print(f"Error getting category spending by month: {e}")
            return {}

    def get_day_of_week_spending(self, start_date, end_date):
        """Get spending organized by day of week"""
        try:
            day_spending = defaultdict(float)
            
            expense_data = self.db_manager.get_expenses(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            for expense in expense_data:
                expense_date = datetime.strptime(expense['date'], '%Y-%m-%d')
                day_name = expense_date.strftime('%A')
                day_spending[day_name] += expense['amount']
            
            return dict(day_spending)
        except Exception as e:
            print(f"Error getting day of week spending: {e}")
            return {}

    def get_networth_snapshots(self, start_date, end_date):
        """Get historical net worth snapshots from database"""
        try:
            # Query net_worth_snapshots table for historical data
            self.db_manager.connect()
            query = '''
                SELECT date, jeff_total, vanessa_total, joint_total, total_net_worth
                FROM net_worth_snapshots
                WHERE date >= ? AND date <= ?
                ORDER BY date ASC
            '''

            result = self.db_manager.execute(
                query,
                (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            )

            snapshots = []
            for row in result.fetchall():
                snapshots.append({
                    'date': row['date'],
                    'jeff_total': row['jeff_total'] or 0,
                    'vanessa_total': row['vanessa_total'] or 0,
                    'joint_total': row['joint_total'] or 0,
                    'total_net_worth': row['total_net_worth'] or 0
                })

            return snapshots
        except Exception as e:
            print(f"Error getting net worth snapshots: {e}")
            return []

    def get_retirement_accounts_by_month(self, start_date, end_date):
        """Get retirement account balances organized by month and type (Roth vs Non-Roth)"""
        try:
            self.db_manager.connect()

            # Query for retirement accounts from net_worth_assets table
            query = '''
                SELECT date, asset_type, asset_name, value
                FROM net_worth_assets
                WHERE asset_type IN ('401(k)', 'Roth 401(k)', 'Roth IRA', 'Traditional IRA')
                    AND date >= ? AND date <= ?
                ORDER BY date ASC
            '''

            result = self.db_manager.execute(
                query,
                (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            )

            # Organize by month and type
            retirement_by_month = defaultdict(lambda: {'roth': 0, 'non_roth': 0, 'total': 0})

            for row in result.fetchall():
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                asset_type = row['asset_type']
                value = row['value'] or 0

                # Classify as Roth or Non-Roth
                if 'Roth' in asset_type:
                    retirement_by_month[month_key]['roth'] += value
                else:
                    retirement_by_month[month_key]['non_roth'] += value

                retirement_by_month[month_key]['total'] += value

            return dict(retirement_by_month)
        except Exception as e:
            print(f"Error getting retirement accounts by month: {e}")
            return {}

    def get_retirement_summary(self):
        """Get current retirement account summary"""
        try:
            assets = self.db_manager.get_assets()

            roth_total = 0
            non_roth_total = 0

            retirement_types = ['401(k)', 'Roth 401(k)', 'Roth IRA', 'Traditional IRA']

            for asset in assets:
                if asset['asset_type'] in retirement_types:
                    value = asset['value']
                    if 'Roth' in asset['asset_type']:
                        roth_total += value
                    else:
                        non_roth_total += value

            return {
                'roth_total': roth_total,
                'non_roth_total': non_roth_total,
                'total': roth_total + non_roth_total
            }
        except Exception as e:
            print(f"Error getting retirement summary: {e}")
            return {'roth_total': 0, 'non_roth_total': 0, 'total': 0}

    # Chart creation methods
    def create_monthly_trends_chart(self, monthly_data):
        """Create monthly trends line chart"""
        if not CHARTS_AVAILABLE or not monthly_data:
            return
            
        try:
            chart = QChart()
            chart.setTitle("Monthly Income vs Expenses Trend")
            
            # Create series for income and expenses
            income_series = QLineSeries()
            income_series.setName("Income")
            expense_series = QLineSeries()
            expense_series.setName("Expenses")
            
            # Add data points
            for i, month_data in enumerate(monthly_data):
                income_series.append(i, month_data['income'])
                expense_series.append(i, month_data['expenses'])
            
            chart.addSeries(income_series)
            chart.addSeries(expense_series)
            
            # Create axes
            axis_x = QCategoryAxis()
            for i, month_data in enumerate(monthly_data):
                axis_x.append(month_data['month'], i)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            
            axis_y = QValueAxis()
            axis_y.setLabelFormat("$%.0f")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            
            income_series.attachAxis(axis_x)
            income_series.attachAxis(axis_y)
            expense_series.attachAxis(axis_x)
            expense_series.attachAxis(axis_y)
            
            self.monthly_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"Error creating monthly trends chart: {e}")

    def create_category_stacked_bar_chart(self):
        """Create stacked bar chart showing category spending trends over time"""
        if not CHARTS_AVAILABLE:
            return
            
        try:
            # Get date range
            end_date = datetime.now()
            period = self.period_selector.currentText()
            if period == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "Last 12 Months":
                start_date = end_date - timedelta(days=365)
            elif period == "Last 2 Years":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = datetime(2020, 1, 1)
            
            # Get category spending by month
            spending_by_month = self.get_category_spending_by_month(start_date, end_date)
            
            if not spending_by_month:
                return
            
            # Get all categories and months
            all_categories = set()
            all_months = sorted(spending_by_month.keys())
            
            for month_data in spending_by_month.values():
                all_categories.update(month_data.keys())
            
            all_categories = sorted(list(all_categories))
            
            # Create chart
            chart = QChart()
            chart.setTitle("Category Spending Trends Over Time")
            
            # Create stacked bar series
            series = QStackedBarSeries()
            
            # Color palette for categories
            colors = [
                QColor("#FF6B6B"), QColor("#4ECDC4"), QColor("#45B7D1"), 
                QColor("#96CEB4"), QColor("#FECA57"), QColor("#FF9FF3"),
                QColor("#54A0FF"), QColor("#5F27CD"), QColor("#00D2D3"),
                QColor("#FF9F43"), QColor("#10AC84"), QColor("#EE5A24")
            ]
            
            # Create bar sets for each category
            for i, category in enumerate(all_categories):
                bar_set = QBarSet(category)
                
                # Add data for each month
                for month in all_months:
                    amount = spending_by_month.get(month, {}).get(category, 0)
                    bar_set.append(amount)
                
                # Set color
                if i < len(colors):
                    bar_set.setColor(colors[i])
                
                series.append(bar_set)
            
            chart.addSeries(series)
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(all_months)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            
            axis_y = QValueAxis()
            axis_y.setLabelFormat("$%.0f")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            
            self.category_trends_chart.setChart(chart)
            
        except Exception as e:
            print(f"Error creating category stacked bar chart: {e}")

    def create_spending_pie_chart(self):
        """Create pie chart showing current period spending distribution"""
        if not CHARTS_AVAILABLE:
            return
            
        try:
            # Get date range for current period
            end_date = datetime.now()
            period = self.period_selector.currentText()
            if period == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "Last 12 Months":
                start_date = end_date - timedelta(days=365)
            elif period == "Last 2 Years":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = datetime(2020, 1, 1)
            
            # Get expenses for the period
            expense_data = self.db_manager.get_expenses(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            # Aggregate by category
            category_totals = defaultdict(float)
            for expense in expense_data:
                category_totals[expense['category']] += expense['amount']
            
            if not category_totals:
                return
            
            # Create pie chart
            chart = QChart()
            chart.setTitle(f"Spending Distribution ({period})")
            
            series = QPieSeries()
            
            # Add slices for each category
            total_spending = sum(category_totals.values())
            for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total_spending) * 100 if total_spending > 0 else 0
                slice_obj = series.append(f"{category}\n${amount:,.0f} ({percentage:.1f}%)", amount)
                
                # Highlight slices over 10%
                if percentage > 10:
                    slice_obj.setExploded(True)
            
            chart.addSeries(series)
            self.spending_pie_chart.setChart(chart)
            
        except Exception as e:
            print(f"Error creating spending pie chart: {e}")

    def create_day_of_week_chart(self):
        """Create day of week spending chart"""
        if not CHARTS_AVAILABLE:
            return
            
        try:
            # Get date range
            end_date = datetime.now()
            period = self.period_selector.currentText()
            if period == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "Last 12 Months":
                start_date = end_date - timedelta(days=365)
            elif period == "Last 2 Years":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = datetime(2020, 1, 1)
            
            # Get day of week spending
            day_spending = self.get_day_of_week_spending(start_date, end_date)
            
            if not day_spending:
                return
            
            # Order days properly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Create bar chart
            chart = QChart()
            chart.setTitle("Average Spending by Day of Week")
            
            series = QStackedBarSeries()
            bar_set = QBarSet("Spending")
            
            days_with_data = []
            for day in day_order:
                if day in day_spending:
                    bar_set.append(day_spending[day])
                    days_with_data.append(day)
                else:
                    bar_set.append(0)
                    days_with_data.append(day)
            
            bar_set.setColor(QColor("#FF6B6B"))
            series.append(bar_set)
            chart.addSeries(series)
            
            # Create axes
            axis_x = QBarCategoryAxis()
            axis_x.append(days_with_data)
            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            
            axis_y = QValueAxis()
            axis_y.setLabelFormat("$%.0f")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            
            self.day_chart.setChart(chart)
            
        except Exception as e:
            print(f"Error creating day of week chart: {e}")

    def create_category_charts(self):
        """Create category trend and pie charts"""
        # This method can be expanded to create category-specific charts
        pass

    def create_networth_chart(self):
        """Create net worth trend chart with real historical data"""
        if not CHARTS_AVAILABLE:
            return
        
        try:
            # Get date range based on period selector
            end_date = datetime.now()
            period = self.period_selector.currentText()

            if period == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "Last 12 Months":
                start_date = end_date - timedelta(days=365)
            elif period == "Last 2 Years":
                start_date = end_date - timedelta(days=730)
            else:  # All Time - start from August 2025 as requested
                start_date = datetime(2025, 8, 1)

            # Get historical net worth snapshots
            snapshots = self.get_networth_snapshots(start_date, end_date)

            if not snapshots:
                # No historical data available - show message
                chart = QChart()
                chart.setTitle("Net Worth Trend - No Data Available")
                self.networth_chart.setChart(chart)
                return

            # Create chart
            chart = QChart()
            chart.setTitle("Net Worth Growth Over Time")

            # Create series for total net worth and individual totals
            total_series = QLineSeries()
            total_series.setName("Total Net Worth")

            jeff_series = QLineSeries()
            jeff_series.setName("Jeff")

            vanessa_series = QLineSeries()
            vanessa_series.setName("Vanessa")

            joint_series = QLineSeries()
            joint_series.setName("Joint")

            # Add data points
            for i, snapshot in enumerate(snapshots):
                total_series.append(i, snapshot['total_net_worth'])
                jeff_series.append(i, snapshot['jeff_total'])
                vanessa_series.append(i, snapshot['vanessa_total'])
                joint_series.append(i, snapshot['joint_total'])

            # Add series to chart
            chart.addSeries(total_series)
            chart.addSeries(jeff_series)
            chart.addSeries(vanessa_series)
            chart.addSeries(joint_series)

            # Create axes
            axis_x = QCategoryAxis()
            for i, snapshot in enumerate(snapshots):
                # Show every nth label to avoid crowding
                if i % max(1, len(snapshots) // 10) == 0 or i == len(snapshots) - 1:
                    axis_x.append(snapshot['date'], i)

            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

            axis_y = QValueAxis()
            axis_y.setLabelFormat("$%.0f")
            axis_y.setTitleText("Net Worth")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

            # Attach axes to all series
            for series in [total_series, jeff_series, vanessa_series, joint_series]:
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)

            self.networth_chart.setChart(chart)
            
            # Calculate and display monthly change
            if len(snapshots) >= 2:
                latest = snapshots[-1]['total_net_worth']
                previous = snapshots[-2]['total_net_worth']
                monthly_change = latest - previous

                self.networth_change_label.setText(f"${monthly_change:,.2f}")

                if monthly_change >= 0:
                    self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
                else:
                    self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")

        except Exception as e:
            print(f"Error creating net worth chart: {e}")

    def create_retirement_chart(self):
        """Create retirement savings chart showing Roth vs Non-Roth growth"""
        if not CHARTS_AVAILABLE:
            return
        
        try:
            # Get date range
            end_date = datetime.now()
            period = self.period_selector.currentText()

            if period == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif period == "Last 12 Months":
                start_date = end_date - timedelta(days=365)
            elif period == "Last 2 Years":
                start_date = end_date - timedelta(days=730)
            else:  # All Time - start from August 2025
                start_date = datetime(2025, 8, 1)

            # Get retirement account data
            retirement_data = self.get_retirement_accounts_by_month(start_date, end_date)

            if not retirement_data:
                # No data available
                chart = QChart()
                chart.setTitle("Retirement Savings - No Data Available")
                self.retirement_chart.setChart(chart)
                return

            # Create chart
            chart = QChart()
            chart.setTitle("Retirement Savings: Roth vs Non-Roth Growth")

            # Create series
            roth_series = QLineSeries()
            roth_series.setName("Roth Accounts")

            non_roth_series = QLineSeries()
            non_roth_series.setName("Non-Roth Accounts")

            total_series = QLineSeries()
            total_series.setName("Total Retirement")

            # Sort months and add data
            sorted_months = sorted(retirement_data.keys())

            for i, month in enumerate(sorted_months):
                data = retirement_data[month]
                roth_series.append(i, data['roth'])
                non_roth_series.append(i, data['non_roth'])
                total_series.append(i, data['total'])

            # Add series to chart
            chart.addSeries(roth_series)
            chart.addSeries(non_roth_series)
            chart.addSeries(total_series)

            # Create axes
            axis_x = QCategoryAxis()
            for i, month in enumerate(sorted_months):
                if i % max(1, len(sorted_months) // 8) == 0 or i == len(sorted_months) - 1:
                    axis_x.append(month, i)

            chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

            axis_y = QValueAxis()
            axis_y.setLabelFormat("$%.0f")
            axis_y.setTitleText("Account Balance")
            chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

            # Attach axes
            for series in [roth_series, non_roth_series, total_series]:
                series.attachAxis(axis_x)
                series.attachAxis(axis_y)

            self.retirement_chart.setChart(chart)

            # Update retirement summary label
            retirement_summary = self.get_retirement_summary()
            self.total_retirement_label.setText(f"${retirement_summary['total']:,.2f}")

        except Exception as e:
            print(f"Error creating retirement chart: {e}")

    # Update methods
    def update_category_table(self):
        """Update category analysis table"""
        # Placeholder implementation
        pass

    def update_spending_insights(self):
        """Update spending insights text"""
        try:
            insights = []
            
            # Get some basic insights
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            expense_data = self.db_manager.get_expenses(
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            if expense_data:
                # Top spending category
                category_totals = defaultdict(float)
                for expense in expense_data:
                    category_totals[expense['category']] += expense['amount']
                
                if category_totals:
                    top_category = max(category_totals, key=category_totals.get)
                    top_amount = category_totals[top_category]
                    insights.append(f"• Your highest spending category this month is {top_category} at ${top_amount:,.2f}")
                
                # Total spending
                total_spending = sum(expense['amount'] for expense in expense_data)
                insights.append(f"• Total spending in the last 30 days: ${total_spending:,.2f}")
                
                # Average daily spending
                avg_daily = total_spending / 30
                insights.append(f"• Average daily spending: ${avg_daily:.2f}")
            
            self.insights_text.setText('\n'.join(insights))
            
        except Exception as e:
            print(f"Error updating spending insights: {e}")

    def update_budget_summary_table(self, estimates_data):
        """Update budget summary table"""
        # Placeholder implementation
        pass

    def get_budget_estimates_history(self):
        """Get budget estimates history data"""
        try:
            selected_category = None
            if hasattr(self, 'budget_category_selector'):
                if self.budget_category_selector.currentText() != "All Categories":
                    selected_category = self.budget_category_selector.currentText()

            # Get date range based on period selection
            end_date = datetime.now()
            period = self.period_selector.currentText()
            if period == "Last 6 Months":
                months_back = 6
            elif period == "Last 12 Months":
                months_back = 12
            elif period == "Last 2 Years":
                months_back = 24
            else:  # All Time
                months_back = 60  # 5 years max

            # Get budget estimates from database
            if self.db_manager and hasattr(self.db_manager, 'get_budget_estimates_history'):
                estimates_data = self.db_manager.get_budget_estimates_history(selected_category, months_back)
            else:
                # Fallback - create sample data
                estimates_data = []
                for i in range(6):
                    month_date = end_date.replace(day=1) - timedelta(days=30*i)
                    estimates_data.append({
                        'category': selected_category or 'Housing',
                        'subcategory': 'Mortgage',
                        'estimated_amount': 1000 + (i * 50),
                        'actual_amount': 950 + (i * 45),
                        'year': month_date.year,
                        'month': month_date.month,
                        'month_str': month_date.strftime('%Y-%m')
                    })

            return estimates_data

        except Exception as e:
            print(f"Error getting budget estimates history: {e}")
            return []

    def export_trends_report(self):
        """Export trends report to file"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Trends Report",
                f"trends_report_{datetime.now().strftime('%Y%m%d')}.txt",
                "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("Budget Tracker - Trends Report\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Period: {self.period_selector.currentText()}\n\n")
                    
                    # Add more report content here
                    f.write("Summary metrics:\n")
                    f.write(f"Average Monthly Income: {self.avg_income_label.text()}\n")
                    f.write(f"Average Monthly Expenses: {self.avg_expense_label.text()}\n")
                    f.write(f"Average Monthly Savings: {self.avg_savings_label.text()}\n")
                    
                QMessageBox.information(self, "Success", f"Trends report exported to {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export trends report: {str(e)}")
