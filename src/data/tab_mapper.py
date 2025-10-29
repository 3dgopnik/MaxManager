"""
Tab mapper - determines which tab a section belongs to.

Maps INI sections to UI tabs based on keywords and patterns.
"""
from typing import Optional

# Tab mapping rules
TAB_KEYWORDS = {
    'Security': ['security', 'safe', 'securitytools', 'securitymessages'],
    'Performance': ['performance', 'openimageio', 'nitrous', 'osl'],
    'Rendering': ['renderer', 'material', 'gamma', 'legacy'],
    'Viewport': ['windowstate', 'selection', 'objectsnap', 'layer', 'viewport'],
    'Paths': ['directories'],
}

# Suffix patterns
PATH_SUFFIXES = ['dirs', 'path', 'dirsttrs']


def get_tab_for_section(section_name: str, ini_file: str = '3dsmax.ini') -> str:
    """
    Determine which tab a section belongs to.
    
    Args:
        section_name: Name of INI section (e.g., 'Performance', 'Security')
        ini_file: Which INI file (e.g., '3dsmax.ini', 'corona.ini')
    
    Returns:
        Tab name: 'Security', 'Performance', 'Rendering', 'Viewport', 
                  'Paths', 'Plugins', or 'Advanced'
    """
    # Plugins: anything not from 3dsmax.ini
    if ini_file != '3dsmax.ini':
        return 'Plugins'
    
    section_lower = section_name.lower()
    
    # Check keyword matches
    for tab_name, keywords in TAB_KEYWORDS.items():
        if any(kw in section_lower for kw in keywords):
            return tab_name
    
    # Check for path-related suffixes
    if any(suffix in section_lower for suffix in PATH_SUFFIXES):
        return 'Paths'
    
    # Everything else goes to Advanced
    return 'Advanced'


def get_dynamic_tabs(sections_by_ini: dict) -> list[str]:
    """
    Create dynamic tab list based on actual sections present.
    
    Args:
        sections_by_ini: {
            '3dsmax.ini': ['Security', 'Performance', ...],
            'corona.ini': ['Corona', ...],
        }
    
    Returns:
        List of tab names to create (only tabs with content)
    """
    tabs_needed = set()
    
    for ini_file, sections in sections_by_ini.items():
        for section in sections:
            tab = get_tab_for_section(section, ini_file)
            tabs_needed.add(tab)
    
    # Order tabs logically
    tab_order = ['Security', 'Performance', 'Rendering', 'Viewport', 'Paths', 'Plugins', 'Advanced']
    
    # Return only tabs that are needed, in correct order
    return [tab for tab in tab_order if tab in tabs_needed]


# Test
if __name__ == '__main__':
    # Test mapping
    test_cases = [
        ('Security', '3dsmax.ini', 'Security'),
        ('Performance', '3dsmax.ini', 'Performance'),
        ('Renderer', '3dsmax.ini', 'Rendering'),
        ('Material Editor', '3dsmax.ini', 'Rendering'),
        ('BitmapDirs', '3dsmax.ini', 'Paths'),
        ('Directories', '3dsmax.ini', 'Paths'),
        ('Corona', 'corona.ini', 'Plugins'),
        ('ForestPack', 'forestpack.ini', 'Plugins'),
        ('Autobackup', '3dsmax.ini', 'Advanced'),
        ('CuiConfiguration', '3dsmax.ini', 'Advanced'),
    ]
    
    print("=" * 80)
    print("TAB MAPPER TEST")
    print("=" * 80)
    
    for section, ini_file, expected in test_cases:
        result = get_tab_for_section(section, ini_file)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} {section:30} ({ini_file:20}) -> {result:15} {'(expected: ' + expected + ')' if result != expected else ''}")
    
    print("\n" + "=" * 80)
    print("DYNAMIC TABS TEST")
    print("=" * 80)
    
    # Test dynamic tabs
    test_sections = {
        '3dsmax.ini': ['Security', 'Performance', 'Renderer', 'BitmapDirs', 'Autobackup'],
        'corona.ini': ['Corona'],
        'forestpack.ini': ['ForestPack'],
    }
    
    tabs = get_dynamic_tabs(test_sections)
    print(f"Sections: {test_sections}")
    print(f"Generated tabs: {tabs}")

