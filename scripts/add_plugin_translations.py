"""
Add human-readable translations for plugin parameters.
"""

import json
from pathlib import Path

# Human translations for plugin parameters
PLUGIN_TRANSLATIONS = {
    # ForestPack
    "latestversion": {
        "en": "Latest Version",
        "ru": "Последняя версия"
    },
    "showmapinviewport": {
        "en": "Show Map in Viewport",
        "ru": "Показывать текстуру во вьюпорте"
    },
    "checktexturepaths": {
        "en": "Check Texture Paths",
        "ru": "Проверять пути текстур"
    },
    "collecttexturepaths": {
        "en": "Collect Texture Paths",
        "ru": "Собирать пути текстур"
    },
    "collectonlybuiltinlibrary": {
        "en": "Collect Only Built-in Library",
        "ru": "Собирать только встроенную библиотеку"
    },
    "collectexcludenet": {
        "en": "Collect Exclude Network",
        "ru": "Исключать сетевые пути при сборе"
    },
    "libaddprefix": {
        "en": "Library Add Prefix",
        "ru": "Добавлять префикс к библиотеке"
    },
    "vshadowplaneoffset": {
        "en": "V-Shadow Plane Offset",
        "ru": "Смещение плоскости V-Shadow"
    },
    "assigngeomname": {
        "en": "Assign Geometry Name",
        "ru": "Назначать имя геометрии"
    },
    "disablemultithreadrender": {
        "en": "Disable Multithread Render",
        "ru": "Отключить многопоточный рендер"
    },
    "suggestdisplayadjust": {
        "en": "Suggest Display Adjust",
        "ru": "Предлагать настройку отображения"
    },
    "uselaubwerkcloud": {
        "en": "Use Laubwerk Cloud",
        "ru": "Использовать Laubwerk Cloud"
    },
    "cloudpointsbyobject": {
        "en": "Cloud Points Per Object",
        "ru": "Точек облака на объект"
    },
    "cloudhittestmaxpoints": {
        "en": "Cloud Hit-Test Max Points",
        "ru": "Макс. точек для выделения облака"
    },
    "cloudsubseldensity": {
        "en": "Cloud Sub-Selection Density",
        "ru": "Плотность точек подвыделения"
    },
    "cloudsubunseldensity": {
        "en": "Cloud Unselected Density",
        "ru": "Плотность точек невыделенных"
    },
    "rollupgeom": {
        "en": "Geometry Rollup",
        "ru": "Свиток геометрии"
    },
    "rollupdist": {
        "en": "Distribution Rollup",
        "ru": "Свиток распределения"
    },
    "rollupareas": {
        "en": "Areas Rollup",
        "ru": "Свиток областей"
    },
    "rollupedit": {
        "en": "Edit Rollup",
        "ru": "Свиток редактирования"
    },
    "rollupcam": {
        "en": "Camera Rollup",
        "ru": "Свиток камеры"
    },
    "rollupshad": {
        "en": "Shader Rollup",
        "ru": "Свиток шейдера"
    },
    "rollupsurf": {
        "en": "Surface Rollup",
        "ru": "Свиток поверхности"
    },
    "rolluptrans": {
        "en": "Transform Rollup",
        "ru": "Свиток трансформации"
    },
    "rollupmat": {
        "en": "Material Rollup",
        "ru": "Свиток материалов"
    },
    "rollupeff": {
        "en": "Effects Rollup",
        "ru": "Свиток эффектов"
    },
    "rollupanim": {
        "en": "Animation Rollup",
        "ru": "Свиток анимации"
    },
    "rollupdisp": {
        "en": "Display Rollup",
        "ru": "Свиток отображения"
    },
    "rollupabout": {
        "en": "About Rollup",
        "ru": "Свиток о программе"
    },
    "nopopups": {
        "en": "No Popups",
        "ru": "Без всплывающих окон"
    },
    "opensinglerollup": {
        "en": "Open Single Rollup",
        "ru": "Открывать один свиток"
    },
    
    # PhoenixFD
    "Pflow.numbercachedframes": {
        "en": "Number of Cached Frames",
        "ru": "Количество кэшированных кадров"
    },
    "Preview.billboardedicons": {
        "en": "Billboarded Icons",
        "ru": "Иконки-билборды"
    },
    "Logging.logverbosity": {
        "en": "Log Verbosity Level",
        "ru": "Уровень детализации логов"
    },
    "Logging.writelogpresets": {
        "en": "Write Log Presets",
        "ru": "Записывать пресеты в лог"
    },
    "Keyboard.esctostopthesim": {
        "en": "ESC to Stop Simulation",
        "ru": "ESC для остановки симуляции"
    },
    "Gui.pinvolumetricsettingsbydefault": {
        "en": "Pin Volumetric Settings by Default",
        "ru": "Закреплять настройки объёма по умолчанию"
    },
    "Gui.highlightmodifiedcolor": {
        "en": "Highlight Modified Color",
        "ru": "Цвет подсветки изменённых"
    },
    "Gui.highlightmodifiedinputs": {
        "en": "Highlight Modified Inputs",
        "ru": "Подсвечивать изменённые значения"
    },
    "Cache.defaultcachedir": {
        "en": "Default Cache Directory",
        "ru": "Папка кэша по умолчанию"
    },
    
    # V-Ray
    "Global Options.vmcversion": {
        "en": "VMC Version",
        "ru": "Версия VMC"
    },
    "Global Options.vmcdialogpos": {
        "en": "VMC Dialog Position",
        "ru": "Позиция диалога VMC"
    },
    "Global Options.checkupdonstartup": {
        "en": "Check Updates on Startup",
        "ru": "Проверять обновления при запуске"
    },
}

def add_translations_to_database():
    """Add plugin parameter translations to database."""
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading database: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    added = 0
    updated = 0
    
    for param_key, translations in PLUGIN_TRANSLATIONS.items():
        # Try to find parameter in database (with section prefix)
        found_key = None
        for db_key in data.keys():
            if db_key.endswith('.' + param_key) or db_key.lower() == param_key.lower():
                found_key = db_key
                break
        
        if found_key:
            # Update existing
            if 'en' in data[found_key] and 'ru' in data[found_key]:
                data[found_key]['en']['display_name'] = translations['en']
                data[found_key]['ru']['display_name'] = translations['ru']
                updated += 1
                print(f"  [UPDATED] {found_key}: {translations['en']} / {translations['ru']}")
        else:
            # Add new (for parameters not in database yet)
            print(f"  [NOT FOUND] {param_key} - skipping")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append("Added human-readable translations for plugin parameters")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")
    print(f"  Updated: {updated}")
    print(f"  Not found in DB: {len(PLUGIN_TRANSLATIONS) - updated}")

if __name__ == '__main__':
    add_translations_to_database()

