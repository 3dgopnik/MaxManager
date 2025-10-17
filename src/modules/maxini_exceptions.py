"""MaxINI Editor Exceptions - Custom exception hierarchy."""


class MaxINIEditorError(Exception):
    """Base exception for MaxINI Editor."""

    pass


class ParsingError(MaxINIEditorError):
    """INI file parsing error."""

    pass


class ValidationError(MaxINIEditorError):
    """Parameter validation error."""

    def __init__(self, errors: list[str]) -> None:
        """
        Initialize validation error with list of errors.

        Args:
            errors: List of validation error messages
        """
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s)")


class PresetNotFoundError(MaxINIEditorError):
    """Preset not found."""

    pass


class ChecksumError(MaxINIEditorError):
    """Backup checksum mismatch (corrupted file)."""

    pass


class Max3dsNotFoundError(MaxINIEditorError):
    """No 3ds Max installations detected."""

    pass

