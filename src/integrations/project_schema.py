from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime


@dataclass
class ResolvedProject:
    name: str
    root: Path
    folders: List[Path]
    paths: Dict[str, Path]


def _format_date_token() -> str:
    return datetime.now().strftime("%Y%m%d")


def load_and_resolve(schema_path: Path, target_root: Path, project_name: str) -> ResolvedProject:
    """
    Load JSON schema and resolve folders/paths for a concrete project root.
    - Replaces tokens: {ROOT}, {PROJECT}, {DATE}
    """
    data = json.loads(Path(schema_path).read_text(encoding="utf-8"))

    tokens = {
        "{ROOT}": str(target_root).replace("\\", "/"),
        "{PROJECT}": project_name,
        "{DATE}": _format_date_token(),
    }

    def _resolve_string(s: str) -> str:
        out = s
        for k, v in tokens.items():
            out = out.replace(k, v)
        return out

    # Resolve folders
    folders = [Path(_resolve_string(p)) for p in data.get("folders", [])]

    # Resolve named paths
    paths = {k: Path(_resolve_string(v)) for k, v in data.get("paths", {}).items()}

    return ResolvedProject(name=project_name, root=target_root, folders=folders, paths=paths)
