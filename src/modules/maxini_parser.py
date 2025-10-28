"""MaxINI Parser - Parse and validate 3ds Max configuration files."""

import configparser
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Type definitions


class ParamType(Enum):
    """Parameter value types."""

    STRING = "STRING"
    INT = "INT"
    BOOL = "BOOL"
    PATH = "PATH"


class ParamCategory(Enum):
    """Parameter categories for UI organization."""

    RENDERING = "RENDERING"
    MEMORY = "MEMORY"
    PATHS = "PATHS"
    UI = "UI"
    PLUGINS = "PLUGINS"
    NETWORK = "NETWORK"
    PERFORMANCE = "PERFORMANCE"


@dataclass
class ValidationRule:
    """Validation rules for a parameter."""

    min_value: int | None = None
    max_value: int | None = None
    regex_pattern: str | None = None
    must_exist: bool = False
    allowed_values: list[str] | None = None


@dataclass
class MaxINIParameter:
    """Represents a single parameter from max.ini."""

    key: str
    value: str | int | bool | Path
    type: ParamType
    category: ParamCategory
    section: str
    description_ru: str | None = None
    description_en: str | None = None
    validation: ValidationRule | None = None
    default_value: Any = None
    unit: str | None = None


@dataclass
class ValidationError:
    """Validation error details."""

    key: str
    message: str


