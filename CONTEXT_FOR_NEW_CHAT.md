# Контекст для продолжения Issue #21

**Дата:** 2025-10-31  
**Issue:** #21 - Manual resize для свитков с auto-shift  
**Статус:** WIP (50% готово)  
**Причина:** Context limit 920k/1M

---

## Что сделано ✅

### 1. Resize Grip (полностью работает)
```python
# src/ui/collapsible_canvas.py, строка ~106
def create_resize_grip(self) -> QWidget:
    grip = QWidget(self)
    grip.setFixedSize(20, 20)
    grip.setCursor(Qt.SizeFDiagCursor)
    grip_pixmap = qta.icon('mdi.resize-bottom-right', color='#666666').pixmap(16, 16)
    # Event filter обрабатывает drag
```

**Работает:**
- Иконка показывается в правом нижнем углу
- Курсор меняется на resize
- Drag события логируются: `[ResizeGrip] Dragging: delta=220px`

### 2. GridLayoutManager.resize_item() (полностью работает)
```python
# src/ui/grid_layout_manager.py, строка ~284
def resize_item(self, canvas_id: str, new_span: int) -> bool:
    item.span = new_span
    self._auto_shift_after_resize(canvas_id, old_span, new_span)
```

**Работает:**
- Span обновляется в grid_manager
- Auto-shift логика: соседи переносятся на следующую строку
- Логи: `[GridLayout] Moving 'V-Ray' to next row (overlap)`

### 3. Span calculation (работает)
```python
# Thresholds:
if new_width >= base_width * 3.2: span = 4
elif new_width >= base_width * 2.2: span = 3
elif new_width >= base_width * 1.3: span = 2
else: span = 1
```

---

## Критическая проблема найдена 🔴

**Текущая архитектура:**
```python
# Сейчас: 4 VBoxLayout колонки
columns_layout = QHBoxLayout()
for i in range(4):
    col_layout = QVBoxLayout()
    columns_layout.addWidget(col_container)
```

**Проблема:**
- Canvas span=2 (width=1104px) добавляется в column 0 (width=547px)
- Canvas **обрезается** - не влезает в одну колонку!

**Решение:**
```python
# Переход на QGridLayout
grid_layout = QGridLayout()
grid_layout.addWidget(canvas, row, col, rowspan=1, colspan=span)
# QGridLayout НАТИВНО поддерживает multi-span!
```

---

## Что в процессе ⚠️

### QGridLayout refactor (50% готово)

**Сделано:**
```python
# init_ui() - строка 773
self.grid_layout = QGridLayout(self.canvas_widget)
self.grid_layout.setContentsMargins(10, 10, 10, 10)
self.grid_layout.setSpacing(10)
```

**Сделано:**
```python
# _rebuild_grid_layout() - строка 835
def _rebuild_grid_layout(self):
    # Remove all from grid
    while self.grid_layout.count() > 0:
        self.grid_layout.takeAt(0)
    
    # Calculate col_width
    col_width = (viewport_width - 20 - (cols-1)*10) // cols
    
    # Place with colspan
    for canvas_id, canvas in self.canvas_items.items():
        grid_item = self.grid_manager.items[canvas_id]
        canvas_width = grid_item.span * col_width + (grid_item.span - 1) * 10
        canvas.setFixedWidth(canvas_width)
        
        self.grid_layout.addWidget(canvas, grid_item.row, grid_item.col, 1, grid_item.span)
```

**НЕ сделано:**
- ❌ Старый код `column_layouts`, `column_containers` НЕ удален (строки 899-1050+)
- ❌ Методы ссылаются на `viewport_width`, `cols` которых нет в scope
- ❌ Файл частично сломан из-за конфликтов при replace

---

## Что нужно доделать (для нового чата)

### Шаг 1: Очистить collapsible_canvas.py

**Удалить весь старый код:**
- Строки ~894-1050: весь старый `_update_visible_columns` код
- Все references на `column_layouts`, `column_containers`
- Переменные `rows_dict`, старые placement логики

**Оставить только:**
```python
def _rebuild_grid_layout(self):
    cols = self.grid_manager.current_columns
    viewport_width = self.scroll_area.viewport().width()
    
    # Calculate col_width
    col_width = (viewport_width - 20 - (cols-1)*10) // cols
    
    # Clear grid
    while self.grid_layout.count() > 0:
        self.grid_layout.takeAt(0)
    
    # Place canvases
    for canvas_id, canvas in self.canvas_items.items():
        grid_item = self.grid_manager.items[canvas_id]
        canvas_width = grid_item.span * col_width + (grid_item.span - 1) * 10
        canvas.setFixedWidth(canvas_width)
        self.grid_layout.addWidget(canvas, grid_item.row, grid_item.col, 1, grid_item.span)
```

### Шаг 2: Исправить add_canvas()

```python
def add_canvas(self, canvas: CollapsibleCanvas, span: int = 1):
    canvas_id = canvas.title
    grid_item = self.grid_manager.add_item(canvas_id, row=0, col=0, span=span)
    self.canvas_items[canvas_id] = canvas
    # Grid будет перестроен в load_canvas_panels
```

### Шаг 3: Тестировать

1. Запустить UI
2. Потянуть grip вправо
3. Проверить: canvas растягивается до 2x/3x/4x БЕЗ обрезания
4. Проверить: соседи сдвигаются вниз

---

## Логи для диагностики

**Рабочие логи (есть сейчас):**
```
[ResizeGrip] End resize: Phoenix FD, new_span=3x
[Canvas.request_resize] CALLING container.resize_canvas('Phoenix FD', 3)
[CanvasContainer] Resize request: 'Phoenix FD' to 3x
[GridLayout] Resizing 'Phoenix FD': 1x → 3x
[GridLayout]   Moving 'V-Ray' to next row (overlap)
[GridLayout] Resize complete: Phoenix FD now 3x
```

**НО:** Визуально не работает, потому что `_rebuild_grid_layout` использует старую логику с column_layouts!

---

## Команды для нового чата

```bash
# Проверить текущее состояние
git status

# Если нужно - откатить
git checkout src/ui/collapsible_canvas.py
git checkout src/ui/grid_layout_manager.py

# Или продолжить WIP
# Начать с очистки строк 894-1050 в collapsible_canvas.py
```

---

## Ключевые файлы

1. **src/ui/collapsible_canvas.py** (строки 773-1050)
   - `init_ui()` - QGridLayout создан
   - `_rebuild_grid_layout()` - частично переписан
   - Старый код column_layouts (строки 894-1050) - УДАЛИТЬ

2. **src/ui/grid_layout_manager.py** (строки 284-347)
   - `resize_item()` - готов
   - `_auto_shift_after_resize()` - готов

3. **src/ui/canvas_main_window.py** 
   - Без изменений (работает)

---

## Важно помнить

- ✅ База в `data/ini_parameters_database.json`
- ✅ Версия в `src/__version__.py` (0.7.0)
- ✅ Все debug логи оставлять до финала
- ✅ QGridLayout - правильное решение (HTML/CSS grid аналог)
- ⚠️ Context limit - продолжить в новом чате

**Модель:** Claude Sonnet 4.5  
**Сессия:** 925k/1M (92.5%)

