"""CSV-Prüfung und explizite Linkzuordnung für das aktuelle Moodle-Preset."""

from __future__ import annotations

import csv
import io
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET


BACKUP_TOKEN = re.compile(r"\$@[^$\s]+@\$")
LEGACY_FIELDS = {"Klasse", "Datum", "Unterrichtsverlauf", "Zusatzmaterial", "Bemerkung", "Hausaufgaben", "Lernziele"}


def read_fields(preset_dir: Path) -> list[dict[str, str]]:
    fields = [{child.tag: child.text or "" for child in field}
              for field in ET.parse(preset_dir / "preset.xml").getroot().findall("field")]
    names = [field["name"] for field in fields]
    if not names or len(names) != len(set(names)):
        raise ValueError("Das Preset muss eindeutige Feldnamen enthalten.")
    return fields


def read_csv(path: Path, expected_names: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        names = reader.fieldnames or []
        if len(names) != len(set(names)) or set(names) != expected_names:
            raise ValueError("CSV-Feldnamen passen nicht zum erwarteten Schema (UTF-8, Komma).")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("Die CSV enthält Zeilen mit abweichender Spaltenzahl.")
    return rows


def load_link_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    mapping = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict):
        raise ValueError("Die Linkzuordnung muss ein JSON-Objekt sein.")
    for token, url in mapping.items():
        if (not BACKUP_TOKEN.fullmatch(token) or not isinstance(url, str)
                or urlsplit(url).scheme not in {"http", "https"} or not urlsplit(url).netloc
                or any(char.isspace() for char in url) or '"' in url or "<" in url or "$@" in url):
            raise ValueError("Ungültige Linkzuordnung; erwartet werden Sicherungstoken und absolute HTTP(S)-URL.")
    return mapping


def prepare_rows(rows: list[dict[str, str]], fields: list[dict[str, str]],
                 link_map: dict[str, str] | None = None) -> list[dict[str, str]]:
    names = {field["name"] for field in fields}
    prepared = []
    for number, row in enumerate(rows, 1):
        if set(row) != names:
            raise ValueError(f"Datensatz {number}: Feldnamen passen nicht zum Preset.")
        result = {}
        for field in fields:
            name = field["name"]
            value = BACKUP_TOKEN.sub(lambda match: (link_map or {}).get(match[0], match[0]), row[name])
            if "$@" in value or "@@PLUGINFILE@@" in value:
                raise ValueError(f"Datensatz {number}, Feld {name}: nicht aufgelöster Sicherungs-/Dateiverweis.")
            if field.get("required") == "1" and not value.strip():
                raise ValueError(f"Datensatz {number}, Feld {name}: Pflichtwert fehlt.")
            if value and name.endswith("datum"):
                try:
                    valid = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) and date.fromisoformat(value)
                except ValueError:
                    valid = False
                if not valid:
                    raise ValueError(f"Datensatz {number}, Feld {name}: gültiges ISO-Datum erwartet.")
            if value and field["type"] in {"menu", "multimenu"}:
                options = {option.strip() for option in field.get("param1", "").splitlines()}
                values = value.split("##") if field["type"] == "multimenu" else [value]
                if any(option not in options for option in values):
                    raise ValueError(f"Datensatz {number}, Feld {name}: unbekannter Auswahlwert.")
            result[name] = value
        prepared.append(result)
    return prepared


def csv_bytes(rows: list[dict[str, str]], fields: list[dict[str, str]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=[field["name"] for field in fields])
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def atomic_write(destination: Path, content: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_csv(destination: Path, rows: list[dict[str, str]], fields: list[dict[str, str]],
              link_map: dict[str, str] | None = None) -> tuple[int, int]:
    prepared = prepare_rows(rows, fields, link_map)
    atomic_write(destination, csv_bytes(prepared, fields))
    return len(prepared), len(fields)
