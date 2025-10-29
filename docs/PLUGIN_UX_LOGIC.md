# MaxManager INI Editor - UX Логика

## Основная концепция

**Плагин работает с РЕАЛЬНЫМ ini пользователя** + база знаний 844 параметров

---

## Режимы работы

### 🆓 FREE MODE (по умолчанию)
**Активны**: 50 критичных параметров (TOP_50_CRITICAL_PARAMETERS.md)

**Остальные 794 параметра**:
- ✅ Видны в интерфейсе
- 🔒 Disabled (серые, не редактируются)
- 💡 Показывают описание из базы
- 🎁 **Замануха**: "Unlock in Advanced Mode"

**Логика**: Пользователь видит ЧТО может получить, покупает Advanced

---

### 💎 ADVANCED MODE
**Активны**: ВСЕ 844 параметра

**Источники**:
- 756 из 3dsmax.ini
- 56 из forestpack.ini
- 11 из corona.ini
- 21 из других плагинов

**Функции**:
- Редактирование всех параметров
- Добавление новых из базы
- Экспорт/импорт конфигов

---

## UI Структура (для всех 844 параметров)

### Главное окно
```
┌─────────────────────────────────────────┐
│ MaxManager INI Editor    [FREE/ADVANCED]│
├─────────────────────────────────────────┤
│ 🔍 Search: [_________]     🎚️ Filters   │
├─────────────────────────────────────────┤
│ ┌─ Categories ─────────┐                │
│ │ ☐ Performance (125)  │                │
│ │ ☐ Security (12)      │                │
│ │ ☐ Viewport (45)      │                │
│ │ ☐ Autobackup (15)    │                │
│ │ ☐ Materials (22)     │                │
│ │ ☐ Renderer (38)      │                │
│ │ ☐ ForestPack (56) 💎 │                │
│ │ ☐ Corona (11) 💎     │                │
│ │ ☐ Other (520)        │                │
│ └──────────────────────┘                │
├─────────────────────────────────────────┤
│ ▼ Performance (25 shown, 100 filtered)  │
│ ┌─────────────────────────────────────┐ │
│ │ [+] ThreadCount = 16                │ │
│ │     ℹ️  Number of render threads    │ │
│ │                                     │ │
│ │ [+] MemoryPool = 2048      🔒       │ │
│ │     ℹ️  Memory pool size (Advanced) │ │
│ │                                     │ │
│ │ [+] UndoLevels = 20                 │ │
│ │     ℹ️  Undo stack depth            │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│         [Apply]  [Reset]  [Export]      │
└─────────────────────────────────────────┘
```

---

## Решение проблемы "много параметров"

### 1. Группировка по категориям
**8 основных категорий** + "Other"
- Каждая категория - collapsible свиток
- По умолчанию свёрнуты (кроме Performance)

### 2. Умный поиск
```
Поиск по:
- Имени параметра
- Описанию (en/ru)
- Секции INI
- Тегам (performance, security, viewport...)
```

### 3. Фильтры
```
☐ Show only FREE parameters (50)
☐ Show only modified (отличаются от дефолта)
☐ Show only from current INI file
☐ Show Advanced only 💎
```

### 4. Виртуализация списка
**Технически**:
- Рендерим только видимые 20-30 параметров
- Остальные виртуализированы (Qt Virtual List)
- Плавная прокрутка без лагов

### 5. Lazy loading
- Описания подгружаются при раскрытии свитка
- Не грузим всё сразу

---

## Источники данных

### Чтение при запуске:
1. **Реальный INI** пользователя
   ```
   C:\Users\<user>\AppData\Local\Autodesk\3dsMax\2025 - 64bit\ENU\3dsMax.ini
   ```

2. **База знаний** (844 параметра)
   ```
   maxini_ultimate_master_v2.json
   ```

3. **Мёрдж**:
   - Значения из реального INI
   - Описания из базы
   - Если параметр есть в INI но НЕТ в базе → показать с описанием "Unknown parameter"

---

## FREE vs ADVANCED визуально

### FREE параметр:
```
[✓] ThreadCount = 16
    ℹ️  Number of render threads (-1 = auto)
    [Change] [Reset to default]
```

### ADVANCED параметр (в FREE режиме):
```
[🔒] MemoryPool = 2048
    ℹ️  Memory pool size in MB
    💎 Available in Advanced Mode
    [Unlock Advanced →]
```

### ADVANCED параметр (в ADVANCED режиме):
```
[✓] MemoryPool = 2048
    ℹ️  Memory pool size in MB
    💡 Recommended: 2048-8192 depending on RAM
    [Change] [Reset to default]
```

---

## Приоритеты реализации

### MVP (Минимум):
1. ✅ Читать 3dsmax.ini
2. ✅ Показать параметры с описаниями из базы
3. ✅ FREE/ADVANCED переключатель
4. ✅ Редактирование + Apply
5. ✅ Backup перед изменением

### v2 (Расширенное):
- Поиск
- Фильтры
- Категории-свитки
- Экспорт/импорт конфигов

### v3 (Продвинутое):
- Плагинные INI (ForestPack, Corona...)
- Сравнение конфигов
- Рекомендации на основе hardware
- История изменений

---

## Технические детали

### Структура данных в памяти:
```python
{
    "ThreadCount": {
        "current_value": "16",          # Из реального INI
        "default_value": "-1",          # Из базы
        "is_modified": True,            # current != default
        "tier": "free",                 # free | advanced
        "description_en": "...",        # Из базы
        "description_ru": "...",        # Из базы
        "recommended": {...},           # Из базы
        "section": "Renderer",
        "ini_file": "3dsmax.ini",
        "in_user_ini": True             # Есть в реальном INI?
    }
}
```

### Логика Apply:
```python
def apply_changes():
    # 1. Создать backup
    backup_manager.create_backup(ini_path)
    
    # 2. Обновить только изменённые параметры
    for param in modified_params:
        if param.tier == "free" or user_mode == "advanced":
            ini_manager.set_value(param.section, param.name, param.new_value)
    
    # 3. Сохранить INI (с сохранением регистра!)
    ini_manager.save()
    
    # 4. Показать уведомление
    show_notification("Applied! Restart 3ds Max to take effect")
```

---

## Заманка FREE → ADVANCED

### Стратегии:
1. **Визуальная** - показать ВСЕ параметры, но 794 disabled
2. **Счётчик** - "Unlock 794 more parameters"
3. **Тизеры** - "Advanced users get X, Y, Z features"
4. **Примеры** - показать что можно настроить в Advanced

### Где показывать:
- Disabled параметры при клике → "Unlock in Advanced"
- Статусная строка: "50/844 parameters available (FREE)"
- Кнопка "Upgrade to Advanced" в toolbar

---

**Дата**: 2025-10-29  
**Автор**: Claude Sonnet 4.5  
**Статус**: Design Doc для реализации

