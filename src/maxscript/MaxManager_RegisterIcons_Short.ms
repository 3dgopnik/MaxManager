-- One-shot registration (run from MaxScript: Run Script...)
local base = @"C:\MaxManager\resources\icons\"
try(cui.unRegisterIcons #MaxManager0)catch()

cui.registerIcons #MaxManager0
#(
    #(base + "MaxManager0_24.png", 24),
    #(base + "MaxManager0_32.png", 32),
    #(base + "MaxManager0_48.png", 48)
)
format "iconIndex=%\n" (cui.iconNameToIndex "MaxManager0")
try(cui.saveConfig()); try(cui.loadConfig (cui.getConfigFile()))
