/*
 * MaxManager - INI Editor for 3ds Max
 * Version: 1.1.1
 * Description: Graphical editor for 3dsmax.ini configuration file
 * Author: MaxManager
 * Created: 2025-10-17
 * Updated: 2025-10-22
 * GitHub: https://github.com/3dgopnik/MaxManager
 * Issue: #10 (closed)
 * 
 * Installation: Drag this .mcr file into 3ds Max viewport to register
 * Usage: Customize UI -> Toolbars -> Category: MaxManager -> MaxManager: INI Editor
 * 
 * Features v1.1.1:
 * - Custom Presets System (create, save, export/import)
 * - Real-time changes without 3ds Max restart
 * - Direct integration with 3ds Max API (pymxs.runtime)
 * - 8 main categories of settings
 * - Hot Reload System for development
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
        local scriptPath = getFilenamePath (getThisScriptFilename())
        local maxManagerPath = scriptPath + "..\\..\\icons\\"
        
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
        
        -- Copy icons (all sizes for different UI scales)
        local iconFiles = #("MaxManager_INIEditor_16.png", "MaxManager_INIEditor_24.png", "MaxManager_INIEditor_32.png", "MaxManager_INIEditor_48.png")
        
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
    
    -- Get script location dynamically
    local scriptPath = getFilenamePath (getThisScriptFilename())
    local maxManagerSrc = scriptPath + "..\\..\\src\\"
    
    -- Add MaxManager src to Python path
    python.Execute ("
import sys
from pathlib import Path

# Get script directory and find src folder
max_manager_path = r'" + maxManagerSrc + "'
max_manager_path = str(Path(max_manager_path).resolve())

if max_manager_path not in sys.path:
    sys.path.insert(0, max_manager_path)

print(f'MaxManager Python path: {max_manager_path}')
")
    
    -- Launch MaxINI Editor v1.1.1
    python.Execute "
from PySide6.QtWidgets import QApplication, QMessageBox
import qtmax

try:
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        print('Created new QApplication')
    
    # Launch MaxINI Editor v1.1.1
    print('Launching MaxManager INI Editor v1.1.1...')
    from ui.maxini_editor_advanced import AdvancedMaxINIEditor
    
    # Get Max main window for parenting
    try:
        max_window = qtmax.GetQMaxMainWindow()
        print('Got Max main window for parenting')
    except:
        max_window = None
        print('Could not get Max main window, using None')
    
    # Create and show editor
    editor = AdvancedMaxINIEditor(parent=max_window)
    editor.show()
    print('MaxManager INI Editor v1.1.1 launched successfully')
    
except Exception as e:
    print(f'ERROR: Failed to launch MaxINI Editor: {e}')
    import traceback
    traceback.print_exc()
    
    # Show error dialog
    QMessageBox.critical(
        None,
        'MaxManager - Error',
        f'Failed to launch INI Editor v1.1.1:\\n\\n{e}\\n\\nCheck MAXScript Listener for details.'
    )
"
    
    logMsg "MaxManager INI Editor v1.1.1 launch script finished"
    format "MaxManager INI Editor launched! Check MAXScript Listener for details.\n"
)
