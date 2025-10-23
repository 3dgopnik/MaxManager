/*
 * MaxManager - INI Editor for 3ds Max
 * Version: 1.8.0
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
 * Features v1.8.0:
 * - Modern Fluent Design UI with bright accents
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
        -- Get user icons directory (correct path from getDir #userIcons)
        userIconsPath = (getDir #userIcons)
        scriptPath = getFilenamePath (getThisScriptFilename())
        maxManagerIconsPath = scriptPath + "..\\..\\icons\\"
        
        logMsg ("Icons source: " + maxManagerIconsPath)
        logMsg ("Icons target: " + userIconsPath)
        
        -- Copy icons (all sizes for different UI scales)
        iconFiles = #("MaxManager_INIEditor_16.png", "MaxManager_INIEditor_24.png", "MaxManager_INIEditor_32.png", "MaxManager_INIEditor_48.png")
        
        for iconFile in iconFiles do (
            srcPath = maxManagerIconsPath + iconFile
            dstPath = userIconsPath + iconFile
            
            if doesFileExist srcPath then (
                if copyFile srcPath dstPath then
                    logMsg ("✓ Installed icon: " + iconFile)
                else
                    logMsg ("✗ Failed to install: " + iconFile)
            ) else (
                logMsg ("✗ Source not found: " + iconFile)
            )
        )
    )
    
    -- Icons are installed by the installer; skip here to avoid noisy logs
    -- installIcons()
    
    logMsg "=== Launching MaxINI Editor ==="
    
    -- Resolve src path from userScripts to avoid relative issues from startup folder
    local userScripts = getDir #userScripts
    local maxManagerRoot = pathConfig.appendPath userScripts "MaxManager"
    local maxManagerSrc = pathConfig.appendPath maxManagerRoot "src"
    local maxManagerSrcNoSlash = trimRight maxManagerSrc "\\/"
    
        -- Add MaxManager src to Python path
        python.Execute (
"import sys\nfrom pathlib import Path\n\nmax_manager_path = r'" + maxManagerSrcNoSlash + "'\nmax_manager_path = str(Path(max_manager_path).resolve())\n\nif max_manager_path not in sys.path:\n    sys.path.insert(0, max_manager_path)\n\nprint(f'MaxManager Python path: {max_manager_path}')\n")
    
    -- Launch MaxINI Editor v1.8.0
    python.Execute "
from PySide6.QtWidgets import QApplication, QMessageBox
import qtmax
import sys

try:
    # Get or create QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        print('Created new QApplication')
    
    # Launch MaxINI Editor v1.8.0
    print('Launching MaxManager INI Editor v1.8.0...')
    print('Using built-in PySide6, pymxs, and qtmax from 3ds Max')
    
    # Force reload MaxManager modules by clearing sys.modules cache
    modules_to_clear = [
        'ui.maxini_editor_advanced',
        'ui.modern_sidebar',
        'ui.modern_header',
        'modules.maxini_parser',
        'modules.maxini_backup', 
        'modules.maxini_presets',
        'modules.file_manager',
        'modules.kanban',
        'modules.module_manager',
        'modules.project_creator'
    ]
    
    cleared_count = 0
    for module in modules_to_clear:
        if sys.modules.pop(module, None) is not None:
            cleared_count += 1
    
    print(f'🔄 Cleared {cleared_count} cached modules from memory')
    
    # Now import fresh version
    from ui.maxini_editor_advanced import AdvancedMaxINIEditor
    
    # Get Max main window for parenting
    try:
        max_window = qtmax.GetQMaxMainWindow()
        print('✅ Got Max main window for parenting')
    except Exception:
        max_window = None
        print('⚠️ Could not get Max main window, using None')
    
    # Create editor with Max as parent
    editor = AdvancedMaxINIEditor(parent=max_window)
    editor.show()
    print('MaxManager INI Editor v1.8.0 launched successfully')
    
except Exception as e:
    print(f'ERROR: Failed to launch MaxINI Editor: {e}')
    import traceback
    traceback.print_exc()
    
    # Show error dialog
    QMessageBox.critical(
        None,
        'MaxManager - Error',
        f'Failed to launch INI Editor v1.8.0:\\n\\n{e}\\n\\nCheck MAXScript Listener for details.'
    )
"
    
    logMsg "MaxManager INI Editor v1.8.0 launch script finished"
    format "MaxManager INI Editor launched! Check MAXScript Listener for details.\n"
)
