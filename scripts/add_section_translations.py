"""
Add section name translations to database metadata.
"""

import json
from pathlib import Path

# Section name translations
SECTION_TRANSLATIONS = {
    # Main 3dsMax sections
    "Security": {"en": "Security", "ru": "Безопасность"},
    "SecurityTools": {"en": "Security Tools", "ru": "Инструменты безопасности"},
    "SecurityMessagesWindow": {"en": "Security Messages Window", "ru": "Окно сообщений безопасности"},
    "Performance": {"en": "Performance", "ru": "Производительность"},
    "Renderer": {"en": "Renderer", "ru": "Рендерер"},
    "OpenImageIO": {"en": "OpenImageIO", "ru": "OpenImageIO"},
    "Materials": {"en": "Materials", "ru": "Материалы"},
    "Material Editor": {"en": "Material Editor", "ru": "Редактор материалов"},
    "Selection": {"en": "Selection", "ru": "Выделение"},
    "WindowState": {"en": "Window State", "ru": "Состояние окна"},
    "Nitrous": {"en": "Nitrous Viewport", "ru": "Вьюпорт Nitrous"},
    "Viewport": {"en": "Viewport", "ru": "Вьюпорт"},
    "Directories": {"en": "Directories", "ru": "Директории"},
    "MAXScript": {"en": "MAXScript", "ru": "MAXScript"},
    "Autobackup": {"en": "Auto Backup", "ru": "Автосохранение"},
    "CuiConfiguration": {"en": "UI Configuration", "ru": "Конфигурация интерфейса"},
    "LegacyMaterial": {"en": "Legacy Materials", "ru": "Устаревшие материалы"},
    "ObjectSnapSettings": {"en": "Object Snap Settings", "ru": "Настройки привязки"},
    "MissingPathCache": {"en": "Missing Path Cache", "ru": "Кэш отсутствующих путей"},
    "FileList": {"en": "File List", "ru": "Список файлов"},
    "Paths": {"en": "Paths", "ru": "Пути"},
    "WelcomeScreen": {"en": "Welcome Screen", "ru": "Экран приветствия"},
    "PreferencesDialog": {"en": "Preferences Dialog", "ru": "Диалог настроек"},
    "SceneConverter": {"en": "Scene Converter", "ru": "Конвертер сцен"},
    "SpinnerPrecision": {"en": "Spinner Precision", "ru": "Точность спиннеров"},
    "ModifierSets": {"en": "Modifier Sets", "ru": "Наборы модификаторов"},
    "VertexNormals": {"en": "Vertex Normals", "ru": "Нормали вершин"},
    "LAYER": {"en": "Layers", "ru": "Слои"},
    
    # Plugin sections
    "Forestpack": {"en": "ForestPack", "ru": "ForestPack"},
    "Phoenixfd": {"en": "Phoenix FD", "ru": "Phoenix FD"},
    "Vray": {"en": "V-Ray", "ru": "V-Ray"},
    "options": {"en": "ForestPack Options", "ru": "Настройки ForestPack"},
    "Pflow": {"en": "Particle Flow", "ru": "Поток частиц"},
    "Preview": {"en": "Preview", "ru": "Предпросмотр"},
    "Logging": {"en": "Logging", "ru": "Логирование"},
    "Keyboard": {"en": "Keyboard", "ru": "Клавиатура"},
    "Gui": {"en": "GUI", "ru": "Интерфейс"},
    "Cache": {"en": "Cache", "ru": "Кэш"},
    "Global Options": {"en": "Global Options", "ru": "Глобальные настройки"},
    "Scene Convert Options": {"en": "Scene Conversion", "ru": "Конвертация сцены"},
    "Advanced Convert Options": {"en": "Advanced Conversion", "ru": "Продвинутая конвертация"},
    "Advanced Tools Options": {"en": "Advanced Tools", "ru": "Продвинутые инструменты"},
    "Batch Process Settings": {"en": "Batch Processing", "ru": "Пакетная обработка"},
}


def add_section_translations():
    """Add section translations to database metadata."""
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get or create metadata
    if '_metadata' not in data:
        data['_metadata'] = {}
    
    metadata = data['_metadata']
    
    # Add section translations to metadata
    metadata['section_translations'] = SECTION_TRANSLATIONS
    
    if 'improvements_v2' not in metadata:
        metadata['improvements_v2'] = []
    metadata['improvements_v2'].append(f"Added translations for {len(SECTION_TRANSLATIONS)} section names")
    
    print(f"\nAdded {len(SECTION_TRANSLATIONS)} section translations to metadata")
    for section, trans in list(SECTION_TRANSLATIONS.items())[:10]:
        print(f"  {section}: {trans['en']} / {trans['ru']}")
    print(f"  ... and {len(SECTION_TRANSLATIONS) - 10} more")
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")

if __name__ == '__main__':
    add_section_translations()

