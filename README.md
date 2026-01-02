# Budget Tracker Application

A comprehensive PyQt6-based personal budget management application designed for Jeff & Vanessa to track income, expenses, net worth, and savings goals with a professional, user-friendly interface.

## Features

### 📊 Budget Overview
- Monthly synopsis of income and expenses
- Real-time budget health indicators
- Top spending categories analysis
- Savings rate calculations
- Quick statistics and projections

### 💰 Net Worth Tracking
- Track multiple asset types (Real Estate, 401k, IRA, HSA, etc.)
- Support for joint and individual accounts
- Historical net worth progression
- Asset categorization and notes
- Liability tracking (negative values)

### 📝 Budget Management
- **Income Tracking**: Separate income entry for Jeff and Vanessa
- **Expense Tracking**: 
  - Manual expense entry with predefined categories
  - Bulk import from credit card statements
  - Support for .txt and .csv file imports
  - Comprehensive category system with subcategories

### 📈 Monthly Presentation
- Detailed spending breakdown by category and subcategory
- Budget vs. actual comparisons
- Visual spending analysis
- Person-specific expense tracking

### 🎯 Savings Goals
- Create and track multiple savings goals
- Automatic allocation of leftover monthly income
- Progress tracking over time
- Priority-based goal management
- Individual spending summaries for joint account withdrawals

### 📉 Trends Analysis
- Long-term spending pattern analysis
- Monthly and yearly trend visualization
- Category-wise spending trends
- Income vs. expense progression

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the application files**
   ```bash
   # If using git
   git clone <repository-url>
   cd budget-tracker
   
   # Or download and extract the files to a folder
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python budget_app.py
   ```

## Application Structure

```
budget-tracker/
├── budget_app.py              # Main application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── budget_tracker.db         # SQLite database (created on first run)
├── database/
│   └── db_manager.py         # Database management
├── gui/
│   ├── main_window.py        # Main application window
│   └── tabs/
│       ├── overview_tab.py   # Budget overview tab
│       ├── net_worth_tab.py  # Net worth tracking tab
│       ├── budget_tab.py     # Budget management tab
│       ├── presentation_tab.py # Monthly presentation tab
│       ├── savings_tab.py    # Savings goals tab
│       └── trends_tab.py     # Trends analysis tab
└── categories.csv            # Predefined expense categories
```

## Usage Guide

### First Time Setup

1. **Launch the application**
   ```bash
   python budget_app.py
   ```

2. **The application will automatically:**
   - Create a SQLite database (`budget_tracker.db`)
   - Load predefined expense categories from the included CSV
   - Initialize all necessary database tables

### Adding Income

1. Navigate to the **Budget** tab
2. Select the **Income** sub-tab
3. Choose the person (Jeff or Vanessa)
4. Enter the income amount and date
5. Add optional description
6. Click "Add Income"

### Adding Expenses

**Manual Entry:**
1. Navigate to the **Budget** tab
2. Select the **Expenses** sub-tab
3. Fill in the expense details:
   - Person (Jeff or Vanessa)
   - Amount
   - Date
   - Category and subcategory
   - Description and payment method
4. Click "Add Expense"

**Bulk Import:**
1. Navigate to the **Budget** tab → **Expenses** sub-tab
2. Click "Import from File"
3. Select your CSV or TXT file with transaction data
4. Map the columns to the appropriate fields
5. Review and confirm the import

### Tracking Net Worth

1. Navigate to the **Net Worth** tab
2. Add assets by filling out the form:
   - Select person (Jeff, Vanessa, or Joint)
   - Choose asset type
   - Enter asset name and current value
   - Add notes if needed
3. Click "Add/Update Asset"
4. View real-time net worth calculations

### Setting Savings Goals

1. Navigate to the **Savings Goals** tab
2. Create new goals with:
   - Goal name and target amount
   - Target date and priority
3. Allocate monthly surplus to goals
4. Track progress over time

### Viewing Reports

- **Overview Tab**: Monthly summary and key metrics
- **Monthly Presentation**: Detailed category breakdowns
- **Trends Tab**: Long-term analysis and patterns

## Database Schema

The application uses SQLite with the following main tables:

- `income`: Income tracking for both persons
- `expenses`: Detailed expense records with categories
- `net_worth_assets`: Asset and liability tracking
- `savings_goals`: Savings goal definitions
- `savings_allocations`: Money allocated to goals
- `budget_targets`: Monthly budget targets
- `categories`: Expense categories and subcategories

## Predefined Categories

The application includes comprehensive expense categories:

- **Housing**: Mortgage, HOA, Property Taxes, etc.
- **Utilities**: Electric, Gas, Internet, Phone, Insurance
- **Food**: Groceries, Dining Out, Take Out, etc.
- **Healthcare**: Doctor visits, Prescriptions, etc.
- **Childcare**: Classes, Clothing, Activities, etc.
- **Vehicles**: Gas, Maintenance, Insurance, etc.
- **Home**: Necessities, Décor, Tools, etc.
- **Other**: Gifts, Donations, Entertainment, etc.
- **Vacation**: Travel, Accommodation, Activities, etc.

## Customization

### Adding New Categories
1. Open the **Budget** tab
2. Use the category management features to add new categories
3. Or directly modify the `categories` table in the database

### Modifying the Interface
The application uses PyQt6 with a professional dark theme. Styles can be modified in the respective tab files.

## Data Backup

**Important**: Regularly backup your `budget_tracker.db` file to prevent data loss.

```bash
# Create a backup
cp budget_tracker.db budget_tracker_backup_$(date +%Y%m%d).db
```

## Troubleshooting

### Common Issues

1. **Application won't start**
   - Ensure Python 3.8+ is installed
   - Verify all requirements are installed: `pip install -r requirements.txt`

2. **Database errors**
   - Check file permissions in the application directory
   - Ensure SQLite is available (included with Python)

3. **Import issues**
   - Verify CSV/TXT file format
   - Check for proper column headers
   - Ensure date formats are consistent

### Error Logs
The application prints error messages to the console. Run from terminal to see detailed error information.

## Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing
```bash
# Install testing dependencies
pip install pytest pytest-qt

# Run tests
pytest
```

## License

This application is developed for personal use by Jeff & Vanessa. All rights reserved.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in the console
3. Verify all requirements are properly installed
4. Check database file permissions

## Version History

- **v1.0.0**: Initial release with all core features
  - Budget overview and tracking
  - Net worth management
  - Savings goals
  - Trend analysis
  - Professional dark theme UI

---

**Happy Budgeting! 💰📊**