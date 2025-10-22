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

    makeDir targetDir all:true

    -- Copy folders using native MaxScript (only src and data)
    local excludes = #( ".git", "__pycache__", ".mypy_cache", ".pytest_cache" )
    for dir in #("src", "data") do (
        local srcPath = pathConfig.appendPath sourceDir dir
        local dstPath = pathConfig.appendPath targetDir dir
        format "Copying %...\n" dir
        copyTree srcPath dstPath exclude:excludes
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

    -- Done
    local msg = "MaxManager v1.1.2 installed successfully!\n\n"
    msg += ("Files copied to:\n" + targetDir + "\n\n")
    msg += "Macro registered: MaxManager → INI Editor\n\n"
    msg += "If category is not visible, restart 3ds Max."
    messageBox msg title:"MaxManager Installed"

    format "Installation complete!\n"
    true
)

fn removeTree p = (
    if doesFileExist p or (doesDirectoryExist p) do (
        for f in (getFiles (pathConfig.appendPath p "*")) do deleteFile f
        for d in (getDirectories (pathConfig.appendPath p "*")) do (
            removeTree d
        )
        deleteDir p
    )
)

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
        removeTree targetDir
        format "Removed dir: %\n" targetDir
    )

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

