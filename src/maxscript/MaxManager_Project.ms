-- MaxManager: Activate Project (MVP)
-- Picks a folder containing project.mm.json and sets render/maps/scenes paths accordingly

fn mm_chooseProject = (
    local root = getSavePath caption:"Select project root"
    if root == undefined then return false
    local metaPath = root + "/project.mm.json"
    if not (doesFileExist metaPath) then (
        messageBox ("project.mm.json not found in:\n" + root) title:"MaxManager"
        return false
    )
    local metaStr = readFile metaPath
    local meta = dotNetObject "Newtonsoft.Json.Linq.JObject" -- requires Json.NET if available, else fallback
    try (
        meta = (dotNetClass "Newtonsoft.Json.Linq.JObject").Parse metaStr
    ) catch (
        messageBox "Cannot parse project.mm.json" title:"MaxManager"
        return false
    )
    local renderPath = meta.Item["paths"].Item["renderPath"].ToString()
    local mapsPath   = meta.Item["paths"].Item["mapsPath"].ToString()
    local maxPath    = meta.Item["paths"].Item["maxPath"].ToString()
    -- Apply paths
    renderers.current.output_splitfilename = renderPath
    -- setDir #renderoutput renderPath -- alternative per engine
    setDir #maps mapsPath
    setDir #scenes maxPath
    messageBox ("Project activated:\n" + root) title:"MaxManager"
    true
)

rollout MaxManagerProject "MaxManager"
(
    button btnActivate "Activate Project" width:200 height:32
    on btnActivate pressed do (
        mm_chooseProject()
    )
)
createDialog MaxManagerProject width:220 height:80