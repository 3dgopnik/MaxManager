# Паттерн динамической группировки секций

## Анализ реального ini: 120 секций

### Распределение:
- Security: 3 секции
- Performance: 3 секции  
- Rendering: 14 секций
- Viewport: 5 секций
- UI/Dialogs: 7 секций
- Directories: 10 секций (+ 11 *Dirs)
- Plugins: 2 секции
- **Other: 76 секций!** (history, presets, positions, hex-codes...)

---

## Паттерн группировки (приоритет сверху вниз)

### 1. По ключевым словам (ТОЧНОЕ совпадение):
```python
KEYWORD_GROUPS = {
    'Security': ['Security', 'SecurityTools', 'Safe'],
    'Performance': ['Performance', 'OpenImageIO', 'Nitrous', 'OSL'],
    'Rendering': ['Renderer', 'Material', 'Gamma', 'Legacy'],
    'Viewport': ['WindowState', 'Selection', 'ObjectSnap', 'LAYER'],
    'Paths': ['Directories'],
}
```

### 2. По суффиксам (ПАТТЕРН):
```python
SUFFIX_GROUPS = {
    'Paths': ['Dirs', 'Paths'],  # BitmapDirs, RenderOutputDirs
    'Advanced': ['Position', 'Dialog'],  # UI state
}
```

### 3. По плагинам:
```python
PLUGIN_KEYWORDS = ['tyFlow', 'Cityscape', 'Corona', 'VRay', 'Forest']
# Если в секции есть эти слова -> Plugins
```

### 4. СКРЫВАЕМ (не показываем вообще):
```python
HIDDEN_PATTERNS = [
    r'^[0-9a-f]{8},',  # Hex-коды (ObjectSnap internal)
    r'History',        # Файловые истории
    r'MRU',            # Recent files
    r'Preset',         # Saved presets
    r'ModSet',         # Modifier sets (binary)
    r'FloaterPosition', # Dialog positions
]
```

---

## Динамическая логика

```python
def group_sections_dynamically(ini_sections):
    """Группирует секции в вкладки динамически"""
    
    tabs = {
        'Security': [],
        'Performance': [],
        'Rendering': [],
        'Viewport': [],
        'Paths': [],
        'Plugins': [],
        'Advanced': []
    }
    
    for section in ini_sections:
        # 1. Скрываем технические
        if should_hide(section):
            continue
        
        # 2. Проверяем ключевые слова
        group = match_keywords(section)
        if group:
            tabs[group].append(section)
            continue
        
        # 3. Проверяем суффиксы
        group = match_suffix(section)
        if group:
            tabs[group].append(section)
            continue
        
        # 4. Проверяем плагины
        if is_plugin(section):
            tabs['Plugins'].append(section)
            continue
        
        # 5. Всё остальное -> Advanced
        tabs['Advanced'].append(section)
    
    # Удаляем пустые вкладки
    tabs = {k: v for k, v in tabs.items() if v}
    
    return tabs
```

---

## Пример работы на твоём ini:

### Входные секции (120):
```
Security, Performance, Materials, BitmapDirs, 
RenderDialogPosition, tyFlow, 38095bc3,6822268f, ...
```

### Результат группировки:
```
Security: [Security, SecurityTools]
Performance: [Performance, OpenImageIO, Nitrous, OSL]  
Rendering: [Materials, Renderer, LegacyMaterial, ...]
Viewport: [WindowState, Selection, ObjectSnapSettings, ...]
Paths: [Directories, BitmapDirs, RenderOutputDirs, ...]
Plugins: [tyFlow, CityscapeProSettings, PluginSettings]
Advanced: [Autobackup, FileList, CuiConfiguration, ...]
```

### Скрыто (не показываем):
```
7 hex-кодов (ObjectSnap internal)
15+ History_* (файловые пути)
10+ *Position (dialog coords)
20+ ModifierSets (binary data)
```

---

## Динамика

**Если у другого пользователя**:
- Есть Corona секции → автоматом попадут в Plugins
- Есть новая секция MyCustom → если нет в паттернах, идёт в Advanced
- Нет Nitrous → вкладка Performance будет меньше

**Вкладки создаются только если есть секции!**

```python
# Если нет плагинов - нет вкладки Plugins
if not tabs['Plugins']:
    del tabs['Plugins']
```

---

## Итоговые вкладки для ТВОЕГО ini:

1. **Security** (2-3 секции) ← важные
2. **Performance** (3-5 секций) ← важные
3. **Rendering** (10-15 секций)
4. **Viewport** (5-7 секций)
5. **Paths** (20-25 секций) ← много *Dirs
6. **Plugins** (2-5 секций)
7. **Advanced** (30-40 секций) ← всё остальное полезное

**Скрыто**: ~40-50 технических секций

---

**Согласен с паттерном?** Или по-другому группировать?

