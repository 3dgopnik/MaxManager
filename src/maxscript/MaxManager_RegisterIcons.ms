-- Register PNG icon sets for MaxManager (project copy)
try (
    local base = @"C:\MaxManager\resources\icons\"
    cui.registerIcons #MaxManager0 
    #(
        (base + "MaxManager0_24.png", 24),
        (base + "MaxManager0_30.png", 30),
        (base + "MaxManager0_36.png", 36),
        (base + "MaxManager0_48.png", 48)
    )

    cui.registerIcons #MaxManager0Hot 
    #(
        (base + "MaxManager0_24.png", 24),
        (base + "MaxManager0_30.png", 30),
        (base + "MaxManager0_36.png", 36),
        (base + "MaxManager0_48.png", 48)
    )

    cui.registerIcons #MaxManager0Dis 
    #(
        (base + "MaxManager0_24.png", 24),
        (base + "MaxManager0_30.png", 30),
        (base + "MaxManager0_36.png", 36),
        (base + "MaxManager0_48.png", 48)
    )
) catch()
