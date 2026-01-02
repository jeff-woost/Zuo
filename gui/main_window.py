"""
Main window for the budget application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

from gui.tabs.overview_tab import OverviewTab
from gui.tabs.net_worth_tab import NetWorthTab
from gui.tabs.budget_tab import BudgetTab
from gui.tabs.presentation_tab import PresentationTab
from gui.tabs.savings_tab import SavingsTab
from gui.tabs.trends_tab import TrendsTab
from gui.utils.styles import get_app_stylesheet

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zuo - Budget Tracker")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set up central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create and add tabs
        self.overview_tab = OverviewTab()
        self.net_worth_tab = NetWorthTab()
        self.budget_tab = BudgetTab()
        self.presentation_tab = PresentationTab()
        self.savings_tab = SavingsTab()
        self.trends_tab = TrendsTab()
        
        self.tabs.addTab(self.overview_tab, "Budget Overview")
        self.tabs.addTab(self.net_worth_tab, "Net Worth")
        self.tabs.addTab(self.budget_tab, "Budget")
        self.tabs.addTab(self.presentation_tab, "Monthly Presentation")
        self.tabs.addTab(self.savings_tab, "Savings Goals")
        self.tabs.addTab(self.trends_tab, "Trends")
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Apply the proper light theme stylesheet
        self.setStyleSheet(get_app_stylesheet())
        
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("&Export Data", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        preferences_action = QAction("&Preferences", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(preferences_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def on_tab_changed(self, index):
        """Handle tab change events"""
        # Refresh data in the newly selected tab
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, 'refresh_data'):
            current_tab.refresh_data()
            
    def export_data(self):
        """Export data to file"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon!")
        
    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog will be implemented soon!")
        
    def refresh_data(self):
        """Refresh current tab data"""
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, 'refresh_data'):
            current_tab.refresh_data()
            self.status_bar.showMessage("Data refreshed", 2000)
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Zuo Budget Tracker",
            "Zuo Budget Tracker v1.0\n\n"
            "A comprehensive budget management application\n\n"
            "© 2024 All rights reserved"
        )