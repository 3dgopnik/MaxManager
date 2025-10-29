"""
Improve Russian translations in ini_parameters_database.json.

Make translations more natural and human-readable, not word-by-word.
"""

import json
from pathlib import Path


# Human-readable translations for common parameter patterns
TRANSLATIONS = {
    # Common full phrases (check these first)
    "Auto Backup Interval": "Интервал автосохранения",
    "Auto Backup Enabled": "Автосохранение включено",
    "Auto Backup Compress On Auto Backup": "Сжатие при автосохранении",
    "Auto Backup Final Countdown Interval": "Интервал обратного отсчёта",
    "Auto Backup Bailout Enabled": "Аварийное прерывание включено",
    "Auto Backup Show Countdown": "Показывать обратный отсчёт",
    "Auto Backup Prepend Scene Name": "Добавлять имя сцены",
    "Auto Backup Num Files": "Количество копий",
    "Auto Backup File Name": "Имя файла автосохранения",
    
    # Font related
    "Font": "Шрифт",
    "Font Size": "Размер шрифта",
    
    # Load/Save
    "Load Startup Scripts": "Загружать скрипты при запуске",
    "Load Save Scene Scripts": "Скрипты сохранения сцены",
    "Load Save Persistent Globals": "Сохранять глобальные переменные",
    
    # Display/Show
    "Display Update Notification": "Показывать уведомления об обновлении",
    "Display Script Editor On Error": "Открывать редактор при ошибке",
    "Show Command Panel Switch": "Показывать переключение панелей",
    "Show Tool Selections": "Показывать выбор инструментов",
    "Show Menu Selections": "Показывать выбор меню",
    "Show Editor Path": "Показывать путь в редакторе",
    "Show G C Status": "Показывать статус сборщика мусора",
    
    # Security
    "Safe Scene Script Execution Enabled": "Безопасное выполнение скриптов включено",
    "Embedded M A X Script System Commands Execution Blocked": "Блокировка системных команд",
    "Embedded Python Execution Blocked": "Блокировка Python",
    "Embedded Dot Net Execution Blocked": "Блокировка .NET",
    "Safe Script Asset Execution Enabled": "Безопасное выполнение ассетов",
    "Show Security Messages Window On Blocked Commands Enabled": "Показывать окно безопасности",
    "Show Script Editor On Blocked Commands Enabled": "Открывать редактор при блокировке",
    "Block Script Controllers": "Блокировать скриптовые контроллеры",
    "Scene Script Execution Policy": "Политика выполнения скриптов",
    "Last Security Log File": "Последний лог безопасности",
    
    # Paths
    "Install Path": "Путь установки",
    "Project Folder": "Папка проекта",
    "Temp Path": "Папка временных файлов",
    
    # Enable/Disable
    "Enabled": "Включено",
    "Disabled": "Отключено",
    "Enable": "Включить",
    "Disable": "Отключить",
    
    # Renderer
    "Thread Count": "Количество потоков",
    "Scan Band Height": "Высота полосы сканирования",
    "Use Environ Alpha": "Использовать альфа окружения",
    "Filter Background": "Фильтровать фон",
    "Open On Error": "Открывать при ошибке",
    "Dont Show Missing Maps Dlg": "Не показывать диалог отсутствующих текстур",
    "Dont Show Missing U V Warning": "Не показывать предупреждение об UV",
    
    # Viewport
    "Max Texture Size": "Максимальный размер текстуры",
    "Disable H Q Shadows": "Отключить высококачественные тени",
    "Legacy Driver": "Старый драйвер",
    "Ortho Pixel Snap": "Привязка к пикселям в орто",
    
    # Materials
    "Default Material Viewport Mode": "Режим материалов во вьюпорте",
    "Use Physical As Default": "Использовать Physical по умолчанию",
    "Default Map Gamma": "Гамма текстур по умолчанию",
    "Disable Bump Limit": "Отключить ограничение Bump",
    "Legacy Normal Invert Green": "Инвертировать зелёный в Normal (старый)",
    
    # Performance
    "Real Time Playback": "Воспроизведение в реальном времени",
    "Play Active Only": "Воспроизводить только активное",
    "Undo Levels": "Уровней отмены",
    "Backup": "Резервное копирование",
    "Write Compressed": "Сжатое сохранение",
    "Reload Textures": "Перезагружать текстуры",
    
    # Window/Dialog
    "Dimension": "Размеры окна",
    "Position": "Позиция окна",
    "Size": "Размер окна",
    "Maximized": "Развёрнуто",
    
    # Cache
    "Cache Enabled": "Кэш включён",
    "Cache Size": "Размер кэша",
    "Cache Limit M B": "Лимит кэша (МБ)",
    
    # History
    "Count": "Количество",
    "History_00": "История 1",
    "History_01": "История 2",
    "History_02": "История 3",
    "History_03": "История 4",
    "History_04": "История 5",
    "History_05": "История 6",
    
    # Animation
    "Animation": "Анимация",
    "Play Active Only": "Воспроизводить только активное",
    
    # Selection
    "Selection Outline": "Контур выделения",
    "Selection High Light": "Подсветка выделения",
    "Highlight Opacity": "Прозрачность подсветки",
    "Outline Thickness": "Толщина контура",
    "Outline Opacity": "Прозрачность контура",
    "Use Scene Depth": "Использовать глубину сцены",
    "Ignore Backfacing": "Игнорировать обратные грани",
    
    # Common technical terms (keep mixed)
    "H D A O Enabled": "HDAO включён",
    "G F X Type": "Тип GFX",
    "G F X Device": "Устройство GFX",
    "G F X Renderer": "Рендерер GFX",
    
    # Dir entries
    "Dir1": "Папка 1",
    "Dir2": "Папка 2",
    "Dir3": "Папка 3",
    "Dir4": "Папка 4",
    "Dir5": "Папка 5",
    "Dir6": "Папка 6",
    "Dir7": "Папка 7",
    "Dir8": "Папка 8",
    "Dir9": "Папка 9",
    "Dir10": "Папка 10",
    "Dir11": "Папка 11",
    "Dir12": "Папка 12",
    "Dir13": "Папка 13",
    "Dir14": "Папка 14",
    "Dir15": "Папка 15",
    "Dir16": "Папка 16",
    "Dir17": "Папка 17",
    "Dir18": "Папка 18",
    "Dir19": "Папка 19",
    "Dir20": "Папка 20",
    "Dir21": "Папка 21",
    
    # Object Snap
    "Object Snap Plugin State": "Состояние привязки объектов",
    
    # Size/Dimensions
    "Size_ Inches": "Размер (дюймы)",
    "Size_ Meters": "Размер (метры)",
    "Len Min_ Inches": "Мин. длина (дюймы)",
    "Len Min_ Meters": "Мин. длина (метры)",
    "Len Max_ Inches": "Макс. длина (дюймы)",
    "Len Max_ Meters": "Макс. длина (метры)",
    
    # Animation
    "Ignore Controller Range": "Игнорировать диапазон контроллера",
    
    # Render engines
    "Use Arnold RenderView": "Использовать Arnold RenderView",
    "Denoiser mode": "Режим шумоподавления",
    "Maximum sample intensity": "Максимальная интенсивность сэмпла",
    "Scene parsing threads": "Потоков парсинга сцены",
    
    # Intervals
    "Interval Minutes": "Интервал (минуты)",
    "Keep Files": "Сохранять файлы",
    
    # Modifiers
    "Chamfer Modifier Preset": "Пресет модификатора Chamfer",
    
    # Cityscape
    "M Efilter Cat Chk": "Фильтр категорий",
    "M Ewet Chk": "Мокрые поверхности",
    "M Ewinter Chk": "Зимний режим",
    "Material Directory": "Каталог материалов",
    
    # Command Panel
    "Command Panel Columns": "Колонок командной панели",
    "Minimal Column Width": "Минимальная ширина колонки",
    "Rollup Break Threshold": "Порог разрыва свитков",
    
    # CUI Configuration
    "Color File Name": "Файл цветов",
    "Current Hotkey Dir": "Папка горячих клавиш",
    "Current Hotkey File": "Файл горячих клавиш",
    "Current Menu Dir": "Папка меню",
    "Current Menu File": "Файл меню",
    "Current Quad Menu Dir": "Папка quad-меню",
    "Current Quad Menu File": "Файл quad-меню",
    "Loaded Workspace": "Загруженное рабочее пространство",
    "Mouse File Name": "Файл настроек мыши",
    
    # File paths and names
    "Archive Options": "Параметры архивации",
    "Archive Prog": "Программа архивации",
    
    # Directories
    "Additional Icons": "Дополнительные иконки",
    "Additional Macros": "Дополнительные макросы",
    "Additional Scripts": "Дополнительные скрипты",
    "Additional Startup Scripts": "Дополнительные скрипты запуска",
    "Additional Startup Templates": "Дополнительные шаблоны запуска",
    "Archives": "Архивы",
    "Assemblies": "Сборки",
    "Auto Backup": "Автосохранение",
    "Bitmap Proxies": "Прокси текстур",
    "Downloads": "Загрузки",
    "Expressions": "Выражения",
    "Fluid Simulations": "Симуляции жидкости",
    "Heidi Drivers": "Драйверы Heidi",
    "Max Data": "Данные Max",
    "Max Start": "Запуск Max",
    "Page File": "Файл подкачки",
    "Photometric": "Фотометрия",
    "Render Assets": "Ассеты рендера",
    "Render Output": "Вывод рендера",
    "Render Presets": "Пресеты рендера",
    "Startup Scripts": "Скрипты запуска",
    "System Image": "Системные изображения",
    "System Photometric": "Системная фотометрия",
    "System Sound": "Системные звуки",
    "User Settings": "Настройки пользователя",
    "User Tools": "Инструменты пользователя",
    "Video Post": "Video Post",
    
    # Common patterns
    "Absolute Scene Names": "Абсолютные имена сцен",
    "Absolute Sub Objects": "Абсолютные подобъекты",
    "Absolute Transforms": "Абсолютные трансформы",
    "Auto Open Listener": "Автоматически открывать Listener",
    "Enable Macro Recorder": "Включить запись макросов",
    "Initial Heap Size": "Начальный размер кучи",
    "Prevalidate Resource Values": "Предварительная проверка ресурсов",
    "Use Fast Node Name Lookup": "Быстрый поиск имён узлов",
    
    # Backup
    "Auto Increment": "Автоинкремент",
    "Preserve Schematic View": "Сохранять Schematic View",
    "Save File Properties": "Сохранять свойства файла",
    "Auto Unit Convert": "Автоконвертация единиц",
    
    # Performance
    "Transform Gizmo Size": "Размер гизмо трансформации",
    "Transform Gizmo Restore Axis": "Восстанавливать ось гизмо",
    "Non Scale Obj Size": "Размер немасштабируемых объектов",
    "Vertex Dots": "Точки вершин",
    "Vertex Dot Type": "Тип точек вершин",
    "Handle Box Type": "Тип хэндлбокса",
    
    # Display
    "Crossing": "Пересечение",
    "Display Obsolete Msg": "Показывать устаревшие сообщения",
    "Dont Show Missing Material Library Dlg": "Не показывать диалог отсутствующих библиотек",
    "Collapse Message": "Сворачивать сообщения",
    "Lock U I Layout": "Заблокировать интерфейс",
    "Topo Message": "Топологические сообщения",
    "Thumbnails": "Миниатюры",
    "Horiz Text Buttons": "Горизонтальные текстовые кнопки",
    "Fixed Width Text Buttons": "Кнопки фиксированной ширины",
    "Text Button Width": "Ширина текстовых кнопок",
    "Large Buttons": "Большие кнопки",
    "Spinner Wrap": "Циклическое изменение спиннеров",
    "Caddy U I": "Caddy UI",
    "Auto Cross": "Автокросс",
    "Auto Cross Dir": "Направление автокросса",
    "Paint Sel Brush Size": "Размер кисти выделения",
    "Grid Nudge": "Шаг сетки",
    "Vis Edge Method": "Метод видимых рёбер",
    "Link Lines": "Линии связей",
    "Dual Planes": "Двойные плоскости",
    "Auto D Planes": "Автоматические плоскости",
    "Bkg Update On Play": "Обновлять фон при воспроизведении",
    
    # Units
    "Unit Type": "Тип единиц",
    "Unit Scale": "Масштаб единиц",
    "Unit Disp Type": "Тип отображения единиц",
    "Unit Disp Metric Type": "Тип метрических единиц",
    "Unit Disp U S Type": "Тип американских единиц",
    "Unit Disp U S Fraction": "Дробные американские единицы",
    "U S Default Unit": "Американские единицы по умолчанию",
    "Unit Disp Custom Name": "Имя пользовательских единиц",
    "Unit Disp Custom Value": "Значение пользовательских единиц",
    "Unit Disp Custom Unit": "Пользовательские единицы",
    
    # Lighting
    "Lighting System": "Система освещения",
    "S F Mask": "Маска SF",
    "Track Bar Visible": "Показывать таймлайн",
    "Zoom Ext Scale Parallel": "Масштаб Zoom Extents (параллельный)",
    "Zoom Ext Scale Persp": "Масштаб Zoom Extents (перспектива)",
    "Ext Use Sel Set": "Использовать выделение при Extents",
    "Ext All Use Sel Set": "Использовать выделение при Extents All",
    "Use End Point Auto Connect": "Автосоединение конечных точек",
    "Cross Hair Cursor": "Перекрестие курсора",
    "End Point Auto Weld Threshold": "Порог автосварки точек",
    
    # Window State
    "G F X Direct3 D Version": "Версия Direct3D",
    "G F X Direct3 D Device": "Устройство Direct3D",
    "G F X Direct3 D Build": "Сборка Direct3D",
    "Save U Ion Exit": "Сохранять UI при выходе",
    "A T S Pos Proto": "Позиция ATS Proto",
    "A T S Column Positions": "Позиции колонок ATS",
    "Place": "Расположение",
    "Xfm Type In Pos": "Позиция ввода трансформации",
    
    # Nitrous
    "Disable D O F For Background": "Отключить DOF для фона",
    "Default Values Skipped": "Пропустить значения по умолчанию",
    "Anti Aliasing Quality": "Качество сглаживания",
    "Viewport Texture Size Limit": "Лимит размера текстур во вьюпорте",
    "G F X Tex Size": "Размер текстур GFX",
    "Viewport Background Texture Size Limit": "Лимит текстур фона",
    
    # Security Tools
    "Load Security Tools": "Загружать инструменты безопасности",
    
    # Welcome Screen
    "Show At Startup Ext": "Показывать при запуске",
    
    # MAXScript
    "Load Save Persistent Globals": "Сохранять глобальные переменные",
    "Load Save Scene Scripts": "Скрипты сохранения сцены",
    
    # History
    "Max Files": "Максимум файлов",
    
    # Paths
    "Resolve U N C Paths For Mapped Drives": "Разрешать UNC пути для сетевых дисков",
    "Resolve To Relative": "Относительные пути",
    
    # File Import/Export
    "Zoom Extents": "Zoom Extents при импорте",
    "F B X Euler Threshold": "Порог FBX Euler",
    
    # Log File
    "Log Type": "Тип логирования",
    "Log File Longevity Type": "Тип хранения логов",
    "Number of Days": "Количество дней",
    "Log File Size": "Размер лог-файла",
    
    # Layer
    "Layer Propagate": "Распространять слои",
    "Duplicate Layer Without Same Hierarchy": "Дублировать слой без иерархии",
    
    # Legacy Material
    "Bake Shell": "Bake Shell",
    "Standard Mtl F B X Import": "Standard Material при импорте FBX",
    "U V W Unwrap": "UVW Unwrap",
    "Multi": "Multi-материал",
    "D X Material": "DirectX материал",
    "Double Sided Mtl": "Двусторонний материал",
    "3 D S Import": "Импорт 3DS",
    "Blend": "Blend материал",
    "Composite Mtl": "Composite материал",
    "X Ref Material": "XRef материал",
    "A T F Importer": "Импорт ATF",
    "Shellac": "Shellac материал",
    "Morpher Mtl": "Morpher материал",
    "Composite": "Composite",
    "Landform": "Landform",
    
    # Preview
    "Enable Preview": "Включить предпросмотр",
    "Sequence Flag": "Флаг последовательности",
    "Max History": "Максимум истории",
    
    # Installed Components
    "Additional Materials": "Дополнительные материалы",
    "Architectural Materials": "Архитектурные материалы",
    
    # Instance Manager
    "Display M S O Mtl Propagation Msg": "Показывать сообщения MSO материалов",
    
    # Interaction Mode
    "Interaction Mode": "Режим взаимодействия",
    
    # Missing Path Cache
    "Cache Case Sensitive": "Регистрозависимый кэш",
    "Cache Entry Purge Time": "Время очистки записей кэша",
    "Cache Entry Validity Time": "Время действия записей кэша",
    "Cache Local Drives": "Кэшировать локальные диски",
    "Cache Sweep Interval": "Интервал очистки кэша",
    "Exists Time Background Threshold": "Порог фоновой проверки",
    "Include File Watch In Sweep": "Включать наблюдение за файлами",
    "Persist Settings On Exit": "Сохранять настройки при выходе",
    "Reset Cache On Reset": "Сбрасывать кэш при Reset",
    "Reset Cache On Scene Load": "Сбрасывать кэш при загрузке сцены",
    "Use File Watch": "Наблюдать за файлами",
    
    # Modifier Sets
    "Current Mod Set": "Текущий набор модификаторов",
    "Mod Set Entry0": "Набор модификаторов 0",
    "Mod Set Entry1": "Набор модификаторов 1",
    "Mod Set Entry2": "Набор модификаторов 2",
    "Mod Set Entry3": "Набор модификаторов 3",
    "Mod Set Entry4": "Набор модификаторов 4",
    "Mod Set Entry5": "Набор модификаторов 5",
    "Mod Set Entry6": "Набор модификаторов 6",
    "Mod Set Entry10": "Набор модификаторов 10",
    "Mod Set Entry11": "Набор модификаторов 11",
    "Mod Set Entry12": "Набор модификаторов 12",
    "Modifier Set Name0": "Имя набора 0",
    "Modifier Set Name1": "Имя набора 1",
    
    # Modstack
    "Visible": "Видимый",
    "Mod Stack Height": "Высота стека модификаторов",
    "Show All Sets": "Показывать все наборы",
    
    # CUI Configuration (extended)
    "Button Label Overflow Behavior": "Поведение при переполнении меток кнопок",
    "Push Button Label Overflow Behavior": "Переполнение меток кнопок",
    
    # Custom Colors/Menus
    "Custom Color Scheme File": "Файл цветовой схемы",
    "Color File": "Файл цветов",
    "Menu File": "Файл меню",
    
    # Debug/Diagnostics
    "Material Eval Log": "Лог оценки материалов",
    "Viewport Log": "Лог вьюпорта",
    "Asset Resolve Trace": "Трассировка разрешения ассетов",
    "Plugin Load Trace": "Трассировка загрузки плагинов",
    "Log Missing Plugins": "Логировать отсутствующие плагины",
    "Trace External Refs": "Трассировка внешних ссылок",
    "Show Heap Stats": "Показывать статистику кучи",
    "Viewport Capture F P S": "FPS захвата вьюпорта",
    
    # Dialog Resizer
    "Batch Render Tool": "Окно пакетного рендера",
    "M X S Debug Floater": "Окно отладки MAXScript",
    "More Utils Dialog": "Диалог утилит",
    "project Paths": "Пути проекта",
    "system Paths": "Системные пути",
    
    # Directories (extended)
    "Animations": "Анимации",
    "Defaults": "Настройки по умолчанию",
    "Export": "Экспорт",
    "Fonts": "Шрифты",
    "Hardware Shaders Cache": "Кэш аппаратных шейдеров",
    "Help": "Справка",
    "Images": "Изображения",
    "Import": "Импорт",
    "Material Libraries": "Библиотеки материалов",
    "Materials": "Материалы",
    "Plug C F G": "Конфигурация плагинов",
    "Plug C F G_ln": "Конфигурация плагинов (ln)",
    "Previews": "Превью",
    "Proxies": "Прокси",
    "Scenes": "Сцены",
    "Scripts": "Скрипты",
    "Sounds": "Звуки",
    "Standard M A X plug-ins": "Стандартные плагины MAX",
    "Temp": "Временные файлы",
    "Video Post": "Video Post",
    
    # Radiosity
    "Default Init Mesh Size_ Inches": "Начальный размер сетки (дюймы)",
    "Default Init Mesh Size_ Meters": "Начальный размер сетки (метры)",
    "Default Max Mesh Size_ Inches": "Макс. размер сетки (дюймы)",
    "Default Max Mesh Size_ Meters": "Макс. размер сетки (метры)",
    "Default Min Mesh Size_ Inches": "Мин. размер сетки (дюймы)",
    "Default Min Mesh Size_ Meters": "Мин. размер сетки (метры)",
    "Default Self Illum Mesh Size_ Inches": "Размер сетки самосвечения (дюймы)",
    "Default Self Illum Mesh Size_ Meters": "Размер сетки самосвечения (метры)",
    
    # Display (Point Cloud)
    "Point-Cloud HitTest Max": "Макс. точек для выделения облака",
    "cloud Hit Test Max Points": "Макс. точек хит-теста облака",
    "ForestPack Points Per Object": "Точек ForestPack на объект",
    "cloud Points By Object": "Точек облака на объект",
    "Selected Items Point Density": "Плотность точек выделенных",
    "cloud Sub Sel Density": "Плотность точек подвыделения",
    "Unselected Items Point Density": "Плотность точек невыделенных",
    "cloud Sub Unsel Density": "Плотность точек без выделения",
    
    # Email Notifications
    "Email From": "Email отправителя",
    "Email To": "Email получателя",
    "Outgoing Email Server": "Сервер исходящей почты",
    "Notify Progress": "Уведомлять о прогрессе",
    "Notify Failure": "Уведомлять о сбоях",
    "Notify Completion": "Уведомлять о завершении",
    "Notify Every Nth": "Уведомлять каждый N-й кадр",
    
    # Environment Dialog
    "Dimension Qt": "Размеры окна (Qt)",
    
    # File Export/Import
    "Physical Mtl As Phong": "Physical материал как Phong",
    "Physical Mtl As Lambert": "Physical материал как Lambert",
    
    # File List
    "Max Files": "Максимум файлов",
    
    # File Resolution Manager
    "Do Caching": "Использовать кэширование",
    "Search Scene Path": "Искать в путях сцены",
    "Search Scene Path Sub Paths": "Искать в подпапках путей сцены",
    "Caching Duration": "Длительность кэширования",
    
    # ForestPack (специфика плагина - можно на английском)
    "Display Density": "Плотность отображения",
    "Display Limit": "Лимит отображения",
    
    # IBitmapPager
    "Auto Mode Idle Percent": "Процент в режиме ожидания",
    "Auto Mode Render Min Percent": "Мин. процент при рендере",
    "Auto Mode Render Max Percent": "Макс. процент при рендере",
    "Auto Mode Render Greedy Cutoff Percent": "Порог жадного режима",
    
    # Image File Picker
    "Enable Preview": "Включить предпросмотр",
    "Sequence Flag": "Флаг последовательности",
    "Max History": "Максимум истории",
    
    # Isolate Selection
    "Zoom Extents On Isolate": "Zoom Extents при изоляции",
    
    # Layer Manager
    "Layer Propagate": "Распространять слои",
    "Duplicate Layer Without Same Hierarchy": "Дублировать слой без иерархии",
    
    # Legacy Viewports
    "Disable A A": "Отключить сглаживание",
    "Force Software Vertex Processing": "Программная обработка вершин",
    
    # MAXHistory List
    "Count": "Количество",
    
    # MAXScript (extended)
    "Font": "Шрифт",
    "Font Size": "Размер шрифта",
    "Initial Heap Size": "Начальный размер кучи",
    "Load Startup Scripts": "Загружать скрипты при запуске",
    "Load Save Scene Scripts": "Скрипты сохранения сцены",
    "Load Save Persistent Globals": "Сохранять глобальные переменные",
    "Auto Open Listener": "Автоматически открывать Listener",
    "Enable Macro Recorder": "Включить запись макросов",
    "Show Command Panel Switch": "Показывать переключение панелей",
    "Show Tool Selections": "Показывать выбор инструментов",
    "Show Menu Selections": "Показывать выбор меню",
    "Absolute Scene Names": "Абсолютные имена сцен",
    "Absolute Sub Objects": "Абсолютные подобъекты",
    "Absolute Transforms": "Абсолютные трансформы",
    "Use Fast Node Name Lookup": "Быстрый поиск имён узлов",
    "Show G C Status": "Показывать статус GC",
    "Show Editor Path": "Показывать путь в редакторе",
    "Prevalidate Resource Values": "Предварительная проверка ресурсов",
    "Display Script Editor On Error": "Открывать редактор при ошибке",
    
    # Material Editor Position
    "Main Window": "Главное окно",
    "Zoom Level": "Уровень масштаба",
    "Mag Window0": "Окно увеличения 0",
    
    # Noise/Cellular/Marble/etc Params
    "Size_ Inches": "Размер (дюймы)",
    "Size_ Meters": "Размер (метры)",
    
    # NTP (Name Template)
    "Count": "Количество",
    "Last": "Последний",
    "Template0": "Шаблон 0",
    "Template1": "Шаблон 1",
    "Template2": "Шаблон 2",
    
    # NURBS
    "Display": "Отображение",
    "Force Shift": "Принудительный Shift",
    "Single Curve Only": "Только одна кривая",
    
    # Object Snap Settings
    "Display Snap Markers": "Показывать маркеры привязки",
    "Snap Marker Size": "Размер маркеров привязки",
    "Use Axis Constraints": "Использовать ограничения по осям",
    "Snap To Frozen": "Привязка к замороженным",
    "Display Rubber Band": "Показывать резиновую нить",
    "Snap Preview Radius": "Радиус предпросмотра привязки",
    "Snap Radius": "Радиус привязки",
    "Snap Type": "Тип привязки",
    
    # OpenEXR
    "OpenEXR_WriteConfig": "Конфигурация записи OpenEXR",
    
    # OpenImageIO
    "max_open_files": "Максимум открытых файлов",
    "max_memory_MB": "Максимум памяти (МБ)",
    "autotile": "Автоматическая плитка",
    "automip": "Автоматические mip-уровни",
    "autoscanline": "Автоматическое сканирование строк",
    "auto File Update": "Автообновление файлов",
    
    # OSL
    "use_property_cache": "Использовать кэш свойств",
    "Viewport Color Management": "Управление цветом вьюпорта",
    "Viewport U D I M Max Count": "Макс. UDIM во вьюпорте",
    "Optimization Cache": "Кэш оптимизации",
    
    # Performance (extended)
    "Real Time Playback": "Воспроизведение в реальном времени",
    "Play Active Only": "Воспроизводить только активное",
    "Unit Type": "Тип единиц",
    "Unit Scale": "Масштаб единиц",
    "Unit Disp Type": "Тип отображения единиц",
    "Lighting System": "Система освещения",
    "Transform Gizmo Restore Axis": "Восстанавливать ось гизмо",
    "S F Mask": "Маска SF",
    "Track Bar Visible": "Показывать таймлайн",
    "Zoom Ext Scale Parallel": "Масштаб Zoom Extents (параллельный)",
    "Zoom Ext Scale Persp": "Масштаб Zoom Extents (перспектива)",
    "Ext Use Sel Set": "Использовать выделение при Extents",
    "Ext All Use Sel Set": "Использовать выделение при Extents All",
    "Use End Point Auto Connect": "Автосоединение конечных точек",
    "Cross Hair Cursor": "Перекрестие курсора",
    "Thumbnails": "Миниатюры",
    "Horiz Text Buttons": "Горизонтальные текстовые кнопки",
    "Fixed Width Text Buttons": "Кнопки фиксированной ширины",
    "Text Button Width": "Ширина текстовых кнопок",
    "Large Buttons": "Большие кнопки",
    "Spinner Wrap": "Циклическое изменение спиннеров",
    "Undo Levels": "Уровней отмены",
    "Caddy U I": "Caddy UI",
    "Auto Cross": "Автокросс",
    "Auto Cross Dir": "Направление автокросса",
    "Paint Sel Brush Size": "Размер кисти выделения",
    "Grid Nudge": "Шаг сетки",
    "Vis Edge Method": "Метод видимых рёбер",
    "Link Lines": "Линии связей",
    "Dual Planes": "Двойные плоскости",
    "Auto D Planes": "Автоматические плоскости",
    "Bkg Update On Play": "Обновлять фон при воспроизведении",
    "Non Scale Obj Size": "Размер немасштабируемых объектов",
    "Vertex Dots": "Точки вершин",
    "Vertex Dot Type": "Тип точек вершин",
    "Handle Box Type": "Тип хэндлбокса",
    "A C I Palette": "Палитра ACI",
    "Collapse Message": "Сворачивать сообщения",
    "Lock U I Layout": "Заблокировать интерфейс",
    "Topo Message": "Топологические сообщения",
    "Crossing": "Пересечение",
    "Display Obsolete Msg": "Показывать устаревшие сообщения",
    "Dont Show Missing Material Library Dlg": "Не показывать диалог отсутствующих библиотек",
    "Auto Increment": "Автоинкремент",
    "Archive Prog": "Программа архивации",
    "Archive Options": "Параметры архивации",
    "Backup": "Резервное копирование",
    "Reload Textures": "Перезагружать текстуры",
    "Write Compressed": "Сжатое сохранение",
    "Preserve Schematic View": "Сохранять Schematic View",
    "Save File Properties": "Сохранять свойства файла",
    "Auto Unit Convert": "Автоконвертация единиц",
    "Walk Through Mode": "Режим прохождения",
    "Transform Gizmo Size": "Размер гизмо трансформации",
    "Active Color Index": "Индекс активного цвета",
    "End Point Auto Weld Threshold": "Порог автосварки точек",
    "Cust Color1": "Пользовательский цвет 1",
    
    # Preferences Dialog
    "Color Management O C I O Rules Table Height": "Высота таблицы правил OCIO",
    "Color Management O C I O Rules Table Column Widths": "Ширина колонок таблицы OCIO",
    "Color Management O C I O Display View Transform Show Advanced": "Показывать расширенные настройки OCIO",
    
    # Preset Output Size
    "Preset Width": "Ширина пресета",
    "Preset Height": "Высота пресета",
    "Preset Aspect": "Соотношение сторон пресета",
    
    # Render Dialog Position
    "Dimension Qt": "Размеры окна (Qt)",
    
    # Render Message Window
    "Dimension": "Размеры окна",
    
    # Render Output Dirs
    "Dir21": "Папка 21",
    
    # Render Presets MRU Files
    "Render Presets Mru File1": "Недавний пресет рендера 1",
    "Render Presets Mru File2": "Недавний пресет рендера 2",
    "Render Presets Mru File3": "Недавний пресет рендера 3",
    "Render Presets Mru File4": "Недавний пресет рендера 4",
    "Render Presets Mru File5": "Недавний пресет рендера 5",
    "Render Presets Mru File6": "Недавний пресет рендера 6",
    
    # Renderer (extended)
    "Dont Show Missing U V Warning": "Не показывать предупреждение об UV",
    "Use Environ Alpha": "Использовать альфа окружения",
    "Filter Background": "Фильтровать фон",
    "R25 Shadows": "Тени R25",
    "Alpha Out On Additive": "Альфа на аддитивных",
    "Scan Band Height": "Высота полосы сканирования",
    "Thread Count": "Количество потоков",
    "Open On Error": "Открывать при ошибке",
    "Dont Show Missing Maps Dlg": "Не показывать диалог отсутствующих текстур",
    "Disable Atmospherics In V F B": "Отключить атмосферу в VFB",
    "Disable Bitmap Pager": "Отключить пейджинг текстур",
    "Skip Missing Map Dlg On Open": "Пропускать диалог текстур при открытии",
    "Render Output Size": "Размер вывода рендера",
    "Save Rendered Images": "Сохранять отрендеренные изображения",
    "Gamma L U T Enable Legacy": "Включить старую гамма-таблицу",
    
    # Scanline
    "Multi Thread": "Многопоточность",
    
    # Scene Converter
    "Auto Apply On Open": "Автоприменение при открытии",
    "Auto Remove Invalid Instances": "Автоудаление некорректных инстансов",
    "Backup Original Files": "Резервное копирование оригинальных файлов",
    "Convert Only Selected Objects": "Конвертировать только выбранные",
    "Do No Show Missing Mental Ray Dialog": "Не показывать диалог Mental Ray",
    "Last Preset": "Последний пресет",
    "Open When Needed On File Open": "Открывать при необходимости",
    "Size": "Размер",
    
    # Security (extended)
    "Block Script Controllers": "Блокировать скриптовые контроллеры",
    "Embedded Dot Net Execution Blocked": "Блокировка .NET",
    "Embedded M A X Script System Commands Execution Blocked": "Блокировка системных команд",
    "Embedded Python Execution Blocked": "Блокировка Python",
    "Last Security Log File": "Последний лог безопасности",
    "Safe Scene Script Execution Enabled": "Безопасное выполнение скриптов",
    "Safe Script Asset Execution Enabled": "Безопасное выполнение ассетов",
    "Scene Script Execution Policy": "Политика выполнения скриптов",
    "Show Script Editor On Blocked Commands Enabled": "Открывать редактор при блокировке",
    "Show Security Messages Window On Blocked Commands Enabled": "Показывать окно безопасности",
    
    # Selection (extended)
    "Animation": "Анимация",
    "Enabled": "Включено",
    "Selection High Light": "Подсветка выделения",
    "Selection Outline": "Контур выделения",
    "Preview High Light": "Подсветка предпросмотра",
    "Preview Outline": "Контур предпросмотра",
    "Highlight Opacity": "Прозрачность подсветки",
    "Use Scene Depth": "Использовать глубину сцены",
    "Outline Thickness": "Толщина контура",
    "Outline Opacity": "Прозрачность контура",
    "Ignore Backfacing": "Игнорировать обратные грани",
    "Marquee Soft Selection": "Мягкое выделение рамкой",
    
    # Settings Management
    "H D A O Enabled": "HDAO включён",
    
    # Shapes
    "Use Fixed Renderable End Cap Material I D": "Использовать фиксированный ID материала торцов",
    "Fixed Renderable End Cap Material I D": "Фиксированный ID материала торцов",
    "Dont Show Missing Material Library Dlg": "Не показывать диалог библиотек",
    
    # Slate Material Editor
    "Show Node I Ds": "Показывать ID узлов",
    "Position": "Позиция",
    
    # Snaps
    "Angle Increment": "Шаг угла",
    "Percent Increment": "Шаг процента",
    
    # Spinner Precision
    "Spinner Decimals": "Десятичных знаков спиннера",
    "Spinner Snap": "Привязка спиннера",
    "Use Snap": "Использовать привязку",
    
    # Startup
    "Safe Mode": "Безопасный режим",
    "Skip Plugin Scan": "Пропустить сканирование плагинов",
    
    # System
    "Cache Limit M B": "Лимит кэша (МБ)",
    "Dump Logs On Crash": "Сохранять логи при краше",
    "Temp Path": "Путь временных файлов",
    
    # Telemetry
    "Enabled": "Включено",
    "Flush Interval": "Интервал записи",
    "Local Log Retention Days": "Дней хранения локальных логов",
    "Log Level": "Уровень логирования",
    
    # UI Debug
    "Show Dock Hints": "Показывать подсказки докинга",
    "Show Dock State": "Показывать состояние докинга",
    "Show Event Pump": "Показывать насос событий",
    "Disable Acrylic Blur": "Отключить Acrylic Blur",
    "Save Per Workspace": "Сохранять для каждого рабочего пространства",
    "Disable Animations": "Отключить анимации",
    
    # Utility Sets
    "Current Mod Set": "Текущий набор утилит",
    "Modifier Set Name0": "Имя набора 0",
    "Modifier Set Name1": "Имя набора 1",
    
    # Values
    "vert1": "Вершина 1",
    
    # Vertex Normals
    "Use Legacy R4 Vertex Normals": "Использовать старые нормали R4",
    
    # Viewport (extended)
    "Disable H Q Shadows": "Отключить высококачественные тени",
    "Legacy Driver": "Старый драйвер",
    "Max Texture Size": "Максимальный размер текстуры",
    "Ortho Pixel Snap": "Привязка к пикселям в орто",
    
    # Window Position Restore
    "Color Chooser Dialog Position": "Позиция диалога выбора цвета",
    "Customize User Interface Dialog Position": "Позиция диалога настройки интерфейса",
    "Material Browser Dialog Position": "Позиция браузера материалов",
    "Particle View Dialog Position": "Позиция Particle View",
    "Particle View Divider": "Разделитель Particle View",
    
    # Window State (extended)
    "G F X Type": "Тип GFX",
    "G F X Renderer": "Рендерер GFX",
    "G F X Device": "Устройство GFX",
    "G F X Direct3 D Version": "Версия Direct3D",
    "G F X Direct3 D Device": "Устройство Direct3D",
    "G F X Direct3 D Build": "Сборка Direct3D",
    "Save U Ion Exit": "Сохранять UI при выходе",
    "A T S Pos Proto": "Позиция ATS Proto",
    "A T S Column Positions": "Позиции колонок ATS",
    "Place": "Расположение",
    "Maximized": "Развёрнуто",
    "Xfm Type In Pos": "Позиция ввода трансформации",
    "Size": "Размер",
    
    # XRef
    "Auto Update": "Автообновление",
    
    # tyFlow (plugin specific - можно на английском)
    "editor Rollout": "Свиток редактора",
    "editor Rollout Val": "Значение свитка редактора",
    "ty Diffusion_root_path": "Путь tyDiffusion",
    "ty Diffusion_assets Version": "Версия ассетов tyDiffusion",
}


