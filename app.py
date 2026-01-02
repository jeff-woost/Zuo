"""
Budget Tracker Application - Main Window
========================================

This module contains the BudgetApp class, which serves as the main application window
and central coordinator for the budget tracker. It manages the tabbed interface and
provides the primary user interaction point for all financial management features.

The main window coordinates:
- Database initialization and management
- Tab creation and organization
- Inter-tab communication and data refresh
- Application-wide styling and theming
- Window management and layout

Classes:
    BudgetApp: Main application window with tabbed interface

Dependencies:
    - PyQt6: GUI framework components
    - database.db_manager: Database operations
    - gui.tabs.*: Individual tab implementations
    - gui.utils.styles: Application styling
"""

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from database.db_manager import DatabaseManager
from gui.tabs.overview_tab import OverviewTab
from gui.tabs.net_worth_tab import NetWorthTab
from gui.tabs.budget_tab import BudgetTab
from gui.tabs.presentation_tab import PresentationTab
from gui.tabs.savings_tab import SavingsTab
from gui.tabs.trends_tab import TrendsTab
from gui.tabs.bank_reconciliation_tab import BankReconciliationTab
from gui.utils.styles import get_app_stylesheet

class BudgetApp(QMainWindow):
    """
    Main application window for the Budget Tracker.

    This class serves as the central coordinator for the entire application,
    managing the tabbed interface and providing a unified entry point for
    all budget management functionality.

    The application is organized into logical tabs:
    - Budget Overview: High-level financial summary
    - Net Worth: Asset and liability tracking
    - Budget: Income and expense management
    - Monthly Presentation: Formatted reports for review
    - Savings Goals: Goal tracking and progress monitoring
    - Trends: Historical analysis and visualization

    Attributes:
        db (DatabaseManager): Central database connection manager
        tabs (QTabWidget): Container for all application tabs
        overview_tab (OverviewTab): Financial overview and summary
        net_worth_tab (NetWorthTab): Asset management interface
        budget_tab (BudgetTab): Income/expense tracking
        presentation_tab (PresentationTab): Monthly reports
        savings_tab (SavingsTab): Savings goal management
        trends_tab (TrendsTab): Historical analysis
    """

    def __init__(self):
        """
        Initialize the main application window.

        This constructor:
        1. Sets up the main window properties (title, size, position)
        2. Initializes the database connection and creates tables
        3. Creates and configures the user interface
        4. Applies the application styling theme

        The window is sized for optimal viewing on most displays and
        positioned at a reasonable default location.
        """
        super().__init__()

        # Configure main window properties
        self.setWindowTitle("Jeff & Vanessa Budget Tracker")
        # Set window size: width=1400px, height=800px for comfortable viewing
        # Position: x=100, y=100 offset from top-left corner
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize database connection and ensure tables exist
        # This creates the SQLite database file if it doesn't exist
        # and sets up all required tables for the application
        self.db = DatabaseManager()
        self.db.initialize_database()
        
        # Build the user interface structure
        self.setup_ui()
        
        # Apply the dark theme styling to all widgets
        self.setStyleSheet(get_app_stylesheet())
        
    def setup_ui(self):
        """
        Create and configure the main user interface structure.

        This method:
        1. Creates the central widget and main layout
        2. Initializes the tab widget container
        3. Creates instances of all application tabs
        4. Adds tabs to the interface in logical order
        5. Connects signals for tab change events

        The tabs are arranged in order of typical user workflow:
        Overview -> Net Worth -> Budget -> Presentation -> Savings -> Trends
        """
        # Create the central widget that will contain all UI elements
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main vertical layout for the central widget
        layout = QVBoxLayout(central_widget)
        
        # Create the tab widget that will hold all application tabs
        # This provides the tabbed interface for different functions
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create instances of all application tabs
        # Each tab is responsible for a specific area of financial management

        # Overview tab: High-level summary and dashboard
        self.overview_tab = OverviewTab()

        # Net Worth tab: Asset and liability tracking
        self.net_worth_tab = NetWorthTab()

        # Budget tab: Income and expense management (the main working area)
        self.budget_tab = BudgetTab()

        # Presentation tab: Monthly reports and formatted views
        # Pass database connection for data access
        self.presentation_tab = PresentationTab(self.db)

        # Savings tab: Goal setting and progress tracking
        self.savings_tab = SavingsTab(self.db)

        # Trends tab: Historical analysis and visualization
        self.trends_tab = TrendsTab(self.db)
        
        # Bank Reconciliation tab: Import and reconcile bank transactions
        self.bank_reconciliation_tab = BankReconciliationTab()
        
        # Add all tabs to the tab widget in logical order
        # Icons enhance visual identification of each tab
        self.tabs.addTab(self.overview_tab, "Budget Overview")
        self.tabs.addTab(self.net_worth_tab, "Net Worth")
        self.tabs.addTab(self.budget_tab, "Budget")  # Primary working tab
        self.tabs.addTab(self.bank_reconciliation_tab, "Bank Reconciliation")
        self.tabs.addTab(self.presentation_tab, "Monthly Presentation")
        self.tabs.addTab(self.savings_tab, "Savings Goals")
        self.tabs.addTab(self.trends_tab, "Trends")
        
        # Connect tab change signal to refresh data when switching tabs
        # This ensures each tab shows current data when activated
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        """
        Handle tab change events to refresh data.

        This method is called whenever the user switches to a different tab.
        It ensures that the newly activated tab displays the most current
        data by calling its refresh_data method if available.

        Args:
            index (int): Index of the newly selected tab

        Note:
            Not all tabs may implement refresh_data(), so we check for
            its existence before calling it.
        """
        # Get the widget for the currently selected tab
        current_widget = self.tabs.currentWidget()

        # Check if the tab has a refresh_data method and call it
        # This pattern allows tabs to update their display when activated
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()