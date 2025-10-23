# Quick Start: Dynamic INI Editor Implementation

**Feature**: 001-ini-dynamic-editor  
**Date**: 2025-10-23  
**For**: Developers implementing this feature

---

## 🎯 Goal

Реализовать динамический редактор 3dsMax.ini с автогенерацией вкладок из секций INI и inline editing параметров.

---

## 📋 Prerequisites

**Установленное**:
- Python 3.10+ (встроен в 3ds Max)
- PySide6 (встроен в 3ds Max)
- MaxManager repository клонирован

**Прочитать**:
- [spec.md](./spec.md) - Функциональные требования
- [plan.md](./plan.md) - Технический план
- [research.md](./research.md) - Дизайн решения
- [data-model.md](./data-model.md) - Структуры данных

---

## 🚀 Implementation Steps

### Step 1: Create INICanvasWidget (60 min)

**File**: `src/ui/ini_canvas.py` (NEW)

**Tasks**:
```python
# 1. Create widget skeleton
class INICanvasWidget(QWidget):
    changes_made = Signal(int)
    save_requested = Signal()
    
    def __init__(self, parent=None, parser=None):
        # Setup QTreeWidget (3 columns)
        # Setup buttons (Apply, Revert, Refresh)
        # Initialize change tracking

# 2. Implement load_section()
def load_section(self, section_name, parameters):
    # Clear tree
    # Populate with params
    # Apply yellow highlights for pending changes

# 3. Implement change tracking
def _on_item_changed(self, item, column):
    # Validate new value
    # Add to changes dict
    # Set yellow background
    # Emit changes_made signal
```

**Test**:
```bash
python maxmanager_test.py
# Verify: Canvas displays parameters, inline editing works
```

**Time estimate**: 60 minutes

---

### Step 2: Implement QStyledItemDelegate (30 min)

**File**: `src/ui/ini_canvas.py` (same file)

**Tasks**:
```python
class INIValueDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        # Get param type from item data
        # Return appropriate editor:
        #   INT → QSpinBox
        #   BOOL → QComboBox ["0", "1"]
        #   STRING → QLineEdit
        #   PATH → QLineEdit + browse button
    
    def setEditorData(self, editor, index):
        # Load current value into editor
    
    def setModelData(self, editor, model, index):
        # Save edited value to model
```

**Test**:
```python
# In maxmanager_test.py
# Edit int param → verify QSpinBox appears
# Edit bool param → verify QComboBox appears
```

**Time estimate**: 30 minutes

---

### Step 3: Implement Apply/Revert/Refresh (45 min)

**File**: `src/ui/ini_canvas.py`

**Tasks**:
```python
def get_modified_params(self):
    # Build list of MaxINIParameter with updated values
    # Return list

def apply_changes(self):
    # Create backup via MaxINIBackupManager
    # Get modified params
    # Save via MaxINIParser.save()
    # Show green backgrounds (2 sec timer)
    # Clear changes dict
    # Emit save_requested signal

def revert_changes(self):
    # Clear changes dict
    # Reload section from original params
    # Remove yellow backgrounds
    # Emit changes_made(0)

def refresh_from_file(self):
    # Show confirmation if unsaved changes
    # Re-parse INI from disk
    # Update tree widget
```

**Test**:
```bash
python maxmanager_test.py
# 1. Edit params → click Apply → verify file updated
# 2. Edit params → click Revert → verify changes discarded
# 3. External edit → click Refresh → verify reloaded
```

**Time estimate**: 45 minutes

---

### Step 4: Integrate with AdvancedMaxINIEditor (45 min)

**File**: `src/ui/maxini_editor_advanced.py` (MODIFY)

**Tasks**:
```python
# 1. Add imports
from .ini_canvas import INICanvasWidget
from ..modules.maxini_parser import MaxINIParser

# 2. Add attributes
def __init__(self):
    ...
    self.ini_sections: Dict[str, List[MaxINIParameter]] = {}
    self.current_ini_path: Path | None = None
    self.canvas: INICanvasWidget | None = None

# 3. Modify create_content_widgets()
def create_content_widgets(self):
    # Create canvas (shared for all INI tabs)
    self.canvas = INICanvasWidget(parent=self, parser=MaxINIParser())
    self.canvas.changes_made.connect(self._on_canvas_changes)
    self.canvas.save_requested.connect(self._on_canvas_save)
    self.content_stack_widget.addWidget(self.canvas)
    
    # Keep other widgets unchanged

# 4. Implement load_ini_file()
def load_ini_file(self):
    # Detect INI path
    # Parse via MaxINIParser
    # Group by section
    # Generate tabs
    # Load first section

# 5. Modify on_sidebar_button_clicked()
def on_sidebar_button_clicked(self, button_name):
    if button_name == 'ini':
        self.load_ini_file()
        return
    # ... existing code

# 6. Modify on_header_tab_changed()
def on_header_tab_changed(self, context, tab_name):
    if context == 'ini':
        params = self.ini_sections[tab_name]
        self.canvas.load_section(tab_name, params)
        self.content_stack_widget.setCurrentWidget(self.canvas)
        return
    # ... existing code
```

