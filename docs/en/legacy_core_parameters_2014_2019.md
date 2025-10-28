# Legacy 3ds Max Parameters (2014–2019)

## Summary
- Added the `data/legacy_core_parameters_2014_2019.json` catalog that records active `3dsmax.ini` options from 3ds Max 2014–2019.
- Highlighted the rarely documented `PluginSettings` and `OpenImageIO` sections plus performance switches such as `Performance.FindMissingMapsOnSceneLoad`.
- Every entry includes data type, default value, recommendations, and source links (Autodesk Help, Polycount, community forums).

## How to use
1. Update MaxManager and restart it so the new catalog becomes available in the lookup UI.
2. In the “Legacy Core” category filter by year and pick the parameter you need.
3. Review the **Recommended** field — it lists possible values and scenarios (loading speed boosts, OpenImageIO cache tuning, etc.).
4. Apply the change to your local `3dsmax.ini`, restart 3ds Max, and validate the outcome (scene load timing, stable viewport FPS).

## Key findings
- **Load-time performance**: `Performance.FindMissingMapsOnSceneLoad` and `Performance.ResolveAssetPathsOnSave` dramatically shorten opening/saving of old or network-heavy projects when disabled.
- **Plug-in proxy system**: the four `PluginSettings.*` flags document deferred initialization useful for diagnosing startup issues.
- **OpenImageIO controls**: cache limits, tile sizes, and auto-reload switches come with tailored recommendations for different hardware.
- **Shading fidelity**: `NormalBump.CalculateBitangentPerPixel` and `SettingsManagement.HDAOEnabled` explain how to restore “hidden” options that still work even if the UI no longer exposes them.

## Sources
- Autodesk Help 2014–2016 (Nitrous, HDAO, OpenImageIO)
- Polycount and Autodesk Forums (scene loading tweaks, `PluginSettings` explanations)
- Arnold OpenImageIO documentation

## Next steps
- Audit remaining `OpenImageIO` keys (e.g., `accept_untiled`) that appear in older configs but are missing from our catalog.
- Prepare ready-to-apply presets in MaxManager for switching between “Legacy Mode” and “Modern Mode”.
