/*
 * Update to Advanced MaxINI Editor v1.0.1
 * Description: Fixes maxscript.evaluate API error
 */

try (
    clearListener()
    format "\n=== Updating to Advanced MaxINI Editor v1.0.1 ===\n\n"
    
    -- Update Advanced Editor with API fix
    local editorSource = "C:\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    local editorTarget = (getdir #maxdata) + "scripts\\MaxManager\\src\\ui\\maxini_editor_advanced.py"
    
    format "🔧 Updating Advanced Editor with API fix...\n"
    if doesFileExist editorSource then (
        copyFile editorSource editorTarget
        format "✅ Advanced Editor v1.0.1 updated (API fix applied)\n"
    ) else (
        format "❌ ERROR: Editor source not found\n"
        throw "Update failed"
    )
    
    format "\n=== Update v1.0.1 Complete! ===\n"
    format "🔧 Fixed: maxscript.evaluate → pymxs.runtime API\n"
    format "🎯 Features: Direct 3ds Max settings modification\n"
    format "📋 Next: Test Apply All button in Advanced Editor\n\n"
    
    messageBox "Advanced MaxINI Editor v1.0.1 updated!\n\n🔧 Fixed: maxscript.evaluate API error\n🎯 Now uses pymxs.runtime for direct 3ds Max integration\n📋 Test the Apply All button!" title:"Update v1.0.1 Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ Update v1.0.1 failed: %\n" errorMsg
    messageBox ("Update v1.0.1 failed!\n\n" + errorMsg) title:"Update Error"
)
