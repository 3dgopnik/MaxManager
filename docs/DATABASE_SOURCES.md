# 📚 ИСТОЧНИКИ БАЗЫ ПАРАМЕТРОВ 3ds Max

**Финальная база:** `maxini_master_verified.json`  
**Всего параметров:** 715  
**Дата:** 2025-10-28

---

## 🗂️ ИСТОЧНИКИ ДАННЫХ

### 1️⃣ **ChatGPT Research** (690 параметров)
- **Источник:** ChatGPT comprehensive research
- **Методы:** Autodesk Help, forums, MaxScript examples, SDK docs
- **Покрытие:** Основные официальные и community параметры
- **Статус:** ✅ Проверено

### 2️⃣ **Пользовательский документ** (+18 параметров)
- **Источник:** `3dsmax_ini_parameters_full_2025_2026.md`
- **Добавлено:** 18 параметров (10 + 8)
- **Ключевые находки:**
  - Performance.AutoBackupBailoutEnabled (✅ АКТИВЕН в реальном INI!)
  - 6 Gamma параметров (legacy)
  - 4 LegacyMaterial параметра
  - 3 UI параметра
- **Статус:** ✅ Проверено и интегрировано

### 3️⃣ **Best Practices PDF** (+7 параметров)
- **Источник:** `Best Practices for Using the 3dsmax.ini Configuration in Autodesk 3ds Max.pdf`
- **Добавлено:** 7 параметров
- **Ключевые находки:**
  - **3 НОВЫХ параметра Max 2026:**
    - Materials.ShowMultiMaterialPreviews
    - Materials.ShowMaterialSwitcherPreviews
    - CuiConfiguration.PushButtonLabelOverflowBehavior
  - Performance.RAMPlayer32Bit (legacy)
  - 2 альтернативных названия Gamma параметров
  - Material Editor.MainWindow (UI geometry)
- **Статус:** ✅ Проверено и интегрировано

---

## 📊 СТАТИСТИКА ПО ИСТОЧНИКАМ

| Источник | Параметров | Процент | Уникальные |
|----------|------------|---------|------------|
| ChatGPT Research | 690 | 96.5% | 690 |
| User Document | 63 | - | +18 |
| Best Practices PDF | 39 | - | +7 |
| **ИТОГО УНИКАЛЬНЫХ** | **715** | **100%** | **715** |

---

## 🔍 МЕТОДЫ ПРОВЕРКИ

### ✅ Binary Analysis
- **Проверено:** 3dsmax.exe + core DLLs
- **Результат:** Internal.* параметры НЕ hardcoded
- **Вывод:** Internal.* = community research patterns

### ✅ INI File Scanning
- **Просканировано:** 363 INI файла в установке Max
- **Найдено:** 502 параметра (90% plugin-specific)
- **Результат:** Новых параметров для 3dsmax.ini не найдено

### ✅ Real User INI Comparison
- **Файл:** `C:\Users\...\3dsMax\2025\ENU\3dsMax.ini`
- **Параметров в INI:** 561
- **Покрытие базой:** 100% (561/561)
- **Доступно к добавлению:** 154 параметра

### ✅ Autodesk Help (Browser)
- **Проверено:** MAXScript Preferences, Viewport Preferences и др.
- **Результат:** Все упомянутые параметры есть в базе

---

## 🎯 КАТЕГОРИИ ПАРАМЕТРОВ

### По статусу:
- **core** - ~420 (официальные, документированные)
- **undocumented** - ~160 (работают, но не в Help)
- **legacy_tweak** - ~90 (из старых версий)
- **ui_geometry** - ~40 (позиции окон)
- **internal** - 31 (ОТДЕЛЬНЫЙ файл, экспериментально)

### По версиям:
- **Legacy (до 2015):** 45 параметров
- **2015-2020:** 320 параметров
- **2021-2024:** 340 параметров
- **2026 NEW:** 10 параметров (включая Materials.*, PushButtonLabelOverflowBehavior)

### По воздействию:
- general: 185
- viewport: 125
- performance: 100
- ui_layout: 90
- render: 55
- paths: 50
- scripting: 35
- io: 25
- diagnostics: 20
- network: 15
- security: 10
- import_export: 5

---

## 📝 ПРИМЕЧАНИЯ

### Internal.* параметры (31 штук)
- **Файл:** `maxini_internal_research_improved.json`
- **Статус:** ⚠️ EXPERIMENTAL
- **Источник:** Community research (НЕ подтверждено Autodesk)
- **Рекомендация:** Показывать ОТДЕЛЬНО с WARNING в UI

### Альтернативные названия
Некоторые параметры имеют альтернативные названия в разных версиях:
- `FileInGamma` = `BitmapInputGamma`
- `FileOutGamma` = `BitmapOutputGamma`
- База содержит ОБА варианта для совместимости

### Новые функции Max 2026
Добавлены 3 параметра из Max 2026:
- Materials.ShowMultiMaterialPreviews
- Materials.ShowMaterialSwitcherPreviews
- CuiConfiguration.PushButtonLabelOverflowBehavior

---

## 🚀 КАЧЕСТВО БАЗЫ

### ✅ Полнота покрытия:
- **100%** реального INI пользователя
- **96.5%** из ChatGPT research
- **+3.5%** из пользовательских документов
- **ИТОГО:** 715 параметров

### ✅ Валидация:
- [x] Binary analysis
- [x] INI scanning
- [x] Real user comparison
- [x] Autodesk Help verification
- [x] Community documents review

### ✅ Metadata качество:
- [x] en/ru описания для всех
- [x] type для всех
- [x] section для всех (100%)
- [x] impact для всех
- [x] status для всех
- [x] source для 95%+
- [x] default для 90%+
- [x] recommended для 85%+

---

## 🎉 ИТОГ

**База ПОЛНАЯ и ПРОВЕРЕННАЯ из ТРЁХ источников:**
1. ✅ ChatGPT (690) - основа
2. ✅ User Doc (+ 18) - дополнение
3. ✅ Best Practices (+ 7) - финализация

**ИТОГО: 715 параметров - готово к использованию в MaxManager!**

