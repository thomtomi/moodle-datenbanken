#!/usr/bin/env python3
"""Prueft Preset, CSV-Beispiel und generiertes ZIP lokal; kein Moodle-Import."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
PRESET = ROOT / "preset"
ZIP = ROOT / "ausgabe" / "kursredaktions-checkliste-moodle504.zip"
CSV_EXAMPLE = ROOT / "beispiel-export.csv"
INSTRUCTION = ROOT / "instruktion.html"
FILES = (
    "preset.xml", "listtemplate.html", "singletemplate.html", "asearchtemplate.html",
    "addtemplate.html", "rsstemplate.html", "csstemplate.css", "jstemplate.js",
    "listtemplateheader.html", "listtemplatefooter.html", "rsstitletemplate.html",
)
STATUS_OPTIONS = ("Erfuellt", "Korrektur noetig", "Nicht anwendbar", "Nicht geprueft")
FIELDS = (
    ("Kursname", "text", True),
    ("Moodle-Kurslink", "url", True),
    ("Pruefdatum", "text", True),
    ("Klassen und Berechtigungen", "menu", True),
    ("Rollenbezeichnungen", "menu", True),
    ("Willkommensnachricht", "menu", True),
    ("Termine in der Planung", "menu", True),
    ("Externe Links", "menu", True),
    ("Abgabefenster", "menu", True),
    ("Abgabetermine", "menu", True),
    ("Kursstruktur und Kursfuehrung", "menu", True),
    ("Nicht funktionierende externe Links", "textarea", False),
    ("Besondere Hinweise", "textarea", False),
)
SPECIAL_TAGS = {"##moreurl##", "##actionsmenu##"}


def validate_source() -> None:
    missing = [name for name in FILES if not (PRESET / name).is_file()]
    assert not missing, "Fehlende Preset-Dateien: " + ", ".join(missing)

    root = ET.parse(PRESET / "preset.xml").getroot()
    assert root.tag == "preset", "Wurzelelement <preset> erwartet"
    settings = root.find("settings")
    assert settings is not None, "Preset-Einstellungen fehlen"
    assert (settings.findtext("intro") or "").strip() == INSTRUCTION.read_text(encoding="utf-8").strip(), "Instruktion ist nicht eingebettet"
    for key, expected in {"comments": "0", "rssarticles": "0", "approval": "0", "defaultsort": "Pruefdatum", "defaultsortdir": "1"}.items():
        assert settings.findtext(key) == expected, "Ungueltige Einstellung: " + key

    fields = root.findall("field")
    assert [field.findtext("name") for field in fields] == [name for name, _, _ in FIELDS], "Feldreihenfolge stimmt nicht"
    assert [field.findtext("type") for field in fields] == [kind for _, kind, _ in FIELDS], "Feldtypen stimmen nicht"
    assert [field.findtext("required") for field in fields] == ["1" if required else "0" for _, _, required in FIELDS], "Pflichtstatus stimmt nicht"
    for field in fields:
        if field.findtext("type") == "menu":
            assert tuple((field.findtext("param1") or "").splitlines()) == STATUS_OPTIONS, "Statusoptionen stimmen nicht"

    names = {name for name, _, _ in FIELDS}
    for path in PRESET.glob("*.html"):
        content = path.read_text(encoding="utf-8")
        for token in re.findall(r"\[\[([^\]]+)\]\]", content):
            base, *suffix = token.split("#")
            assert base in names, f"{path.name}: unbekannter Platzhalter {token}"
            assert not suffix or (path.name in {"addtemplate.html", "asearchtemplate.html"} and suffix == ["id"]), f"{path.name}: ungueltiger Platzhalter {token}"
        assert set(re.findall(r"##[^#\s]+##", content)) <= SPECIAL_TAGS, f"{path.name}: unbekannter Spezialtag"
    add_template = (PRESET / "addtemplate.html").read_text(encoding="utf-8")
    assert all(add_template.count("[[" + name + "]]" ) == 1 for name, _, _ in FIELDS), "Eingabevorlage muss jedes Feld genau einmal enthalten"
    assert not re.search(r"\bid\s*=", (PRESET / "listtemplate.html").read_text(encoding="utf-8")), "Feste IDs in wiederholter Liste sind nicht erlaubt"

    css = (PRESET / "csstemplate.css").read_text(encoding="utf-8").lower()
    assert "@import" not in css and "url(" not in css, "CSS darf keine externen Ressourcen laden"
    assert all(selector in css for selector in (".kc-db", ".kc-card", ".kc-search")), "Gekapselte CSS-Selektoren fehlen"
    script = (PRESET / "jstemplate.js").read_text(encoding="utf-8").strip()
    assert not script, "Unerwartetes JavaScript"


def validate_outputs() -> None:
    assert ZIP.is_file(), "ZIP fehlt; zuerst build.py ausfuehren"
    with ZipFile(ZIP) as archive:
        assert set(archive.namelist()) == set(FILES) and len(archive.namelist()) == len(FILES), "ZIP-Struktur stimmt nicht"
        assert archive.testzip() is None, "ZIP ist beschaedigt"
        for name in FILES:
            assert archive.read(name) == (PRESET / name).read_bytes(), "ZIP-Inhalt weicht ab: " + name

    with CSV_EXAMPLE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1 and rows[0].keys() == {name for name, _, _ in FIELDS}, "CSV-Kopf oder Datensatz stimmt nicht"
    assert rows[0]["Nicht funktionierende externe Links"].count("\n") == 1, "Mehrzeiliger Linkbefund fehlt"
    edge = {name: "" for name, _, _ in FIELDS}
    edge.update({"Kursname": "Kurs, \"Spezial\"", "Besondere Hinweise": "Zeile 1\nZeile 2 mit Umlaut: fuer", "Pruefdatum": "2026-09-14"})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=[name for name, _, _ in FIELDS])
    writer.writeheader()
    writer.writerow(edge)
    stream.seek(0)
    assert next(csv.DictReader(stream)) == edge, "CSV-Rundlauf verliert Sonderzeichen"


def main() -> None:
    validate_source()
    validate_outputs()
    print("OK: 13 Felder, 11 Preset-Dateien, CSV-Rundlauf und ZIP-Inhalte geprueft.")
    print("ZIP SHA-256:", hashlib.sha256(ZIP.read_bytes()).hexdigest())
    print("Moodle-Import, Rollen und echter Moodle-CSV-Export: NICHT ausgefuehrt.")


if __name__ == "__main__":
    main()
