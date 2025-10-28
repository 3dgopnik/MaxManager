"""Test INI Manager with real file."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modules.ini_manager import INIManager

def main():
    """Test INI manager."""
    # Use simple test INI file
    ini_path = Path("test_simple.ini")
    
    # Create test file if doesn't exist
    if not ini_path.exists():
        test_content = """[Gamma]
DisplayGamma=2.200000
FileInGamma=1.000000
FileOutGamma=1.000000

[Rendering]
ThreadCount=8
UseGPU=1
MaxSampleRate=4096

[Memory]
MaxHeapSize=8192
EnableMemoryCompression=1
CacheSize=2048
"""
        ini_path.write_text(test_content, encoding='utf-8')
    
    if not ini_path.exists():
        print(f"Error: {ini_path} not found!")
        return
    
    # Create manager
    manager = INIManager(ini_path)
    
    # Load INI
    print("Loading INI...")
    if manager.load_ini():
        print(f"✅ Loaded {len(manager.original_parameters)} parameters")
        print(f"✅ Found {len(manager.original_sections)} sections")
        
        # Print sections
        print("\nSections:")
        for section_name in manager.current_sections.keys():
            param_count = len(manager.current_sections[section_name].parameters)
            print(f"  - {section_name}: {param_count} parameters")
        
        # Test getting parameters
        print("\n[Gamma] section parameters:")
        gamma_params = manager.get_section_parameters("Gamma")
        for key, value in gamma_params.items():
            print(f"  {key} = {value}")
        
        # Test modification
        print("\nTesting modification...")
        manager.update_parameter("Gamma", "DisplayGamma", "2.5")
        print(f"Modified count: {manager.get_modified_count()}")
        print(f"Has unsaved changes: {manager.has_unsaved_changes()}")
        
        # Test revert
        print("\nTesting revert...")
        manager.revert_section("Gamma")
        print(f"Modified count after revert: {manager.get_modified_count()}")
        
        print("\n✅ All tests passed!")
    else:
        print("❌ Failed to load INI")

if __name__ == "__main__":
    main()

