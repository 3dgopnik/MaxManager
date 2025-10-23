# Data Model: Dynamic INI Editor

**Feature**: 001-ini-dynamic-editor  
**Date**: 2025-10-23  
**Phase**: 1 - Data Model & Contracts

## Overview

Определение структур данных и их взаимодействия для динамического редактора 3dsMax.ini.

---

## Core Entities

### 1. MaxINIParameter

**Purpose**: Представляет один параметр из INI файла (ключ-значение в секции)

**Source**: Существующий класс в `src/modules/maxini_parser.py` (уже реализован)

**Structure**:
```python
@dataclass
class MaxINIParameter:
    key: str                    # e.g., "SafeSceneScriptExecutionEnabled"
    value: str | int | bool | Path
    type: ParamType             # INT, BOOL, STRING, PATH
    category: ParamCategory     # RENDERING, MEMORY, PATHS, UI, etc.
    section: str                # e.g., "Security"
    description_ru: str | None  # Optional description
    description_en: str | None
    validation: ValidationRule | None
    default_value: Any | None
    unit: str | None            # e.g., "MB", "seconds"
```

**Validation**:
- Type checking (int должен быть int, bool должен быть 0/1)
- Range validation (min/max для int)
- Path existence (для PATH типа)

**State**: Immutable (изменения через копирование или tracking dict)

---

### 2. INISection

**Purpose**: Группирует параметры одной секции INI файла

**Structure**:
```python
@dataclass
class INISection:
    name: str                              # e.g., "Security"
    parameters: List[MaxINIParameter]      # All params in this section
    
    def get_param(self, key: str) -> MaxINIParameter | None:
        """Find parameter by key (case-insensitive)."""
        
    def get_param_count(self) -> int:
        """Total number of parameters in section."""
```

**Usage**:
- One section = one tab in UI
- Displayed in canvas when tab is selected

**Example**:
```python
security_section = INISection(
    name="Security",
    parameters=[
        MaxINIParameter(key="SafeSceneScriptExecutionEnabled", value=0, ...),
        MaxINIParameter(key="EmbeddedPythonExecutionBlocked", value=1, ...),
    ]
)
```

---

### 3. ParameterChange

**Purpose**: Отслеживает изменение одного параметра

**Structure**:
```python
@dataclass
class ParameterChange:
    section: str           # Which section
    key: str               # Which parameter
    old_value: Any         # Original value
    new_value: Any         # Modified value
    timestamp: float       # When changed (for undo/redo future enhancement)
    
    def is_valid(self) -> bool:
        """Check if new_value matches expected type."""
```

**State tracking**:
```python
# Changes dictionary
changes: Dict[str, Dict[str, ParameterChange]] = {
    "Security": {
        "SafeSceneScriptExecutionEnabled": ParameterChange(
            section="Security",
            key="SafeSceneScriptExecutionEnabled",
            old_value=0,
            new_value=1,
            timestamp=time.time()
        )
    }
}
```

---

### 4. INIEditorState

**Purpose**: Глобальное состояние редактора (текущая секция, изменения, режим)

**Structure**:
```python
@dataclass
class INIEditorState:
    ini_file_path: Path | None              # Path to 3dsMax.ini
    sections: Dict[str, INISection]         # All loaded sections
    current_section: str | None             # Currently displayed section
    changes: Dict[str, Dict[str, ParameterChange]]  # Pending changes
    is_modified: bool                       # Any unsaved changes?
    last_saved: float | None                # Timestamp of last save
    
    def get_change_count(self) -> int:
        """Total number of changed parameters."""
        return sum(len(changes) for changes in self.changes.values())
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved modifications."""
        return len(self.changes) > 0
    
    def clear_changes(self):
        """Clear all changes (after save or revert)."""
        self.changes.clear()
        self.is_modified = False
```

**Usage**: Single source of truth для всего состояния редактора

---

## Data Flow

### Loading INI File

```
User clicks "INI" button
    ↓
maxini_editor_advanced.load_ini_file()
    ↓
MaxINIParser.load(ini_path) → List[MaxINIParameter]
    ↓
Group by section → Dict[str, INISection]
    ↓
Generate tab names from sections.keys()
    ↓
ModernHeader.set_context('ini', tab_names)
    ↓
INIEditorState updated with sections
```

### Selecting Tab

```
User clicks tab (e.g., "Security")
    ↓
on_header_tab_changed(context='ini', tab_name='Security')
    ↓
Get INISection from state.sections['Security']
    ↓
INICanvasWidget.load_section('Security', section.parameters)
    ↓
Populate QTreeWidget with parameters
    ↓
Apply yellow highlights for any existing changes
```

### Editing Parameter

```
User double-clicks parameter value
    ↓
QTreeWidget triggers edit mode
    ↓
QStyledItemDelegate creates editor (QSpinBox/QLineEdit/etc.)
    ↓
User enters new value
    ↓
INICanvasWidget.on_item_changed(item, column)
    ↓
Validate new value (type, range)
    ↓
Create ParameterChange object
    ↓
Add to state.changes[section][key]
    ↓
Set yellow background on item
    ↓
Emit changes_made signal
```

### Saving Changes

```
User clicks "Apply" button
    ↓
INICanvasWidget.apply_changes()
    ↓
Get all ParameterChange objects from state.changes
    ↓
Update MaxINIParameter values
    ↓
MaxINIBackupManager.create_backup(ini_path) → backup_path
    ↓
MaxINIParser.save(ini_path, updated_params)
    ↓
Set green background on saved items (2 sec timer)
    ↓
state.clear_changes()
    ↓
state.last_saved = time.time()
    ↓
Show success message in status bar
```

