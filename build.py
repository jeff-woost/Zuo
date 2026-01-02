#!/usr/bin/env python3
"""
Build Script for Zuo Budget Tracker
===================================

This script builds Zuo into a standalone executable using PyInstaller.

Usage:
    python build.py

Requirements:
    - PyInstaller: pip install pyinstaller
    - All dependencies in requirements.txt must be installed
"""

import subprocess
import sys
import os

def main():
    """Build the application using PyInstaller"""
    print("=" * 60)
    print("Building Zuo Budget Tracker")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found")
        print("  Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    print()
    
    # Check if spec file exists
    spec_file = "Zuo.spec"
    if not os.path.exists(spec_file):
        print(f"✗ {spec_file} not found")
        print("  Please ensure Zuo.spec exists in the current directory")
        return 1
    
    print(f"✓ Found {spec_file}")
    print()
    
    # Build the application
    print("Building executable...")
    print("-" * 60)
    
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec_file, "--clean"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✓ Build completed successfully!")
        print("=" * 60)
        print()
        print("The executable can be found in the 'dist' directory:")
        
        if sys.platform == "win32":
            print("  dist/Zuo.exe")
        else:
            print("  dist/Zuo")
        
        return 0
    else:
        print()
        print("=" * 60)
        print("✗ Build failed")
        print("=" * 60)
        print()
        print("Please check the error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
