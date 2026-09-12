from __future__ import annotations

import io
import json
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

PRESET = Path(__file__).resolve().parents[1] / "moodle-database-preset"
sys.path.insert(0, str(PRESET))

from build import build, TEMPLATE_FILES
from convert_moodle_csv_to_current_structure import convert_csv
from export_moodle_records_csv import export_csv
from preset_io import LEGACY_FIELDS, load_link_map, prepare_rows, read_csv, read_fields, write_csv


class PresetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.fields = read_fields(PRESET / "lektionsplaner-db-preset")
        self.names = {field["name"] for field in self.fields}
        self.row = {name: "" for name in self.names}
        self.row.update(klasse="BM1-2629", unterrichtsdatum="2026-09-09")

    def test_csv_roundtrip_preserves_rich_text_and_special_characters(self):
        self.row["hausaufgaben"] = '<p>Äpfel; Öl, "Zellen"</p>\n<p>Zweite Zeile</p>'
        self.row["thema"] = "Facheinführung##Grundlagen Biologie: Allgemeine Grundlagen"
        destination = self.root / "roundtrip.csv"
        write_csv(destination, [self.row], self.fields)
        self.assertEqual(read_csv(destination, self.names), [self.row])

    def test_unresolved_links_leave_existing_output_unchanged(self):
        destination = self.root / "output.csv"
        destination.write_text("bisherige Ausgabe")
        for token in ["$@UNKNOWN*7@$", "@@PLUGINFILE@@/bild.png"]:
            self.row["hausaufgaben"] = token
            with self.assertRaisesRegex(ValueError, "nicht aufgelöster"):
                write_csv(destination, [self.row], self.fields)
            self.assertEqual(destination.read_text(), "bisherige Ausgabe")

    def test_explicit_map_changes_only_the_requested_link(self):
        token = "$@COURSEVIEWBYID*42@$"
        self.row["hausaufgaben"] = f'<a href="{token}">Quelle</a>\nUnverändert'
        prepared = prepare_rows([self.row], self.fields, {token: "https://example.invalid/course/view.php?id=42"})
        self.assertEqual(prepared[0]["hausaufgaben"], '<a href="https://example.invalid/course/view.php?id=42">Quelle</a>\nUnverändert')
        self.assertIn(token, self.row["hausaufgaben"])
        self.assertEqual({key: value for key, value in prepared[0].items() if key != "hausaufgaben"},
                         {key: value for key, value in self.row.items() if key != "hausaufgaben"})

    def test_invalid_dates_options_and_required_values_are_rejected(self):
        for name, value in [("unterrichtsdatum", "2026-02-31"), ("unterrichtsdatum", "09.09.2026"),
                            ("klasse", ""), ("klasse", "Unbekannte Klasse"), ("thema", "Unbekannt")]:
            with self.subTest(field=name, value=value), self.assertRaises(ValueError):
                prepare_rows([{**self.row, name: value}], self.fields)

    def test_current_csv_is_rejected_by_legacy_converter(self):
        source = self.root / "current.csv"
        write_csv(source, [self.row], self.fields)
        destination = self.root / "result.csv"
        with self.assertRaisesRegex(ValueError, "Schema"):
            convert_csv(source, PRESET / "lektionsplaner-db-preset", destination)
        self.assertFalse(destination.exists())
        with self.assertRaisesRegex(ValueError, "unterschiedliche"):
            convert_csv(source, PRESET / "lektionsplaner-db-preset", source)
        self.assertEqual(read_csv(source, self.names), [self.row])

    def test_link_map_rejects_script_urls(self):
        path = self.root / "mapping.json"
        path.write_text(json.dumps({"$@COURSEVIEWBYID*42@$": "javascript:alert(1)"}))
        with self.assertRaises(ValueError):
            load_link_map(path)

    def test_mbz_export_requires_resolved_links(self):
        activity = ET.Element("activity")
        data = ET.SubElement(activity, "data")
        fields = ET.SubElement(data, "fields")
        records = ET.SubElement(data, "records")
        record = ET.SubElement(records, "record", id="1")
        contents = ET.SubElement(record, "contents")
        token = "$@COURSEVIEWBYID*42@$"
        values = {"Klasse": "BM1-2629", "Datum": "1788912000", "Hausaufgaben": f'<p><a href="{token}">Auftrag</a></p>'}
        for number, name in enumerate(sorted(LEGACY_FIELDS), 1):
            field = ET.SubElement(fields, "field", id=str(number))
            ET.SubElement(field, "name").text = name
            content = ET.SubElement(contents, "content", id=str(number))
            ET.SubElement(content, "fieldid").text = str(number)
            ET.SubElement(content, "content").text = values.get(name, "")
        xml = ET.tostring(activity)
        source = self.root / "synthetic.mbz"
        with tarfile.open(source, "w:gz") as archive:
            info = tarfile.TarInfo("activities/data_1/data.xml")
            info.size = len(xml)
            archive.addfile(info, io.BytesIO(xml))
        output = self.root / "records.csv"
        with self.assertRaisesRegex(ValueError, "nicht aufgelöster"):
            export_csv(source, PRESET / "lektionsplaner-db-preset", output)
        self.assertFalse(output.exists())
        self.assertEqual(export_csv(source, PRESET / "lektionsplaner-db-preset", output,
                                    {token: "https://example.invalid/course/view.php?id=42"}), (1, 40))
        self.assertNotIn("$@", output.read_text())

    def test_build_is_reproducible_and_preserves_input(self):
        source = self.root / "lektionsplaner-db-preset"
        source.mkdir()
        for name in TEMPLATE_FILES:
            shutil.copyfile(PRESET / "lektionsplaner-db-preset" / name, source / name)
        original = self.root / "lektionsplaner-daten-import.csv"
        write_csv(original, [self.row], self.fields)
        (self.root / "link-zuordnung.json").write_text("{}")
        before = original.read_bytes()
        first = build(self.root)
        second = build(self.root)
        self.assertEqual(first, second)
        self.assertEqual((first["records_before"], first["records_after"], first["fields"]), (1, 1, 40))
        self.assertEqual(original.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
