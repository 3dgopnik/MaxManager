/*
 * MaxManager Installer
 * Copies all necessary files to 3ds Max user scripts directory
 */

fn copyTree src dst exclude:#() = (
    if findString src ":" == undefined do (
        -- Normalize relative to absolute if needed
        src = pathConfig.makeAbsolute src
    )
    makeDir dst all:true

    -- Copy files
    for f in (getFiles (pathConfig.appendPath src "*")) do (
        local name = (getFilenameFile f) + (getFilenameType f)
        local target = pathConfig.appendPath dst name
        copyFile f target
    )

    -- Recurse into directories
    for d in (getDirectories (pathConfig.appendPath src "*")) do (
        local dirName = getFilenameFile (trimRight d "\\/")
        if (findItem exclude dirName) == 0 do (
            local childDst = pathConfig.appendPath dst dirName
            copyTree d childDst exclude:exclude
        )
    )
)

fn installMaxManager = (
    -- Paths
    local userScripts = getDir #userScripts
    local userStartup = getDir #userStartupScripts
    local userIcons = getDir #userIcons

    local sourceDir = getFilenamePath (getThisScriptFilename())
    local targetDir = pathConfig.appendPath userScripts "MaxManager"

    format "=== MaxManager Installation ===\n"
    format "Source: %\n" sourceDir
    format "Target: %\n" targetDir
    format "Startup: %\n" userStartup
    format "Icons: %\n\n" userIcons

    -- FORCE CLEAR old installation to prevent cache issues
    format "=== FORCE CLEARING OLD INSTALLATION ===\n"
    if doesDirectoryExist targetDir do (
        -- Remove all files in directory first
        for f in (getFiles (pathConfig.appendPath targetDir "*")) do (
            deleteFile f
            format "Removed file: %\n" f
        )
        -- FORCE REMOVE all subdirectories completely using Windows command
        for d in (getDirectories (pathConfig.appendPath targetDir "*")) do (
            local dirName = getFilenameFile (trimRight d "\\/")
            local subDir = pathConfig.appendPath targetDir dirName
            if doesDirectoryExist subDir do (
                -- Use Windows rmdir command to force remove directory
                local rmdirCmd = "rmdir /s /q \"" + subDir + "\""
                dosCommand rmdirCmd
                format "FORCE REMOVED subdirectory: %\n" subDir
            )
        )
        format "Cleared old MaxManager directory: %\n" targetDir
    )
    
    -- Remove old startup macro
    local oldStartupMacro = pathConfig.appendPath userStartup "maxmanager.mcr"
    if doesFileExist oldStartupMacro do (
        deleteFile oldStartupMacro
        format "Removed old startup macro: %\n" oldStartupMacro
    )

    makeDir targetDir all:true

        -- Copy folders using native MaxScript (only src and data)
        local excludes = #( ".git", "__pycache__", ".mypy_cache", ".pytest_cache" )
        for dir in #("src", "data") do (
            local srcPath = pathConfig.appendPath sourceDir dir
            local dstPath = pathConfig.appendPath targetDir dir
            format "Copying %...\n" dir
            copyTree srcPath dstPath exclude:excludes
        )
        
        -- FORCE CLEAR Python cache directories
        format "=== CLEARING PYTHON CACHE ===\n"
        local cacheDirs = #("__pycache__", ".mypy_cache", ".pytest_cache")
        for cacheDir in cacheDirs do (
            local cachePath = pathConfig.appendPath targetDir cacheDir
            if doesDirectoryExist cachePath do (
                -- Remove all files in cache directory
                for f in (getFiles (pathConfig.appendPath cachePath "*")) do (
                    deleteFile f
                )
                format "Cleared cache: %\n" cachePath
            )
        )

    -- Install PNG icons directly to user icons folder
    (
        local iconsSrc = pathConfig.appendPath sourceDir "icons"
        local iconNames = #(
            "MaxManager_INIEditor_16.png",
            "MaxManager_INIEditor_24.png",
            "MaxManager_INIEditor_32.png",
            "MaxManager_INIEditor_48.png"
        )
        format "Copying icons to usericons...\n"
        for n in iconNames do (
            local s = pathConfig.appendPath iconsSrc n
            local d = pathConfig.appendPath userIcons n
            if doesFileExist s then copyFile s d
        )
    )

    -- Remove stale copies from usermacros to avoid old code
    (
        local userMacros = getDir #userMacros
        for f in (getFiles (pathConfig.appendPath userMacros "MaxManager-*.mcr")) do (
            deleteFile f
            format "Removed stale macro: %\n" f
        )
    )

    -- Copy macro to user startup scripts
    local mcrSrc = pathConfig.appendPath (pathConfig.appendPath sourceDir "src") (pathConfig.appendPath "maxscript" "maxmanager.mcr")
    local mcrDst = pathConfig.appendPath userStartup "maxmanager.mcr"

    if doesFileExist mcrSrc then (
        format "Installing macro to startup...\n"
        copyFile mcrSrc mcrDst
        format "✓ Macro installed: %\n" mcrDst
        -- Auto-register macro in current session
        fileIn mcrDst
    ) else (
        messageBox "Error: maxmanager.mcr not found!" title:"Installation Error"
        return false
    )
    
    -- No Python dependencies needed - using only built-in 3ds Max modules
    format "=== Checking Python Environment ===\n"
    format "✓ Using built-in PySide6, pymxs, and qtmax from 3ds Max\n"
    format "✓ No external dependencies required\n"

    -- Done
        local msg = "MaxManager v1.1.3 installed successfully!\n\n"
    msg += ("Files copied to:\n" + targetDir + "\n\n")
    msg += "Macro registered: MaxManager → INI Editor\n\n"
    msg += "If category is not visible, restart 3ds Max."
    messageBox msg title:"MaxManager Installed"

    format "Installation complete!\n"
    true
)