class MaxINIParser:
    """Parser for 3ds Max configuration files."""

    def __init__(self, validation_rules_path: Path | None = None) -> None:
        """
        Initialize parser with optional validation rules.

        Args:
            validation_rules_path: Path to validation_rules.json
        """
        self.validation_rules: dict[str, dict[str, Any]] = {}
        if validation_rules_path and validation_rules_path.exists():
            with open(validation_rules_path, encoding="utf-8") as f:
                self.validation_rules = json.load(f)

    def load(self, ini_path: Path) -> list[MaxINIParameter]:
        """
        Load and parse max.ini file.

        Args:
            ini_path: Path to 3dsMax.ini

        Returns:
            List of MaxINIParameter objects

        Raises:
            FileNotFoundError: If ini_path doesn't exist
            UnicodeDecodeError: If encoding is not UTF-16 LE
        """
        if not ini_path.exists():
            raise FileNotFoundError(f"INI file not found: {ini_path}")

        config = configparser.ConfigParser()

        # Read file as binary first to detect encoding
        with open(ini_path, 'rb') as f:
            raw_data = f.read()
        
        # Check for UTF-16 LE BOM (FF FE)
        if raw_data.startswith(b'\xff\xfe'):
            content = raw_data.decode('utf-16-le')
        # Check for UTF-8 BOM (EF BB BF)
        elif raw_data.startswith(b'\xef\xbb\xbf'):
            content = raw_data.decode('utf-8-sig')
        # Try UTF-8
        else:
            try:
                content = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                # Last resort - try UTF-16
                content = raw_data.decode('utf-16')
        
        # Remove BOM if still present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        config.read_string(content)

        parameters: list[MaxINIParameter] = []

        for section in config.sections():
            for key in config[section]:
                value = config[section][key]

                # Get validation rules if available (case-insensitive)
                rules = self._get_rules_for_key(key)

                # Determine type
                param_type_str = rules.get("type", "STRING")
                param_type = ParamType[param_type_str]

                # Determine category
                category_str = rules.get("category", "UI")
                category = ParamCategory[category_str]

                # Parse value based on type
                parsed_value: str | int | bool | Path
                if param_type == ParamType.INT:
                    try:
                        parsed_value = int(value)
                    except ValueError:
                        parsed_value = value  # Keep as string if can't parse
                elif param_type == ParamType.BOOL:
                    parsed_value = value.lower() in ("1", "yes", "true", "on")
                elif param_type == ParamType.PATH:
                    parsed_value = Path(value)
                else:
                    parsed_value = value

                # Create validation rule object
                validation: ValidationRule | None = None
                if rules:
                    validation = ValidationRule(
                        min_value=rules.get("min"),
                        max_value=rules.get("max"),
                        regex_pattern=rules.get("regex"),
                        must_exist=rules.get("must_exist", False),
                        allowed_values=rules.get("allowed_values"),
                    )

                param = MaxINIParameter(
                    key=key,
                    value=parsed_value,
                    type=param_type,
                    category=category,
                    section=section,
                    description_ru=rules.get("description_ru"),
                    description_en=rules.get("description_en"),
                    validation=validation,
                    default_value=rules.get("default"),
                    unit=rules.get("unit"),
                )

                parameters.append(param)

        return parameters

    def save(
        self,
        ini_path: Path,
        parameters: list[MaxINIParameter],
        create_backup: bool = True,
    ) -> Path | None:
        """
        Save parameters to max.ini file.

        Args:
            ini_path: Path to 3dsMax.ini
            parameters: List of parameters to save
            create_backup: Whether to backup before writing

        Returns:
            Path to backup file (if created)

        Raises:
            PermissionError: If no write access to ini_path
        """
        # Validation will be done separately via validate()

        config = configparser.ConfigParser()

        # Group by section
        sections: dict[str, dict[str, Any]] = {}
        for param in parameters:
            if param.section not in sections:
                sections[param.section] = {}

            # Convert value to string for INI format
            if isinstance(param.value, bool):
                str_value = "1" if param.value else "0"
            elif isinstance(param.value, Path):
                str_value = str(param.value)
            else:
                str_value = str(param.value)

            sections[param.section][param.key] = str_value

        # Build config
        for section, keys in sections.items():
            config[section] = keys

        # Write to file with UTF-16 LE encoding and BOM
        import io
        output = io.StringIO()
        config.write(output)
        content = output.getvalue()
        with open(ini_path, "w", encoding="utf-16-le") as f:
            f.write('\ufeff' + content)  # Add BOM

        return None  # Backup handled by MaxINIBackupManager

    def validate(self, parameters: list[MaxINIParameter]) -> list[ValidationError]:
        """
        Validate parameters against rules.

        Args:
            parameters: List of parameters to validate

        Returns:
            List of validation errors (empty if all valid)
        """
        errors: list[ValidationError] = []

        for param in parameters:
            if not param.validation:
                continue

            # Type validation
            if param.type == ParamType.INT and not isinstance(param.value, int):
                errors.append(
                    ValidationError(
                        param.key, f"Must be an integer, got {type(param.value).__name__}"
                    )
                )
                continue

            # Range validation
            if param.validation.min_value is not None:
                if isinstance(param.value, int) and param.value < param.validation.min_value:
                    errors.append(
                        ValidationError(
                            param.key,
                            f"Value {param.value} is below minimum {param.validation.min_value}",
                        )
                    )

            if param.validation.max_value is not None:
                if isinstance(param.value, int) and param.value > param.validation.max_value:
                    errors.append(
                        ValidationError(
                            param.key,
                            f"Value {param.value} is above maximum {param.validation.max_value}",
                        )
                    )

            # Path validation
            if param.type == ParamType.PATH and param.validation.must_exist:
                if isinstance(param.value, Path) and not param.value.exists():
                    errors.append(ValidationError(param.key, f"Path does not exist: {param.value}"))

        return errors

    def get_parameter(
        self, parameters: list[MaxINIParameter], key: str
    ) -> MaxINIParameter | None:
        """
        Find parameter by key (case-insensitive).

        Args:
            parameters: List to search
            key: Parameter key (e.g., "RenderThreads")

        Returns:
            Parameter or None if not found
        """
        key_lower = key.lower()
        for param in parameters:
            if param.key.lower() == key_lower:
                return param
        return None

    def group_by_category(
        self, parameters: list[MaxINIParameter]
    ) -> dict[ParamCategory, list[MaxINIParameter]]:
        """
        Group parameters by category for UI display.

        Args:
            parameters: List of parameters

        Returns:
            Dict mapping category to parameters
        """
        grouped: dict[ParamCategory, list[MaxINIParameter]] = {}

        for param in parameters:
            if param.category not in grouped:
                grouped[param.category] = []
            grouped[param.category].append(param)

        return grouped

    def _get_rules_for_key(self, key: str) -> dict[str, Any]:
        """
        Get validation rules for a key (case-insensitive).

        Args:
            key: Parameter key

        Returns:
            Validation rules dict or empty dict
        """
        # Try exact match first
        if key in self.validation_rules:
            return self.validation_rules[key]

        # Try case-insensitive match
        key_lower = key.lower()
        for rule_key, rules in self.validation_rules.items():
            if rule_key.lower() == key_lower:
                return rules

        return {}

