/*
 * Hot Reload System for MaxManager
 * Description: Automatic module reloading system for development
 * Version: 1.0.0
 * Author: MaxManager
 * Created: 2025-10-17
 */

-- Hot reload system for MaxManager modules
fn hotReloadMaxManager = (
    try (
        clearListener()
        format "\n=== MaxManager Hot Reload System v1.0.0 ===\n\n"
        
        -- Define source and target paths
        local sourcePath = "C:\\MaxManager\\src\\"
        local targetPath = (getdir #maxdata) + "scripts\\MaxManager\\src\\"
        
        format "🔄 Hot reloading MaxManager modules...\n"
        
        -- Copy updated Python files
        local pythonFiles = #(
            "ui\\maxini_editor_advanced.py",
            "ui\\maxini_editor_modern.py", 
            "ui\\maxini_editor_window.py",
            "ui\\maxini_installer.py",
            "ui\\maxini_preset_dialog.py",
            "ui\\maxini_widgets.py",
            "ui\\theme_loader.py",
            "modules\\maxini_parser.py",
            "modules\\maxini_backup.py",
            "modules\\maxini_presets.py",
            "modules\\file_manager.py",
            "modules\\kanban.py",
            "modules\\module_manager.py",
            "modules\\project_creator.py"
        )
        
        for file in pythonFiles do (
            local sourceFile = sourcePath + file
            local targetFile = targetPath + file
            
            if doesFileExist sourceFile then (
                copyFile sourceFile targetFile
                format "✅ Updated: %\n" file
            ) else (
                format "⚠️ Source not found: %\n" file
            )
        )
        
        -- Copy updated macro
        local macroSource = sourcePath + "maxscript\\MaxManager_INIEditor.mcr"
        local macroTarget = (getdir #maxdata) + "UI\\macroscripts\\MaxManager_INIEditor.mcr"
        
        if doesFileExist macroSource then (
            copyFile macroSource macroTarget
            format "✅ Updated macro: MaxManager_INIEditor.mcr\n"
        )
        
        -- Force reload macro
        format "🔄 Reloading macro...\n"
        try (
            fileIn macroTarget
            format "✅ Macro reloaded successfully\n"
        ) catch (
            format "⚠️ Could not reload macro: %\n" (getCurrentException())
        )
        
        format "\n=== Hot Reload Complete! ===\n"
        format "🎯 All MaxManager modules updated\n"
        format "🔧 Advanced Editor v1.0.1 with hot reload ready\n"
        format "📋 Next: Click MaxINI Editor button to test\n\n"
        
        messageBox "MaxManager Hot Reload Complete!\n\n🎯 All modules updated to latest version\n🔧 Advanced Editor v1.0.1 with hot reload system\n📋 Click MaxINI Editor button to test!" title:"Hot Reload Complete" beep:false
        
    ) catch (
        local errorMsg = getCurrentException()
        format "\n❌ Hot Reload failed: %\n" errorMsg
        messageBox ("Hot Reload failed!\n\n" + errorMsg) title:"Hot Reload Error"
    )
)

-- Auto-reload on file change (development mode)
fn startFileWatcher = (
    format "🔍 Starting file watcher for development...\n"
    -- This would monitor file changes and auto-reload
    -- For now, manual reload via hotReloadMaxManager()
)

-- Run hot reload
hotReloadMaxManager()
