"""
Net Worth Tab - Track assets and calculate net worth over time
Maintains a mutable list of assets with current values, history stored in backend for charts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QDateEdit, QTextEdit, QSplitter,
    QHeaderView, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis, QPieSeries
from datetime import datetime
import csv
from database.db_manager import DatabaseManager

# Define asset categories and subcategories with default liquidity ratings
ASSET_CATEGORIES = {
    "Retirement": {
        "subcategories": ["Roth 401k", "Traditional 401k", "Roth IRA", "Traditional IRA", "Pension", "403b", "457"],
        "default_liquidity": 2,
        "color": "#4CAF50"
    },
    "Brokerage Account": {
        "subcategories": ["Investments", "Individual Stocks", "ETFs", "Mutual Funds", "Bonds"],
        "default_liquidity": 8,
        "color": "#2196F3"
    },
    "Real Asset": {
        "subcategories": ["House", "Condo", "Land", "Rental Property", "Commercial Property"],
        "default_liquidity": 1,
        "color": "#FF9800"
    },
    "Checking Account": {
        "subcategories": ["Cash", "Primary Checking", "Secondary Checking"],
        "default_liquidity": 10,
        "color": "#00BCD4"
    },
    "Savings Account": {
        "subcategories": ["Cash", "Emergency Fund", "High-Yield Savings", "Money Market"],
        "default_liquidity": 9,
        "color": "#009688"
    },
    "Trust": {
        "subcategories": ["Investments", "Family Trust", "Revocable Trust", "Irrevocable Trust"],
        "default_liquidity": 3,
        "color": "#9C27B0"
    },
    "HSA": {
        "subcategories": ["Health Savings", "Investments"],
        "default_liquidity": 6,
        "color": "#E91E63"
    },
    "529 Plan": {
        "subcategories": ["Education Savings", "Investments"],
        "default_liquidity": 3,
        "color": "#673AB7"
    },
    "Cryptocurrency": {
        "subcategories": ["Bitcoin", "Ethereum", "Altcoins", "Stablecoins"],
        "default_liquidity": 7,
        "color": "#FFC107"
    },
    "Precious Metals": {
        "subcategories": ["Gold", "Silver", "Platinum", "Collectibles"],
        "default_liquidity": 4,
        "color": "#795548"
    },
    "Vehicle": {
        "subcategories": ["Car", "Motorcycle", "Boat", "RV"],
        "default_liquidity": 3,
        "color": "#607D8B"
    },
    "Debt/Liability": {
        "subcategories": ["Mortgage", "Auto Loan", "Student Loan", "Credit Card", "Personal Loan", "HELOC"],
        "default_liquidity": 0,
        "color": "#F44336"
    },
    "Other": {
        "subcategories": ["Other Asset", "Business Interest", "Art", "Jewelry", "Collectibles"],
        "default_liquidity": 2,
        "color": "#9E9E9E"
    }
}

# Preset assets to get users started
PRESET_ASSETS = [
    {"name": "Jeff's TD 401k", "person": "Jeff", "category": "Retirement", "subcategory": "Roth 401k", "liquidity": 2},
    {"name": "Vanessa's Roth 401k", "person": "Vanessa", "category": "Retirement", "subcategory": "Roth 401k", "liquidity": 2},
    {"name": "Jeff's Schwab Roth", "person": "Jeff", "category": "Retirement", "subcategory": "Roth IRA", "liquidity": 2},
    {"name": "618 Chase Court", "person": "Joint", "category": "Real Asset", "subcategory": "House", "liquidity": 1},
    {"name": "Lima Condo", "person": "Joint", "category": "Real Asset", "subcategory": "Condo", "liquidity": 1},
    {"name": "Joint Schwab Brokerage", "person": "Joint", "category": "Brokerage Account", "subcategory": "Investments", "liquidity": 8},
    {"name": "TD Joint Checking", "person": "Joint", "category": "Checking Account", "subcategory": "Cash", "liquidity": 10},
    {"name": "Joint Savings Account", "person": "Joint", "category": "Savings Account", "subcategory": "Cash", "liquidity": 9},
    {"name": "Jeff's Trust", "person": "Jeff", "category": "Trust", "subcategory": "Investments", "liquidity": 3},
]


class AddAssetDialog(QDialog):
    """Dialog to add a new asset to the list"""

    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.categories = categories or ASSET_CATEGORIES
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Add New Asset")
        self.setModal(True)
        self.resize(450, 400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Asset name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Jeff's Fidelity 401k")
        form_layout.addRow("Asset Name:", self.name_input)

        # Person
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa", "Joint"])
        form_layout.addRow("Person:", self.person_combo)

        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(sorted(self.categories.keys()))
        form_layout.addRow("Category:", self.category_combo)

        # Subcategory
        self.subcategory_combo = QComboBox()
        form_layout.addRow("Subcategory:", self.subcategory_combo)

        # Initial Value
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("0.00")
        self.value_input.setText("0")
        form_layout.addRow("Initial Value:", self.value_input)

        # Liquidity - CREATE THIS BEFORE connecting category signal
        self.liquidity_spin = QSpinBox()
        self.liquidity_spin.setRange(1, 10)
        self.liquidity_spin.setValue(5)
        self.liquidity_spin.setToolTip("1 = Least liquid, 10 = Most liquid (cash)")
        form_layout.addRow("Liquidity (1-10):", self.liquidity_spin)

        # Comments
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Notes about this asset...")
        form_layout.addRow("Comments:", self.notes_input)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # NOW connect the category signal and initialize subcategories
        # (after liquidity_spin exists)
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        self.on_category_changed(self.category_combo.currentText())

    def on_category_changed(self, category):
        self.subcategory_combo.clear()
        if category in self.categories:
            self.subcategory_combo.addItems(self.categories[category].get('subcategories', []))
            self.liquidity_spin.setValue(self.categories[category].get('default_liquidity', 5))

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter an asset name")
            return
        self.accept()

    def get_data(self):
        try:
            value = float(self.value_input.text().replace(",", "").replace("$", "") or "0")
        except ValueError:
            value = 0

        return {
            "name": self.name_input.text().strip(),
            "person": self.person_combo.currentText(),
            "category": self.category_combo.currentText(),
            "subcategory": self.subcategory_combo.currentText(),
            "value": value,
            "liquidity": self.liquidity_spin.value(),
            "notes": self.notes_input.toPlainText()
        }


class AddCategoryDialog(QDialog):
    """Dialog to add a new category or subcategory"""

    def __init__(self, parent=None, existing_categories=None):
        super().__init__(parent)
        self.existing_categories = existing_categories or ASSET_CATEGORIES
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Add New Category")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.category_type_combo = QComboBox()
        self.category_type_combo.addItems(["Add to existing category", "Create new category"])
        self.category_type_combo.currentIndexChanged.connect(self.on_category_type_changed)
        form_layout.addRow("Action:", self.category_type_combo)

        self.existing_category_combo = QComboBox()
        self.existing_category_combo.addItems(sorted(self.existing_categories.keys()))
        form_layout.addRow("Existing Category:", self.existing_category_combo)

        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("Enter new category name")
        self.new_category_input.setEnabled(False)
        form_layout.addRow("New Category:", self.new_category_input)

        self.new_subcategory_input = QLineEdit()
        self.new_subcategory_input.setPlaceholderText("Enter new subcategory name")
        form_layout.addRow("New Subcategory:", self.new_subcategory_input)

        self.liquidity_spin = QSpinBox()
        self.liquidity_spin.setRange(1, 10)
        self.liquidity_spin.setValue(5)
        form_layout.addRow("Default Liquidity:", self.liquidity_spin)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_category_type_changed(self, index):
        is_new = index == 1
        self.existing_category_combo.setEnabled(not is_new)
        self.new_category_input.setEnabled(is_new)

    def get_data(self):
        is_new_category = self.category_type_combo.currentIndex() == 1
        return {
            "is_new_category": is_new_category,
            "category": self.new_category_input.text().strip() if is_new_category else self.existing_category_combo.currentText(),
            "subcategory": self.new_subcategory_input.text().strip(),
            "liquidity": self.liquidity_spin.value()
        }


class NetWorthTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.categories = dict(ASSET_CATEGORIES)
        self.assets_list = []  # Mutable list of current assets
        self.init_ui()
        self.initialize_preset_assets()
        self.load_assets()
        self.refresh_display()

    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Net Worth Tracker")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Add Asset button
        add_asset_btn = QPushButton("+ Add Asset")
        add_asset_btn.clicked.connect(self.show_add_asset_dialog)
        add_asset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        header_layout.addWidget(add_asset_btn)

        # Add Category button
        add_category_btn = QPushButton("+ Add Category")
        add_category_btn.clicked.connect(self.add_category)
        add_category_btn.setStyleSheet("background-color: #9C27B0; color: white; padding: 8px;")
        header_layout.addWidget(add_category_btn)

        main_layout.addLayout(header_layout)

        # Create main vertical splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section - Summary and Assets Table
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        # Summary cards at the top
        summary_widget = self.create_summary_section()
        top_layout.addWidget(summary_widget)

        # Assets table - the main mutable list
        table_group = QGroupBox("Assets (Click value cell to edit, double-click row to edit all details)")
        table_layout = QVBoxLayout(table_group)

        # Table toolbar
        toolbar_layout = QHBoxLayout()

        # Filter
        toolbar_layout.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Assets"] + sorted(self.categories.keys()))
        self.filter_combo.currentTextChanged.connect(self.refresh_display)
        toolbar_layout.addWidget(self.filter_combo)

        toolbar_layout.addStretch()

        # CSV buttons
        export_template_btn = QPushButton("📋 Export Template")
        export_template_btn.setToolTip("Export a template with all assets (values blank) to update")
        export_template_btn.clicked.connect(self.export_template)
        export_template_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
        toolbar_layout.addWidget(export_template_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        toolbar_layout.addWidget(export_btn)

        import_btn = QPushButton("Import CSV")
        import_btn.clicked.connect(self.import_csv)
        toolbar_layout.addWidget(import_btn)

        # Save snapshot button
        save_snapshot_btn = QPushButton("📸 Save Snapshot")
        save_snapshot_btn.setToolTip("Save current values to history for tracking over time")
        save_snapshot_btn.clicked.connect(self.save_snapshot)
        save_snapshot_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 8px;")
        toolbar_layout.addWidget(save_snapshot_btn)

        table_layout.addLayout(toolbar_layout)

        # Create the assets table
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(8)
        self.assets_table.setHorizontalHeaderLabels([
            "Asset Name", "Person", "Category", "Subcategory",
            "Value", "Liquidity", "Comments", "ID"
        ])
        self.assets_table.hideColumn(7)  # Hide ID column

        # Make value column editable directly
        self.assets_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.assets_table.cellChanged.connect(self.on_cell_changed)
        self.assets_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.assets_table.setAlternatingRowColors(True)

        # Set column widths
        header = self.assets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)       # Asset Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Person
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Subcategory
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)         # Value
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)         # Liquidity
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)       # Comments

        self.assets_table.setColumnWidth(4, 120)  # Value
        self.assets_table.setColumnWidth(5, 70)   # Liquidity

        table_layout.addWidget(self.assets_table)
        top_layout.addWidget(table_group)

        main_splitter.addWidget(top_widget)

        # Bottom section - Charts
        charts_widget = self.create_charts_section()
        main_splitter.addWidget(charts_widget)

        main_splitter.setSizes([450, 300])

        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

    def create_summary_section(self):
        """Create the summary cards section"""
        summary_group = QGroupBox("Net Worth Summary")
        summary_layout = QGridLayout(summary_group)

        self.jeff_total_label = self.create_summary_card("Jeff's Assets", "$0.00")
        summary_layout.addWidget(self.jeff_total_label, 0, 0)

        self.vanessa_total_label = self.create_summary_card("Vanessa's Assets", "$0.00")
        summary_layout.addWidget(self.vanessa_total_label, 0, 1)

        self.joint_total_label = self.create_summary_card("Joint Assets", "$0.00")
        summary_layout.addWidget(self.joint_total_label, 0, 2)

        self.total_net_worth_label = self.create_summary_card("Total Net Worth", "$0.00")
        self.total_net_worth_label.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 3px solid #4CAF50;
                border-radius: 8px;
            }
        """)
        summary_layout.addWidget(self.total_net_worth_label, 0, 3)

        self.liquid_assets_label = self.create_summary_card("Liquid (7-10)", "$0.00")
        summary_layout.addWidget(self.liquid_assets_label, 0, 4)

        self.illiquid_assets_label = self.create_summary_card("Illiquid (1-6)", "$0.00")
        summary_layout.addWidget(self.illiquid_assets_label, 0, 5)

        return summary_group

    def create_summary_card(self, title, value):
        """Create a summary card widget"""
        group = QGroupBox()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 9))

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2a82da;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        group.setLayout(layout)
        group.value_label = value_label
        return group

    def create_charts_section(self):
        """Create the bottom section with charts"""
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)

        # Left chart - Net Worth Over Time
        left_chart_group = QGroupBox("Net Worth History")
        left_chart_layout = QVBoxLayout(left_chart_group)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("View:"))
        self.growth_category_filter = QComboBox()
        self.growth_category_filter.addItems(["Total Net Worth", "Retirement", "Real Asset",
                                               "Brokerage Account", "Checking Account", "Savings Account"])
        self.growth_category_filter.currentTextChanged.connect(self.update_growth_chart)
        filter_layout.addWidget(self.growth_category_filter)
        filter_layout.addStretch()
        left_chart_layout.addLayout(filter_layout)

        self.growth_chart = QChart()
        self.growth_chart.setTitle("Value Over Time")
        self.growth_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.growth_chart_view = QChartView(self.growth_chart)
        self.growth_chart_view.setMinimumHeight(180)
        left_chart_layout.addWidget(self.growth_chart_view)

        charts_layout.addWidget(left_chart_group)

        # Right chart - Allocation Pie
        right_chart_group = QGroupBox("Asset Allocation")
        right_chart_layout = QVBoxLayout(right_chart_group)

        # Add dropdown to select what to show in pie chart
        pie_filter_layout = QHBoxLayout()
        pie_filter_layout.addWidget(QLabel("View:"))
        self.pie_category_filter = QComboBox()
        self.pie_category_filter.addItems(["All Categories"] + sorted(self.categories.keys()))
        self.pie_category_filter.currentTextChanged.connect(self.update_allocation_chart)
        pie_filter_layout.addWidget(self.pie_category_filter)
        pie_filter_layout.addStretch()
        right_chart_layout.addLayout(pie_filter_layout)

        self.allocation_chart = QChart()
        self.allocation_chart.setTitle("Current Distribution")
        self.allocation_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.allocation_chart.legend().setVisible(True)
        self.allocation_chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        self.allocation_chart_view = QChartView(self.allocation_chart)
        self.allocation_chart_view.setMinimumHeight(180)
        right_chart_layout.addWidget(self.allocation_chart_view)

        charts_layout.addWidget(right_chart_group)

        return charts_widget

    def initialize_preset_assets(self):
        """Initialize preset assets if none exist"""
        try:
            existing = self.db.get_current_assets()
            if len(existing) == 0:
                for preset in PRESET_ASSETS:
                    self.db.upsert_asset(
                        asset_name=preset['name'],
                        person=preset['person'],
                        category=preset['category'],
                        subcategory=preset['subcategory'],
                        value=0,
                        liquidity=preset['liquidity'],
                        notes=""
                    )
        except Exception as e:
            print(f"Error initializing preset assets: {e}")

    def load_assets(self):
        """Load current assets from database into the mutable list"""
        try:
            self.assets_list = self.db.get_current_assets()
        except Exception as e:
            print(f"Error loading assets: {e}")
            self.assets_list = []

    def refresh_display(self):
        """Refresh the table and summary displays"""
        self.refresh_table()
        self.refresh_summary()
        self.update_growth_chart()
        self.update_allocation_chart()

    def refresh_table(self):
        """Refresh the assets table"""
        # Block signals to prevent triggering cellChanged during population
        self.assets_table.blockSignals(True)
        self.assets_table.setSortingEnabled(False)

        try:
            # Get filter
            filter_category = self.filter_combo.currentText()

            # Filter assets
            if filter_category == "All Assets":
                display_assets = self.assets_list
            else:
                display_assets = [a for a in self.assets_list if a.get('category') == filter_category]

            # Sort by category, then name
            display_assets = sorted(display_assets, key=lambda x: (
                x.get('category', '') or '',
                x.get('asset_name', '') or ''
            ))

            self.assets_table.setRowCount(0)

            for asset in display_assets:
                row = self.assets_table.rowCount()
                self.assets_table.insertRow(row)

                # Asset Name (not directly editable)
                name_item = QTableWidgetItem(asset.get('asset_name', ''))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assets_table.setItem(row, 0, name_item)

                # Person
                person_item = QTableWidgetItem(asset.get('person', ''))
                person_item.setFlags(person_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assets_table.setItem(row, 1, person_item)

                # Category
                cat_item = QTableWidgetItem(asset.get('category', ''))
                cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assets_table.setItem(row, 2, cat_item)

                # Subcategory
                subcat_item = QTableWidgetItem(asset.get('subcategory', ''))
                subcat_item.setFlags(subcat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assets_table.setItem(row, 3, subcat_item)

                # Value - EDITABLE
                value = asset.get('value', 0) or 0
                value_item = QTableWidgetItem(f"${value:,.2f}")
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if value >= 0:
                    value_item.setForeground(QColor("#4CAF50"))
                else:
                    value_item.setForeground(QColor("#F44336"))
                self.assets_table.setItem(row, 4, value_item)

                # Liquidity
                liquidity = asset.get('liquidity', 5) or 5
                liq_item = QTableWidgetItem(str(liquidity))
                liq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                liq_item.setFlags(liq_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if liquidity >= 7:
                    liq_item.setBackground(QColor("#C8E6C9"))
                elif liquidity >= 4:
                    liq_item.setBackground(QColor("#FFF9C4"))
                else:
                    liq_item.setBackground(QColor("#FFCDD2"))
                self.assets_table.setItem(row, 5, liq_item)

                # Comments
                notes_item = QTableWidgetItem(asset.get('notes', '') or '')
                notes_item.setFlags(notes_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.assets_table.setItem(row, 6, notes_item)

                # ID (hidden)
                self.assets_table.setItem(row, 7, QTableWidgetItem(str(asset.get('id', ''))))

        finally:
            self.assets_table.setSortingEnabled(True)
            self.assets_table.blockSignals(False)

    def refresh_summary(self):
        """Refresh summary totals"""
        jeff_total = sum(a.get('value', 0) or 0 for a in self.assets_list if a.get('person') == 'Jeff')
        vanessa_total = sum(a.get('value', 0) or 0 for a in self.assets_list if a.get('person') == 'Vanessa')
        joint_total = sum(a.get('value', 0) or 0 for a in self.assets_list if a.get('person') == 'Joint')
        total = jeff_total + vanessa_total + joint_total

        liquid_total = sum(a.get('value', 0) or 0 for a in self.assets_list if (a.get('liquidity', 5) or 5) >= 7)
        illiquid_total = sum(a.get('value', 0) or 0 for a in self.assets_list if (a.get('liquidity', 5) or 5) < 7)

        self.jeff_total_label.value_label.setText(f"${jeff_total:,.2f}")
        self.vanessa_total_label.value_label.setText(f"${vanessa_total:,.2f}")
        self.joint_total_label.value_label.setText(f"${joint_total:,.2f}")
        self.total_net_worth_label.value_label.setText(f"${total:,.2f}")
        self.liquid_assets_label.value_label.setText(f"${liquid_total:,.2f}")
        self.illiquid_assets_label.value_label.setText(f"${illiquid_total:,.2f}")

        # Color code total
        if total >= 0:
            self.total_net_worth_label.value_label.setStyleSheet("color: #4CAF50; font-size: 14px; font-weight: bold;")
        else:
            self.total_net_worth_label.value_label.setStyleSheet("color: #F44336; font-size: 14px; font-weight: bold;")

    def on_cell_double_clicked(self, row, column):
        """Handle double-click on cells"""
        if column == 4:  # Value column - allow direct editing
            self.assets_table.editItem(self.assets_table.item(row, column))
        else:
            # For other columns, open full edit dialog
            self.edit_asset_dialog(row)

    def on_cell_changed(self, row, column):
        """Handle cell value changes (for direct value editing)"""
        if column != 4:  # Only handle Value column changes
            return

        try:
            # Get asset ID
            id_item = self.assets_table.item(row, 7)
            if not id_item:
                return
            asset_id = int(id_item.text())

            # Get new value
            value_text = self.assets_table.item(row, 4).text()
            value = float(value_text.replace("$", "").replace(",", ""))

            # Update in database
            self.db.update_asset_value(asset_id, value)

            # Update local list
            for asset in self.assets_list:
                if asset.get('id') == asset_id:
                    asset['value'] = value
                    break

            # Refresh display
            self.refresh_summary()
            self.update_allocation_chart()

        except Exception as e:
            print(f"Error updating value: {e}")
            # Reload to revert invalid changes
            self.load_assets()
            self.refresh_display()

    def edit_asset_dialog(self, row):
        """Open dialog to edit ALL asset details"""
        try:
            id_item = self.assets_table.item(row, 7)
            if not id_item:
                return
            asset_id = int(id_item.text())

            # Find asset in list
            asset = None
            for a in self.assets_list:
                if a.get('id') == asset_id:
                    asset = a
                    break

            if not asset:
                return

            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Asset")
            dialog.setModal(True)
            dialog.resize(500, 450)

            layout = QVBoxLayout(dialog)
            form_layout = QFormLayout()

            # Asset name - EDITABLE
            name_input = QLineEdit()
            name_input.setText(asset.get('asset_name', ''))
            name_input.setFont(QFont("Arial", 11))
            form_layout.addRow("Asset Name:", name_input)

            # Person - EDITABLE
            person_combo = QComboBox()
            person_combo.addItems(["Jeff", "Vanessa", "Joint"])
            person_combo.setCurrentText(asset.get('person', 'Joint'))
            form_layout.addRow("Person:", person_combo)

            # Category - EDITABLE
            category_combo = QComboBox()
            category_combo.addItems(sorted(self.categories.keys()))
            current_category = asset.get('category', 'Other')
            if current_category in self.categories:
                category_combo.setCurrentText(current_category)
            form_layout.addRow("Category:", category_combo)

            # Subcategory - EDITABLE
            subcategory_combo = QComboBox()
            def update_subcategories(cat):
                subcategory_combo.clear()
                if cat in self.categories:
                    subcategory_combo.addItems(self.categories[cat].get('subcategories', []))
                    # Try to restore previous subcategory
                    prev_subcat = asset.get('subcategory', '')
                    idx = subcategory_combo.findText(prev_subcat)
                    if idx >= 0:
                        subcategory_combo.setCurrentIndex(idx)

            category_combo.currentTextChanged.connect(update_subcategories)
            update_subcategories(current_category)
            if asset.get('subcategory'):
                idx = subcategory_combo.findText(asset.get('subcategory'))
                if idx >= 0:
                    subcategory_combo.setCurrentIndex(idx)
            form_layout.addRow("Subcategory:", subcategory_combo)

            # Value - EDITABLE
            value_input = QLineEdit()
            value_input.setText(f"{asset.get('value', 0):,.2f}")
            form_layout.addRow("Value:", value_input)

            # Liquidity - EDITABLE
            liquidity_spin = QSpinBox()
            liquidity_spin.setRange(1, 10)
            liquidity_spin.setValue(asset.get('liquidity', 5) or 5)
            liquidity_spin.setToolTip("1 = Least liquid, 10 = Most liquid (cash)")
            form_layout.addRow("Liquidity (1-10):", liquidity_spin)

            # Notes - EDITABLE
            notes_input = QTextEdit()
            notes_input.setMaximumHeight(80)
            notes_input.setText(asset.get('notes', '') or '')
            form_layout.addRow("Comments:", notes_input)

            layout.addLayout(form_layout)

            # Buttons
            btn_layout = QHBoxLayout()

            save_btn = QPushButton("Save Changes")
            save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px 20px; font-weight: bold;")

            delete_btn = QPushButton("Delete Asset")
            delete_btn.setStyleSheet("background-color: #F44336; color: white; padding: 10px 20px;")

            cancel_btn = QPushButton("Cancel")
            cancel_btn.setStyleSheet("padding: 10px 20px;")

            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(save_btn)

            layout.addLayout(btn_layout)

            # Connect buttons
            def save_changes():
                try:
                    new_name = name_input.text().strip()
                    if not new_name:
                        QMessageBox.warning(dialog, "Warning", "Asset name cannot be empty")
                        return

                    new_value = float(value_input.text().replace(",", "").replace("$", ""))

                    self.db.update_asset_all_fields(
                        asset_id,
                        asset_name=new_name,
                        person=person_combo.currentText(),
                        category=category_combo.currentText(),
                        subcategory=subcategory_combo.currentText(),
                        value=new_value,
                        liquidity=liquidity_spin.value(),
                        notes=notes_input.toPlainText()
                    )
                    self.load_assets()
                    self.refresh_display()
                    dialog.accept()
                    QMessageBox.information(self, "Success", "Asset updated successfully!")
                except Exception as e:
                    QMessageBox.critical(dialog, "Error", f"Failed to save: {str(e)}")

            def delete_asset():
                reply = QMessageBox.question(
                    dialog, "Confirm Delete",
                    f"Delete '{asset.get('asset_name', '')}'?\n\nThis will remove it from your asset list.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.db.delete_asset(asset_id)
                    self.load_assets()
                    self.refresh_display()
                    dialog.accept()

            save_btn.clicked.connect(save_changes)
            delete_btn.clicked.connect(delete_asset)
            cancel_btn.clicked.connect(dialog.reject)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit asset: {str(e)}")

    def show_add_asset_dialog(self):
        """Show dialog to add a new asset"""
        dialog = AddAssetDialog(self, self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                self.db.upsert_asset(
                    asset_name=data['name'],
                    person=data['person'],
                    category=data['category'],
                    subcategory=data['subcategory'],
                    value=data['value'],
                    liquidity=data['liquidity'],
                    notes=data['notes']
                )
                self.load_assets()
                self.refresh_display()
                QMessageBox.information(self, "Success", f"Added asset: {data['name']}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add asset: {str(e)}")

    def add_category(self):
        """Add a new category or subcategory"""
        dialog = AddCategoryDialog(self, self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            if data['is_new_category']:
                if data['category']:
                    self.categories[data['category']] = {
                        'subcategories': [data['subcategory']] if data['subcategory'] else [],
                        'default_liquidity': data['liquidity'],
                        'color': '#9E9E9E'
                    }
                    self.filter_combo.clear()
                    self.filter_combo.addItems(["All Assets"] + sorted(self.categories.keys()))
                    QMessageBox.information(self, "Success", f"Added category: {data['category']}")
            else:
                if data['category'] in self.categories and data['subcategory']:
                    if data['subcategory'] not in self.categories[data['category']]['subcategories']:
                        self.categories[data['category']]['subcategories'].append(data['subcategory'])
                        QMessageBox.information(self, "Success", f"Added subcategory: {data['subcategory']}")

    def save_snapshot(self):
        """Save current values to history for tracking over time"""
        try:
            self.db.save_net_worth_snapshot(self.assets_list)
            QMessageBox.information(self, "Success",
                "Snapshot saved! Your current asset values have been recorded for historical tracking.")
            self.update_growth_chart()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save snapshot: {str(e)}")

    def update_growth_chart(self):
        """Update the growth chart with historical data"""
        try:
            self.growth_chart.removeAllSeries()
            for axis in self.growth_chart.axes():
                self.growth_chart.removeAxis(axis)

            category = self.growth_category_filter.currentText()
            history = self.db.get_net_worth_history(category)

            if not history:
                return

            series = QLineSeries()
            series.setName(category)

            min_value = float('inf')
            max_value = float('-inf')

            for record in history:
                try:
                    date_str = record.get('date', '')
                    value = record.get('total_value', 0) or 0

                    if date_str:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        timestamp = date.timestamp() * 1000
                        series.append(timestamp, value)
                        min_value = min(min_value, value)
                        max_value = max(max_value, value)
                except:
                    continue

            if series.count() > 0:
                self.growth_chart.addSeries(series)

                axis_x = QDateTimeAxis()
                axis_x.setFormat("MMM yyyy")
                self.growth_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
                series.attachAxis(axis_x)

                axis_y = QValueAxis()
                axis_y.setTitleText("Value ($)")
                if min_value != float('inf'):
                    padding = (max_value - min_value) * 0.1 if max_value != min_value else 1000
                    axis_y.setRange(min_value - padding, max_value + padding)
                self.growth_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
                series.attachAxis(axis_y)

        except Exception as e:
            print(f"Error updating growth chart: {e}")

    def update_allocation_chart(self):
        """Update the allocation pie chart - can show all categories or subcategory breakdown"""
        try:
            self.allocation_chart.removeAllSeries()

            selected_category = self.pie_category_filter.currentText()

            if selected_category == "All Categories":
                # Show breakdown by category
                category_totals = {}
                for asset in self.assets_list:
                    category = asset.get('category', 'Other')
                    value = asset.get('value', 0) or 0
                    if value > 0:
                        category_totals[category] = category_totals.get(category, 0) + value

                if not category_totals:
                    self.allocation_chart.setTitle("No Assets to Display")
                    return

                series = QPieSeries()
                total_value = sum(category_totals.values())

                for category, total in sorted(category_totals.items(), key=lambda x: -x[1]):
                    percentage = (total / total_value * 100) if total_value > 0 else 0
                    slice = series.append(f"{category}", total)
                    slice.setLabel(f"{category}\n${total:,.0f} ({percentage:.1f}%)")
                    if category in self.categories:
                        slice.setColor(QColor(self.categories[category].get('color', '#9E9E9E')))
                    # Make larger slices explode slightly for visibility
                    if percentage > 20:
                        slice.setExploded(True)
                        slice.setExplodeDistanceFactor(0.05)

                series.setLabelsVisible(True)
                series.setLabelsPosition(QPieSeries.LabelPosition.LabelOutside)
                self.allocation_chart.addSeries(series)
                self.allocation_chart.setTitle(f"Asset Allocation by Category (Total: ${total_value:,.0f})")

            else:
                # Show breakdown by subcategory within selected category
                subcategory_totals = {}
                for asset in self.assets_list:
                    if asset.get('category') == selected_category:
                        subcategory = asset.get('subcategory', 'Other')
                        asset_name = asset.get('asset_name', 'Unknown')
                        value = asset.get('value', 0) or 0
                        if value > 0:
                            # Use asset name for more detail
                            key = f"{subcategory}: {asset_name}"
                            subcategory_totals[key] = subcategory_totals.get(key, 0) + value

                if not subcategory_totals:
                    self.allocation_chart.setTitle(f"No {selected_category} Assets")
                    return

                series = QPieSeries()
                total_value = sum(subcategory_totals.values())

                # Generate colors for subcategories
                base_color = QColor(self.categories.get(selected_category, {}).get('color', '#9E9E9E'))
                colors = self._generate_color_palette(base_color, len(subcategory_totals))

                for i, (name, total) in enumerate(sorted(subcategory_totals.items(), key=lambda x: -x[1])):
                    percentage = (total / total_value * 100) if total_value > 0 else 0
                    slice = series.append(name, total)
                    slice.setLabel(f"{name}\n${total:,.0f} ({percentage:.1f}%)")
                    slice.setColor(colors[i])
                    if percentage > 25:
                        slice.setExploded(True)
                        slice.setExplodeDistanceFactor(0.05)

                series.setLabelsVisible(True)
                series.setLabelsPosition(QPieSeries.LabelPosition.LabelOutside)
                self.allocation_chart.addSeries(series)
                self.allocation_chart.setTitle(f"{selected_category} Breakdown (Total: ${total_value:,.0f})")

        except Exception as e:
            print(f"Error updating allocation chart: {e}")

    def _generate_color_palette(self, base_color, count):
        """Generate a palette of colors based on a base color"""
        colors = []
        h, s, l, a = base_color.getHslF()

        for i in range(count):
            # Vary the lightness and saturation
            new_l = max(0.3, min(0.8, l + (i - count/2) * 0.1))
            new_s = max(0.3, min(1.0, s - i * 0.05))
            color = QColor()
            color.setHslF(h, new_s, new_l, a)
            colors.append(color)

        return colors

    def export_template(self):
        """Export a template CSV with all assets (values blank) for easy updating"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Template",
                f"asset_update_template_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if file_path:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Include update_date column for when the asset is being updated
                    writer.writerow(['asset_name', 'person', 'category', 'subcategory',
                                   'value', 'update_date', 'liquidity', 'notes'])

                    # Sort assets by category then name for easier editing
                    sorted_assets = sorted(self.assets_list,
                                          key=lambda x: (x.get('category', ''), x.get('asset_name', '')))

                    for asset in sorted_assets:
                        writer.writerow([
                            asset.get('asset_name', ''),
                            asset.get('person', ''),
                            asset.get('category', ''),
                            asset.get('subcategory', ''),
                            '',  # Value left blank for user to fill in
                            datetime.now().strftime('%Y-%m-%d'),  # Default to today
                            asset.get('liquidity', 5),
                            asset.get('notes', '')
                        ])

                QMessageBox.information(self, "Template Exported",
                    f"Template exported to:\n{file_path}\n\n"
                    f"Instructions:\n"
                    f"1. Open the CSV file\n"
                    f"2. Fill in the 'value' column with current values\n"
                    f"3. Update 'update_date' if needed\n"
                    f"4. Save and use 'Import CSV' to update\n\n"
                    f"Assets in template: {len(self.assets_list)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export template: {str(e)}")

    def export_csv(self):
        """Export current assets to CSV"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Assets",
                f"assets_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )

            if file_path:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['asset_name', 'person', 'category', 'subcategory',
                                   'value', 'liquidity', 'notes'])
                    for asset in self.assets_list:
                        writer.writerow([
                            asset.get('asset_name', ''),
                            asset.get('person', ''),
                            asset.get('category', ''),
                            asset.get('subcategory', ''),
                            asset.get('value', 0),
                            asset.get('liquidity', 5),
                            asset.get('notes', '')
                        ])
                QMessageBox.information(self, "Success", f"Exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def import_csv(self):
        """Import assets from CSV - updates values for existing assets, adds new ones"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Import Assets", "", "CSV Files (*.csv)"
            )

            if file_path:
                imported = 0
                updated = 0
                skipped = 0
                errors = 0

                with open(file_path, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)

                    for row in reader:
                        try:
                            asset_name = row.get('asset_name', '').strip()
                            if not asset_name:
                                errors += 1
                                continue

                            # Get value - skip if empty (template not filled in)
                            value_str = row.get('value', '').strip()
                            if not value_str:
                                skipped += 1
                                continue

                            value = float(value_str.replace(',', '').replace('$', ''))

                            # Check if asset exists
                            existing = next((a for a in self.assets_list if a.get('asset_name') == asset_name), None)

                            if existing:
                                # Update existing asset's value
                                self.db.update_asset_value(existing['id'], value)
                                updated += 1
                            else:
                                # Add new asset
                                self.db.upsert_asset(
                                    asset_name=asset_name,
                                    person=row.get('person', 'Joint').strip(),
                                    category=row.get('category', 'Other').strip(),
                                    subcategory=row.get('subcategory', '').strip(),
                                    value=value,
                                    liquidity=int(row.get('liquidity', 5) or 5),
                                    notes=row.get('notes', '').strip()
                                )
                                imported += 1
                        except Exception as e:
                            errors += 1
                            print(f"Error importing row: {e}")

                self.load_assets()
                self.refresh_display()

                message = f"Import Complete!\n\n"
                message += f"✓ New assets added: {imported}\n"
                message += f"✓ Existing assets updated: {updated}\n"
                if skipped > 0:
                    message += f"○ Skipped (empty value): {skipped}\n"
                if errors > 0:
                    message += f"✗ Errors: {errors}"

                QMessageBox.information(self, "Import Complete", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")