-- removeTree function removed - using Windows rmdir command instead

fn uninstallMaxManager = (
    local userScripts = getDir #userScripts
    local userStartup = getDir #userStartupScripts
    local userIcons = getDir #userIcons

    local targetDir = pathConfig.appendPath userScripts "MaxManager"
    local mcrPath = pathConfig.appendPath userStartup "maxmanager.mcr"

    format "=== MaxManager Uninstall ===\n"

    if doesFileExist mcrPath do (
        deleteFile mcrPath
        format "Removed: %\n" mcrPath
    )

    for n in #( "MaxManager_INIEditor_16.png", "MaxManager_INIEditor_24.png", "MaxManager_INIEditor_32.png", "MaxManager_INIEditor_48.png" ) do (
        local p = pathConfig.appendPath userIcons n
        if doesFileExist p do (
            deleteFile p
            format "Removed: %\n" p
        )
    )

    if doesDirectoryExist targetDir do (
        -- Remove all files in directory
        for f in (getFiles (pathConfig.appendPath targetDir "*")) do (
            deleteFile f
            format "Removed file: %\n" f
        )
        -- Remove all subdirectories recursively
        for d in (getDirectories (pathConfig.appendPath targetDir "*")) do (
            local dirName = getFilenameFile (trimRight d "\\/")
            local subDir = pathConfig.appendPath targetDir dirName
            if doesDirectoryExist subDir do (
                -- Remove files in subdirectory
                for f in (getFiles (pathConfig.appendPath subDir "*")) do (
                    deleteFile f
                )
                format "Cleared subdirectory: %\n" subDir
            )
        )
        format "Cleared directory: %\n" targetDir
    )
    
    -- FORCE CLEAR Python cache by removing entire directory
    format "=== FORCE CLEARING PYTHON CACHE ===\n"
    format "Removing entire MaxManager directory to clear Python cache\n"

    messageBox "MaxManager uninstalled." title:"MaxManager"
    true
)

-- Minimal auto-add to Main Toolbar
fn addToolbarButton macroName catName btnText = (
    local cfg = cui.getConfigFile()
    try(
        cui.loadConfig cfg; cui.saveConfigAs cfg; cui.loadConfig cfg
        local line = "<Item typeID=\"2\" type=\"CTB_MACROBUTTON\" width=\"0\" height=\"0\" controlID=\"0\" macroTypeID=\"3\" macroType=\"MB_TYPE_ACTION\" actionTableID=\"647394\" imageID=\"-1\" imageName=\"\" actionID=\"" + macroName + "`[" + catName + "]\" tip=\"" + btnText + "\" label=\"" + btnText + "\" />"
        local f = openFile cfg mode:"r"
        local old = readChars f (getFileSize cfg)
        close f
        local tag = "</Items>"
        local pos = findString old tag
        if pos != undefined do (
            local pre = substring old 1 (pos-1)
            local post = substring old pos (old.count - pos + 1)
            local new = pre + "\t\t" + line + "\n" + post
            local w = createFile cfg
            format new to:w
            close w
            cui.loadConfig cfg; cui.saveConfigAs cfg; cui.loadConfig cfg
        )
    )catch()
)

-- Run install and add toolbar button
-- Reinstall flow on drag-and-drop: uninstall then install
try( uninstallMaxManager() ) catch()
installMaxManager()
addToolbarButton "MaxManager_INIEditor" "MaxManager" "INI Editor"