**Test**:
```bash
python maxmanager_test.py
# 1. Click INI sidebar → verify tabs appear
# 2. Click tab → verify canvas updates
# 3. Edit param → verify yellow highlight
```

**Time estimate**: 45 minutes

---

### Step 5: Add Tab Scrolling to ModernHeader (30 min)

**File**: `src/ui/modern_header.py` (MODIFY)

**Tasks**:
```python
# 1. Wrap tabs in QScrollArea
def __init__(self):
    ...
    # Create scroll area
    self.scroll_area = QScrollArea()
    self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.scroll_area.setWidget(self.tabs_container)
    
    # Add navigation arrows
    self.left_arrow = QPushButton("←")
    self.right_arrow = QPushButton("→")
    self.left_arrow.clicked.connect(self._scroll_left)
    self.right_arrow.clicked.connect(self._scroll_right)
    
    # Layout: [←] [scroll_area] [→]
    header_layout.addWidget(self.left_arrow)
    header_layout.addWidget(self.scroll_area)
    header_layout.addWidget(self.right_arrow)

# 2. Implement scroll functions
def _scroll_left(self):
    current = self.scroll_area.horizontalScrollBar().value()
    self.scroll_area.horizontalScrollBar().setValue(current - 160)

def _scroll_right(self):
    current = self.scroll_area.horizontalScrollBar().value()
    self.scroll_area.horizontalScrollBar().setValue(current + 160)

# 3. Dynamic arrow visibility
def _update_arrow_visibility(self):
    has_overflow = self.tabs_container.width() > self.scroll_area.width()
    self.left_arrow.setVisible(has_overflow)
    self.right_arrow.setVisible(has_overflow)

# Call on resize and tab addition
```

**Test**:
```bash
python maxmanager_test.py
# Load INI with >10 sections
# Verify: arrows appear, scrolling works
```

**Time estimate**: 30 minutes

---

### Step 6: Add _detect_ini_path() (20 min)

**File**: `src/ui/maxini_editor_advanced.py`

**Tasks**:
```python
def _detect_ini_path(self) -> Path:
    # 1. Try MaxScript API
    if MAXSCRIPT_AVAILABLE:
        max_root = rt.getDir(#maxroot)
        ini_path = Path(max_root) / "3dsMax.ini"
        if ini_path.exists():
            return ini_path
    
    # 2. Try standard path
    appdata = Path(os.environ.get('LOCALAPPDATA', ''))
    max_dir = appdata / "Autodesk" / "3dsMax"
    versions = sorted(max_dir.glob("*/ENU/3dsMax.ini"))
    if versions:
        return versions[-1]
    
    # 3. File dialog
    from PySide6.QtWidgets import QFileDialog
    path, _ = QFileDialog.getOpenFileName(
        self, "Select 3dsMax.ini", str(appdata), "INI Files (*.ini)"
    )
    if path:
        return Path(path)
    
    raise FileNotFoundError("Cannot find 3dsMax.ini")
```

**Test**:
```python
# Standalone test
path = editor._detect_ini_path()
assert path.exists()
assert path.name == "3dsMax.ini"
```

**Time estimate**: 20 minutes

---

### Step 7: Add closeEvent handler (10 min)

**File**: `src/ui/maxini_editor_advanced.py`

**Tasks**:
```python
def closeEvent(self, event):
    if hasattr(self, 'canvas') and self.canvas.has_unsaved_changes:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            f"You have {self.canvas.change_count} unsaved changes.\n"
            "Discard and close?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply != QMessageBox.Yes:
            event.ignore()
            return
    event.accept()
```

**Test**:
```bash
# Make changes → close window → verify warning appears
```

**Time estimate**: 10 minutes

---

### Step 8: Polish & Error Handling (30 min)

**Tasks**:
- Add loading indicator (QProgressDialog or status bar)
- Add validation error tooltips
- Add logging statements
- Test error scenarios (file not found, permission denied)
- Add type hints to all functions
- Add docstrings

**Test**:
```bash
# Error scenarios:
# 1. No 3dsMax.ini → verify error dialog
# 2. Read-only INI → verify save error
# 3. Invalid value → verify validation error tooltip
```

**Time estimate**: 30 minutes

---

## 🧪 Testing

### Unit Tests (optional для этой фичи)

```python
# tests/unit/test_ini_canvas.py
def test_load_section():
    canvas = INICanvasWidget()
    params = [MaxINIParameter(...), ...]
    canvas.load_section("Security", params)
    assert canvas.tree.topLevelItemCount() == len(params)

def test_track_changes():
    canvas = INICanvasWidget()
    # ... edit parameter
    assert canvas.change_count == 1
```

