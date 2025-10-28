# MaxManager Roadmap

Планы развития проекта MaxManager с приоритетами и оценками.

---

## 🎯 Текущий этап: v0.5.0 - Базовый UI и INI парсинг

### ✅ Завершено:
- [x] Modern UI с sidebar/header/canvas
- [x] Collapsible canvas панели
- [x] INI parameter widgets (toggle, spinbox, slider, path, string)
- [x] Help tooltips для параметров
- [x] Контекстное меню (Expand/Collapse All)
- [x] Индикаторы изменений (save/undo)
- [x] Унифицированные стили (7.5px скругление, tooltips, меню)

### 🔄 В процессе:
- [ ] Чтение INI файлов (парсинг)
- [ ] Запись INI файлов (сохранение изменений)
- [ ] Валидация значений параметров
- [ ] Применение изменений в 3ds Max

---

## 📋 Backlog - Запланированные фичи

### v0.6.0 - INI Editor Core
**Приоритет:** 🔴 Высокий  
**Оценка:** 2-3 недели

- [ ] Полный парсинг 3dsmax.ini
- [ ] Запись изменений обратно в INI
- [ ] Резервное копирование перед изменениями
- [ ] История изменений (undo/redo)
- [ ] Поиск по параметрам
- [ ] Фильтрация параметров

---

### v0.7.0 - Advanced Canvas Layout (Grid + Resize)
**Приоритет:** 🟡 Средний  
**Оценка:** 3-4 недели  
**Статус:** Отложено до завершения базового функционала

#### 🎨 Концепция:
Продвинутая система управления canvas панелями с grid layout и изменяемыми размерами.

#### 📐 Функциональность:

**1. Grid Layout (размещение рядом):**
```
┌─────────────────┬─────────────────┐
│ Script          │ File Access     │  ← 2 свитка в ряд
│ Execution       │                 │
│                 │                 │
├─────────────────┴─────────────────┤
│ Plugin Security                   │  ← на всю ширину
│                                   │
└───────────────────────────────────┘
```

**2. Drag & Drop (перетаскивание):**
- Хватаешь за header панели
- Перетаскиваешь в любую позицию grid
- Панели автоматически адаптируются

**3. Resize (изменение размера):**
- Уголок справа-снизу (⟋) для resize
- Изменение ширины И высоты
- Минимальные/максимальные ограничения

#### 🔧 Технические детали:

**Ограничения размеров:**
```python
# Минимальная ширина
min_width = max_parameter_width + padding
# Пример: [?] LongParamName [Input...] [Browse] = ~400px

# Минимальная высота
min_height = header_height + min_one_param = 70px

# Максимальная ширина
max_width = canvas_container_width

# Максимальная высота
max_height = auto (по контенту) или canvas_container_height
```

**Архитектура:**
```
CanvasContainer
  ↓
QGridLayout (вместо QVBoxLayout)
  ↓
ResizableCanvasWrapper (новый класс)
  ├─ CollapsibleCanvas (свиток)
  ├─ DragHandle (header для drag&drop)
  └─ ResizeHandle (⟋ уголок)
```

**Конфигурация (сохранение layout):**
```json
{
  "canvas_layout": {
    "grid": [
      {
        "id": "script_execution",
        "row": 0,
        "col": 0,
        "width": 400,
        "height": 300,
        "expanded": true
      },
      {
        "id": "file_access",
        "row": 0,
        "col": 1,
        "width": 350,
        "height": 250,
        "expanded": true
      }
    ]
  }
}
```

#### 📊 Оценка работ:
- **Этап 1:** Система ID + min/max размеры + ResizeHandle (30-50 calls)
- **Этап 2:** Grid Layout + Drag & Drop (50-80 calls)
- **Этап 3:** Сохранение/загрузка конфига (20-30 calls)
- **Итого:** ~100-160 tool calls

#### ⚠️ Сложности:
- QGridLayout не поддерживает resize напрямую → нужен кастомный layout
- Сложная система сохранения/восстановления позиций
- Адаптивность при resize окна (2-column ↔ 1-column)

#### 💡 Примечания:
- Нужна система уникальных ID для каждой canvas панели
- Сохранение в config.json или отдельный layout.json
- Возможность сброса layout к дефолтному

---

### v0.8.0 - UI Customization
**Приоритет:** 🟢 Низкий  
**Оценка:** 1-2 недели

- [ ] Настройки цветовой схемы
- [ ] Размер шрифтов
- [ ] Компактный/расширенный режим
- [ ] Экспорт/импорт layout

---

### v0.9.0 - Script Manager
**Приоритет:** 🟡 Средний  
**Оценка:** 2-3 недели

- [ ] Управление startup scripts
- [ ] Редактор MaxScript
- [ ] Hotkeys настройка
- [ ] Макросы управление

---

### v1.0.0 - Production Release
**Приоритет:** 🔴 Высокий  
**Оценка:** 1-2 недели

- [ ] Полное тестирование
- [ ] Документация пользователя
- [ ] Инсталлятор
- [ ] Auto-update система

---

## 🔮 Будущие идеи (v1.x+)

### Интеграция с 3ds Max:
- [ ] Real-time preview изменений
- [ ] Профили для разных проектов
- [ ] Синхронизация с облаком
- [ ] Плагины marketplace

### Advanced Features:
- [ ] AI-powered recommendations
- [ ] Performance monitoring
- [ ] Batch operations на несколько файлов
- [ ] Comparison tool (diff INI files)

---

## 📝 Changelog

### v0.5.0 (Текущая)
- Базовый UI завершен
- Canvas система с параметрами
- Help tooltips
- Контекстные меню

---

**Обновлено:** 2025-10-27

