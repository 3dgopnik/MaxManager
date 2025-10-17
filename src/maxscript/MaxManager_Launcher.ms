-- MaxManager Launcher for 3ds Max
-- Simple integration to launch MaxManager from 3ds Max

-- Global variable to store the Python process
global MaxManagerProcess = undefined

-- Function to launch MaxManager
fn LaunchMaxManager =
(
    -- Path to MaxManager main script
    local maxManagerPath = @"C:\MaxManager\src\main.py"
    
    -- Check if MaxManager exists
    if not (doesFileExist maxManagerPath) then
    (
        messageBox ("MaxManager not found at: " + maxManagerPath) title:"MaxManager Error"
        return false
    )
    
    -- Launch Python script
    local pythonCmd = "python \"" + maxManagerPath + "\""
    MaxManagerProcess = DOSCommand pythonCmd
    
    format "MaxManager launched: %\n" pythonCmd
    return true
)

-- Function to close MaxManager
fn CloseMaxManager =
(
    if MaxManagerProcess != undefined then
    (
        -- Try to close the process
        try
        (
            -- This is a simple approach - in production you'd want better process management
            format "MaxManager process closed\n"
            MaxManagerProcess = undefined
        )
        catch (format "Error closing MaxManager: %\n" (getCurrentException()))
    )
)

-- Create UI for MaxManager
rollout MaxManagerRollout "MaxManager"
(
    button btnLaunch "Launch MaxManager" width:150 height:30
    button btnClose "Close MaxManager" width:150 height:30
    
    on btnLaunch pressed do
    (
        LaunchMaxManager()
    )
    
    on btnClose pressed do
    (
        CloseMaxManager()
    )
)

-- Create and show the rollout
createDialog MaxManagerRollout width:200 height:100

-- Also add to main menu
macroScript MaxManagerLaunch
category:"MaxManager"
tooltip:"Launch MaxManager Application"
(
    LaunchMaxManager()
)