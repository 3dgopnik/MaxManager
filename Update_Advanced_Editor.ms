/*
 * Update Advanced MaxINI Editor v1.0.0
 * Description: Updates to Advanced Editor with direct 3ds Max API integration
 */

try (
    clearListener()
    format "\n=== Updating to Advanced MaxINI Editor v1.0.0 ===\n\n"
    
    -- Update macro
    local macroSource = "C:\\MaxManager\\src\\maxscript\\MaxManager_INIEditor.mcr"
    local macroTarget = (getdir #maxdata) + "UI\\macroscripts\\MaxManager_INIEditor.mcr"
    
    if doesFileExist macroSource then (
        copyFile macroSource macroTarget
        format "✅ Macro updated to v1.0.0\n"
    ) else (
        format "❌ ERROR: Macro source not found\n"
        throw "Update failed"
    )
    
    -- Update Advanced Editor
    local editorSource = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    local editorTarget = (getdir #maxdata) + "scripts\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    
    if doesFileExist editorSource then (
        copyFile editorSource editorTarget
        format "✅ Advanced Editor updated to v1.0.0\n"
    ) else (
        format "❌ ERROR: Editor source not found\n"
        throw "Update failed"
    )
    
    -- Reload macro
    try (
        fileIn macroTarget
        format "✅ Macro reloaded successfully\n"
    ) catch (
        format "⚠️ WARNING: Could not reload macro (restart 3ds Max)\n"
    )
    
    format "\n=== Update Complete! ===\n"
    format "🎯 Now click the MaxINI Editor button to launch Advanced Editor v1.0.0\n"
    format "🔧 Features: Direct 3ds Max API, Security settings, Performance tuning\n\n"
    
    messageBox "Advanced MaxINI Editor v1.0.0 updated successfully!\n\n🎯 Click the MaxINI Editor button to launch the new Advanced Editor!\n🔧 Features: Direct 3ds Max API integration" title:"Update Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ Update failed: %\n" errorMsg
    messageBox ("Update failed!\n\n" + errorMsg) title:"Update Error"
)
