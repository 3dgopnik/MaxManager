# План добавления таба Plugins

## Что менять:

### 1. Добавить таб в список (строка 600)
```python
# БЫЛО:
'ini': ['Security', 'Performance', 'Renderer', 'Viewport', 'Settings']

# СТАНЕТ:
'ini': ['Security', 'Performance', 'Renderer', 'Viewport', 'Settings', 'Plugins']
```

### 2. Добавить обработчик таба (после строки 728)
```python
elif category == 'ini' and tab_name == 'Plugins':
    # Load plugin parameters from database
    plugin_params = self.load_plugin_parameters()
    
    canvases = {
        'ForestPack (56)': plugin_params['forestpack'],
        'Corona (11)': plugin_params['corona'],
        'VRay (4)': plugin_params['vray'],
        # ... другие плагины
    }
```

### 3. Создать метод загрузки параметров плагинов
```python
def load_plugin_parameters(self):
    """Load plugin parameters from ultimate database"""
    # Читаем базу
    db = json.load('docs/maxini_ultimate_master_v2.json')
    
    # Группируем по ini_file
    plugins = {}
    for param_name, param_data in db.items():
        ini_file = param_data.get('ini_file')
        if ini_file != '3dsmax.ini':
            # Это плагин
            if ini_file not in plugins:
                plugins[ini_file] = []
            plugins[ini_file].append({
                'name': param_name,
                'data': param_data,
                'in_real_ini': self.check_if_in_real_ini(ini_file, param_name)
            })
    
    return plugins
```

### 4. FREE/ADVANCED логика
```python
# В FREE режиме:
if self.is_free_mode:
    # Таб Plugins disabled
    self.header.disable_tab('Plugins')
    # Или показывает unlock message
    
# В ADVANCED режиме:
if self.is_advanced_mode:
    # Таб Plugins активен
    self.header.enable_tab('Plugins')
```

---

## Структура данных для плагинов:

```python
{
    'forestpack.ini': [
        {
            'name': 'Display.cloudPointsByObject',
            'current_value': '250000',      # Из реального ini (если есть)
            'default_value': '250000',       # Из базы
            'description_en': '...',
            'description_ru': '...',
            'in_real_ini': True,            # Яркий или тусклый
            'can_edit': True/False          # Зависит от FREE/ADVANCED
        },
        ...
    ],
    'corona.ini': [...],
    ...
}
```

---

## UI свитков для плагинов:

```
▼ ForestPack (56 параметров) 💎
  [✓] cloudPointsByObject = 250000     ← В реальном ini (яркий)
  [?+] showMapInViewport              ← НЕТ в ini (тусклый)
      ℹ️ "Controls map visibility in viewport"
      [+] кнопка добавить
```

---

## Файлы которые нужно менять:

1. `src/ui/canvas_main_window.py` (добавить таб + обработчик)
2. Возможно `src/ui/modern_header.py` (если там захардкожены табы)
3. `src/modules/ini_manager.py` (поддержка нескольких ini файлов)

---

**Подтверждаешь план?** Или что-то поправить перед кодингом?

