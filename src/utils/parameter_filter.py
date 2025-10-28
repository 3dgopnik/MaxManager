"""
Parameter filtering utilities for INI editor.

Filters ONLY window coordinates and truly useless technical data.
Goal: Give access to ALL useful settings!
"""

import re


# Patterns for TRULY useless parameters (only window positions)
HIDDEN_PATTERNS = [
    # Window positions and sizes ONLY
    r'^dimension$',
    r'^position$',
    r'^place$',
    r'^mainwindow$',
    r'.*dialogposition$',
    r'.*windowposition$',
    r'^magwindow\d+$',
    r'^atsposproto$',
    r'^atscolumnpositions$',
    r'^xfmtypeinpos$',
    
    # Binary modifier sets (impossible to edit)
    r'^modsetentry\d+$',
    
    # Values section (unknown binary)
    r'^vert\d+$',
]


def is_technical_parameter(param_name: str) -> bool:
    """
    Check if parameter is truly useless (window coords only).
    
    Args:
        param_name: Parameter name (case-insensitive)
        
    Returns:
        True if parameter should be hidden, False otherwise
    """
    param_lower = param_name.lower()
    
    for pattern in HIDDEN_PATTERNS:
        if re.match(pattern, param_lower):
            return True
    
    return False


def filter_parameters(parameters: dict) -> dict:
    """
    Filter out ONLY window coordinates and binary data.
    
    Args:
        parameters: Dictionary of {param_name: param_value}
        
    Returns:
        Filtered dictionary with useful parameters
    """
    return {
        name: value
        for name, value in parameters.items()
        if not is_technical_parameter(name)
    }
