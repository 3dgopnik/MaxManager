"""Add 26 new parameters from ChatGPT plugin research"""
import json

# Load current database
with open('docs/maxini_master_verified.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

metadata = db.pop('_metadata')

# All 26 new parameters with full data
new_params = {
    "Performance.FindMissingMapsOnSceneLoad": {
        "en": "Find Missing Maps on Scene Load",
        "ru": "Поиск отсутствующих карт при загрузке сцены",
        "description": {
            "en": "When enabled, 3ds Max will search for missing texture maps every time a scene is opened. Turning this off can significantly speed up scene loading.",
            "ru": "Если включено, 3ds Max при каждой загрузке сцены ищет отсутствующие текстуры. Отключение заметно ускоряет загрузку сцен."
        },
        "type": "bool",
        "default": "1",
        "recommended": {
            "en": "Set to 0 to disable automatic missing-map search (improves load times); set to 1 for default behavior.",
            "ru": "Установите 0 для отключения автопоиска карт (быстрее загрузка); 1 для поведения по умолчанию."
        },
        "impact": ["performance", "io"],
        "status": "undocumented",
        "source": ["https://polycount.com/discussion/223680/"],
        "section": "Performance",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2015"
    },
    "Performance.ResolveAssetPathsOnSave": {
        "en": "Resolve Asset Paths on Save",
        "ru": "Обработка путей ассетов при сохранении",
        "description": {
            "en": "Controls whether 3ds Max resolves external asset file paths when saving. Disabling reduces save times and file size.",
            "ru": "Определяет обработку путей внешних ресурсов при сохранении. Отключение уменьшает время сохранения и размер файла."
        },
        "type": "bool",
        "default": "1",
        "recommended": {
            "en": "Set to 0 for faster saves (smaller files); set to 1 to store full asset metadata (default).",
            "ru": "Установите 0 для быстрого сохранения (меньший файл); 1 для полных метаданных."
        },
        "impact": ["performance", "io"],
        "status": "undocumented",
        "source": ["https://cganimator.com/3dsmax-tips-1-3dsmax-ini-setting-for-file-load-save-speed-up/"],
        "section": "Performance",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2015"
    },
    "AnimationPreferences.IgnoreControllerRange": {
        "en": "Ignore Controller Range",
        "ru": "Игнорировать диапазон контроллера",
        "description": {
            "en": "New animation controllers ignore parent range settings by default.",
            "ru": "Новые анимационные контроллеры игнорируют диапазон родительского контроллера."
        },
        "type": "bool",
        "default": "0",
        "recommended": {
            "en": "0 to respect range limits (default); 1 for controllers to ignore default range.",
            "ru": "0 для учёта ограничений диапазона (по умолчанию); 1 чтобы игнорировать."
        },
        "impact": ["ui_layout"],
        "status": "core",
        "source": ["https://cganimator.com/3dsmax-tips-4-my-rig-is-stuck-at-the-previous-animation-range/"],
        "section": "AnimationPreferences",
        "ini_file": "3dsmax.ini",
        "tier": "free",
        "introduced_in": "2022"
    },
    "Performance.BufferedFileBufferSize": {
        "en": "File I/O Buffer Size",
        "ru": "Размер буфера ввода-вывода",
        "description": {
            "en": "Buffer size for file reading/writing of bitmaps (in bytes). Larger buffer improves I/O performance.",
            "ru": "Размер буфера для чтения/записи bitmap файлов (в байтах). Увеличение улучшает производительность."
        },
        "type": "int",
        "default": "262144",
        "recommended": {
            "en": "Use 524288 (512 KB) or 1048576 (1 MB) for large files. Default 262144 (256 KB) is adequate.",
            "ru": "Используйте 524288 (512 КБ) или 1048576 (1 МБ) для крупных файлов. По умолчанию 262144 (256 КБ)."
        },
        "impact": ["performance", "io"],
        "status": "core",
        "source": ["https://cgpress.org/archives/3ds-max-2023-2-released/"],
        "section": "Performance",
        "ini_file": "3dsmax.ini",
        "tier": "free",
        "introduced_in": "2023"
    },
    "OpenPBR.UseSimplifiedViewportShader": {
        "en": "Simplified Viewport Shader",
        "ru": "Упрощённый шейдер вьюпорта",
        "description": {
            "en": "Uses lightweight shader for OpenPBR in viewport. Disabling gives full-quality preview at performance cost.",
            "ru": "Использует облегчённый шейдер для OpenPBR во вьюпорте. Отключение даёт полное качество ценой производительности."
        },
        "type": "bool",
        "default": "1",
        "recommended": {
            "en": "Keep 1 for smooth viewport; set 0 for highest fidelity preview (slower).",
            "ru": "Оставьте 1 для плавного вьюпорта; 0 для максимально точного отображения (медленнее)."
        },
        "impact": ["viewport"],
        "status": "core",
        "source": ["https://cganimator.com/unofficial-3dsmax-whats-new/"],
        "section": "OpenPBR",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2026"
    },
    "Arnold.UseArnoldRenderView": {
        "en": "Use Arnold RenderView",
        "ru": "Использовать Arnold RenderView",
        "description": {
            "en": "Clicking Render opens Arnold RenderView instead of standard frame buffer.",
            "ru": "Нажатие Render открывает Arnold RenderView вместо стандартного окна кадра."
        },
        "type": "bool",
        "default": "0",
        "recommended": {
            "en": "1 for Arnold RenderView (real-time feedback); 0 for classic frame buffer.",
            "ru": "1 для Arnold RenderView (обратная связь в реальном времени); 0 для классического окна."
        },
        "impact": ["render", "ui_layout"],
        "status": "core",
        "source": ["https://help.autodesk.com/view/ARNOL/ENU/"],
        "section": "Arnold",
        "ini_file": "Arnold.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "system.sceneExportPath": {
        "en": "Corona Scene Export Path",
        "ru": "Путь экспорта сцены Corona",
        "description": {
            "en": "File path to export Corona scene (.scn) during render.",
            "ru": "Путь для экспорта сцены Corona (.scn) во время рендеринга."
        },
        "type": "string",
        "default": "",
        "recommended": {
            "en": "Leave empty unless you need to export scene for debugging.",
            "ru": "Оставьте пустым если не требуется экспорт для отладки."
        },
        "impact": ["io"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "system",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2022"
    },
    "dr.numThreads": {
        "en": "Corona DR Slave Threads",
        "ru": "Потоки CPU Corona DR",
        "description": {
            "en": "Number of CPU threads on Corona distributed rendering slaves. 0=unlimited, -1=all but one core.",
            "ru": "Количество потоков CPU на узлах Corona DR. 0=без ограничения, -1=все кроме одного ядра."
        },
        "type": "int",
        "default": "-1",
        "recommended": {
            "en": "Use -1 (all but one core on slaves); 0 for all cores; or specific number to limit CPU.",
            "ru": "Используйте -1 (все кроме одного ядра); 0 для всех ядер; или число для ограничения CPU."
        },
        "impact": ["performance", "network"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "dr",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2022"
    },
    "mtlEditor.lightsSize": {
        "en": "Material Editor Light Size",
        "ru": "Размер света в редакторе материалов",
        "description": {
            "en": "Size of lights in Corona Material Editor previews. Larger=softer, smaller=sharper.",
            "ru": "Размер света в предпросмотре Corona. Больше=мягче, меньше=резче."
        },
        "type": "float",
        "default": "1.0",
        "recommended": {
            "en": "Keep 1.0; increase for softer preview lighting or decrease for focused light.",
            "ru": "Оставьте 1.0; увеличьте для мягкого света или уменьшите для резкого."
        },
        "impact": ["ui_layout"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "mtlEditor",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2022"
    },
    "mtlEditor.lightsIntensity": {
        "en": "Material Editor Light Intensity",
        "ru": "Яркость света в редакторе материалов",
        "description": {
            "en": "Brightness of lights in Corona Material Editor preview.",
            "ru": "Яркость света в предпросмотре Corona."
        },
        "type": "float",
        "default": "1.0",
        "recommended": {
            "en": "Keep 1.0; increase if previews too dark; decrease for dimmer lighting.",
            "ru": "Оставьте 1.0; увеличьте если превью тёмный; уменьшите для приглушённого света."
        },
        "impact": ["ui_layout"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "mtlEditor",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2022"
    },
    "renderStamp.fontSize": {
        "en": "Render Stamp Font Size",
        "ru": "Размер шрифта штампа рендера",
        "description": {
            "en": "Font size of render stamp text in Corona VFB.",
            "ru": "Размер шрифта текста штампа в Corona VFB."
        },
        "type": "int",
        "default": "8",
        "recommended": {
            "en": "Adjust if stamp text too small/large. Use 10-12 for larger text.",
            "ru": "Меняйте если текст мелкий/крупный. Используйте 10-12 для увеличения."
        },
        "impact": ["ui_layout"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "renderStamp",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2022"
    },
    "system.threadPriority": {
        "en": "Corona Thread Priority",
        "ru": "Приоритет потоков Corona",
        "description": {
            "en": "CPU priority of Corona rendering threads. Values: Low, BelowNormal, Normal, AboveNormal, High.",
            "ru": "Приоритет потоков Corona в Windows. Значения: Low, BelowNormal, Normal, AboveNormal, High."
        },
        "type": "string",
        "default": "Low",
        "recommended": {
            "en": "Leave Low for minimal interference. Use Normal/High only if Corona needs maximum CPU.",
            "ru": "Оставьте Low для минимального влияния. Normal/High только если нужен максимум CPU."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "system",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2023"
    },
    "shading.enableAa": {
        "en": "Disable Beauty Antialiasing",
        "ru": "Отключить сглаживание beauty",
        "description": {
            "en": "When true, disables antialiasing for Corona beauty pass. Produces aliased images.",
            "ru": "При true отключает сглаживание для beauty прохода Corona. Создаёт зазубренные края."
        },
        "type": "bool",
        "default": "false",
        "recommended": {
            "en": "Keep false (AA on) for normal rendering; true only for special needs (masks, etc).",
            "ru": "Оставьте false (сглаживание вкл) для обычного рендера; true только для спецзадач."
        },
        "impact": ["render"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "shading",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2023"
    },
    "geometry.displace.maxSizeScreenOutFrustumMultiplier": {
        "en": "Displacement Out-Frustum Multiplier",
        "ru": "Коэффициент дисплейсмента вне фрустума",
        "description": {
            "en": "Extends displacement calculation outside camera frustum by factor. Increases RAM usage.",
            "ru": "Расширяет расчёт дисплейсмента за пределы фрустума камеры. Увеличивает использование RAM."
        },
        "type": "float",
        "default": "1.0",
        "recommended": {
            "en": "Use 1 by default; increase (e.g. 2) for reflections if displaced geometry cut off. Watch memory!",
            "ru": "Используйте 1 по умолчанию; увеличьте (напр. 2) для отражений если дисплейсмент обрезается. Следите за памятью!"
        },
        "impact": ["performance", "render"],
        "status": "core",
        "source": ["https://support.chaos.com/hc/en-us/articles/4528609584017"],
        "section": "geometry",
        "ini_file": "corona.ini",
        "tier": "advanced",
        "introduced_in": "2023"
    },
    "Display.cloudPointsByObject": {
        "en": "ForestPack Points Per Object",
        "ru": "Количество точек на объект ForestPack",
        "description": {
            "en": "Points to represent each ForestPack object in point-cloud mode. Default 250,000.",
            "ru": "Точек для отображения каждого объекта ForestPack в режиме облака точек. По умолчанию 250 000."
        },
        "type": "int",
        "default": "250000",
        "recommended": {
            "en": "250000 for balance; increase for denser clouds (slower); 0 for adaptive mode.",
            "ru": "250000 для баланса; увеличьте для плотности (медленнее); 0 для адаптивного режима."
        },
        "impact": ["viewport", "performance"],
        "status": "core",
        "source": ["https://docs.itoosoft.com/forestpack/forest-plugin/display"],
        "section": "Display",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "Display.cloudHitTestMaxPoints": {
        "en": "Point-Cloud HitTest Max",
        "ru": "Макс точек для теста попадания",
        "description": {
            "en": "Max points for hit-testing in point-cloud. Lower improves selection performance.",
            "ru": "Максимум точек для теста попадания в облаке. Уменьшение улучшает производительность выбора."
        },
        "type": "int",
        "default": "1000",
        "recommended": {
            "en": "Keep 1000; reduce (e.g. 500) if selection slow in dense clouds.",
            "ru": "Оставьте 1000; уменьшите (напр. 500) если выбор медленный в плотных облаках."
        },
        "impact": ["viewport", "performance"],
        "status": "core",
        "source": ["https://docs.itoosoft.com/forestpack/forest-plugin/display"],
        "section": "Display",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "Display.cloudSubSelDensity": {
        "en": "Selected Items Point Density",
        "ru": "Плотность точек выделенных элементов",
        "description": {
            "en": "Percentage of points for selected items in Custom Edit. 300%=3x more points.",
            "ru": "Процент точек для выделенных элементов в Custom Edit. 300%=в 3 раза больше."
        },
        "type": "int",
        "default": "300",
        "recommended": {
            "en": "Keep 300 (3x density for selected). Higher=denser; 100=same as unselected.",
            "ru": "Оставьте 300 (3x плотность для выделенных). Выше=плотнее; 100=как невыделенные."
        },
        "impact": ["viewport"],
        "status": "core",
        "source": ["https://docs.itoosoft.com/forestpack/forest-plugin/display"],
        "section": "Display",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "Display.cloudSubUnselDensity": {
        "en": "Unselected Items Point Density",
        "ru": "Плотность точек невыделенных элементов",
        "description": {
            "en": "Percentage of points for unselected items. 100%=base count.",
            "ru": "Процент точек для невыделенных элементов. 100%=базовое количество."
        },
        "type": "int",
        "default": "100",
        "recommended": {
            "en": "Keep 100; lower if you want unselected less visible.",
            "ru": "Оставьте 100; снизьте если нужно уменьшить видимость невыделенных."
        },
        "impact": ["viewport"],
        "status": "core",
        "source": ["https://docs.itoosoft.com/forestpack/forest-plugin/display"],
        "section": "Display",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "General.samplesCacheLimit": {
        "en": "ForestPack Samples Cache Limit",
        "ru": "Лимит кеша образцов ForestPack",
        "description": {
            "en": "Memory limit for animated geometry samples (KB). Default 10 GB to prevent unlimited growth.",
            "ru": "Лимит памяти для образцов анимированной геометрии (КБ). По умолчанию 10 ГБ."
        },
        "type": "int",
        "default": "10485760",
        "recommended": {
            "en": "Use default 10485760 (10 GB); set 0 for no limit (caution!); lower to conserve memory.",
            "ru": "Используйте 10485760 (10 ГБ); 0 для снятия лимита (осторожно!); меньше для экономии памяти."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.itoosoft.com/changelog/2024/09/23/forestpack-9"],
        "section": "General",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2024"
    },
    "General.optimizeAutomaterial": {
        "en": "ForestPack Optimize Material",
        "ru": "Оптимизация материалов ForestPack",
        "description": {
            "en": "Use Material Optimizer in ForestPack. Off reverts to old material behavior.",
            "ru": "Использовать Material Optimizer в ForestPack. Выкл возвращает старый алгоритм."
        },
        "type": "bool",
        "default": "1",
        "recommended": {
            "en": "Keep 1 for optimized workflow; 0 only if issues or prefer legacy behavior.",
            "ru": "Оставьте 1 для оптимизированного процесса; 0 только при проблемах."
        },
        "impact": ["render"],
        "status": "legacy_tweak",
        "source": ["https://oakcorp.net/archives/5312"],
        "section": "General",
        "ini_file": "forestpack.ini",
        "tier": "advanced",
        "introduced_in": "2016"
    },
    "PhoenixFD.NumberOfPumps": {
        "en": "Phoenix FD Pumps",
        "ru": "Насосы Phoenix FD",
        "description": {
            "en": "0=disable Phoenix FD pumps (prevents some crashes); 1=enable pumps.",
            "ru": "0=отключить насосы Phoenix FD (предотвращает краши); 1=включить."
        },
        "type": "int",
        "default": "1",
        "recommended": {
            "en": "Use 0 if simulation crashes; 1 for default (more accurate fluid).",
            "ru": "Установите 0 при крашах симуляции; 1 по умолчанию (точнее жидкость)."
        },
        "impact": ["stability", "simulation"],
        "status": "undocumented",
        "source": ["https://www.facebook.com/groups/phoenixfd"],
        "section": "PhoenixFD",
        "ini_file": "phoenixfd.ini",
        "tier": "advanced",
        "introduced_in": "2023"
    },
    "tyFlow.PinThreads": {
        "en": "Pin tyFlow Threads",
        "ru": "Закрепить потоки tyFlow",
        "description": {
            "en": "Pin worker threads to specific CPU cores. Improves performance on high-core CPUs (Threadripper).",
            "ru": "Закрепить потоки за ядрами CPU. Улучшает производительность на многоядерных CPU (Threadripper)."
        },
        "type": "bool",
        "default": "0",
        "recommended": {
            "en": "Enable (1) on Threadripper/high-core CPUs; leave 0 for most systems.",
            "ru": "Включите (1) на Threadripper/многоядерных CPU; оставьте 0 для обычных систем."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.tyflow.com/tyflow_particles/object/cpu/"],
        "section": "tyFlow",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2025"
    },
    "tyFlow.UseThreadingHints": {
        "en": "tyFlow Threading Hints",
        "ru": "Подсказки потоков tyFlow",
        "description": {
            "en": "Use tyFlow internal hints for thread allocation. Disabling may hurt performance.",
            "ru": "Использовать внутренние подсказки tyFlow для распределения потоков. Отключение снижает производительность."
        },
        "type": "bool",
        "default": "1",
        "recommended": {
            "en": "Keep 1 for optimal performance; 0 only if directed by tyFlow support.",
            "ru": "Оставьте 1 для оптимальной производительности; 0 только по рекомендации поддержки."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.tyflow.com/tyflow_particles/object/cpu/"],
        "section": "tyFlow",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2025"
    },
    "tyFlow.HighThreadPriority": {
        "en": "tyFlow High Priority",
        "ru": "Высокий приоритет tyFlow",
        "description": {
            "en": "Run tyFlow threads at high Windows priority. Faster simulations but impacts system responsiveness.",
            "ru": "Запускать потоки tyFlow с высоким приоритетом Windows. Быстрее симуляции, но снижает отзывчивость."
        },
        "type": "bool",
        "default": "0",
        "recommended": {
            "en": "Use 0 unless you need max CPU for tyFlow; 1 accelerates but makes PC less responsive.",
            "ru": "Используйте 0 если не нужен максимум CPU; 1 ускоряет но снижает отзывчивость ПК."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.tyflow.com/tyflow_particles/object/cpu/"],
        "section": "tyFlow",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2025"
    },
    "tyFlow.ReservedProcessors": {
        "en": "tyFlow Reserved Cores",
        "ru": "Резерв ядер tyFlow",
        "description": {
            "en": "Number of CPU cores to leave unused by tyFlow. Reserves CPU for other tasks.",
            "ru": "Количество ядер CPU которые tyFlow не будет использовать. Резервирует CPU для других задач."
        },
        "type": "int",
        "default": "0",
        "recommended": {
            "en": "Use 0 to let tyFlow use all cores; set number (e.g. 2) to reserve cores.",
            "ru": "Используйте 0 для всех ядер; укажите число (напр. 2) для резерва ядер."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.tyflow.com/tyflow_particles/object/cpu/"],
        "section": "tyFlow",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2025"
    },
    "tyFlow.PinThreadsPhysX": {
        "en": "Pin PhysX Threads",
        "ru": "Закрепить потоки PhysX",
        "description": {
            "en": "Pin PhysX simulation threads to specific cores. Improves determinism on some systems.",
            "ru": "Закрепить потоки PhysX симуляции за ядрами. Улучшает детерминированность на некоторых системах."
        },
        "type": "bool",
        "default": "0",
        "recommended": {
            "en": "Use 1 if PhysX performance issues on many cores; leave 0 otherwise.",
            "ru": "Установите 1 при проблемах PhysX на многоядерном CPU; оставьте 0 в остальных случаях."
        },
        "impact": ["performance"],
        "status": "core",
        "source": ["https://docs.tyflow.com/tyflow_particles/object/cpu/"],
        "section": "tyFlow",
        "ini_file": "3dsmax.ini",
        "tier": "advanced",
        "introduced_in": "2025"
    }
}

# Add to database
added = 0
for param_name, param_data in new_params.items():
    if param_name not in db:
        db[param_name] = param_data
        added += 1
        ini_file = param_data.get('ini_file', '3dsmax.ini')
        print(f'+ {param_name} ({ini_file})')

# Update metadata
metadata['total_parameters'] = len(db)
metadata['date'] = '2025-10-28 (ChatGPT plugins)'
metadata['improvements'].append(f'Added {added} plugin parameters (Corona, ForestPack, tyFlow, Phoenix, Arnold)')

# Tier stats
free_count = sum(1 for p in db.values() if p.get('tier') == 'free')
advanced_count = sum(1 for p in db.values() if p.get('tier') == 'advanced')
metadata['tier_distribution'] = {'free': free_count, 'advanced': advanced_count}

# Save
final_db = {'_metadata': metadata}
final_db.update(db)

with open('docs/maxini_master_verified.json', 'w', encoding='utf-8') as f:
    json.dump(final_db, f, ensure_ascii=False, indent=2)

print(f'\\nAdded: {added} parameters')
print(f'Total: {len(db)} parameters')
print(f'FREE: {free_count} | ADVANCED: {advanced_count}')

