"""
Bank Reconciliation Tab
=======================

This tab provides functionality to import and reconcile bank transactions from CSV files,
particularly designed for TD Bank format. It allows users to:
- Import bank transactions from CSV
- View and filter transactions by month
- Mark transactions as reconciled
- Import selected transactions as income or expenses to the budget system

CSV Format Expected:
Date,Bank RTN,Account Number,Transaction Type,Description,Debit,Credit,Check Number,Account Running Balance
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QDateEdit, QGroupBox, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
import csv
from src.database.db_manager import DatabaseManager
from src.database.category_manager import get_category_manager

class ImportTransactionDialog(QDialog):
    """Dialog for importing a bank transaction as income or expense"""
    
    def __init__(self, parent, transaction, transaction_type):
        super().__init__(parent)
        self.transaction = transaction
        self.transaction_type = transaction_type  # 'income' or 'expense'
        self.category_manager = get_category_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the import dialog UI"""
        self.setWindowTitle(f"Import as {self.transaction_type.title()}")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        
        # Show transaction details
        info_group = QGroupBox("Transaction Details")
        info_layout = QFormLayout()
        info_layout.addRow("Date:", QLabel(self.transaction['date']))
        info_layout.addRow("Description:", QLabel(self.transaction['description']))
        info_layout.addRow("Amount:", QLabel(f"${abs(self.transaction['amount']):.2f}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Import settings
        settings_group = QGroupBox(f"{self.transaction_type.title()} Settings")
        settings_layout = QFormLayout()
        
        if self.transaction_type == 'income':
            # Person selector for income
            settings_layout.addRow("Person:", QLabel("For income imports"))
            self.person_combo = QComboBox()
            self.person_combo.addItems(["Jeff", "Vanessa"])
            settings_layout.addRow("Assign to:", self.person_combo)

            # Source/description
            self.source_input = QLineEdit(self.transaction['description'])
            settings_layout.addRow("Source:", self.source_input)
            
        else:  # expense
            # Person selector for expense
            self.person_combo = QComboBox()
            self.person_combo.addItems(["Jeff", "Vanessa"])
            settings_layout.addRow("Person:", self.person_combo)

            # Category selector
            categories = self.category_manager.get_all_categories()
            self.category_combo = QComboBox()
            category_names = sorted(list(set([cat['category'] for cat in categories])))
            self.category_combo.addItems(category_names)
            self.category_combo.currentTextChanged.connect(self.on_category_changed)
            settings_layout.addRow("Category:", self.category_combo)
            
            # Subcategory selector
            self.subcategory_combo = QComboBox()
            settings_layout.addRow("Subcategory:", self.subcategory_combo)
            
            # Description
            self.description_input = QLineEdit(self.transaction['description'])
            settings_layout.addRow("Description:", self.description_input)
            
            # Payment method
            self.payment_method_combo = QComboBox()
            self.payment_method_combo.addItems(["Checking", "Credit Card", "Cash", "Debit Card", "Other"])
            settings_layout.addRow("Payment Method:", self.payment_method_combo)
            
            # Initialize subcategories
            if len(category_names) > 0:
                self.on_category_changed(category_names[0])
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def on_category_changed(self, category):
        """Update subcategories when category changes"""
        self.subcategory_combo.clear()
        categories = self.category_manager.get_all_categories()
        subcategories = [cat['subcategory'] for cat in categories if cat['category'] == category]
        self.subcategory_combo.addItems(sorted(subcategories))
        
    def get_import_data(self):
        """Get the data to import"""
        data = {
            'date': self.transaction['date'],
            'amount': abs(self.transaction['amount']),
        }
        
        if self.transaction_type == 'income':
            data['person'] = self.person_combo.currentText()
            data['source'] = self.source_input.text()
            data['notes'] = f"Imported from bank: {self.transaction['description']}"
        else:
            data['person'] = self.person_combo.currentText()
            data['category'] = self.category_combo.currentText()
            data['subcategory'] = self.subcategory_combo.currentText()
            data['description'] = self.description_input.text()
            data['payment_method'] = self.payment_method_combo.currentText()

        return data


class BankReconciliationTab(QWidget):
    """Tab for bank reconciliation and transaction import"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.transactions = []
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Bank Reconciliation - Checking Account")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #f7fafc; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Controls section
        controls_layout = QHBoxLayout()
        
        # Month selector
        filter_label = QLabel("Filter by Month:")
        filter_label.setStyleSheet("color: #e2e8f0; font-size: 14px;")
        controls_layout.addWidget(filter_label)
        self.month_selector = QDateEdit()
        self.month_selector.setDisplayFormat("MMMM yyyy")
        self.month_selector.setDate(QDate.currentDate())
        self.month_selector.setCalendarPopup(True)
        self.month_selector.dateChanged.connect(self.refresh_data)
        controls_layout.addWidget(self.month_selector)
        
        controls_layout.addStretch()
        
        # Import CSV button
        import_btn = QPushButton("📁 Import Bank CSV")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #4c51bf;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #5a67d8;
            }
            QPushButton:pressed {
                background-color: #434190;
            }
        """)
        import_btn.clicked.connect(self.import_csv)
        controls_layout.addWidget(import_btn)
        
        # Clear All button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53e3e;
                color: white;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #fc8181;
            }
            QPushButton:pressed {
                background-color: #c53030;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_transactions)
        controls_layout.addWidget(clear_btn)

        layout.addLayout(controls_layout)
        
        # Summary section
        summary_group = QGroupBox("Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #f7fafc;
                border: 2px solid #4a5568;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        summary_layout = QHBoxLayout()
        
        self.total_debits_label = QLabel("Total Debits: $0.00")
        self.total_credits_label = QLabel("Total Credits: $0.00")
        self.net_change_label = QLabel("Net Change: $0.00")
        self.reconciled_count_label = QLabel("Reconciled: 0/0")
        
        summary_layout.addWidget(self.total_debits_label)
        summary_layout.addWidget(self.total_credits_label)
        summary_layout.addWidget(self.net_change_label)
        summary_layout.addWidget(self.reconciled_count_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Amount", "Balance", "Comment", "Reconciled"
        ])
        
        # Style the table - match dark theme from other tabs
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSortingEnabled(True)
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background-color: #374151;
                alternate-background-color: #2d3748;
                gridline-color: #4a5568;
                color: #e2e8f0;
                border: 1px solid #4a5568;
                border-radius: 4px;
                selection-background-color: #4c51bf;
                font-size: 14px;
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
                padding: 10px;
                border: 1px solid #2d3748;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        # Set column widths
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Comment - stretch
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)    # Reconciled

        self.transactions_table.setColumnWidth(0, 110)  # Date
        self.transactions_table.setColumnWidth(1, 90)   # Type
        self.transactions_table.setColumnWidth(3, 130)  # Amount
        self.transactions_table.setColumnWidth(4, 140)  # Balance
        # Column 5 (Comment) is Stretch - takes remaining space
        self.transactions_table.setColumnWidth(6, 120)  # Reconciled - wider for checkmark

        # Set default row height (reduced from 50 since no action buttons)
        self.transactions_table.verticalHeader().setDefaultSectionSize(40)
        self.transactions_table.verticalHeader().setVisible(False)

        layout.addWidget(self.transactions_table)
        
    def import_csv(self):
        """Import transactions from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Bank Transactions CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                
                # Skip header row
                header = next(csv_reader)
                
                imported_count = 0
                duplicate_count = 0
                
                for row in csv_reader:
                    if len(row) < 9:
                        continue
                        
                    # Parse CSV row
                    date_str = row[0].strip()
                    bank_rtn = row[1].strip() if len(row) > 1 else ""
                    account_number = row[2].strip() if len(row) > 2 else ""
                    transaction_type = row[3].strip() if len(row) > 3 else ""
                    description = row[4].strip() if len(row) > 4 else ""
                    debit = row[5].strip() if len(row) > 5 else ""
                    credit = row[6].strip() if len(row) > 6 else ""
                    check_number = row[7].strip() if len(row) > 7 else ""
                    account_balance = row[8].strip() if len(row) > 8 else ""
                    
                    # Parse date
                    try:
                        # Try multiple date formats
                        for fmt in ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']:
                            try:
                                date_obj = datetime.strptime(date_str, fmt)
                                date_str = date_obj.strftime('%Y-%m-%d')
                                break
                            except ValueError:
                                continue
                    except:
                        continue
                    
                    # Parse amounts - handle empty strings and currency formatting
                    try:
                        debit_amt = float(debit.replace(',', '').replace('$', '')) if debit and debit.strip() else None
                    except (ValueError, AttributeError):
                        debit_amt = None

                    try:
                        credit_amt = float(credit.replace(',', '').replace('$', '')) if credit and credit.strip() else None
                    except (ValueError, AttributeError):
                        credit_amt = None

                    try:
                        balance = float(account_balance.replace(',', '').replace('$', '')) if account_balance and account_balance.strip() else None
                    except (ValueError, AttributeError):
                        balance = None

                    # Insert into database (OR IGNORE skips duplicates based on unique constraint)
                    try:
                        self.db.execute('''
                            INSERT OR IGNORE INTO bank_transactions 
                            (date, bank_rtn, account_number, transaction_type, description, 
                             debit, credit, check_number, account_balance)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (date_str, bank_rtn, account_number, transaction_type, description,
                              debit_amt, credit_amt, check_number, balance))
                        # Check if row was actually inserted
                        if self.db.execute('SELECT changes()').fetchone()[0] > 0:
                            imported_count += 1
                        else:
                            duplicate_count += 1
                    except Exception as e:
                        print(f"Error importing transaction: {e}")

                self.db.commit()
                
                QMessageBox.information(
                    self, "Import Complete",
                    f"Imported {imported_count} new transactions.\n"
                    f"{duplicate_count} duplicates skipped."
                )
                
                self.refresh_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import CSV: {str(e)}")
            
    def refresh_data(self):
        """Refresh the transactions table"""
        # Get selected month
        selected_date = self.month_selector.date()
        year = selected_date.year()
        month = selected_date.month()
        
        # Calculate month range
        month_start = f"{year}-{month:02d}-01"
        if month == 12:
            month_end = f"{year + 1}-01-01"
        else:
            month_end = f"{year}-{month + 1:02d}-01"
        
        # Query transactions for the month
        self.transactions = self.db.execute('''
            SELECT * FROM bank_transactions
            WHERE date >= ? AND date < ?
            ORDER BY date DESC, id DESC
        ''', (month_start, month_end)).fetchall()
        
        # Update table
        self.transactions_table.setRowCount(len(self.transactions))
        
        total_debits = 0
        total_credits = 0
        reconciled_count = 0
        
        for row_idx, transaction in enumerate(self.transactions):
            # Determine transaction type and amount based on which column has a value
            # Credit column has value = CREDIT, Debit column has value = DEBIT
            debit_val = transaction['debit'] if transaction['debit'] else 0
            credit_val = transaction['credit'] if transaction['credit'] else 0

            # Determine type based on which column has a value (not both)
            if credit_val > 0:
                # Credit column has a value - label as CREDIT
                trans_type = "CREDIT"
                amount = credit_val
                total_credits += credit_val
            elif debit_val > 0:
                # Debit column has a value - label as DEBIT
                trans_type = "DEBIT"
                amount = -debit_val
                total_debits += debit_val
            else:
                # No amount in either column
                trans_type = transaction['transaction_type'] or "N/A"
                amount = 0

            # Date
            date_item = QTableWidgetItem(transaction['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setFont(QFont("Arial", 12))
            self.transactions_table.setItem(row_idx, 0, date_item)
            
            # Type
            type_item = QTableWidgetItem(trans_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            type_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            if trans_type == "DEBIT":
                type_item.setForeground(QColor("#ff6b6b"))  # Brighter red for dark theme
            else:
                type_item.setForeground(QColor("#69db7c"))  # Brighter green for dark theme
            self.transactions_table.setItem(row_idx, 1, type_item)
            
            # Description
            desc_item = QTableWidgetItem(transaction['description'])
            desc_item.setFont(QFont("Arial", 12))
            self.transactions_table.setItem(row_idx, 2, desc_item)

            # Amount - format with commas ($##,###.##)
            amount_item = QTableWidgetItem(f"${abs(amount):,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            amount_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            if amount < 0:
                amount_item.setForeground(QColor("#ff6b6b"))  # Brighter red for dark theme
            else:
                amount_item.setForeground(QColor("#69db7c"))  # Brighter green for dark theme
            self.transactions_table.setItem(row_idx, 3, amount_item)
            
            # Balance - format with commas ($##,###.##)
            if transaction['account_balance']:
                balance_text = f"${transaction['account_balance']:,.2f}"
            else:
                balance_text = ""
            balance_item = QTableWidgetItem(balance_text)
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            balance_item.setFont(QFont("Arial", 12))
            self.transactions_table.setItem(row_idx, 4, balance_item)
            
            # Comment - editable text field for user notes
            comment_widget = QWidget()
            comment_widget.setStyleSheet("background-color: transparent;")
            comment_layout = QHBoxLayout(comment_widget)
            comment_layout.setContentsMargins(4, 4, 4, 4)

            comment_input = QLineEdit()
            # Safely get comment value (may not exist in older databases)
            try:
                comment_text = transaction['comment'] if transaction['comment'] else ""
            except (KeyError, IndexError):
                comment_text = ""
            comment_input.setText(comment_text)
            comment_input.setPlaceholderText("Add notes...")
            comment_input.setStyleSheet("""
                QLineEdit {
                    background-color: #2d3748;
                    color: #e2e8f0;
                    border: 1px solid #4a5568;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 12px;
                }
                QLineEdit:focus {
                    border: 1px solid #4c51bf;
                    background-color: #374151;
                }
            """)
            # Save comment when user finishes editing
            comment_input.editingFinished.connect(
                lambda tid=transaction['id'], input_field=comment_input: self.save_comment(tid, input_field.text())
            )
            comment_layout.addWidget(comment_input)

            self.transactions_table.setCellWidget(row_idx, 5, comment_widget)

            # Reconciled checkbox with big red checkmark when checked
            reconciled_widget = QWidget()
            reconciled_widget.setStyleSheet("background-color: transparent;")
            reconciled_layout = QHBoxLayout(reconciled_widget)
            reconciled_layout.setContentsMargins(0, 0, 0, 0)
            reconciled_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if transaction['reconciled']:
                # Show big red checkmark for reconciled items
                checkmark_label = QLabel("✓")
                checkmark_label.setStyleSheet("""
                    QLabel {
                        color: #ff4444;
                        font-size: 28px;
                        font-weight: bold;
                    }
                """)
                checkmark_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkmark_label.setCursor(Qt.CursorShape.PointingHandCursor)
                checkmark_label.mousePressEvent = lambda event, tid=transaction['id']: self.toggle_reconciled_from_label(tid, False)
                reconciled_layout.addWidget(checkmark_label)
                reconciled_count += 1
            else:
                # Show checkbox for unreconciled items
                reconciled_cb = QCheckBox()
                reconciled_cb.setChecked(False)
                reconciled_cb.setStyleSheet("""
                    QCheckBox {
                        spacing: 0px;
                    }
                    QCheckBox::indicator {
                        width: 26px;
                        height: 26px;
                        border-radius: 4px;
                        border: 2px solid #6b7280;
                        background-color: #374151;
                    }
                    QCheckBox::indicator:hover {
                        border-color: #ff4444;
                        background-color: #4a5568;
                    }
                """)
                reconciled_cb.stateChanged.connect(lambda state, tid=transaction['id']: self.toggle_reconciled(tid, state))
                reconciled_layout.addWidget(reconciled_cb)

            self.transactions_table.setCellWidget(row_idx, 6, reconciled_widget)

        # Update summary with comma formatting
        net_change = total_credits - total_debits
        self.total_debits_label.setText(f"Total Debits: ${total_debits:,.2f}")
        self.total_debits_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px;")
        self.total_credits_label.setText(f"Total Credits: ${total_credits:,.2f}")
        self.total_credits_label.setStyleSheet("color: #69db7c; font-weight: bold; font-size: 14px;")
        self.net_change_label.setText(f"Net Change: ${net_change:,.2f}")
        if net_change >= 0:
            self.net_change_label.setStyleSheet("color: #69db7c; font-weight: bold; font-size: 14px;")
        else:
            self.net_change_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px;")
        self.reconciled_count_label.setText(f"Reconciled: {reconciled_count}/{len(self.transactions)}")
        self.reconciled_count_label.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 14px;")

    def toggle_reconciled(self, transaction_id, state):
        """Toggle reconciled status"""
        self.db.execute(
            'UPDATE bank_transactions SET reconciled = ? WHERE id = ?',
            (1 if state == Qt.CheckState.Checked.value else 0, transaction_id)
        )
        self.db.commit()
        self.refresh_data()

    def toggle_reconciled_from_label(self, transaction_id, new_state):
        """Toggle reconciled status when clicking the checkmark label"""
        self.db.execute(
            'UPDATE bank_transactions SET reconciled = ? WHERE id = ?',
            (1 if new_state else 0, transaction_id)
        )
        self.db.commit()
        self.refresh_data()

    def save_comment(self, transaction_id, comment_text):
        """Save comment/note for a transaction"""
        try:
            self.db.execute(
                'UPDATE bank_transactions SET comment = ? WHERE id = ?',
                (comment_text, transaction_id)
            )
            self.db.commit()
        except Exception as e:
            print(f"Error saving comment: {e}")
            QMessageBox.warning(self, "Error", f"Failed to save comment: {str(e)}")

    def clear_all_transactions(self):
        """Clear all bank transactions from the database"""
        reply = QMessageBox.question(
            self, "Clear All Transactions",
            "Are you sure you want to delete ALL bank transactions?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.execute('DELETE FROM bank_transactions')
                self.db.commit()
                QMessageBox.information(self, "Success", "All bank transactions have been deleted.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear transactions: {str(e)}")

    def import_as_income(self, transaction):
        """Import transaction as income"""
        # Prepare transaction data - use credit if available, otherwise debit
        amount = transaction['credit'] if transaction['credit'] else (transaction['debit'] if transaction['debit'] else 0)
        trans_data = {
            'date': transaction['date'],
            'description': transaction['description'],
            'amount': amount,
            'transaction_type': transaction['transaction_type']
        }
        
        # Show import dialog
        dialog = ImportTransactionDialog(self, trans_data, 'income')
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_import_data()
            
            # Insert income
            try:
                self.db.execute('''
                    INSERT INTO income (date, person, amount, source, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (data['date'], data['person'], data['amount'], data['source'], data['notes']))

                # Mark as imported
                self.db.execute(
                    'UPDATE bank_transactions SET imported_to_budget = 1 WHERE id = ?',
                    (transaction['id'],)
                )
                
                self.db.commit()
                
                QMessageBox.information(self, "Success", "Transaction imported as income!")
                self.refresh_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
    
    def import_as_expense(self, transaction):
        """Import transaction as expense"""
        # Prepare transaction data - use debit if available, otherwise credit
        amount = transaction['debit'] if transaction['debit'] else (transaction['credit'] if transaction['credit'] else 0)
        trans_data = {
            'date': transaction['date'],
            'description': transaction['description'],
            'amount': amount,
            'transaction_type': transaction['transaction_type']
        }
        # Show import dialog
        dialog = ImportTransactionDialog(self, trans_data, 'expense')
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_import_data()
            
            # Insert expense
            try:
                self.db.execute('''
                    INSERT INTO expenses (date, person, amount, category, subcategory, 
                                         description, payment_method, realized, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (data['date'], data['person'], data['amount'], data['category'],
                      data['subcategory'], data['description'], data['payment_method'],
                      1 if data['realized'] else 0))

                # Mark as imported
                self.db.execute(
                    'UPDATE bank_transactions SET imported_to_budget = 1 WHERE id = ?',
                    (transaction['id'],)
                )
                
                self.db.commit()
                
                QMessageBox.information(self, "Success", "Transaction imported as expense!")
                self.refresh_data()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")
