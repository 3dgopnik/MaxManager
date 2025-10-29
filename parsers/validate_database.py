#!/usr/bin/env python3
"""Validate database and find parameters that need enrichment"""
import json
import sys
sys.path.insert(0, '.')

db = json.load(open('docs/maxini_ultimate_master_v2.json', 'r', encoding='utf-8'))
params = {k: v for k, v in db.items() if k != '_metadata'}

print("=" * 80)
print("DATABASE VALIDATION")
print("=" * 80)

# Stats
stats = {
    'total': len(params),
    'no_description': 0,
    'no_recommendation': 0,
    'no_introduced': 0,
    'empty_source': 0,
    'needs_enrichment': []
}

for name, data in params.items():
    issues = []
    
    # Check description
    desc_en = data.get('en', {}).get('description', '')
    if not desc_en or len(desc_en) < 20:
        stats['no_description'] += 1
        issues.append('no_desc')
    
    # Check recommendation
    rec_en = data.get('recommended', {}).get('en', '')
    if not rec_en or rec_en in ['Default value', 'Default from Corona installation']:
        stats['no_recommendation'] += 1
        issues.append('no_rec')
    
    # Check introduced_in
    if not data.get('introduced_in'):
        stats['no_introduced'] += 1
        issues.append('no_version')
    
    # Check source
    sources = data.get('source', [])
    if not sources or sources == [] or sources == ['']:
        stats['empty_source'] += 1
        issues.append('no_source')
    
    if len(issues) >= 2:  # Needs enrichment if 2+ issues
        stats['needs_enrichment'].append({
            'name': name,
            'section': data.get('section'),
            'ini_file': data.get('ini_file'),
            'issues': issues
        })

print(f"\nTotal parameters: {stats['total']}")
print(f"\nQuality issues:")
print(f"  No description: {stats['no_description']} ({stats['no_description']/stats['total']*100:.1f}%)")
print(f"  No recommendation: {stats['no_recommendation']} ({stats['no_recommendation']/stats['total']*100:.1f}%)")
print(f"  No version info: {stats['no_introduced']} ({stats['no_introduced']/stats['total']*100:.1f}%)")
print(f"  No sources: {stats['empty_source']} ({stats['empty_source']/stats['total']*100:.1f}%)")

print(f"\nParameters needing enrichment: {len(stats['needs_enrichment'])}")

# Show top candidates for enrichment (3dsmax.ini only)
candidates = [p for p in stats['needs_enrichment'] if p['ini_file'] == '3dsmax.ini'][:20]

print(f"\nTop 20 candidates from 3dsmax.ini:")
for i, p in enumerate(candidates, 1):
    print(f"  {i}. {p['name']} (issues: {', '.join(p['issues'])})")

print("\n" + "=" * 80)

