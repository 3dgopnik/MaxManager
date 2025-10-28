# Code Review Report (MaxManager)

## Goal
Document the issues spotted during the initial review and suggest follow-up actions without touching the source code.

## Findings and recommendations

1. **Incorrect backup manager initialization**  
   `INIManager` instantiates `MaxINIBackupManager` with a directory path even though the constructor only accepts a backup count. This will raise a `TypeError` inside `cleanup_old_backups` and does not create a dedicated folder for backup copies. Extend `MaxINIBackupManager` so that it accepts a backup directory, ensures its existence, and uses it when building backup paths.【F:src/modules/ini_manager.py†L33-L38】【F:src/modules/maxini_backup.py†L25-L190】

2. **INI key casing gets lost**  
   `MaxINIParser` relies on the default `configparser.ConfigParser()` configuration, which lowercases every key. The UI then fails to find parameters and the saved INI may be corrupted. Set `config.optionxform = str` during load and apply the same rule when writing files to preserve the original casing.【F:src/modules/maxini_parser.py†L101-L142】【F:src/modules/maxini_parser.py†L186-L205】

3. **Only original parameters are written back**  
   While saving, `INIManager` iterates over `original_parameters`, so any user-added keys are silently dropped and deleted ones reappear. Switch the write path to the current `current_sections` snapshot to support additions and removals.【F:src/modules/ini_manager.py†L225-L258】

4. **Duplicate ModuleManager implementations and missing logger**  
   `module_manager.py` contains two different `ModuleManager` implementations and both import `core.logger`, which is absent from the repository. This produces an inconsistent API surface and leads to `ModuleNotFoundError`. Keep a single implementation, move it to a dedicated module, and hook it to the actual logging facility (or ship the missing package).【F:src/modules/module_manager.py†L1-L200】

5. **Invalid logger import in FileManager**  
   `file_manager.py` tries to import `get_logger` from `..core.logger`, but there is no `core` package. Wire it up to a real logger (or add the module) and add an initialization smoke test so similar regressions are caught early.【F:src/modules/file_manager.py†L6-L194】

## Suggested next steps
- Add configurable backup directory support and ensure stale backups are purged.
- Preserve INI key casing during both read and write operations.
- Rewrite the save pipeline to mirror the current in-memory sections.
- Consolidate the `ModuleManager` responsibilities and point it to the working logging backend.
- Fix logger imports in the file manager and cover them with a sanity test.

