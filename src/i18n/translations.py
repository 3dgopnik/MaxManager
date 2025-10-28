"""
Translation system for MaxManager.

Supports multiple languages with easy switching.
"""

from enum import Enum
from typing import Dict


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    RUSSIAN = "ru"


# Global translations dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # UI Elements
        "refresh": "Refresh",
        "revert": "Revert",
        "apply": "Apply",
        "reset": "Reset",
        "save": "Save",
        "undo": "Undo",
        
        # Sidebar buttons
        "sidebar_ini": ".ini",
        "sidebar_ui": "UI",
        "sidebar_script": "Script",
        "sidebar_cuix": "CUIX",
        "sidebar_projects": "Projects",
        
        # Header tabs
        "tab_security": "Security",
        "tab_performance": "Performance",
        "tab_renderer": "Renderer",
        "tab_viewport": "Viewport",
        "tab_settings": "Settings",
        
        # Status messages
        "no_changes": "No changes to save",
        "changes_applied": "Changes applied successfully",
        "changes_reverted": "All changes reverted",
        
        # Common
        "version": "Version",
        "language": "Language",
    },
    "ru": {
        # UI Elements
        "refresh": "Обновить",
        "revert": "Откатить",
        "apply": "Применить",
        "reset": "Сброс",
        "save": "Сохранить",
        "undo": "Отменить",
        
        # Sidebar buttons
        "sidebar_ini": ".ini",
        "sidebar_ui": "Интерфейс",
        "sidebar_script": "Скрипты",
        "sidebar_cuix": "CUIX",
        "sidebar_projects": "Проекты",
        
        # Header tabs
        "tab_security": "Безопасность",
        "tab_performance": "Производительность",
        "tab_renderer": "Рендер",
        "tab_viewport": "Вьюпорт",
        "tab_settings": "Настройки",
        
        # Status messages
        "no_changes": "Нет изменений для сохранения",
        "changes_applied": "Изменения применены успешно",
        "changes_reverted": "Все изменения откачены",
        
        # Common
        "version": "Версия",
        "language": "Язык",
    }
}


# Global current language (SINGLE SOURCE OF TRUTH)
_current_language = Language.ENGLISH  # Default to English


class TranslationManager:
    """Manages translations and language switching."""
    
    def __init__(self, default_language: Language = Language.ENGLISH):
        global _current_language
        _current_language = default_language  # Set global on init
        self._callbacks = []  # UI update callbacks
    
    @property
    def current_language(self):
        """Get current language from GLOBAL state (shared across ALL instances)."""
        global _current_language
        return _current_language
    
    def get(self, key: str, fallback: str = None) -> str:
        """Get translated text for a key."""
        global _current_language
        translations = TRANSLATIONS.get(_current_language.value, {})
        return translations.get(key, fallback or key)
    
    def set_language(self, language: Language):
        """Set current language in GLOBAL state and notify all callbacks."""
        global _current_language
        _current_language = language
        for callback in self._callbacks:
            callback()
    
    def register_callback(self, callback):
        """Register a callback to be called when language changes."""
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """Unregister a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# Global translation manager instance
_translation_manager = TranslationManager()


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager."""
    return _translation_manager


def t(key: str, fallback: str = None) -> str:
    """Shortcut to get translated text."""
    return _translation_manager.get(key, fallback)
