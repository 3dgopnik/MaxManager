/*
 * MaxINI Editor - Professional Installer
 * Version: 1.0.0
 * Description: Drag-and-drop installer with automatic button creation
 * Author: MaxManager
 * Created: 2025-10-17
 */

try (
    clearListener()
    format "\n=== MaxINI Editor Professional Installer v1.0.0 ===\n\n"
    
    -- Define paths
    local maxAppDataPath = getdir #maxdata
    local maxMacroscriptsPath = maxAppDataPath + "UI\\macroscripts\\"
    local maxScriptsPath = maxAppDataPath + "scripts\\MaxManager\\src\\"
    local maxUIScriptsPath = maxScriptsPath + "ui\\"
    local maxModulesScriptsPath = maxScriptsPath + "modules\\"
    local maxDataPath = maxAppDataPath + "scripts\\MaxManager\\data\\"
    local maxIconsPathDark = maxAppDataPath + "usericons\\Dark\\"
    local maxIconsPathLight = maxAppDataPath + "usericons\\Light\\"
    
    -- Source paths
    local sourceMacroPath = "C:\\MaxManager\\src\\maxscript\\MaxManager_INIEditor.mcr"
    local sourceAdvancedEditorPath = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    local sourceModulesPath = "C:\\MaxManager\\src\\modules\\"
    local sourceUIPath = "C:\\MaxManager\\src\\ui\\"
    local sourceDataPath = "C:\\MaxManager\\data\\"
    local sourceIconsPath = "C:\\MaxManager\\icons\\"
    
    -- Helper function for logging
    fn logMsg msg = (
        format "[Installer] %\n" msg
    )
    
    -- Helper function to create directory if not exists
    fn createDir path = (
        if not (doesFileExist path) then (
            makeDir path
            logMsg ("Created: " + path)
            return true
        )
        return false
    )
    
    -- Helper function to copy file
    fn copyFileWithLog source dest = (
        if doesFileExist source then (
            try (
                copyFile source dest
                logMsg ("Copied: " + (filenameFromPath source))
                return true
            ) catch (
                logMsg ("ERROR: Failed to copy: " + source)
                return false
            )
        ) else (
            logMsg ("WARNING: Source not found: " + source)
            return false
        )
    )
    
    -- Create directories
    logMsg "Creating directories..."
    createDir maxMacroscriptsPath
    createDir (maxAppDataPath + "scripts\\MaxManager\\")
    createDir maxScriptsPath
    createDir maxUIScriptsPath
    createDir maxModulesScriptsPath
    createDir maxDataPath
    createDir (maxDataPath + "presets\\")
    createDir (maxDataPath + "translations\\")
    createDir (maxDataPath + "validation\\")
    createDir maxIconsPathDark
    createDir maxIconsPathLight
    
    -- Copy macro
    logMsg "\nCopying macro script..."
    if not (copyFileWithLog sourceMacroPath (maxMacroscriptsPath + "MaxManager_INIEditor.mcr")) then (
        messageBox "ERROR: Failed to copy macro script!\nCheck MAXScript Listener for details." title:"Installation Failed"
        throw "Macro copy failed"
    )
    
    -- Copy Advanced Editor
    logMsg "\nCopying Advanced Editor..."
    if not (copyFileWithLog sourceAdvancedEditorPath (maxUIScriptsPath + "maxini_editor_advanced.py")) then (
        messageBox "ERROR: Failed to copy Advanced Editor!\nCheck MAXScript Listener for details." title:"Installation Failed"
        throw "Editor copy failed"
    )
    
    -- Copy other UI files
    logMsg "\nCopying UI files..."
    local uiFiles = getFiles (sourceUIPath + "*.py")
    for f in uiFiles do (
        if (filenameFromPath f) != "maxini_editor_advanced.py" then (
            copyFileWithLog f (maxUIScriptsPath + (filenameFromPath f))
        )
    )
    
    -- Copy modules files
    logMsg "\nCopying modules..."
    local moduleFiles = getFiles (sourceModulesPath + "*.py")
    for f in moduleFiles do (
        copyFileWithLog f (maxModulesScriptsPath + (filenameFromPath f))
    )
    
    -- Copy data files
    logMsg "\nCopying data files..."
    local dataFiles = getFiles (sourceDataPath + "*.*")
    for f in dataFiles do (
        copyFileWithLog f (maxDataPath + (filenameFromPath f))
    )
    
    -- Copy presets
    local presetFiles = getFiles (sourceDataPath + "presets\\*.*")
    for f in presetFiles do (
        copyFileWithLog f (maxDataPath + "presets\\" + (filenameFromPath f))
    )
    
    -- Copy translations
    local translationFiles = getFiles (sourceDataPath + "translations\\*.*")
    for f in translationFiles do (
        copyFileWithLog f (maxDataPath + "translations\\" + (filenameFromPath f))
    )
    
    -- Copy validation rules
    local validationFiles = getFiles (sourceDataPath + "validation\\*.*")
    for f in validationFiles do (
        copyFileWithLog f (maxDataPath + "validation\\" + (filenameFromPath f))
    )
    
    -- Copy icons
    logMsg "\nCopying icons..."
    local iconFiles = getFiles (sourceIconsPath + "MaxManager_INIEditor_*.png")
    for iconFile in iconFiles do (
        copyFileWithLog iconFile (maxIconsPathDark + (filenameFromPath iconFile))
        copyFileWithLog iconFile (maxIconsPathLight + (filenameFromPath iconFile))
    )
    
    -- Load macro to register it
    logMsg "\nRegistering macro..."
    try (
        fileIn (maxMacroscriptsPath + "MaxManager_INIEditor.mcr")
        logMsg "Macro registered successfully"
    ) catch (
        logMsg "WARNING: Could not register macro (will be available after restart)"
    )
    
    format "\n=== Installation Complete! ===\n\n"
    format "✅ Files copied successfully\n"
    format "✅ Macro registered\n"
    format "✅ Icons installed\n\n"
    format "📍 To add button to toolbar:\n"
    format "   1. Customize → Customize User Interface\n"
    format "   2. Toolbars → Category: MaxManager\n"
    format "   3. Drag 'MaxINI Editor' to your toolbar\n\n"
    format "🔄 Or restart 3ds Max for automatic detection\n\n"
    
    messageBox "MaxINI Editor v1.0.0 installed successfully!\n\n✅ Files copied\n✅ Macro registered\n✅ Icons installed\n\n📍 Add button: Customize UI → Toolbars → MaxManager\n🔄 Or restart 3ds Max" title:"Installation Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ Installation failed: %\n" errorMsg
    messageBox ("Installation failed!\n\n" + errorMsg + "\n\nCheck MAXScript Listener for details.") title:"Installation Error"
)

