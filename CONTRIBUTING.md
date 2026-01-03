# Contributing to Zuo Budget Tracker

Thank you for your interest in contributing to Zuo! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/Zuo.git`
3. Add the upstream remote: `git remote add upstream https://github.com/jeff-woost/Zuo.git`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install development dependencies (if needed):
   ```bash
   pip install -r requirements_all.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
Zuo/
├── src/                # Core application code
│   ├── gui/           # User interface components
│   ├── database/      # Database layer
│   ├── config/        # Configuration management
│   └── app.py         # Main application window
├── scripts/           # Utility and migration scripts
│   ├── migrations/    # Database migration scripts
│   └── utilities/     # Debug and maintenance utilities
├── docs/              # Documentation
├── data/              # Data files
├── main.py            # Application entry point
└── build.py           # Build script
```

### Key Directories

- **src/gui/** - PyQt6 user interface components
  - `tabs/` - Main application tabs
  - `utils/` - Reusable UI utilities and dialogs
  - `views/` - Special views (onboarding, etc.)

- **src/database/** - Data access layer
  - `db_manager.py` - Database operations
  - `models.py` - Data models
  - `category_manager.py` - Category management

- **src/config/** - Application configuration
  - `__init__.py` - Settings and defaults loader
  - `defaults.json` - Default categories

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black formatter default)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

### File Naming

- Python modules: `snake_case.py`
- Python classes: `PascalCase` within files
- Documentation: `UPPER_CASE.md` or `Title_Case.md`

### Import Organization

Organize imports in the following order:
1. Standard library imports
2. Third-party library imports
3. Local application imports

Use absolute imports with the `src.` prefix for all src/ modules:

```python
from src.database.db_manager import DatabaseManager
from src.config import load_settings
```

### Documentation

- Add docstrings to all modules, classes, and public functions
- Use Google-style docstrings for consistency
- Keep comments concise and meaningful
- Update README.md for user-facing changes

Example:
```python
def calculate_budget_variance(income: float, expenses: float) -> float:
    """
    Calculate the variance between income and expenses.
    
    Args:
        income: Total income amount
        expenses: Total expenses amount
        
    Returns:
        Variance amount (positive means surplus, negative means deficit)
    """
    return income - expenses
```

## Making Changes

### Before You Start

1. Check existing issues to avoid duplicate work
2. Create an issue to discuss significant changes
3. Ensure your idea aligns with project goals

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow coding standards
   - Add comments where necessary
   - Update documentation

3. **Test your changes**
   - Test the application thoroughly
   - Verify all imports work
   - Check for syntax errors
   - Test edge cases

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   Commit message format:
   - Use present tense: "Add feature" not "Added feature"
   - Be descriptive but concise
   - Reference issues: "Fix #123: Description"

### Types of Changes

- **Features**: New functionality
- **Bug fixes**: Corrections to existing code
- **Refactoring**: Code improvements without behavior changes
- **Documentation**: README, docs, or code comments
- **Performance**: Speed or efficiency improvements

## Testing

### Manual Testing

1. **Test basic functionality**
   ```bash
   python main.py
   ```

2. **Test imports**
   ```bash
   python -c "from src.config import load_settings; print('OK')"
   ```

3. **Check Python syntax**
   ```bash
   python -m py_compile src/**/*.py
   ```

### Testing Checklist

- [ ] Application starts without errors
- [ ] All tabs load correctly
- [ ] Database operations work
- [ ] Import/export functions work
- [ ] No console errors
- [ ] UI is responsive
- [ ] Changes don't break existing features

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**
   - Go to the GitHub repository
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

### Pull Request Guidelines

**Title**: Use a clear, descriptive title
- Good: "Add CSV export for expenses"
- Bad: "Update files"

**Description**: Include:
- What changes were made and why
- How to test the changes
- Screenshots (for UI changes)
- Related issues (e.g., "Closes #123")

**Checklist**:
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Changes tested locally
- [ ] No new warnings or errors
- [ ] Commits are clear and organized

### After Submission

- Respond to review comments promptly
- Make requested changes if needed
- Be patient during the review process

## Database Migrations

When making database schema changes:

1. Create a migration script in `scripts/migrations/`
2. Document the migration in the script
3. Test on a backup database first
4. Include rollback instructions
5. Update the database schema documentation

## Questions?

- Check existing issues and documentation
- Open an issue for questions or clarifications
- Be specific about your environment and the problem

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Zuo Budget Tracker! 🎉
