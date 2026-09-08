#!/usr/bin/env python3
"""Erzeugt das Moodle-5.0-Preset und eine lokale Vorschau ohne Abhängigkeiten."""
import csv
import html
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent
PRESET = ROOT / 'preset'
FILES = (
    'preset.xml', 'listtemplate.html', 'singletemplate.html', 'asearchtemplate.html',
    'addtemplate.html', 'rsstemplate.html', 'csstemplate.css', 'jstemplate.js',
    'listtemplateheader.html', 'listtemplatefooter.html', 'rsstitletemplate.html',
)
FIELDS = (
    ('Gruppenname', 'Name der zugeordneten Moodle-Gruppe, zum Beispiel Gruppe 01.'),
    ('Gruppenmitglieder', 'Alle Namen, getrennt durch Semikolon und Leerzeichen, zum Beispiel Meier; Müller.'),
    ('Thema der Hausarbeit', 'Kurzer, aussagekräftiger Titel des gemeinsam gewählten Themas.'),
    ('Forschungsfrage', 'Konkrete, eingegrenzte und gemeinsam abgestimmte Forschungsfrage.'),
)
# Ausschliesslich synthetische Beispiele; keine Moodle-Exporte oder echten Lernendendaten.
SAMPLES = (
    ('Gruppe 01', 'Meier; Müller', 'Mikroplastik',
     'Welchen Einfluss hat Mikroplastik im Boden auf die Keimung von Kresse?'),
    ('Gruppe 02', 'Keller; Huber; Baumann', 'Biodiversität im Siedlungsraum',
     'Wie unterscheidet sich die Pflanzenvielfalt zwischen intensiv gepflegten Rasenflächen und extensiv gepflegten Wiesen?'),
    ('Gruppe 03', 'Frei; Schmid', 'Lebensmittelverschwendung',
     'Welche vermeidbaren Lebensmittelabfälle entstehen während einer Woche in ausgewählten Haushalten?'),
)


def textfile(name):
    return (PRESET / name).read_text(encoding='utf-8')


def render_record(template, values, number):
    for (name, _), value in zip(FIELDS, values):
        template = template.replace('[[' + name + ']]', html.escape(value))
    return template.replace('##moreurl##', '#arbeit-' + str(number)).replace('##actionsmenu##', '')


def build_xml():
    preset = ET.Element('preset')
    ET.SubElement(preset, 'description').text = 'Hausarbeiten: eine Erfassung je Gruppe mit vier Textfeldern und responsiven Karten. Moodle-Gruppenmodus nach dem Import separat konfigurieren.'
    settings = ET.SubElement(preset, 'settings')
    values = {
        'intro': (ROOT / 'instruktion.html').read_text(encoding='utf-8'),
        'comments': '0', 'requiredentries': '0', 'requiredentriestoview': '0',
        'maxentries': '1', 'rssarticles': '0', 'approval': '0',
        'defaultsortdir': '0', 'defaultsort': 'Gruppenname',
    }
    for name, value in values.items():
        ET.SubElement(settings, name).text = value
    for name, description in FIELDS:
        field = ET.SubElement(preset, 'field')
        for key, value in (('type', 'text'), ('name', name), ('description', description), ('required', '1'), ('param1', '0')):
            ET.SubElement(field, key).text = value
    ET.indent(preset, space='  ')
    (PRESET / 'preset.xml').write_bytes(ET.tostring(preset, encoding='utf-8', xml_declaration=True) + b'\n')


