# План максимального покрытия базы параметров 3ds Max

## Краткое резюме
- Сформирован список направлений, которые помогут довести каталог ini-параметров до полного охвата 3ds Max 2014–2026 и ключевых плагинов.
- Предложены конкретные датасеты, которые стоит добавить в MaxManager (core, рендереры, плагины, автоматизация).
- Подготовлен пошаговый чек-лист для команды по расширению базы и валидации новых параметров.

## Ключевые направления расширения
### 1. Core 3dsmax.ini (2014–2026)
- Собрать оставшиеся секции: `Nitrous.Debug`, `MAXScript`, `OpenSubdiv`, `Slate.MaterialEditor`, `Python` (после 2022), `USD` (2024+).
- Зафиксировать настройки системных модулей: `Security`, `SafeScene`, `Telemetry`, `Analytics`, `LiveSync`.
- Добавить параметры для оффлайн-рендеринга: `Backburner`, `NetworkRendering`, `Batch`.

### 2. Встроенные рендереры
- **Arnold**: `skydome_light`, `render_view`, `ai_options` (логирование, adaptive sampling, RTX).
- **Scanline**: скрытые тумблеры освещения, legacy GI.
- **Art Renderer** и `PhysicalMaterial`: параметры качества, denoiser.

### 3. Популярные рендер-плагины
- **V-Ray** (`vray.ini`): distributed rendering, IPR, VRayDenoiser, VFB2 tweaks.
- **Corona** (`corona.ini`): UHD cache, Denoising, Chaos Scatter параметры.
- **F-Storm** (`fstorm.ini`): режимы GPU, шумоподавление.
- **Octane** (`octane.ini`): AI Light, Out-of-core, упоминания в OSL-дереве.
- **Redshift**: каталог `.redshiftPreferences`, чтобы покрыть GPU overrides.

### 4. Геометрические плагины и эффекты
- **RailClone/Forest Pack**: скрытые параметры генераторов, кэширования и дисплея.
- **Phoenix FD**: сетевые симуляции, cache warming, Chaos Cloud overrides.
- **tyFlow**: параметры времени компиляции, кешей и viewport оптимизаций.
- **GrowFX**, **Multiscatter**, **CityTraffic**: собрать рабочие твики из форумов.

### 5. Автоматизация и инфраструктура
- Каталоги `*.ms`, `*.py`, `*.mcr` с параметрами, которые влияют на ini.
- Хуки для **3ds Max Batch** и **Command Line**.
- Интеграция с **ShotGrid**, **Deadline**, **Royal Render**.

## Данные, которые стоит добавить в репозиторий
| Категория | Формат | Источник | Комментарий |
|-----------|--------|----------|-------------|
| Core 2014–2026 | `data/core_parameters_2014_2026.json` | Autodesk Help, SDK samples | Включить даты появления, диапазоны значений |
| Arnold/Scanline | `data/renderers_builtin.json` | Arnold docs, Autodesk forums | Указать различия между версиями Max |
| V-Ray/Corona | `data/renderers_plugins.json` | Chaos Docs, официальные wiki | Поддержка режимов production/IPR |
| FX плагины | `data/fx_plugins_parameters.json` | Chaos, tyFlow, Exlevel | Документировать зависимости от версий плагинов |
| Автоматизация | `data/automation_toggles.json` | GitHub MaxScript, Deadline docs | Показать влияние на batch/CLI |

## Пошаговые рекомендации
1. **Сбор**: настроить парсеры для Autodesk Help (2014–2026), Chaos Docs, GitHub MaxScript.
2. **Верификация**: для каждого параметра зафиксировать рабочий пример и протестировать на соответствующих версиях (минимум одна сцена).
3. **Структурирование**: распределить параметры по JSON-каталогам (core/renderers/plugins/automation) с унифицированными полями.
4. **Интеграция**: обновить MaxManager, добавив фильтры «Renderers», «FX Plugins», «Automation».
5. **Документация**: подготовить двуязычные гиды по каждому новому каталогу и обновить справочник по поиску.
6. **Автоматические проверки**: добавить в CI smoke-тест, который проверяет наличие обязательных полей и валидность URL.

## Проверка и валидация
- Сценарии запуска 3ds Max (UI и Batch) с логированием времени и ошибок.
- Сравнительные профайлы viewport (FPS, память) для включенных/выключенных твиков.
- Регулярные user-tests с артистами: чек-лист параметров, которые реально помогают.

## Источники для постоянного мониторинга
- Autodesk Area, CGTalk, Polycount (legacy threads, hidden ini tweaks).
- Chaos Forums (V-Ray/Corona/Phoenix FD), tyFlow Discord, Otoy Forums (Octane).
- GitHub-репозитории MaxScript/Python: **ADN samples**, **Ephere repos**, **CG-Press scripts**.
- Релизные заметки 3ds Max 2014–2026 и changelog плагинов.
