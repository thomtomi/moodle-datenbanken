#!/usr/bin/env python3
"""Lokale Regressionstests mit Chromium/CDP und synthetischen Moodle-Feldern."""

import base64
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request
import html
import re
import xml.etree.ElementTree as ET

class CDP:
    def __init__(self, address):
        from urllib.parse import urlsplit
        url = urlsplit(address)
        self.sock = socket.create_connection((url.hostname, url.port), timeout=15)
        key = base64.b64encode(os.urandom(16)).decode()
        request = f'GET {url.path} HTTP/1.1\r\nHost: {url.hostname}:{url.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'
        self.sock.sendall(request.encode())
        header = b''
        while not header.endswith(b'\r\n\r\n'):
            header += self.read(1)
        assert header.split(b'\r\n', 1)[0].split()[1] == b'101', header
        self.counter = 0

    def read(self, count):
        value = b''
        while len(value) < count:
            chunk = self.sock.recv(count - len(value))
            if not chunk:
                raise RuntimeError('Browser-Verbindung beendet')
            value += chunk
        return value

    def send(self, data, opcode=1):
        length = len(data)
        header = bytes([0x80 | opcode])
        if length < 126:
            header += bytes([0x80 | length])
        elif length < 65536:
            header += b'\xfe' + struct.pack('!H', length)
        else:
            header += b'\xff' + struct.pack('!Q', length)
        mask = os.urandom(4)
        self.sock.sendall(header + mask + bytes(byte ^ mask[n % 4] for n, byte in enumerate(data)))

    def receive(self):
        combined = b''
        while True:
            a, b = self.read(2)
            length = b & 127
            if length == 126:
                length = struct.unpack('!H', self.read(2))[0]
            elif length == 127:
                length = struct.unpack('!Q', self.read(8))[0]
            mask = self.read(4) if b & 128 else None
            data = self.read(length)
            if mask:
                data = bytes(byte ^ mask[n % 4] for n, byte in enumerate(data))
            if a & 15 == 9:
                self.send(data, 10)
                continue
            if a & 15 == 8:
                raise RuntimeError('WebSocket geschlossen')
            combined += data
            if a & 128:
                return json.loads(combined)

    def call(self, method, params=None):
        self.counter += 1
        wanted = self.counter
        self.send(json.dumps({'id': wanted, 'method': method, 'params': params or {}}).encode())
        while True:
            result = self.receive()
            if result.get('id') == wanted:
                assert 'error' not in result, result
                return result.get('result', {})

    def evaluate(self, expression):
        response = self.call('Runtime.evaluate', {'expression': expression, 'returnByValue': True})
        assert 'exceptionDetails' not in response, response
        return response['result'].get('value')


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'moodle-database-preset' / 'lektionsplaner-db-preset'


