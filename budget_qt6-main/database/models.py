"""
Database models and operations
"""

from datetime import datetime, date

class IncomeModel:
    """Model for income operations"""
    
    @staticmethod
    def add(db, date_str, person, amount, source, notes):
        """Add income entry"""
        db.execute('''
            INSERT INTO income (date, person, amount, source, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, person, amount, source, notes))
        db.commit()
        
    @staticmethod
    def get_all(db, limit=50):
        """Get all income entries"""
        return db.execute('''
            SELECT * FROM income
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
    @staticmethod
    def get_by_month(db, month_start, month_end):
        """Get income for a specific month"""
        return db.execute('''
            SELECT * FROM income
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (month_start, month_end)).fetchall()
        
    @staticmethod
    def get_total_by_month(db, month_start, month_end):
        """Get total income for a month"""
        result = db.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM income
            WHERE date >= ? AND date <= ?
        ''', (month_start, month_end)).fetchone()
        return result['total'] if result else 0
        
    @staticmethod
    def delete(db, income_id):
        """Delete income entry"""
        db.execute('DELETE FROM income WHERE id = ?', (income_id,))
        db.commit()

class ExpenseModel:
    """Model for expense operations"""
    
    @staticmethod
    def add(db, date_str, person, amount, category, subcategory, description, payment_method, realized=False):
        """Add expense entry with validation"""
        # Validate required fields
        if not date_str or not date_str.strip():
            raise ValueError("Date is required")
        if not person or not person.strip():
            raise ValueError("Person is required")
        if amount is None or amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not category or not category.strip():
            raise ValueError("Category is required")
        if not subcategory or not subcategory.strip():
            raise ValueError("Subcategory is required")

        # Clean and validate data
        date_str = date_str.strip()
        person = person.strip()
        category = category.strip()
        subcategory = subcategory.strip()
        description = description.strip() if description else ""
        payment_method = payment_method.strip() if payment_method else ""

        db.execute('''
            INSERT INTO expenses (date, person, amount, category, subcategory, description, payment_method, realized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, person, amount, category, subcategory, description, payment_method, realized))
        db.commit()

    @staticmethod
    def clear_all(db):
        """Clear all expenses from the database"""
        try:
            # Get count before deletion for logging
            cursor = db.execute("SELECT COUNT(*) as count FROM expenses")
            count = cursor.fetchone()['count']

            # Delete all expenses
            db.execute("DELETE FROM expenses")

            # Reset auto-increment counter
            db.execute("DELETE FROM sqlite_sequence WHERE name='expenses'")

            db.commit()
            return count
        except Exception as e:
            db.conn.rollback() if db.conn else None
            raise e

    @staticmethod
    def get_all(db, limit=50):
        """Get all expense entries"""
        return db.execute('''
            SELECT * FROM expenses
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,)).fetchall()

    @staticmethod
    def get_by_month(db, month_start, month_end):
        """Get expenses for a specific month"""
        return db.execute('''
            SELECT * FROM expenses
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (month_start, month_end)).fetchall()

    @staticmethod
    def get_total_by_month(db, month_start, month_end):
        """Get total expenses for a month"""
        result = db.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
        ''', (month_start, month_end)).fetchone()
        return result['total'] if result else 0

    @staticmethod
    def get_by_category(db, month_start, month_end):
        """Get expenses grouped by category"""
        return db.execute('''
            SELECT category, subcategory, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category, subcategory
            ORDER BY category, subcategory
        ''', (month_start, month_end)).fetchall()

    @staticmethod
    def get_unrealized_by_person(db, month_start, month_end):
        """Get unrealized expenses by person for a specific month"""
        return db.execute('''
            SELECT person, COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ? AND realized = 0
            GROUP BY person
        ''', (month_start, month_end)).fetchall()

    @staticmethod
    def get_unrealized_expenses(db, month_start, month_end):
        """Get all unrealized expenses for a specific month"""
        return db.execute('''
            SELECT * FROM expenses
            WHERE date >= ? AND date <= ? AND realized = 0
            ORDER BY person, date DESC
        ''', (month_start, month_end)).fetchall()

    @staticmethod
    def mark_as_realized(db, expense_id):
        """Mark an expense as realized"""
        db.execute('UPDATE expenses SET realized = 1 WHERE id = ?', (expense_id,))
        db.commit()

    @staticmethod
    def mark_as_unrealized(db, expense_id):
        """Mark an expense as unrealized"""
        db.execute('UPDATE expenses SET realized = 0 WHERE id = ?', (expense_id,))
        db.commit()

    @staticmethod
    def delete(db, expense_id):
        """Delete expense entry"""
        db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        db.commit()

