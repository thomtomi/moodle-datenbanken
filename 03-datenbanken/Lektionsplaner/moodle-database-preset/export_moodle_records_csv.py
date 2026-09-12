#!/usr/bin/env python3
"""Exportiert alte Moodle-Datenbankeintraege als CSV fuer das aktuelle Preset."""

from __future__ import annotations

import argparse
import tarfile
from pathlib import Path
from xml.etree import ElementTree as ET

from convert_mbz_to_current_architecture import map_record, old_record_values
from preset_io import LEGACY_FIELDS, load_link_map, read_fields, write_csv


def mapped_records(source_mbz: Path) -> list[dict[str, str]]:
    with tarfile.open(source_mbz, "r:gz") as archive:
        candidates = [member for member in archive.getmembers()
                      if member.isfile() and Path(member.name).match("activities/data_*/data.xml")]
        if len(candidates) != 1:
            raise ValueError("Das Backup muss genau eine alte Datenbankaktivität enthalten.")
        data = ET.parse(archive.extractfile(candidates[0])).getroot().find("data")
        if data is None:
            raise RuntimeError("Die Datenbankaktivitaet enthaelt kein <data>-Element.")

        fields_element = data.find("fields")
        records_element = data.find("records")
        if fields_element is None or records_element is None:
            raise RuntimeError("Das Backup enthaelt keine lesbaren Felder oder Datensaetze.")

        field_names_by_id = {
            field.get("id") or "": field.findtext("name") or ""
            for field in fields_element.findall("field")
        }
        if set(field_names_by_id.values()) != LEGACY_FIELDS:
            raise ValueError("Das Backup entspricht nicht dem erwarteten alten Schema mit sieben Feldern.")
        return [
            map_record(old_record_values(record, field_names_by_id))
            for record in records_element.findall("record")
        ]


def export_csv(source_mbz: Path, preset_dir: Path, destination_csv: Path,
               link_map: dict[str, str] | None = None) -> tuple[int, int]:
    if source_mbz.resolve() == destination_csv.resolve():
        raise ValueError("Quelle und Ausgabe müssen unterschiedliche Dateien sein.")
    return write_csv(destination_csv, mapped_records(source_mbz), read_fields(preset_dir), link_map)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_mbz", type=Path)
    parser.add_argument("preset_dir", type=Path)
    parser.add_argument("destination_csv", type=Path)
    parser.add_argument("--link-map", type=Path, help="Explizite JSON-Zuordnung für Sicherungslinks")
    args = parser.parse_args()

    records, fields = export_csv(args.source_mbz, args.preset_dir, args.destination_csv, load_link_map(args.link_map))
    print(f"{args.destination_csv}: {records} Datensaetze, {fields} Felder")


if __name__ == "__main__":
    main()
