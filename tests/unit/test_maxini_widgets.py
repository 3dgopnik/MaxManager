"""Unit tests for MaxINI Editor Widgets."""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from src.modules.maxini_parser import MaxINIParameter, ParamType, ParamCategory, ValidationRule
from src.ui.maxini_widgets import (
    create_parameter_widget,
    IntegerParameterWidget,
    BooleanParameterWidget,
    StringParameterWidget,
    PathParameterWidget,
)


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def int_parameter():
    """Create integer parameter for testing."""
    return MaxINIParameter(
        key="RenderThreads",
        value=8,
        type=ParamType.INT,
        category=ParamCategory.RENDERING,
        section="Rendering",
        validation=ValidationRule(min_value=1, max_value=128),
        description_en="Number of render threads",
        unit="threads",
    )


@pytest.fixture
def bool_parameter():
    """Create boolean parameter for testing."""
    return MaxINIParameter(
        key="AutoBackup",
        value=True,
        type=ParamType.BOOL,
        category=ParamCategory.RENDERING,
        section="Rendering",
        description_en="Enable automatic backup",
    )


@pytest.fixture
def string_parameter():
    """Create string parameter for testing."""
    return MaxINIParameter(
        key="Mode",
        value="3dsMax",
        type=ParamType.STRING,
        category=ParamCategory.UI,
        section="UI",
        description_en="Application mode",
    )


@pytest.fixture
def path_parameter():
    """Create path parameter for testing."""
    return MaxINIParameter(
        key="ProjectFolder",
        value=Path("C:/Projects"),
        type=ParamType.PATH,
        category=ParamCategory.PATHS,
        section="Paths",
        description_en="Default project folder",
    )


def test_create_integer_widget(qapp, int_parameter):
    """Test creating integer parameter widget."""
    widget = create_parameter_widget(int_parameter)
    
    assert isinstance(widget, IntegerParameterWidget)
    assert widget.get_value() == 8


def test_create_boolean_widget(qapp, bool_parameter):
    """Test creating boolean parameter widget."""
    widget = create_parameter_widget(bool_parameter)
    
    assert isinstance(widget, BooleanParameterWidget)
    assert widget.get_value() is True


def test_create_string_widget(qapp, string_parameter):
    """Test creating string parameter widget."""
    widget = create_parameter_widget(string_parameter)
    
    assert isinstance(widget, StringParameterWidget)
    assert widget.get_value() == "3dsMax"


def test_create_path_widget(qapp, path_parameter):
    """Test creating path parameter widget."""
    widget = create_parameter_widget(path_parameter)
    
    assert isinstance(widget, PathParameterWidget)
    assert str(widget.get_value()) == str(Path("C:/Projects"))


def test_integer_widget_value_change(qapp, int_parameter):
    """Test integer widget value change."""
    widget = IntegerParameterWidget(int_parameter)
    
    # Test initial value
    assert widget.get_value() == 8
    
    # Change value
    widget.set_value(16)
    assert widget.get_value() == 16
    
    # Test validation constraints
    widget.value_widget.setValue(0)  # Below min
    assert widget.get_value() == 0  # Should allow but validation will catch later


def test_boolean_widget_value_change(qapp, bool_parameter):
    """Test boolean widget value change."""
    widget = BooleanParameterWidget(bool_parameter)
    
    # Test initial value
    assert widget.get_value() is True
    
    # Change value
    widget.set_value(False)
    assert widget.get_value() is False


def test_string_widget_value_change(qapp, string_parameter):
    """Test string widget value change."""
    widget = StringParameterWidget(string_parameter)
    
    # Test initial value
    assert widget.get_value() == "3dsMax"
    
    # Change value
    widget.set_value("TestMode")
    assert widget.get_value() == "TestMode"


def test_path_widget_value_change(qapp, path_parameter):
    """Test path widget value change."""
    widget = PathParameterWidget(path_parameter)
    
    # Test initial value
    assert str(widget.get_value()) == str(Path("C:/Projects"))
    
    # Change value
    widget.set_value("C:/NewProjects")
    assert widget.get_value() == "C:/NewProjects"


def test_boolean_widget_string_conversion(qapp):
    """Test boolean widget with string values."""
    param = MaxINIParameter(
        key="TestBool",
        value="1",  # String value
        type=ParamType.BOOL,
        category=ParamCategory.UI,
        section="UI",
    )
    
    widget = BooleanParameterWidget(param)
    assert widget.get_value() is True
    
    # Test other string values
    widget.set_value("true")
    assert widget.get_value() is True
    
    widget.set_value("0")
    assert widget.get_value() is False


def test_integer_widget_string_conversion(qapp):
    """Test integer widget with string values."""
    param = MaxINIParameter(
        key="TestInt",
        value="42",  # String value
        type=ParamType.INT,
        category=ParamCategory.UI,
        section="UI",
    )
    
    widget = IntegerParameterWidget(param)
    assert widget.get_value() == 42
