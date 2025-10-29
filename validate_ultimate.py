#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate ultimate database"""
import json

print("=" * 80)
print("VALIDATING ULTIMATE DATABASE")
print("=" * 80)

ultimate = json.load(open('docs/maxini_ultimate_master_v2.json', 'r', encoding='utf-8'))
params = {k: v for k, v in ultimate.items() if k != '_metadata'}
meta = ultimate['_metadata']

print(f"\nTotal parameters: {len(params)}")
print(f"Schema version: {meta['schema_version']}")
print(f"Created: {meta['created_date']}")

# Check structure
print("\n" + "=" * 80)
print("STRUCTURE VALIDATION")
print("=" * 80)

required_fields = ['en', 'ru', 'type', 'default', 'recommended', 'impact', 
                   'status', 'source', 'section', 'ini_file', 'tier', 'introduced_in']

missing_fields = {}
for field in required_fields:
    missing = [k for k, v in params.items() if field not in v]
    if missing:
        missing_fields[field] = len(missing)
        print(f"  [{field}]: {len(missing)} params missing")
    else:
        print(f"  [{field}]: OK")

# Check en/ru structure
print("\n" + "=" * 80)
print("EN/RU STRUCTURE CHECK")
print("=" * 80)

sample = list(params.values())[0]
print(f"\nSample 'en' keys: {list(sample['en'].keys())}")
print(f"Sample 'ru' keys: {list(sample['ru'].keys())}")

en_objects = sum(1 for v in params.values() if isinstance(v.get('en'), dict))
ru_objects = sum(1 for v in params.values() if isinstance(v.get('ru'), dict))
print(f"\n'en' as object: {en_objects}/{len(params)}")
print(f"'ru' as object: {ru_objects}/{len(params)}")

# Check recommended structure
rec_objects = sum(1 for v in params.values() if isinstance(v.get('recommended'), dict))
print(f"'recommended' as object: {rec_objects}/{len(params)}")

# Check impact structure
impact_lists = sum(1 for v in params.values() if isinstance(v.get('impact'), list))
print(f"'impact' as list: {impact_lists}/{len(params)}")

# Check ini_file distribution
print("\n" + "=" * 80)
print("INI FILE DISTRIBUTION")
print("=" * 80)

ini_files = {}
for param_name, param_data in params.items():
    ini = param_data.get('ini_file', 'unknown')
    ini_files[ini] = ini_files.get(ini, 0) + 1

for ini_file, count in sorted(ini_files.items(), key=lambda x: -x[1]):
    print(f"  {ini_file}: {count}")

# Check introduced_in
print("\n" + "=" * 80)
print("INTRODUCED_IN STATISTICS")
print("=" * 80)

has_intro = sum(1 for v in params.values() if v.get('introduced_in'))
no_intro = len(params) - has_intro
print(f"  Has version info: {has_intro}")
print(f"  NULL (unknown): {no_intro}")

if has_intro > 0:
    versions = {}
    for v in params.values():
        intro = v.get('introduced_in')
        if intro:
            versions[intro] = versions.get(intro, 0) + 1
    
    print(f"\nVersion distribution:")
    for ver, count in sorted(versions.items()):
        print(f"  {ver}: {count}")

# Check tier
print("\n" + "=" * 80)
print("TIER DISTRIBUTION")
print("=" * 80)

tiers = {}
for v in params.values():
    tier = v.get('tier', 'unknown')
    tiers[tier] = tiers.get(tier, 0) + 1

for tier, count in sorted(tiers.items()):
    print(f"  {tier}: {count}")

# Show samples
print("\n" + "=" * 80)
print("SAMPLE PARAMETERS")
print("=" * 80)

# Sample from old master
old_master = [k for k in params.keys() if 'Performance.' in k][:1]
print(f"\n1. FROM OLD MASTER: {old_master[0]}")
print(json.dumps(params[old_master[0]], indent=2, ensure_ascii=False)[:500])

# Sample from codex internal
codex_internal = [k for k in params.keys() if 'Internal.' in k][:1]
if codex_internal:
    print(f"\n2. FROM CODEX INTERNAL: {codex_internal[0]}")
    print(json.dumps(params[codex_internal[0]], indent=2, ensure_ascii=False)[:500])

# Sample from codex plugin
codex_plugin = [k for k in params.keys() if any(x in k for x in ['Corona', 'Arnold', 'VRay'])][:1]
if codex_plugin:
    print(f"\n3. FROM CODEX PLUGIN: {codex_plugin[0]}")
    print(json.dumps(params[codex_plugin[0]], indent=2, ensure_ascii=False)[:500])

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)

