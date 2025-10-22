# src/modules/knowledge_base.py
import json
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

class ParameterType(Enum):
    BOOL = "BOOL"
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    PATH = "PATH"
    ENUM = "ENUM"

class ParameterStatus(Enum):
    STABLE = "STABLE"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED = "DEPRECATED"
    HIDDEN = "HIDDEN"

@dataclass
class INIParameter:
    key: str
    section: str
    type: ParameterType
    default: any
    description: str = ""
    status: ParameterStatus = ParameterStatus.STABLE
    min_value: any = None
    max_value: any = None
    options: list = field(default_factory=list)

@dataclass
class KnowledgeEntry:
    section: str
    key: str
    parameter: INIParameter

class KnowledgeBase:
    def __init__(self, knowledge_file: Path):
        self.knowledge_file = knowledge_file
        self.entries: dict[str, dict[str, INIParameter]] = {}
        self.load_knowledge_base()

    def load_knowledge_base(self):
        if not self.knowledge_file.exists():
            print(f"Knowledge base file not found: {self.knowledge_file}")
            return

        try:
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.entries = {}
            if isinstance(data, list):
                # Handle list of entries
                for entry_data in data:
                    section = entry_data.get("section")
                    key = entry_data.get("key")
                    parameter_data = entry_data.get("parameter")
                    if section and key and parameter_data:
                        self._add_parameter_from_dict(section, key, parameter_data)
            elif isinstance(data, dict):
                # Handle dictionary where keys are sections
                for section, section_data in data.items():
                    for key, parameter_data in section_data.items():
                        self._add_parameter_from_dict(section, key, parameter_data)
            else:
                print(f"Warning: Unknown format for knowledge base file: {self.knowledge_file}")

            print(f"Loaded knowledge base with {self.count_parameters()} entries.")

        except json.JSONDecodeError as e:
            print(f"Error decoding knowledge base JSON: {e}")
        except Exception as e:
            print(f"Failed to load knowledge base: {e}")

    def _add_parameter_from_dict(self, section: str, key: str, parameter_data: dict):
        try:
            param_type = ParameterType(parameter_data.get("type", "STRING").upper())
            param_status = ParameterStatus(parameter_data.get("status", "STABLE").upper())

            parameter = INIParameter(
                key=key,
                section=section,
                type=param_type,
                default=parameter_data.get("default"),
                description=parameter_data.get("description", ""),
                status=param_status,
                min_value=parameter_data.get("min_value"),
                max_value=parameter_data.get("max_value"),
                options=parameter_data.get("options", [])
            )
            if section not in self.entries:
                self.entries[section] = {}
            self.entries[section][key] = parameter
        except ValueError as e:
            print(f"Error parsing parameter '{key}' in section '{section}': {e}")
        except Exception as e:
            print(f"Unexpected error adding parameter '{key}' in section '{section}': {e}")

    def get_parameter(self, section: str, key: str) -> INIParameter | None:
        return self.entries.get(section, {}).get(key)

    def get_parameters_in_section(self, section: str) -> dict[str, INIParameter]:
        return self.entries.get(section, {})

    def get_all_sections(self) -> list[str]:
        return sorted(self.entries.keys())

    def count_parameters(self) -> int:
        return sum(len(section_params) for section_params in self.entries.values())