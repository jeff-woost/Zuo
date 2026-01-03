"""
Category Management Dialog
==========================

Dialog for managing categories and subcategories in the Budget Tracker.
Allows users to add, edit, rename, and delete categories and subcategories
with proper validation and error handling.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
    QWidget, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from src.database.category_manager import get_category_manager
import os


class CategoryManagementDialog(QDialog):
    """Dialog for managing categories and subcategories"""
    
    # Signal emitted when categories are changed
    categoriesChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_manager = get_category_manager()
        self.setWindowTitle("Zuo - Manage Categories")
        self.setMinimumSize(700, 600)
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        
        # Try to load Zuo logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "zuo_logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            header_layout.addWidget(logo_label)
        
        title = QLabel("Category Management")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Instructions
        instructions = QLabel(
            "Manage your expense categories and subcategories. "
            "Categories organize your spending, and subcategories provide detailed breakdowns."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #64748b; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Category tree
        tree_group = QGroupBox("Categories")
        tree_layout = QVBoxLayout()
        
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["Category / Subcategory"])
        self.category_tree.setAlternatingRowColors(True)
        self.category_tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QTreeWidget::item:selected {
                background-color: #1e3a5f;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #f0f9ff;
            }
        """)
        tree_layout.addWidget(self.category_tree)
        
        tree_group.setLayout(tree_layout)
        layout.addWidget(tree_group)
        
        # Action buttons
        button_group = QGroupBox("Actions")
        button_layout = QGridLayout()
        
        # Category actions
        button_layout.addWidget(QLabel("Category:"), 0, 0)
        
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.add_category_btn.clicked.connect(self.add_category)
        button_layout.addWidget(self.add_category_btn, 0, 1)
        
        self.rename_category_btn = QPushButton("Rename Category")
        self.rename_category_btn.clicked.connect(self.rename_category)
        button_layout.addWidget(self.rename_category_btn, 0, 2)
        
        self.delete_category_btn = QPushButton("Delete Category")
        self.delete_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        self.delete_category_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(self.delete_category_btn, 0, 3)
        
        # Subcategory actions
        button_layout.addWidget(QLabel("Subcategory:"), 1, 0)
        
        self.add_subcategory_btn = QPushButton("Add Subcategory")
        self.add_subcategory_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.add_subcategory_btn.clicked.connect(self.add_subcategory)
        button_layout.addWidget(self.add_subcategory_btn, 1, 1)
        
        self.rename_subcategory_btn = QPushButton("Rename Subcategory")
        self.rename_subcategory_btn.clicked.connect(self.rename_subcategory)
        button_layout.addWidget(self.rename_subcategory_btn, 1, 2)
        
        self.delete_subcategory_btn = QPushButton("Delete Subcategory")
        self.delete_subcategory_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        self.delete_subcategory_btn.clicked.connect(self.delete_subcategory)
        button_layout.addWidget(self.delete_subcategory_btn, 1, 3)
        
        button_group.setLayout(button_layout)
        layout.addWidget(button_group)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        close_btn.clicked.connect(self.accept)
        close_layout.addWidget(close_btn)
        
        layout.addLayout(close_layout)
    
    def load_categories(self):
        """Load categories into the tree"""
        self.category_tree.clear()
        
        categories = self.category_manager.get_categories()
        
        for category in sorted(categories.keys()):
            category_item = QTreeWidgetItem([category])
            category_item.setFont(0, QFont("Arial", 12, QFont.Weight.Bold))
            category_item.setForeground(0, Qt.GlobalColor.darkBlue)
            
            for subcategory in sorted(categories[category]):
                subcategory_item = QTreeWidgetItem([subcategory])
                subcategory_item.setFont(0, QFont("Arial", 11))
                category_item.addChild(subcategory_item)
            
            category_item.setExpanded(True)
            self.category_tree.addTopLevelItem(category_item)
    
    def add_category(self):
        """Add a new category"""
        name, ok = QInputDialog.getText(
            self,
            "Zuo - Add Category",
            "Enter new category name:",
        )
        
        if ok and name:
            name = name.strip()
            if self.category_manager.add_category(name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Category '{name}' added successfully!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not add category '{name}'. It may already exist."
                )
    
    def rename_category(self):
        """Rename selected category"""
        selected = self.category_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Zuo - No Selection", "Please select a category to rename.")
            return
        
        # Make sure it's a top-level item (category, not subcategory)
        if selected.parent():
            QMessageBox.warning(self, "Zuo - Invalid Selection", "Please select a category (not a subcategory) to rename.")
            return
        
        old_name = selected.text(0)
        new_name, ok = QInputDialog.getText(
            self,
            "Zuo - Rename Category",
            f"Rename category '{old_name}' to:",
            text=old_name
        )
        
        if ok and new_name:
            new_name = new_name.strip()
            if self.category_manager.rename_category(old_name, new_name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Category renamed from '{old_name}' to '{new_name}'!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not rename category. The name '{new_name}' may already exist."
                )
    
    def delete_category(self):
        """Delete selected category"""
        selected = self.category_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Zuo - No Selection", "Please select a category to delete.")
            return
        
        # Make sure it's a top-level item (category, not subcategory)
        if selected.parent():
            QMessageBox.warning(self, "Zuo - Invalid Selection", "Please select a category (not a subcategory) to delete.")
            return
        
        name = selected.text(0)
        
        reply = QMessageBox.question(
            self,
            "Zuo - Confirm Deletion",
            f"Are you sure you want to delete the category '{name}' and all its subcategories?\n\n"
            "This will only work if the category is not used in any expenses or budget estimates.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.category_manager.delete_category(name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Category '{name}' deleted successfully!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not delete category '{name}'.\n\n"
                    "It may be in use by expenses or budget estimates."
                )
    
    def add_subcategory(self):
        """Add a new subcategory"""
        selected = self.category_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Zuo - No Selection", "Please select a category to add a subcategory to.")
            return
        
        # Get the category (either selected or its parent)
        if selected.parent():
            category = selected.parent().text(0)
        else:
            category = selected.text(0)
        
        name, ok = QInputDialog.getText(
            self,
            "Zuo - Add Subcategory",
            f"Add subcategory to '{category}':",
        )
        
        if ok and name:
            name = name.strip()
            if self.category_manager.add_subcategory(category, name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Subcategory '{name}' added to '{category}'!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not add subcategory '{name}'. It may already exist."
                )
    
    def rename_subcategory(self):
        """Rename selected subcategory"""
        selected = self.category_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Zuo - No Selection", "Please select a subcategory to rename.")
            return
        
        # Make sure it's a child item (subcategory, not category)
        if not selected.parent():
            QMessageBox.warning(self, "Zuo - Invalid Selection", "Please select a subcategory (not a category) to rename.")
            return
        
        category = selected.parent().text(0)
        old_name = selected.text(0)
        
        new_name, ok = QInputDialog.getText(
            self,
            "Zuo - Rename Subcategory",
            f"Rename subcategory '{old_name}' in '{category}' to:",
            text=old_name
        )
        
        if ok and new_name:
            new_name = new_name.strip()
            if self.category_manager.rename_subcategory(category, old_name, new_name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Subcategory renamed from '{old_name}' to '{new_name}'!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not rename subcategory. The name '{new_name}' may already exist."
                )
    
    def delete_subcategory(self):
        """Delete selected subcategory"""
        selected = self.category_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "Zuo - No Selection", "Please select a subcategory to delete.")
            return
        
        # Make sure it's a child item (subcategory, not category)
        if not selected.parent():
            QMessageBox.warning(self, "Zuo - Invalid Selection", "Please select a subcategory (not a category) to delete.")
            return
        
        category = selected.parent().text(0)
        name = selected.text(0)
        
        reply = QMessageBox.question(
            self,
            "Zuo - Confirm Deletion",
            f"Are you sure you want to delete the subcategory '{name}' from '{category}'?\n\n"
            "This will only work if the subcategory is not used in any expenses or budget estimates.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.category_manager.delete_subcategory(category, name):
                QMessageBox.information(
                    self,
                    "Zuo - Success",
                    f"Subcategory '{name}' deleted successfully!"
                )
                self.load_categories()
                self.categoriesChanged.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Zuo - Error",
                    f"Could not delete subcategory '{name}'.\n\n"
                    "It may be in use by expenses or budget estimates."
                )
