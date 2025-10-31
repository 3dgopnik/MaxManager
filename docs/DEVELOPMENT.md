# MaxManager Development Guide

**Текущая версия:** 0.7.0  
**Обновлено:** 2025-10-31

---

## 🏗 Структура проекта (КРИТИЧНО - НЕ МЕНЯТЬ!)

```
MaxManager/
├── data/                           # ЕДИНСТВЕННОЕ место для данных
│   ├── ini_parameters_database.json  # ← ОСНОВНАЯ БАЗА (916 параметров)
│   ├── presets/                      # Пресеты (будущее)
│   └── validation/                   # Правила валидации (будущее)
│
├── src/                            # Исходный код
│   ├── __version__.py               # ← ЕДИНСТВЕННЫЙ источник версии
│   ├── data/
│   │   ├── database_loader.py       # Загрузка базы из data/
│   │   └── tab_mapper.py
│   ├── modules/
│   │   ├── ini_manager.py           # Парсинг/запись INI
│   │   ├── parameter_info_loader.py # Загрузка метаданных
│   │   └── plugin_ini_finder.py     # Поиск plugin INI
│   ├── ui/
│   │   ├── canvas_main_window.py    # Главное окно
│   │   ├── collapsible_canvas.py    # Свитки
│   │   └── grid_layout_manager.py   # Grid layout
│   ├── maxscript/
│   │   └── maxmanager.mcr           # MaxScript макросы
│   └── i18n/
│       └── translations.py           # EN/RU переводы UI
│
├── docs/                           # Документация
│   ├── DEVELOPMENT.md               # ← Этот файл
│   ├── ROADMAP.md                   # План развития
│   └── VERSION_MANAGEMENT.md        # Управление версией
│
├── scripts/                        # Утилитные скрипты
│   ├── update_version.py            # Автоматический бамп версии
│   └── test_*.py                    # Тесты
│
├── Install_MaxManager.ms           # Установщик для 3ds Max
├── README.md                       # Главный README (GitHub)
└── .gitignore                      # Игнорируемые файлы
```

---

## 📦 База данных параметров

### КРИТИЧНО: Единственное место!

**Путь:** `data/ini_parameters_database.json`

**НЕ создавать:**
- ❌ Копии в других папках
- ❌ Бэкапы в git (только локально)
- ❌ Дубликаты с другими именами

**Загрузка в коде:**
```python
# src/data/database_loader.py
db_path = Path(__file__).parent.parent.parent / 'data' / 'ini_parameters_database.json'

# src/modules/parameter_info_loader.py
json_path = Path(__file__).parent.parent.parent / 'data' / 'ini_parameters_database.json'
```

### Формат базы данных

```json
{
  "_metadata": {
    "version": "2.0",
    "section_translations": {
      "Security": {"en": "Security", "ru": "Безопасность"},
      ...
    }
  },
  "Security.SafeScript": {
    "display_name": {"en": "Safe Script Execution", "ru": "Безопасное выполнение скриптов"},
    "description": {"en": "...", "ru": "..."},
    "help_text": {"en": "...", "ru": "..."},
    "type": "boolean",
    "default_value": "0",
    "recommendations": {"en": "...", "ru": "..."},
    "ini_file": "3dsmax.ini"
  },
  ...
}
```

### Статистика

- **Всего параметров:** 916
- **3ds Max Core:** ~700
- **Plugins:** V-Ray, Corona, ForestPack, PhoenixFD
- **Переводы:** EN + RU (100%)
- **Секций:** 63

---

## 🔢 Управление версией

### ЕДИНСТВЕННЫЙ источник: `src/__version__.py`

```python
__version__ = "0.7.0"  # ← МЕНЯЙ ТОЛЬКО ЗДЕСЬ
```

### Автоматическое обновление

```bash
python scripts/update_version.py 0.8.0
```

### Где отображается версия

1. **UI** (правый верхний угол): `v.0.7.0`
2. **Installer**: `MaxManager v.0.7.0 installed successfully!`
3. **README.md**: Вручную обновляется

