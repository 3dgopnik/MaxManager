"""Localization module for MaxManager."""

from .translations import (
    Language,
    TranslationManager,
    get_translation_manager,
    t,
    TRANSLATIONS
)

__all__ = [
    'Language',
    'TranslationManager',
    'get_translation_manager',
    't',
    'TRANSLATIONS'
]
