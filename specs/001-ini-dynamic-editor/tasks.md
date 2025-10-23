# Tasks: Dynamic INI Editor with Real-time Editing

**Input**: Design documents from `/specs/001-ini-dynamic-editor/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Manual testing через `python maxmanager_test.py` и 3ds Max (no automated test tasks)

**Organization**: Tasks grouped by user story для independent implementation and testing

---

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and canvas widget skeleton

- [ ] T001 Review all planning artifacts (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)
- [ ] T002 Create new file `src/ui/ini_canvas.py` with basic QWidget skeleton
- [ ] T003 [P] Add imports for required dependencies (PySide6, MaxINIParser, MaxINIBackupManager) in `src/ui/ini_canvas.py`

**Time**: ~15 minutes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core canvas infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create `INICanvasWidget` class with basic layout (QVBoxLayout, QTreeWidget, button bar) in `src/ui/ini_canvas.py`
- [ ] T005 Setup QTreeWidget with 3 columns (Parameter, Value, Type) in `INICanvasWidget.__init__`
- [ ] T006 [P] Create button bar with Apply/Revert/Refresh buttons (no functionality yet) in `INICanvasWidget.__init__`
- [ ] T007 [P] Add Signal declarations (changes_made, save_requested) to `INICanvasWidget` class
- [ ] T008 [P] Initialize change tracking data structures (self._changes dict, self._original_params list) in `INICanvasWidget.__init__`
- [ ] T009 Add `load_section()` method skeleton with basic QTreeWidget population in `src/ui/ini_canvas.py`
- [ ] T010 Test canvas widget displays in `maxmanager_test.py` (import and show widget)

**Checkpoint**: Canvas skeleton ready - user story implementation can now begin

**Time**: ~45 minutes

---

## Phase 3: User Story 1 - View and Edit Single INI Section (Priority: P1) 🎯 MVP

**Goal**: Load INI section → edit parameter → save to file

**Independent Test**: 
1. Run `python maxmanager_test.py`
2. Canvas displays parameters from one section
3. Double-click parameter → edit value → click Apply
4. Verify change saved to 3dsMax.ini file

### Implementation for User Story 1

#### T011-T016: Core Editing (can parallelize models/delegates)

- [ ] T011 [P] [US1] Create `INIValueDelegate` class (QStyledItemDelegate) with skeleton in `src/ui/ini_canvas.py`
- [ ] T012 [P] [US1] Implement `createEditor()` method with type-specific editors (INT→QSpinBox, BOOL→QComboBox, STRING→QLineEdit, PATH→QLineEdit) in `INIValueDelegate`
- [ ] T013 [US1] Implement `setEditorData()` to load current value into editor in `INIValueDelegate`
- [ ] T014 [US1] Implement `setModelData()` to save edited value to tree item in `INIValueDelegate`
- [ ] T015 [US1] Connect QTreeWidget with INIValueDelegate via `setItemDelegateForColumn(1, delegate)` in `INICanvasWidget.__init__`
- [ ] T016 [US1] Set edit triggers `setEditTriggers(QTreeWidget.DoubleClicked)` on QTreeWidget

#### T017-T020: Change Tracking

- [ ] T017 [US1] Implement `_on_item_changed(item, column)` handler to detect edits in `src/ui/ini_canvas.py`
- [ ] T018 [US1] Add value validation logic (type checking) in `_on_item_changed()`
- [ ] T019 [US1] Add change to `self._changes` dict and set yellow background in `_on_item_changed()`
- [ ] T020 [US1] Emit `changes_made` signal with change count in `_on_item_changed()`

#### T021-T026: Save Functionality

- [ ] T021 [US1] Implement `get_modified_params()` method to build list of MaxINIParameter with updated values in `src/ui/ini_canvas.py`
- [ ] T022 [US1] Implement `apply_changes()` method with MaxINIBackupManager integration in `src/ui/ini_canvas.py`
- [ ] T023 [US1] Call `MaxINIParser.save()` in `apply_changes()` to write changes to disk
- [ ] T024 [US1] Add green background flash (2 sec QTimer) after successful save in `apply_changes()`
- [ ] T025 [US1] Clear `self._changes` dict and emit signals after save in `apply_changes()`
- [ ] T026 [US1] Connect Apply button to `apply_changes()` slot in `INICanvasWidget.__init__`

#### T027-T030: Integration with Editor

- [ ] T027 [US1] Add canvas import and initialization in `src/ui/maxini_editor_advanced.py::create_content_widgets()`
- [ ] T028 [US1] Implement `load_ini_file()` method to parse INI and group by sections in `src/ui/maxini_editor_advanced.py`
- [ ] T029 [US1] Implement `_detect_ini_path()` method with auto-detection logic in `src/ui/maxini_editor_advanced.py`
- [ ] T030 [US1] Modify `on_sidebar_button_clicked('ini')` to call `load_ini_file()` and generate first tab in `src/ui/maxini_editor_advanced.py`

#### T031: Testing & Validation

- [ ] T031 [US1] Test complete US1 workflow in `maxmanager_test.py`: load section → edit → save → verify file

**Checkpoint**: User Story 1 MVP complete - single section editing fully functional ✅

**Time**: ~2 hours

---

## Phase 4: User Story 2 - Navigate Through Multiple Sections (Priority: P2)

**Goal**: Switch between multiple INI sections using dynamic tabs with scroll support

**Independent Test**:
1. Run `python maxmanager_test.py`
2. Click INI sidebar button → verify multiple tabs appear
3. Click different tabs → verify canvas content updates
4. If >10 tabs → verify scroll arrows work

### Implementation for User Story 2

#### T032-T036: Dynamic Tab Generation

- [ ] T032 [P] [US2] Modify `load_ini_file()` to extract ALL section names and call `header.set_context('ini', section_names)` in `src/ui/maxini_editor_advanced.py`
- [ ] T033 [P] [US2] Implement `on_header_tab_changed(context, tab_name)` to load section params into canvas in `src/ui/maxini_editor_advanced.py`
- [ ] T034 [US2] Add `self.ini_sections: Dict[str, List[MaxINIParameter]]` attribute to store all sections in `src/ui/maxini_editor_advanced.py`
- [ ] T035 [US2] Connect header tab change signal to section loading in `src/ui/maxini_editor_advanced.py::init_ui()`
- [ ] T036 [US2] Add canvas to content stack widget and switch to it on INI context in `src/ui/maxini_editor_advanced.py`

#### T037-T042: Tab Scrolling

- [ ] T037 [P] [US2] Wrap tabs container in QScrollArea with horizontal policy in `src/ui/modern_header.py::__init__()`
- [ ] T038 [P] [US2] Create left/right arrow buttons (← →) in `src/ui/modern_header.py::__init__()`
- [ ] T039 [US2] Implement `_scroll_left()` method to scroll by -160px in `src/ui/modern_header.py`
- [ ] T040 [US2] Implement `_scroll_right()` method to scroll by +160px in `src/ui/modern_header.py`
- [ ] T041 [US2] Implement `_update_arrow_visibility()` to show/hide arrows based on overflow in `src/ui/modern_header.py`
- [ ] T042 [US2] Connect arrow buttons and call `_update_arrow_visibility()` on resize in `src/ui/modern_header.py`

#### T043: Testing & Validation

- [ ] T043 [US2] Test tab navigation and scrolling with 3dsMax.ini (60+ sections) in `maxmanager_test.py`

**Checkpoint**: User Story 2 complete - multi-section navigation with scroll works ✅

**Time**: ~1 hour

---

## Phase 5: User Story 3 - Review Changes Before Saving (Priority: P2)

**Goal**: Visual indicators for changes, revert functionality, confirmation dialogs

**Independent Test**:
1. Run `python maxmanager_test.py`
2. Edit 3-5 parameters across 2 sections
3. Verify yellow backgrounds on modified params
4. Click Revert → verify changes discarded and yellow removed
5. Edit again → click Apply → verify green flash

### Implementation for User Story 3

#### T044-T048: Revert Functionality

- [ ] T044 [P] [US3] Implement `revert_changes()` method to clear `self._changes` dict in `src/ui/ini_canvas.py`
- [ ] T045 [P] [US3] Reload original parameters from `self._original_params` in `revert_changes()`
- [ ] T046 [US3] Remove yellow backgrounds from all tree items in `revert_changes()`
- [ ] T047 [US3] Emit `changes_made(0)` signal in `revert_changes()`
- [ ] T048 [US3] Connect Revert button to `revert_changes()` slot in `INICanvasWidget.__init__`

#### T049-T052: Enhanced Visual Feedback

- [ ] T049 [P] [US3] Add property `has_unsaved_changes` returning bool based on `self._changes` in `INICanvasWidget`
- [ ] T050 [P] [US3] Add property `change_count` returning len(self._changes) in `INICanvasWidget`
- [ ] T051 [US3] Improve green flash animation with QTimer.singleShot(2000) in `apply_changes()`
- [ ] T052 [US3] Add status bar updates on change tracking in `src/ui/maxini_editor_advanced.py::_on_canvas_changes()`

#### T053-T055: Close Confirmation

- [ ] T053 [P] [US3] Override `closeEvent(event)` in `src/ui/maxini_editor_advanced.py`
- [ ] T054 [US3] Check `canvas.has_unsaved_changes` and show QMessageBox confirmation in `closeEvent()`
- [ ] T055 [US3] Allow cancel or proceed based on user choice in `closeEvent()`

#### T056: Testing & Validation

- [ ] T056 [US3] Test revert, visual indicators, and close confirmation in `maxmanager_test.py`

**Checkpoint**: User Story 3 complete - change review and revert works ✅

**Time**: ~45 minutes

---

## Phase 6: User Story 4 - Reload and Refresh Configuration (Priority: P3)

**Goal**: Refresh INI from disk, detect external changes

**Independent Test**:
1. Run `maxmanager_test.py`
2. Make changes in editor (unsaved)
3. Manually edit 3dsMax.ini externally
4. Click Refresh → verify confirmation dialog → verify external changes loaded

### Implementation for User Story 4

#### T057-T061: Refresh Functionality

- [ ] T057 [P] [US4] Implement `refresh_from_file()` method skeleton in `src/ui/ini_canvas.py`
- [ ] T058 [US4] Check `has_unsaved_changes` and show confirmation dialog in `refresh_from_file()`
- [ ] T059 [US4] Call `MaxINIParser.load()` to re-read INI from disk in `refresh_from_file()`
- [ ] T060 [US4] Update canvas with new parameters and clear changes in `refresh_from_file()`
- [ ] T061 [US4] Connect Refresh button to `refresh_from_file()` slot in `INICanvasWidget.__init__`

#### T062-T063: Editor Integration

- [ ] T062 [P] [US4] Add Refresh support to `src/ui/maxini_editor_advanced.py` (reload all sections)
- [ ] T063 [US4] Update status bar with refresh status messages

#### T064: Testing & Validation

- [ ] T064 [US4] Test refresh with external file changes in `maxmanager_test.py`

**Checkpoint**: User Story 4 complete - refresh functionality works ✅

**Time**: ~30 minutes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, logging, documentation, final validation

#### T065-T070: Error Handling & Validation

- [ ] T065 [P] Add comprehensive error handling for file I/O (FileNotFoundError, PermissionError) in `src/ui/ini_canvas.py`
- [ ] T066 [P] Add validation tooltips for invalid parameter values in `INIValueDelegate`
- [ ] T067 [P] Add logging statements (logger.info, logger.warning, logger.error) throughout `src/ui/ini_canvas.py`
- [ ] T068 [P] Add type hints to all functions in `src/ui/ini_canvas.py`
- [ ] T069 [P] Add docstrings to all public methods in `src/ui/ini_canvas.py`
- [ ] T070 [P] Add error dialogs (QMessageBox) for edge cases in `src/ui/maxini_editor_advanced.py`

#### T071-T075: Code Quality

- [ ] T071 [P] Run Ruff format on all modified files
- [ ] T072 [P] Run Ruff linter and fix issues
- [ ] T073 [P] Run Mypy type checker and fix type errors
- [ ] T074 [P] Remove any debug print statements
- [ ] T075 [P] Clean up imports (remove unused)

#### T076-T080: Documentation

- [ ] T076 [P] Update CHANGELOG.md with feature description and changes
- [ ] T077 [P] Update README.md if needed (new INI editing functionality)
- [ ] T078 [P] Add inline code comments for complex logic
- [ ] T079 [P] Verify all contracts match implementation (contracts/ini_canvas_api.md, contracts/integration_api.md)
- [ ] T080 Update version number via `python scripts/update_version.py [NEW_VERSION]`

#### T081-T084: Final Testing

- [ ] T081 Full workflow test in `python maxmanager_test.py` (all user stories)
- [ ] T082 Install in 3ds Max via `Install_MaxManager.ms`
- [ ] T083 Manual test in 3ds Max: load INI → navigate tabs → edit params → save → verify
- [ ] T084 Edge case testing: read-only file, malformed INI, large sections (>100 params)

#### T085: Final Validation

- [ ] T085 Review quickstart.md "Definition of Done" checklist and confirm all items complete

**Checkpoint**: Feature complete and production-ready ✅

**Time**: ~1 hour

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 can start immediately after Foundational ✅
  - US2 depends on US1 (needs canvas integration) 🔗
  - US3 can start after US1 (adds to existing canvas) 🔗
  - US4 can start after US1 (adds refresh button) 🔗
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
US1 (Phase 3) ← MVP baseline, required for all others
    ↓
    ├─→ US2 (Phase 4) ← extends US1 with navigation
    ├─→ US3 (Phase 5) ← extends US1 with revert
    └─→ US4 (Phase 6) ← extends US1 with refresh
```

