"""Verify Autodesk-documented INI parameters against the master database."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence, Tuple

DEFAULT_DOC_PATH = Path("docs/3dsmax_ini_parameters_full_2025_2026.md")
DEFAULT_DATABASE_PATH = Path("docs/maxini_master_verified.json")

# Mapping used when a heading contains multiple sections and parameters must be
# routed to a specific section depending on their name.
MULTI_SECTION_OVERRIDES: Mapping[Tuple[str, ...], Mapping[str, str]] = {
    ("CustomMenus", "CustomColors", "KeyboardFile"): {
        "MenuFile": "CustomMenus",
        "ColorFile": "CustomColors",
        "KeyboardFile": "KeyboardFile",
    }
}

PARAMETER_RANGE_PATTERN = re.compile(r"^(?P<prefix>Dir\d+)\s+[–-]\s+DirN$")
SECTION_HEADING_PATTERN = re.compile(r"^##\s+(.*)")
SECTION_TOKEN_PATTERN = re.compile(r"\[(.+?)\]")
BOLD_TOKEN_PATTERN = re.compile(r"\*\*(.+?)\*\*")


@dataclass(frozen=True)
class ParameterEntry:
    """Parameter extracted from the Autodesk markdown document."""

    section: str
    parameter: str
    raw_section_tokens: Tuple[str, ...]

    @property
    def key(self) -> str:
        return f"{self.section}.{self.parameter}"


def extract_parameters_from_doc(doc_path: Path = DEFAULT_DOC_PATH) -> List[ParameterEntry]:
    """Parse the Autodesk markdown document and collect parameter entries."""

    text = doc_path.read_text(encoding="utf-8")
    current_sections: Tuple[str, ...] = tuple()
    entries: List[ParameterEntry] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_match = SECTION_HEADING_PATTERN.match(line)
        if heading_match:
            tokens = SECTION_TOKEN_PATTERN.findall(heading_match.group(1))
            current_sections = tuple(tokens)
            continue

        if "|" not in line:
            continue

        names = [name.strip() for name in BOLD_TOKEN_PATTERN.findall(line) if name.strip()]
        if not names or not current_sections:
            continue

        for name in names:
            section = determine_section_for_name(name, current_sections)
            parameter = normalize_parameter_name(name)
            entries.append(ParameterEntry(section=section, parameter=parameter, raw_section_tokens=current_sections))

    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique_entries: List[ParameterEntry] = []
    for entry in entries:
        if entry.key in seen:
            continue
        seen.add(entry.key)
        unique_entries.append(entry)

    return unique_entries


def determine_section_for_name(name: str, sections: Tuple[str, ...]) -> str:
    """Return the section that should host the parameter name."""

    if not sections:
        raise ValueError("Section context is required to map parameter names.")

    if sections in MULTI_SECTION_OVERRIDES:
        override = MULTI_SECTION_OVERRIDES[sections]
        mapped = override.get(name)
        if mapped:
            return mapped

    # Default to the first section listed in the heading.
    return sections[0]


def normalize_parameter_name(name: str) -> str:
    """Normalize parameter tokens to match database keys."""

    match = PARAMETER_RANGE_PATTERN.match(name)
    if match:
        return match.group("prefix")

    return name


def load_database_keys(database_path: Path = DEFAULT_DATABASE_PATH) -> set[str]:
    """Load the verified parameter database and extract keys."""

    data = json.loads(database_path.read_text(encoding="utf-8"))
    data.pop("_metadata", None)
    return set(data)


def find_missing_parameters(doc_entries: Sequence[ParameterEntry], database_keys: Iterable[str]) -> List[ParameterEntry]:
    """Return parameters present in docs but absent in the database."""

    key_set = set(database_keys)
    return [entry for entry in doc_entries if entry.key not in key_set]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Autodesk documentation coverage against the parameter database.")
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC_PATH, help="Path to the Autodesk markdown document.")
    parser.add_argument(
        "--database", type=Path, default=DEFAULT_DATABASE_PATH, help="Path to the verified parameter database JSON file."
    )
    args = parser.parse_args()

    entries = extract_parameters_from_doc(args.doc)
    keys = load_database_keys(args.database)
    missing = find_missing_parameters(entries, keys)

    if not missing:
        print(f"All {len(entries)} Autodesk-documented parameters are present in the database.")
        return 0

    print("The following Autodesk-documented parameters are missing from the database:")
    for entry in missing:
        section_list = ", ".join(entry.raw_section_tokens)
        print(f"- {entry.key} (heading sections: {section_list})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
