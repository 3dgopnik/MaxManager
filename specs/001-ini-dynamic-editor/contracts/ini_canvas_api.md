# API Contract: INICanvasWidget

**Component**: `src/ui/ini_canvas.py::INICanvasWidget`  
**Purpose**: Canvas widget для отображения и редактирования параметров INI секции  
**Type**: Qt Widget (PySide6.QtWidgets.QWidget)

---

## Public API

### Class: INICanvasWidget

```python
class INICanvasWidget(QWidget):
    """
    Canvas widget for displaying and editing INI section parameters.
    
    Features:
    - QTreeWidget с inline editing
    - Change tracking (yellow highlights)
    - Save confirmation (green highlights)
    - Apply/Revert/Refresh buttons
    """
```

---

## Signals

### changes_made

```python
changes_made = Signal(int)
```

**Purpose**: Emitted when parameters are modified  
**Parameters**: 
- `count: int` - Number of changed parameters (total across all sections)

**Usage**:
```python
canvas.changes_made.connect(lambda count: print(f"{count} changes pending"))
```

**When emitted**:
- After user edits a parameter value
- After revert (count=0)
- After apply (count=0)

---

### save_requested

```python
save_requested = Signal()
```

**Purpose**: Emitted when user clicks Apply button  
**Parameters**: None

**Usage**:
```python
canvas.save_requested.connect(on_save)
```

**When emitted**:
- User clicks "Apply" button in canvas
- Not emitted if no changes to save

---

## Methods

### __init__

```python
def __init__(
    self,
    parent: QWidget | None = None,
    parser: MaxINIParser | None = None
) -> None:
    """
    Initialize canvas widget.
    
    Args:
        parent: Parent Qt widget
        parser: MaxINIParser instance for save/load operations
    """
```

**Contract**:
- Creates QTreeWidget with 3 columns (Parameter, Value, Type)
- Creates Apply/Revert/Refresh buttons
- Initializes change tracking dict
- Sets up delegates for inline editing

---

### load_section

```python
def load_section(
    self,
    section_name: str,
    parameters: List[MaxINIParameter]
) -> None:
    """
    Load and display parameters for a specific INI section.
    
    Args:
        section_name: Name of INI section (e.g., "Security")
        parameters: List of parameters to display
        
    Raises:
        ValueError: If section_name is empty or parameters is empty
        
    Side effects:
        - Clears current tree widget content
        - Populates tree with new parameters
        - Applies yellow highlights for pending changes (if any)
        - Resets scroll position to top
    """
```

**Performance**:
- Loads up to 50 parameters immediately
- Shows "Load More" button for additional parameters (lazy loading)
- Target: <500ms for 50 params, <2s for 500 params

**Example**:
```python
security_params = [
    MaxINIParameter(key="SafeSceneScriptExecutionEnabled", value=0, ...),
    MaxINIParameter(key="EmbeddedPythonExecutionBlocked", value=1, ...),
]
canvas.load_section("Security", security_params)
```

---

### get_modified_params

```python
def get_modified_params(self) -> List[MaxINIParameter]:
    """
    Get list of modified parameters ready for saving.
    
    Returns:
        List of MaxINIParameter objects with updated values
        
    Side effects: None
    
    Contract:
        - Returns empty list if no changes
        - Returns NEW MaxINIParameter objects (not originals)
        - Values are validated before returning
    """
```

**Example**:
```python
modified = canvas.get_modified_params()
for param in modified:
    print(f"Changed: {param.section}.{param.key} = {param.value}")
```

---

### apply_changes

```python
def apply_changes(self) -> Tuple[bool, str]:
    """
    Apply pending changes to INI file.
    
    Returns:
        (success, message): Tuple of success flag and message
        
    Side effects:
        - Creates backup via MaxINIBackupManager
        - Writes changes to INI file via MaxINIParser
        - Shows green backgrounds on saved items (2 sec)
        - Clears changes tracking dict
        - Emits save_requested signal
        
    Raises:
        INIWriteError: If file cannot be written (permissions, disk full)
        
    Contract:
        - ALWAYS creates backup before writing
        - Validates all changes before writing
        - Atomic operation (all or nothing)
        - Shows error dialog on failure (does not raise to caller)
    """
```

**Error handling**:
```python
success, msg = canvas.apply_changes()
if not success:
    print(f"Save failed: {msg}")
else:
    print(f"Saved: {msg}")
```

**Expected messages**:
- Success: "Saved 5 parameters to 3dsMax.ini"
- Failure: "Permission denied: Cannot write to 3dsMax.ini"
- Failure: "Validation failed: UndoLevels must be >= 10"

---

### revert_changes

```python
def revert_changes(self) -> int:
    """
    Discard all pending changes and reload original values.
    
    Returns:
        Number of changes discarded
        
    Side effects:
        - Clears changes tracking dict
        - Reloads current section from original parameters
        - Removes yellow backgrounds
        - Emits changes_made(0) signal
        
    Contract:
        - Does NOT modify INI file
        - Returns to pre-edit state
        - No confirmation dialog (caller handles confirmation)
    """
```

**Example**:
```python
count = canvas.revert_changes()
print(f"Discarded {count} changes")
```

---

### refresh_from_file

