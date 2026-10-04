from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final
import json


@dataclass(frozen=True, slots=True)
class PreservedModule:
    source_id: str
    destinations: tuple[str, ...]
    classes: int
    functions: int
    source_lines: int
    destination_lines: int


_MANIFEST: Final[Path] = Path(__file__).resolve().parents[4] / "docs" / "logic_parity_manifest.json"


def preserved_modules() -> tuple[PreservedModule, ...]:
    """Return the feature-parity inventory generated from the original source tree."""
    raw = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    return tuple(
        PreservedModule(
            source_id=str(row["source_id"]),
            destinations=tuple(str(value) for value in row["destinations"]),
            classes=int(row["source_classes"]),
            functions=int(row["source_functions"]),
            source_lines=int(row["source_lines"]),
            destination_lines=int(row["destination_lines"]),
        )
        for row in raw
    )