class NetWorthModel:
    """Model for net worth operations"""

    @staticmethod
    def add_or_update(db, asset_type, asset_name, value, person):
        """Add or update asset"""
        # Check if asset exists
        existing = db.execute('''
            SELECT id FROM net_worth
            WHERE asset_name = ? AND date = date('now')
        ''', (asset_name,)).fetchone()

        if existing:
            db.execute('''
                UPDATE net_worth
                SET value = ?, asset_type = ?, person = ?
                WHERE id = ?
            ''', (value, asset_type, person, existing['id']))
        else:
            db.execute('''
                INSERT INTO net_worth (date, asset_type, asset_name, value, person)
                VALUES (date('now'), ?, ?, ?, ?)
            ''', (asset_type, asset_name, value, person))
        db.commit()

class SavingsGoalModel:
    """Model for savings goal operations"""

    @staticmethod
    def create(db, goal_name, target_amount, target_date=None, priority=1, notes=None, initial_amount=0):
        """Create a new savings goal"""
        # Ensure the initial_amount column exists
        try:
            db.execute('ALTER TABLE savings_goals ADD COLUMN initial_amount REAL DEFAULT 0')
            db.commit()
        except:
            # Column already exists
            pass

        db.execute('''
            INSERT INTO savings_goals (goal_name, target_amount, target_date, priority, notes, initial_amount, current_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (goal_name, target_amount, target_date, priority, notes, initial_amount, initial_amount))
        db.commit()
        return db.cursor.lastrowid

    @staticmethod
    def get_all(db, include_completed=False):
        """Get all savings goals"""
        if include_completed:
            query = "SELECT * FROM savings_goals ORDER BY priority, goal_name"
        else:
            query = "SELECT * FROM savings_goals WHERE is_completed = 0 ORDER BY priority, goal_name"

        return db.execute(query).fetchall()

    @staticmethod
    def get_by_id(db, goal_id):
        """Get a savings goal by ID"""
        return db.execute('SELECT * FROM savings_goals WHERE id = ?', (goal_id,)).fetchone()

    @staticmethod
    def update(db, goal_id, goal_name, target_amount, target_date=None, priority=1, notes=None, initial_amount=None):
        """Update a savings goal"""
        if initial_amount is not None:
            db.execute('''
                UPDATE savings_goals 
                SET goal_name = ?, target_amount = ?, target_date = ?, priority = ?, notes = ?, initial_amount = ?
                WHERE id = ?
            ''', (goal_name, target_amount, target_date, priority, notes, initial_amount, goal_id))
        else:
            db.execute('''
                UPDATE savings_goals 
                SET goal_name = ?, target_amount = ?, target_date = ?, priority = ?, notes = ?
                WHERE id = ?
            ''', (goal_name, target_amount, target_date, priority, notes, goal_id))
        db.commit()

    @staticmethod
    def delete(db, goal_id):
        """Delete a savings goal and its allocations"""
        # Delete allocations first (foreign key constraint)
        db.execute('DELETE FROM savings_allocations WHERE goal_id = ?', (goal_id,))
        # Delete the goal
        db.execute('DELETE FROM savings_goals WHERE id = ?', (goal_id,))
        db.commit()

    @staticmethod
    def complete(db, goal_id):
        """Mark a savings goal as completed"""
        db.execute('''
            UPDATE savings_goals 
            SET is_completed = 1, completion_date = DATE('now'), status = 'completed'
            WHERE id = ?
        ''', (goal_id,))
        db.commit()
    
    @staticmethod
    def retire_goal(db, goal_id, status='retired'):
        """
        Feature 5: Retire a savings goal (mark as retired or abandoned)
        
        Args:
            goal_id: ID of the goal to retire
            status: 'retired' for abandoned goals, 'completed' for successfully reached goals
        """
        db.execute('''
            UPDATE savings_goals 
            SET status = ?, is_completed = 1, completion_date = DATE('now')
            WHERE id = ?
        ''', (status, goal_id))
        db.commit()
    
    @staticmethod
    def get_by_status(db, status=None):
        """
        Feature 5: Get savings goals filtered by status
        
        Args:
            status: 'active', 'completed', 'retired', or None for all
        
        Returns:
            List of goals matching the status filter
        """
        if status:
            # Ensure status column exists with default
            return db.execute('''
                SELECT * FROM savings_goals 
                WHERE COALESCE(status, 'active') = ?
                ORDER BY priority, goal_name
            ''', (status,)).fetchall()
        else:
            return db.execute('''
                SELECT * FROM savings_goals 
                ORDER BY priority, goal_name
            ''').fetchall()
    
    @staticmethod
    def get_active_goals(db):
        """Feature 5: Get only active (non-retired, non-completed) goals"""
        return db.execute('''
            SELECT * FROM savings_goals 
            WHERE COALESCE(status, 'active') = 'active' AND is_completed = 0
            ORDER BY priority, goal_name
        ''').fetchall()

    @staticmethod
    def clear_all(db):
        """Clear all savings goals and allocations"""
        try:
            # Get count before deletion
            cursor = db.execute("SELECT COUNT(*) as count FROM savings_goals")
            count = cursor.fetchone()['count']

            # Delete all allocations first (foreign key constraint)
            db.execute("DELETE FROM savings_allocations")

            # Delete all goals
            db.execute("DELETE FROM savings_goals")

            # Reset auto-increment counters
            db.execute("DELETE FROM sqlite_sequence WHERE name='savings_goals'")
            db.execute("DELETE FROM sqlite_sequence WHERE name='savings_allocations'")

            db.commit()
            return count
        except Exception as e:
            if db.conn:
                db.conn.rollback()
            raise e

class SavingsAllocationModel:
    """Model for savings allocation operations"""

    @staticmethod
    def create(db, goal_id, amount, date_str, notes=None):
        """Create a new savings allocation"""
        # Add allocation record
        db.execute('''
            INSERT INTO savings_allocations (goal_id, amount, date, notes)
            VALUES (?, ?, ?, ?)
        ''', (goal_id, amount, date_str, notes))

        # Update current amount in goals table
        db.execute('''
            UPDATE savings_goals 
            SET current_amount = current_amount + ?
            WHERE id = ?
        ''', (amount, goal_id))

        db.commit()
        return db.cursor.lastrowid

    @staticmethod
    def get_by_goal(db, goal_id):
        """Get all allocations for a specific goal"""
        return db.execute('''
            SELECT * FROM savings_allocations 
            WHERE goal_id = ?
            ORDER BY date DESC
        ''', (goal_id,)).fetchall()

    @staticmethod
    def get_by_month(db, year, month):
        """Get all allocations for a specific month"""
        return db.execute('''
            SELECT sa.*, sg.goal_name 
            FROM savings_allocations sa
            JOIN savings_goals sg ON sa.goal_id = sg.id
            WHERE strftime('%Y', sa.date) = ? AND strftime('%m', sa.date) = ?
            ORDER BY sa.date DESC
        ''', (str(year), f"{month:02d}")).fetchall()

    @staticmethod
    def get_total_by_month(db, year, month):
        """Get total allocations for a specific month"""
        result = db.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM savings_allocations
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ''', (str(year), f"{month:02d}")).fetchone()
        return result['total'] if result else 0

    @staticmethod
    def delete(db, allocation_id):
        """Delete an allocation and update goal current amount"""
        # Get allocation details first
        allocation = db.execute('''
            SELECT goal_id, amount FROM savings_allocations WHERE id = ?
        ''', (allocation_id,)).fetchone()

        if allocation:
            # Remove allocation
            db.execute('DELETE FROM savings_allocations WHERE id = ?', (allocation_id,))

            # Update goal current amount
            db.execute('''
                UPDATE savings_goals 
                SET current_amount = current_amount - ?
                WHERE id = ?
            ''', (allocation['amount'], allocation['goal_id']))

            db.commit()

