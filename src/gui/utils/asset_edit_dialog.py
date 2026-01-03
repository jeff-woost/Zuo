"""
Asset Edit Dialog - Dialog for editing net worth assets
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QDateEdit, QTextEdit, QGridLayout,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime

class AssetEditDialog(QDialog):
    """Dialog for editing an existing asset"""
    
    asset_updated = pyqtSignal()  # Signal emitted when asset is updated
    
    def __init__(self, asset_data, db_manager, parent=None):
        super().__init__(parent)
        self.asset_data = asset_data
        self.db = db_manager
        self.setWindowTitle("Edit Asset")
        self.setModal(True)
        self.resize(400, 350)
        self.init_ui()
        self.populate_data()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Edit Asset Details")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Form group
        form_group = QGroupBox("Asset Information")
        form_layout = QGridLayout()
        
        # Person selector
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa", "Joint"])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        # Asset type
        form_layout.addWidget(QLabel("Asset Type:"), 1, 0)
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems([
            "Real Estate", "Checking Account", "Savings Account",
            "Brokerage Account", "401(k)", "Roth 401(k)", "Roth IRA", 
            "Traditional IRA", "Trust", "HSA", "529 Plan", "Cryptocurrency", 
            "Precious Metals", "Vehicle", "Other Asset", "Debt/Liability"
        ])
        form_layout.addWidget(self.asset_type_combo, 1, 1)
        
        # Asset name
        form_layout.addWidget(QLabel("Asset Name:"), 2, 0)
        self.asset_name_input = QLineEdit()
        self.asset_name_input.setPlaceholderText("e.g., Chase Checking, Fidelity 401k")
        form_layout.addWidget(self.asset_name_input, 2, 1)
        
        # Value
        form_layout.addWidget(QLabel("Value:"), 3, 0)
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter amount (negative for liabilities)")
        form_layout.addWidget(self.value_input, 3, 1)
        
        # Date
        form_layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 4, 1)
        
        # Notes
        form_layout.addWidget(QLabel("Notes:"), 5, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        form_layout.addWidget(self.notes_input, 5, 1)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6bb8;
            }
        """)
        button_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("Delete Asset")
        delete_btn.clicked.connect(self.delete_asset)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def populate_data(self):
        """Populate the form with existing asset data"""
        if not self.asset_data:
            return
            
        # Set person
        person_index = self.person_combo.findText(self.asset_data.get('person', ''))
        if person_index >= 0:
            self.person_combo.setCurrentIndex(person_index)
            
        # Set asset type
        type_index = self.asset_type_combo.findText(self.asset_data.get('asset_type', ''))
        if type_index >= 0:
            self.asset_type_combo.setCurrentIndex(type_index)
            
        # Set asset name
        self.asset_name_input.setText(self.asset_data.get('asset_name', ''))
        
        # Set value
        value = self.asset_data.get('value', 0)
        self.value_input.setText(str(value))
        
        # Set date
        date_str = self.asset_data.get('date', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.date_input.setDate(QDate(date_obj))
            except ValueError:
                self.date_input.setDate(QDate.currentDate())
        
        # Set notes
        self.notes_input.setPlainText(self.asset_data.get('notes', ''))
        
    def save_changes(self):
        """Save the updated asset data"""
        try:
            person = self.person_combo.currentText()
            asset_type = self.asset_type_combo.currentText()
            asset_name = self.asset_name_input.text().strip()
            value_text = self.value_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            notes = self.notes_input.toPlainText().strip()
            
            # Validate inputs
            if not asset_name:
                QMessageBox.warning(self, "Warning", "Please enter an asset name")
                return
                
            if not value_text:
                QMessageBox.warning(self, "Warning", "Please enter a value")
                return
                
            try:
                value = float(value_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for value")
                return
            
            # Add updated asset to database (creates new record for tracking)
            self.db.add_asset(person, asset_type, asset_name, value, date, notes)
            
            # Emit signal and close
            self.asset_updated.emit()
            QMessageBox.information(self, "Success", "Asset updated successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update asset: {str(e)}")
            
    def delete_asset(self):
        """Delete the asset (mark as deleted with $0 value)"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete '{self.asset_data.get('asset_name', 'this asset')}'?\n\n"
            "This will add a $0.00 entry to mark it as deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Add a $0 entry to effectively "delete" the asset
                person = self.asset_data.get('person', '')
                asset_type = self.asset_data.get('asset_type', '')
                asset_name = self.asset_data.get('asset_name', '')
                date = QDate.currentDate().toString("yyyy-MM-dd")
                notes = f"Asset deleted on {date}"
                
                self.db.add_asset(person, asset_type, asset_name, 0.0, date, notes)
                
                # Emit signal and close
                self.asset_updated.emit()
                QMessageBox.information(self, "Success", "Asset deleted successfully!")
                self.accept()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete asset: {str(e)}")
