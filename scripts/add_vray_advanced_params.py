"""
Add V-Ray advanced tool parameters with proper descriptions.
"""

import json
from pathlib import Path

NEW_VRAY_PARAMS = {
    "Advanced Tools Options.vrayset": {
        "en": {
            "display_name": "V-Ray Tools Settings Array",
            "description": "Complex MaxScript array storing V-Ray advanced tool settings.",
            "help_text": "MaxScript array format: #(enabled, value, locked). Each element represents a tool setting. DO NOT edit manually unless you know MaxScript syntax. Changes may break V-Ray tools."
        },
        "ru": {
            "display_name": "Массив настроек V-Ray Tools",
            "description": "Сложный MaxScript массив с настройками продвинутых инструментов V-Ray.",
            "help_text": "Формат MaxScript массива: #(включено, значение, заблокировано). Каждый элемент - настройка инструмента. НЕ редактируйте вручную если не знаете синтаксис MaxScript. Изменения могут сломать инструменты V-Ray."
        },
        "type": "array",
        "default": "",
        "recommended": {
            "en": "[!] DO NOT EDIT manually. This is a complex data structure managed by V-Ray. Edit through V-Ray UI instead.",
            "ru": "[!] НЕ РЕДАКТИРУЙТЕ вручную. Это сложная структура данных управляемая V-Ray. Редактируйте через интерфейс V-Ray."
        },
        "impact": ["vray_tools", "ui"],
        "status": "vendor_internal",
        "source": "vendor",
        "section": "Advanced Tools Options",
        "ini_file": "vray.ini",
        "tier": "internal",
        "warnings": [
            "Manual editing may corrupt V-Ray settings",
            "Use V-Ray UI for changing tool settings",
            "Backup INI before any manual changes"
        ],
        "introduced_in": None,
        "last_verified": "2025-10-30"
    },
    "Advanced Tools Options.batchadvtools": {
        "en": {
            "display_name": "Batch Advanced Tools",
            "description": "Enable batch processing for V-Ray advanced tools.",
            "help_text": "Allow V-Ray advanced tools to process multiple objects/scenes in batch mode."
        },
        "ru": {
            "display_name": "Пакетная обработка",
            "description": "Включить пакетную обработку для продвинутых инструментов V-Ray.",
            "help_text": "Разрешить продвинутым инструментам V-Ray обрабатывать несколько объектов/сцен пакетно."
        },
        "type": "boolean",
        "default": "false",
        "recommended": {
            "en": "false (off) - enable only when processing multiple scenes",
            "ru": "false (выкл) - включайте только при обработке нескольких сцен"
        },
        "impact": ["performance", "workflow"],
        "status": "documented",
        "source": "vendor",
        "section": "Advanced Tools Options",
        "ini_file": "vray.ini",
        "tier": "advanced"
    },
    "Advanced Tools Options.switchcolorspace": {
        "en": {
            "display_name": "Switch Color Space",
            "description": "Automatically switch color space when converting materials.",
            "help_text": "Enable to auto-switch color space during V-Ray material conversion."
        },
        "ru": {
            "display_name": "Переключать цветовое пространство",
            "description": "Автоматически переключать цветовое пространство при конвертации материалов.",
            "help_text": "Включите для автопереключения цветового пространства при конвертации материалов V-Ray."
        },
        "type": "boolean",
        "default": "false",
        "recommended": {
            "en": "false (off) - enable only if materials have wrong colors after conversion",
            "ru": "false (выкл) - включайте только если материалы имеют неправильные цвета после конвертации"
        },
        "impact": ["rendering", "materials"],
        "status": "documented",
        "source": "vendor",
        "section": "Advanced Tools Options",
        "ini_file": "vray.ini",
        "tier": "advanced"
    },
}


def add_params():
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    added = 0
    for param_key, param_data in NEW_VRAY_PARAMS.items():
        if param_key not in data:
            data[param_key] = param_data
            added += 1
            print(f"  [ADDED] {param_key}")
            print(f"    EN: {param_data['en']['display_name']}")
            print(f"    RU: {param_data['ru']['display_name']}")
            print(f"    Rec: {param_data['recommended']['en'][:80]}...")
        else:
            print(f"  [EXISTS] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Added {added} V-Ray Advanced Tools parameters with warnings")
        metadata['total_parameters'] = len(data)
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Added {added} V-Ray parameters")

if __name__ == '__main__':
    add_params()

