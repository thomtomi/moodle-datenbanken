#!/usr/bin/env python3
"""Baut das Moodle-Preset, ein synthetisches CSV-Beispiel und eine lokale Vorschau."""

from __future__ import annotations

import csv
import html
import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pruefen import FIELDS, FILES, validate_source


ROOT = Path(__file__).resolve().parent
PRESET = ROOT / "preset"
OUTPUT = ROOT / "ausgabe" / "sosafe-zertifikate-moodle504.zip"
CSV_OUTPUT = ROOT / "beispiel-export.csv"
PREVIEW = ROOT / "vorschau.html"
SAMPLES = (
    {
        "Klasse": "BM1-2427",
        "Abgabestatus": "Alle Zertifikate abgegeben",
        "Hinweis zur fehlenden Abgabe": "",
        "__user": "Anna Muster",
        "__modified": "17. September 2026, 09:15",
        "__detail": "vollstaendig",
    },
    {
        "Klasse": "BMLMT-2427",
        "Abgabestatus": "Nicht alle Zertifikate abgegeben",
        "Hinweis zur fehlenden Abgabe": "Nora Beispiel hat ihr Zertifikat noch nicht abgegeben.",
        "__user": "Marco Beispiel",
        "__modified": "17. September 2026, 10:40",
        "__detail": "unvollstaendig",
    },
)


def render(template: str, sample: dict[str, str]) -> str:
    for name, _, _ in FIELDS:
        rendered = html.escape(sample[name]).replace("\n", "<br>")
        template = template.replace("[[" + name + "]]", rendered)
    return (template.replace("##moreurl##", "#" + sample["__detail"])
                    .replace("##actionsmenu##", "")
                    .replace("##user##", html.escape(sample["__user"]))
                    .replace("##timemodified##", html.escape(sample["__modified"])))


def synchronise_instruction() -> None:
    tree = ET.parse(PRESET / "preset.xml")
    intro = tree.find("settings/intro")
    if intro is None:
        raise ValueError("preset.xml: Einstellung intro fehlt.")
    instruction = (ROOT / "instruktion.html").read_text(encoding="utf-8").strip()
    if (intro.text or "").strip() != instruction:
        intro.text = instruction
        ET.indent(tree, space="  ")
        tree.write(PRESET / "preset.xml", encoding="utf-8", xml_declaration=True)


def build_zip() -> None:
    archive_bytes = io.BytesIO()
    with zipfile.ZipFile(archive_bytes, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (PRESET / name).read_bytes())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(archive_bytes.getvalue())


def build_csv() -> None:
    with CSV_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[name for name, _, _ in FIELDS])
        writer.writeheader()
        for sample in SAMPLES:
            writer.writerow({name: sample[name] for name, _, _ in FIELDS})


def build_preview() -> None:
    listing = (PRESET / "listtemplateheader.html").read_text(encoding="utf-8")
    listing += "".join(render((PRESET / "listtemplate.html").read_text(encoding="utf-8"), sample) for sample in SAMPLES)
    listing += (PRESET / "listtemplatefooter.html").read_text(encoding="utf-8")
    details = "".join(
        '<section id="{}">{}</section>'.format(sample["__detail"], render((PRESET / "singletemplate.html").read_text(encoding="utf-8"), sample))
        for sample in SAMPLES
    )
    page = """<!doctype html>
<html lang="de-CH">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SoSafe-Zertifikate - lokale Vorschau</title>
  <style>
    body { background: #eaf1f1; color: #1d3440; margin: 0; }
    .ss-preview { margin: 0 auto; max-width: 78rem; padding: 1.5rem; }
    .ss-preview-note { font-family: system-ui, sans-serif; margin: 0 0 1rem; }
""" + (PRESET / "csstemplate.css").read_text(encoding="utf-8") + """
  </style>
</head>
<body>
  <main class="ss-preview">
    <p class="ss-preview-note">Lokale Vorschau mit ausschliesslich synthetischen Beispieldaten. Kein Moodle-Funktionstest.</p>
    <h1>Klassenübersicht</h1>
""" + listing + """
    <h1>Einzelansichten</h1>
""" + details + """
  </main>
  <script>
""" + (PRESET / "jstemplate.js").read_text(encoding="utf-8") + """
  </script>
</body>
</html>
"""
    PREVIEW.write_text(page, encoding="utf-8")


def main() -> None:
    synchronise_instruction()
    validate_source()
    build_zip()
    build_csv()
    build_preview()
    print("Erzeugt: Preset-ZIP, CSV-Beispiel und lokale Vorschau.")


if __name__ == "__main__":
    main()
