#!/usr/bin/env python3
"""Test parser on sample parameters"""
import sys
sys.path.insert(0, '.')

from autodesk_help_parser import AutodeskHelpParser
from merger import DatabaseMerger

# Test parameters
TEST_PARAMS = [
    "ThreadCount",
    "SaveAssetResolvedFileName",
    "MemoryPool",
    "AdaptiveNavigation",
    "UndoLevels"
]

def main():
    print("=" * 80)
    print("AUTODESK HELP PARSER - TEST RUN")
    print("=" * 80)
    
    parser = AutodeskHelpParser()
    merger = DatabaseMerger('../docs/maxini_ultimate_master_v2.json')
    
    total_found = 0
    total_merged = 0
    
    for param in TEST_PARAMS:
        print(f"\n[{param}]")
        results = parser.parse(param)
        
        for result in results:
            total_found += 1
            if merger.merge_parameter(result):
                total_merged += 1
    
    print("\n" + "=" * 80)
    print(f"Found: {total_found} parameters")
    print(f"Merged: {total_merged} updates")
    print("=" * 80)
    
    if total_merged > 0:
        merger.save()
        print("\n✓ Saved to database!")

if __name__ == '__main__':
    main()

