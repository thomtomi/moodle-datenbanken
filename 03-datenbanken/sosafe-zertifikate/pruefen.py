#!/usr/bin/env python3
"""Prüft das SoSafe-Zertifikats-Preset und seine erzeugten Artefakte."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
PRESET = ROOT / "preset"
INSTRUCTION = ROOT / "instruktion.html"
ZIP = ROOT / "ausgabe" / "sosafe-zertifikate-moodle504.zip"
CSV_EXAMPLE = ROOT / "beispiel-export.csv"
FILES = (
    "preset.xml",
    "listtemplate.html",
    "singletemplate.html",
    "asearchtemplate.html",
    "addtemplate.html",
    "rsstemplate.html",
    "csstemplate.css",
    "jstemplate.js",
    "listtemplateheader.html",
    "listtemplatefooter.html",
    "rsstitletemplate.html",
)
CLASSES = (
    "BM1-2427",
    "BM1-2528",
    "BM1-2629",
    "BMLMT-2427",
    "BMLMT-2326",
    "BM2tz-2527",
    "BM2tz-2628",
    "BM2vz-2627",
)
STATUS_OPTIONS = (
    "Alle Zertifikate abgegeben",
    "Nicht alle Zertifikate abgegeben",
)
FIELDS = (
    ("Klasse", "menu", True),
    ("Abgabestatus", "menu", True),
    ("Hinweis zur fehlenden Abgabe", "textarea", False),
)
SPECIAL_TAGS = {
    "##actionsmenu##",
    "##moreurl##",
    "##timemodified##",
    "##user##",
}


def validate_source() -> None:
    missing = [name for name in FILES if not (PRESET / name).is_file()]
    assert not missing, "Fehlende Preset-Dateien: " + ", ".join(missing)

    root = ET.parse(PRESET / "preset.xml").getroot()
    assert root.tag == "preset", "Wurzelelement <preset> erwartet"
    settings = root.find("settings")
    assert settings is not None, "Preset-Einstellungen fehlen"
    assert (settings.findtext("intro") or "").strip() == INSTRUCTION.read_text(encoding="utf-8").strip(), "Instruktion ist nicht eingebettet"
    expected_settings = {
        "comments": "0",
        "requiredentries": "0",
        "requiredentriestoview": "0",
        "maxentries": "0",
        "rssarticles": "0",
        "approval": "0",
        "defaultsortdir": "0",
        "defaultsort": "Klasse",
    }
    for key, expected in expected_settings.items():
        assert settings.findtext(key) == expected, "Ungültige Einstellung: " + key

    fields = root.findall("field")
    assert [field.findtext("name") for field in fields] == [name for name, _, _ in FIELDS], "Feldreihenfolge stimmt nicht"
    assert [field.findtext("type") for field in fields] == [kind for _, kind, _ in FIELDS], "Feldtypen stimmen nicht"
    assert [field.findtext("required") for field in fields] == ["1" if required else "0" for _, _, required in FIELDS], "Pflichtstatus stimmt nicht"
    assert tuple((fields[0].findtext("param1") or "").splitlines()) == CLASSES, "Klassenoptionen stimmen nicht"
    assert tuple((fields[1].findtext("param1") or "").splitlines()) == STATUS_OPTIONS, "Statusoptionen stimmen nicht"

    names = {name for name, _, _ in FIELDS}
    for path in PRESET.glob("*.html"):
        content = path.read_text(encoding="utf-8")
        for token in re.findall(r"\[\[([^\]]+)\]\]", content):
            base, *suffix = token.split("#")
            assert base in names, f"{path.name}: unbekannter Platzhalter {token}"
            assert not suffix or (path.name in {"addtemplate.html", "asearchtemplate.html"} and suffix == ["id"]), f"{path.name}: ungültiger Platzhalter {token}"
        assert set(re.findall(r"##[^#\s]+##", content)) <= SPECIAL_TAGS, f"{path.name}: unbekannter Spezialtag"

    add_template = (PRESET / "addtemplate.html").read_text(encoding="utf-8")
    assert all(add_template.count("[[" + name + "]]" ) == 1 for name, _, _ in FIELDS), "Eingabevorlage muss jedes Feld genau einmal enthalten"
    search_template = (PRESET / "asearchtemplate.html").read_text(encoding="utf-8")
    assert set(re.findall(r"\[\[([^#\]]+)", search_template)) == {"Klasse", "Abgabestatus"}, "Suche muss nach Klasse und Status filtern"
    list_template = (PRESET / "listtemplate.html").read_text(encoding="utf-8")
    assert not re.search(r"\bid\s*=", list_template), "Feste IDs in wiederholter Liste sind nicht erlaubt"
    assert "##user##" in list_template and "##timemodified##" in list_template, "Listenansicht muss Ersteller:in und Änderungszeit anzeigen"
    assert "data-ss-status" in list_template, "Listenansicht braucht einen Statusanker"

    css = (PRESET / "csstemplate.css").read_text(encoding="utf-8").lower()
    assert "@import" not in css and "url(" not in css, "CSS darf keine externen Ressourcen laden"
    assert all(selector in css for selector in (".ss-db", ".ss-list", ".ss-status")), "Gekapselte CSS-Selektoren fehlen"
    script = (PRESET / "jstemplate.js").read_text(encoding="utf-8")
    assert "data-ss-status" in script and "is-complete" in script and "is-pending" in script, "Status-Markierung fehlt"
    assert not re.search(r"innerHTML|outerHTML|document\.write|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage", script), "JavaScript verwendet eine nicht erlaubte API"
    assert "[[" not in script and "##" not in script, "JavaScript darf keine Moodle-Platzhalter verarbeiten"


def validate_outputs() -> None:
    assert ZIP.is_file(), "ZIP fehlt; zuerst build.py ausführen"
    with ZipFile(ZIP) as archive:
        assert set(archive.namelist()) == set(FILES) and len(archive.namelist()) == len(FILES), "ZIP-Struktur stimmt nicht"
        assert archive.testzip() is None, "ZIP ist beschädigt"
        for name in FILES:
            assert archive.read(name) == (PRESET / name).read_bytes(), "ZIP-Inhalt weicht ab: " + name

    with CSV_EXAMPLE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2 and tuple(rows[0]) == tuple(name for name, _, _ in FIELDS), "CSV-Kopf oder Datensatz stimmt nicht"
    assert rows[0]["Abgabestatus"] == STATUS_OPTIONS[0] and rows[0]["Hinweis zur fehlenden Abgabe"] == "", "Vollständiger Beispielstatus stimmt nicht"
    assert rows[1]["Abgabestatus"] == STATUS_OPTIONS[1] and "Nora Beispiel" in rows[1]["Hinweis zur fehlenden Abgabe"], "Unvollständiger Beispielstatus stimmt nicht"

    edge = {name: "" for name, _, _ in FIELDS}
    edge.update({
        "Klasse": "BM1-2427",
        "Abgabestatus": STATUS_OPTIONS[1],
        "Hinweis zur fehlenden Abgabe": "Müller, Nina\nRückmeldung: \"ausstehend\"",
    })
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=[name for name, _, _ in FIELDS])
    writer.writeheader()
    writer.writerow(edge)
    stream.seek(0)
    assert next(csv.DictReader(stream)) == edge, "CSV-Rundlauf verliert Sonderzeichen"


def main() -> None:
    validate_source()
    validate_outputs()
    print("OK: 3 Felder, 8 Klassen, 2 Statuswerte, 11 Preset-Dateien, CSV-Rundlauf und ZIP-Inhalte geprüft.")
    print("ZIP SHA-256:", hashlib.sha256(ZIP.read_bytes()).hexdigest())
    print("Moodle-Import, Rollen und echte Moodle-Nutzung: NICHT ausgeführt.")


if __name__ == "__main__":
    main()
