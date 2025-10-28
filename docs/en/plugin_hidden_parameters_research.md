# Hidden Plugin Parameters Research (3ds Max 2015–2026)

## Goals and Scope
- Refresh the catalog of parameters for Arnold, V-Ray, Corona, Octane, F-Storm, RailClone, Forest Pack, Phoenix FD, and tyFlow.
- Focus on production-ready yet sparsely documented INI options.
- Validate configurations across 2015–2026 releases and record current defaults.

## Key Findings
1. **Arnold** – confirmed logging controls and Autotx modes that help diagnostics and offline texture conversion.
2. **V-Ray** – clarified RT memory limits, hidden VFB history controls, and DR server caps for render farms.
3. **Corona** – added parameters that influence sample intensity and post denoiser selection.
4. **Octane** – located working AI upsampling toggle and expanded denoiser mode list.
5. **F-Storm** – discovered community tweaks for interactive viewport scaling and temporal denoise.
6. **RailClone & Forest Pack** – captured viewport tuning and multithreading options.
7. **Phoenix FD & tyFlow** – documented useful cache and viewport integration settings.

## Practical Recommendations
- Back up configuration files before enabling experimental tweaks (F-Storm, tyFlow).
- For distributed rendering, lock DR/Swarm limits and Phoenix FD cache modes to keep nodes in sync.
- On mobile workstations, reduce interactive viewport load (Arnold ThreadsManualCount, FStorm.ViewportResolutionScale).

## Related Files
- `data/plugin_hidden_parameters.json` – structured catalog of new parameters with descriptions and references.
- Updates documented in `CHANGELOG.md` ([Unreleased] section).

## Verified Sources
- Autodesk Help (Arnold for 3ds Max, Logging, Licensing, Textures, System Threads).
- Chaos Docs (V-Ray, Phoenix FD).
- Corona Renderer Documentation (INI Settings, Denoising).
- OTOY OctaneRender Standalone Help.
- Itoo Software Manual (RailClone, Forest Pack).
- tyFlow Docs.
