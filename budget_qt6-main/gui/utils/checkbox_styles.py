"""
Centralized Checkbox Styling Utilities
=====================================

This module provides consistent checkbox styling utilities for the Budget Tracker
application. It ensures that all checkboxes across different tabs and components
have uniform appearance and behavior, enhancing user experience and visual consistency.

The module provides two distinct checkbox styles:
1. Form checkboxes: Used in data entry forms and settings
2. Table checkboxes: Used for row selection in tables and lists

Design Philosophy:
- Consistent visual appearance across all application components
- Clear visual feedback for checked/unchecked states
- Hover effects to improve user interaction feedback
- Accessible color contrast for better usability
- Red accent color (#dc3545) for selection states to match application theme

Functions:
    get_checkbox_style(): Returns CSS styling for form checkboxes
    get_table_checkbox_style(): Returns CSS styling for table selection checkboxes
    create_form_checkbox(): Factory function for styled form checkboxes
    create_table_checkbox(): Factory function for styled table checkboxes

Dependencies:
    - PyQt6.QtWidgets.QCheckBox: Base checkbox widget class
"""

from PyQt6.QtWidgets import QCheckBox

def get_checkbox_style():
    """
    Get the standard checkbox styling for form elements.

    This function returns CSS styling specifically designed for checkboxes
    used in forms, settings panels, and general data entry contexts.
    The styling provides clear visual states and smooth hover transitions.

    Features:
    - Medium grey text color for good readability
    - 20x20 pixel checkbox indicator with rounded corners
    - Red accent color (#dc3545) for checked state
    - Subtle hover effects with light background changes
    - Bold white checkmark symbol for clear checked indication

    Returns:
        str: CSS stylesheet string for form checkboxes
    """
    return """
    QCheckBox {
        color: #2d3748;
        font-size: 13px;
        spacing: 8px;
        margin: 5px;
    }
    
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 3px;
        border: 2px solid #666;
        background-color: #ffffff;
    }
    
    QCheckBox::indicator:hover {
        border-color: #dc3545;
        background-color: #f8f9fa;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #ffffff;
        border: 2px solid #6c757d;
    }
    
    QCheckBox::indicator:unchecked:hover {
        background-color: #fff5f5;
        border: 2px solid #dc3545;
    }
    
    QCheckBox::indicator:checked {
        background-color: #dc3545;
        border: 2px solid #dc3545;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    
    QCheckBox::indicator:checked:hover {
        background-color: #c82333;
        border: 2px solid #c82333;
    }
    
    QCheckBox::indicator:checked:before {
        content: "✓";
        color: white;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        position: absolute;
        top: 1px;
        left: 3px;
    }
    """

def get_table_checkbox_style():
    """
    Get the specialized checkbox styling for table selection.

    This function returns CSS styling specifically optimized for checkboxes
    used in table rows for item selection. The styling is more compact
    and focused on clear selection indication.

    Features:
    - Compact 20x20 pixel indicator optimized for table rows
    - Minimal margins for tight table layouts
    - Enhanced hover effects with subtle scaling
    - Same red accent color for consistency
    - Clear visual feedback for selection operations

    Returns:
        str: CSS stylesheet string for table selection checkboxes
    """
    return """
    QCheckBox {
        margin: 5px;
        spacing: 0px;
    }
    
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border-radius: 3px;
        border: 2px solid #666;
        background-color: #ffffff;
    }
    
    QCheckBox::indicator:hover {
        border-color: #dc3545;
        background-color: #f8f9fa;
        transform: scale(1.05);
    }
    
    QCheckBox::indicator:unchecked {
        background-color: #ffffff;
        border: 2px solid #6c757d;
    }
    
    QCheckBox::indicator:unchecked:hover {
        background-color: #fff5f5;
        border: 2px solid #dc3545;
    }
    
    QCheckBox::indicator:checked {
        background-color: #dc3545;
        border: 2px solid #dc3545;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    
    QCheckBox::indicator:checked:hover {
        background-color: #c82333;
        border: 2px solid #c82333;
    }
    
    QCheckBox::indicator:checked:before {
        content: "✓";
        color: white;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        position: absolute;
        top: 1px;
        left: 3px;
    }
    """

def create_form_checkbox(text="", tooltip=""):
    """
    Create a checkbox with standard form styling.

    This factory function creates a properly styled checkbox for use in
    forms and data entry contexts. It applies the standard form styling
    and optionally sets text and tooltip.

    Args:
        text (str, optional): Label text to display next to checkbox
        tooltip (str, optional): Tooltip text for user guidance

    Returns:
        QCheckBox: Configured checkbox widget with form styling applied

    Example:
        checkbox = create_form_checkbox(
            "Enable automatic backup",
            "Check to enable daily automatic backups"
        )
    """
    checkbox = QCheckBox(text)
    checkbox.setStyleSheet(get_checkbox_style())
    if tooltip:
        checkbox.setToolTip(tooltip)
    return checkbox

def create_table_checkbox(tooltip="Click to select this item"):
    """
    Create a checkbox with table selection styling.

    This factory function creates a properly styled checkbox for use in
    table rows for item selection. It applies the table-specific styling
    and sets a default tooltip for selection guidance.

    Args:
        tooltip (str, optional): Tooltip text for selection guidance
                               Defaults to "Click to select this item"

    Returns:
        QCheckBox: Configured checkbox widget with table styling applied

    Example:
        checkbox = create_table_checkbox("Select this expense for deletion")
        # Add to table cell
        table.setCellWidget(row, 0, checkbox)
    """
    checkbox = QCheckBox()
    checkbox.setStyleSheet(get_table_checkbox_style())
    checkbox.setToolTip(tooltip)
    return checkbox
