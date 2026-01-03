"""
Stylesheet Definitions for Zuo Budget Tracker Application
=========================================================

This module provides centralized styling for the Zuo application
using a Modern Fintech theme with professional colors. The stylesheet ensures
consistent visual appearance across all components while maintaining
readability and professional aesthetics.

Theme Design Philosophy - "Modern Fintech":
- Light theme by default for professional appearance
- Deep Navy (#1e3a5f) for primary elements
- Emerald Green (#10b981) for income/success indicators
- Muted Coral (#ef4444) for expense/danger indicators
- Clean, card-based layouts with subtle shadows
- Professional typography with good contrast

Color Palette:
- Primary: Deep Navy #1e3a5f (Professional, trustworthy)
- Secondary: Slate #64748b (Neutral, readable)
- Success/Income: Emerald Green #10b981
- Danger/Expense: Muted Coral #ef4444
- Background: #f8fafc (Light)
- Card Background: #ffffff with subtle shadow
- Text Primary: #0f172a
- Text Secondary: #64748b

Functions:
    get_app_stylesheet(): Returns the complete application stylesheet

Dependencies:
    None - Pure CSS-like styling for PyQt6 widgets
"""

def get_app_stylesheet():
    """
    Return the main application stylesheet with Modern Fintech theme.

    This function provides a comprehensive stylesheet that applies consistent
    light theme styling to all PyQt6 widgets used in the Zuo application.

    Returns:
        str: Complete CSS-style stylesheet for PyQt6 application
    """
    return """
    /* Main Application Theme - Modern Fintech Light */
    QMainWindow {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Central Widget - Base styling for all widgets */
    QWidget {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: "Inter", "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Tab Widget - Main tabbed interface styling */
    QTabWidget {
        background-color: #f8fafc;
        border: none;
    }
    
    /* Tab widget pane - Container for tab content */
    QTabWidget::pane {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-top: -1px;
    }
    
    /* Tab bar alignment */
    QTabWidget::tab-bar {
        alignment: left;
    }
    
    /* Individual tab styling */
    QTabBar::tab {
        background-color: #f1f5f9;
        color: #64748b;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border: 1px solid #e2e8f0;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        color: #1e3a5f;
        font-weight: 600;
        border-bottom: 1px solid #ffffff;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #e2e8f0;
        color: #1e3a5f;
    }
    
    /* Tables - Data display with modern aesthetics */
    QTableWidget {
        background-color: #ffffff;
        alternate-background-color: #f8fafc;
        gridline-color: #e2e8f0;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        selection-background-color: #1e3a5f;
        selection-color: #ffffff;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #f1f5f9;
    }
    
    QTableWidget::item:selected {
        background-color: #1e3a5f;
        color: #ffffff;
    }
    
    QHeaderView::section {
        background-color: #f8fafc;
        color: #1e3a5f;
        padding: 10px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }
    
    /* Buttons - Interactive elements with distinct states */
    QPushButton {
        background-color: #1e3a5f;
        color: #ffffff;
        border: 2px solid #1e3a5f;
        font-weight: 600;
        font-size: 14px;
        min-width: 80px;
        padding: 8px 16px;
        border-radius: 8px;
    }
    
    QPushButton:hover {
        background-color: #2d4a6f;
        border-color: #2d4a6f;
    }
    
    QPushButton:pressed {
        background-color: #152a45;
        border-color: #152a45;
    }
    
    QPushButton:disabled {
        background-color: #cbd5e1;
        border-color: #cbd5e1;
        color: #94a3b8;
    }
    
    /* Input Fields - Form elements for user data entry */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        background-color: #ffffff;
        color: #0f172a;
        border: 2px solid #e2e8f0;
        padding: 8px;
        border-radius: 8px;
        font-size: 14px;
    }
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border-color: #1e3a5f;
        background-color: #ffffff;
    }
    
    QComboBox::drop-down {
        border: none;
        background-color: #f1f5f9;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #64748b;
        margin: 0px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
        selection-background-color: #1e3a5f;
        selection-color: #ffffff;
    }
    
    /* Labels - Text elements for descriptions and titles */
    QLabel {
        color: #0f172a;
        font-size: 14px;
    }
    
    /* Group Boxes - Container elements for grouping related widgets */
    QGroupBox {
        color: #1e3a5f;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        margin-top: 10px;
        font-weight: 600;
        background-color: #ffffff;
        padding-top: 15px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        background-color: #ffffff;
    }
    
    /* Scroll Bars - Custom styling for scrollable areas */
    QScrollBar:vertical {
        background-color: #f1f5f9;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #cbd5e1;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #94a3b8;
    }
    
    QScrollBar:horizontal {
        background-color: #f1f5f9;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #cbd5e1;
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #94a3b8;
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    
    /* Check Boxes - Binary choice elements */
    QCheckBox {
        color: #0f172a;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #1e3a5f;
        border-color: #1e3a5f;
        image: url(data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>);
    }
    
    /* Radio Buttons - Single choice elements */
    QRadioButton {
        color: #0f172a;
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 9px;
    }
    
    QRadioButton::indicator:checked {
        background-color: #1e3a5f;
        border-color: #1e3a5f;
    }
    
    /* Progress Bars - Visual indicators of progress */
    QProgressBar {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        text-align: center;
        color: #0f172a;
    }
    
    QProgressBar::chunk {
        background-color: #10b981;
        border-radius: 7px;
    }
    
    /* Dialog Boxes - Pop-up windows for interactions */
    QDialog {
        background-color: #ffffff;
        color: #0f172a;
    }
    
    QDialog QPushButton, QMessageBox QPushButton {
        background-color: #1e3a5f;
        border: 2px solid #1e3a5f;
        color: white;
        font-weight: 600;
        font-size: 14px;
        min-width: 80px;
        padding: 8px 16px;
        border-radius: 8px;
    }
    
    QDialog QPushButton:hover, QMessageBox QPushButton:hover {
        background-color: #2d4a6f;
        border-color: #2d4a6f;
    }
    
    QDialog QPushButton:pressed, QMessageBox QPushButton:pressed {
        background-color: #152a45;
        border-color: #152a45;
    }
    
    QMessageBox {
        background-color: #ffffff;
        color: #0f172a;
    }
    
    QMessageBox QLabel {
        color: #0f172a;
        font-size: 14px;
    }
    
    /* Menu Bar - Application menu styling */
    QMenuBar {
        background-color: #ffffff;
        color: #0f172a;
        border-bottom: 1px solid #e2e8f0;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 16px;
    }
    
    QMenuBar::item:selected {
        background-color: #f1f5f9;
    }
    
    QMenu {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #e2e8f0;
    }
    
    QMenu::item {
        padding: 8px 32px 8px 16px;
    }
    
    QMenu::item:selected {
        background-color: #1e3a5f;
        color: #ffffff;
    }
    
    /* Status Bar - Information and status messages area */
    QStatusBar {
        background-color: #ffffff;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Splitter - Resizable panels */
    QSplitter::handle {
        background-color: #e2e8f0;
        border: 1px solid #cbd5e1;
    }
    
    QSplitter::handle:horizontal {
        width: 6px;
    }
    
    QSplitter::handle:vertical {
        height: 6px;
    }
    """