### Reverting Changes

```
User clicks "Revert" button
    ↓
INICanvasWidget.revert_changes()
    ↓
state.clear_changes()
    ↓
Reload current section from original params
    ↓
Remove yellow backgrounds
    ↓
Show "Changes discarded" in status bar
```

---

## Type System

### ParamType Enum

```python
class ParamType(Enum):
    STRING = "STRING"   # General text
    INT = "INT"         # Integer numbers
    BOOL = "BOOL"       # Boolean (0/1)
    PATH = "PATH"       # File/directory path
```

**Validation mapping**:
- `STRING`: No validation (any text)
- `INT`: Must be valid integer, optional min/max range
- `BOOL`: Must be "0", "1", "true", "false", "yes", "no"
- `PATH`: Optional existence check

### Editor mapping (QStyledItemDelegate):

```python
def createEditor(self, parent, option, index):
    param_type = index.data(Qt.UserRole)  # Store type in item data
    
    if param_type == ParamType.INT:
        editor = QSpinBox(parent)
        editor.setRange(-2147483648, 2147483647)  # int32 range
        return editor
    
    elif param_type == ParamType.BOOL:
        editor = QComboBox(parent)
        editor.addItems(["0", "1"])
        return editor
    
    elif param_type == ParamType.PATH:
        editor = PathEditor(parent)  # Custom widget with browse button
        return editor
    
    else:  # STRING
        editor = QLineEdit(parent)
        return editor
```

---

## Relationships

```
INIEditorState (1) ──┐
                      ├──> sections (N) ──> INISection ──> parameters (N) ──> MaxINIParameter
                      └──> changes (N) ──> ParameterChange

UI Components:
    ModernHeader ──displays──> section names (tabs)
    INICanvasWidget ──displays──> parameters (QTreeWidget items)
    INICanvasWidget ──tracks──> changes (ParameterChange objects)
```

---

## Persistence

### File Format: 3dsMax.ini

```ini
[Security]
SafeSceneScriptExecutionEnabled=0
EmbeddedPythonExecutionBlocked=1

[Performance]
UndoLevels=200
ThreadCount=-1
```

**Encoding**: UTF-16 LE with BOM (0xFF 0xFE)  
**Line ending**: CRLF (Windows standard)

### Backup Files

```
3dsMax.ini                          # Current file
3dsMax.ini.bak                      # Last backup
3dsMax_20251023_150430.ini.bak     # Timestamped backup
```

**Format**: Same as original (UTF-16 LE)  
**Retention**: MaxINIBackupManager handles cleanup

---

## Validation Rules

### Type Validation

```python
def validate_value(param: MaxINIParameter, new_value: str) -> Tuple[bool, str]:
    """
    Validate new value against parameter type and constraints.
    
    Returns: (is_valid, error_message)
    """
    if param.type == ParamType.INT:
        try:
            val = int(new_value)
            if param.validation:
                if param.validation.min_value and val < param.validation.min_value:
                    return False, f"Value must be >= {param.validation.min_value}"
                if param.validation.max_value and val > param.validation.max_value:
                    return False, f"Value must be <= {param.validation.max_value}"
            return True, ""
        except ValueError:
            return False, "Must be a valid integer"
    
    elif param.type == ParamType.BOOL:
        if new_value not in ["0", "1", "true", "false", "yes", "no"]:
            return False, "Must be 0, 1, true, false, yes, or no"
        return True, ""
    
    elif param.type == ParamType.PATH:
        path = Path(new_value)
        if param.validation and param.validation.must_exist:
            if not path.exists():
                return False, f"Path does not exist: {path}"
        return True, ""
    
    else:  # STRING
        return True, ""  # No validation for strings
```

---

## Error Handling

### File Access Errors

```python
class INIFileError(Exception):
    """Base exception for INI file operations."""
    pass

class INIReadError(INIFileError):
    """Failed to read INI file."""
    pass

class INIWriteError(INIFileError):
    """Failed to write INI file (permissions, disk full, etc.)."""
    pass

class INIParseError(INIFileError):
    """Failed to parse INI file (encoding, malformed sections)."""
    pass
```

**Error recovery**:
- `INIReadError`: Show error dialog, disable editing
- `INIWriteError`: Show error, keep changes in memory, allow retry
- `INIParseError`: Show error, attempt to load valid sections, mark invalid as unreadable

---

## Performance Considerations

### Large Sections (>100 params)

**Problem**: Loading 500 parameters into QTreeWidget can cause UI freeze

**Solution**: Lazy loading with pagination
```python
PAGE_SIZE = 50

def load_section_lazy(section: INISection):
    """Load section in pages of 50 params."""
    for i in range(0, len(section.parameters), PAGE_SIZE):
        page = section.parameters[i:i+PAGE_SIZE]
        self._add_items_to_tree(page)
        if i + PAGE_SIZE < len(section.parameters):
            self._show_load_more_button()
```

**Benchmark target**: Load 500 params < 2 seconds

### Memory Usage

**Typical INI file**: ~60 sections, ~500 params total = ~50 KB в памяти  
**Changes tracking**: Dict overhead minimal (<1 KB)  
**Total memory footprint**: <1 MB (negligible)

---

## Summary

**Core entities**: 4 (MaxINIParameter, INISection, ParameterChange, INIEditorState)  
**Data flow**: Clear separation (load → display → edit → save)  
**Type safety**: Type hints на всех структурах  
**Validation**: Per-type validation с понятными error messages  
**Performance**: Lazy loading для больших секций  
**Error handling**: Graceful degradation с recovery options

**Ready for contracts definition** (Phase 1 continues) ✅

