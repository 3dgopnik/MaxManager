# Plan for Comprehensive Coverage of 3ds Max Configuration Parameters

## Summary
- Defines the focus areas required to complete the ini-parameter catalog for 3ds Max 2014–2026 and major plugins.
- Proposes concrete datasets to ingest into MaxManager (core, renderers, plugins, automation).
- Provides a step-by-step checklist for expanding and validating the knowledge base.

## Key Expansion Tracks
### 1. Core 3dsmax.ini (2014–2026)
- Capture the remaining sections: `Nitrous.Debug`, `MAXScript`, `OpenSubdiv`, `Slate.MaterialEditor`, `Python` (2022+), `USD` (2024+).
- Record system module settings: `Security`, `SafeScene`, `Telemetry`, `Analytics`, `LiveSync`.
- Add offline rendering toggles: `Backburner`, `NetworkRendering`, `Batch`.

### 2. Built-in Renderers
- **Arnold**: `skydome_light`, `render_view`, `ai_options` (logging, adaptive sampling, RTX).
- **Scanline**: hidden lighting switches, legacy GI.
- **Art Renderer** and `PhysicalMaterial`: quality levels, denoiser controls.

### 3. Major Third-Party Renderers
- **V-Ray** (`vray.ini`): distributed rendering, IPR, VRayDenoiser, VFB2 tweaks.
- **Corona** (`corona.ini`): UHD cache, denoising, Chaos Scatter parameters.
- **F-Storm** (`fstorm.ini`): GPU modes, noise reduction options.
- **Octane** (`octane.ini`): AI Light, out-of-core, OSL tree overrides.
- **Redshift**: `.redshiftPreferences` catalog for GPU overrides.

### 4. Geometry and FX Plugins
- **RailClone/Forest Pack**: generator controls, caching, viewport display limits.
- **Phoenix FD**: network simulation, cache warming, Chaos Cloud overrides.
- **tyFlow**: compile-time switches, cache tunables, viewport optimizations.
- **GrowFX**, **Multiscatter**, **CityTraffic**: community-proven tweaks from forums.

### 5. Automation and Pipeline Integrations
- Catalogs of `*.ms`, `*.py`, `*.mcr` scripts that expose ini-impacting switches.
- Hooks for **3ds Max Batch** and command-line workflows.
- Integrations with **ShotGrid**, **Deadline**, **Royal Render**.

## Recommended Repository Datasets
| Category | Format | Source | Notes |
|----------|--------|--------|-------|
| Core 2014–2026 | `data/core_parameters_2014_2026.json` | Autodesk Help, SDK samples | Store introduction year and value ranges |
| Arnold/Scanline | `data/renderers_builtin.json` | Arnold docs, Autodesk forums | Highlight Max version differences |
| V-Ray/Corona | `data/renderers_plugins.json` | Chaos Docs, official wiki | Cover production/IPR modes |
| FX plugins | `data/fx_plugins_parameters.json` | Chaos, tyFlow, Exlevel | Document plugin version dependencies |
| Automation | `data/automation_toggles.json` | GitHub MaxScript, Deadline docs | Show impact on batch/CLI flows |

## Step-by-Step Recommendations
1. **Collect**: configure scrapers for Autodesk Help (2014–2026), Chaos docs, GitHub MaxScript.
2. **Verify**: record working examples for each parameter and test on the relevant Max/plugin versions (at least one scene).
3. **Structure**: split parameters into JSON catalogs (core/renderers/plugins/automation) with unified fields.
4. **Integrate**: update MaxManager with new filters "Renderers", "FX Plugins", "Automation".
5. **Document**: ship bilingual guides for every new catalog and update the search reference.
6. **Automated QA**: extend CI with a smoke test that validates required fields and URL availability.

## Validation Checklist
- Run 3ds Max (UI and Batch) scenarios with timing/error logs enabled.
- Capture comparative viewport profiles (FPS, memory) with toggles on/off.
- Schedule regular user tests with artists: checklist of parameters that deliver measurable wins.

## Ongoing Monitoring Sources
- Autodesk Area, CGTalk, Polycount (legacy threads, hidden ini tweaks).
- Chaos forums (V-Ray/Corona/Phoenix FD), tyFlow Discord, Otoy forums (Octane).
- GitHub repositories for MaxScript/Python: **ADN samples**, **Ephere repos**, **CG-Press scripts**.
- Release notes for 3ds Max 2014–2026 and plugin changelogs.
