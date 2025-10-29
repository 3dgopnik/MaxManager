# План реализации динамических вкладок и маппинга базы

## Финальная структура

### Вкладки (динамические, максимум 7):
1. **Security** (если есть секции Security, SecurityTools)
2. **Performance** (если есть Performance, OpenImageIO, Nitrous)
3. **Rendering** (если есть Renderer, Material, Gamma)
4. **Viewport** (если есть WindowState, Selection, ObjectSnap)
5. **Paths** (если есть Directories, *Dirs)
6. **Plugins** (если есть плагинные ini файлы) - ВСЕ плагины тут
7. **Advanced** (всё остальное)

### Свитки:
- Свиток = секция INI
- Название = название секции (без префиксов)
- Все свёрнуты по умолчанию

### Параметры на свитке:
- **Яркие** (активные): есть в реальном ini
- **Тусклые** (доступные): есть в базе, но НЕТ в ini
- Кнопка **+** добавляет в ini

---

## Логика маппинга

```python
# 1. Определение вкладки для секции
def get_tab_for_section(section_name, ini_file):
    # Плагины
    if ini_file != '3dsmax.ini':
        return 'Plugins'
    
    # Core вкладки (по ключевым словам)
    if 'security' in section_name.lower():
        return 'Security'
    if any(x in section_name.lower() for x in ['performance', 'openimageio', 'nitrous']):
        return 'Performance'
    if any(x in section_name.lower() for x in ['render', 'material', 'gamma']):
        return 'Rendering'
    if any(x in section_name.lower() for x in ['window', 'selection', 'snap', 'viewport']):
        return 'Viewport'
    if 'dir' in section_name.lower() or 'path' in section_name.lower():
        return 'Paths'
    
    # Всё остальное
    return 'Advanced'

# 2. Создание свитка
def create_rollout(section_name, real_params, db_params):
    rollout = Rollout(section_name)
    
    # Добавляем активные параметры (из реального ini)
    for param_name, value in real_params.items():
        widget = ParameterWidget(
            name=param_name,
            value=value,
            active=True,
            can_edit=can_edit_param(param_name)  # FREE/ADVANCED
        )
        rollout.add(widget)
    
    # Добавляем доступные параметры (из базы, тусклые)
    for param_name, param_data in db_params.items():
        if param_name not in real_params:
            widget = ParameterWidget(
                name=param_name,
                value=param_data['default'],
                active=False,  # тусклый
                dimmed=True,
                description=param_data['en']['description'],
                can_add=can_add_param()  # ADVANCED only
            )
            rollout.add(widget)
    
    return rollout

# 3. FREE vs ADVANCED
TOP_50 = ['Security.*', 'Performance.ThreadCount', 'Renderer.*', ...]

def can_edit_param(param_name):
    if mode == 'ADVANCED':
        return True
    if mode == 'FREE':
        return param_name in TOP_50
    return False

def can_add_param():
    return mode == 'ADVANCED'
```

---

## Файлы для изменения

### 1. `src/ui/canvas_main_window.py`
- Метод `get_tab_for_section()` - определение вкладки
- Метод `create_dynamic_tabs()` - создание вкладок из реального ini
- Метод `load_database_parameters()` - загрузка базы
- Метод `merge_real_and_db_params()` - слияние

### 2. `src/ui/ini_parameter_widget.py`
- Свойство `dimmed` - тусклый вид
- Кнопка `+` для добавления
- Событие `on_add_clicked()`

### 3. `src/modules/ini_manager.py`
- Метод `add_parameter()` - добавление в ini
- Backup перед изменением

### 4. `docs/maxini_ultimate_master_v2.json`
- Переименовать в `ini_parameters_database.json`

---

## Порядок реализации

1. ✅ Загрузить базу и создать маппинг секций
2. ✅ Реализовать `get_tab_for_section()`
3. ✅ Создать динамические вкладки из реального ini
4. ✅ Загрузить параметры из базы для каждой секции
5. ✅ Создать виджеты (активные + тусклые)
6. ✅ Добавить кнопку + и логику добавления
7. ✅ FREE/ADVANCED режимы
8. ✅ Backup перед изменениями

---

**Начинаю с пункта 1** ✅

