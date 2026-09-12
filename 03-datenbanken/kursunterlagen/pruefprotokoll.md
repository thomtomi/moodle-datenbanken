---
title: "Prüfprotokoll Kursunterlagen"
date: 2026-09-10
---

# Prüfprotokoll Kursunterlagen

## Prüfgegenstand und Umgebung

Prüfgegenstand sind die Dateien in `preset/`, der lokale Build `build.py` und die daraus erzeugte ZIP-Datei `ausgabe/kursunterlagen-preset.zip` (SHA-256: `6c9e5a46c5c1b8996a2b9f8d7015817b36cc02c6ed4ead2003998293120a1865`). Als Quelle dient ausschliesslich `02-rohdaten/Unterlagen zum Kurs-preset-20260910_0753.zip`; die Rohdatei bleibt unverändert. Moodle-Version, Theme und Testrollen sind für den Moodle-Test offen. Die lokale Vorschau lief mit Chromium 152.0.7977.82 und ausschliesslich synthetischen Werten.

## Prüffälle

| Prüffall | Status | Erwartetes Ergebnis |
| --- | --- | --- |
| XML, Felder und Platzhalter | bestanden | `build.py --check` bestätigte sieben Felddefinitionen; ausser sprachlich vereinheitlichten Beschreibungen stimmen sie vollständig mit dem Rohpreset überein. Alle Feldplatzhalter sind bekannt, die Eingabevorlage enthält jedes Feld genau einmal. |
| Sicherheitscheck | bestanden | Der Prüfbefehl bestätigte ein leeres JavaScript-Template sowie keine Skripte, Inline-Eventhandler und externen CSS-Ressourcen. |
| Inklusive Bezeichnungen | bestanden | Eingabe-, Einzel- und Suchansicht sowie die Feldbeschreibung verwenden einheitlich «Herausgeber:in». Der technische Feldname `Verlag` bleibt unverändert. |
| Reduzierte Listenansicht | bestanden | Die Listenkarte enthält `Typ`, `Titel` und den Linkwert ohne feste «Link:»-Beschriftung. Der leere Linkcontainer wird per `:empty` ausgeblendet; `Titel` verwendet zusätzlich den dokumentierten Zieltag `##moreurl##` für die Detailansicht. |
| ZIP-Struktur | bestanden | Der Build erzeugte elf Preset-Dateien in der Archivwurzel; `unzip -t` bestätigte alle CRC-Prüfungen ohne Fehler. Zwei unmittelbar aufeinanderfolgende Builds lieferten denselben SHA-256-Hash. |
| Lokale Mobilvorschau | nicht_geprueft | Die frühere Vorschau bezog sich auf die umfangreichere Listenansicht. Die neue kompakte Listenansicht ist in Moodle beziehungsweise mit einer neuen lokalen Vorschau zu prüfen. |
| Moodle-Import | nicht_geprueft | In einer leeren Testaktivität werden Felder, Vorlagen und Beschreibung wie erwartet übernommen. |
| Lernendensicht und Rollen | nicht_geprueft | Lernende finden und öffnen Unterlagen, können aber keine Einträge erstellen, bearbeiten oder löschen. |
| Theme, Mobil und Tastatur | nicht_geprueft | Karten, Suche, Fokus und Umbrüche bleiben bei kleinen Bildschirmen lesbar und bedienbar. |
| Datei- und Linkzugriff | nicht_geprueft | Datei und Link eines synthetischen Testeintrags sind mit Lernendenrolle erreichbar; unberechtigte Ziele bleiben nicht nur scheinbar verborgen. |

## Lokal ausgeführte Befehle

```bash
python3 -B 03-datenbanken/kursunterlagen/build.py --check
python3 -B 03-datenbanken/kursunterlagen/build.py
unzip -t 03-datenbanken/kursunterlagen/ausgabe/kursunterlagen-preset.zip
python3 -B -m py_compile 03-datenbanken/kursunterlagen/build.py
```

## Nächster Schritt

Nach dem lokalen Build das ZIP in eine leere Moodle-Testaktivität importieren. Die Prüfergebnisse mit Moodle-Version, Theme, Browser und den verwendeten Rollen ergänzen. Erst der erfolgreiche Import und Nutzungstest belegt die Funktion in der Zielumgebung.
