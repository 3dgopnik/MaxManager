"""
Name formatter for INI parameters.

Converts technical parameter names to human-readable format.
"""

import re


def camel_case_split(text: str) -> str:
    """
    Split camelCase or PascalCase text into separate words.
    
    Examples:
        safescenescriptexecutionenabled -> Safe Scene Script Execution Enabled
        ThreadCount -> Thread Count
        UseGPU -> Use GPU
    
    Args:
        text: camelCase or lowercase text
        
    Returns:
        Space-separated capitalized words
    """
    # First, handle acronyms (GPU, UI, etc.)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    
    # Insert space before uppercase letters
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Split on spaces and capitalize each word
    words = text.split()
    
    # Capitalize first letter of each word
    formatted_words = []
    for word in words:
        if word.upper() in ['GPU', 'UI', 'CPU', 'RAM', 'API', 'URL', 'HTTP', 'FTP', 
                            'MAX', 'INI', 'EXE', 'DLL', 'XML', 'JSON', 'HDAO']:
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.capitalize())
    
    return ' '.join(formatted_words)


def format_parameter_name(param_name: str, use_title_case: bool = True) -> str:
    """
    Format parameter name for display.
    
    Args:
        param_name: Raw parameter name from INI
        use_title_case: Whether to capitalize words
        
    Returns:
        Formatted readable name
    """
    # Remove common prefixes/suffixes
    name = param_name.strip()
    
    # Split camelCase
    readable = camel_case_split(name)
    
    # Clean up common patterns
    readable = readable.replace('Enabled', '')
    readable = readable.replace('Disabled', '')
    
    # Trim whitespace
    readable = readable.strip()
    
    return readable if readable else param_name


def get_short_name(param_name: str, max_length: int = 40) -> str:
    """
    Get shortened version of parameter name.
    
    Args:
        param_name: Parameter name
        max_length: Maximum length
        
    Returns:
        Shortened name with "..." if needed
    """
    formatted = format_parameter_name(param_name)
    
    if len(formatted) <= max_length:
        return formatted
    
    # Truncate and add ellipsis
    return formatted[:max_length-3] + '...'


# Example usage and testing
if __name__ == "__main__":
    test_names = [
        'safescenescriptexecutionenabled',
        'embeddedmaxscriptsystemcommandsexecutionblocked',
        'ThreadCount',
        'UseGPU',
        'DisplayGamma',
        'AutoBackupEnabled',
        'HDAOEnabled',
    ]
    
    print("Parameter name formatting examples:\n")
    for name in test_names:
        formatted = format_parameter_name(name)
        short = get_short_name(name, 30)
        print(f"{name:50s} -> {formatted:40s} (short: {short})")

