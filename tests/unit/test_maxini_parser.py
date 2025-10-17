"""Unit tests for MaxINIParser."""

import tempfile
from pathlib import Path

import pytest

from src.modules.maxini_parser import (
    MaxINIParameter,
    MaxINIParser,
    ParamCategory,
    ParamType,
    ValidationError,
    ValidationRule,
)


@pytest.fixture
def sample_ini_file() -> Path:
    """Create a temporary max.ini file for testing."""
    content = """[Rendering]
RenderThreads=8
AutoBackup=1
BackupInterval=10

[Memory]
MemoryPool=512
DynamicHeapSize=1

[Paths]
ProjectFolder=C:\\Projects
"""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-16-le", suffix=".ini", delete=False
    ) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def validation_rules() -> Path:
    """Create temporary validation rules."""
    rules = """{
  "RenderThreads": {
    "type": "INT",
    "min": 1,
    "max": 128,
    "category": "RENDERING"
  },
  "MemoryPool": {
    "type": "INT",
    "min": 128,
    "max": 8192,
    "category": "MEMORY"
  }
}"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(rules)
        temp_path = Path(f.name)

    yield temp_path

    temp_path.unlink(missing_ok=True)


def test_parser_init_without_rules() -> None:
    """Test parser initialization without validation rules."""
    parser = MaxINIParser()
    assert parser.validation_rules == {}


def test_parser_init_with_rules(validation_rules: Path) -> None:
    """Test parser initialization with validation rules."""
    parser = MaxINIParser(validation_rules)
    assert "RenderThreads" in parser.validation_rules
    assert parser.validation_rules["RenderThreads"]["type"] == "INT"


def test_load_ini_file(sample_ini_file: Path, validation_rules: Path) -> None:
    """Test loading max.ini file."""
    parser = MaxINIParser(validation_rules)
    parameters = parser.load(sample_ini_file)

    assert len(parameters) > 0

    # Check RenderThreads parameter
    render_threads = parser.get_parameter(parameters, "RenderThreads")
    assert render_threads is not None
    assert render_threads.value == 8
    assert render_threads.type == ParamType.INT


def test_load_nonexistent_file() -> None:
    """Test loading non-existent file raises error."""
    parser = MaxINIParser()
    with pytest.raises(FileNotFoundError):
        parser.load(Path("nonexistent.ini"))


def test_validate_parameters() -> None:
    """Test parameter validation."""
    parser = MaxINIParser()

    # Valid parameter
    valid_param = MaxINIParameter(
        key="RenderThreads",
        value=8,
        type=ParamType.INT,
        category=ParamCategory.RENDERING,
        section="Rendering",
        validation=ValidationRule(min_value=1, max_value=128),
    )

    errors = parser.validate([valid_param])
    assert len(errors) == 0

    # Invalid parameter (below min)
    invalid_param = MaxINIParameter(
        key="RenderThreads",
        value=0,
        type=ParamType.INT,
        category=ParamCategory.RENDERING,
        section="Rendering",
        validation=ValidationRule(min_value=1, max_value=128),
    )

    errors = parser.validate([invalid_param])
    assert len(errors) == 1
    assert "below minimum" in errors[0].message


def test_group_by_category(sample_ini_file: Path, validation_rules: Path) -> None:
    """Test grouping parameters by category."""
    parser = MaxINIParser(validation_rules)
    parameters = parser.load(sample_ini_file)

    grouped = parser.group_by_category(parameters)

    assert ParamCategory.RENDERING in grouped
    assert ParamCategory.MEMORY in grouped
    assert len(grouped[ParamCategory.RENDERING]) > 0


def test_save_parameters(sample_ini_file: Path, validation_rules: Path) -> None:
    """Test saving parameters to file."""
    parser = MaxINIParser(validation_rules)
    parameters = parser.load(sample_ini_file)

    # Modify a parameter
    render_threads = parser.get_parameter(parameters, "RenderThreads")
    if render_threads:
        render_threads.value = 16

    # Save to new file
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as f:
        output_path = Path(f.name)

    try:
        parser.save(output_path, parameters, create_backup=False)

        # Reload and verify
        new_parameters = parser.load(output_path)
        new_render_threads = parser.get_parameter(new_parameters, "RenderThreads")
        assert new_render_threads is not None
        assert new_render_threads.value == 16
    finally:
        output_path.unlink(missing_ok=True)

