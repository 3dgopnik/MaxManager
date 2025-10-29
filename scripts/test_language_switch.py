"""
Test script to verify language switching works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modules.parameter_info_loader import ParameterInfoLoader

# Initialize loader
loader = ParameterInfoLoader()

# Test parameters
test_params = [
    "Font",
    "FontSize",
    "LoadStartupScripts",
    "AutoBackupInterval",
    "HDAOEnabled"
]

print("=" * 80)
print("TESTING PARAMETER INFO LOADER - LANGUAGE SWITCHING")
print("=" * 80)

for param in test_params:
    print(f"\nParameter: {param}")
    print("-" * 80)
    
    # Try English
    en_name = loader.get_display_name(param, "en")
    en_help = loader.get_help_text(param, "en")
    
    # Try Russian
    ru_name = loader.get_display_name(param, "ru")
    ru_help = loader.get_help_text(param, "ru")
    
    print(f"  EN Display Name: {en_name}")
    print(f"  RU Display Name: {ru_name}")
    print(f"  EN Help (first 100 chars): {en_help[:100] if en_help else 'None'}...")
    print(f"  RU Help (first 100 chars): {ru_help[:100] if ru_help else 'None'}...")
    
    # Check if found
    if not en_name and not ru_name:
        print(f"  [!] WARNING: Parameter '{param}' not found in database!")
    elif en_name == ru_name:
        print(f"  [i] INFO: EN and RU names are the same (technical terms)")
    else:
        print(f"  [OK] Different translations found")

print("\n" + "=" * 80)
print("DATABASE STATS")
print("=" * 80)
print(f"Total parameters loaded: {len(loader.parameters)}")
print(f"Database path: {loader.json_path}")
print(f"Database exists: {loader.json_path.exists()}")

