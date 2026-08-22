"""Load curated ticker universe from CSV files."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UniverseRow:
    ticker: str
    region: str
    name: str


def load_universe(universe_dir: Path) -> list[UniverseRow]:
    rows: list[UniverseRow] = []
    seen: set[str] = set()
    for path in sorted(universe_dir.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for raw in reader:
                ticker = (raw.get("ticker") or "").strip()
                if not ticker or ticker in seen:
                    continue
                seen.add(ticker)
                rows.append(
                    UniverseRow(
                        ticker=ticker,
                        region=(raw.get("region") or "UNK").strip(),
                        name=(raw.get("name") or ticker).strip(),
                    )
                )
    return rows