### Импорт версии в коде

```python
from src.__version__ import __version__

# UI
version_label = QLabel(f"v.{__version__}")
```

---

## 🎨 UI Architecture

### Responsive Grid Layout (v0.7.0)

**Колонки:** 1-4 (адаптивно по ширине окна)  
**Spacing:** Ровно 10px везде  
**Drag-and-drop:** Перетаскивание свитков с иконкой ⋮⋮

**Ключевые компоненты:**
- `CanvasContainer` - главный контейнер
- `CollapsibleCanvas` - свитки (collapsible panels)
- `GridLayoutManager` - логика grid (1-4 cols), collision detection
- `LayoutStorage` - сохранение/загрузка layout

### Translate-in-place (v0.7.0)

**БЕЗ пересоздания UI!**
- Обновляет только текст на месте
- Мгновенная смена языка EN ↔ RU
- Нет крашей, нет задержек

```python
def reload_current_view(self):
    # 1. Update header tabs
    # 2. Update footer buttons
    # 3. Update canvas titles (update_language)
    # 4. Update param widgets (on_language_changed)
```

---

## 🔧 Development Workflow

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Тест UI (локально, вне 3ds Max)
python src/ui/canvas_main_window.py

# Тест в 3ds Max (основной способ)
# 1. Перетащить Install_MaxManager.ms в viewport
# 2. Customize UI → MaxManager → INI Editor
```

### Git Workflow

```bash
# 1. Локальные изменения
git add .
git commit -m "feat: новая фича"

# 2. ТЕСТИРОВАНИЕ (обязательно!)
# Запустить UI, проверить работу

# 3. Push ТОЛЬКО после подтверждения пользователя
git push origin main
```

### Правила коммитов

```
feat: новая функция
fix: исправление бага
chore: техническая работа (версия, очистка)
docs: документация
refactor: рефакторинг без изменения функционала
```

---

## 📋 Roadmap

### v0.7.0 (Текущая) ✅
- ✅ Responsive grid layout (1-4 колонки)
- ✅ Drag-and-drop для свитков
- ✅ Translate-in-place
- ✅ Layout persistence
- ✅ Plugin support (V-Ray, ForestPack, PhoenixFD)

### v0.8.0 - UI Customization
**Приоритет:** 🟢 Низкий  
**Оценка:** 1-2 недели

- [ ] Настройки цветовой схемы
- [ ] Размер шрифтов
- [ ] Компактный/расширенный режим
- [ ] Экспорт/импорт layout

### v0.9.0 - Script Manager
**Приоритет:** 🟡 Средний  
**Оценка:** 2-3 недели

- [ ] Управление startup scripts
- [ ] Редактор MaxScript
- [ ] Hotkeys настройка
- [ ] Макросы управление

### v1.0.0 - Production Release
**Приоритет:** 🔴 Высокий  
**Оценка:** 1-2 недели

- [ ] Полное тестирование
- [ ] Документация пользователя
- [ ] Инсталлятор
- [ ] Auto-update система

---

## 🐛 Known Issues

### Исправленные в v0.7.0:
- ✅ Исчезающие свитки при смене языка → translate-in-place
- ✅ Краш на Advanced tab (88 секций) → защита от deleted widgets
- ✅ Замороженная вкладка "Безопасность" → добавлен tab handler
- ✅ Header торчит из canvas → size policy fix
- ✅ "Гребенка" в полях → unified field widths

---

## 🤝 Contributing

1. **Issue-driven development** - каждая задача = GitHub Issue
2. **Локальные коммиты** → тест → push после подтверждения
3. **Структура НЕ меняется** без явного согласования
4. **База данных** - только `data/ini_parameters_database.json`

---

## 📚 References

- **GitHub:** https://github.com/3dgopnik/MaxManager
- **Issues:** https://github.com/3dgopnik/MaxManager/issues
- **Autodesk 3ds Max:** https://help.autodesk.com/view/MAXDEV/2025/

---

**Автор:** [@3dgopnik](https://github.com/3dgopnik)  
**Лицензия:** TBD

