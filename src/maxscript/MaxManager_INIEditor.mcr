/*
 * MaxManager INI Editor - MacroScript
 * Version: 1.0.0 (Advanced Editor)
 * Description: Graphical editor for 3ds Max configuration file (max.ini)
 * Author: MaxManager
 * Created: 2025-10-17
 * Updated: 2025-10-17
 * GitHub Issue: #10
 * 
 * Installation: Drag this .mcr file into 3ds Max viewport to register
 * Usage: Customize UI -> Toolbars -> Category: MaxManager -> MaxManager: INI Editor
 * 
 * Features v0.2.0:
 * - Editable widgets (QSpinBox, QCheckBox, QLineEdit, Path browser)
 * - Real-time validation
 * - Installation GUI with versioning
 * - Automatic icon installation
 */

macroScript MaxManager_INIEditor
category:"MaxManager"
buttonText:"INI Editor"
toolTip:"Edit max.ini with GUI - Safe editing with validation and backups"
iconName:"MaxManager_INIEditor"
(
    -- Log messages to MAXScript Listener
    fn logMsg msg = (
        local timestamp = localTime as string
        format "[%] MaxINI Editor: %\n" timestamp msg
    )
    
    -- Install icons automatically
    fn installIcons = (
        local userIconsPath = (getDir #userIcons)
        local maxManagerPath = "C:\\MaxManager\\icons\\"
        
        -- Create directories if they don't exist
        local darkPath = userIconsPath + "Dark\\"
        local lightPath = userIconsPath + "Light\\"
        
        if not doesFileExist darkPath do (
            makeDir darkPath all:true
            logMsg "Created Dark icons directory"
        )
        
        if not doesFileExist lightPath do (
            makeDir lightPath all:true
            logMsg "Created Light icons directory"
        )
        
        -- Copy icons
        local iconFiles = #("MaxManager_INIEditor_24.png", "MaxManager_INIEditor_48.png")
        
        for iconFile in iconFiles do (
            local srcPath = "C:\\MaxManager\\icons\\" + iconFile
            
            if doesFileExist srcPath do (
                -- Copy to Dark theme
                local darkDest = darkPath + iconFile
                if copyFile srcPath darkDest then
                    logMsg ("Installed Dark icon: " + iconFile)
                else
                    logMsg ("Failed to install Dark icon: " + iconFile)
                
                -- Copy to Light theme
                local lightDest = lightPath + iconFile
                if copyFile srcPath lightDest then
                    logMsg ("Installed Light icon: " + iconFile)
                else
                    logMsg ("Failed to install Light icon: " + iconFile)
            )
        )
    )
    
    -- Install icons on first run
    installIcons()
    
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
    
    -- Launch Modern MaxINI Editor
    python.Execute "
from PySide6.QtWidgets import QApplication
import qtmax

try:
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        print('Created new QApplication')
    
    # Try Advanced editor first
    print('Attempting to launch Advanced MaxINI Editor v1.0.0...')
    from ui.maxini_editor_advanced import AdvancedMaxINIEditor
    
    # Get Max main window for parenting
    try:
        max_window = qtmax.GetQMaxMainWindow()
        print('Got Max main window for parenting')
    except:
        max_window = None
        print('Could not get Max main window, using None')
    
    editor = AdvancedMaxINIEditor(parent=max_window)
    editor.show()
    print('Advanced MaxINI Editor v1.0.0 launched successfully')
    
except Exception as e:
    print(f'Advanced editor failed: {e}')
    try:
        # Fallback to classic editor
        from ui.maxini_editor_window import MaxINIEditorWindow
        
        # Get Max main window for parenting
        try:
            max_window = qtmax.GetQMaxMainWindow()
        except:
            max_window = None
        
        editor = MaxINIEditorWindow(parent=max_window)
        editor.show()
        print('MaxINI Editor Classic launched (fallback)')
        
    except Exception as e2:
        print(f'Classic editor failed: {e2}')
        try:
            # Final fallback to installer
            from ui.maxini_installer import launch_installer
            installer = launch_installer()
            print('MaxINI Editor Installer launched (final fallback)')
            
        except Exception as e3:
            print(f'All launch methods failed: {e3}')
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                'MaxINI Editor Error',
                f'Failed to launch any editor:\\n\\n{e}\\n\\n{e2}\\n\\n{e3}'
            )
"
    
    logMsg "Advanced MaxINI Editor v1.0.0 launch script finished"
    format "Advanced MaxINI Editor v1.0.0 launched! Check MAXScript Listener for details.\n"
)