def fixture(directory, case, *, date='2026-09-09', filled=False, tiny=False, javascript=True, view='add'):
    fields = ET.parse(SOURCE / 'preset.xml').getroot().findall('field')
    controls = {}
    for number, field in enumerate(fields, 1):
        name, kind = field.findtext('name'), field.findtext('type')
        ident = f'field_{number}'
        label = f'<label class="accesshide" for="{ident}">{name}</label>'
        value = date if name == 'unterrichtsdatum' else ('KW 19' if name == 'kalenderwoche' else '')
        if kind in ('menu', 'multimenu'):
            multiple = kind == 'multimenu'
            options = '' if multiple else '<option value="">Auswählen</option>'
            options += ''.join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>'
                               for v in field.findtext('param1').splitlines())
            hidden = f'<input type="hidden" name="{ident}[xxx]" value="xxx">' if multiple else ''
            control = hidden + label + f'<select id="{ident}" name="{ident}" '+('multiple' if multiple else '')+f'>{options}</select>'
        elif kind == 'textarea':
            if filled and name == 'lektion_4_aktivitaeten':
                value = '<p>Ausgefüllte Aktivität</p>'
            elif name == 'lektion_5_aktivitaeten':
                value = '<p><br data-mce-bogus="1"></p>'
            control = f'<input type="hidden" name="{ident}_itemid" value="12345">'+label
            control += f'<textarea id="{ident}" name="{ident}" data-fieldtype="editor">{html.escape(value)}</textarea>'
            control += f'<select name="{ident}_content1"><option value="1" selected>HTML</option></select>'
        else:
            control = label + f'<input type="text" id="{ident}" name="{ident}" value="{html.escape(value)}">'
        controls[name] = f'<div>{control}</div>'
    template = (SOURCE / (view + 'template.html')).read_text()
    if view != 'add':
        controls = {'klasse': 'Testklasse', 'unterrichtsdatum': '2026-09-09', 'thema': 'Grundlagen',
                    'lektion_1_beginn': '07:40', 'lektion_1_ende': '08:25',
                    'lektion_1_aktivitaeten': '<p>Ergebnisse vergleichen.</p><p>'+'Langtext'*90+'</p>',
                    'lektion_6_aktivitaeten': '<p>Erkenntnisse diskutieren.</p>', 'lernziele': '<p>Beobachtungen begründen.</p>'}
    if view == 'list':
        template = (SOURCE / 'listtemplateheader.html').read_text() + template*3 + (SOURCE / 'listtemplatefooter.html').read_text()
    template = re.sub(r'\[\[([^\]]+)\]\]', lambda match: controls.get(match[1], ''), template)
    template = template.replace('##actionsmenu##', '<button type="button">Aktionen</button>').replace('##moreurl##', '#details')
    setup = 'window.fixtureCase='+json.dumps(case)+';window.errors=[];window.addEventListener("error",e=>errors.push(e.message));'
    if tiny:
        setup += '''window.mockEditor={initialized:false,content:'',calls:[],
          getContent(){return this.content},setContent(value){this.calls.push('setContent');this.content=value},
          save(){this.calls.push('save');document.querySelector('[data-lp-prefill] textarea').value=this.content},
          focus(){},undoManager:{transact(fn){fn()}}};
          window.tinyMCE={get(id){return id===document.querySelector('[data-lp-prefill] textarea').id?window.mockEditor:null}};'''
    base_css = '.accesshide{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}body{margin:8px}'
    script = (SOURCE / 'jstemplate.js').read_text() if javascript else ''
    document = '<!doctype html><html lang="de"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    document += '<style>'+base_css+(SOURCE / 'csstemplate.css').read_text()+'</style><form>'+template+'</form>'
    document += '<script>'+setup+'</script><script>'+script+'</script></html>'
    path = directory / (case+'.html')
    path.write_text(document)
    return path


