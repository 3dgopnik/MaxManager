"""
Fix OpenImageIO parameters - translations and naming.
"""

import json
from pathlib import Path

OPENIMAGIO_FIXES = {
    "OpenImageIO.max_open_files": {
        "en": "Maximum Open Files",
        "ru": "Максимум открытых файлов",
        "help_en": "Maximum number of image files OpenImageIO can keep open simultaneously. Higher values improve performance but use more file handles.",
        "help_ru": "Максимальное количество файлов изображений которые OpenImageIO может держать открытыми одновременно. Большие значения улучшают производительность но используют больше файловых дескрипторов."
    },
    "OpenImageIO.max_memory_MB": {
        "en": "Maximum Memory (MB)",
        "ru": "Максимум памяти (МБ)",
        "help_en": "Maximum memory in megabytes that OpenImageIO can use for image caching. 0 = unlimited. Recommended: 16384 (16GB) for high-res textures.",
        "help_ru": "Максимум памяти в мегабайтах которую OpenImageIO может использовать для кэширования изображений. 0 = без ограничений. Рекомендуется: 16384 (16ГБ) для текстур высокого разрешения."
    },
    "OpenImageIO.autotile": {
        "en": "Auto Tile",
        "ru": "Автоматическая нарезка плиток",
        "help_en": "Automatically tile large images for better memory management. 0 = off, 1 = on.",
        "help_ru": "Автоматически нарезать большие изображения на плитки для лучшего управления памятью. 0 = выкл, 1 = вкл."
    },
    "OpenImageIO.automip": {
        "en": "Auto MIP-Mapping",
        "ru": "Автоматические MIP-уровни",
        "help_en": "Automatically generate MIP maps for textures. 1 = on (recommended). Improves rendering performance.",
        "help_ru": "Автоматически генерировать MIP-карты для текстур. 1 = вкл (рекомендуется). Улучшает производительность рендера."
    },
    "OpenImageIO.autoscanline": {
        "en": "Auto Scanline",
        "ru": "Автоматическое построчное чтение",
        "help_en": "Use scanline-oriented I/O for better streaming. 0 = off (default), 1 = on.",
        "help_ru": "Использовать построчное чтение для лучшего стриминга. 0 = выкл (по умолчанию), 1 = вкл."
    },
    "OpenImageIO.autoFileUpdate": {
        "en": "Auto File Update",
        "ru": "Автообновление файлов",
        "help_en": "Automatically reload changed image files. 1 = on (recommended). Useful when textures are updated externally.",
        "help_ru": "Автоматически перезагружать изменённые файлы изображений. 1 = вкл (рекомендуется). Полезно когда текстуры обновляются извне."
    },
}


def fix_openimagio():
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    updated = 0
    
    for param_key, fixes in OPENIMAGIO_FIXES.items():
        if param_key in data:
            # Update display names
            data[param_key]['en']['display_name'] = fixes['en']
            data[param_key]['ru']['display_name'] = fixes['ru']
            
            # Update help text if available
            if 'help_en' in fixes:
                data[param_key]['en']['help_text'] = fixes['help_en']
            if 'help_ru' in fixes:
                data[param_key]['ru']['help_text'] = fixes['help_ru']
            
            updated += 1
            print(f"  [UPDATED] {param_key}")
            print(f"    EN: {fixes['en']}")
            print(f"    RU: {fixes['ru']}")
        else:
            print(f"  [NOT FOUND] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Fixed OpenImageIO parameter names and translations")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Updated {updated} OpenImageIO parameters")

if __name__ == '__main__':
    fix_openimagio()

