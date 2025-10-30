"""
Add ALL missing V-Ray parameters as new entries in database.
"""

import json
from pathlib import Path

# All V-Ray parameters visible in UI but not in database
NEW_VRAY_PARAMS = {
    # Scene Convert Options
    "Scene Convert Options.bakedtexpath": {
        "en": {"display_name": "Baked Texture Path", "description": "Path for baked textures.", "help_text": "Directory to save baked textures during conversion."},
        "ru": {"display_name": "Путь запечённых текстур", "description": "Путь для запечённых текстур.", "help_text": "Папка для сохранения запечённых текстур при конвертации."},
        "type": "path", "default": "", "recommended": {"en": "", "ru": ""}, "impact": ["io"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.bakedtexgammaauto": {
        "en": {"display_name": "Baked Texture Gamma Auto", "description": "Auto gamma for baked textures.", "help_text": "Automatically set gamma for baked textures."},
        "ru": {"display_name": "Авто-гамма запечённых текстур", "description": "Автогамма для запечённых текстур.", "help_text": "Автоматически устанавливать гамму для запечённых текстур."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.bakedtexgamma": {
        "en": {"display_name": "Baked Texture Gamma", "description": "Gamma value for baked textures.", "help_text": "Gamma correction value for baked textures."},
        "ru": {"display_name": "Гамма запечённых текстур", "description": "Значение гаммы для запечённых текстур.", "help_text": "Значение гамма-коррекции для запечённых текстур."},
        "type": "float", "default": "1.0", "recommended": {"en": "1.0 (linear), 2.2 (sRGB)", "ru": "1.0 (линейная), 2.2 (sRGB)"}, "impact": ["rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.bakedtexorigsize": {
        "en": {"display_name": "Baked Texture Original Size", "description": "Keep original texture size when baking.", "help_text": "Preserve original texture dimensions during baking."},
        "ru": {"display_name": "Оригинальный размер текстур", "description": "Сохранять оригинальный размер при запекании.", "help_text": "Сохранять оригинальные размеры текстур при запекании."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["memory", "quality"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.showtexmapinvp": {
        "en": {"display_name": "Show Texture Maps in Viewport", "description": "Display texture maps in viewport after conversion.", "help_text": "Show converted texture maps in viewport preview."},
        "ru": {"display_name": "Показывать текстуры во вьюпорте", "description": "Отображать текстуры во вьюпорте после конвертации.", "help_text": "Показывать сконвертированные текстуры в превью вьюпорта."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["viewport"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.savescenentisstate": {
        "en": {"display_name": "Save Scene NTIS State", "description": "Save scene NTIS state during conversion.", "help_text": "Preserve NTIS (Night Time Illumination System) state."},
        "ru": {"display_name": "Сохранять состояние NTIS", "description": "Сохранять состояние NTIS при конвертации.", "help_text": "Сохранять состояние NTIS (Night Time Illumination System)."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["scene"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.switchrenderengine": {
        "en": {"display_name": "Switch Render Engine", "description": "Automatically switch to V-Ray renderer after conversion.", "help_text": "Set V-Ray as active renderer after material conversion."},
        "ru": {"display_name": "Переключать рендер-движок", "description": "Автоматически переключаться на V-Ray после конвертации.", "help_text": "Установить V-Ray активным рендером после конвертации материалов."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["rendering"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.batchsceneconvert": {
        "en": {"display_name": "Batch Scene Convert", "description": "Enable batch conversion of multiple scenes.", "help_text": "Process multiple scene files in batch mode."},
        "ru": {"display_name": "Пакетная конвертация сцен", "description": "Включить пакетную конвертацию нескольких сцен.", "help_text": "Обрабатывать несколько файлов сцен пакетно."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (use carefully)", "ru": "false (использовать осторожно)"}, "impact": ["workflow"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Scene Convert Options.convertdirection": {
        "en": {"display_name": "Convert Direction", "description": "Direction of material conversion (0=to VRay, 1=from VRay, 2=bi-directional).", "help_text": "0 = Convert to V-Ray materials, 1 = Convert from V-Ray materials, 2 = Both directions."},
        "ru": {"display_name": "Направление конвертации", "description": "Направление конвертации материалов (0=в VRay, 1=из VRay, 2=оба).", "help_text": "0 = Конвертировать в материалы V-Ray, 1 = Из материалов V-Ray, 2 = Оба направления."},
        "type": "integer", "default": "2", "recommended": {"en": "2 (bi-directional)", "ru": "2 (в обе стороны)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Scene Convert Options.scenemtlsmapsconvert": {
        "en": {"display_name": "Convert Scene Materials and Maps", "description": "Include materials and maps in scene conversion.", "help_text": "Convert materials and texture maps during scene conversion."},
        "ru": {"display_name": "Конвертировать материалы и текстуры", "description": "Включать материалы и текстуры в конвертацию.", "help_text": "Конвертировать материалы и текстурные карты при конвертации сцены."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Scene Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    
    # Advanced Convert Options
    "Advanced Convert Options.batchadvconvert": {
        "en": {"display_name": "Batch Advanced Convert", "description": "Batch mode for advanced conversion options.", "help_text": "Enable advanced conversion in batch processing mode."},
        "ru": {"display_name": "Пакетная продвинутая конвертация", "description": "Пакетный режим для продвинутых опций конвертации.", "help_text": "Включить продвинутую конвертацию в пакетном режиме."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["workflow"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.proxyconvert": {
        "en": {"display_name": "Convert Proxies", "description": "Include proxy objects in conversion.", "help_text": "Convert V-Ray proxy objects during scene conversion."},
        "ru": {"display_name": "Конвертировать прокси", "description": "Включать прокси объекты в конвертацию.", "help_text": "Конвертировать V-Ray прокси объекты при конвертации сцены."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["geometry"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.proxyconvertdirection": {
        "en": {"display_name": "Proxy Convert Direction", "description": "Direction for proxy conversion (0=to VRayProxy, 1=from VRayProxy).", "help_text": "0 = Convert to V-Ray Proxy, 1 = Convert from V-Ray Proxy."},
        "ru": {"display_name": "Направление конвертации прокси", "description": "Направление конвертации прокси (0=в VRayProxy, 1=из VRayProxy).", "help_text": "0 = Конвертировать в V-Ray Proxy, 1 = Из V-Ray Proxy."},
        "type": "integer", "default": "0", "recommended": {"en": "0 (to V-Ray)", "ru": "0 (в V-Ray)"}, "impact": ["geometry"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.proxypreviewtype": {
        "en": {"display_name": "Proxy Preview Type", "description": "Preview type for converted proxies (0=box, 1=point cloud, 2=full mesh).", "help_text": "0 = Bounding box, 1 = Point cloud preview, 2 = Full mesh preview."},
        "ru": {"display_name": "Тип превью прокси", "description": "Тип превью для сконвертированных прокси (0=бокс, 1=облако точек, 2=полная сетка).", "help_text": "0 = Баундинг бокс, 1 = Превью облаком точек, 2 = Полное превью сетки."},
        "type": "integer", "default": "1", "recommended": {"en": "1 (point cloud - balanced)", "ru": "1 (облако точек - сбалансировано)"}, "impact": ["viewport", "performance"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.proxyoverwrite": {
        "en": {"display_name": "Overwrite Existing Proxies", "description": "Overwrite existing proxy files during conversion.", "help_text": "Replace existing .vrmesh files with new ones."},
        "ru": {"display_name": "Перезаписывать прокси", "description": "Перезаписывать существующие файлы прокси при конвертации.", "help_text": "Заменять существующие .vrmesh файлы новыми."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (safer)", "ru": "false (безопаснее)"}, "impact": ["io"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.proxycollect": {
        "en": {"display_name": "Collect Proxy Files", "description": "Collect proxy files to project folder.", "help_text": "Copy all .vrmesh files to project directory during conversion."},
        "ru": {"display_name": "Собирать файлы прокси", "description": "Собирать файлы прокси в папку проекта.", "help_text": "Копировать все .vrmesh файлы в папку проекта при конвертации."},
        "type": "boolean", "default": "false", "recommended": {"en": "true (for portability)", "ru": "true (для переносимости)"}, "impact": ["io", "workflow"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.bitmapconvert": {
        "en": {"display_name": "Convert Bitmaps", "description": "Convert bitmap textures during scene conversion.", "help_text": "Include bitmap texture conversion."},
        "ru": {"display_name": "Конвертировать текстуры", "description": "Конвертировать bitmap текстуры при конвертации сцены.", "help_text": "Включить конвертацию bitmap текстур."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Advanced Convert Options.bitmapconvertdirection": {
        "en": {"display_name": "Bitmap Convert Direction", "description": "Direction for bitmap conversion.", "help_text": "0 = to V-Ray bitmaps, 1 = from V-Ray bitmaps."},
        "ru": {"display_name": "Направление конвертации текстур", "description": "Направление конвертации bitmap.", "help_text": "0 = в V-Ray bitmap, 1 = из V-Ray bitmap."},
        "type": "integer", "default": "0", "recommended": {"en": "0", "ru": "0"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Convert Options.cameraconvert": {
        "en": {"display_name": "Convert Cameras", "description": "Convert cameras to V-Ray Physical Camera.", "help_text": "Convert standard cameras to V-Ray Physical Camera during conversion."},
        "ru": {"display_name": "Конвертировать камеры", "description": "Конвертировать камеры в V-Ray Physical Camera.", "help_text": "Конвертировать стандартные камеры в V-Ray Physical Camera при конвертации."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (recommended)", "ru": "true (рекомендуется)"}, "impact": ["rendering", "cameras"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Advanced Convert Options.cameraconvertdirection": {
        "en": {"display_name": "Camera Convert Direction", "description": "Direction for camera conversion.", "help_text": "0 = to V-Ray Physical Camera, 1 = from V-Ray Physical Camera."},
        "ru": {"display_name": "Направление конвертации камер", "description": "Направление конвертации камер.", "help_text": "0 = в V-Ray Physical Camera, 1 = из V-Ray Physical Camera."},
        "type": "integer", "default": "0", "recommended": {"en": "0", "ru": "0"}, "impact": ["cameras"], "status": "documented", "source": "vendor", "section": "Advanced Convert Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    
    # Advanced Tools Options
    "Advanced Tools Options.switchcolorspaceselnode": {
        "en": {"display_name": "Switch Color Space for Selected Node", "description": "Switch color space for selected material node only.", "help_text": "Apply color space conversion to selected node instead of entire scene."},
        "ru": {"display_name": "Переключать цветовое пространство для выбранной ноды", "description": "Переключать цветовое пространство только для выбранной ноды материала.", "help_text": "Применять конвертацию цветового пространства к выбранной ноде вместо всей сцены."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Tools Options.rgbprim": {
        "en": {"display_name": "RGB Primaries", "description": "RGB color primaries setting.", "help_text": "RGB color space primaries for color management."},
        "ru": {"display_name": "RGB первичные", "description": "Настройка первичных RGB цветов.", "help_text": "Первичные цвета RGB для управления цветом."},
        "type": "string", "default": "", "recommended": {"en": "", "ru": ""}, "impact": ["rendering"], "status": "vendor_internal", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "internal"
    },
    "Advanced Tools Options.useoslmapnode": {
        "en": {"display_name": "Use OSL Map Node", "description": "Use OSL (Open Shading Language) map nodes.", "help_text": "Enable OSL map node support in V-Ray material converter."},
        "ru": {"display_name": "Использовать OSL Map ноду", "description": "Использовать ноды OSL (Open Shading Language).", "help_text": "Включить поддержку OSL map нод в конвертере материалов V-Ray."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (unless using OSL)", "ru": "false (если не используете OSL)"}, "impact": ["materials", "rendering"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Tools Options.useociofile": {
        "en": {"display_name": "Use OCIO File", "description": "Use OpenColorIO configuration file.", "help_text": "Enable OCIO (OpenColorIO) file for color management."},
        "ru": {"display_name": "Использовать файл OCIO", "description": "Использовать конфигурационный файл OpenColorIO.", "help_text": "Включить файл OCIO (OpenColorIO) для управления цветом."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (unless using OCIO)", "ru": "false (если не используете OCIO)"}, "impact": ["rendering", "color_management"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Advanced Tools Options.correctcolormapping": {
        "en": {"display_name": "Correct Color Mapping", "description": "Automatically correct color mapping during conversion.", "help_text": "Fix color mapping issues when converting materials."},
        "ru": {"display_name": "Корректировать маппинг цветов", "description": "Автоматически корректировать маппинг цветов при конвертации.", "help_text": "Исправлять проблемы маппинга цветов при конвертации материалов."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (recommended)", "ru": "true (рекомендуется)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Advanced Tools Options.renamedupnames": {
        "en": {"display_name": "Rename Duplicate Names", "description": "Automatically rename duplicate material/map names.", "help_text": "Add suffix to duplicate names during conversion to avoid conflicts."},
        "ru": {"display_name": "Переименовывать дубликаты", "description": "Автоматически переименовывать дубликаты имён материалов/текстур.", "help_text": "Добавлять суффикс к дубликатам имён при конвертации чтобы избежать конфликтов."},
        "type": "boolean", "default": "true", "recommended": {"en": "true (prevents errors)", "ru": "true (предотвращает ошибки)"}, "impact": ["materials"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "standard"
    },
    "Advanced Tools Options.standardsel": {
        "en": {"display_name": "Standard Selection", "description": "Use standard selection mode.", "help_text": "Standard selection behavior for V-Ray tools."},
        "ru": {"display_name": "Стандартное выделение", "description": "Использовать стандартный режим выделения.", "help_text": "Стандартное поведение выделения для инструментов V-Ray."},
        "type": "boolean", "default": "true", "recommended": {"en": "true", "ru": "true"}, "impact": ["ui"], "status": "documented", "source": "vendor", "section": "Advanced Tools Options", "ini_file": "vray.ini", "tier": "standard"
    },
    
    # Batch Process Settings
    "Batch Process Settings.silent": {
        "en": {"display_name": "Silent Mode", "description": "Run batch processing silently without dialogs.", "help_text": "Suppress confirmation dialogs during batch processing."},
        "ru": {"display_name": "Тихий режим", "description": "Запускать пакетную обработку без диалогов.", "help_text": "Подавлять диалоги подтверждения при пакетной обработке."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (safer)", "ru": "false (безопаснее)"}, "impact": ["workflow"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Batch Process Settings.subdirinclude": {
        "en": {"display_name": "Include Subdirectories", "description": "Process files in subdirectories during batch.", "help_text": "Recursively process all subdirectories."},
        "ru": {"display_name": "Включать подпапки", "description": "Обрабатывать файлы в подпапках при пакетной обработке.", "help_text": "Рекурсивно обрабатывать все подпапки."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (be careful)", "ru": "false (будьте осторожны)"}, "impact": ["workflow"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Batch Process Settings.savetoorigfolder": {
        "en": {"display_name": "Save to Original Folder", "description": "Save processed files to original location.", "help_text": "Save batch-processed files in same folder as source."},
        "ru": {"display_name": "Сохранять в исходную папку", "description": "Сохранять обработанные файлы в исходное расположение.", "help_text": "Сохранять пакетно обработанные файлы в ту же папку что и исходники."},
        "type": "boolean", "default": "true", "recommended": {"en": "false (safer to use output folder)", "ru": "false (безопаснее использовать выходную папку)"}, "impact": ["io"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Batch Process Settings.overwrite": {
        "en": {"display_name": "Overwrite Existing Files", "description": "Overwrite existing files during batch processing.", "help_text": "Replace existing files without confirmation."},
        "ru": {"display_name": "Перезаписывать файлы", "description": "Перезаписывать существующие файлы при пакетной обработке.", "help_text": "Заменять существующие файлы без подтверждения."},
        "type": "boolean", "default": "false", "recommended": {"en": "false (DANGEROUS if true!)", "ru": "false (ОПАСНО если true!)"}, "impact": ["io"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced",
        "warnings": ["Can delete original files if enabled"]
    },
    "Batch Process Settings.savetomaxversion": {
        "en": {"display_name": "Save to 3ds Max Version", "description": "Target 3ds Max version for saving (e.g., 2025).", "help_text": "Specify 3ds Max version number for saving converted scenes."},
        "ru": {"display_name": "Сохранять для версии Max", "description": "Целевая версия 3ds Max для сохранения (например, 2025).", "help_text": "Укажите номер версии 3ds Max для сохранения сконвертированных сцен."},
        "type": "integer", "default": "2025", "recommended": {"en": "2025 (current version)", "ru": "2025 (текущая версия)"}, "impact": ["compatibility"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced"
    },
    "Batch Process Settings.saveinoriginalversion": {
        "en": {"display_name": "Save in Original Version", "description": "Save in original 3ds Max version instead of converting.", "help_text": "Keep original Max version format instead of upgrading."},
        "ru": {"display_name": "Сохранять в исходной версии", "description": "Сохранять в исходной версии 3ds Max без конвертации.", "help_text": "Сохранять в формате оригинальной версии Max вместо обновления."},
        "type": "boolean", "default": "false", "recommended": {"en": "false", "ru": "false"}, "impact": ["compatibility"], "status": "documented", "source": "vendor", "section": "Batch Process Settings", "ini_file": "vray.ini", "tier": "advanced"
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
        else:
            print(f"  [EXISTS] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Added {added} V-Ray conversion/batch parameters")
        metadata['total_parameters'] = len(data)
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Added {added} parameters")

if __name__ == '__main__':
    add_params()

