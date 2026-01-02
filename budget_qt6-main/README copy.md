# Budget Tracker for Jeff & Vanessa

A comprehensive PyQt6-based budget tracking application designed for two-person household financial management.

## Features

- **Budget Overview**: Monthly income and expense synopsis
- **Net Worth Tracking**: Track investments, savings, and assets
- **Income & Expense Management**: Manual entry and bulk import capabilities
- **Monthly Presentations**: Visual breakdown of spending by category
- **Savings Goals**: Allocate surplus funds to savings targets
- **Trend Analysis**: Track spending patterns over time

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jeff-woost/budget_qt6.git
cd budget_qt6
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
budget_qt6/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── budget.db              # SQLite database (created on first run)
├── database/              # Database management
│   ├── __init__.py
│   ├── connection.py      # Database connection manager
│   └── models.py          # Database models and operations
├── tabs/                  # GUI tabs
│   ├── __init__.py
│   ├── overview_tab.py    # Budget overview
│   ├── net_worth_tab.py   # Net worth tracking
│   ├── budget_tab.py      # Income/expense entry
│   ├── presentation_tab.py # Monthly presentation
│   ├── savings_tab.py     # Savings goals
│   └── trends_tab.py      # Trend analysis
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── categories.py      # Category management
│   ├── importers.py       # CSV/TXT import functions
│   └── styles.py          # Application styling
└── resources/             # Resources (icons, sample data)
    └── sample_categories.csv
```

## Database Schema

The application uses SQLite with the following tables:
- `income`: Track income entries
- `expenses`: Track expense entries
- `net_worth`: Asset tracking
- `savings_goals`: Savings targets
- `savings_allocations`: Savings allocation history

## Contributing

Feel free to submit issues and pull requests.

## License

MIT License