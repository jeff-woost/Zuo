"""
Onboarding Wizard
================

Multi-step wizard for first-time application setup.
Guides users through:
1. Welcome screen
2. User setup (names)
3. Data location selection
4. Completion confirmation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QStackedWidget, QWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
import os
from src.config import save_settings, load_settings


class OnboardingWizard(QDialog):
    """
    First-run onboarding wizard for Zuo Budget Tracker.
    
    Collects essential configuration from the user:
    - User names for personalization
    - Database location for data storage
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Zuo")
        self.setModal(True)
        self.setMinimumSize(600, 450)
        
        # Store user choices
        self.settings = load_settings()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the wizard UI"""
        layout = QVBoxLayout(self)
        
        # Create stacked widget for different pages
        self.pages = QStackedWidget()
        layout.addWidget(self.pages)
        
        # Create wizard pages
        self.pages.addWidget(self.create_welcome_page())
        self.pages.addWidget(self.create_user_setup_page())
        self.pages.addWidget(self.create_data_location_page())
        self.pages.addWidget(self.create_completion_page())
        
        # Navigation buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.hide()  # Hidden on first page
        button_layout.addWidget(self.back_button)
        
        self.next_button = QPushButton("Get Started")
        self.next_button.setDefault(True)
        self.next_button.clicked.connect(self.go_next)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
        
    def create_welcome_page(self) -> QWidget:
        """Create the welcome page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo/Branding area
        title = QLabel("Welcome to Zuo")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Your Personal Budget Tracking Companion")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Features list
        features_text = """
        <div style="line-height: 1.8;">
        <p>✓ Track income and expenses with detailed categorization</p>
        <p>✓ Monitor your net worth and assets</p>
        <p>✓ Set and track savings goals</p>
        <p>✓ Analyze spending trends and patterns</p>
        <p>✓ Generate monthly financial reports</p>
        <p style="margin-top: 20px; color: #10b981; font-weight: bold;">
        Your data stays private and secure on your computer
        </p>
        </div>
        """
        features = QLabel(features_text)
        features.setWordWrap(True)
        features.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(features)
        
        layout.addStretch()
        
        return page
    
    def create_user_setup_page(self) -> QWidget:
        """Create the user setup page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Title
        title = QLabel("Who's Using Zuo?")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Personalize your experience by entering your name(s).")
        desc.setStyleSheet("color: #64748b; margin-bottom: 30px;")
        layout.addWidget(desc)
        
        # User A name input
        user_a_label = QLabel("Primary User Name:")
        user_a_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(user_a_label)
        
        self.user_a_input = QLineEdit()
        self.user_a_input.setPlaceholderText("e.g., Alex")
        self.user_a_input.setText(self.settings.get("user_a_name", ""))
        layout.addWidget(self.user_a_input)
        
        # User B name input
        user_b_label = QLabel("Partner Name (Optional):")
        user_b_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(user_b_label)
        
        user_b_hint = QLabel("Leave blank if you're the only user")
        user_b_hint.setStyleSheet("color: #64748b; font-size: 11px; margin-bottom: 5px;")
        layout.addWidget(user_b_hint)
        
        self.user_b_input = QLineEdit()
        self.user_b_input.setPlaceholderText("e.g., Jordan (optional)")
        self.user_b_input.setText(self.settings.get("user_b_name", ""))
        layout.addWidget(self.user_b_input)
        
        layout.addStretch()
        
        return page
    
    def create_data_location_page(self) -> QWidget:
        """Create the data location selection page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Title
        title = QLabel("Where Should Zuo Keep Your Data?")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Choose where to store your financial database. "
            "Your data stays on your computer and is never uploaded to the cloud."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; margin-bottom: 30px;")
        layout.addWidget(desc)
        
        # Database path selection
        path_label = QLabel("Database Location:")
        path_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        
        # Default to current directory
        default_path = os.path.join(os.getcwd(), "budget_tracker.db")
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.settings.get("database_path", default_path))
        self.db_path_input.setReadOnly(True)
        path_layout.addWidget(self.db_path_input)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_database_location)
        path_layout.addWidget(browse_button)
        
        layout.addLayout(path_layout)
        
        # Info message
        info = QLabel(
            "💡 Tip: Choose a location you regularly back up, "
            "like your Documents folder or cloud-synced folder."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #64748b; margin-top: 20px; padding: 10px; "
                          "background-color: #f1f5f9; border-radius: 5px;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        return page
    
    def create_completion_page(self) -> QWidget:
        """Create the completion page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Success icon/title
        title = QLabel("You're All Set!")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Completion message
        message = QLabel(
            "Zuo is now configured and ready to help you manage your finances.\n\n"
            "You can change these settings anytime in the preferences."
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: #64748b; margin: 20px;")
        layout.addWidget(message)
        
        # Summary box
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background-color: #f8fafc; padding: 20px; "
            "border-radius: 8px; border: 1px solid #e2e8f0;"
        )
        layout.addWidget(self.summary_label)
        
        layout.addStretch()
        
        return page
    
    def browse_database_location(self):
        """Open file dialog to select database location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose Database Location",
            self.db_path_input.text(),
            "SQLite Database (*.db);;All Files (*)"
        )
        
        if file_path:
            # Ensure .db extension
            if not file_path.endswith('.db'):
                file_path += '.db'
            self.db_path_input.setText(file_path)
    
    def go_next(self):
        """Handle next button click"""
        current_index = self.pages.currentIndex()
        
        if current_index == 0:  # Welcome page
            self.pages.setCurrentIndex(1)
            self.back_button.show()
            self.next_button.setText("Next")
            
        elif current_index == 1:  # User setup page
            # Validate at least user A name is provided
            user_a = self.user_a_input.text().strip()
            if not user_a:
                QMessageBox.warning(
                    self,
                    "Name Required",
                    "Please enter at least the primary user name."
                )
                return
            
            self.settings["user_a_name"] = user_a
            self.settings["user_b_name"] = self.user_b_input.text().strip()
            
            self.pages.setCurrentIndex(2)
            self.next_button.setText("Next")
            
        elif current_index == 2:  # Data location page
            self.settings["database_path"] = self.db_path_input.text()
            
            # Update summary
            user_a = self.settings["user_a_name"]
            user_b = self.settings["user_b_name"]
            users_text = user_a
            if user_b:
                users_text = f"{user_a} and {user_b}"
            
            summary = f"""
            <p><b>Users:</b> {users_text}</p>
            <p><b>Database:</b> {self.settings["database_path"]}</p>
            """
            self.summary_label.setText(summary)
            
            self.pages.setCurrentIndex(3)
            self.back_button.show()
            self.next_button.setText("Launch Zuo")
            
        elif current_index == 3:  # Completion page
            # Save settings and close
            self.settings["onboarding_completed"] = True
            if save_settings(self.settings):
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to save settings. Please try again."
                )
    
    def go_back(self):
        """Handle back button click"""
        current_index = self.pages.currentIndex()
        
        if current_index > 0:
            self.pages.setCurrentIndex(current_index - 1)
            
            if current_index == 1:  # Going back to welcome
                self.back_button.hide()
                self.next_button.setText("Get Started")
            elif current_index == 2:  # Going back to user setup
                self.next_button.setText("Next")
            elif current_index == 3:  # Going back to data location
                self.next_button.setText("Next")
