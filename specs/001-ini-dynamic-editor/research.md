# Research: Dynamic INI Editor Implementation

**Feature**: 001-ini-dynamic-editor  
**Date**: 2025-10-23  
**Phase**: 0 - Research & Design Decisions

## Overview

Исследование технических решений для реализации динамического редактора 3dsMax.ini с inline editing, tab scrolling, и change tracking.

---

## 1. QTreeWidget Inline Editing

### Decision: QTreeWidget с 3 колонками + QStyledItemDelegate

**Rationale**:
- QTreeWidget обеспечивает встроенный inline editing через flags
- QStyledItemDelegate позволяет кастомизировать редакторы по типу данных
- 3 колонки (Key, Value, Type) дают визуальную ясность
- Подсветка через `item.setBackground()` - простое решение

**Implementation**:
```python
# Колонки
tree.setHeaderLabels(["Parameter", "Value", "Type"])

# Inline editing для колонки Value
tree.setEditTriggers(QTreeWidget.DoubleClicked)
tree.setItemDelegateForColumn(1, INIValueDelegate())  # custom delegate

# Цветовая индикация
item.setBackground(1, QColor(255, 255, 200))  # yellow for modified
item.setBackground(1, QColor(200, 255, 200))  # green for saved
```

**Type-specific editors** через QStyledItemDelegate:
- INT: QSpinBox с min/max validation
- BOOL: QComboBox ["0", "1"] или QCheckBox
- STRING: QLineEdit с regex validation (if needed)
- PATH: QLineEdit + browse button

**Alternatives considered**:
- ❌ QTableWidget - менее гибкий для древовидной структуры (если понадобится группировка)
- ❌ Custom widget - over-engineering для простой задачи

---

## 2. Tab Scroll Mechanism

### Decision: QScrollArea + custom navigation arrows

**Rationale**:
- ModernHeader уже использует QHBoxLayout для вкладок
- QScrollArea легко оборачивает layout с горизонтальным scroll
- Custom стрелки (← →) дают больше контроля над UX
- Показываем стрелки только когда есть overflow (динамически)

**Implementation**:
```python
# Wrap tabs container in QScrollArea
scroll_area = QScrollArea()
scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
scroll_area.setWidget(tabs_container)

# Navigation arrows (show only when needed)
left_arrow = QPushButton("←")
right_arrow = QPushButton("→")

# Detect overflow
def update_arrow_visibility():
    has_overflow = tabs_container.width() > scroll_area.width()
    left_arrow.setVisible(has_overflow)
    right_arrow.setVisible(has_overflow)
```

**Scroll behavior**:
- Click arrow → scroll by 160px (1 tab width)
- Smooth scroll animation via QPropertyAnimation (optional)
- Auto-hide arrows when no overflow

**Alternatives considered**:
- ❌ QTabBar.setUsesScrollButtons() - некрасивые стандартные кнопки, сложно стилизовать
- ❌ Manual pagination - user-hostile, требует многократных кликов

---

## 3. UTF-16 LE Encoding

### Decision: Existing MaxINIParser handles it correctly ✅

**Verification**:
```python
# MaxINIParser уже корректно работает с UTF-16 LE
# src/modules/maxini_parser.py:104
with open(ini_path, encoding="utf-16-le") as f:
    content = f.read()
    if content.startswith('\ufeff'):  # Remove BOM
        content = content[1:]

# При записи
with open(ini_path, "w", encoding="utf-16-le") as f:
    f.write('\ufeff' + content)  # Add BOM
```

**Rationale**:
- MaxINIParser протестирован и работает с реальными 3dsMax.ini файлами
- BOM handling корректен (удаляем при чтении, добавляем при записи)
- Не требуется дополнительная логика

**Testing scenario**:
1. Загрузить 3dsMax.ini с кириллицей в комментариях
2. Изменить параметр
3. Сохранить
4. Проверить файл в hex editor (должен начинаться с FF FE BOM)
5. Открыть в 3ds Max (должен корректно читаться)

**No changes needed** - используем существующий MaxINIParser as-is.

---

## 4. Change Tracking Strategy

### Decision: Separate changes dict + original params snapshot

**Rationale**:
- Clean separation of concerns (original data vs modifications)
- Easy to implement Revert (discard changes dict)
- Easy to visualize changes (compare with original)
- No mutation of original MaxINIParameter objects

**Data structure**:
```python
class INICanvasWidget:
    def __init__(self):
        self.original_params: Dict[str, List[MaxINIParameter]] = {}
        self.changes: Dict[str, Dict[str, Any]] = {}
        # changes = {section: {key: new_value}}
    
    def mark_changed(self, section: str, key: str, new_value: Any):
        if section not in self.changes:
            self.changes[section] = {}
        self.changes[section][key] = new_value
        # Update visual indicator (yellow background)
    
    def apply_changes(self):
        # Merge changes into original_params
        for section, params in self.changes.items():
            for key, new_value in params.items():
                # Find param and update value
        # Save via MaxINIParser
        # Show green background briefly
        # Clear changes dict
    
    def revert_changes(self):
        # Clear changes dict
        # Reload original params to UI
        # Remove yellow backgrounds
```

**Visual feedback**:
- Modified: Yellow background (persists until Apply or Revert)
- Saved: Green background for 2 seconds → fade to white
- Original: White background

