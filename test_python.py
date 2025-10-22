#!/usr/bin/env python3
"""
Test script to check MaxManager imports
"""

import sys
from pathlib import Path

# Add MaxManager to path
max_manager_path = r"C:\MaxManager\src"
if max_manager_path not in sys.path:
    sys.path.insert(0, max_manager_path)

print(f"Python path: {sys.path[:3]}")

try:
    print("Testing imports...")
    
    # Test PySide6
    from PySide6.QtWidgets import QApplication
    print("+ PySide6 imported successfully")
    
    # Test MaxManager modules
    from ui.maxini_editor_advanced import AdvancedMaxINIEditor
    print("+ AdvancedMaxINIEditor imported successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
