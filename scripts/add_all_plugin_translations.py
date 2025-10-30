"""
Add ALL missing plugin parameter translations.
"""

import json
from pathlib import Path

# Massive translation dictionary for all visible plugin params
PLUGIN_TRANSLATIONS = {
    # ForestPack - display rollups
    "handlevrayproxies": {"en": "Handle V-Ray Proxies", "ru": "Обрабатывать V-Ray Proxy"},
    "usecoloredicon": {"en": "Use Colored Icons", "ru": "Использовать цветные иконки"},
    "fontchanged": {"en": "Font Changed", "ru": "Шрифт изменён"},
    "fontfamily": {"en": "Font Family", "ru": "Семейство шрифта"},
    "fontsize": {"en": "Font Size", "ru": "Размер шрифта"},
    "fontweight": {"en": "Font Weight", "ru": "Насыщенность шрифта"},
    "fontitalic": {"en": "Font Italic", "ru": "Курсивный шрифт"},
    "samplescachelimit": {"en": "Samples Cache Limit", "ru": "Лимит кэша сэмплов"},
    "Lock billboards to camera": {"en": "Lock Billboards to Camera", "ru": "Привязать билборды к камере"},
    "Adaptive distribution step": {"en": "Adaptive Distribution Step", "ru": "Шаг адаптивного распределения"},
    "ForestPack Optimize Material": {"en": "Optimize Material", "ru": "Оптимизация материалов"},
    "ForestPack Samples Cache Limit": {"en": "Samples Cache Limit", "ru": "Лимит кэша сэмплов"},
    
    # V-Ray Scene Convert Options
    "Scene Convert Options.bakedtexpath": {"en": "Baked Texture Path", "ru": "Путь запечённых текстур"},
    "Scene Convert Options.bakedtexgammaauto": {"en": "Baked Texture Gamma Auto", "ru": "Авто-гамма запечённых текстур"},
    "Scene Convert Options.bakedtexgamma": {"en": "Baked Texture Gamma", "ru": "Гамма запечённых текстур"},
    "Scene Convert Options.bakedtexorigsize": {"en": "Baked Texture Original Size", "ru": "Оригинальный размер запечённых текстур"},
    "Scene Convert Options.showtexmapinvp": {"en": "Show Texture Map in Viewport", "ru": "Показывать текстуры во вьюпорте"},
    "Scene Convert Options.savescenentisstate": {"en": "Save Scene NTIS State", "ru": "Сохранять состояние NTIS сцены"},
    "Scene Convert Options.switchrenderengine": {"en": "Switch Render Engine", "ru": "Переключать рендер-движок"},
    "Scene Convert Options.batchsceneconvert": {"en": "Batch Scene Convert", "ru": "Пакетная конвертация сцен"},
    "Scene Convert Options.convertdirection": {"en": "Convert Direction", "ru": "Направление конвертации"},
    "Scene Convert Options.scenemtlsmapsconvert": {"en": "Scene Materials/Maps Convert", "ru": "Конвертация материалов/текстур сцены"},
    
    # V-Ray Advanced Convert Options
    "Advanced Convert Options.batchadvconvert": {"en": "Batch Advanced Convert", "ru": "Пакетная продвинутая конвертация"},
    "Advanced Convert Options.proxyconvert": {"en": "Proxy Convert", "ru": "Конвертация прокси"},
    "Advanced Convert Options.proxyconvertdirection": {"en": "Proxy Convert Direction", "ru": "Направление конвертации прокси"},
    "Advanced Convert Options.proxypreviewtype": {"en": "Proxy Preview Type", "ru": "Тип превью прокси"},
    "Advanced Convert Options.proxyoverwrite": {"en": "Proxy Overwrite", "ru": "Перезаписывать прокси"},
    "Advanced Convert Options.proxycollect": {"en": "Proxy Collect", "ru": "Собирать прокси"},
    "Advanced Convert Options.bitmapconvert": {"en": "Bitmap Convert", "ru": "Конвертация текстур"},
    "Advanced Convert Options.bitmapconvertdirection": {"en": "Bitmap Convert Direction", "ru": "Направление конвертации текстур"},
    "Advanced Convert Options.cameraconvert": {"en": "Camera Convert", "ru": "Конвертация камер"},
    "Advanced Convert Options.cameraconvertdirection": {"en": "Camera Convert Direction", "ru": "Направление конвертации камер"},
    
    # V-Ray Advanced Tools Options
    "Advanced Tools Options.switchcolorspaceselnode": {"en": "Switch Color Space Selected Node", "ru": "Переключать цветовое пространство выбранного узла"},
    "Advanced Tools Options.rgbprim": {"en": "RGB Primaries", "ru": "RGB первичные"},
    "Advanced Tools Options.useoslmapnode": {"en": "Use OSL Map Node", "ru": "Использовать OSL Map ноду"},
    "Advanced Tools Options.useociofile": {"en": "Use OCIO File", "ru": "Использовать файл OCIO"},
    "Advanced Tools Options.correctcolormapping": {"en": "Correct Color Mapping", "ru": "Корректировать маппинг цветов"},
    "Advanced Tools Options.renamedupnames": {"en": "Rename Duplicate Names", "ru": "Переименовывать дубликаты имён"},
    "Advanced Tools Options.standardsel": {"en": "Standard Selection", "ru": "Стандартное выделение"},
    
    # V-Ray Batch Process Settings
    "Batch Process Settings.silent": {"en": "Silent Mode", "ru": "Тихий режим"},
    "Batch Process Settings.subdirinclude": {"en": "Include Subdirectories", "ru": "Включать подпапки"},
    "Batch Process Settings.savetoorigfolder": {"en": "Save to Original Folder", "ru": "Сохранять в исходную папку"},
    "Batch Process Settings.overwrite": {"en": "Overwrite Existing", "ru": "Перезаписывать существующие"},
    "Batch Process Settings.savetomaxversion": {"en": "Save to Max Version", "ru": "Сохранять для версии Max"},
    "Batch Process Settings.saveinoriginalversion": {"en": "Save in Original Version", "ru": "Сохранять в исходной версии"},
}


def add_translations():
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    print(f"Loading: {db_path}")
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    updated = 0
    added = 0
    
    for param_key, translations in PLUGIN_TRANSLATIONS.items():
        # Find in database (with or without prefix)
        found_key = None
        for db_key in data.keys():
            if db_key == param_key or db_key.endswith('.' + param_key):
                found_key = db_key
                break
        
        if found_key:
            # Update display names
            if 'en' in data[found_key] and 'ru' in data[found_key]:
                data[found_key]['en']['display_name'] = translations['en']
                data[found_key]['ru']['display_name'] = translations['ru']
                updated += 1
                print(f"  [UPD] {found_key}: {translations['ru']}")
        else:
            print(f"  [NOT IN DB] {param_key}")
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append(f"Added translations for {updated} plugin parameters")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone! Updated {updated} parameters")

if __name__ == '__main__':
    add_translations()

