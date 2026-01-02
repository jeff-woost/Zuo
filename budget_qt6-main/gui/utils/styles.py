"""
Stylesheet Definitions for the Budget Tracker Application
=======================================================

This module provides centralized styling for the Budget Tracker application
using a dark theme with medium/light grey colors. The stylesheet ensures
consistent visual appearance across all components while maintaining
readability and professional aesthetics.

Theme Design Philosophy:
- Dark theme reduces eye strain during extended use
- Medium grey (#2d3748) provides good contrast without being harsh
- Light text (#e2e8f0) ensures excellent readability
- Blue accents (#2a82da) for interactive elements and highlights
- Consistent spacing and borders for professional appearance

The stylesheet covers:
- Main application window and widgets
- Tab interface with hover effects
- Tables with alternating row colors and modern headers
- Buttons with different states (normal, hover, pressed)
- Input fields and form elements
- Group boxes and containers
- Scrollbars with custom styling

Functions:
    get_app_stylesheet(): Returns the complete application stylesheet

Dependencies:
    None - Pure CSS-like styling for PyQt6 widgets
"""

def get_app_stylesheet():
    """
    Return the main application stylesheet with medium/light dark grey theme.

    This function provides a comprehensive stylesheet that applies consistent
    dark theme styling to all PyQt6 widgets used in the Budget Tracker application.

    The styling includes:
    - Base widget appearance (background, text colors, fonts)
    - Tab widget styling with hover effects and rounded corners
    - Table styling with modern headers and alternating row colors
    - Button styling with multiple variants (primary, secondary, danger, etc.)
    - Input field styling with focus states
    - Scrollbar customization for better user experience
    - Group box styling for organized content sections

    Returns:
        str: Complete CSS-style stylesheet for PyQt6 application
    """
    return """
    /* Main Application Theme - Medium/Light Dark Grey */
    QMainWindow {
        background-color: #2d3748;
        color: #e2e8f0;
    }
    
    /* Central Widget - Base styling for all widgets */
    QWidget {
        background-color: #2d3748;
        color: #e2e8f0;
        font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Tab Widget - Main tabbed interface styling */
    QTabWidget {
        background-color: #2d3748;
        border: none;
    }
    
    /* Tab widget pane - Container for tab content */
    QTabWidget::pane {
        background-color: #374151;
        border: 1px solid #4a5568;
        border-radius: 6px;
        margin-top: -1px;
    }
    
    /* Tab bar alignment */
    QTabWidget::tab-bar {
        alignment: left;
    }
    
    /* Individual tab styling */
    QTabBar::tab {
        background-color: #4a5568;
        color: #cbd5e0;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        border: 1px solid #4a5568;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: #374151;
        color: #f7fafc;
        border-bottom: 1px solid #374151;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #5a6c7d;
        color: #f7fafc;
    }
    
    /* Tables - Data display with modern aesthetics */
    QTableWidget {
        background-color: #374151;
        alternate-background-color: #2d3748;
        gridline-color: #4a5568;
        color: #e2e8f0;
        border: 1px solid #4a5568;
        border-radius: 4px;
        selection-background-color: #4c51bf;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #4a5568;
    }
    
    QTableWidget::item:selected {
        background-color: #4c51bf;
        color: #ffffff;
    }
    
    QHeaderView::section {
        background-color: #4a5568;
        color: #f7fafc;
        padding: 8px;
        border: 1px solid #2d3748;
        font-weight: bold;
    }
    
    /* Buttons - Interactive elements with distinct states */
    QPushButton {
        background-color: #4c51bf;
        color: #ffffff;
        border: 2px solid #4c51bf;
        font-weight: 600;
        font-size: 14px;
        min-width: 80px;
        padding: 8px 16px;
        border-radius: 6px;
    }
    
    QPushButton:hover {
        background-color: #5a67d8;
        border-color: #5a67d8;
    }
    
    QPushButton:pressed {
        background-color: #434190;
        border-color: #434190;
    }
    
    QPushButton:disabled {
        background-color: #4a5568;
        border-color: #4a5568;
        color: #9ca3af;
    }
    
    /* Input Fields - Form elements for user data entry */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #4a5568;
        color: #f7fafc;
        border: 2px solid #6b7280;
        padding: 8px;
        border-radius: 4px;
        font-size: 14px;
    }
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border-color: #4c51bf;
        background-color: #374151;
    }
    
    QComboBox::drop-down {
        border: none;
        background-color: #6b7280;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #f7fafc;
        margin: 0px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #4a5568;
        color: #f7fafc;
        border: 1px solid #6b7280;
        selection-background-color: #4c51bf;
    }
    
    /* Labels - Text elements for descriptions and titles */
    QLabel {
        color: #e2e8f0;
        font-size: 14px;
    }
    
    /* Group Boxes - Container elements for grouping related widgets */
    QGroupBox {
        color: #f7fafc;
        border: 2px solid #4a5568;
        border-radius: 6px;
        margin-top: 10px;
        font-weight: bold;
        background-color: #374151;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        background-color: #374151;
    }
    
    /* Scroll Bars - Custom styling for scrollable areas */
    QScrollBar:vertical {
        background-color: #4a5568;
        width: 16px;
        border-radius: 8px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #6b7280;
        border-radius: 8px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #9ca3af;
    }
    
    QScrollBar:horizontal {
        background-color: #4a5568;
        height: 16px;
        border-radius: 8px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #6b7280;
        border-radius: 8px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #9ca3af;
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    
    /* Check Boxes - Binary choice elements */
    QCheckBox {
        color: #e2e8f0;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #4a5568;
        border: 2px solid #6b7280;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4c51bf;
        border-color: #4c51bf;
        image: url(data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>);
    }
    
    /* Radio Buttons - Single choice elements */
    QRadioButton {
        color: #e2e8f0;
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        background-color: #4a5568;
        border: 2px solid #6b7280;
        border-radius: 9px;
    }
    
    QRadioButton::indicator:checked {
        background-color: #4c51bf;
        border-color: #4c51bf;
    }
    
    /* Progress Bars - Visual indicators of progress */
    QProgressBar {
        background-color: #4a5568;
        border: 1px solid #6b7280;
        border-radius: 6px;
        text-align: center;
        color: #f7fafc;
    }
    
    QProgressBar::chunk {
        background-color: #10b981;
        border-radius: 5px;
    }
    
    /* Dialog Boxes - Pop-up windows for interactions */
    QDialog {
        background-color: #374151;
        color: #e2e8f0;
    }
    
    QDialog QPushButton, QMessageBox QPushButton {
        background-color: #4c51bf;
        border: 2px solid #4c51bf;
        color: white;
        font-weight: 600;
        font-size: 14px;
        min-width: 80px;
        padding: 8px 16px;
        border-radius: 6px;
    }
    
    QDialog QPushButton:hover, QMessageBox QPushButton:hover {
        background-color: #5a67d8;
        border-color: #5a67d8;
    }
    
    QDialog QPushButton:pressed, QMessageBox QPushButton:pressed {
        background-color: #434190;
        border-color: #434190;
    }
    
    QMessageBox {
        background-color: #374151;
        color: #e2e8f0;
    }
    
    QMessageBox QLabel {
        color: #e2e8f0;
        font-size: 14px;
    }
    
    /* Menu Bar - Application menu styling */
    QMenuBar {
        background-color: #2d3748;
        color: #e2e8f0;
        border-bottom: 1px solid #4a5568;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 16px;
    }
    
    QMenuBar::item:selected {
        background-color: #4a5568;
    }
    
    QMenu {
        background-color: #374151;
        color: #e2e8f0;
        border: 1px solid #4a5568;
    }
    
    QMenu::item {
        padding: 8px 32px 8px 16px;
    }
    
    QMenu::item:selected {
        background-color: #4c51bf;
    }
    
    /* Status Bar - Information and status messages area */
    QStatusBar {
        background-color: #2d3748;
        color: #e2e8f0;
        border-top: 1px solid #4a5568;
    }
    
    /* Splitter - Resizable panels */
    QSplitter::handle {
        background-color: #4a5568;
        border: 1px solid #6b7280;
    }
    
    QSplitter::handle:horizontal {
        width: 6px;
    }
    
    QSplitter::handle:vertical {
        height: 6px;
    }
    """