def main():
    report = {'environment': 'Chromium, synthetischer Moodle-5.1-Feldnachbau; kein Moodle, TinyMCE nur als API-Testdouble', 'cases': []}
    with tempfile.TemporaryDirectory(prefix='lp-browser-') as temporary:
        directory = Path(temporary)
        profile = directory / 'profile'
        with (directory / 'chromium.log').open('w') as log:
            browser = subprocess.Popen(['chromium', '--headless', '--disable-gpu', '--no-first-run',
                '--disable-background-networking', '--disable-component-update', '--remote-debugging-port=0',
                '--user-data-dir='+str(profile), 'about:blank'], stdout=log, stderr=log)
            try:
                portfile = profile / 'DevToolsActivePort'
                deadline = time.monotonic()+15
                while not portfile.exists() and time.monotonic()<deadline:
                    time.sleep(.05)
                if not portfile.exists():
                    raise RuntimeError('Chromium konnte nicht starten; lokale Sockets und Chromium-Installation prüfen.')
                port = portfile.read_text().splitlines()[0]
                with urllib.request.urlopen('http://127.0.0.1:'+port+'/json/list') as response:
                    page = next(item for item in json.load(response) if item['type'] == 'page')
                cdp = CDP(page['webSocketDebuggerUrl'])
                cdp.call('Page.enable')
                report['browser'] = cdp.call('Browser.getVersion')['product']

                def load(case, width=1440, **kwargs):
                    path = fixture(directory, case, **kwargs)
                    cdp.call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
                    cdp.call('Page.navigate', {'url': path.as_uri()})
                    deadline = time.monotonic()+8
                    while time.monotonic()<deadline:
                        ready = cdp.evaluate('window.fixtureCase === '+json.dumps(case)+' && document.readyState === "complete"')
                        if ready:
                            return
                        time.sleep(.05)
                    raise RuntimeError('Testseite wurde nicht geladen: '+case)

                def check(name, expression):
                    passed = cdp.evaluate(expression) is True
                    report['cases'].append({'name': name, 'status': 'bestanden' if passed else 'fehlgeschlagen'})

                for width in [1440, 390, 320]:
                    load('empty-'+str(width), width)
                    check(f'{width}: leere optionale Abschnitte geschlossen', "[...document.querySelectorAll('details[data-open-if-filled]')].every(d=>!d.open)")
                    check(f'{width}: Kalenderwoche', "document.querySelector('[data-lp-week-output]').textContent==='KW 37'")
                    check(f'{width}: Zeitfenster beschriftet', "[...document.querySelectorAll('[data-lp-slot-select]')].every(s=>s.labels.length===1&&!s.disabled)")
                    check(f'{width}: Datum und Lernziele unverändert', "document.querySelector('[data-lp-field=unterrichtsdatum] input').value==='2026-09-09' && document.querySelector('[data-lp-prefill] textarea').value===''")
                    check(f'{width}: kein Seitenüberlauf', "document.documentElement.scrollWidth<=innerWidth")
                    check(f'{width}: keine JavaScript-Fehler', 'window.errors.length===0')
                check('Zeitfenster aktualisiert beide Moodle-Felder', "(()=>{let s=document.querySelector('[data-lp-slot-select]');s.value='07:40|08:25';s.dispatchEvent(new Event('change',{bubbles:true}));return document.querySelector('[data-lp-field=lektion_1_beginn] select').value==='07:40'&&document.querySelector('[data-lp-field=lektion_1_ende] select').value==='08:25'})()")
                check('Themenbutton synchronisiert Mehrfachauswahl', "(()=>{let b=document.querySelector('.lp-topic-chip');b.click();return b.getAttribute('aria-pressed')==='true'&&document.querySelector('[data-lp-topic-picker] select').selectedOptions.length===1})()")
                check('Satzanfang nur auf Klick', "(()=>{document.querySelector('.lp-starter-button').click();return document.querySelector('[data-lp-prefill] textarea').value==='Sie sind in der Lage, '})()")
                check('Vorhandene Lernziele bleiben erhalten', "(()=>{let t=document.querySelector('[data-lp-prefill] textarea');t.value='Vorhandenes Lernziel';document.querySelector('.lp-starter-button').click();return t.value==='Vorhandenes Lernziel'})()")
                cdp.evaluate("document.querySelector('[data-lp-prefill] textarea').value=''")
                time.sleep(1.7)
                check('Bewusst geleerte Lernziele bleiben leer', "document.querySelector('[data-lp-prefill] textarea').value===''")
                load('filled', filled=True)
                check('Nur belegter optionaler Bereich wird geöffnet', "[...document.querySelectorAll('details[data-open-if-filled]')].filter(d=>d.open).map(d=>d.querySelector('summary').textContent).join(',')==='4. Lektion'")
                cdp.evaluate("document.querySelector('details[data-open-if-filled]').open=false")
                time.sleep(1.7)
                check('Manuell geschlossener Bereich bleibt geschlossen', "!document.querySelector('details[data-open-if-filled]').open")
                for value, expected, week in [('09.09.2026','2026-09-09','37'), ('29.02.2024','2024-02-29','9'), ('2021-01-01','2021-01-01','53')]:
                    load('date-'+expected, date=value)
                    check('Datum '+value, "document.querySelector('[data-lp-field=unterrichtsdatum] input').value==="+json.dumps(expected))
                    check('KW für '+value, "document.querySelector('[data-lp-week-output]').textContent==="+json.dumps('KW '+week))
                for number, value in enumerate(['31.02.2026','29.02.2023','morgen']):
                    load('invalid-'+str(number), date=value)
                    check('Unbekanntes Datum erhalten: '+value, "document.querySelector('[data-lp-field=unterrichtsdatum] input').value==="+json.dumps(value))
                    check('Bestehende Woche und Hinweis: '+value, "document.querySelector('[data-lp-field=kalenderwoche] input').value==='KW 19'&&!document.querySelector('[data-lp-field=unterrichtsdatum] .lp-date-help').hidden")
                check('Korrektur eines unbekannten Datums', "(()=>{let d=document.querySelector('[data-lp-field=unterrichtsdatum] input');d.value='9.9.2026';d.dispatchEvent(new Event('change',{bubbles:true}));return d.type==='date'&&d.value==='2026-09-09'&&document.querySelector('[data-lp-week-output]').textContent==='KW 37'})()")
                load('tiny', tiny=True)
                check('Nicht bereiter Editor wird nicht überschrieben', "(()=>{document.querySelector('.lp-starter-button').click();return window.mockEditor.calls.length===0&&document.querySelector('[role=status]').textContent.includes('noch nicht bereit')})()")
                check('Satzanfang über Editor-API synchronisiert', "(()=>{window.mockEditor.initialized=true;document.querySelector('.lp-starter-button').click();return window.mockEditor.calls.join(',')==='setContent,save'&&document.querySelector('[data-lp-prefill] textarea').value==='<p>Sie sind in der Lage, </p>'})()")
                check('Editor-Inhalt hat Vorrang vor leerer Textarea', "(()=>{window.mockEditor.content='<p>Vorhandenes Lernziel</p>';document.querySelector('[data-lp-prefill] textarea').value='';document.querySelector('.lp-starter-button').click();return window.mockEditor.content==='<p>Vorhandenes Lernziel</p>'})()")
                load('no-js', javascript=False)
                check('Ohne JS bleiben native Eingaben erreichbar', "getComputedStyle(document.querySelector('.lp-auto-week-storage')).position!=='absolute'&&[...document.querySelectorAll('[data-lp-slot-select]')].every(s=>s.disabled)&&document.querySelector('[data-lp-topic-picker] select').tabIndex===0")
                for width in [1440,390,320]:
                    for view in ['single','list']:
                        load(view+str(width), width, view=view)
                        check(f'{view}/{width}: langer Inhalt ohne Seitenüberlauf', "document.documentElement.scrollWidth<=innerWidth")
                        if view=='single':
                            check(f'{view}/{width}: leere Lektionen verborgen', "[...document.querySelectorAll('.lp-lesson:not(.lp-hidden) h5')].map(e=>e.textContent).join(',')==='1. Lektion,6. Lektion'")
                        else:
                            check(f'{view}/{width}: drei Karten', "document.querySelectorAll('.lp-list-card').length===3")
                cdp.call('Browser.close')
                cdp.sock.close()
            finally:
                browser.terminate()
                browser.wait(timeout=10)
    output = ROOT / 'pruefung-moodle-5-1' / 'browser-nach-korrektur.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    failed = [case['name'] for case in report['cases'] if case['status']!='bestanden']
    print(f"{len(report['cases'])-len(failed)}/{len(report['cases'])} Browserprüfungen bestanden.")
    if failed:
        raise SystemExit('\n'.join(failed))


if __name__ == '__main__':
    main()

