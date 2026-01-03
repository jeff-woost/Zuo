#!/usr/bin/env python3
"""
Budget Tracker Application - Main Entry Point
================================================

This is the main entry point for the Zuo Budget Tracker application.
A comprehensive PyQt6-based personal finance management tool that provides:

Features:
- Income and expense tracking with categorization
- Net worth monitoring with asset management
- Budget planning and variance analysis
- Monthly financial presentations and reports
- Savings goals tracking and progress monitoring
- Financial trends analysis and visualization

The application uses a SQLite database for data persistence and provides
a user-friendly tabbed interface for different financial management tasks.

Usage:
    python main.py

Dependencies:
    - PyQt6: For the graphical user interface
    - SQLite3: For database operations (built into Python)
    - Additional dependencies listed in requirements.txt

Version: 1.0
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project root to Python path to enable relative imports
# This ensures the application can find all modules regardless of
# where it's executed from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import load_settings
from src.gui.views.onboarding import OnboardingWizard
from src.app import BudgetApp

def main():
    """
    Main application entry point and initialization.

    This function:
    1. Configures high DPI display scaling for modern monitors
    2. Creates the PyQt6 application instance
    3. Sets application metadata (name, organization)
    4. Instantiates and displays the main window
    5. Starts the Qt event loop

    The application will run until the user closes the main window
    or the system sends a termination signal.

    Returns:
        int: Application exit code (0 for success, non-zero for errors)
    """
    # Enable high DPI scaling for crisp display on modern monitors
    # This ensures the application scales properly on 4K displays, retina screens, etc.
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create the main Qt application instance
    # This manages the GUI application's control flow and main settings
    app = QApplication(sys.argv)

    # Set application metadata for proper OS integration
    # This affects window titles, system tray integration, and file associations5
    app.setApplicationName("Zuo")
    app.setOrganizationName("Zuo")
    
    # Check if onboarding is needed
    settings = load_settings()
    if not settings.get("onboarding_completed", False):
        # Show onboarding wizard
        wizard = OnboardingWizard()
        if wizard.exec() != wizard.DialogCode.Accepted:
            # User cancelled onboarding - exit application
            return 0
    
    # Create the main application window
    # BudgetApp is the primary window containing all tabs and functionality
    window = BudgetApp()

    # Display the main window to the user
    window.show()
    
    # Start the Qt event loop and run until application exit
    # This blocks until the user closes the application
    sys.exit(app.exec())

if __name__ == "__main__":
    # Only run the application if this file is executed directly
    # (not imported as a module)
    main()
