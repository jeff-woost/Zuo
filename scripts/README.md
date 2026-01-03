# Scripts Directory

This directory contains utility scripts and database migrations for the Zuo Budget Tracker application.

## Directory Structure

```
scripts/
├── migrations/      # Database migration scripts
├── utilities/       # Debug and utility scripts
└── README.md        # This file
```

## Migrations

Database migration scripts in `migrations/` are used to upgrade the database schema as new features are added. These scripts should be run when:
- Upgrading from an older version of the application
- Adding new features that require database changes
- Fixing database schema issues

### Available Migrations

- `database_migration.py` - Main migration script for major feature additions
- `add_comment_column.py` - Adds comment column to bank_transactions table
- `fix_comment_column.py` - Fixes comment column issues
- `fix_savings_schema.py` - Updates savings goals schema
- `migrate_column_names.py` - Migrates legacy column names
- `fix_savings_goals_comprehensive.py` - Comprehensive savings goals fixes
- `setup_bank_reconciliation.py` - Sets up bank reconciliation features

### Running Migrations

```bash
# From the project root directory
cd /path/to/Zuo
python scripts/migrations/database_migration.py
```

**Important**: Always backup your database before running migrations!

```bash
cp budget_tracker.db budget_tracker_backup_$(date +%Y%m%d).db
```

## Utilities

Utility scripts in `utilities/` are used for debugging, testing, and maintenance tasks.

### Available Utilities

- `check_bank_transactions.py` - Verify bank transaction imports
- `clear_all_expenses.py` - Remove all expense records (use with caution!)
- `clear_expenses_and_fix.py` - Clear expenses and fix related issues
- `debug_savings_goals.py` - Debug savings goals functionality
- `debug_stuck_expense.py` - Debug stuck expense issues
- `verify_trends.py` - Verify trends calculation accuracy
- `budget_vs_actual_methods.py` - Test budget vs actual calculations
- `fix_savings_comprehensive.py` - Comprehensive savings fixes

### Running Utilities

```bash
# From the project root directory
cd /path/to/Zuo
python scripts/utilities/<script_name>.py
```

## Safety Guidelines

1. **Always backup your database** before running any migration or utility script
2. **Read the script documentation** to understand what it does
3. **Test on a copy** of your database first if possible
4. **Run scripts from the project root** to ensure correct paths
5. **Check for errors** in the script output

## Development

When creating new scripts:

1. **Migrations**: Add to `migrations/` directory
   - Include clear documentation of changes
   - Add error handling and rollback capabilities
   - Test thoroughly on sample databases

2. **Utilities**: Add to `utilities/` directory
   - Add usage documentation at the top of the file
   - Include safety checks (e.g., confirmation prompts)
   - Log all actions performed

## Getting Help

If you encounter issues with scripts:

1. Check the script's internal documentation
2. Ensure you're running from the correct directory
3. Verify your database file path
4. Check console output for error messages
5. Restore from backup if needed
