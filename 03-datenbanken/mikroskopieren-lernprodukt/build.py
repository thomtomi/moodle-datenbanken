#!/usr/bin/env python3
"""Prüft und baut das Preset für Lernprodukte zum Mikroskopieren."""

from __future__ import annotations

import hashlib
import io
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "preset"
RAW_PRESET = ROOT.parents[1] / "02-rohdaten" / "Mikroskopieren Lernprodukt hier hochladen!-preset-20260910_1013.zip"
OUTPUT = ROOT / "ausgabe" / "mikroskopieren-lernprodukt-preset.zip"
FILES = (
    "preset.xml", "listtemplate.html", "singletemplate.html", "asearchtemplate.html",
    "addtemplate.html", "rsstemplate.html", "csstemplate.css", "jstemplate.js",
    "listtemplateheader.html", "listtemplatefooter.html", "rsstitletemplate.html",
)
SPECIAL_TAGS = {"##moreurl##", "##actionsmenu##", "##user##", "##timemodified##"}


def fields_from_xml(content: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(content)
    if root.tag != "preset":
        raise ValueError("preset.xml: Wurzelelement <preset> erwartet.")
    fields = [{child.tag: child.text or "" for child in field} for field in root.findall("field")]
    names = [field.get("name", "") for field in fields]
    if not names or "" in names or len(names) != len(set(names)):
        raise ValueError("preset.xml: eindeutige, nicht leere Feldnamen erwartet.")
    return fields


def verify() -> dict[str, object]:
    missing = [name for name in FILES if not (SOURCE / name).is_file()]
    if missing:
        raise ValueError("Fehlende Preset-Dateien: " + ", ".join(missing))
    contents = {name: (SOURCE / name).read_bytes() for name in FILES}
    fields = fields_from_xml(contents["preset.xml"])
    names = {field["name"] for field in fields}

    root = ET.fromstring(contents["preset.xml"])
    settings_element = root.find("settings")
    if settings_element is None:
        raise ValueError("preset.xml: Einstellungen fehlen.")
    settings = {child.tag: child.text or "" for child in settings_element}
    required_settings = {"approval": "1", "comments": "1", "maxentries": "20", "defaultsort": "Präparat"}
    if any(settings.get(name) != value for name, value in required_settings.items()):
        raise ValueError("Die moderierte Freigabe oder die erwarteten Einstellungen fehlen.")
    if "manageapproved" in settings:
        raise ValueError("Nicht belegtes Preset-Setting manageapproved darf nicht verwendet werden.")

    for name, content in contents.items():
        if name.endswith(".html"):
            text = content.decode("utf-8")
            tokens = re.findall(r"\[\[([^\]]+)\]\]", text)
            unknown = set(tokens) - names
            if unknown:
                raise ValueError(f"{name}: unbekannte Feldplatzhalter: {', '.join(sorted(unknown))}")
            if re.search(r"<script\b|\bon[a-z]+\s*=", text, flags=re.IGNORECASE):
                raise ValueError(f"{name}: ausführbarer HTML-Code ist nicht erlaubt.")
            for tag in re.findall(r"##[^#\s]+##", text):
                if tag not in SPECIAL_TAGS:
                    raise ValueError(f"{name}: nicht freigegebener Moodle-Spezialtag {tag}.")

    add_tokens = re.findall(r"\[\[([^\]]+)\]\]", contents["addtemplate.html"].decode("utf-8"))
    if len(add_tokens) != len(names) or set(add_tokens) != names:
        raise ValueError("addtemplate.html muss jedes Feld genau einmal enthalten.")
    if contents["jstemplate.js"].strip():
        raise ValueError("jstemplate.js muss leer bleiben; das Preset benötigt kein JavaScript.")
    css = contents["csstemplate.css"].decode("utf-8")
    if "@import" in css.lower() or re.search(r"url\s*\(", css, flags=re.IGNORECASE):
        raise ValueError("csstemplate.css darf keine externen Ressourcen laden.")
    if not all(selector in css for selector in (".ml-db", ".ml-card", ".ml-gallery")):
        raise ValueError("csstemplate.css: erwartete, gekapselte Selektoren fehlen.")

    if not RAW_PRESET.is_file():
        raise ValueError(f"Rohpreset fehlt: {RAW_PRESET}")
    with zipfile.ZipFile(RAW_PRESET) as archive:
        raw_fields = fields_from_xml(archive.read("preset.xml"))
    source_signature = [{key: value for key, value in item.items() if key != "description"} for item in raw_fields]
    current_signature = [{key: value for key, value in item.items() if key != "description"} for item in fields]
    if current_signature != source_signature:
        raise ValueError("Die Felddefinitionen ausser Feldbeschreibungen weichen vom Rohpreset ab.")
    return {"contents": contents, "fields": fields}


def build() -> Path:
    checked = verify()
    archive_bytes = io.BytesIO()
    with zipfile.ZipFile(archive_bytes, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, checked["contents"][name])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(archive_bytes.getvalue())
    return OUTPUT


if __name__ == "__main__":
    if "--check" in sys.argv:
        result = verify()
        print(f"Prüfung bestanden: {len(result['fields'])} Felder, {len(FILES)} Preset-Dateien.")
    else:
        output = build()
        print(f"Preset erstellt: {output.name} ({hashlib.sha256(output.read_bytes()).hexdigest()})")