### Within Each User Story

- Core implementation before integration
- Canvas changes before editor changes
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup**: T002 and T003 can run in parallel
- **Foundational**: T005, T006, T007, T008 can run in parallel after T004
- **US1 Core**: T011 and T012 can run in parallel (different sections of same file)
- **US1 Integration**: T027 and T029 can run in parallel (different files)
- **US2 Tabs**: T032, T033, T034 can run in parallel (similar changes)
- **US2 Scroll**: T037 and T038 can run in parallel (different UI elements)
- **US3 Revert**: T044, T045, T046, T047 can run in parallel (related but separate logic)
- **US3 Visual**: T049, T050, T051 can run in parallel (different properties)
- **US4 Refresh**: T057, T062 can run in parallel (different files)
- **Polish**: All error handling (T065-T070), quality (T071-T075), docs (T076-T080) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch inline editing components in parallel:
Task T011: "Create INIValueDelegate class skeleton"
Task T012: "Implement createEditor() with type-specific editors"

# Launch integration tasks in parallel:
Task T027: "Add canvas initialization in maxini_editor_advanced.py"
Task T029: "Implement _detect_ini_path() auto-detection"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~15 min)
2. Complete Phase 2: Foundational (~45 min)
3. Complete Phase 3: User Story 1 (~2 hours)
4. **STOP and VALIDATE**: Test US1 independently via `python maxmanager_test.py`
5. Deploy/demo if ready → ✅ **MVP READY**