### Integration Test (обязательно)

```bash
# maxmanager_test.py
python maxmanager_test.py
```

**Test cases**:
1. ✅ Canvas loads parameters
2. ✅ Inline editing works
3. ✅ Yellow highlights appear on edit
4. ✅ Apply saves to file
5. ✅ Green highlights appear after save
6. ✅ Revert discards changes
7. ✅ Tab scrolling works (if >10 tabs)

### Manual Test in 3ds Max

```maxscript
-- Install
fileIn @"C:\MaxManager\Install_MaxManager.ms"

-- Launch
macros.run "MaxManager" "MaxManager_INIEditor"
```

**Test cases**:
1. ✅ Click INI → tabs appear
2. ✅ Switch tabs → content updates
3. ✅ Edit param → save → verify in 3ds Max
4. ✅ Close with unsaved → warning appears

---

## 📊 Progress Tracking

| Step | Task | Time | Status |
|------|------|------|--------|
| 1 | INICanvasWidget skeleton | 60m | ⏳ |
| 2 | QStyledItemDelegate | 30m | ⏳ |
| 3 | Apply/Revert/Refresh | 45m | ⏳ |
| 4 | Integration with Editor | 45m | ⏳ |
| 5 | Tab scrolling | 30m | ⏳ |
| 6 | Auto-detect INI path | 20m | ⏳ |
| 7 | Close event handler | 10m | ⏳ |
| 8 | Polish & error handling | 30m | ⏳ |
| **Total** | | **4h 30m** | |

---

## 🔧 Development Tips

### Fast Iteration

```bash
# Edit code
# Test immediately (no 3ds Max restart)
python maxmanager_test.py
```

### Debugging

```python
# Add debug prints
logger.debug(f"Loaded {len(params)} params")
print(f"Changes: {self._changes}")

# Or use debugger
import pdb; pdb.set_trace()
```

### Common Issues

**Issue**: QTreeWidget не отображает изменения  
**Fix**: Вызывай `tree.update()` после изменений

**Issue**: Inline editing не работает  
**Fix**: Проверь флаги: `tree.setEditTriggers(QTreeWidget.DoubleClicked)`

**Issue**: UTF-16 LE encoding errors  
**Fix**: Используй `MaxINIParser` (он уже корректно работает)

---

## 📝 Code Style

### Type Hints (обязательно)

```python
def load_section(
    self,
    section_name: str,
    parameters: List[MaxINIParameter]
) -> None:
    ...
```

### Docstrings (обязательно)

```python
def apply_changes(self) -> Tuple[bool, str]:
    """
    Apply pending changes to INI file.
    
    Returns:
        (success, message): Success flag and status message
        
    Raises:
        INIWriteError: If file cannot be written
    """
```

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Loaded {len(params)} parameters")
logger.warning(f"Validation failed: {error}")
logger.error(f"Save failed: {exception}")
```

---

## 🎓 Resources

### Documentation
- [PySide6 QTreeWidget](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTreeWidget.html)
- [QStyledItemDelegate](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QStyledItemDelegate.html)
- [Python configparser](https://docs.python.org/3/library/configparser.html)

### Existing Code
- `src/modules/maxini_parser.py` - INI parsing/writing
- `src/modules/maxini_backup.py` - Backup management
- `src/ui/modern_sidebar.py` - Sidebar example
- `src/ui/modern_header.py` - Header example

---

## ✅ Definition of Done

- [ ] INICanvasWidget created and functional
- [ ] Inline editing works for all param types
- [ ] Change tracking (yellow highlights) works
- [ ] Apply/Revert/Refresh buttons work
- [ ] Tab scrolling works for >10 tabs
- [ ] Integration with maxini_editor_advanced complete
- [ ] `python maxmanager_test.py` passes
- [ ] Manual test in 3ds Max successful
- [ ] Type hints на всех функциях
- [ ] Docstrings на всех публичных методах
- [ ] Error handling для file I/O
- [ ] Commit локально с осмысленным сообщением
- [ ] User (Alexey) протестировал и одобрил

---

## 🚀 Next Steps After Implementation

1. **Commit локально**:
   ```bash
   git add .
   git commit -m "feat: dynamic INI editor with inline editing"
   ```

2. **User testing**: Alexey тестирует в 3ds Max

3. **Iterative fixes**: Если баги → fix → commit → test again

4. **Update documentation**:
   - CHANGELOG.md
   - README.md (если нужно)

5. **Push after approval**:
   ```bash
   git push origin 001-ini-dynamic-editor
   ```

6. **Create GitHub Issue** и закрыть после merge

---

**Ready to start coding?** Следуй шагам 1-8 последовательно! 🔥

