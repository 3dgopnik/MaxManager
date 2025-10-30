"""
Add missing section translations for Advanced tab.
"""

import json
from pathlib import Path

# Missing section translations
NEW_SECTION_TRANSLATIONS = {
    "NormalBump": {"en": "Normal Bump", "ru": "Карты нормалей"},
    "HeightManagerUS_Standard": {"en": "Height Manager (US)", "ru": "Менеджер высоты (США)"},
    "HeightManagerMetric": {"en": "Height Manager (Metric)", "ru": "Менеджер высоты (метрическая)"},
    "HeightManagerCustom": {"en": "Height Manager (Custom)", "ru": "Менеджер высоты (настраиваемая)"},
    "InstalledComponents": {"en": "Installed Components", "ru": "Установленные компоненты"},
    "PluginSettings": {"en": "Plugin Settings", "ru": "Настройки плагинов"},
    "Modstack": {"en": "Modifier Stack", "ru": "Стек модификаторов"},
    "SettingsManagement": {"en": "Settings Management", "ru": "Управление настройками"},
    "Sounds": {"en": "Sounds", "ru": "Звуки"},
    "PluginKeys": {"en": "Plugin Keys", "ru": "Лицензии плагинов"},
    "CommandPanel": {"en": "Command Panel", "ru": "Командная панель"},
    "SpinnerSettings": {"en": "Spinner Settings", "ru": "Настройки спиннеров"},
    "NamedSelectionSets": {"en": "Named Selection Sets", "ru": "Именованные наборы выделения"},
    "AnimationSettings": {"en": "Animation Settings", "ru": "Настройки анимации"},
    "DisplayDrivers": {"en": "Display Drivers", "ru": "Драйверы отображения"},
    "FileHandling": {"en": "File Handling", "ru": "Обработка файлов"},
    "NetworkSettings": {"en": "Network Settings", "ru": "Сетевые настройки"},
    "CustomUI": {"en": "Custom UI", "ru": "Настройка интерфейса"},
    "ScriptSettings": {"en": "Script Settings", "ru": "Настройки скриптов"},
    "RenderPresets": {"en": "Render Presets", "ru": "Пресеты рендера"},
}


def add_missing_translations():
    """Add missing section translations to database metadata."""
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get metadata
    if '_metadata' not in data:
        data['_metadata'] = {}
    
    metadata = data['_metadata']
    
    # Get existing section translations
    if 'section_translations' not in metadata:
        metadata['section_translations'] = {}
    
    section_translations = metadata['section_translations']
    
    # Add new translations
    added = 0
    for section, trans in NEW_SECTION_TRANSLATIONS.items():
        if section not in section_translations:
            section_translations[section] = trans
            added += 1
            print(f"  [ADDED] {section}: {trans['en']} / {trans['ru']}")
        else:
            print(f"  [EXISTS] {section}")
    
    metadata['section_translations'] = section_translations
    
    if 'improvements_v2' not in metadata:
        metadata['improvements_v2'] = []
    metadata['improvements_v2'].append(f"Added {added} missing section translations for Advanced tab")
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Added {added} new section translations")
    print(f"Total section translations: {len(section_translations)}")

if __name__ == '__main__':
    add_missing_translations()

