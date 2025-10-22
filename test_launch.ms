/*
 * Test Launch Script
 * Simple test to check if MaxManager can launch
 */

-- Test script
fn logMsg msg = (
    timestamp = localTime as string
    format "[%] Test: %\n" timestamp msg
)

logMsg "Starting MaxManager test..."

-- Add MaxManager src to Python path
maxManagerPath = "C:\\MaxManager\\src"
python.Execute ("
import sys
from pathlib import Path

# Add MaxManager to path
max_manager_path = r'" + maxManagerPath + "'
if max_manager_path not in sys.path:
    sys.path.insert(0, max_manager_path)

print(f'Python path updated: {max_manager_path}')
")

-- Test import
python.Execute "
try:
    print('Testing imports...')
    from ui.maxini_editor_advanced import AdvancedMaxINIEditor
    print('✓ AdvancedMaxINIEditor imported successfully')
    
    from PySide6.QtWidgets import QApplication
    print('✓ PySide6 imported successfully')
    
    import qtmax
    print('✓ qtmax imported successfully')
    
    print('All imports successful!')
    
except Exception as e:
    print(f'Import failed: {e}')
    import traceback
    traceback.print_exc()
"

logMsg "Test completed"

