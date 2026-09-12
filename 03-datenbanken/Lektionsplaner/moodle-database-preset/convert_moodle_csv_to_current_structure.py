#!/usr/bin/env python3
"""Fuehrt eine alte Moodle-Datenbank-CSV in die aktuelle Lektionsplaner-Struktur ueber."""

from __future__ import annotations

import argparse
from pathlib import Path

from convert_mbz_to_current_architecture import map_record
from preset_io import LEGACY_FIELDS, load_link_map, read_csv, read_fields, write_csv


def convert_csv(source_csv: Path, preset_dir: Path, destination_csv: Path,
                link_map: dict[str, str] | None = None) -> tuple[int, int]:
    if source_csv.resolve() == destination_csv.resolve():
        raise ValueError("Quelle und Ausgabe müssen unterschiedliche Dateien sein.")
    fields = read_fields(preset_dir)
    rows = read_csv(source_csv, LEGACY_FIELDS)
    return write_csv(destination_csv, [map_record(row) for row in rows], fields, link_map)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("preset_dir", type=Path)
    parser.add_argument("destination_csv", type=Path)
    parser.add_argument("--link-map", type=Path, help="Explizite JSON-Zuordnung für Sicherungslinks")
    args = parser.parse_args()

    records, fields = convert_csv(args.source_csv, args.preset_dir, args.destination_csv, load_link_map(args.link_map))
    print(f"{args.destination_csv}: {records} Datensaetze, {fields} Felder")


if __name__ == "__main__":
    main()
