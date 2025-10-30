"""
Add ALL remaining V-Ray parameters visible in UI.
"""

import json
from pathlib import Path

# Complete V-Ray parameters from screenshots
ALL_VRAY_PARAMS = {
    # Scene Convert Options (extended)
    "Scene Convert Options.modhelperconvert": {
        "en": {"display_name": "Convert Modifier Helpers", "description": "Convert modifier helpers during scene conversion.", "help_text": "Include helper objects from modifiers in conversion."},
        "ru": {"display_name": "Конвертировать хелперы модификаторов", "description": "Конвертировать хелперы модификаторов при конвертации сцены.", "help_text": "Включать хелпер-объекты модификаторов в конвертацию."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["geometry"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertrendergienvironment": {
        "en": {"display_name": "Convert Render GI Environment", "description": "Convert render GI environment settings.", "help_text": "Include Global Illumination environment in conversion."},
        "ru": {"display_name": "Конвертировать GI окружение", "description": "Конвертировать настройки GI окружения.", "help_text": "Включать настройки Global Illumination окружения в конвертацию."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.reconvert": {
        "en": {"display_name": "Reconvert Materials", "description": "Allow reconversion of already converted materials.", "help_text": "Reconvert materials that were previously converted."},
        "ru": {"display_name": "Переконвертировать материалы", "description": "Разрешить переконвертацию уже сконвертированных материалов.", "help_text": "Переконвертировать материалы которые были ранее сконвертированы."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (avoid double conversion)", "ru": "false (избегать двойной конвертации)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.lightconvert": {
        "en": {"display_name": "Convert Lights", "description": "Convert lights to V-Ray lights.", "help_text": "Convert standard lights to V-Ray light sources."},
        "ru": {"display_name": "Конвертировать источники света", "description": "Конвертировать источники света в V-Ray lights.", "help_text": "Конвертировать стандартные источники в V-Ray light источники."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (recommended)", "ru": "true (рекомендуется)"}, "impact": ["rendering", "lighting"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.cameraconvert": {
        "en": {"display_name": "Convert Cameras", "description": "Convert cameras to V-Ray Physical Camera.", "help_text": "Convert standard cameras to V-Ray Physical Camera."},
        "ru": {"display_name": "Конвертировать камеры", "description": "Конвертировать камеры в V-Ray Physical Camera.", "help_text": "Конвертировать стандартные камеры в V-Ray Physical Camera."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["cameras"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.selnodeonly": {
        "en": {"display_name": "Selected Nodes Only", "description": "Convert only selected nodes instead of entire scene.", "help_text": "Apply conversion only to selected objects/materials."},
        "ru": {"display_name": "Только выбранные ноды", "description": "Конвертировать только выбранные ноды вместо всей сцены.", "help_text": "Применять конвертацию только к выбранным объектам/материалам."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (convert all)", "ru": "false (конвертировать всё)"}, "impact": ["workflow"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.conversiontarget": {
        "en": {"display_name": "Conversion Target", "description": "Target renderer for conversion (0=Corona, 1=Arnold, 2=V-Ray).", "help_text": "0 = Corona Renderer, 1 = Arnold, 2 = V-Ray (default)."},
        "ru": {"display_name": "Целевой рендерер", "description": "Целевой рендерер для конвертации (0=Corona, 1=Arnold, 2=V-Ray).", "help_text": "0 = Corona Renderer, 1 = Arnold, 2 = V-Ray (по умолчанию)."},
        "type": "integer", "default": "2", "recommended": {"en": "2 (V-Ray)", "ru": "2 (V-Ray)"}, "impact": ["rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.updatemtlsfromfile": {
        "en": {"display_name": "Update Materials from File", "description": "Update materials from external file during conversion.", "help_text": "Load material definitions from external file."},
        "ru": {"display_name": "Обновлять материалы из файла", "description": "Обновлять материалы из внешнего файла при конвертации.", "help_text": "Загружать определения материалов из внешнего файла."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.autorefreshscenemtlslist": {
        "en": {"display_name": "Auto-Refresh Scene Materials List", "description": "Automatically refresh materials list during conversion.", "help_text": "Update UI materials list automatically."},
        "ru": {"display_name": "Автообновление списка материалов", "description": "Автоматически обновлять список материалов при конвертации.", "help_text": "Автоматически обновлять список материалов в интерфейсе."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["ui"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.convertphysicalmtl": {
        "en": {"display_name": "Convert Physical Materials", "description": "Convert Physical materials during scene conversion.", "help_text": "Include Physical (PBR) materials in conversion."},
        "ru": {"display_name": "Конвертировать Physical материалы", "description": "Конвертировать Physical материалы при конвертации сцены.", "help_text": "Включать Physical (PBR) материалы в конвертацию."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (important!)", "ru": "true (важно!)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.convertstdbitmaptonativebitmap": {
        "en": {"display_name": "Convert Standard Bitmap to Native Bitmap", "description": "Convert standard bitmap to V-Ray native bitmap.", "help_text": "Use V-Ray native bitmap node instead of standard 3ds Max bitmap."},
        "ru": {"display_name": "Конвертировать Bitmap в нативный", "description": "Конвертировать стандартный bitmap в нативный V-Ray bitmap.", "help_text": "Использовать нативную ноду V-Ray bitmap вместо стандартного 3ds Max bitmap."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (unless needed)", "ru": "false (если не требуется)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertopacitytorefract": {
        "en": {"display_name": "Convert Opacity to Refraction", "description": "Convert opacity maps to refraction.", "help_text": "Use refraction for opacity instead of simple opacity channel."},
        "ru": {"display_name": "Конвертировать прозрачность в преломление", "description": "Конвертировать карты прозрачности в преломление.", "help_text": "Использовать преломление для прозрачности вместо простого opacity канала."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (keep opacity)", "ru": "false (оставить opacity)"}, "impact": ["materials", "rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertvrayhdritocoronabitmap": {
        "en": {"display_name": "Convert VRayHDRI to Corona Bitmap", "description": "Convert VRayHDRI to Corona Bitmap.", "help_text": "Convert V-Ray HDRI maps to Corona Bitmap format."},
        "ru": {"display_name": "Конвертировать VRayHDRI в Corona Bitmap", "description": "Конвертировать VRayHDRI в Corona Bitmap.", "help_text": "Конвертировать V-Ray HDRI карты в формат Corona Bitmap."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (only for Corona)", "ru": "false (только для Corona)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertvray2sidedtodoublesided": {
        "en": {"display_name": "Convert VRay2Sided to DoubleSided", "description": "Convert VRay2Sided material to standard DoubleSided.", "help_text": "Use standard DoubleSided material instead of VRay2Sided."},
        "ru": {"display_name": "Конвертировать VRay2Sided в DoubleSided", "description": "Конвертировать VRay2Sided материал в стандартный DoubleSided.", "help_text": "Использовать стандартный DoubleSided материал вместо VRay2Sided."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (keep VRay2Sided)", "ru": "false (оставить VRay2Sided)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertnativenormalmaptovraynormal": {
        "en": {"display_name": "Convert Native Normal Map to VRayNormal", "description": "Convert standard Normal map to VRayNormalMap.", "help_text": "Use VRayNormalMap instead of standard Normal Bump map."},
        "ru": {"display_name": "Конвертировать Normal в VRayNormal", "description": "Конвертировать стандартную Normal карту в VRayNormalMap.", "help_text": "Использовать VRayNormalMap вместо стандартной Normal Bump карты."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (standard works fine)", "ru": "false (стандартная работает нормально)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertcoronacolorcorrect": {
        "en": {"display_name": "Convert Corona ColorCorrect", "description": "Convert Corona ColorCorrect nodes.", "help_text": "Convert Corona ColorCorrect to V-Ray equivalent."},
        "ru": {"display_name": "Конвертировать Corona ColorCorrect", "description": "Конвертировать ноды Corona ColorCorrect.", "help_text": "Конвертировать Corona ColorCorrect в V-Ray эквивалент."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (if using Corona)", "ru": "true (если используете Corona)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.convertundefinedmtl": {
        "en": {"display_name": "Convert Undefined Materials", "description": "Convert undefined/missing materials to default.", "help_text": "Replace undefined materials with default material."},
        "ru": {"display_name": "Конвертировать неопределённые материалы", "description": "Конвертировать неопределённые/отсутствующие материалы в дефолтные.", "help_text": "Заменять неопределённые материалы материалом по умолчанию."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (prevents errors)", "ru": "true (предотвращает ошибки)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.undefinedmtldiffusecolor": {
        "en": {"display_name": "Undefined Material Diffuse Color", "description": "Default diffuse color for undefined materials.", "help_text": "RGB color for undefined materials (format: color R G B)."},
        "ru": {"display_name": "Цвет неопределённых материалов", "description": "Цвет диффуза по умолчанию для неопределённых материалов.", "help_text": "RGB цвет для неопределённых материалов (формат: color R G B)."},
        "type": "color", "default": "(color 255 0 0)", "recommended": {"en": "(color 255 0 0) - red highlights missing mtls", "ru": "(color 255 0 0) - красный подсвечивает отсутствующие"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.bakedtexres": {
        "en": {"display_name": "Baked Texture Resolution", "description": "Resolution for baked textures (power of 2: 0-12 = 1px to 4096px).", "help_text": "0=1px, 1=2px, 2=4px, 3=8px, 4=16px, 5=32px, 6=64px, 7=128px, 8=256px, 9=512px, 10=1024px, 11=2048px, 12=4096px."},
        "ru": {"display_name": "Разрешение запечённых текстур", "description": "Разрешение для запечённых текстур (степень 2: 0-12 = 1px до 4096px).", "help_text": "0=1px, 1=2px, 2=4px, 3=8px, 4=16px, 5=32px, 6=64px, 7=128px, 8=256px, 9=512px, 10=1024px, 11=2048px, 12=4096px."},
        "type": "integer", "default": "6", "recommended": {"en": "6 (64px) to 10 (1024px)", "ru": "6 (64px) до 10 (1024px)"}, "impact": ["quality", "memory"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.bakedtexext": {
        "en": {"display_name": "Baked Texture Extension", "description": "File extension for baked textures.", "help_text": "Format for baked texture files (png, jpg, tga, etc)."},
        "ru": {"display_name": "Расширение запечённых текстур", "description": "Расширение файла для запечённых текстур.", "help_text": "Формат файлов запечённых текстур (png, jpg, tga и т.д)."},
        "type": "string", "default": "png", "recommended": {"en": "png (lossless) or jpg (smaller)", "ru": "png (без потерь) или jpg (меньше)"}, "impact": ["io", "quality"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    
    # V-Ray Rendering Settings (from second screenshot)
    "Distributed rendering server cap": {
        "en": {"display_name": "Distributed Rendering Server Cap", "description": "Maximum number of distributed rendering servers.", "help_text": "Limit number of render servers to use in distributed rendering."},
        "ru": {"display_name": "Лимит серверов распределённого рендера", "description": "Максимальное количество серверов распределённого рендера.", "help_text": "Ограничить количество рендер-серверов для распределённого рендера."},
        "type": "integer", "default": "0", "recommended": {"en": "0 = unlimited (use all available)", "ru": "0 = без ограничений (использовать все)"}, "impact": ["performance", "rendering"], "status": "documented", "source": "vendor", "section": "Rendering", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Dynamic memory limit (MB)": {
        "en": {"display_name": "Dynamic Memory Limit (MB)", "description": "Dynamic memory allocation limit in megabytes.", "help_text": "Maximum RAM that V-Ray can use for dynamic allocation. 0 = automatic."},
        "ru": {"display_name": "Лимит динамической памяти (МБ)", "description": "Лимит динамического выделения памяти в мегабайтах.", "help_text": "Максимум RAM который V-Ray может использовать для динамического выделения. 0 = автоматически."},
        "type": "integer", "default": "0", "recommended": {"en": "0 (auto) or 80% of total RAM", "ru": "0 (авто) или 80% от всей RAM"}, "impact": ["performance", "memory"], "status": "documented", "source": "vendor", "section": "Performance", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Low thread priority": {
        "en": {"display_name": "Low Thread Priority", "description": "Run V-Ray rendering threads at low priority.", "help_text": "Reduce CPU priority for render threads to keep system responsive."},
        "ru": {"display_name": "Низкий приоритет потоков", "description": "Запускать потоки рендера V-Ray с низким приоритетом.", "help_text": "Снизить приоритет CPU для потоков рендера чтобы система оставалась отзывчивой."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (max speed), true (if working while rendering)", "ru": "false (макс. скорость), true (если работаете во время рендера)"}, "impact": ["performance"], "status": "documented", "source": "vendor", "section": "Performance", "ini_file": "vray.ini", "tier": "standard"
    },
    "VFB history limit": {
        "en": {"display_name": "VFB History Limit", "description": "Number of render history entries to keep in V-Ray Frame Buffer.", "help_text": "Maximum number of previous renders stored in VFB history."},
        "ru": {"display_name": "Лимит истории VFB", "description": "Количество записей истории рендера в V-Ray Frame Buffer.", "help_text": "Максимальное количество предыдущих рендеров сохраняемых в истории VFB."},
        "type": "integer", "default": "10", "recommended": {"en": "10-20 (balance memory vs history)", "ru": "10-20 (баланс памяти и истории)"}, "impact": ["memory", "ui"], "status": "documented", "source": "vendor", "section": "VFB", "ini_file": "vray.ini", "tier": "standard"
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
    updated = 0
    
    for param_key, param_data in ALL_VRAY_PARAMS.items():
        if param_key not in data:
            data[param_key] = param_data
            added += 1
            en_name = param_data['en']['display_name']
            ru_name = param_data['ru']['display_name']
            print(f"  [ADDED] {param_key}")
            print(f"    EN: {en_name}")
            print(f"    RU: {ru_name}")
        else:
            # Update if exists
            data[param_key]['en']['display_name'] = param_data['en']['display_name']
            data[param_key]['ru']['display_name'] = param_data['ru']['display_name']
            updated += 1
            print(f"  [UPDATED] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Added {added} complete V-Ray parameters, updated {updated}")
        metadata['total_parameters'] = len(data)
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Added {added}, Updated {updated}")

if __name__ == '__main__':
    add_params()

