"""
Configuration Module
===================

This module handles application configuration including:
- Default categories and subcategories
- User settings and preferences
- Database configuration
"""

import json
import os
from typing import Dict, Any, Optional

# Get the directory where this config module is located
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULTS_FILE = os.path.join(CONFIG_DIR, "defaults.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")


def load_defaults() -> Dict[str, Any]:
    """
    Load default categories and settings from defaults.json.
    
    Returns:
        Dict containing default categories and other default settings
    """
    if not os.path.exists(DEFAULTS_FILE):
        return {"categories": {}}
    
    try:
        with open(DEFAULTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading defaults: {e}")
        return {"categories": {}}


def load_settings() -> Dict[str, Any]:
    """
    Load user settings from settings.json.
    
    Returns:
        Dict containing user settings, or default settings if file doesn't exist
    """
    if not os.path.exists(SETTINGS_FILE):
        return {
            "user_a_name": "",
            "user_b_name": "",
            "database_path": "budget_tracker.db",
            "theme": "modern-fintech",
            "onboarding_completed": False
        }
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {
            "user_a_name": "",
            "user_b_name": "",
            "database_path": "budget_tracker.db",
            "theme": "modern-fintech",
            "onboarding_completed": False
        }


def save_settings(settings: Dict[str, Any]) -> bool:
    """
    Save user settings to settings.json.
    
    Args:
        settings: Dictionary containing user settings to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def get_user_names() -> tuple[str, str]:
    """
    Get user names from settings.
    
    Returns:
        Tuple of (user_a_name, user_b_name)
    """
    settings = load_settings()
    user_a = settings.get("user_a_name", "User A")
    user_b = settings.get("user_b_name", "User B")
    
    # Use defaults if not set
    if not user_a:
        user_a = "User A"
    if not user_b:
        user_b = "User B"
        
    return user_a, user_b
