"""
Enhanced filtering dialog for table data
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateEdit, QPushButton, QGroupBox, QGridLayout,
    QCheckBox, QSpinBox, QDoubleSpinBox, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
import re

class AdvancedFilterDialog(QDialog):
    """Advanced filtering dialog for table data"""

    # Signal emitted when filters are applied
    filtersApplied = pyqtSignal(dict)

    def __init__(self, parent=None, filter_type="expenses"):
        super().__init__(parent)
        self.filter_type = filter_type
        self.setWindowTitle(f"Advanced {filter_type.title()} Filters")
        self.setModal(True)
        self.resize(500, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the filter dialog UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Advanced {self.filter_type.title()} Filters")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Date Range Filter
        date_group = QGroupBox("Date Range")
        date_layout = QGridLayout()

        # Predefined date ranges
        self.date_preset = QComboBox()
        self.date_preset.addItems([
            "Custom Range", "Today", "Yesterday", "This Week", "Last Week",
            "This Month", "Last Month", "This Quarter", "Last Quarter",
            "This Year", "Last Year", "Last 30 Days", "Last 90 Days"
        ])
        self.date_preset.currentTextChanged.connect(self.on_date_preset_changed)

        date_layout.addWidget(QLabel("Quick Select:"), 0, 0)
        date_layout.addWidget(self.date_preset, 0, 1, 1, 2)

        # Custom date range
        date_layout.addWidget(QLabel("From:"), 1, 0)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.start_date, 1, 1)

        date_layout.addWidget(QLabel("To:"), 1, 2)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date, 1, 3)

        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # Amount Range Filter
        amount_group = QGroupBox("Amount Range")
        amount_layout = QGridLayout()

        self.amount_enabled = QCheckBox("Enable amount filtering")
        amount_layout.addWidget(self.amount_enabled, 0, 0, 1, 4)

        amount_layout.addWidget(QLabel("Min Amount:"), 1, 0)
        self.min_amount = QDoubleSpinBox()
        self.min_amount.setPrefix("$")
        self.min_amount.setMinimum(0.0)
        self.min_amount.setMaximum(999999.99)
        self.min_amount.setEnabled(False)
        amount_layout.addWidget(self.min_amount, 1, 1)

        amount_layout.addWidget(QLabel("Max Amount:"), 1, 2)
        self.max_amount = QDoubleSpinBox()
        self.max_amount.setPrefix("$")
        self.max_amount.setMinimum(0.0)
        self.max_amount.setMaximum(999999.99)
        self.max_amount.setValue(1000.0)
        self.max_amount.setEnabled(False)
        amount_layout.addWidget(self.max_amount, 1, 3)

        self.amount_enabled.toggled.connect(self.min_amount.setEnabled)
        self.amount_enabled.toggled.connect(self.max_amount.setEnabled)

        amount_group.setLayout(amount_layout)
        layout.addWidget(amount_group)

        # Text Search Filter
        text_group = QGroupBox("Text Search")
        text_layout = QGridLayout()

        self.text_enabled = QCheckBox("Enable text search")
        text_layout.addWidget(self.text_enabled, 0, 0, 1, 2)

        text_layout.addWidget(QLabel("Search in:"), 1, 0)
        self.search_field = QComboBox()
        self.search_field.addItems(["Description", "Category", "Subcategory", "All Fields"])
        self.search_field.setEnabled(False)
        text_layout.addWidget(self.search_field, 1, 1)

        text_layout.addWidget(QLabel("Search Text:"), 2, 0)
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Enter search terms...")
        self.search_text.setEnabled(False)
        text_layout.addWidget(self.search_text, 2, 1)

        self.case_sensitive = QCheckBox("Case sensitive")
        self.case_sensitive.setEnabled(False)
        text_layout.addWidget(self.case_sensitive, 3, 0, 1, 2)

        self.text_enabled.toggled.connect(self.search_field.setEnabled)
        self.text_enabled.toggled.connect(self.search_text.setEnabled)
        self.text_enabled.toggled.connect(self.case_sensitive.setEnabled)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Person Filter (if applicable)
        if self.filter_type in ["expenses", "income"]:
            person_group = QGroupBox("Person Filter")
            person_layout = QHBoxLayout()

            self.person_all = QCheckBox("All")
            self.person_all.setChecked(True)
            self.person_jeff = QCheckBox("Jeff")
            self.person_vanessa = QCheckBox("Vanessa")

            self.person_all.toggled.connect(self.on_person_all_toggled)
            self.person_jeff.toggled.connect(self.on_person_individual_toggled)
            self.person_vanessa.toggled.connect(self.on_person_individual_toggled)

            person_layout.addWidget(self.person_all)
            person_layout.addWidget(self.person_jeff)
            person_layout.addWidget(self.person_vanessa)
            person_layout.addStretch()

            person_group.setLayout(person_layout)
            layout.addWidget(person_group)

        # Category Filter (for expenses)
        if self.filter_type == "expenses":
            category_group = QGroupBox("Category Filter")
            category_layout = QVBoxLayout()

            self.category_enabled = QCheckBox("Filter by category")
            category_layout.addWidget(self.category_enabled)

            self.category_combo = QComboBox()
            self.category_combo.setEnabled(False)
            category_layout.addWidget(self.category_combo)

            self.category_enabled.toggled.connect(self.category_combo.setEnabled)

            category_group.setLayout(category_layout)
            layout.addWidget(category_group)

        # Buttons
        button_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_filters)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply Filters")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        apply_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(apply_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def on_date_preset_changed(self, preset):
        """Handle predefined date range selection"""
        today = QDate.currentDate()

        if preset == "Today":
            self.start_date.setDate(today)
            self.end_date.setDate(today)
        elif preset == "Yesterday":
            yesterday = today.addDays(-1)
            self.start_date.setDate(yesterday)
            self.end_date.setDate(yesterday)
        elif preset == "This Week":
            start_of_week = today.addDays(-(today.dayOfWeek() - 1))
            self.start_date.setDate(start_of_week)
            self.end_date.setDate(today)
        elif preset == "Last Week":
            start_of_last_week = today.addDays(-(today.dayOfWeek() - 1) - 7)
            end_of_last_week = start_of_last_week.addDays(6)
            self.start_date.setDate(start_of_last_week)
            self.end_date.setDate(end_of_last_week)
        elif preset == "This Month":
            start_of_month = QDate(today.year(), today.month(), 1)
            self.start_date.setDate(start_of_month)
            self.end_date.setDate(today)
        elif preset == "Last Month":
            if today.month() == 1:
                last_month = QDate(today.year() - 1, 12, 1)
                last_month_end = QDate(today.year() - 1, 12, 31)
            else:
                last_month = QDate(today.year(), today.month() - 1, 1)
                last_month_end = QDate(today.year(), today.month(), 1).addDays(-1)
            self.start_date.setDate(last_month)
            self.end_date.setDate(last_month_end)
        elif preset == "Last 30 Days":
            self.start_date.setDate(today.addDays(-30))
            self.end_date.setDate(today)
        elif preset == "Last 90 Days":
            self.start_date.setDate(today.addDays(-90))
            self.end_date.setDate(today)
        elif preset == "This Year":
            start_of_year = QDate(today.year(), 1, 1)
            self.start_date.setDate(start_of_year)
            self.end_date.setDate(today)
        elif preset == "Last Year":
            start_of_last_year = QDate(today.year() - 1, 1, 1)
            end_of_last_year = QDate(today.year() - 1, 12, 31)
            self.start_date.setDate(start_of_last_year)
            self.end_date.setDate(end_of_last_year)

    def on_person_all_toggled(self, checked):
        """Handle 'All' checkbox for person filter"""
        if checked:
            self.person_jeff.setChecked(False)
            self.person_vanessa.setChecked(False)

    def on_person_individual_toggled(self):
        """Handle individual person checkboxes"""
        if self.person_jeff.isChecked() or self.person_vanessa.isChecked():
            self.person_all.setChecked(False)
        elif not self.person_jeff.isChecked() and not self.person_vanessa.isChecked():
            self.person_all.setChecked(True)

    def clear_filters(self):
        """Clear all filter settings"""
        self.date_preset.setCurrentText("Custom Range")
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())

        self.amount_enabled.setChecked(False)
        self.min_amount.setValue(0.0)
        self.max_amount.setValue(1000.0)

        self.text_enabled.setChecked(False)
        self.search_text.clear()
        self.case_sensitive.setChecked(False)

        if hasattr(self, 'person_all'):
            self.person_all.setChecked(True)
            self.person_jeff.setChecked(False)
            self.person_vanessa.setChecked(False)

        if hasattr(self, 'category_enabled'):
            self.category_enabled.setChecked(False)

    def apply_filters(self):
        """Apply the selected filters"""
        filters = {
            'start_date': self.start_date.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date.date().toString("yyyy-MM-dd"),
        }

        # Amount filter
        if self.amount_enabled.isChecked():
            filters['min_amount'] = self.min_amount.value()
            filters['max_amount'] = self.max_amount.value()

        # Text search filter
        if self.text_enabled.isChecked() and self.search_text.text().strip():
            filters['search_text'] = self.search_text.text().strip()
            filters['search_field'] = self.search_field.currentText()
            filters['case_sensitive'] = self.case_sensitive.isChecked()

        # Person filter
        if hasattr(self, 'person_all'):
            if not self.person_all.isChecked():
                selected_persons = []
                if self.person_jeff.isChecked():
                    selected_persons.append("Jeff")
                if self.person_vanessa.isChecked():
                    selected_persons.append("Vanessa")
                if selected_persons:
                    filters['persons'] = selected_persons

        # Category filter
        if hasattr(self, 'category_enabled') and self.category_enabled.isChecked():
            if self.category_combo.currentText():
                filters['category'] = self.category_combo.currentText()

        self.filtersApplied.emit(filters)
        self.accept()

    def set_categories(self, categories):
        """Set available categories for filtering"""
        if hasattr(self, 'category_combo'):
            self.category_combo.clear()
            self.category_combo.addItems(["All Categories"] + sorted(categories))
