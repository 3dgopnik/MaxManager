# API Contract: MaxINI Editor Integration

**Component**: `src/ui/maxini_editor_advanced.py::AdvancedMaxINIEditor`  
**Purpose**: Integration point для динамического INI редактора  
**Type**: Qt MainWindow extensions

---

## New Methods

### load_ini_file

```python
def load_ini_file(self) -> Tuple[bool, str]:
    """
    Load and parse 3dsMax.ini file, generate dynamic tabs.
    
    Returns:
        (success, message): Success flag and status message
        
    Side effects:
        - Parses INI via MaxINIParser
        - Groups parameters by section
        - Generates dynamic tabs via header.set_context()
        - Stores sections in self.ini_sections
        - Shows first section in canvas
        
    Contract:
        - Auto-detects INI path (%APPDATA%/Autodesk/3dsMax/...)
        - Falls back to pymxs rt.getDir if available
        - Shows error dialog on failure
        - Returns (False, error_msg) on error
        
    Performance:
        - Target: <2s for typical INI (~500 params)
    """
```

**Implementation outline**:
```python
def load_ini_file(self) -> Tuple[bool, str]:
    try:
        # 1. Detect INI path
        ini_path = self._detect_ini_path()
        
        # 2. Parse INI
        parser = MaxINIParser()
        params = parser.load(ini_path)
        
        # 3. Group by section
        sections = {}
        for param in params:
            if param.section not in sections:
                sections[param.section] = []
            sections[param.section].append(param)
        
        # 4. Store sections
        self.ini_sections = sections
        self.current_ini_path = ini_path
        
        # 5. Generate tabs
        tab_names = list(sections.keys())
        self.header.set_context('ini', tab_names)
        
        # 6. Load first section
        if tab_names:
            first_section = tab_names[0]
            self.canvas.load_section(first_section, sections[first_section])
        
        return True, f"Loaded {len(params)} parameters from {len(sections)} sections"
        
    except Exception as e:
        logger.error(f"Failed to load INI: {e}")
        return False, str(e)
```

---

### _detect_ini_path

```python
def _detect_ini_path(self) -> Path:
    """
    Auto-detect 3dsMax.ini file location.
    
    Returns:
        Path to 3dsMax.ini
        
    Raises:
        FileNotFoundError: If INI not found
        
    Detection order:
        1. MaxScript API: rt.getDir(#maxroot) + "3dsMax.ini"
        2. Environment: %APPDATA%/Autodesk/3dsMax/<YEAR>/ENU/3dsMax.ini
        3. Prompt user with file dialog
    """
```

**Implementation**:
```python
def _detect_ini_path(self) -> Path:
    # Try MaxScript API
    if MAXSCRIPT_AVAILABLE:
        try:
            max_root = rt.getDir(#maxroot)
            ini_path = Path(max_root) / "3dsMax.ini"
            if ini_path.exists():
                return ini_path
        except:
            pass
    
    # Try standard path
    appdata = Path(os.environ.get('LOCALAPPDATA', ''))
    max_dir = appdata / "Autodesk" / "3dsMax"
    
    # Find latest version
    if max_dir.exists():
        versions = sorted(max_dir.glob("*64bit/ENU/3dsMax.ini"))
        if versions:
            return versions[-1]  # Latest version
    
    # Fallback: file dialog
    from PySide6.QtWidgets import QFileDialog
    path, _ = QFileDialog.getOpenFileName(
        self,
        "Select 3dsMax.ini",
        str(appdata),
        "INI Files (*.ini)"
    )
    
    if path:
        return Path(path)
    
    raise FileNotFoundError("Cannot find 3dsMax.ini")
```

---

### on_sidebar_button_clicked (modified)

```python
def on_sidebar_button_clicked(self, button_name: str) -> None:
    """
    Handle sidebar button clicks.
    
    Changes for 'ini' button:
        - Triggers load_ini_file()
        - Shows loading indicator
        - Handles errors gracefully
        
    Contract:
        - Existing behavior preserved for other buttons
        - 'ini' button now loads real INI data (not stubs)
    """
```

**New implementation for 'ini'**:
```python
def on_sidebar_button_clicked(self, button_name: str):
    if button_name == 'ini':
        # Show loading indicator
        self.statusBar().showMessage("Loading 3dsMax.ini...")
        QApplication.processEvents()  # Update UI
        
        # Load INI
        success, msg = self.load_ini_file()
        
        # Show result
        if success:
            self.statusBar().showMessage(msg, 3000)
        else:
            QMessageBox.critical(self, "Load Error", f"Failed to load INI:\n{msg}")
            self.statusBar().showMessage("Load failed", 3000)
        
        return
    
    # Existing behavior for other buttons
    ...
```

