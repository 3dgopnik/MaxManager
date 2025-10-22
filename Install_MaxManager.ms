/*
 * MaxManager Installer
 * Copies all necessary files to 3ds Max user scripts directory
 */

fn installMaxManager = (
    -- Get directories using getDir (correct 3ds Max paths)
    userScripts = getDir #userScripts
    userStartup = getDir #userStartupScripts
    userIcons = getDir #userIcons
    
    -- Get source directory
    sourceDir = getFilenamePath (getThisScriptFilename())
    targetDir = userScripts + "MaxManager\\"
    
    print "=== MaxManager Installation ==="
    print ("Source: " + sourceDir)
    print ("Target: " + targetDir)
    print ("Startup: " + userStartup)
    print ("Icons: " + userIcons)
    print ""
    
    -- Create target directory
    makeDir targetDir all:true
    
        -- Copy directories
        dirsToCopy = #("src", "data", "icons")
        for dir in dirsToCopy do (
            srcPath = sourceDir + dir
            dstPath = targetDir + dir
            print ("Copying " + dir + "...")

            cmd = "robocopy \"" + srcPath + "\" \"" + dstPath + "\" /E /R:1 /W:1 /NFL /NDL"
            DOSCommand cmd
        )
    
    -- Copy .mcr file to startup
    mcrSrc = sourceDir + "src\\maxscript\\maxmanager.mcr"
    mcrDst = userStartup + "maxmanager.mcr"
    
    if doesFileExist mcrSrc then (
        print "Installing macro to startup..."
        copyFile mcrSrc mcrDst
        print ("✓ Macro installed: " + mcrDst)
    ) else (
        messageBox "Error: maxmanager.mcr not found!" title:"Installation Error"
        return false
    )
    
    -- Success message
    local msg = "MaxManager v1.1.1 installed successfully!\n\n"
    msg += "Files copied to:\n" + targetDir + "\n\n"
    msg += "Macro registered: MaxManager → INI Editor\n\n"
    msg += "To use:\n"
    msg += "1. Restart 3ds Max\n"
    msg += "2. Customize UI → Category: MaxManager\n"
    msg += "3. Add 'INI Editor' to your toolbar"
    
    messageBox msg title:"MaxManager Installed"
    
    print ("Installation complete!")
    true
)

-- Run installer
installMaxManager()

