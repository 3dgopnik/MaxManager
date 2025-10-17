# Tasks: MaxINI Editor GUI

**Feature**: 001-maxini-editor-gui  
**Branch**: `001-maxini-editor-gui`  
**Date**: 2025-10-17  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)  
**GitHub Issue**: [#10](https://github.com/3dgopnik/MaxManager/issues/10)

## Overview

Task breakdown для MaxINI Editor GUI организованный по User Stories для независимой реализации и тестирования. Каждая User Story - это отдельный deliverable increment.

**Total Tasks**: 47  
**User Stories**: 4 (P1-P4)  
**MVP Scope**: User Story 1 только (T001-T015)  
**Full Feature**: All stories (T001-T047)

---

## Implementation Strategy

### Incremental Delivery

1. **MVP (User Story 1)**: Basic editing functionality
   - Deliverable: Can open, edit, save max.ini with validation and backups
   - Value: Safe editing without corruption risk
   - Estimated Time: 12-15 hours

2. **Core Value (+ User Story 2)**: Built-in presets
   - Deliverable: One-click preset application
   - Value: 30 second setup vs 30+ minutes manual
   - Estimated Time: +8 hours

3. **Extensibility (+ User Story 3)**: Custom presets
   - Deliverable: Users can create and share presets
   - Value: Reusable configurations across projects/machines
   - Estimated Time: +6 hours

4. **Polish (+ User Story 4)**: Localization
   - Deliverable: Full RU/EN support
   - Value: Accessibility for Russian users
   - Estimated Time: +4 hours

**Total Estimated Time**: 35-40 hours (7-8 days @ 5h/day)

---

## Dependencies Between User Stories

```
FOUNDATIONAL (Phase 2)
    ↓
USER STORY 1 (MVP) ───→ All other stories depend on US1
    ├── USER STORY 2 (requires parser, backup from US1)
    ├── USER STORY 3 (requires preset infrastructure from US2)
    └── USER STORY 4 (requires UI from US1)
```

**Independent Stories**: US2, US3, US4 can be implemented in parallel after US1 complete

---

## Phase 1: Setup & Infrastructure

**Goal**: Project initialization, directory structure, base configuration

**Tasks**:

- [ ] T001 Create module directory structure per implementation plan (src/modules/, src/ui/, data/, tests/)
- [ ] T002 Create data/validation/rules.json with initial parameter validation schema
- [ ] T003 Create data/translations/maxini_i18n.json with basic EN translations (RU in US4)
- [ ] T004 Create data/presets/built-in/ directory for built-in presets
- [ ] T005 [P] Set up pytest configuration in pyproject.toml or pytest.ini
- [ ] T006 [P] Configure mypy with strict-ish mode in pyproject.toml
- [ ] T007 [P] Configure ruff for linting and formatting

**Completion Criteria**: ✅ Directory structure matches plan.md, config files in place, dev tools ready

---

## Phase 2: Foundational Components

**Goal**: Blocking prerequisites needed by all user stories (parser, backup, exceptions)

**Tasks**:

- [ ] T008 Create src/modules/maxini_parser.py with MaxINIParameter dataclass
- [ ] T009 Implement MaxINIParser.__init__() to load validation rules from JSON
- [ ] T010 Implement MaxINIParser.load() to parse max.ini with UTF-16 LE encoding
- [ ] T011 Implement MaxINIParser.validate() with type/range/path validation
- [ ] T012 Implement MaxINIParser.group_by_category() for UI organization
- [ ] T013 Create src/modules/maxini_backup.py with MaxINIBackup dataclass
- [ ] T014 Implement MaxINIBackupManager with create_backup() and timestamp logic
- [ ] T015 Implement MaxINIBackupManager.cleanup_old_backups() with max 10 limit
- [ ] T016 Create custom exception classes in src/modules/maxini_exceptions.py
- [ ] T017 [P] Write unit test for MaxINIParser.load() in tests/unit/test_maxini_parser.py
- [ ] T018 [P] Write unit test for MaxINIParser.validate() covering all validation types
- [ ] T019 [P] Write unit test for MaxINIBackupManager in tests/unit/test_maxini_backup.py

**Completion Criteria**: ✅ Parser loads and validates max.ini, backups create with cleanup, tests pass

---

## Phase 3: User Story 1 - Просмотр и редактирование max.ini (P1) 🎯 MVP

**Goal**: Open Qt editor, display parameters grouped by category, edit values, save with validation and backup

**Independent Test**: Open editor in 3ds Max → change RenderThreads=16 → save → verify max.ini updated and backup created

**Value**: Safe editing without corruption, 5 min vs 15+ min manual editing

### Tasks:

- [ ] T020 [US1] Create src/ui/maxini_editor_window.py with basic QDialog structure
- [ ] T021 [US1] Implement MaxINIEditorWindow.__init__() with qtmax parenting
- [ ] T022 [US1] Create src/ui/maxini_widgets.py with ParameterWidget base class
- [ ] T023 [P] [US1] Implement IntParameterWidget (QSpinBox) for INT parameters
- [ ] T024 [P] [US1] Implement BoolParameterWidget (QCheckBox) for BOOL parameters
- [ ] T025 [P] [US1] Implement PathParameterWidget (QLineEdit + file picker button) for PATH parameters
- [ ] T026 [P] [US1] Implement StringParameterWidget (QLineEdit) for STRING parameters
- [ ] T027 [US1] Create QTabWidget for parameter categories (Rendering, Memory, Paths, UI, etc.)
- [ ] T028 [US1] Implement dynamic widget creation from MaxINIParameter list in load_parameters()
- [ ] T029 [US1] Add QToolTip support with description_en from parameters
- [ ] T030 [US1] Implement "Save" button handler with validation check
- [ ] T031 [US1] Integrate MaxINIBackupManager in save workflow (create backup before write)
- [ ] T032 [US1] Implement error dialog for validation failures showing specific errors
- [ ] T033 [US1] Add "unsaved changes" indicator (asterisk in title or status bar)
- [ ] T034 [US1] Implement MaxINIParser.save() to write parameters to max.ini with UTF-16 LE
- [ ] T035 [US1] Create src/modules/maxini_editor.py facade with detect_max_versions()
- [ ] T036 [US1] Implement MaxINIEditor.load_ini() integrating parser
- [ ] T037 [US1] Implement MaxINIEditor.save_ini() integrating parser + backup
- [ ] T038 [US1] Create src/maxscript/MaxManager_INIEditor.ms production macro
- [ ] T039 [US1] Add Python path setup and import in MaxScript macro
- [ ] T040 [US1] Add QApplication instance check and MaxINIEditorWindow launch
- [ ] T041 [US1] Apply MaxManager theme to editor window using theme_loader
- [ ] T042 [P] [US1] Write integration test for full edit workflow in tests/integration/test_edit_workflow.py
- [ ] T043 [US1] Manual test: Open in Max, edit parameter, save, verify file updated

**Completion Criteria for US1**: ✅ Can open editor in 3ds Max, edit parameters, save with validation, backup auto-created, changes persist in max.ini

---

## Phase 4: User Story 2 - Применение готовых пресетов (P2)

**Goal**: Load built-in presets, preview changes, apply with one click

**Independent Test**: Select "High Performance" preset → preview shows RenderThreads change → apply → verify max.ini has all preset parameters

**Value**: 30 second setup vs 30+ minutes manual

### Tasks:

- [ ] T044 [US2] Create data/presets/built-in/high_performance.json with researched parameters
- [ ] T045 [P] [US2] Create data/presets/built-in/memory_optimized.json
- [ ] T046 [P] [US2] Create data/presets/built-in/arnold_optimized.json
- [ ] T047 [P] [US2] Create data/presets/built-in/vray_optimized.json
- [ ] T048 [P] [US2] Create data/presets/built-in/minimal_safe.json
- [ ] T049 [US2] Create src/modules/maxini_presets.py with MaxINIPreset dataclass
- [ ] T050 [US2] Implement MaxINIPresetManager.__init__() loading built-in and user presets
- [ ] T051 [US2] Implement MaxINIPresetManager.list_presets() filtering by author
- [ ] T052 [US2] Implement MaxINIPresetManager.load_preset() from JSON
- [ ] T053 [US2] Implement MaxINIPresetManager.preview_changes() returning ParameterChange list
- [ ] T054 [US2] Implement MaxINIPresetManager.apply_preset() updating parameters
- [ ] T055 [US2] Add preset selection QComboBox to editor window
- [ ] T056 [US2] Implement preset list population on window load
- [ ] T057 [US2] Create preset preview dialog showing parameter changes table
- [ ] T058 [US2] Add "Apply Preset" button handler with preview → apply workflow
- [ ] T059 [US2] Show confirmation dialog if user has unsaved changes before preset apply
- [ ] T060 [US2] Integrate preset application with backup creation
- [ ] T061 [US2] Add success notification after preset applied
- [ ] T062 [P] [US2] Write unit test for MaxINIPresetManager in tests/unit/test_maxini_presets.py
- [ ] T063 [US2] Manual test: Apply High Performance preset, verify all parameters changed

**Completion Criteria for US2**: ✅ 5 built-in presets available, can preview and apply, backup created, parameters updated

---

## Phase 5: User Story 3 - Пользовательские пресеты (P3)

**Goal**: Create custom presets from current settings, save, export/import, delete

**Independent Test**: Edit parameters → Save as "My Config" → close editor → reopen → verify "My Config" in user presets list

**Value**: Reusable configurations across projects and machines

### Tasks:

- [ ] T064 [US3] Implement MaxINIPresetManager.create_from_current() capturing current parameters
- [ ] T065 [US3] Implement MaxINIPresetManager.save_preset() writing to ~/.maxmanager/presets/
- [ ] T066 [US3] Implement MaxINIPresetManager.delete_preset() with file removal
- [ ] T067 [US3] Create user preset directory ~/.maxmanager/presets/ if not exists
- [ ] T068 [US3] Add "Save as Preset" button to editor window
- [ ] T069 [US3] Create save preset dialog with Name/Description RU/EN/Tags fields
- [ ] T070 [US3] Implement save preset handler validating name uniqueness
- [ ] T071 [US3] Add user presets section to preset list (separate from built-in)
- [ ] T072 [US3] Add context menu to user presets with Export/Delete options
- [ ] T073 [US3] Implement export preset to file dialog (save JSON)
- [ ] T074 [US3] Implement import preset from file dialog (load JSON)
- [ ] T075 [US3] Add delete confirmation dialog for user presets
- [ ] T076 [P] [US3] Write unit test for user preset CRUD operations
- [ ] T077 [US3] Manual test: Create preset, export, delete, import, verify

**Completion Criteria for US3**: ✅ Can create user presets, save to file, export/import JSON, delete with confirmation

---

## Phase 6: User Story 4 - Мультиязычность (P4)

**Goal**: Switch between RU/EN, all UI and tooltips translate, language persists

**Independent Test**: Switch to Russian → verify all tooltips in Russian → restart editor → verify Russian still active

**Value**: Accessibility for Russian-speaking users

### Tasks:

- [ ] T078 [US4] Populate data/translations/maxini_i18n.json with full RU translations
- [ ] T079 [US4] Add window titles, button labels, dialog texts to i18n
- [ ] T080 [US4] Add all parameter descriptions_ru to i18n file
- [ ] T081 [US4] Create src/core/i18n.py with I18n class loading translations
- [ ] T082 [US4] Implement I18n.tr() method returning translated text by key
- [ ] T083 [US4] Add language switcher QComboBox to editor window (RU/EN)
- [ ] T084 [US4] Implement language change handler reloading all UI text
- [ ] T085 [US4] Update ParameterWidget tooltips to use I18n for descriptions
- [ ] T086 [US4] Save selected language to MaxManager config on change
- [ ] T087 [US4] Load saved language from config on editor init
- [ ] T088 [US4] Add "[EN]" marker for parameters missing RU translation
- [ ] T089 [P] [US4] Write unit test for I18n class in tests/unit/test_i18n.py
- [ ] T090 [US4] Manual test: Switch to RU, verify all tooltips, restart, verify persists

**Completion Criteria for US4**: ✅ Full RU/EN support, switch works, language persists across sessions, fallback to EN with marker

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Final polish, error handling, edge cases, documentation

**Tasks**:

- [ ] T091 [P] Implement Max3dsVersion detection via Windows Registry (winreg)
- [ ] T092 [P] Add version selector if multiple Max installations detected
- [ ] T093 [P] Implement search/filter for parameters by name or description
- [ ] T094 [P] Add keyboard shortcuts (Ctrl+S save, Ctrl+F search, Esc close)
- [ ] T095 Handle edge case: max.ini doesn't exist → create with defaults
- [ ] T096 Handle edge case: max.ini corrupted → offer restore from backup
- [ ] T097 Handle edge case: no write permissions → show error with admin instructions
- [ ] T098 Handle edge case: max.ini > 10MB → show warning
- [ ] T099 Add logging for all operations (load, save, preset apply) to MaxManager logger
- [ ] T100 Create MaxManager_INIEditor icon and register in 3ds Max
- [ ] T101 [P] Update docs/changelog.md with feature description
- [ ] T102 [P] Create docs/maxini_editor_guide.md user documentation (RU)
- [ ] T103 Copy MaxScript macro to 3ds Max scripts folder automatically
- [ ] T104 Add version number to editor window title
- [ ] T105 Final integration test: All user stories end-to-end
- [ ] T106 Performance test: Load 5MB max.ini < 2 seconds
- [ ] T107 Code review checklist: Type hints, docstrings, no dead code
- [ ] T108 Run ruff + mypy + pytest, fix all issues
- [ ] T109 User acceptance test with Alexey in 3ds Max

**Completion Criteria for Phase 7**: ✅ All edge cases handled, docs updated, tests pass, ready for production

---

## Parallel Execution Opportunities

### Setup Phase (Phase 1)
```
T001 (structure) → BLOCKS all
T002, T003, T004 → [P] can run in parallel
T005, T006, T007 → [P] can run in parallel
```

### Foundational Phase (Phase 2)
```
T008-T012 (parser) → sequential
T013-T015 (backup) → [P] parallel with tests T017-T019
T016 (exceptions) → [P] parallel with parser/backup
```

### User Story 1 (MVP)
```
T020-T022 (window structure) → sequential
T023-T026 (widgets) → [P] can implement all 4 widgets in parallel
T027-T033 (UI logic) → depends on T026
T034-T037 (facade) → [P] parallel with T038-T041 (MaxScript)
T042 (integration test) → depends on all above
```

### User Story 2 (Presets)
```
T044-T048 (preset JSON files) → [P] all 5 can be created in parallel
T049-T054 (preset logic) → sequential
T055-T061 (UI integration) → sequential after T054
T062 (tests) → [P] parallel with UI tasks
```

### User Story 3 (Custom Presets)
```
T064-T066 (CRUD logic) → sequential
T067 (directory) → [P] parallel with logic
T068-T075 (UI) → sequential
T076 (tests) → [P] parallel with UI
```

### User Story 4 (i18n)
```
T078-T080 (translations) → [P] can be done in parallel
T081-T082 (I18n class) → sequential
T083-T088 (UI integration) → sequential
T089 (tests) → [P] parallel with UI
```

### Polish Phase
```
T091-T094 (features) → [P] all independent
T095-T098 (edge cases) → [P] all independent
T099-T104 (docs/logging) → [P] all independent
T105-T109 (final tests) → sequential
```

**Total Parallel Opportunities**: ~35 tasks can run in parallel (74% of tasks)

---

## MVP vs Full Feature

### MVP Scope (User Story 1 только)
**Tasks**: T001-T043 (43 tasks)  
**Time**: 12-15 hours  
**Deliverable**: Basic editor with validation and backups

### Extended MVP (+ User Story 2)
**Tasks**: T001-T063 (63 tasks)  
**Time**: 20-23 hours  
**Deliverable**: MVP + built-in presets (core value)

### Full Feature (All Stories)
**Tasks**: T001-T109 (109 tasks)  
**Time**: 35-40 hours  
**Deliverable**: Complete MaxINI Editor with all features

---

## Task Progress Tracking

Use this section to track completion:

```
Phase 1 Setup:      [       ] 0/7 tasks
Phase 2 Foundation: [       ] 0/12 tasks  
Phase 3 US1 (MVP):  [       ] 0/24 tasks
Phase 4 US2:        [       ] 0/20 tasks
Phase 5 US3:        [       ] 0/14 tasks
Phase 6 US4:        [       ] 0/13 tasks
Phase 7 Polish:     [       ] 0/19 tasks

Total: [                                                    ] 0/109 tasks (0%)
```

---

## Notes

- **Tests are included** (pytest approach per Constitution requirement)
- **TDD workflow**: Write test → Test fails → Implement → Test passes
- **Manual testing required** for MaxScript + Qt integration (per Constitution)
- **Parallel opportunities**: 35+ tasks marked with [P] can run concurrently
- **Independent stories**: US2, US3, US4 can be implemented in any order after US1

**Ready for `/MaxManager.implement`** when approved! 🚀


