"""
Goal Edit Dialog
Dialog for editing savings goals with all details
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDateEdit, QTextEdit, QPushButton, QDialogButtonBox,
    QFormLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime

class GoalEditDialog(QDialog):
    """Dialog for editing savings goal details"""

    def __init__(self, parent=None, goal_data=None, db_manager=None):
        super().__init__(parent)
        self.goal_data = goal_data
        self.db = db_manager
        self.is_new_goal = goal_data is None
        self.init_ui()
        if goal_data:
            self.populate_fields()

    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Edit Savings Goal" if not self.is_new_goal else "Add New Savings Goal")
        self.setModal(True)
        self.resize(450, 500)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Savings Goal Details")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2196F3; margin-bottom: 20px;")
        layout.addWidget(title)

        # Form layout
        form_layout = QFormLayout()

        # Goal name
        self.goal_name = QLineEdit()
        self.goal_name.setPlaceholderText("e.g., Emergency Fund, Vacation, New Car")
        form_layout.addRow("Goal Name:", self.goal_name)

        # Target amount
        self.target_amount = QLineEdit()
        self.target_amount.setPlaceholderText("10000.00")
        form_layout.addRow("Target Amount ($):", self.target_amount)

        # Initial amount (money already allocated from other sources)
        self.initial_amount = QLineEdit()
        self.initial_amount.setPlaceholderText("0.00")
        self.initial_amount.setToolTip("Money already allocated to this goal from other sources")
        form_layout.addRow("Initial Amount ($):", self.initial_amount)

        # Priority
        self.priority = QSpinBox()
        self.priority.setRange(1, 10)
        self.priority.setValue(5)
        self.priority.setToolTip("1 = Highest Priority, 10 = Lowest Priority")
        form_layout.addRow("Priority (1-10):", self.priority)

        # Target date
        self.target_date = QDateEdit()
        self.target_date.setDate(QDate.currentDate().addMonths(12))
        self.target_date.setCalendarPopup(True)
        form_layout.addRow("Target Date:", self.target_date)

        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Optional notes about this goal...")
        self.notes.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes)

        # Completion status (only for existing goals)
        if not self.is_new_goal:
            self.is_completed = QCheckBox("Mark as Completed")
            self.is_completed.setToolTip("Check this box to mark the goal as completed")
            form_layout.addRow("Status:", self.is_completed)

        layout.addLayout(form_layout)

        # Progress info (only for existing goals)
        if not self.is_new_goal:
            progress_layout = QVBoxLayout()
            progress_label = QLabel("Current Progress")
            progress_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            progress_label.setStyleSheet("color: #333; margin-top: 20px;")
            progress_layout.addWidget(progress_label)

            self.current_amount_label = QLabel("Current Amount: $0.00")
            self.progress_percentage_label = QLabel("Progress: 0%")

            progress_layout.addWidget(self.current_amount_label)
            progress_layout.addWidget(self.progress_percentage_label)

            layout.addLayout(progress_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        # Style buttons
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Save Goal")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        button_box.accepted.connect(self.save_goal)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        # Add delete button for existing goals
        if not self.is_new_goal:
            delete_button = QPushButton("🗑️ Delete Goal")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 6px;
                    border: none;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #f57c00;
                }
            """)
            delete_button.clicked.connect(self.delete_goal)
            layout.addWidget(delete_button)

        self.setLayout(layout)

    def populate_fields(self):
        """Populate the form with existing goal data"""
        if not self.goal_data:
            return

        self.goal_name.setText(self.goal_data.get('goal_name', ''))
        self.target_amount.setText(str(self.goal_data.get('target_amount', 0)))
        self.initial_amount.setText(str(self.goal_data.get('initial_amount', 0)))
        self.priority.setValue(self.goal_data.get('priority', 5))

        # Set target date
        target_date = self.goal_data.get('target_date', '')
        if target_date:
            try:
                date_obj = datetime.strptime(target_date, '%Y-%m-%d').date()
                self.target_date.setDate(QDate(date_obj))
            except ValueError:
                self.target_date.setDate(QDate.currentDate().addMonths(12))

        self.notes.setPlainText(self.goal_data.get('notes', ''))

        # Set completion status
        if hasattr(self, 'is_completed'):
            self.is_completed.setChecked(self.goal_data.get('is_completed', False))

        # Update progress info
        if not self.is_new_goal:
            current_amount = self.goal_data.get('current_amount', 0)
            target_amount = self.goal_data.get('target_amount', 1)
            progress = (current_amount / target_amount * 100) if target_amount > 0 else 0

            self.current_amount_label.setText(f"Current Amount: ${current_amount:,.2f}")
            self.progress_percentage_label.setText(f"Progress: {progress:.1f}%")

    def save_goal(self):
        """Save the goal with proper error handling for UNIQUE constraints"""
        try:
            goal_name = self.goal_name.text().strip()
            target_amount_text = self.target_amount.text().strip()
            initial_amount_text = self.initial_amount.text().strip()
            priority = self.priority.value()
            target_date = self.target_date.date().toString("yyyy-MM-dd")
            notes = self.notes.toPlainText().strip()

            # Validate inputs
            if not goal_name:
                QMessageBox.warning(self, "Warning", "Please enter a goal name")
                return

            if not target_amount_text:
                QMessageBox.warning(self, "Warning", "Please enter a target amount")
                return

            try:
                target_amount = float(target_amount_text.replace(",", "").replace("$", ""))
                initial_amount = float(initial_amount_text.replace(",", "").replace("$", "")) if initial_amount_text else 0.0
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter valid numbers for amounts")
                return

            if target_amount <= 0:
                QMessageBox.warning(self, "Warning", "Target amount must be greater than 0")
                return

            if initial_amount < 0:
                QMessageBox.warning(self, "Warning", "Initial amount cannot be negative")
                return

            # Import the models at the top of the method to avoid circular imports
            from src.database.models import SavingsGoalModel

            if self.is_new_goal:
                # Check if goal name already exists
                existing_goals = self.db.get_savings_goals(include_completed=True)
                existing_names = [goal['goal_name'].lower() for goal in existing_goals]

                if goal_name.lower() in existing_names:
                    QMessageBox.warning(
                        self,
                        "Duplicate Goal Name",
                        f"A goal named '{goal_name}' already exists.\n\nPlease choose a different name."
                    )
                    return

                # Create new goal
                goal_id = SavingsGoalModel.create(
                    self.db,
                    goal_name=goal_name,
                    target_amount=target_amount,
                    target_date=target_date,
                    priority=priority,
                    notes=notes,
                    initial_amount=initial_amount
                )

                QMessageBox.information(self, "Success", f"Goal '{goal_name}' created successfully!")
                self.accept()

            else:
                # Update existing goal
                is_completed = self.is_completed.isChecked() if hasattr(self, 'is_completed') else False

                # Check if name conflicts with other goals (excluding current goal)
                existing_goals = self.db.get_savings_goals(include_completed=True)
                existing_names = [goal['goal_name'].lower() for goal in existing_goals
                                if goal['id'] != self.goal_data['id']]

                if goal_name.lower() in existing_names:
                    QMessageBox.warning(
                        self,
                        "Duplicate Goal Name",
                        f"Another goal named '{goal_name}' already exists.\n\nPlease choose a different name."
                    )
                    return

                SavingsGoalModel.update(
                    self.db,
                    goal_id=self.goal_data['id'],
                    goal_name=goal_name,
                    target_amount=target_amount,
                    target_date=target_date,
                    priority=priority,
                    notes=notes,
                    initial_amount=initial_amount
                )

                if is_completed:
                    SavingsGoalModel.complete(self.db, self.goal_data['id'])

                QMessageBox.information(self, "Success", f"Goal '{goal_name}' updated successfully!")
                self.accept()

        except Exception as e:
            error_msg = str(e)
            if "UNIQUE constraint failed" in error_msg:
                QMessageBox.critical(
                    self,
                    "Duplicate Goal Name",
                    f"A goal with this name already exists.\n\nPlease choose a different name.\n\nTechnical details: {error_msg}"
                )
            else:
                QMessageBox.critical(self, "Error", f"Failed to save goal: {str(e)}")

    def delete_goal(self):
        """Delete the current goal"""
        if not self.goal_data:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the goal '{self.goal_data['goal_name']}'?\n\n"
            "This will also delete all allocation history for this goal.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_savings_goal(self.goal_data['id'])
                QMessageBox.information(self, "Success", "Goal deleted successfully!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete goal: {str(e)}")