---

### on_header_tab_changed (modified)

```python
def on_header_tab_changed(self, context: str, tab_name: str) -> None:
    """
    Handle header tab changes.
    
    Changes for 'ini' context:
        - Loads section parameters into canvas
        - Updates status bar with section info
        
    Contract:
        - Existing behavior preserved for other contexts
        - 'ini' tabs now load real data (not stubs)
    """
```

**New implementation for 'ini'**:
```python
def on_header_tab_changed(self, context: str, tab_name: str):
    if context == 'ini':
        # Get section parameters
        if tab_name in self.ini_sections:
            params = self.ini_sections[tab_name]
            
            # Load into canvas
            self.canvas.load_section(tab_name, params)
            
            # Update status
            self.statusBar().showMessage(
                f"Section: {tab_name} ({len(params)} parameters)"
            )
        else:
            logger.warning(f"Section not found: {tab_name}")
        
        return
    
    # Existing behavior for other contexts
    ...
```

---

## New Attributes

### ini_sections

```python
self.ini_sections: Dict[str, List[MaxINIParameter]] = {}
```

**Purpose**: Store parsed INI sections  
**Type**: Dict mapping section name to list of parameters  
**Lifetime**: Updated on each load_ini_file() call

---

### current_ini_path

```python
self.current_ini_path: Path | None = None
```

**Purpose**: Track currently loaded INI file path  
**Type**: Path or None if not loaded  
**Usage**: For refresh operations and status display

---

### canvas

```python
self.canvas: INICanvasWidget
```

**Purpose**: Reference to canvas widget  
**Initialization**: Created in `create_content_widgets()` for 'ini' context  
**Location**: Replaces stub QLabel widgets

---

## Modified UI Initialization

### create_content_widgets (changes)

**Before** (stub widgets):
```python
self.content_widgets = {
    'ini': {
        'Security': QLabel("INI Security Settings Content"),
        'Performance': QLabel("INI Performance Settings Content"),
        ...
    }
}
```

**After** (real canvas):
```python
from .ini_canvas import INICanvasWidget

def create_content_widgets(self):
    # Create canvas for INI (shared across all sections)
    self.canvas = INICanvasWidget(parent=self, parser=MaxINIParser())
    
    # Connect signals
    self.canvas.changes_made.connect(self._on_canvas_changes)
    self.canvas.save_requested.connect(self._on_canvas_save)
    
    # Other widgets unchanged
    self.content_widgets = {
        'ui': {
            'Interface': QLabel("UI Interface Settings Content"),
            ...
        },
        'script': {...},
        'cuix': {...},
        'projects': {...}
    }
    
    # Add canvas to stack (will be shown for 'ini' context)
    self.content_stack_widget.addWidget(self.canvas)
```

---

### _on_canvas_changes

```python
def _on_canvas_changes(self, count: int) -> None:
    """
    Handle canvas changes signal.
    
    Args:
        count: Number of changed parameters
        
    Side effects:
        - Updates status bar
        - Shows unsaved changes indicator
    """
```

**Implementation**:
```python
def _on_canvas_changes(self, count: int):
    if count > 0:
        self.statusBar().showMessage(f"⚠ {count} unsaved changes", 0)
    else:
        self.statusBar().showMessage("No unsaved changes", 3000)
```

---

### _on_canvas_save

```python
def _on_canvas_save(self) -> None:
    """
    Handle canvas save request.
    
    Side effects:
        - Shows save confirmation
        - Updates status bar
    """
```

**Implementation**:
```python
def _on_canvas_save(self):
    success, msg = self.canvas.apply_changes()
    
    if success:
        QMessageBox.information(self, "Save Successful", msg)
        self.statusBar().showMessage("✓ Changes saved", 3000)
    else:
        QMessageBox.critical(self, "Save Failed", msg)
        self.statusBar().showMessage("✗ Save failed", 3000)
```

---

## Window Close Event (new)

### closeEvent (override)

```python
def closeEvent(self, event: QCloseEvent) -> None:
    """
    Handle window close event.
    
    Contract:
        - Warn user about unsaved changes
        - Allow cancel
        - Save window state
    """
```

