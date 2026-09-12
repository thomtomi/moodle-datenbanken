#!/usr/bin/env python3
"""Prüft generierte Sitzplan-Vorschauen mit dem vorhandenen Chromium/CDP-Helfer."""
import base64
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
helper = ROOT.parent / 'Lektionsplaner' / 'tests' / 'browser_pruefung.py'
spec = importlib.util.spec_from_file_location('lp_browser_helper', helper)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CDP = module.CDP


def main():
    output = ROOT / 'pruefung'
    output.mkdir(exist_ok=True)
    report = {'environment': 'Lokale synthetische HTML-Vorschauen, kein Moodle und keine echten Datei-Uploads', 'cases': []}
    with tempfile.TemporaryDirectory(prefix='sitzplan-browser-') as temp:
        profile = Path(temp) / 'profile'
        with (Path(temp) / 'browser.log').open('w') as log:
            browser = subprocess.Popen(['chromium', '--headless', '--disable-gpu', '--no-first-run',
                '--disable-background-networking', '--disable-component-update', '--no-default-browser-check',
                '--remote-debugging-port=0', '--user-data-dir=' + str(profile), 'about:blank'], stdout=log, stderr=log)
            try:
                deadline = time.monotonic() + 12
                portfile = profile / 'DevToolsActivePort'
                while not portfile.exists() and browser.poll() is None and time.monotonic() < deadline:
                    time.sleep(.05)
                if not portfile.exists():
                    raise RuntimeError('Chromium konnte nicht starten: ' + (Path(temp) / 'browser.log').read_text()[-2000:])
                port = portfile.read_text().splitlines()[0]
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/json/list') as response:
                    target = next(p for p in json.load(response) if p['type'] == 'page')
                cdp = CDP(target['webSocketDebuggerUrl'])
                cdp.call('Page.enable')
                cdp.call('Emulation.setFocusEmulationEnabled', {'enabled': True})
                report['browser'] = cdp.call('Browser.getVersion')['product']

                def check(name, expression):
                    passed = cdp.evaluate(expression) is True
                    report['cases'].append({'name': name, 'status': 'bestanden' if passed else 'fehlgeschlagen'})

                def load(filename, width):
                    cdp.call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 1100, 'deviceScaleFactor': 1, 'mobile': False})
                    url = (ROOT / filename).as_uri()
                    cdp.call('Page.navigate', {'url': url})
                    deadline = time.monotonic() + 6
                    while time.monotonic() < deadline:
                        if cdp.evaluate('location.href===' + json.dumps(url) + '&&document.readyState==="complete"'):
                            return
                        time.sleep(.05)
                    raise RuntimeError('Vorschau nicht geladen: ' + filename)

                def screenshot(name):
                    response = cdp.call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': True})
                    (output / name).write_bytes(base64.b64decode(response['data']))

                for width in [1200, 390, 320]:
                    for filename in ['vorschau.html', 'vorschau-leer.html', 'vorschau-lang.html']:
                        load(filename, width)
                        case = f'{filename}/{width}'
                        check(case + ': 21 Plätze', 'document.querySelectorAll(".sp-desk").length===21')
                        check(case + ': kein Seitenüberlauf', 'document.documentElement.scrollWidth<=innerWidth')
                        check(case + ': Lehrpersonenperspektive', '''(()=>{
                          const rect=s=>document.querySelector(s).getBoundingClientRect();
                          const front=rect('[data-seat="r1-p1"]'),back=rect('[data-seat="r3-p1"]');
                          const right=rect('[data-seat="r1-p7"]'),pult=rect('.sp-pult'),board=rect('.sp-board'),room=rect('.sp-room');
                          return back.y<front.y&&front.x<right.x&&Math.abs(front.y-right.y)<1&&pult.y>=front.bottom&&board.y>pult.y&&Math.abs((pult.x+pult.width/2)-(room.x+room.width/2))<2;
                        })()''')
                        check(case + ': keine abgeschnittenen Namen', '[...document.querySelectorAll(".sp-name")].every(e=>e.scrollWidth<=e.clientWidth+1&&e.scrollHeight<=e.clientHeight+1)')
                        check(case + ': Fotos geladen', '[...document.images].every(i=>i.complete&&i.naturalWidth>0&&i.alt.length>0)')
                        if 'leer' in filename:
                            check(case + ': kein leerer Bildbereich', '[...document.querySelectorAll(".sp-photo")].every(e=>getComputedStyle(e).display==="none")')
                        if width == 1200 and filename == 'vorschau.html':
                            screenshot('sitzplan-desktop.png')
                        if width == 390 and filename == 'vorschau.html':
                            screenshot('sitzplan-mobil.png')
                        if width == 320:
                            check(case + ': lokaler Scrollbereich', 'document.querySelector(".sp-scroll").scrollWidth>document.querySelector(".sp-scroll").clientWidth')
                    load('vorschau-eingabe.html', width)
                    check(f'Eingabe/{width}: kein Seitenüberlauf', 'document.documentElement.scrollWidth<=innerWidth')
                    check(f'Eingabe/{width}: Felder beschriftet', '[...document.querySelectorAll("input:not([type=hidden])")].every(e=>e.labels.length>0)')
                    check(f'Eingabe/{width}: einziges Pflichtfeld', 'document.querySelectorAll("[required]").length===1')
                    check(f'Eingabe/{width}: 21 Fotofelder vorhanden', 'document.querySelectorAll("input[type=file]").length===21')
                    cdp.evaluate('document.querySelector("details").open=true')
                    check(f'Eingabe/{width}: aufgeklappter Upload erreichbar', 'document.querySelector("input[type=file]").getBoundingClientRect().height>0&&document.documentElement.scrollWidth<=innerWidth')
                    for filename in ['vorschau-liste.html', 'vorschau-suche.html']:
                        load(filename, width)
                        check(f'{filename}/{width}: kein Seitenüberlauf', 'document.documentElement.scrollWidth<=innerWidth')
                load('vorschau.html', 390)
                cdp.evaluate('document.querySelector(".sp-scroll").focus()')
                report['focus_observation'] = cdp.evaluate('({element:document.activeElement.className,focused:document.hasFocus(),style:getComputedStyle(document.activeElement).outlineStyle,width:getComputedStyle(document.activeElement).outlineWidth})')
                check('Scrollbereich: sichtbarer Tastaturfokus', 'getComputedStyle(document.activeElement).outlineStyle==="solid"&&getComputedStyle(document.activeElement).outlineWidth==="3px"')
                for _ in range(4):
                    cdp.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'ArrowRight', 'code': 'ArrowRight', 'windowsVirtualKeyCode': 39})
                    cdp.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'ArrowRight', 'code': 'ArrowRight', 'windowsVirtualKeyCode': 39})
                time.sleep(.3)
                check('Scrollbereich: per Pfeiltaste bedienbar', 'document.querySelector(".sp-scroll").scrollLeft>0')
                load('vorschau-eingabe.html', 390)
                cdp.evaluate('document.querySelector("details").open=false;document.querySelector("summary").focus()')
                cdp.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13, 'text': '\r'})
                cdp.call('Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter', 'code': 'Enter', 'windowsVirtualKeyCode': 13})
                time.sleep(.1)
                check('Fotoabschnitt: per Tastatur geöffnet', 'document.querySelector("details").open')
                load('vorschau.html', 1120)
                cdp.call('Emulation.setEmulatedMedia', {'media': 'print'})
                check('Druck-CSS: Plan passt ohne Scrollen', 'document.querySelector(".sp-scroll").scrollWidth<=document.querySelector(".sp-scroll").clientWidth+1')
                check('Druck-CSS: 21 Plätze bleiben erhalten', 'document.querySelectorAll(".sp-desk").length===21&&getComputedStyle(document.querySelector(".sp-desk")).display!=="none"')
                cdp.call('Browser.close')
                cdp.sock.close()
            finally:
                if browser.poll() is None:
                    browser.terminate()
                    browser.wait(timeout=10)
    (output / 'browser-ergebnisse.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    failed = [case['name'] for case in report['cases'] if case['status'] != 'bestanden']
    print(f'{len(report["cases"])-len(failed)}/{len(report["cases"])} Browserprüfungen bestanden.')
    if failed:
        raise SystemExit('\n'.join(failed))


if __name__ == '__main__':
    main()
