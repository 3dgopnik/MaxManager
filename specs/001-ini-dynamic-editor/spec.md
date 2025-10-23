# Feature Specification: Dynamic INI Editor with Real-time Editing

**Feature Branch**: `001-ini-dynamic-editor`  
**Created**: 2025-10-23  
**Status**: Draft  
**Input**: User description: "Реальное редактирование 3dsMax.ini с динамической генерацией вкладок из секций INI-файла и возможностью изменять/сохранять параметры"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View and Edit Single INI Section (Priority: P1)

As a 3ds Max user, I want to open the MaxManager INI Editor, see all available configuration sections as tabs, select a specific section (like "Security"), view all parameters in that section, modify values, and save changes back to the INI file.

**Why this priority**: This is the core functionality - without it, the feature provides no value. It represents the minimal viable product that allows users to accomplish the primary goal of editing their 3ds Max configuration.

**Independent Test**: Can be fully tested by opening the editor, clicking on any section tab, changing one parameter value, clicking Apply, and verifying the change persists in the actual 3dsMax.ini file.

**Acceptance Scenarios**:

1. **Given** MaxManager is opened and INI Editor is launched, **When** user clicks on the "Security" tab, **Then** all parameters from the [Security] section are displayed in a readable list format with current values
2. **Given** user is viewing the Security section parameters, **When** user double-clicks on "SafeSceneScriptExecutionEnabled" parameter, **Then** an inline editor appears allowing the user to change the value
3. **Given** user has modified a parameter value, **When** user clicks the "Apply" button, **Then** the change is written to the 3dsMax.ini file and a backup file is created
4. **Given** user has saved changes, **When** user reopens 3ds Max or checks the INI file directly, **Then** the modified value persists

---

### User Story 2 - Navigate Through Multiple Sections (Priority: P2)

As a 3ds Max user working with multiple configuration areas, I want to quickly switch between different INI sections (like Security, Performance, Renderer, Directories) using tabs, without losing any unsaved changes in other sections.

**Why this priority**: Essential for productivity when users need to configure multiple areas of 3ds Max in one session. Builds on P1 by adding navigation between sections.

**Independent Test**: Can be tested by opening the editor, switching between 3+ different section tabs, verifying each tab shows correct parameters, and confirming that switching tabs doesn't lose unsaved edits.

**Acceptance Scenarios**:

1. **Given** MaxManager INI Editor is open, **When** user looks at the header area, **Then** all INI sections are visible as individual tabs (Security, Performance, Renderer, Directories, etc.)
2. **Given** user is viewing the "Performance" section with unsaved changes, **When** user clicks on the "Renderer" tab, **Then** the Renderer section parameters are displayed and Performance changes remain unsaved but preserved
3. **Given** there are more than 10 section tabs, **When** user looks at the tab area, **Then** navigation arrows (← →) appear allowing horizontal scrolling through tabs
4. **Given** user has clicked the right arrow, **When** hidden tabs scroll into view, **Then** user can click on any newly visible tab to navigate to that section

---

### User Story 3 - Review Changes Before Saving (Priority: P2)

As a cautious 3ds Max user, I want to see visual indicators for any parameters I've modified, review all pending changes at once, and have the ability to revert individual changes or all changes before applying them to the INI file.

**Why this priority**: Prevents accidental misconfiguration and gives users confidence when making changes. Critical for professional users who need to be careful with system settings.

**Independent Test**: Can be tested by modifying 3-5 parameters across 2 different sections, observing visual indicators (color changes), using the Revert function, and confirming only intended changes are applied.

**Acceptance Scenarios**:

1. **Given** user has modified a parameter value, **When** user views the parameter list, **Then** the modified parameter is highlighted with a yellow background color
2. **Given** user has multiple modified parameters, **When** user clicks the "Revert" button, **Then** all modified parameters return to their original values and yellow highlights disappear
3. **Given** user has applied changes successfully, **When** the save operation completes, **Then** modified parameters briefly show a green background indicating successful save
4. **Given** user has unsaved changes, **When** user attempts to close the editor, **Then** a confirmation dialog warns about losing unsaved changes

---

### User Story 4 - Reload and Refresh Configuration (Priority: P3)

As a 3ds Max user experimenting with settings, I want to reload the current INI file values at any time to see external changes or reset to the file's current state without closing and reopening the editor.

**Why this priority**: Nice-to-have functionality that improves user experience for advanced scenarios like comparing settings or recovering from mistakes, but not essential for basic editing workflow.

**Independent Test**: Can be tested by making changes in the editor, manually editing the 3dsMax.ini file externally, clicking Refresh in the editor, and confirming external changes are loaded.

