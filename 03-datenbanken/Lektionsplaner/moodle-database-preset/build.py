#!/usr/bin/env python3
"""Baut ein reproduzierbares Preset und die korrigierte CSV mit zehn Einträgen."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from preset_io import atomic_write, csv_bytes, load_link_map, prepare_rows, read_csv, read_fields


ROOT = Path(__file__).resolve().parent
TEMPLATE_FILES = (
    "preset.xml", "listtemplate.html", "singletemplate.html", "asearchtemplate.html",
    "addtemplate.html", "rsstemplate.html", "csstemplate.css", "jstemplate.js",
    "listtemplateheader.html", "listtemplatefooter.html", "rsstitletemplate.html",
)


def build(root: Path = ROOT) -> dict:
    source = root / "lektionsplaner-db-preset"
    fields = read_fields(source)
    names = {field["name"] for field in fields}
    contents = {name: (source / name).read_bytes() for name in TEMPLATE_FILES}
    for name, content in contents.items():
        if name.endswith(".html"):
            references = re.findall(r"\[\[([^\]]+)\]\]", content.decode("utf-8"))
            if set(references) - names:
                raise ValueError(f"{name}: unbekannte Feldplatzhalter.")
            if name == "addtemplate.html" and (len(references) != len(names) or set(references) != names):
                raise ValueError("Die Eingabevorlage muss jedes Feld genau einmal enthalten.")
    original = root / "lektionsplaner-daten-import.csv"
    mapping_path = root / "link-zuordnung.json"
    rows = read_csv(original, names)
    prepared = prepare_rows(rows, fields, load_link_map(mapping_path))
    csv_content = csv_bytes(prepared, fields)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, content in contents.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, content)
    outputs = {"lektionsplaner-moodle-5-1.zip": archive.getvalue(),
               "lektionsplaner-daten-moodle-5-1.csv": csv_content}
    manifest = {
        "target": "Moodle 5.1; lokaler Build, Moodle-Import nicht geprüft",
        "source_csv": original.name,
        "source_csv_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
        "link_map_sha256": hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        "fields": len(fields), "records_before": len(rows), "records_after": len(prepared),
        "changed_cells": sum(row[name] != fixed[name] for row, fixed in zip(rows, prepared) for name in names),
        "source_files": {name: hashlib.sha256(content).hexdigest() for name, content in contents.items()},
        "outputs": {name: hashlib.sha256(content).hexdigest() for name, content in outputs.items()},
    }
    for name, content in outputs.items():
        atomic_write(root / "ausgabe" / name, content)
    atomic_write(root / "ausgabe" / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())
    return manifest


if __name__ == "__main__":
    result = build()
    print(f"Ausgabe erstellt: {result['fields']} Felder, {result['records_after']} Datensätze, "
          f"{result['changed_cells']} korrigierte Zellen.")
