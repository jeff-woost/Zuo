"""
Savings Goals Tab
Manage and allocate funds to savings goals with monthly tracking
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QDateEdit, QTabWidget, QSpinBox,
    QHeaderView, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QCheckBox, QScrollArea, QFrame,
    QProgressBar, QFormLayout
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, date
import json
import csv
from src.database.db_manager import DatabaseManager
from src.database.models import SavingsGoalModel, SavingsAllocationModel
from src.gui.utils.goal_edit_dialog import GoalEditDialog

class SavingsTab(QWidget):
    """Tab for managing savings goals and fund allocation"""

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Savings Goals Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create main content with tabs - renamed and reorganized
        self.content_tabs = QTabWidget()

        # Goal Setting Tab - Where users create and manage goals
        self.goal_setting_tab = self.create_goal_setting_tab()
        self.content_tabs.addTab(self.goal_setting_tab, "🎯 Goal Setting")

        # Goal Allocation Tab - Where users allocate monthly leftover funds
        self.allocation_tab = self.create_goal_allocation_tab()
        self.content_tabs.addTab(self.allocation_tab, "💰 Goal Allocation")

        # Progress Tracking Tab - View progress across all goals
        self.progress_tab = self.create_progress_tracking_tab()
        self.content_tabs.addTab(self.progress_tab, "📈 Progress Tracking")

        # Achievement History Tab - Completed goals
        self.history_tab = self.create_achievement_history_tab()
        self.content_tabs.addTab(self.history_tab, "🏆 Achievement History")

        layout.addWidget(self.content_tabs)
        self.setLayout(layout)

    def create_goal_setting_tab(self):
        """Create the Goal Setting tab where users create and manage savings goals"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header with instructions
        header_label = QLabel("Goal Setting")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c5530; margin-bottom: 10px;")
        layout.addWidget(header_label)

        instructions = QLabel(
            "Create and manage your savings goals here. Set target amounts, priorities, and deadlines. "
            "Once goals are created, you can allocate monthly leftover funds to them in the Goal Allocation tab."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 20px; font-size: 12px; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)

        # Goals table with management functionality
        goals_table_group = QGroupBox("📋 Your Savings Goals")
        goals_table_layout = QVBoxLayout()

        # Control buttons for goal management
        control_layout = QHBoxLayout()

        # Add new goal button
        add_goal_btn = QPushButton("➕ Create New Goal")
        add_goal_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_goal_btn.clicked.connect(self.create_new_goal)
        control_layout.addWidget(add_goal_btn)

        # Refresh goals button
        refresh_goals_btn = QPushButton("🔄 Refresh Goals")
        refresh_goals_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_goals_btn.clicked.connect(self.refresh_goals_data)
        control_layout.addWidget(refresh_goals_btn)

        control_layout.addStretch()
        goals_table_layout.addLayout(control_layout)

        # Goals table
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(8)
        self.goals_table.setHorizontalHeaderLabels([
            "Goal Name", "Target Amount", "Current Amount", "Progress %",
            "Priority", "Target Date", "Status", "Actions"
        ])

        # Set column widths for better visibility
        header = self.goals_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Goal Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Target Amount
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Current Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Progress
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Priority
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Target Date
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)    # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)    # Actions

        self.goals_table.setColumnWidth(1, 120)  # Target Amount
        self.goals_table.setColumnWidth(2, 120)  # Current Amount
        self.goals_table.setColumnWidth(3, 80)   # Progress
        self.goals_table.setColumnWidth(4, 70)   # Priority
        self.goals_table.setColumnWidth(5, 100)  # Target Date
        self.goals_table.setColumnWidth(6, 80)   # Status
        self.goals_table.setColumnWidth(7, 100)  # Actions

        self.goals_table.setAlternatingRowColors(True)
        self.goals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        goals_table_layout.addWidget(self.goals_table)
        goals_table_group.setLayout(goals_table_layout)
        layout.addWidget(goals_table_group)

        return widget

    def create_goal_allocation_tab(self):
        """Create the Goal Allocation tab where users allocate monthly leftover funds"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header with instructions
        header_label = QLabel("Goal Allocation")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c5530; margin-bottom: 10px;")
        layout.addWidget(header_label)

        instructions = QLabel(
            "Allocate your monthly leftover funds (Income - Expenses) to your savings goals. "
            "Select a month to see available funds and allocate them to your existing goals by priority."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 20px; font-size: 12px; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)

        # Month selector for allocation
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Allocation Month:"))

        self.allocation_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.allocation_month_combo.addItems(months)
        self.allocation_month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        self.allocation_month_combo.currentIndexChanged.connect(self.refresh_allocation_data)
        month_layout.addWidget(self.allocation_month_combo)

        self.allocation_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 3):
            self.allocation_year_combo.addItem(str(year))
        self.allocation_year_combo.setCurrentText(str(current_year))
        self.allocation_year_combo.currentTextChanged.connect(self.refresh_allocation_data)
        month_layout.addWidget(self.allocation_year_combo)

        refresh_allocation_btn = QPushButton("🔄 Refresh Data")
        refresh_allocation_btn.clicked.connect(self.refresh_allocation_data)
        month_layout.addWidget(refresh_allocation_btn)

        month_layout.addStretch()
        layout.addLayout(month_layout)

        # Available funds summary - shows leftover from Income - Expenses
        available_group = QGroupBox("💰 Available Funds for Allocation")
        available_layout = QGridLayout()

        available_layout.addWidget(QLabel("Monthly Income:"), 0, 0)
        self.allocation_income_label = QLabel("$0.00")
        self.allocation_income_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        available_layout.addWidget(self.allocation_income_label, 0, 1)

        available_layout.addWidget(QLabel("Monthly Expenses:"), 1, 0)
        self.allocation_expenses_label = QLabel("$0.00")
        self.allocation_expenses_label.setStyleSheet("color: #f44336; font-weight: bold;")
        available_layout.addWidget(self.allocation_expenses_label, 1, 1)

        available_layout.addWidget(QLabel("Previous Allocations:"), 2, 0)
        self.previous_allocations_label = QLabel("$0.00")
        self.previous_allocations_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        available_layout.addWidget(self.previous_allocations_label, 2, 1)

        available_layout.addWidget(QLabel("Available for Goals:"), 3, 0)
        self.allocation_remaining_label = QLabel("$0.00")
        self.allocation_remaining_label.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 16px;")
        available_layout.addWidget(self.allocation_remaining_label, 3, 1)

        available_group.setLayout(available_layout)
        layout.addWidget(available_group)

        # Allocation form - only for allocating to existing goals
        allocation_form_group = QGroupBox("💵 Allocate Funds to Existing Goals")
        allocation_form_layout = QFormLayout()

        self.allocation_goal_combo = QComboBox()
        self.allocation_goal_combo.currentIndexChanged.connect(self.update_goal_info)
        allocation_form_layout.addRow("Select Goal:", self.allocation_goal_combo)

        # Show selected goal info
        self.selected_goal_info = QLabel("Select a goal to see details")
        self.selected_goal_info.setStyleSheet("color: #666; font-style: italic;")
        allocation_form_layout.addRow("Goal Info:", self.selected_goal_info)

        self.allocation_amount = QLineEdit()
        self.allocation_amount.setPlaceholderText("0.00")
        allocation_form_layout.addRow("Amount to Allocate ($):", self.allocation_amount)

        allocate_btn = QPushButton("💰 Allocate Funds")
        allocate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        allocate_btn.clicked.connect(self.allocate_funds)
        allocation_form_layout.addRow(allocate_btn)

        allocation_form_group.setLayout(allocation_form_layout)
        layout.addWidget(allocation_form_group)

        # Monthly allocations table
        allocations_group = QGroupBox("📈 This Month's Allocations")
        allocations_layout = QVBoxLayout()

        self.allocations_table = QTableWidget()
        self.allocations_table.setColumnCount(4)
        self.allocations_table.setHorizontalHeaderLabels([
            "Date", "Goal Name", "Amount", "Remaining Available"
        ])
        self.allocations_table.setAlternatingRowColors(True)

        allocations_layout.addWidget(self.allocations_table)
        allocations_group.setLayout(allocations_layout)
        layout.addWidget(allocations_group)

        return widget

    def create_progress_tracking_tab(self):
        """Create the progress tracking tab with visual progress bars"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Month/Year selector for progress view
        progress_date_layout = QHBoxLayout()
        progress_date_layout.addWidget(QLabel("View Progress for:"))

        self.progress_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.progress_month_combo.addItems(months)
        self.progress_month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        progress_date_layout.addWidget(self.progress_month_combo)

        self.progress_year_combo = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 6):
            self.progress_year_combo.addItem(str(year))
        self.progress_year_combo.setCurrentText(str(current_year))
        progress_date_layout.addWidget(self.progress_year_combo)

        refresh_progress_btn = QPushButton("🔄 Update Progress")
        refresh_progress_btn.clicked.connect(self.refresh_progress_data)
        progress_date_layout.addWidget(refresh_progress_btn)

        progress_date_layout.addStretch()
        layout.addLayout(progress_date_layout)

        # Scrollable area for progress bars
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.progress_widget = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_widget)

        scroll_area.setWidget(self.progress_widget)
        layout.addWidget(scroll_area)

        return widget

    def create_achievement_history_tab(self):
        """Create the achievement history tab for completed goals"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Feature 5: Add status filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Status:"))
        
        self.history_status_filter = QComboBox()
        self.history_status_filter.addItems(["All", "Completed", "Retired"])
        self.history_status_filter.currentTextChanged.connect(self.refresh_achievement_history)
        filter_layout.addWidget(self.history_status_filter)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)

        # Achievement summary
        achievement_group = QGroupBox("🏆 Achievements Summary")
        achievement_layout = QGridLayout()

        self.completed_goals_label = QLabel("0")
        self.completed_goals_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        achievement_layout.addWidget(QLabel("Completed Goals:"), 0, 0)
        achievement_layout.addWidget(self.completed_goals_label, 0, 1)

        self.total_saved_label = QLabel("$0.00")
        self.total_saved_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        achievement_layout.addWidget(QLabel("Total Amount Saved:"), 1, 0)
        achievement_layout.addWidget(self.total_saved_label, 1, 1)

        achievement_group.setLayout(achievement_layout)
        layout.addWidget(achievement_group)

        # History table with enhanced information
        history_group = QGroupBox("📚 Achievement History")
        history_layout = QVBoxLayout()

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)  # Feature 5: Added Status column
        self.history_table.setHorizontalHeaderLabels([
            "Goal Name", "Target Amount", "Final Amount", "Completion Date",
            "Duration (Days)", "Monthly Avg", "Status"
        ])

        # Set column properties
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.history_table.setColumnWidth(i, 120)

        self.history_table.setAlternatingRowColors(True)
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        return widget

    def add_goal(self):
        """Add a new savings goal"""
        try:
            name = self.goal_name.text().strip()
            target_text = self.goal_target.text().strip()
            priority = self.goal_priority.value()
            target_date = self.goal_date.date().toString("yyyy-MM-dd")
            notes = self.goal_notes.text().strip()

            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a goal name")
                return

            if not target_text:
                QMessageBox.warning(self, "Warning", "Please enter a target amount")
                return

            try:
                target_amount = float(target_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for target amount")
                return

            # Add to database
            self.db.add_savings_goal(name, target_amount, target_date, priority, notes)

            # Clear form
            self.clear_goal_form()

            # Refresh display
            self.refresh_data()

            QMessageBox.information(self, "Success", "Savings goal added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add savings goal: {str(e)}")

    def clear_goal_form(self):
        """Clear the goal form"""
        self.goal_name.clear()
        self.goal_target.clear()
        self.goal_priority.setValue(5)
        self.goal_date.setDate(QDate.currentDate().addMonths(12))
        self.goal_notes.clear()

    def calculate_available_funds(self):
        """Calculate available funds for allocation"""
        try:
            # Get current month data
            current_date = QDate.currentDate()
            year = current_date.year()
            month = current_date.month()

            # Get monthly summary
            summary = self.db.get_monthly_summary(year, month)

            total_income = sum(summary['income'].values())
            total_expenses = sum(summary['expenses'].values())
            available = total_income - total_expenses

            # Update summary cards
            self.available_summary.value_label.setText(f"${available:,.2f}")

            # Calculate remaining after existing allocations
            # This would need to be implemented based on allocation tracking
            remaining = available  # Simplified for now
            self.remaining_summary.value_label.setText(f"${remaining:,.2f}")

        except Exception as e:
            print(f"Error calculating available funds: {e}")

    def auto_allocate_funds(self):
        """Auto-allocate available funds by priority"""
        QMessageBox.information(self, "Auto-Allocate", "Auto-allocation feature coming soon!")

    def refresh_data(self):
        """Refresh all data in the tab"""
        try:
            self.refresh_financial_summary()
            self.load_goals_table()
            self.load_goal_combos()
            self.refresh_allocation_data()
            self.refresh_progress_data()
            self.refresh_achievement_history()

        except Exception as e:
            print(f"Error refreshing savings data: {e}")

    def load_goals_table(self):
        """Load savings goals into the table with edit buttons"""
        try:
            goals = self.db.get_savings_goals()
            self.goals_table.setRowCount(len(goals))

            for row, goal in enumerate(goals):
                # Goal name
                self.goals_table.setItem(row, 0, QTableWidgetItem(goal['goal_name']))

                # Target amount
                target_item = QTableWidgetItem(f"${goal['target_amount']:,.2f}")
                target_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.goals_table.setItem(row, 1, target_item)

                # Current amount
                current_item = QTableWidgetItem(f"${goal['current_amount']:,.2f}")
                current_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.goals_table.setItem(row, 2, current_item)

                # Progress percentage
                if goal['target_amount'] > 0:
                    progress = (goal['current_amount'] / goal['target_amount']) * 100
                else:
                    progress = 0

                progress_item = QTableWidgetItem(f"{progress:.1f}%")
                progress_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.goals_table.setItem(row, 3, progress_item)

                # Priority
                priority_item = QTableWidgetItem(str(goal['priority']))
                priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.goals_table.setItem(row, 4, priority_item)

                # Target date
                target_date = goal.get('target_date', '')
                if target_date:
                    try:
                        date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    except:
                        formatted_date = target_date
                else:
                    formatted_date = "No date set"

                self.goals_table.setItem(row, 5, QTableWidgetItem(formatted_date))

                # Status
                status = "Completed" if goal.get('is_completed', False) else "Active"
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.goals_table.setItem(row, 6, status_item)

                # Actions - Edit and Retire buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️ Edit")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 4px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, g=goal: self.edit_goal(g))
                actions_layout.addWidget(edit_btn)
                
                # Feature 5: Add Retire button
                if not goal.get('is_completed', False):
                    retire_btn = QPushButton("🚫 Retire")
                    retire_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #ff9800;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 4px;
                            border: none;
                        }
                        QPushButton:hover {
                            background-color: #f57c00;
                        }
                    """)
                    retire_btn.clicked.connect(lambda checked, g=goal: self.retire_goal(g))
                    actions_layout.addWidget(retire_btn)
                
                self.goals_table.setCellWidget(row, 7, actions_widget)

        except Exception as e:
            print(f"Error loading goals table: {e}")

    def load_goal_combos(self):
        """Load goals into combo boxes for allocation"""
        try:
            goals = self.db.get_savings_goals()

            # Clear and populate allocation combo
            self.allocation_goal_combo.clear()
            for goal in goals:
                if not goal.get('is_completed', False):  # Only active goals
                    self.allocation_goal_combo.addItem(goal['goal_name'], goal['id'])

        except Exception as e:
            print(f"Error loading goal combos: {e}")

    def allocate_funds(self):
        """Allocate funds to the selected goal"""
        try:
            if self.allocation_goal_combo.currentIndex() == -1:
                QMessageBox.warning(self, "Warning", "Please select a goal to allocate funds to.")
                return

            amount_text = self.allocation_amount.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Warning", "Please enter an amount to allocate.")
                return

            try:
                amount = float(amount_text.replace(',', '').replace('$', ''))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid amount.")
                return

            if amount <= 0:
                QMessageBox.warning(self, "Warning", "Amount must be greater than 0.")
                return

            # Get selected goal
            goal_id = self.allocation_goal_combo.currentData()
            current_date = QDate.currentDate().toString("yyyy-MM-dd")

            # Allocate to goal
            self.db.allocate_to_goal(goal_id, amount, current_date)

            # Clear form
            self.allocation_amount.clear()

            # Refresh data
            self.refresh_allocation_data()
            self.refresh_data()

            QMessageBox.information(self, "Success", f"${amount:,.2f} allocated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to allocate funds: {str(e)}")

    def refresh_allocation_data(self):
        """Refresh the data in the goal allocation tab"""
        try:
            month = self.allocation_month_combo.currentIndex() + 1
            year = int(self.allocation_year_combo.currentText())

            # Get allocation data from database
            allocations = self.db.get_monthly_goal_allocations(year, month)

            # Update available funds labels
            summary = self.db.get_monthly_summary(year, month)
            total_income = sum(summary['income'].values())
            total_expenses = sum(summary['expenses'].values())
            available_funds = total_income - total_expenses

            self.allocation_income_label.setText(f"${total_income:,.2f}")
            self.allocation_expenses_label.setText(f"${total_expenses:,.2f}")
            self.allocation_remaining_label.setText(f"${available_funds:,.2f}")

            # Load allocations into table
            self.allocations_table.setRowCount(len(allocations))

            for row, allocation in enumerate(allocations):
                # Date
                date_item = QTableWidgetItem(allocation['date'])
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.allocations_table.setItem(row, 0, date_item)

                # Goal name
                self.allocations_table.setItem(row, 1, QTableWidgetItem(allocation['goal_name']))

                # Amount
                amount_item = QTableWidgetItem(f"${allocation['amount']:,.2f}")
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.allocations_table.setItem(row, 2, amount_item)

                # Running total for this goal
                goal_total = sum(a['amount'] for a in allocations
                               if a['goal_name'] == allocation['goal_name']
                               and allocations.index(a) <= row)
                running_total_item = QTableWidgetItem(f"${goal_total:,.2f}")
                running_total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.allocations_table.setItem(row, 3, running_total_item)

        except Exception as e:
            print(f"Error refreshing allocation data: {e}")

    def refresh_progress_data(self):
        """Refresh the progress tracking data with visual progress bars"""
        try:
            # Clear existing progress bars
            for i in reversed(range(self.progress_layout.count())):
                widget = self.progress_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

            # Get goals data
            goals = self.db.get_savings_goals()

            if not goals:
                no_goals_label = QLabel("No savings goals found. Add some goals in the Goals Allocation tab!")
                no_goals_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                no_goals_label.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
                self.progress_layout.addWidget(no_goals_label)
                return

            for goal in goals:
                # Create progress card for each goal
                goal_frame = QFrame()
                goal_frame.setFrameStyle(QFrame.Shape.Box)
                goal_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 5px;
                        background-color: #f9f9f9;
                    }
                """)

                goal_layout = QVBoxLayout(goal_frame)

                # Goal name and amount info
                goal_info_layout = QHBoxLayout()

                goal_name_label = QLabel(goal['goal_name'])
                goal_name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                goal_info_layout.addWidget(goal_name_label)

                goal_info_layout.addStretch()

                amount_info = QLabel(f"${goal['current_amount']:,.2f} / ${goal['target_amount']:,.2f}")
                amount_info.setStyleSheet("color: #666;")
                goal_info_layout.addWidget(amount_info)

                goal_layout.addLayout(goal_info_layout)

                # Progress bar
                progress_bar = QProgressBar()
                progress_bar.setTextVisible(True)
                progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #ddd;
                        border-radius: 5px;
                        text-align: center;
                        height: 25px;
                    }
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                        border-radius: 3px;
                    }
                """)

                # Calculate progress
                if goal['target_amount'] > 0:
                    progress = (goal['current_amount'] / goal['target_amount']) * 100
                    progress = min(progress, 100)  # Cap at 100%
                else:
                    progress = 0

                progress_bar.setValue(int(progress))
                progress_bar.setFormat(f"{progress:.1f}%")

                goal_layout.addWidget(progress_bar)

                # Status and target date
                status_layout = QHBoxLayout()

                status = "✅ Completed" if goal.get('is_completed', False) else "🎯 In Progress"
                status_label = QLabel(status)
                status_layout.addWidget(status_label)

                status_layout.addStretch()

                if goal.get('target_date'):
                    target_date_label = QLabel(f"Target: {goal['target_date']}")
                    target_date_label.setStyleSheet("color: #666; font-size: 10px;")
                    status_layout.addWidget(target_date_label)

                goal_layout.addLayout(status_layout)

                self.progress_layout.addWidget(goal_frame)

        except Exception as e:
            print(f"Error refreshing progress data: {e}")

    def refresh_achievement_history(self):
        """Feature 5: Refresh the achievement history tab with status filter"""
        try:
            # Get filter selection
            filter_text = self.history_status_filter.currentText() if hasattr(self, 'history_status_filter') else "All"
            
            # Map filter text to status
            if filter_text == "Completed":
                status_filter = "completed"
            elif filter_text == "Retired":
                status_filter = "retired"
            else:
                status_filter = None  # All
            
            # Get completed/retired goals based on filter
            if status_filter:
                completed_goals = SavingsGoalModel.get_by_status(self.db, status_filter)
            else:
                completed_goals = self.db.get_completed_goals()

            # Update summary
            total_completed = len(completed_goals)
            total_saved = sum(goal['current_amount'] for goal in completed_goals)

            self.completed_goals_label.setText(str(total_completed))
            self.total_saved_label.setText(f"${total_saved:,.2f}")

            # Load history table
            self.history_table.setRowCount(len(completed_goals))

            for row, goal in enumerate(completed_goals):
                # Goal name
                self.history_table.setItem(row, 0, QTableWidgetItem(goal['goal_name']))

                # Target amount
                target_item = QTableWidgetItem(f"${goal['target_amount']:,.2f}")
                target_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.history_table.setItem(row, 1, target_item)

                # Final amount
                final_item = QTableWidgetItem(f"${goal['current_amount']:,.2f}")
                final_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.history_table.setItem(row, 2, final_item)

                # Completion date
                completion_date = goal.get('completion_date', '')
                if completion_date:
                    try:
                        date_obj = datetime.strptime(completion_date, '%Y-%m-%d').date()
                        formatted_date = date_obj.strftime('%m/%d/%Y')
                    except:
                        formatted_date = completion_date
                else:
                    formatted_date = "Unknown"

                self.history_table.setItem(row, 3, QTableWidgetItem(formatted_date))

                # Duration calculation
                if goal.get('created_at') and goal.get('completion_date'):
                    try:
                        created = datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S').date()
                        completed = datetime.strptime(goal['completion_date'], '%Y-%m-%d').date()
                        duration = (completed - created).days
                        duration_item = QTableWidgetItem(str(duration))
                    except:
                        duration_item = QTableWidgetItem("Unknown")
                else:
                    duration_item = QTableWidgetItem("Unknown")

                duration_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setItem(row, 4, duration_item)

                # Monthly average
                if goal.get('created_at') and goal.get('completion_date'):
                    try:
                        created = datetime.strptime(goal['created_at'], '%Y-%m-%d %H:%M:%S').date()
                        completed = datetime.strptime(goal['completion_date'], '%Y-%m-%d').date()
                        months = max(1, (completed - created).days / 30.44)  # Average days per month
                        monthly_avg = goal['current_amount'] / months
                        monthly_avg_item = QTableWidgetItem(f"${monthly_avg:,.2f}")
                    except:
                        monthly_avg_item = QTableWidgetItem("$0.00")
                else:
                    monthly_avg_item = QTableWidgetItem("$0.00")

                monthly_avg_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.history_table.setItem(row, 5, monthly_avg_item)
                
                # Feature 5: Add Status column
                status = goal.get('status', 'completed')
                status_display = status.title()
                status_item = QTableWidgetItem(status_display)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Color code based on status
                if status == 'completed':
                    status_item.setForeground(QColor(76, 175, 80))  # Green
                elif status == 'retired':
                    status_item.setForeground(QColor(255, 152, 0))  # Orange
                    
                self.history_table.setItem(row, 6, status_item)

        except Exception as e:
            print(f"Error refreshing achievement history: {e}")

    def add_new_goal(self):
        """Open the dialog to add a new goal"""
        dialog = GoalEditDialog(self, None, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            self.load_goal_combos()

    def edit_goal(self, goal_data):
        """Open the dialog to edit an existing goal"""
        dialog = GoalEditDialog(self, goal_data, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            self.load_goal_combos()
    
    def retire_goal(self, goal_data):
        """
        Feature 5: Retire a savings goal (mark as retired/abandoned)
        """
        try:
            # Ask user for reason
            from PyQt6.QtWidgets import QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Retire Goal")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)
            
            label = QLabel(f"Are you sure you want to retire the goal '{goal_data['goal_name']}'?\n\n"
                          "Choose the retirement status:")
            label.setWordWrap(True)
            layout.addWidget(label)
            
            # Status selection
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("Status:"))
            status_combo = QComboBox()
            status_combo.addItems(["Retired (Abandoned)", "Completed (Achieved)"])
            status_layout.addWidget(status_combo)
            layout.addLayout(status_layout)
            
            # Buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Determine status
                status = "retired" if "Retired" in status_combo.currentText() else "completed"
                
                # Update goal status
                SavingsGoalModel.retire_goal(self.db, goal_data['id'], status)
                
                QMessageBox.information(
                    self, "Success",
                    f"Goal '{goal_data['goal_name']}' has been retired successfully!"
                )
                
                # Refresh data
                self.refresh_data()
                self.load_goal_combos()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to retire goal: {str(e)}")

    def refresh_financial_summary(self):
        """Refresh the financial summary data"""
        try:
            month = self.summary_month_combo.currentIndex() + 1
            year = int(self.summary_year_combo.currentText())

            # Get monthly summary
            summary = self.db.get_monthly_summary(year, month)

            # Calculate totals
            total_income = sum(summary['income'].values())
            jeff_expenses = summary['expenses'].get('Jeff', 0)
            vanessa_expenses = summary['expenses'].get('Vanessa', 0)
            total_expenses = jeff_expenses + vanessa_expenses
            available_savings = total_income - total_expenses

            # Update labels
            self.total_income_label.setText(f"${total_income:,.2f}")
            self.jeff_expenses_label.setText(f"${jeff_expenses:,.2f}")
            self.vanessa_expenses_label.setText(f"${vanessa_expenses:,.2f}")
            self.total_expenses_label.setText(f"${total_expenses:,.2f}")
            self.available_savings_label.setText(f"${available_savings:,.2f}")

        except Exception as e:
            print(f"Error refreshing financial summary: {e}")
            # Set default values on error
            self.total_income_label.setText("$0.00")
            self.jeff_expenses_label.setText("$0.00")
            self.vanessa_expenses_label.setText("$0.00")
            self.total_expenses_label.setText("$0.00")
            self.available_savings_label.setText("$0.00")

    def create_new_goal(self):
        """Open the dialog to create a new goal in the Goal Setting tab"""
        dialog = GoalEditDialog(self, None, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_goals_data()
            self.load_goal_combos()

    def refresh_goals_data(self):
        """Refresh the goals data in the Goal Setting tab"""
        try:
            self.load_goals_table()
            self.load_goal_combos()
        except Exception as e:
            print(f"Error refreshing goals data: {e}")

    def update_goal_info(self):
        """Update the goal info display when a goal is selected for allocation"""
        try:
            if self.allocation_goal_combo.currentIndex() == -1:
                self.selected_goal_info.setText("Select a goal to see details")
                return

            goal_id = self.allocation_goal_combo.currentData()
            if not goal_id:
                self.selected_goal_info.setText("Select a goal to see details")
                return

            # Get goal details
            goals = self.db.get_savings_goals()
            selected_goal = None
            for goal in goals:
                if goal['id'] == goal_id:
                    selected_goal = goal
                    break

            if selected_goal:
                current_amount = selected_goal['current_amount']
                target_amount = selected_goal['target_amount']
                progress = (current_amount / target_amount * 100) if target_amount > 0 else 0
                remaining = target_amount - current_amount

                info_text = (
                    f"Target: ${target_amount:,.2f} | "
                    f"Current: ${current_amount:,.2f} | "
                    f"Progress: {progress:.1f}% | "
                    f"Remaining: ${remaining:,.2f}"
                )
                self.selected_goal_info.setText(info_text)
                self.selected_goal_info.setStyleSheet("color: #333; font-weight: bold;")
            else:
                self.selected_goal_info.setText("Goal details not found")
                self.selected_goal_info.setStyleSheet("color: #f44336; font-style: italic;")

        except Exception as e:
            print(f"Error updating goal info: {e}")
            self.selected_goal_info.setText("Error loading goal details")
            self.selected_goal_info.setStyleSheet("color: #f44336; font-style: italic;")

