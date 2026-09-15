#!/usr/bin/env python3
"""Erzeugt bis zu 8 × 16 Plätze, Moodle-Vorlagen und synthetische Vorschauen.

Quellen: Moodle v5.1.0 manager::TEMPLATES_LIST und data_field_picture.
Dieses Skript, instruktion.html, sitzplan.js und preset/csstemplate.css sind die Quellen.
Die übrigen Preset-Dateien sowie Vorschauen und Feldliste werden generiert.
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
PRESET = ROOT / 'preset'
FILES = ('preset.xml', 'listtemplate.html', 'singletemplate.html', 'asearchtemplate.html',
         'addtemplate.html', 'rsstemplate.html', 'csstemplate.css', 'jstemplate.js',
         'listtemplateheader.html', 'listtemplatefooter.html', 'rsstitletemplate.html')
ROWS = 8
PLACES = 16


def layout_fields() -> list[tuple[str, str, str, int, int]]:
    return [('Reihen', 'rows', 'Anzahl Reihen', ROWS, 3)] + [
        (f'r{row}_tische', f'row-{row}', f'Tische in Reihe {row}', PLACES, 7)
        for row in range(1, ROWS + 1)
    ]


def token(name: str) -> str:
    return '[[' + name + ']]'


def seat_fields(row: int, place: int) -> tuple[str, str]:
    return f'r{row}_p{place}_name', f'r{row}_p{place}_foto'


def fields() -> list[dict[str, str]]:
    result = [
        dict(type='text', name='Plan', description='Klasse und Bezeichnung des Sitzplans', required='1', param1='0'),
        dict(type='text', name='Raum', description='Zimmerbezeichnung, optional', required='0', param1='0'),
    ]
    for name, key, label, maximum, default in layout_fields():
        result.append(dict(type='menu', name=name, description=f'{label}: 1 bis {maximum}; leer entspricht {default}.',
                           required='0', param1='\n'.join(str(n) for n in range(1, maximum + 1))))
    for row in range(1, ROWS + 1):
        for place in range(1, PLACES + 1):
            name, photo = seat_fields(row, place)
            label = f'Reihe {row}, Platz {place} von links aus Lehrpersonensicht'
            result.append(dict(type='text', name=name, description=f'{label}: Name; leer für unbesetzten Platz.', required='0', param1='0'))
            result.append(dict(type='picture', name=photo, description=f'{label}: optionales Foto. Alternativtext mit Namen ergänzen.', required='0',
                               param1='160', param2='0', param3='2097152', param4='160', param5='0'))
    return result


def header(kind: str, title: str, actions: bool = False) -> str:
    return (f'<header class="sp-header"><div><p class="sp-eyebrow">{kind}</p>'
            f'<h3>{title}</h3><p class="sp-meta">Raum: [[Raum]]</p></div>'
            + ('<div class="sp-actions">##actionsmenu##</div>' if actions else '') + '</header>\n')


def room() -> str:
    # DOM und Darstellung laufen von der Rückwand zur Wandtafel, ohne Spiegelung.
    result = '<div class="sp-scroll" tabindex="0" role="region" aria-label="Sitzplan aus Sicht der Lehrperson, horizontal scrollbar">\n'
    result += '<div class="sp-room"><p class="sp-back">Rückwand · hinten im Zimmer</p>\n'
    for row in range(ROWS, 0, -1):
        result += f'<section class="sp-row" data-sp-row="{row}" aria-label="Reihe {row}"><p class="sp-row-label">Reihe {row}'
        result += (' · nahe am Pult' if row == 1 else '') + '</p><div class="sp-desks">\n'
        for place in range(1, PLACES + 1):
            name, photo = seat_fields(row, place)
            result += (f'<div class="sp-desk" data-seat="r{row}-p{place}" data-sp-place="{place}">'
                       f'<p class="sp-place">R{row} · P{place}</p>'
                       f'<div class="sp-photo">{token(photo)}</div>'
                       f'<p class="sp-name">{token(name)}</p></div>\n')
        result += '</div></section>\n'
    result += ('<div class="sp-front"><p class="sp-viewpoint">↑ Blick der Lehrperson in die Klasse</p>'
               '<div class="sp-pult">Lehrer:innen-Pult</div><div class="sp-board">Wandtafel</div></div>'
               '<div class="sp-caption"><span>links aus Ihrer Sicht</span><span>rechts aus Ihrer Sicht</span></div>'
               '</div></div>\n')
    return result


def control(name: str, label: str, key: str = '') -> str:
    # Moodle liefert im Feldtoken eigene zugängliche Labels; keine Annahme über Feld-IDs.
    attr = f' data-sp-config="{key}"' if key else ''
    return f'<fieldset class="sp-field"{attr}><legend>{label}</legend>{token(name)}</fieldset>'


def layout_readout() -> str:
    return ('<details class="sp-layout-readout"><summary>Raumaufteilung</summary><dl>'
            + ''.join(f'<div><dt>{label} (leer: {default})</dt><dd data-sp-config="{key}">{token(name)}</dd></div>'
                      for name, key, label, maximum, default in layout_fields())
            + '</dl></details>')


def layout_status() -> str:
    # Auch bei blockiertem oder fehlerhaftem JS keine irreführend verkürzte Raumansicht.
    return ('<p class="sp-layout-warning">Raumaufteilung noch nicht angewendet: Alle 128 möglichen Plätze sind aufgeführt. '
            'Für die eingestellte Anordnung muss das Sitzplan-JavaScript geladen sein.</p>'
            '<p class="sp-layout-status" role="status" aria-live="polite"></p>')


def templates() -> dict[str, str]:
    intro = (ROOT / 'instruktion.html').read_text(encoding='utf-8')
    xml = ET.Element('preset')
    ET.SubElement(xml, 'description').text = 'Flexibler Sitzplan: 1 bis 8 Querreihen mit je 1 bis 16 Tischen; pro Platz Name und optionales Foto.'
    settings = ET.SubElement(xml, 'settings')
    for name, value in {'intro': intro, 'comments': '0', 'requiredentries': '0', 'requiredentriestoview': '0',
                        'maxentries': '0', 'rssarticles': '0', 'approval': '0', 'defaultsortdir': '0', 'defaultsort': 'Plan'}.items():
        ET.SubElement(settings, name).text = value
    for values in fields():
        field = ET.SubElement(xml, 'field')
        for name, value in values.items():
            ET.SubElement(field, name).text = value
    ET.indent(xml, space='  ')
    data = {'preset.xml': ET.tostring(xml, encoding='unicode', xml_declaration=True) + '\n'}
    data['singletemplate.html'] = ('<article class="sp-db sp-single">\n' + header('Sitzplan · Lehrpersonensicht', '[[Plan]]', True)
                                   + '<p class="sp-hint">Reihe 1 liegt direkt vor dem Pult. Plätze zählen von links nach rechts. Auf kleinen Bildschirmen seitlich scrollen.</p>\n'
                                   + layout_readout() + layout_status()
                                   + room() + '</article>\n')
    data['listtemplateheader.html'] = '<div class="sp-list">\n'
    data['listtemplatefooter.html'] = '</div>\n'
    data['listtemplate.html'] = ('<article class="sp-db sp-list-entry">\n'
                                  + header('Sitzplan', '<a href="##moreurl##">[[Plan]]</a>', True)
                                  + '<div class="sp-summary"><a class="sp-open" href="##moreurl##">Sitzplan öffnen</a></div></article>\n')
    adding = ('<div class="sp-db sp-add">\n' + header('Planung', 'Sitzplan erstellen oder bearbeiten')
              + '<div class="sp-form-body"><p>Ein Eintrag enthält den ganzen Sitzplan. Nur der Planname ist Pflicht. Leere Namen und Fotos kennzeichnen unbesetzte Plätze.</p>'
              + '<div class="sp-form-meta">' + control('Plan', 'Planname · Pflichtfeld') + control('Raum', 'Raum · optional') + '</div>'
              + '<section class="sp-layout-editor"><h4>Raumaufteilung</h4><p>Wählen Sie 1 bis 8 Reihen und je Reihe 1 bis 16 Tische. Leere Auswahl: 3 Reihen bzw. 7 Tische. Kürzere Reihen beginnen links.</p>'
              + '<div class="sp-form-meta">' + ''.join(control(name, label, key) for name, key, label, maximum, default in layout_fields()) + '</div></section>'
              + '<p class="sp-hint">Beim Verkleinern werden Plätze nur ausgeblendet. Ihre Namen und Fotos bleiben gespeichert und erscheinen beim Vergrössern wieder. Ausblenden ist kein Löschen und kein Zugriffsschutz.</p>'
              + layout_status()
              + '<p class="sp-hint">Reihe 1 ist dem Pult am nächsten; Platz 1 liegt links aus Ihrer Sicht. Name und Foto bei einem Platzwechsel gemeinsam ändern.</p>')
    # Im Formular bearbeitet man ab Reihe 1; Bezeichnungen stimmen mit dem Grundriss überein.
    for row in range(1, ROWS + 1):
        adding += f'<section class="sp-editor-row" data-sp-row="{row}"><h4>Reihe {row}' + (' · nahe am Pult' if row == 1 else '') + '</h4><div class="sp-edit-grid">'
        for place in range(1, PLACES + 1):
            name, photo = seat_fields(row, place)
            adding += (f'<fieldset class="sp-edit-desk" data-sp-place="{place}"><legend>R{row} · P{place}</legend>' + control(name, 'Name')
                       + '<details class="sp-photo-editor"><summary>Foto · optional</summary><div>'
                       + token(photo) + '</div></details></fieldset>\n')
        adding += '</div></section>\n'
    adding += '<p>Nutzen Sie zum Speichern die Moodle-Schaltflächen unter diesem Formular.</p></div></div>\n'
    # Der Kopf der Eingabe darf keinen zweiten Raum-Feldtoken enthalten.
    data['addtemplate.html'] = adding.replace('<p class="sp-meta">Raum: [[Raum]]</p>', '')
    data['asearchtemplate.html'] = ('<div class="sp-db sp-search"><div class="sp-header"><h3>Sitzpläne suchen</h3></div>'
                                   + '<div class="sp-form-body sp-form-meta">' + control('Plan', 'Planname') + control('Raum', 'Raum') + '</div></div>\n')
    data['rsstemplate.html'] = '<p>Sitzplan – nur für berechtigte Lehrpersonen.</p>\n'
    data['rsstitletemplate.html'] = 'Sitzplan\n'
    data['jstemplate.js'] = (ROOT / 'sitzplan.js').read_text(encoding='utf-8')
    data['csstemplate.css'] = (PRESET / 'csstemplate.css').read_text(encoding='utf-8')
    return data


def validate(data: dict[str, str]) -> None:
    assert set(data) == set(FILES)
    names = {field['name'] for field in fields()}
    assert len(names) == 2 + len(layout_fields()) + ROWS * PLACES * 2
    for path, content in data.items():
        if not path.endswith('.html'):
            continue
        assert set(re.findall(r'\[\[([^\]]+)\]\]', content)) <= names, path
        assert set(re.findall(r'##[^#]+##', content)) <= {'##moreurl##', '##actionsmenu##'}, path
        assert not re.search(r'<(?:script|iframe|object|embed)\b|\bon\w+\s*=', content, re.I), path
        assert not re.search(r'\bid\s*=', content), path
        # Keine Feldwerte in Attributen: Bild und Text werden ausschliesslich durch Moodle gerendert.
        assert not re.search(r'<[^>]*\[\[', content), path
    for path in ['addtemplate.html', 'singletemplate.html']:
        refs = re.findall(r'\[\[([^\]]+)\]\]', data[path])
        assert len(refs) == len(names) and set(refs) == names, path
    assert not re.search(r'innerHTML|outerHTML|document\.write|\beval\s*\(|\bfetch\s*\(|XMLHttpRequest|localStorage|sessionStorage', data['jstemplate.js'])
    assert '[[' not in data['jstemplate.js']
    assert not re.search(r'@import|url\s*\(', data['csstemplate.css'], re.I)
    assert ET.fromstring(data['preset.xml']).findtext('settings/intro') == (ROOT / 'instruktion.html').read_text(encoding='utf-8')


def sample_values(case: str = 'normal') -> dict[str, str]:
    values = {field['name']: '' for field in fields()}
    values.update(Plan='Beispielklasse · Sitzplan', Raum='B 204')
    if case != 'legacy':
        values.update({name: str(default) for name, key, label, maximum, default in layout_fields()})
    if case == 'four':
        values.update(Reihen='4', **{f'r{r}_tische': '5' for r in range(1, ROWS + 1)})
    elif case == 'uneven':
        values.update(Reihen='4', r1_tische='6', r2_tische='5', r3_tische='4', r4_tische='3')
    elif case == 'maximum':
        values.update(Reihen='8', **{f'r{r}_tische': str(PLACES) for r in range(1, ROWS + 1)})
    elif case == 'minimum':
        values.update(Reihen='1', r1_tische='1')
    elif case == 'invalid':
        values.update(Reihen='99', r1_tische='2; color:red')
    if case == 'empty':
        return values
    for row in range(1, ROWS + 1):
        for place in range(1, PLACES + 1):
            name, photo = seat_fields(row, place)
            number = (row - 1) * PLACES + place
            if number not in (7, 14, 20, 21):
                values[name] = f'Lernende:r {number:02d}'
                if number % 3 == 1:
                    values[photo] = '<a href="vorschau-foto.svg"><img src="vorschau-foto.svg" width="160" alt="Synthetisches Porträt" class="list_picture"></a>'
    if case == 'long':
        values['r1_p1_name'] = 'SehrlangerNachnameOhneTrennzeichen' * 4
        values['r3_p7_name'] = html.escape('Beispiel <script>alert("Test")</script> & "Name"')
        values['Plan'] = 'Beispielklasse mit einem ausführlich bezeichneten Sitzplan ' * 3
    return values


def replace_tokens(template: str, values: dict[str, str]) -> str:
    return re.sub(r'\[\[([^\]]+)\]\]', lambda m: values[m[1]], template).replace('##moreurl##', 'vorschau.html').replace('##actionsmenu##', '')


def preview_document(body: str, css: str, title: str, javascript: str) -> str:
    return ('<!doctype html><html lang="de-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            + '<title>' + title + '</title><style>'
            + 'body{margin:0;background:#eef2ed;font-family:Arial,sans-serif;}main{max-width:1220px;margin:0 auto;padding:24px 16px;} '
              '.demo-note{font-size:13px;color:#53635c;margin:0 0 20px} .accesshide{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)} '
            + css + '</style></head><body><main><p class="demo-note">Lokale Vorschau · ausschliesslich synthetische Namen und Symbolbilder · keine Speicherung</p>'
            + body + '</main><script>' + javascript + '</script></body></html>\n')


def preview(data: dict[str, str]) -> dict[str, str]:
    output = {}
    for case, filename in [('normal', 'vorschau.html'), ('empty', 'vorschau-leer.html'), ('long', 'vorschau-lang.html'),
                           ('four', 'vorschau-vier-reihen.html'), ('uneven', 'vorschau-ungleich.html'),
                           ('maximum', 'vorschau-maximal.html'), ('minimum', 'vorschau-minimal.html'),
                           ('legacy', 'vorschau-altbestand.html'), ('invalid', 'vorschau-ungueltig.html')]:
        output[filename] = preview_document(replace_tokens(data['singletemplate.html'], sample_values(case)), data['csstemplate.css'], 'Sitzplan – lokale Vorschau', data['jstemplate.js'])
    forms = {}
    for number, field in enumerate(fields(), 1):
        ident = f'field_{number}'
        if field['type'] == 'text':
            forms[field['name']] = (f'<label class="accesshide" for="{ident}">{field["description"]}</label>'
                                   f'<input type="text" id="{ident}" name="{ident}"' + (' required' if field['required'] == '1' else '') + '>')
        elif field['type'] == 'menu':
            forms[field['name']] = (f'<div><label for="{ident}">{field["description"]}</label>'
                                    f'<select id="{ident}" name="{ident}"><option value="">Auswählen …</option>'
                                    + ''.join(f'<option value="{n}">{n}</option>' for n in field['param1'].splitlines()) + '</select></div>')
        else:
            forms[field['name']] = (f'<fieldset><legend>Foto für {field["name"]}</legend><label for="{ident}">Bild auswählen (Vorschau)</label>'
                                   f'<input id="{ident}" type="file" accept="image/png,image/jpeg"><input type="hidden" value="12345">'
                                   f'<label for="{ident}_alttext">Alternativtext</label><input type="text" id="{ident}_alttext"></fieldset>')
    output['vorschau-eingabe.html'] = preview_document('<form>' + replace_tokens(data['addtemplate.html'], forms) + '</form>', data['csstemplate.css'], 'Sitzplan – Eingabevorschau', data['jstemplate.js'])
    output['vorschau-mehrere.html'] = preview_document(''.join(replace_tokens(data['singletemplate.html'], sample_values(case))
                                                             for case in ['four', 'minimum']), data['csstemplate.css'], 'Sitzplan – getrennte Raumaufteilungen', data['jstemplate.js'])
    # Zwei Einträge, um Listenrahmen und wiederholte Komponenten zu prüfen.
    listing = data['listtemplateheader.html'] + ''.join(replace_tokens(data['listtemplate.html'], sample_values(case)) for case in ['normal', 'long']) + data['listtemplatefooter.html']
    output['vorschau-liste.html'] = preview_document(listing, data['csstemplate.css'], 'Sitzplan – Listenansicht', data['jstemplate.js'])
    output['vorschau-suche.html'] = preview_document('<form>' + replace_tokens(data['asearchtemplate.html'], forms) + '</form>', data['csstemplate.css'], 'Sitzplan – Suche', data['jstemplate.js'])
    output['vorschau-foto.svg'] = ('<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">'
                                  '<rect width="160" height="160" rx="12" fill="#e0eee4"/>'
                                  '<circle cx="80" cy="57" r="28" fill="#6e9b8d"/>'
                                  '<path d="M25 150v-15a55 55 0 0 1 110 0v15" fill="#006d68"/></svg>\n')
    return output


def field_document() -> str:
    content = '---\ntitle: "Sitzplan: vollständige Feldliste"\ndate: 2026-09-14\n---\n\n# Feldliste Sitzplan\n\n'
    content += 'Generiert durch `build.py`. Platzbezeichnungen sind aus Sicht der Lehrperson. Beispiele sind synthetisch.\n\n'
    content += '| Feldname | Moodle-Typ | Pflicht | Zweck / Format | Beispiel |\n| --- | --- | --- | --- | --- |\n'
    for field in fields():
        example = ('3' if field['name'] == 'Reihen' else '7') if field['type'] == 'menu' else 'portraet-beispiel.jpg' if field['type'] == 'picture' else ('BMS · September' if field['name'] == 'Plan' else 'B 204' if field['name'] == 'Raum' else 'Lernende:r 01')
        content += f'| `{field["name"]}` | {field["type"]} | {"ja" if field["required"] == "1" else "nein"} | {field["description"]} | {example} |\n'
    return content + '\nFotos: ein Bild je Platz, maximal 2 MiB; Instanzgrenzen können niedriger liegen. Bildbreite und Thumbnailbreite 160 px, proportionale Höhe; CSS passt die Darstellung dem Tisch an.\n'


def build() -> dict:
    data = templates()
    validate(data)
    for name, content in data.items():
        if name != 'csstemplate.css':
            (PRESET / name).write_text(content, encoding='utf-8')
    for name, content in preview(data).items():
        (ROOT / name).write_text(content, encoding='utf-8')
    (ROOT / 'felder.md').write_text(field_document(), encoding='utf-8')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        for name in FILES:
            entry = zipfile.ZipInfo(name, date_time=(2026, 9, 14, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data[name].encode('utf-8'))
    out = ROOT / 'ausgabe'
    out.mkdir(exist_ok=True)
    (out / 'sitzplan-preset.zip').write_bytes(buffer.getvalue())
    manifest = {'reference': 'Moodle v5.1.0; Zielinstanz offen, kein Moodle-Importtest', 'fields': len(fields()), 'seats': ROWS * PLACES,
                'max_rows': ROWS, 'max_places_per_row': PLACES, 'default_rows': 3, 'default_places_per_row': 7,
                'files': {name: hashlib.sha256(content.encode('utf-8')).hexdigest() for name, content in data.items()},
                'zip_sha256': hashlib.sha256(buffer.getvalue()).hexdigest()}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    result = build()
    print(f'Erstellt: {result["seats"]} Plätze, {result["fields"]} Felder, ZIP und Vorschauen. SHA-256: {result["zip_sha256"]}')
