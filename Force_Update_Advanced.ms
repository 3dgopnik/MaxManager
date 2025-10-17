/*
 * Force Update to Advanced MaxINI Editor v1.0.0
 * Description: Forces update to Advanced Editor with direct 3ds Max API
 */

try (
    clearListener()
    format "\n=== FORCE UPDATE to Advanced MaxINI Editor v1.0.0 ===\n\n"
    
    -- Force copy updated macro
    local macroSource = "C:\\MaxManager\\src\\maxscript\\MaxManager_INIEditor.mcr"
    local macroTarget = (getdir #maxdata) + "UI\\macroscripts\\MaxManager_INIEditor.mcr"
    
    format "📁 Copying updated macro...\n"
    if doesFileExist macroSource then (
        copyFile macroSource macroTarget
        format "✅ Macro updated to v1.0.0 (Advanced Editor priority)\n"
    ) else (
        format "❌ ERROR: Macro source not found: %\n" macroSource
        throw "Update failed"
    )
    
    -- Force copy Advanced Editor
    local editorSource = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    local editorTarget = (getdir #maxdata) + "scripts\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    
    format "📁 Copying Advanced Editor...\n"
    if doesFileExist editorSource then (
        copyFile editorSource editorTarget
        format "✅ Advanced Editor v1.0.0 copied\n"
    ) else (
        format "❌ ERROR: Editor source not found: %\n" editorSource
        throw "Update failed"
    )
    
    -- Force reload macro
    format "🔄 Reloading macro...\n"
    try (
        fileIn macroTarget
        format "✅ Macro reloaded successfully\n"
    ) catch (
        format "⚠️ WARNING: Could not reload macro (restart 3ds Max)\n"
    )
    
    format "\n=== FORCE UPDATE COMPLETE! ===\n"
    format "🎯 Advanced MaxINI Editor v1.0.0 is now the PRIMARY editor\n"
    format "🔧 Features: Direct 3ds Max API, Security settings, Performance tuning\n"
    format "📋 Next: Click MaxINI Editor button to launch Advanced Editor v1.0.0\n\n"
    
    messageBox "FORCE UPDATE COMPLETE!\n\n🎯 Advanced MaxINI Editor v1.0.0 is now PRIMARY\n🔧 Direct 3ds Max API integration\n📋 Click MaxINI Editor button to test!" title:"Force Update Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ FORCE UPDATE FAILED: %\n" errorMsg
    messageBox ("FORCE UPDATE FAILED!\n\n" + errorMsg) title:"Force Update Error"
)