**Alternatives considered**:
- ❌ Modify MaxINIParameter.value in-place - теряем оригинал, сложно Revert
- ❌ Deep copy каждый раз - memory overhead для больших INI

---

## 5. Canvas Widget Architecture

### Decision: Custom INICanvasWidget с QTreeWidget внутри

**Rationale**:
- Инкапсуляция логики (load section, track changes, apply/revert)
- Reusable компонент (можно использовать в других контекстах)
- Clean API для maxini_editor_advanced.py

**API Design**:
```python
class INICanvasWidget(QWidget):
    """Canvas widget for displaying and editing INI parameters."""
    
    # Signals
    changes_made = Signal(int)  # emit number of changed params
    save_requested = Signal()
    
    def load_section(self, section_name: str, params: List[MaxINIParameter]):
        """Load parameters for a specific section."""
        
    def get_modified_params(self) -> List[MaxINIParameter]:
        """Get list of modified parameters ready for save."""
        
    def apply_changes(self):
        """Apply changes to INI file (calls MaxINIParser.save)."""
        
    def revert_changes(self):
        """Discard all changes and reload original values."""
        
    def refresh_from_file(self):
        """Reload current section from disk."""
```

**Composition**:
```
INICanvasWidget (QWidget)
├── QVBoxLayout
│   ├── QTreeWidget (parameters list)
│   │   └── INIValueDelegate (custom editors)
│   └── QHBoxLayout (buttons)
│       ├── QPushButton("Refresh")
│       ├── QPushButton("Revert")
│       └── QPushButton("Apply")
```

**Integration** with maxini_editor_advanced.py:
```python
def on_sidebar_button_clicked(self, button_name):
    if button_name == 'ini':
        self.load_ini_file()  # Parse INI
        tabs = list(self.ini_sections.keys())
        self.header.set_context('ini', tabs)
        
def on_header_tab_changed(self, context, tab_name):
    if context == 'ini':
        params = self.ini_sections[tab_name]
        self.canvas.load_section(tab_name, params)
```

**No deep architecture changes** - plug-and-play в существующий UI.

---

## 6. Performance Optimization

### Decision: Lazy loading + pagination для больших секций

**Rationale**:
- Некоторые секции содержат >100 параметров (e.g., [Directories])
- Загружать все сразу в QTreeWidget может вызвать UI freeze
- Lazy loading решает проблему

**Implementation**:
```python
class INICanvasWidget:
    PAGE_SIZE = 50  # Load 50 params at a time
    
    def load_section(self, section_name, params):
        self.all_params = params
        self.loaded_count = 0
        self._load_next_page()
    
    def _load_next_page(self):
        end = min(self.loaded_count + self.PAGE_SIZE, len(self.all_params))
        for param in self.all_params[self.loaded_count:end]:
            self._add_tree_item(param)
        self.loaded_count = end
        
        # Show "Load More" button if not all loaded
        if self.loaded_count < len(self.all_params):
            self.show_load_more_button()
```

**Alternative**: Virtual scrolling (QAbstractItemModel) - overkill для этой задачи.

**Benchmark goal**: Загрузка секции с 500 параметрами < 2 сек.

---

## 7. Color Feedback Timing

### Decision: Green fade animation 2 секунды

**Rationale**:
- Достаточно времени чтобы пользователь заметил успех
- Не раздражает (не слишком долго)
- Industry standard (Windows, macOS используют 1.5-2 сек)

**Implementation**:
```python
def show_save_success(self, item: QTreeWidgetItem):
    # Green background
    item.setBackground(1, QColor(200, 255, 200))
    
    # Fade to white after 2 seconds
    QTimer.singleShot(2000, lambda: item.setBackground(1, QColor(255, 255, 255)))
```

**Animation** (optional enhancement):
- QPropertyAnimation для smooth fade
- Не критично для MVP

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Canvas | QTreeWidget + QStyledItemDelegate | Встроенный inline editing, type-specific editors |
| Tab scroll | QScrollArea + custom arrows | Гибкость, красивый UX, dynamic visibility |
| Encoding | Use existing MaxINIParser | Уже работает корректно, протестирован |
| Change tracking | Separate changes dict | Clean separation, easy Revert |
| Architecture | Custom INICanvasWidget | Инкапсуляция, reusability, clean API |
| Performance | Lazy loading (50 params/page) | UI responsive для больших секций |
| Color timing | Green fade 2 sec | User-friendly, industry standard |

---

## Implementation Order

1. **INICanvasWidget skeleton** (empty widget с кнопками)
2. **QTreeWidget setup** (3 колонки, basic items)
3. **Inline editing** (QStyledItemDelegate для Value колонки)
4. **Change tracking** (yellow highlight на edit)
5. **Apply/Revert** (save через MaxINIParser, clear changes)
6. **Tab scroll** (QScrollArea + arrows в ModernHeader)
7. **Load INI** (parse при клике на INI sidebar button)
8. **Integration** (connect all pieces в maxini_editor_advanced.py)
9. **Polish** (green fade, validation, error handling)

**Total estimated LOC**: ~300-400 lines (один новый файл + модификации существующих)

**No research blockers** - все решения clear, можно начинать Phase 1 (Data Model).