```python
def refresh_from_file(self) -> Tuple[bool, str]:
    """
    Reload current section from disk (external changes).
    
    Returns:
        (success, message): Tuple of success flag and message
        
    Side effects:
        - Discards any unsaved changes
        - Reloads section via MaxINIParser
        - Updates tree widget display
        - Resets changes tracking
        
    Raises:
        INIReadError: If file cannot be read
        
    Contract:
        - Shows confirmation dialog if unsaved changes exist
        - Re-parses INI file from disk
        - Updates UI with new values
    """
```

**Example**:
```python
success, msg = canvas.refresh_from_file()
if success:
    print("Refreshed from disk")
```

---

## Properties

### section_name (read-only)

```python
@property
def section_name(self) -> str | None:
    """Currently displayed section name."""
```

---

### has_unsaved_changes (read-only)

```python
@property
def has_unsaved_changes(self) -> bool:
    """True if there are pending changes."""
```

---

### change_count (read-only)

```python
@property
def change_count(self) -> int:
    """Number of modified parameters."""
```

---

## Events

### itemChanged

**Internal event**: QTreeWidget.itemChanged signal  
**Purpose**: Triggered when user edits a parameter value

**Handler**:
```python
def _on_item_changed(self, item: QTreeWidgetItem, column: int):
    """
    Handle parameter value change.
    
    Contract:
        - Validates new value against parameter type
        - Shows error tooltip if validation fails
        - Adds to changes dict if valid
        - Sets yellow background
        - Emits changes_made signal
    """
```

---

## Data Structures

### Change Tracking

```python
# Internal dict (not exposed via API)
self._changes: Dict[str, Any] = {}
# Format: {param_key: new_value}

# Original parameters (for revert)
self._original_params: List[MaxINIParameter] = []
```

---

## UI Layout

```
INICanvasWidget
├── QVBoxLayout
│   ├── QTreeWidget [90% height]
│   │   ├── Column 0: Parameter (200px width)
│   │   ├── Column 1: Value (300px width, editable)
│   │   └── Column 2: Type (80px width, read-only)
│   │
│   └── QHBoxLayout [10% height]
│       ├── QPushButton("Refresh") [left]
│       ├── Stretch [middle]
│       ├── QPushButton("Revert") [right]
│       └── QPushButton("Apply") [right, primary style]
```

---

## Styling

### Color Scheme

```python
COLORS = {
    'background': '#4D4D4D',
    'text': '#FFFFFF',
    'modified': '#FFFFCC',  # Yellow background
    'saved': '#CCFFCC',     # Green background
    'error': '#FFCCCC',     # Red background
}
```

### Button Styles

```python
# Apply button (primary)
QPushButton#applyBtn {
    background-color: #0078d4;
    color: white;
    font-weight: bold;
}

# Revert button (warning)
QPushButton#revertBtn {
    background-color: #d83b01;
    color: white;
}
```

---

## Dependencies

### Required Imports

```python
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton,
    QStyledItemDelegate
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QColor

from ..modules.maxini_parser import MaxINIParser, MaxINIParameter, ParamType
from ..modules.maxini_backup import MaxINIBackupManager
```

---

## Error Handling

### User-facing Errors

```python
# Validation error
QMessageBox.warning(
    self,
    "Invalid Value",
    f"UndoLevels must be between 10 and 500"
)

# File write error
QMessageBox.critical(
    self,
    "Save Failed",
    f"Cannot write to 3dsMax.ini:\n{error_message}"
)
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Loaded section: {section_name} ({len(params)} params)")
logger.warning(f"Validation failed for {key}: {error}")
logger.error(f"Failed to save INI: {exception}")
```

---

## Testing Contract

### Unit Tests

```python
def test_load_section():
    """Should populate tree with parameters."""
    
def test_edit_parameter():
    """Should track changes and show yellow highlight."""
    
def test_apply_changes():
    """Should save to file and show green highlight."""
    
def test_revert_changes():
    """Should discard changes and remove highlights."""
    
def test_validate_int_value():
    """Should reject non-integer values for INT params."""
```

### Integration Tests

```python
def test_save_and_reload():
    """Should persist changes to disk."""
    
def test_concurrent_edit():
    """Should detect external file modifications."""
```

---

## Performance Requirements

- Load 50 parameters: <500ms
- Load 500 parameters (lazy): <2s
- Apply changes (10 params): <1s (including backup)
- UI responsiveness: No freezes during operations

---

## Thread Safety

**Contract**: INICanvasWidget is NOT thread-safe. All operations must run on Qt main thread.

**File I/O**: Potentially blocking operations (load, save) run on main thread. For future: consider QThread for large files (>1000 params).

---

## Backward Compatibility

**Version**: 1.0.0 (initial implementation)  
**Breaking changes**: None (new component)  
**Deprecations**: None

---

## Example Usage

```python
from src.ui.ini_canvas import INICanvasWidget
from src.modules.maxini_parser import MaxINIParser

# Setup
parser = MaxINIParser()
canvas = INICanvasWidget(parent=self, parser=parser)

# Connect signals
canvas.changes_made.connect(lambda count: self.statusBar().showMessage(f"{count} changes"))
canvas.save_requested.connect(lambda: print("Saving..."))

# Load section
params = parser.load(Path("3dsMax.ini"))
security_params = [p for p in params if p.section == "Security"]
canvas.load_section("Security", security_params)

# User edits, then apply
success, msg = canvas.apply_changes()
if success:
    QMessageBox.information(self, "Success", msg)
```

---

**Contract Version**: 1.0  
**Last Updated**: 2025-10-23  
**Status**: Draft (awaiting implementation)

