"""
Utility helpers for loading Guardian AI datasets.

The loader is intentionally lightweight and backend-friendly:
- Reads demo data from data/demo
- Reads PAN-style datasets from data/pan2012 when present
- Returns normalized message dicts for ML ingestion
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data"
PAN2012_ROOT = DATA_ROOT / "pan2012"
DEMO_ROOT = DATA_ROOT / "demo"


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize a record into the {sender, text, timestamp, label} shape."""
    return {
        "sender": str(record.get("sender", "unknown")),
        "text": str(record.get("text", "")).strip(),
        "timestamp": str(record.get("timestamp", "")).strip(),
        "label": int(record.get("label", 0)),
    }


def load_pan2012_dataset(dataset_root: str | Path | None = None) -> list[dict[str, Any]]:
    """
    Load a PAN-style dataset into normalized message dictionaries.

    Supported input files in the target directory:
    - CSV with columns: sender,text,timestamp,label
    - JSON/JSONL with objects containing those keys
    - TXT files are treated as unlabeled text snippets (label=0)

    Returns:
        list[dict]: normalized records with sender/text/timestamp/label
    """
    root = Path(dataset_root) if dataset_root else PAN2012_ROOT
    if not root.exists():
        raise FileNotFoundError(
            f"PAN dataset directory not found: {root}. Create it under data/pan2012/ or pass dataset_root."
        )

    records: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        if suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    records.append(_normalize_record(row))
        elif suffix in {".json", ".jsonl"}:
            with path.open("r", encoding="utf-8") as handle:
                if suffix == ".jsonl":
                    for line in handle:
                        line = line.strip()
                        if line:
                            records.append(_normalize_record(json.loads(line)))
                else:
                    payload = json.load(handle)
                    if isinstance(payload, list):
                        for item in payload:
                            records.append(_normalize_record(item))
                    elif isinstance(payload, dict):
                        records.append(_normalize_record(payload))
        elif suffix == ".txt":
            text = path.read_text(encoding="utf-8").strip()
            if text:
                records.append(
                    _normalize_record({
                        "sender": "unknown",
                        "text": text,
                        "timestamp": "",
                        "label": 0,
                    })
                )

    return records


def load_demo_dataset(name: str) -> list[dict[str, Any]]:
    """Load a demo JSON dataset from data/demo."""
    path = DEMO_ROOT / name
    if not path.exists():
        raise FileNotFoundError(f"Demo dataset not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "messages" in payload:
        return payload["messages"]
    if isinstance(payload, list):
        return payload
    raise ValueError(f"Unsupported demo payload format in {path}")
