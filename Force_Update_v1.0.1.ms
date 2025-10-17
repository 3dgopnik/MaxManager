/*
 * Force Update Advanced MaxINI Editor v1.0.1
 * Description: Forces update of Advanced Editor with API fix
 */

try (
    clearListener()
    format "\n=== FORCE UPDATE Advanced MaxINI Editor v1.0.1 ===\n\n"
    
    -- Force copy updated Advanced Editor
    local editorSource = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    local editorTarget = (getdir #maxdata) + "scripts\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    
    format "🔧 Force copying Advanced Editor v1.0.1...\n"
    if doesFileExist editorSource then (
        copyFile editorSource editorTarget
        format "✅ Advanced Editor v1.0.1 force updated\n"
        format "📁 Target: %\n" editorTarget
    ) else (
        format "❌ ERROR: Source not found: %\n" editorSource
        throw "Force update failed"
    )
    
    -- Verify file was updated
    if doesFileExist editorTarget then (
        local fileInfo = getFileModDate editorTarget
        format "✅ File updated at: %\n" fileInfo
    )
    
    format "\n=== FORCE UPDATE COMPLETE! ===\n"
    format "🎯 Advanced Editor v1.0.1 with API fix is now installed\n"
    format "🔧 Fixed: maxscript.evaluate → pymxs.runtime\n"
    format "📋 Next: Restart 3ds Max and test Advanced Editor\n\n"
    
    messageBox "FORCE UPDATE v1.0.1 COMPLETE!\n\n🎯 Advanced Editor v1.0.1 with API fix installed\n🔧 Fixed: maxscript.evaluate → pymxs.runtime\n📋 Restart 3ds Max and test!" title:"Force Update Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ FORCE UPDATE FAILED: %\n" errorMsg
    messageBox ("FORCE UPDATE FAILED!\n\n" + errorMsg) title:"Force Update Error"
)
