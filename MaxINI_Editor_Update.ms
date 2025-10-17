/*
 * MaxINI Editor - Updater
 * Version: 1.0.0
 * Description: Updates MaxINI Editor files without reinstallation
 * Author: MaxManager
 * Created: 2025-10-17
 */

try (
    clearListener()
    format "\n=== MaxINI Editor Updater v1.0.0 ===\n\n"
    
    -- Define paths
    local maxAppDataPath = getdir #maxdata
    local maxMacroscriptsPath = maxAppDataPath + "UI\\macroscripts\\"
    local maxScriptsPath = maxAppDataPath + "scripts\\MaxManager\\src\\"
    local maxUIScriptsPath = maxScriptsPath + "ui\\"
    
    -- Source paths
    local sourceMacroPath = "C:\\MaxManager\\src\\maxscript\\MaxManager_INIEditor.mcr"
    local sourceAdvancedEditorPath = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    
    -- Helper function
    fn logMsg msg = (
        format "[Updater] %\n" msg
    )
    
    -- Update macro
    logMsg "Updating macro script..."
    if doesFileExist sourceMacroPath then (
        copyFile sourceMacroPath (maxMacroscriptsPath + "MaxManager_INIEditor.mcr")
        logMsg "Macro updated"
    ) else (
        logMsg "ERROR: Macro source not found"
        throw "Update failed"
    )
    
    -- Update Advanced Editor
    logMsg "Updating Advanced Editor..."
    if doesFileExist sourceAdvancedEditorPath then (
        copyFile sourceAdvancedEditorPath (maxUIScriptsPath + "maxini_editor_advanced.py")
        logMsg "Advanced Editor updated"
    ) else (
        logMsg "ERROR: Editor source not found"
        throw "Update failed"
    )
    
    -- Reload macro
    logMsg "Reloading macro..."
    try (
        fileIn (maxMacroscriptsPath + "MaxManager_INIEditor.mcr")
        logMsg "Macro reloaded"
    ) catch (
        logMsg "WARNING: Could not reload macro (restart 3ds Max)"
    )
    
    format "\n=== Update Complete! ===\n\n"
    messageBox "MaxINI Editor v1.0.0 updated successfully!\n\n🔄 Restart 3ds Max to apply changes" title:"Update Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ Update failed: %\n" errorMsg
    messageBox ("Update failed!\n\n" + errorMsg) title:"Update Error"
)

