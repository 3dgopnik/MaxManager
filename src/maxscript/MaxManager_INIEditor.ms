/*
 * MaxManager INI Editor
 * Version: 0.1.0 (MVP Development)
 * Description: Graphical editor for 3ds Max configuration file (max.ini)
 * Author: MaxManager
 * Created: 2025-10-17
 * GitHub Issue: #10
 */

macroScript MaxManager_INIEditor
category:"MaxManager"
buttonText:"INI Editor"
toolTip:"Edit max.ini with GUI - Safe editing with validation and backups"
icon:#("MaxManager", 1)
(
    -- Log messages to MAXScript Listener
    fn logMsg msg = (
        local timestamp = localTime as string
        format "[%] MaxINI Editor: %\n" timestamp msg
    )
    
    logMsg "=== Launching MaxINI Editor ==="
    
    -- Add MaxManager src to Python path
    local maxManagerPath = "C:\\MaxManager\\src"
    python.Execute ("
import sys
from pathlib import Path

# Add MaxManager to path
max_manager_path = r'" + maxManagerPath + "'
if max_manager_path not in sys.path:
    sys.path.insert(0, max_manager_path)

print(f'Python path updated: {max_manager_path}')
")
    
    -- Launch Qt GUI
    python.Execute "
from PySide6.QtWidgets import QApplication
import qtmax
from ui.maxini_editor_window import MaxINIEditorWindow

try:
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        print('Created new QApplication')
    
    # Get Max main window for proper parenting
    try:
        max_window = qtmax.GetQMaxMainWindow()
        print('Got Max main window via qtmax')
    except Exception as e:
        print(f'qtmax not available: {e}')
        max_window = None
    
    # Disable Max accelerators when Qt window has focus
    # This prevents keyboard shortcuts from conflicting
    
    # Create and show editor
    editor = MaxINIEditorWindow(parent=max_window)
    
    # Disable Max hotkeys when editor has focus
    if max_window:
        try:
            qtmax.DisableMaxAcceleratorsOnFocus(editor, True)
            print('Disabled Max accelerators for editor window')
        except:
            pass  # Not critical if this fails
    
    editor.show()
    
    print('MaxINI Editor window launched successfully')
    print(f'Window title: {editor.windowTitle()}')
    
except Exception as e:
    print(f'ERROR launching MaxINI Editor: {e}')
    import traceback
    traceback.print_exc()
    
    # Show error dialog
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.critical(
        None,
        'MaxINI Editor Error',
        f'Failed to launch editor:\\n\\n{e}'
    )
"
    
    logMsg "MaxINI Editor launch script finished"
    format "To close editor, use the Close button in the Qt window\n"
)

