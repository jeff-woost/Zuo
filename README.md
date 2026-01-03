# Zuo - Budget Tracker Application

A comprehensive PyQt6-based personal budget management application for tracking income, expenses, net worth, and savings goals with a professional, user-friendly interface.

## ✨ Features

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
- **Income Tracking**: Separate income entry for multiple users
- **Expense Tracking**: 
  - Manual expense entry with predefined categories
  - Bulk import from credit card statements
  - Support for .txt and .csv file imports
  - Comprehensive category system with subcategories

### 🏦 Bank Reconciliation
- Import bank transactions from CSV/TXT files
- Reconcile transactions with expenses
- Track account balances
- Prevent duplicate entries

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

### 📉 Trends Analysis
- Long-term spending pattern analysis
- Monthly and yearly trend visualization
- Category-wise spending trends
- Income vs. expense progression

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/jeff-woost/Zuo.git
   cd Zuo
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
Zuo/
├── src/                      # Core application source code
│   ├── gui/                 # User interface components
│   │   ├── tabs/           # Application tabs (overview, budget, trends, etc.)
│   │   ├── utils/          # UI utilities and dialogs
│   │   └── views/          # Special views (onboarding, etc.)
│   ├── database/           # Database layer
│   │   ├── db_manager.py   # Main database operations
│   │   ├── models.py       # Data models
│   │   ├── category_manager.py  # Category management
│   │   └── connection.py   # Database connection handling
│   ├── config/             # Configuration management
│   │   ├── __init__.py     # Config loader and settings
│   │   └── defaults.json   # Default categories and settings
│   └── app.py              # Main application window
├── scripts/                # Utility and migration scripts
│   ├── migrations/         # Database migration scripts
│   ├── utilities/          # Debug and maintenance utilities
│   └── README.md           # Scripts documentation
├── docs/                   # Development documentation
│   ├── FEATURES_IMPLEMENTED.md
│   ├── ISSUES_FIXED.md
│   ├── REFACTORING_SUMMARY.md
│   └── README.md
├── data/                   # Data files
│   └── categories.csv      # Default expense categories
├── main.py                 # Application entry point
├── build.py                # Build script for creating executables
├── Zuo.spec                # PyInstaller build specification
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 💻 Usage

### Running the Application

```bash
# From the project root directory
python main.py
```

### First Time Setup

1. The application will launch an onboarding wizard
2. Enter user names for the two primary users
3. Configure initial settings
4. The application will automatically:
   - Create a SQLite database (`budget_tracker.db`)
   - Load predefined expense categories
   - Initialize all necessary database tables

### Adding Income

1. Navigate to the **Budget** tab
2. Select the **Income** sub-tab
3. Choose the person
4. Enter the income amount and date
5. Add optional description
6. Click "Add Income"

### Adding Expenses

**Manual Entry:**
1. Navigate to the **Budget** tab → **Expenses** sub-tab
2. Fill in expense details (person, amount, date, category)
3. Click "Add Expense"

**Bulk Import:**
1. Go to **Budget** tab → **Expenses** sub-tab
2. Click "Import from File"
3. Select your CSV or TXT file
4. Map columns and confirm

### Tracking Net Worth

1. Navigate to the **Net Worth** tab
2. Add assets with type, value, and ownership
3. Track changes over time

### Setting Savings Goals

1. Navigate to the **Savings Goals** tab
2. Create goals with target amounts and dates
3. Allocate monthly surplus to goals

## 🔧 Building from Source

### Creating a Standalone Executable

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Run the build script
python build.py
```

The executable will be created in the `dist/` directory:
- Windows: `dist/Zuo.exe`
- macOS: `dist/Zuo.app`
- Linux: `dist/Zuo`

### Build Requirements

- All dependencies from `requirements.txt`
- PyInstaller (`pip install pyinstaller`)

## 🗄️ Database

The application uses SQLite with the following main tables:

- `income` - Income tracking
- `expenses` - Expense records with categories
- `net_worth_assets` - Asset and liability tracking
- `savings_goals` - Savings goal definitions
- `savings_allocations` - Money allocated to goals
- `budget_estimates` - Monthly budget targets
- `categories` - Expense categorization system
- `bank_transactions` - Bank transaction imports

**Important**: Regularly backup your `budget_tracker.db` file!

```bash
# Create a backup
cp budget_tracker.db budget_tracker_backup_$(date +%Y%m%d).db
```

## 🛠️ Development

### Running Database Migrations

```bash
# From project root
python scripts/migrations/database_migration.py
```

See [scripts/README.md](scripts/README.md) for more details on available scripts.

### Code Organization

- **src/gui/** - All UI components using PyQt6
- **src/database/** - Data access layer and models
- **src/config/** - Configuration and settings management
- **scripts/** - Standalone scripts for maintenance and migrations
- **docs/** - Development documentation and history

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🐛 Troubleshooting

### Application Won't Start
- Ensure Python 3.8+ is installed: `python --version`
- Verify all dependencies: `pip install -r requirements.txt`
- Check for error messages in the console

### Database Errors
- Verify file permissions in the application directory
- Ensure SQLite is available (included with Python)
- Check if database file is locked by another process

### Import Issues
- Verify CSV/TXT file format
- Check for proper column headers
- Ensure date formats are consistent

### Build Issues
- Ensure PyInstaller is installed: `pip install pyinstaller`
- Check that all files in `src/` are accessible
- Verify `Zuo.spec` is present and correct

## 📊 Category System

The application includes comprehensive expense categories:

- **Housing**: Mortgage, HOA, Property Taxes, Insurance, etc.
- **Utilities**: Electric, Gas, Internet, Phone, Insurance
- **Food**: Groceries, Dining Out, Take Out, etc.
- **Healthcare**: Doctor visits, Prescriptions, etc.
- **Childcare**: Classes, Clothing, Activities, etc.
- **Vehicles**: Gas, Maintenance, Insurance, etc.
- **Home**: Necessities, Décor, Tools, etc.
- **Other**: Gifts, Donations, Entertainment, etc.
- **Vacation**: Travel, Accommodation, Activities, etc.

Categories can be customized through the application interface.

## 📝 License

This application is developed for personal use. All rights reserved.

## 🙏 Acknowledgments

- Built with PyQt6 for the user interface
- Uses SQLite for data persistence
- Pandas for data import and analysis
- PyQt6-Charts for visualizations

---

**Happy Budgeting! 💰📊**

For development history and detailed feature documentation, see the [docs/](docs/) directory.