**Implementation**:
```python
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMessageBox

def closeEvent(self, event: QCloseEvent):
    # Check for unsaved changes
    if hasattr(self, 'canvas') and self.canvas.has_unsaved_changes:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"You have {self.canvas.change_count} unsaved changes.\nDiscard changes and close?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            event.ignore()
            return
        elif reply == QMessageBox.No:
            event.ignore()
            return
        # Yes: continue closing
    
    # Accept event
    event.accept()
```

---

## Data Flow

### Initial Load (sidebar click)

```
User clicks sidebar "INI" button
    ↓
on_sidebar_button_clicked('ini')
    ↓
load_ini_file()
    ↓
├─ _detect_ini_path() → Path
├─ MaxINIParser.load(path) → List[MaxINIParameter]
├─ Group by section → Dict[str, List[MaxINIParameter]]
└─ header.set_context('ini', section_names)
    ↓
on_header_tab_changed('ini', first_section_name)
    ↓
canvas.load_section(section_name, params)
    ↓
UI shows parameters in tree widget
```

### Tab Switch

```
User clicks header tab (e.g., "Performance")
    ↓
on_header_tab_changed('ini', 'Performance')
    ↓
Get params from self.ini_sections['Performance']
    ↓
canvas.load_section('Performance', params)
    ↓
UI updates tree widget content
```

### Edit & Save

```
User edits parameter in canvas
    ↓
canvas.itemChanged signal
    ↓
canvas tracks change + yellow highlight
    ↓
canvas.changes_made signal → _on_canvas_changes(count)
    ↓
Status bar: "⚠ 5 unsaved changes"
    ↓
User clicks "Apply" in canvas
    ↓
canvas.save_requested signal → _on_canvas_save()
    ↓
canvas.apply_changes() → MaxINIParser.save()
    ↓
Success dialog + status bar: "✓ Changes saved"
```

---

## Error Handling

### File Not Found

```python
try:
    success, msg = self.load_ini_file()
except FileNotFoundError as e:
    QMessageBox.warning(
        self,
        "INI Not Found",
        "Cannot find 3dsMax.ini.\nPlease select file manually."
    )
    # Show file dialog
```

### Parse Error

```python
try:
    params = parser.load(ini_path)
except UnicodeDecodeError:
    QMessageBox.critical(
        self,
        "Encoding Error",
        "3dsMax.ini has invalid encoding.\nExpected UTF-16 LE."
    )
```

### Write Permission Error

```python
try:
    parser.save(ini_path, params)
except PermissionError:
    QMessageBox.critical(
        self,
        "Permission Denied",
        "Cannot write to 3dsMax.ini.\nClose 3ds Max or run as administrator."
    )
```

---

## Testing

### Manual Test Cases

1. **Load INI**: Click INI → verify tabs appear
2. **Switch tabs**: Click different tabs → verify content changes
3. **Edit parameter**: Double-click value → edit → verify yellow highlight
4. **Save changes**: Click Apply → verify file updated
5. **Revert changes**: Click Revert → verify yellow highlights removed
6. **Close with unsaved**: Close window with unsaved → verify warning dialog

### Automated Tests (via maxmanager_test.py)

```python
def test_load_ini_file():
    """Should load and parse INI file."""
    editor = AdvancedMaxINIEditor()
    success, msg = editor.load_ini_file()
    assert success
    assert len(editor.ini_sections) > 0

def test_tab_switch():
    """Should update canvas when switching tabs."""
    editor = AdvancedMaxINIEditor()
    editor.load_ini_file()
    editor.on_header_tab_changed('ini', 'Security')
    assert editor.canvas.section_name == 'Security'
```

---

## Dependencies

### New Imports

```python
from pathlib import Path
from typing import Dict, List, Tuple
import os
import logging

from .ini_canvas import INICanvasWidget
from ..modules.maxini_parser import MaxINIParser, MaxINIParameter
```

---

## Backward Compatibility

**Breaking changes**: None  
**New functionality**: INI editing (replaces stub widgets)  
**Existing features**: Preserved (UI, Script, CUIX, Projects stubs unchanged)

---

## Performance Requirements

- Load INI: <2s for 500 params
- Tab switch: <3s
- UI responsive during operations
- No freezes on large INI files

---

**Contract Version**: 1.0  
**Last Updated**: 2025-10-23  
**Status**: Draft (awaiting implementation)