def build_zip():
    # Feste Metadaten und explizite Dateiliste ermöglichen reproduzierbare Pakete.
    with ZipFile(ROOT / 'hausarbeit-gruppenerfassung-moodle50.zip', 'w') as archive:
        for name in FILES:
            entry = ZipInfo(name, date_time=(2026, 9, 8, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, (PRESET / name).read_bytes())


def build_preview():
    cards = ''.join(render_record(textfile('listtemplate.html'), values, n) for n, values in enumerate(SAMPLES, 1))
    listing = textfile('listtemplateheader.html') + cards + textfile('listtemplatefooter.html')
    adding = textfile('addtemplate.html')
    for n, ((name, description), value) in enumerate(zip(FIELDS, SAMPLES[0]), 1):
        identifier = 'field_' + str(n)
        adding = adding.replace('[[' + name + '#id]]', identifier)
        # Näherung an data_field_base::display_add_field, keine Moodle-Ausführung.
        control = '<div title="{}"><label for="{}"><span class="accesshide">{}</span><span class="inline-req" aria-hidden="true">*</span></label><input class="basefieldinput form-control d-inline mod-data-input" type="text" name="{}" id="{}" value="{}"></div>'.format(
            html.escape(description, quote=True), identifier, html.escape(name), identifier,
            identifier, html.escape(value, quote=True))
        adding = adding.replace('[[' + name + ']]', control)
    singles = ''.join('<section data-view="arbeit-{}" hidden>{}</section>'.format(
        n, render_record(textfile('singletemplate.html'), values, n)) for n, values in enumerate(SAMPLES, 1))
    document = '''<!doctype html>
<html lang="de-CH"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hausarbeiten – lokale Vorschau</title><style>
body { margin:0; background:#ffffff; color:#16354a; font-family:system-ui,-apple-system,"Segoe UI",sans-serif; }
.preview-shell { max-width:1200px; margin:0 auto; padding:32px 24px 64px; }
.preview-note { font-size:13px; color:#486274; margin:0 0 20px; }
.preview-nav { display:flex; flex-wrap:wrap; gap:12px; margin:0 0 28px; }
.preview-nav a { color:#184c71; padding:10px 16px; border:1px solid #bdd4e5; border-radius:24px; text-decoration:none; font-size:14px; font-weight:600; }
.preview-nav a[aria-current="page"] { background:#184c71; color:white; border-color:#184c71; }
.preview-nav a:focus-visible { outline:3px solid #184c71; outline-offset:3px; }
[hidden] { display:none !important; }
.accesshide { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
.inline-req { color:#8b2f22; font-size:12px; }
.preview-buttons { max-width:52rem; box-sizing:border-box; margin:20px auto; }
.preview-buttons button { background:#184c71; color:white; border:0; border-radius:8px; padding:12px 20px; font:inherit; cursor:pointer; }
.preview-instruction { max-width:52rem; margin:0 auto; line-height:1.7; }
@media(max-width:600px) { .preview-shell { padding:20px 12px 40px; } }
''' + textfile('csstemplate.css') + '''</style></head><body><main class="preview-shell">
<p class="preview-note">Lokale Gestaltungsvorschau · erfundene Beispieldaten · Kartenübersicht der Lehrperson · kein Moodle-Funktionstest</p>
<nav class="preview-nav" aria-label="Vorschauansichten"><a href="#liste">Kartenansicht</a><a href="#erfassung">Erfassung</a><a href="#anleitung">Lernendenanleitung</a></nav>
<section data-view="liste">''' + listing + '''</section>
<section data-view="erfassung" hidden><form id="preview-form">''' + adding + '''<div class="preview-buttons"><button type="submit">Speichern (Vorschau)</button><p id="preview-result" role="status"></p></div></form></section>
<section data-view="anleitung" class="preview-instruction" hidden>''' + (ROOT / 'instruktion.html').read_text(encoding='utf-8') + '''</section>
''' + singles + '''</main><script>''' + textfile('jstemplate.js') + '''</script><script>
(function () {
  function selectView() {
    var view = location.hash.slice(1) || 'liste';
    var panes = Array.from(document.querySelectorAll('[data-view]'));
    if (!panes.some(function (pane) { return pane.dataset.view === view; })) { view = 'liste'; }
    panes.forEach(function (pane) { pane.hidden = pane.dataset.view !== view; });
    document.querySelectorAll('.preview-nav a').forEach(function (link) {
      if (link.hash === '#' + view) { link.setAttribute('aria-current', 'page'); }
      else { link.removeAttribute('aria-current'); }
    });
  }
  window.addEventListener('hashchange', selectView);
  selectView();
  document.getElementById('preview-form').addEventListener('submit', function (event) {
    event.preventDefault();
    document.getElementById('preview-result').textContent = 'Vorschau: Die Eingabe ist vollständig. Es wurden keine Daten gespeichert.';
  });
}());
</script></body></html>
'''
    (ROOT / 'vorschau.html').write_text(document, encoding='utf-8')


def main():
    build_xml()
    build_zip()
    with (ROOT / 'beispiel-export.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow([name for name, _ in FIELDS])
        writer.writerows(SAMPLES)
    build_preview()
    print('Erzeugt: Preset-XML, ZIP mit 11 Dateien, CSV-Beispiel und lokale HTML-Vorschau.')


if __name__ == '__main__':
    main()