**Total MVP time**: ~3 hours

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 → Single section editing works ✅
2. **V1.1**: Add US2 → Multi-section navigation works ✅
3. **V1.2**: Add US3 → Change review and revert works ✅
4. **V1.3**: Add US4 → Refresh from file works ✅
5. **V2.0**: Polish phase → Production-ready ✅

Each increment adds value without breaking previous functionality.

### Sequential Strategy (Solo Developer)

**Recommended order for single developer**:

1. Phase 1: Setup (15 min)
2. Phase 2: Foundational (45 min)
3. Phase 3: US1 - MVP (2 hours)
   - **Test checkpoint**: Verify single section editing
4. Phase 4: US2 - Navigation (1 hour)
   - **Test checkpoint**: Verify tab switching
5. Phase 5: US3 - Review (45 min)
   - **Test checkpoint**: Verify revert/visual indicators
6. Phase 6: US4 - Refresh (30 min)
   - **Test checkpoint**: Verify external changes reload
7. Phase 7: Polish (1 hour)
   - **Test checkpoint**: Full integration test

**Total time**: ~6 hours (matches quickstart.md estimate)

---

## Task Summary

**Total Tasks**: 85  
**By Phase**:
- Setup: 3 tasks
- Foundational: 7 tasks (blocking)
- US1 (MVP): 21 tasks
- US2: 12 tasks
- US3: 13 tasks
- US4: 8 tasks
- Polish: 21 tasks

**By User Story**:
- US1: 21 tasks (~2 hours) 🎯 MVP
- US2: 12 tasks (~1 hour)
- US3: 13 tasks (~45 min)
- US4: 8 tasks (~30 min)
- Infrastructure: 31 tasks (~2.75 hours)

**Parallelizable Tasks**: 45 marked with [P]

**MVP Scope**: Phases 1-3 only (31 tasks, ~3 hours)

---

## Notes

- [P] tasks = different files or independent logic, no blocking dependencies
- [Story] label maps task to specific user story for traceability
- Each user story can be independently tested via `python maxmanager_test.py`
- No automated test tasks - manual testing via maxmanager_test.py and 3ds Max
- Stop at any checkpoint to validate story independently
- Commit after completing each user story phase
- Follow quickstart.md for detailed implementation guidance per task

---

**Ready to implement?** Start with Phase 1 and follow tasks sequentially! 🚀

