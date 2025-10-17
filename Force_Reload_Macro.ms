/*
 * Force Reload MaxINI Editor Macro
 * Description: Forces 3ds Max to reload the updated macro
 */

try (
    clearListener()
    format "\n=== FORCE RELOAD MaxINI Editor Macro ===\n\n"
    
    -- Unregister old macro first
    format "🗑️ Unregistering old macro...\n"
    try (
        unregisterMacroScript "MaxManager" "MaxManager_INIEditor"
        format "✅ Old macro unregistered\n"
    ) catch (
        format "⚠️ Old macro not found (OK)\n"
    )
    
    -- Force reload from file
    local macroPath = (getdir #maxdata) + "UI\\macroscripts\\MaxManager_INIEditor.mcr"
    format "🔄 Reloading macro from: %\n" macroPath
    
    if doesFileExist macroPath then (
        fileIn macroPath
        format "✅ Macro reloaded successfully\n"
    ) else (
        format "❌ ERROR: Macro file not found: %\n" macroPath
        throw "Reload failed"
    )
    
    -- Verify registration
    format "🔍 Verifying macro registration...\n"
    if (macroScriptExists "MaxManager" "MaxManager_INIEditor") then (
        format "✅ Macro registered: MaxManager - MaxManager_INIEditor\n"
    ) else (
        format "❌ ERROR: Macro not registered!\n"
        throw "Registration failed"
    )
    
    format "\n=== FORCE RELOAD COMPLETE! ===\n"
    format "🎯 Macro updated to v1.0.0 (Advanced Editor priority)\n"
    format "📋 Next: Click MaxINI Editor button to launch Advanced Editor v1.0.0\n\n"
    
    messageBox "FORCE RELOAD COMPLETE!\n\n🎯 Macro updated to v1.0.0\n🔧 Advanced Editor is now PRIMARY\n📋 Click MaxINI Editor button to test!" title:"Force Reload Complete" beep:false
    
) catch (
    local errorMsg = getCurrentException()
    format "\n❌ FORCE RELOAD FAILED: %\n" errorMsg
    messageBox ("FORCE RELOAD FAILED!\n\n" + errorMsg) title:"Force Reload Error"
)