**Acceptance Scenarios**:

1. **Given** user has the INI Editor open, **When** user clicks the "Refresh" button, **Then** all parameter values reload from the disk file and any unsaved changes are discarded
2. **Given** 3dsMax.ini file was modified by another application, **When** user clicks Refresh, **Then** the editor displays the updated values from disk
3. **Given** user has unsaved changes, **When** user clicks Refresh, **Then** a confirmation dialog asks if user wants to discard changes before reloading

---

### Edge Cases

- **What happens when the 3dsMax.ini file is read-only or locked?**  
  System displays an error message indicating the file cannot be written and disables the Apply button. User can still view and edit values but cannot save until file permissions are corrected.

- **What happens when a section contains more than 100 parameters?**  
  Parameters are displayed in a scrollable list with no performance degradation. Large sections load within 1 second.

- **What happens when the INI file contains malformed sections or invalid encoding?**  
  Parser detects encoding issues and displays an error dialog with the specific problem. For malformed sections, the system attempts to load valid sections and marks invalid ones as "Unreadable - Manual Fix Required".

- **What happens when user enters an invalid value type (e.g., text for a numeric field)?**  
  Inline validation highlights the field in red and prevents saving until a valid value is entered. A tooltip explains the expected format.

- **What happens when two instances of MaxManager try to edit the same INI file simultaneously?**  
  The second instance detects the file has been modified since loading and prompts user to either reload and lose their changes, or force-save and overwrite the other changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically detect and load the 3dsMax.ini file from the standard installation path (%USERPROFILE%\AppData\Local\Autodesk\3dsMax\<YEAR> - 64bit\ENU\3dsMax.ini)
- **FR-002**: System MUST parse the INI file and extract all sections (e.g., [Security], [Performance], [Directories])
- **FR-003**: System MUST dynamically generate header tabs for each INI section found in the file
- **FR-004**: System MUST display all parameters within a selected section as a list showing parameter name, current value, and description (if available)
- **FR-005**: Users MUST be able to edit parameter values through inline editing (double-click to activate)
- **FR-006**: System MUST validate parameter values based on expected type (integer, boolean, string, path) before allowing save
- **FR-007**: System MUST visually indicate modified parameters with a distinct background color (yellow for unsaved, green for successfully saved)
- **FR-008**: System MUST provide horizontal scroll navigation when more than 10 section tabs exist
- **FR-009**: System MUST create a timestamped backup file (.bak) before writing changes to 3dsMax.ini
- **FR-010**: System MUST write changes to disk using UTF-16 LE encoding with BOM (3ds Max standard)
- **FR-011**: System MUST provide an "Apply" button that saves all pending changes to the INI file
- **FR-012**: System MUST provide a "Revert" button that discards all unsaved changes and reloads original values
- **FR-013**: System MUST provide a "Refresh" button that reloads the current INI file from disk
- **FR-014**: System MUST handle file permission errors gracefully and inform the user when the INI file cannot be written
- **FR-015**: System MUST prevent data loss by warning users about unsaved changes when closing the editor

### Key Entities

- **INI Section**: Represents a configuration category in 3dsMax.ini (e.g., [Security], [Performance]). Contains multiple parameters. Sections are used to organize related settings and drive the tab structure in the UI.

- **INI Parameter**: Represents a single configuration key-value pair within a section. Has attributes: name (key), value, type (integer/boolean/string/path), description, and modification state (original/modified/saved). Parameters are the actual editable settings displayed to users.

- **INI File**: Represents the 3dsMax.ini configuration file. Has attributes: file path, encoding (UTF-16 LE), modification timestamp. Contains all sections and parameters. Used to track file state for conflict detection.

- **Backup File**: Represents a timestamped copy of 3dsMax.ini created before any modifications. Has attributes: original file path, backup timestamp, backup file path. Used to allow recovery from errors or unwanted changes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view and navigate between INI sections in under 3 seconds per section switch
- **SC-002**: Users can modify and save a parameter value in under 10 seconds for the complete workflow (locate → edit → save)
- **SC-003**: System successfully parses and loads INI files with up to 100 sections and 500 parameters within 2 seconds
- **SC-004**: 100% of valid parameter edits are correctly persisted to the INI file and survive 3ds Max restart
- **SC-005**: Users can operate horizontal tab scroll navigation with no more than 3 clicks to reach any section
- **SC-006**: System creates a valid backup file for 100% of save operations before modifying the INI file
- **SC-007**: Zero data corruption incidents - all writes maintain proper UTF-16 LE encoding and INI structure
- **SC-008**: Users successfully complete the edit-save-verify workflow on first attempt 90% of the time without errors
