from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass(frozen=True)
class ResolvedProject:
    name: str
    root: Path
    folders: List[Path]
    paths: Dict[str, Path]


def _today_compact() -> str:
    return datetime.now().strftime("%Y%m%d")


def load_and_resolve(
    schema_path: Path,
    target_root: Path,
    project_name: str,
    user: Optional[str] = None,
) -> ResolvedProject:
    """Resolve folders and named paths from JSON schema.

    Replaces tokens: {ROOT}, {PROJECT}, {DATE}, {USER}
    """
    data = json.loads(Path(schema_path).read_text(encoding="utf-8"))

    placeholders = {
        "ROOT": str(target_root),
        "PROJECT": project_name,
        "DATE": _today_compact(),
        "USER": user or "",
    }

    def sub(s: str) -> str:
        out = s
        for k, v in placeholders.items():
            out = out.replace("{" + k + "}", v)
        return out

    folders = [Path(sub(p)) for p in data.get("folders", [])]
    paths = {k: Path(sub(v)) for k, v in data.get("paths", {}).items()}

    return ResolvedProject(
        name=data.get("name", project_name),
        root=target_root,
        folders=folders,
        paths=paths,
    )