def get_better_translation(en_name: str, ru_desc: str) -> str:
    """
    Get better human-readable translation.
    
    Args:
        en_name: English parameter name
        ru_desc: Russian description (for context)
    
    Returns:
        Improved Russian translation
    """
    # Check exact match first
    if en_name in TRANSLATIONS:
        return TRANSLATIONS[en_name]
    
    # Keep original if it's technical abbreviation or already OK
    if len(en_name) <= 4 or en_name.isupper():
        return en_name
    
    # For unknown params, return English (better than bad translation)
    return en_name


def process_database(input_path: Path):
    """Process and improve Russian translations."""
    print(f"Loading: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data.pop('_metadata', None)
    
    improved_count = 0
    kept_english_count = 0
    total_params = len(data)
    
    print(f"Processing {total_params} parameters...\n")
    
    for key, param_data in data.items():
        if 'en' in param_data and 'ru' in param_data:
            en_name = param_data['en'].get('display_name', '')
            current_ru_name = param_data['ru'].get('display_name', '')
            ru_desc = param_data['ru'].get('description', '')
            
            if not en_name:
                continue
            
            # Get better translation
            new_ru_name = get_better_translation(en_name, ru_desc)
            
            if new_ru_name != current_ru_name:
                param_data['ru']['display_name'] = new_ru_name
                improved_count += 1
                
                # Show samples
                if improved_count <= 20:
                    print(f"  {key}")
                    print(f"    EN: {en_name}")
                    print(f"    OLD RU: {current_ru_name}")
                    print(f"    NEW RU: {new_ru_name}")
                    print()
                
                if new_ru_name == en_name:
                    kept_english_count += 1
    
    if metadata:
        if 'improvements_v2' not in metadata:
            metadata['improvements_v2'] = []
        metadata['improvements_v2'].append("Improved Russian translations to be more natural")
        data = {'_metadata': metadata, **data}
    
    print(f"\nSaving...")
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")
    print(f"  Improved: {improved_count} translations")
    print(f"  Kept English (technical): {kept_english_count}")
    print(f"  Total params: {total_params}")


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / "docs" / "ini_parameters_database.json"
    
    # Backup
    backup_path = db_path.parent / "ini_parameters_database_backup3.json"
    print(f"Creating backup: {backup_path}")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    process_database(db_path)

