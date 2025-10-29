/*
 * MaxManager - INI Editor for 3ds Max
 * Version: 0.6.0
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
 * Features v0.6.0:
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
        format "[%] MaxManager: %\n" timestamp msg
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
    
    logMsg "=== Launching MaxManager ==="
    
    -- Resolve src path from userScripts to avoid relative issues from startup folder
    local userScripts = getDir #userScripts
    local maxManagerRoot = pathConfig.appendPath userScripts "MaxManager"
    local maxManagerSrc = pathConfig.appendPath maxManagerRoot "src"
    local maxManagerSrcNoSlash = trimRight maxManagerSrc "\\/"
    
        -- Add MaxManager src to Python path and read version
        python.Execute (
"import sys\nfrom pathlib import Path\n\nmax_manager_path = r'" + maxManagerSrcNoSlash + "'\nmax_manager_path = str(Path(max_manager_path).resolve())\n\nif max_manager_path not in sys.path:\n    sys.path.insert(0, max_manager_path)\n\nprint(f'MaxManager Python path: {max_manager_path}')\n\n# Read version from __version__.py\ntry:\n    from __version__ import __version__\n    globals()['MAXMANAGER_VERSION'] = __version__\nexcept:\n    globals()['MAXMANAGER_VERSION'] = 'unknown'\n")
    
    -- Launch MaxManager (version read from __version__.py)
    python.Execute "
from PySide6.QtWidgets import QApplication, QMessageBox
import qtmax
import sys
from pathlib import Path

try:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    ver = MAXMANAGER_VERSION if 'MAXMANAGER_VERSION' in dir() else 'unknown'
    print(f'Launching MaxManager Canvas Test v.{ver}...')
    
    # Clear ALL MaxManager modules from cache
    modules_to_clear = [
        m for m in list(sys.modules.keys()) 
        if any(x in m for x in ['MaxManager', 'test_canvas', 'collapsible_canvas', 'ini_parameter', 'i18n', 'modern_sidebar', 'modern_header', 'toggle_switch', 'parameter_info', 'name_formatter', 'parameter_filter', 'ini_manager', 'maxini_parser'])
    ]
    for m in modules_to_clear:
        del sys.modules[m]
    print(f'Cleared {len(modules_to_clear)} cached modules')
    
    # Import canvas main window
    from ui.canvas_main_window import CanvasMainWindow
    
    # Get Max main window
    try:
        max_window = qtmax.GetQMaxMainWindow()
    except:
        max_window = None
    
    # Create window
    window = CanvasMainWindow()
    if max_window:
        window.setParent(max_window, window.windowFlags())
    window.show()
    
    print('Canvas Test launched!')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
    QMessageBox.critical(None, 'Error', f'Failed to launch:\\n\\n{e}')
"
    
    -- Read version from __version__.py file
    local versionFile = pathConfig.appendPath maxManagerSrc "__version__.py"
    local mmVersion = "unknown"
    if doesFileExist versionFile do (
        local f = openFile versionFile mode:"r"
        if f != undefined do (
            while not eof f do (
                local line = readLine f
                if matchPattern line pattern:"__version__*=*\"*\"*" do (
                    -- Extract version between quotes
                    local startQuote = findString line "\""
                    if startQuote != undefined do (
                        local endQuote = findString line "\"" startPos:(startQuote + 1)
                        if endQuote != undefined do (
                            mmVersion = substring line (startQuote + 1) (endQuote - startQuote - 1)
                        )
                    )
                )
            )
            close f
        )
    )
    
    logMsg ("MaxManager v." + mmVersion + " launch script finished")
    format "MaxManager launched! Check MAXScript Listener for details.\n"
)
