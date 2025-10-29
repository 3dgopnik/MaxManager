#!/usr/bin/env python3
"""
Simple database enricher - adds recommendations and versions
Uses community knowledge + manual curation
"""
import json
from typing import Dict

# Community-sourced recommendations (manually curated)
RECOMMENDATIONS = {
    "Renderer.ThreadCount": {
        "en": "-1 (auto) = recommended for workstations. Set manual count only for render farms.",
        "ru": "-1 (авто) = рекомендуется для рабочих станций. Ручной подсчёт только для рендер-ферм.",
        "introduced_in": "2009"
    },
    "Performance.MemoryPool": {
        "en": "2048-4096 MB for 16GB RAM, 8192+ MB for 32GB+ RAM. Higher = faster but more memory usage.",
        "ru": "2048-4096 МБ для 16ГБ ОЗУ, 8192+ МБ для 32ГБ+ ОЗУ. Больше = быстрее но больше памяти.",
        "introduced_in": "2010"
    },
    "Performance.UndoLevels": {
        "en": "20-50 recommended. Higher = more memory usage. Lower for heavy scenes.",
        "ru": "20-50 рекомендуется. Больше = больше памяти. Меньше для тяжёлых сцен.",
        "introduced_in": "2009"
    },
    "Security.SafeSceneScriptExecutionEnabled": {
        "en": "1 = enable (RECOMMENDED). Blocks malicious scripts in downloaded scenes.",
        "ru": "1 = включить (РЕКОМЕНДУЕТСЯ). Блокирует вредоносные скрипты в скачанных сценах.",
        "introduced_in": "2020"
    },
    "Autobackup.AutoBackupEnabled": {
        "en": "1 = enable (RECOMMENDED). Auto-saves work every N minutes.",
        "ru": "1 = включить (РЕКОМЕНДУЕТСЯ). Автосохранение работы каждые N минут.",
        "introduced_in": "2009"
    },
    "Autobackup.AutoBackupInterval": {
        "en": "5-15 minutes recommended. Lower = safer but more disk activity.",
        "ru": "5-15 минут рекомендуется. Меньше = безопаснее но больше активности диска.",
        "introduced_in": "2009"
    },
}

def enrich_database(db_path: str):
    """Add recommendations to database"""
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    params = {k: v for k, v in db.items() if k != '_metadata'}
    meta = db['_metadata']
    
    updated = 0
    for param_name, enrichment in RECOMMENDATIONS.items():
        if param_name in params:
            param = params[param_name]
            
            # Update recommendation
            if enrichment.get('en'):
                param['recommended']['en'] = enrichment['en']
                param['recommended']['ru'] = enrichment.get('ru', enrichment['en'])
            
            # Update version
            if enrichment.get('introduced_in'):
                param['introduced_in'] = enrichment['introduced_in']
            
            updated += 1
            print(f"[OK] {param_name}")
    
    # Save
    db_updated = {'_metadata': meta, **dict(sorted(params.items()))}
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db_updated, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated: {updated} parameters")

if __name__ == '__main__':
    from pathlib import Path
    db_path = Path(__file__).parent.parent / 'docs' / 'maxini_ultimate_master_v2.json'
    enrich_database(str(db_path))

