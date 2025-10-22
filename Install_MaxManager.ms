/*
 * MaxManager Installer
 * Copies all necessary files to 3ds Max user scripts directory
 */

fn installMaxManager = (
    -- Get target directory
    local userScripts = getDir #userScripts
    local targetDir = userScripts + "MaxManager\\"
    
    -- Get source directory (where this installer is located)
    local sourceDir = getFilenamePath (getThisScriptFilename())
    
    print ("Installing MaxManager...")
    print ("Source: " + sourceDir)
    print ("Target: " + targetDir)
    
    -- Create target directory
    makeDir targetDir all:true
    
    -- Copy directories
    local dirsToCopy = #("src", "data", "icons")
    for dir in dirsToCopy do (
        local srcPath = sourceDir + dir
        local dstPath = targetDir + dir
        print ("Copying " + dir + "...")
        
        -- Use robocopy for reliable directory copying
        local cmd = "robocopy \"" + srcPath + "\" \"" + dstPath + "\" /E /R:1 /W:1"
        DOSCommand cmd quiet:false
    )
    
    -- Copy .mcr file to startup
    local mcrSrc = sourceDir + "src\\maxscript\\maxmanager.mcr"
    local mcrDst = (getDir #userStartupScripts) + "maxmanager.mcr"
    
    if doesFileExist mcrSrc then (
        print ("Installing macro script...")
        copyFile mcrSrc mcrDst
        print ("✓ Macro installed to startup")
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

