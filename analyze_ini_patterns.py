#!/usr/bin/env python3
"""Analyze patterns in INI sections for smart grouping"""
import re
from collections import defaultdict

ini_path = r'C:\Users\acherednikov\AppData\Local\Autodesk\3dsMax\2025 - 64bit\ENU\3dsMax.ini'

with open(ini_path, 'r', encoding='utf-16-le') as f:
    content = f.read()

sections = re.findall(r'\[([^\]]+)\]', content)

print("=" * 80)
print("ПАТТЕРНЫ ГРУППИРОВКИ В INI")
print("=" * 80)

# Анализ 1: По суффиксам
suffixes = defaultdict(list)
for section in sections:
    # *Dirs, *Params, *Settings, etc
    match = re.search(r'(\w+)(Dirs|Params|Settings|Position|Manager)$', section)
    if match:
        suffix = match.group(2)
        suffixes[suffix].append(section)
    else:
        suffixes['Other'].append(section)

print("\n1. ГРУППИРОВКА ПО СУФФИКСАМ:")
for suffix, secs in sorted(suffixes.items(), key=lambda x: -len(x[1])):
    print(f"  *{suffix}: {len(secs)} секций")
    if len(secs) <= 5:
        for s in secs:
            print(f"    - {s}")

# Анализ 2: По ключевым словам
keywords = {
    'Security': ['Security', 'Safe'],
    'Performance': ['Performance', 'OpenImageIO', 'Nitrous'],
    'Rendering': ['Render', 'Material', 'Gamma', 'Legacy'],
    'Viewport': ['Window', 'Selection', 'Snap'],
    'Directories': ['Directories', 'Dirs', 'Path'],
    'UI': ['Dialog', 'Position', 'Floater'],
    'Plugins': ['tyFlow', 'Cityscape', 'Forest', 'Corona', 'VRay']
}

keyword_groups = defaultdict(list)
for section in sections:
    matched = False
    for group, kws in keywords.items():
        if any(kw.lower() in section.lower() for kw in kws):
            keyword_groups[group].append(section)
            matched = True
            break
    if not matched:
        keyword_groups['Other'].append(section)

print("\n2. ГРУППИРОВКА ПО КЛЮЧЕВЫМ СЛОВАМ:")
for group, secs in sorted(keyword_groups.items(), key=lambda x: -len(x[1])):
    print(f"  {group}: {len(secs)} секций")

# Анализ 3: Hex-коды (странные секции)
hex_sections = [s for s in sections if re.match(r'^[0-9a-f]{8},', s)]
print(f"\n3. HEX-КОДЫ (ObjectSnap плагины): {len(hex_sections)}")
for s in hex_sections:
    print(f"  - {s}")

print("\n" + "=" * 80)
print("ПРЕДЛОЖЕНИЕ ПАТТЕРНА ГРУППИРОВКИ:")
print("=" * 80)

pattern = """
1. ПО КЛЮЧЕВЫМ СЛОВАМ (приоритет):
   - Security → вкладка Security
   - Performance, OpenImageIO, Nitrous → вкладка Performance
   - Render*, Material*, Gamma → вкладка Rendering
   - Window*, Selection, Snap → вкладка Viewport
   
2. ПО СУФФИКСАМ:
   - *Dirs, Directories, Paths → вкладка Paths
   - *Position, *Dialog → вкладка Advanced
   - *Params → группа Textures (или скрыть)
   
3. ПЛАГИНЫ:
   - tyFlow, Cityscape → вкладка Plugins (из 3dsmax.ini)
   - + отдельные ini файлы плагинов
   
4. СКРЫТЬ:
   - History_* (файловые пути)
   - Dialog positions (UI state)
   - Preset* (сохраненные пресеты)
   - Hex-коды (внутренние плагины)
   - ModifierSets (бинарные данные)
"""

print(pattern)

# Финальная группировка
final_tabs = {
    'Security': [],
    'Performance': [],
    'Rendering': [],
    'Viewport': [],
    'Paths': [],
    'Plugins': [],
    'Advanced': []
}

for section in sections:
    s_lower = section.lower()
    
    # Скрываем технические
    if any(x in s_lower for x in ['history', 'mru', 'preset', 'modset']):
        continue
    if re.match(r'^[0-9a-f]{8},', section):  # hex codes
        continue
    
    # Группируем
    if 'security' in s_lower or 'safe' in s_lower:
        final_tabs['Security'].append(section)
    elif any(x in s_lower for x in ['performance', 'openimageio', 'nitrous', 'osl']):
        final_tabs['Performance'].append(section)
    elif any(x in s_lower for x in ['render', 'material', 'gamma', 'legacy']):
        final_tabs['Rendering'].append(section)
    elif any(x in s_lower for x in ['window', 'selection', 'snap', 'viewport']):
        final_tabs['Viewport'].append(section)
    elif 'dir' in s_lower or 'path' in s_lower:
        final_tabs['Paths'].append(section)
    elif any(x in s_lower for x in ['tyflow', 'cityscape', 'plugin']):
        final_tabs['Plugins'].append(section)
    else:
        final_tabs['Advanced'].append(section)

print("\nФИНАЛЬНЫЕ ВКЛАДКИ:")
for tab, secs in final_tabs.items():
    if secs:
        print(f"{tab}: {len(secs)} секций")

print("\n" + "=" * 80)