class BudgetEstimateModel:
    """Model for budget estimate operations"""

    @staticmethod
    def save(db, category, subcategory, estimated_amount, year, month):
        """Save or update a budget estimate"""
        try:
            db.execute('''
                INSERT OR REPLACE INTO budget_estimates 
                (category, subcategory, estimated_amount, year, month, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (category, subcategory, estimated_amount, year, month))
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving budget estimate: {e}")
            return False

    @staticmethod
    def get_by_month(db, year, month):
        """Get all budget estimates for a specific month"""
        return db.execute('''
            SELECT * FROM budget_estimates
            WHERE year = ? AND month = ?
            ORDER BY category, subcategory
        ''', (year, month)).fetchall()

    @staticmethod
    def get_by_category(db, category, year, month):
        """Get budget estimates for a specific category and month"""
        return db.execute('''
            SELECT * FROM budget_estimates
            WHERE category = ? AND year = ? AND month = ?
            ORDER BY subcategory
        ''', (category, year, month)).fetchall()
    
    @staticmethod
    def save_with_default(db, category, subcategory, estimated_amount, year, month, is_default=False):
        """Save or update a budget estimate with default flag (Feature 4)"""
        try:
            db.execute('''
                INSERT OR REPLACE INTO budget_estimates 
                (category, subcategory, estimated_amount, year, month, is_default, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (category, subcategory, estimated_amount, year, month, 1 if is_default else 0))
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving budget estimate: {e}")
            return False
    
    @staticmethod
    def get_default_estimates(db):
        """Get all default budget estimates (Feature 4)"""
        return db.execute('''
            SELECT DISTINCT category, subcategory, estimated_amount
            FROM budget_estimates
            WHERE is_default = 1
            ORDER BY category, subcategory
        ''').fetchall()
    
    @staticmethod
    def apply_defaults_to_month(db, year, month):
        """
        Apply default estimates to a specific month if no estimates exist (Feature 4)
        Returns the number of estimates applied
        """
        # Check if month already has estimates
        existing = db.execute('''
            SELECT COUNT(*) as count FROM budget_estimates
            WHERE year = ? AND month = ?
        ''', (year, month)).fetchone()
        
        if existing and existing['count'] > 0:
            return 0  # Month already has estimates
        
        # Get default estimates
        defaults = BudgetEstimateModel.get_default_estimates(db)
        
        if not defaults:
            return 0
        
        # Apply defaults to the month
        count = 0
        for estimate in defaults:
            db.execute('''
                INSERT INTO budget_estimates 
                (category, subcategory, estimated_amount, year, month, is_default, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
            ''', (estimate['category'], estimate['subcategory'], estimate['estimated_amount'], year, month))
            count += 1
        
        db.commit()
        return count
    
    @staticmethod
    def copy_from_previous_month(db, year, month):
        """
        Copy estimates from the previous month (Feature 4)
        Returns the number of estimates copied
        """
        # Calculate previous month
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1
        
        # Get previous month's estimates
        prev_estimates = BudgetEstimateModel.get_by_month(db, prev_year, prev_month)
        
        if not prev_estimates:
            return 0
        
        # Copy to current month
        count = 0
        for estimate in prev_estimates:
            try:
                db.execute('''
                    INSERT OR REPLACE INTO budget_estimates 
                    (category, subcategory, estimated_amount, year, month, is_default, updated_at)
                    VALUES (?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
                ''', (estimate['category'], estimate['subcategory'], estimate['estimated_amount'], year, month))
                count += 1
            except:
                pass  # Skip duplicates
        
        db.commit()
        return count
