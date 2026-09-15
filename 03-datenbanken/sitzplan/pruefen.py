#!/usr/bin/env python3
"""Statische Sitzplan-Prüfung; kein Ersatz für Moodle-Funktionstests."""
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import html5lib
import build

ROOT = Path(__file__).resolve().parent


def main():
    data = {name: (ROOT / 'preset' / name).read_text(encoding='utf-8') for name in build.FILES}
    build.validate(data)
    fieldnodes = ET.fromstring(data['preset.xml']).findall('field')
    actual = [{node.tag: node.text or '' for node in field} for field in fieldnodes]
    assert actual == build.fields()
    assert sum(f['required'] == '1' for f in actual) == 1
    assert len(actual) == len(build.fields()) == 2 + len(build.layout_fields()) + build.ROWS * build.PLACES * 2
    assert sum(f['type'] == 'picture' for f in actual) == build.ROWS * build.PLACES
    record = data['singletemplate.html']
    codes = re.findall(r'data-seat="(r\d+-p\d+)"', record)
    assert codes == [f'r{r}-p{p}' for r in range(build.ROWS, 0, -1) for p in range(1, build.PLACES + 1)]
    parser = html5lib.HTMLParser(namespaceHTMLElements=False)
    fragment = parser.parseFragment(record)
    for desk in fragment.iter('div'):
        if desk.get('class') == 'sp-desk':
            row, place = desk.get('data-seat').replace('r', '').replace('p', '').split('-')
            contents = ''.join(desk.itertext())
            assert all(build.token(name) in contents for name in build.seat_fields(int(row), int(place)))
    assert ET.fromstring(data['preset.xml']).findtext('settings/rssarticles') == '0'
    for path in ROOT.glob('vorschau*.html'):
        parser = html5lib.HTMLParser(namespaceHTMLElements=False)
        document = parser.parse(path.read_text(encoding='utf-8'))
        assert not parser.errors, (path.name, parser.errors)
        ids = [e.get('id') for e in document.iter() if e.get('id')]
        assert len(ids) == len(set(ids)), path.name
        assert not re.search(r'\[\[|##(?:more|actions)', path.read_text()), path.name
    css = re.sub(r'/\*.*?\*/', '', data['csstemplate.css'], flags=re.S)
    for selector in re.findall(r'([^{}]+)\{', css):
        if selector.strip().startswith('@media'):
            continue
        assert all(s.strip().startswith('.sp-db') for s in selector.split(',')), selector
    package = ROOT / 'ausgabe' / 'sitzplan-preset.zip'
    with zipfile.ZipFile(package) as archive:
        assert len(archive.namelist()) == len(build.FILES) and set(archive.namelist()) == set(build.FILES)
        assert archive.testzip() is None
        assert all(archive.read(name) == data[name].encode('utf-8') for name in build.FILES)
    manifest = json.loads((ROOT / 'ausgabe' / 'manifest.json').read_text())
    assert manifest['zip_sha256'] == hashlib.sha256(package.read_bytes()).hexdigest()
    for path in [ROOT / 'README.md', ROOT / 'spezifikation.md', ROOT / 'felder.md']:
        text = path.read_text(encoding='utf-8')
        assert text.startswith('---\n') and len(re.findall(r'^# ', text, re.M)) == 1
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if not target.startswith('http'):
                assert (path.parent / target).exists(), (path, target)
    print(f'Bestanden: {len(actual)} Felder, {build.ROWS * build.PLACES} zugeordnete Plätze, Orientierung, HTML, CSS-Geltungsbereich, ZIP und Dokumentlinks.')


if __name__ == '__main__':
    main()
