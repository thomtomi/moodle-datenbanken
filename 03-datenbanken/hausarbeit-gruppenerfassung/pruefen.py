#!/usr/bin/env python3
"""Lokale Konsistenzprüfung; führt keinen Moodle-Import aus."""
import csv
import hashlib
import io
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent
EXPECTED_FIELDS = ['Gruppenname', 'Gruppenmitglieder', 'Thema der Hausarbeit', 'Forschungsfrage']
# Paketvertrag aus Moodle v5.0.0, mod_data/manager::TEMPLATES_LIST.
EXPECTED_FILES = {
    'preset.xml', 'listtemplate.html', 'singletemplate.html', 'asearchtemplate.html',
    'addtemplate.html', 'rsstemplate.html', 'csstemplate.css', 'jstemplate.js',
    'listtemplateheader.html', 'listtemplatefooter.html', 'rsstitletemplate.html',
}


def main():
    archivepath = ROOT / 'hausarbeit-gruppenerfassung-moodle50.zip'
    with ZipFile(archivepath) as archive:
        assert len(archive.namelist()) == len(EXPECTED_FILES), 'Doppelte oder zusätzliche ZIP-Einträge'
        assert set(archive.namelist()) == EXPECTED_FILES, 'Paketstruktur stimmt nicht mit Moodle 5.0 überein'
        assert archive.testzip() is None, 'Beschädigtes ZIP'
        for name in EXPECTED_FILES:
            assert archive.read(name) == (ROOT / 'preset' / name).read_bytes(), 'Veralteter ZIP-Inhalt: ' + name
    print('OK: 11 Paketdateien direkt im ZIP; alle entsprechen den Quelldateien.')

    xml = ET.parse(ROOT / 'preset' / 'preset.xml').getroot()
    assert xml.tag == 'preset'
    assert [field.findtext('name') for field in xml.findall('field')] == EXPECTED_FIELDS
    assert all(field.findtext('type') == 'text' and field.findtext('required') == '1' for field in xml.findall('field'))
    settings = xml.find('settings')
    assert settings.findtext('intro') == (ROOT / 'instruktion.html').read_text(encoding='utf-8')
    for name, value in {'comments': '0', 'requiredentries': '0', 'requiredentriestoview': '0', 'maxentries': '1', 'rssarticles': '0', 'approval': '0', 'defaultsort': 'Gruppenname', 'defaultsortdir': '0'}.items():
        assert settings.findtext(name) == value, name
    assert settings.find('groupmode') is None, 'Gruppenmodus wird nicht durch ein Preset übertragen'
    print('OK: vier Text-Pflichtfelder in Exportreihenfolge, Einstellungen und vollständige Instruktion.')

    for path in (ROOT / 'preset').glob('*.html'):
        content = path.read_text(encoding='utf-8')
        for token in re.findall(r'\[\[(.*?)\]\]', content):
            parts = token.split('#')
            assert parts[0] in EXPECTED_FIELDS, (path.name, token)
            assert len(parts) == 1 or (path.name == 'addtemplate.html' and parts[1:] == ['id']), (path.name, token)
        assert set(re.findall(r'##(.*?)##', content)) <= {'actionsmenu', 'moreurl'}, path.name
    for name in ('addtemplate.html', 'listtemplate.html', 'singletemplate.html', 'asearchtemplate.html'):
        content = (ROOT / 'preset' / name).read_text(encoding='utf-8')
        assert all(content.count('[[' + field + ']]') == 1 for field in EXPECTED_FIELDS), name
    assert not re.search(r'\bid\s*=', (ROOT / 'preset' / 'listtemplate.html').read_text()), 'Feste ID in wiederholter Karte'
    print('OK: vollständige Feldzuordnung, erlaubte Tags und keine festen Karten-IDs.')

    with (ROOT / 'beispiel-export.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == EXPECTED_FIELDS
    assert len(rows) == 4 and all(len(row) == 4 for row in rows)
    assert rows[1][:3] == ['Gruppe 01', 'Meier; Müller', 'Mikroplastik']
    edge = ['Gruppe 01', 'Meier; Müller', 'Wasser, Boden und "Umwelt"', 'Wie wirkt sich X aus?\nWelche Unterschiede zeigen sich?']
    stream = io.StringIO(newline='')
    csv.writer(stream).writerow(edge)
    stream.seek(0)
    assert next(csv.reader(stream)) == edge
    print('OK: vier CSV-Spalten; Umlaute, Semikolon, führende Null, Komma, Anführungszeichen und Zeilenumbruch bleiben erhalten.')
    print('ZIP SHA-256:', hashlib.sha256(archivepath.read_bytes()).hexdigest())
    print('Moodle-Import, Gruppenzugriff und echter Export: NICHT ausgeführt.')


if __name__ == '__main__':
    main()
