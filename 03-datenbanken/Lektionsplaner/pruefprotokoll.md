---
title: "Lektionsplaner: Prüfung nach den Korrekturen für Moodle 5.1"
date: 2026-09-09
---

# Prüfung nach den Korrekturen für Moodle 5.1

Die dokumentierten Import- und Formularfehler sind für die **aktuelle ZIP-/CSV-Lieferung** behoben. Die lokale Prüfung umfasst 15 bestandene Python-Tests, 54 bestandene Browserprüfungen und einen vollständigen Vergleich der ausgegebenen Daten. Ein tatsächlicher Import und Nutzungstest in Moodle ist weiterhin offen.

Aktuelle Dateien: [Preset-ZIP](moodle-database-preset/ausgabe/lektionsplaner-moodle-5-1.zip), [CSV mit zehn Einträgen](moodle-database-preset/ausgabe/lektionsplaner-daten-moodle-5-1.csv), [Importanleitung](moodle-database-preset/README.md). Die ursprünglichen Archive und CSVs bleiben erhalten und sind als Altbestand gekennzeichnet. Der [erste Prüfbericht](pruefprotokoll-moodle-5-1.md) dokumentiert den Ausgangszustand.

## Änderungen und Ergebnis

| Befund | Umsetzung | Ergebnis |
| --- | --- | --- |
| B1: Sicherungstokens in der vorgesehenen CSV | Vier explizite Linkzuordnungen anhand des vorhandenen Moodle-Exports. Der Build ersetzt nur diese Tokens. Unbekannte Tokens und nicht aufgelöste Dateiverweise blockieren weitere CSV-Ausgaben vor dem Schreiben. | Zehn Einträge vor und nach der Korrektur; genau 21 geänderte Zellen, keine sonstige Wert- oder Reihenfolgeänderung. |
| B2: Abweichende MBZ und ZIPs | Eindeutige aktuelle Lieferung unter `ausgabe/`, aus dem bearbeiteten Quellordner reproduzierbar erzeugt. Die ältere MBZ mit 37 Feldern und die alten ZIPs sind ausdrücklich Altbestand. | Aktuelle ZIP und CSV stimmen in allen 40 Feldern überein. Eine neue MBZ wurde nicht erzeugt; sie kann aus einer später tatsächlich geprüften Moodle-Aktivität gesichert werden. |
| B3: Leere optionale Abschnitte öffnen sich | Hidden-Inputs, Formatfelder und leeres Rich-Text-Markup werden bei der Inhaltsprüfung ausgeschlossen. Automatisches Öffnen erfolgt einmalig. | Leere Bereiche bleiben geschlossen; ein belegter Bereich öffnet sich. Manuelles Schliessen wird nicht rückgängig gemacht. |
| B4: Datumswerte werden geleert | Validierung vor der Typumstellung, Umwandlung eindeutiger Daten mit Punkten, Erhalt unbekannter Werte mit Hinweis. Bei unbekanntem Datum bleibt die gespeicherte Kalenderwoche erhalten und editierbar. | ISO-Datum, Schweizer Datum, Schaltjahr, Jahreswechsel und ungültige/unklare Werte lokal geprüft. |
| B5: Unbeschriftete Zeitfenster | Sechs eindeutige IDs mit verknüpften Labels. Komfortmenüs sind ohne JavaScript deaktiviert; native Moodle-Zeitfelder bleiben nutzbar. | Alle sechs Menüs besitzen einen zugänglichen Namen; gewähltes Zeitfenster synchronisiert Beginn und Ende. |
| Lernziel-Satzstarter | Sichtbarer Hinweis und Einfügen auf Klick. Vorhandene Texte bleiben erhalten; eine TinyMCE-Instanz wird über ihre API bedient. | Keine automatische Änderung beim Öffnen oder nach bewusstem Leeren. Nicht bereiter Editor erhält einen Hinweis. API-Verhalten mit Testdouble geprüft. |
| Suchbeschriftung | «Aktivitäten der 1. Lektion» benennt den tatsächlichen Filterumfang. | Keine irreführende Zusicherung einer Suche über alle sechs Felder. |
| Lokale App und Anleitung | Startbefehl auf vorhandene `server.py` umgestellt. Repository-Wurzel korrigiert; Daten- und Archivpfade liegen standardmässig im Planer und können per CLI gesetzt werden. | Hilfe und bestehende Speicher-, Such-, Export- und Archivtests bestehen. |
| Weitere Konsistenz | Nicht unterstütztes Preset-Setting `manageapproved` entfernt; Themenpicker zugänglich benannt, manuelle Wochenangabe ohne JavaScript sichtbar; Umbruch langer Inhalte ergänzt. | Feldnamen, Typen und fachliche Planungsdaten bleiben erhalten. |

## Umgebung und Nachweise

Geprüft am 2026-09-09 unter Python 3.13 und Chromium 152.0.7977.82. Der Browser verwendet originales Preset-CSS und -JavaScript mit synthetischen Moodle-Feldern. Listen- und Einzelansichten werden aus den tatsächlichen Vorlagen zusammengesetzt. Der Feldnachbau enthält insbesondere versteckte Draft-IDs, Formatfelder und leeres Editor-Markup.

Der Browsernachbau enthält keine Moodle-Installation, keinen echten TinyMCE-Editor, keine echte Dateiverwaltung und keine Moodle-Rollen. Die vereinfachte TinyMCE-API wird als Testdouble bereitgestellt. Die lokale Darstellung bei 320, 390 und 1440 Pixel Breite belegt nur die geprüften Fälle.

| Nachweis | Inhalt |
| --- | --- |
| [manifest.json](moodle-database-preset/ausgabe/manifest.json) | Hashes aller elf Preset-Quelldateien, der Ausgangs-CSV, der Linkzuordnung und der beiden Ausgaben |
| [artefakte-nach-korrektur.json](pruefung-moodle-5-1/artefakte-nach-korrektur.json) | Datenvergleich, vier im Referenzexport belegte Linkziele, unveränderte Originaldateien, Paketvergleich und reproduzierbarer Build |
| [browser-nach-korrektur.json](pruefung-moodle-5-1/browser-nach-korrektur.json) | Status aller 54 Browserprüfungen |
| [test_preset.py](tests/test_preset.py) | Acht Tests für CSV-Rundlauf, Formatprüfung, Linkzuordnung, Schutz bestehender Ausgaben und reproduzierbaren Build |
| [test_server.py](tests/test_server.py) | Sieben vorhandene Tests für die lokale Anwendung |
| [browser_pruefung.py](tests/browser_pruefung.py) | Wiederholbarer Browserlauf mit synthetischen Daten |

SHA-256 der aktuellen ZIP: `6b27e418ad939a7c9d77134b96071b1c990f60235e69f0cef1c7b016f9e27eeb`.

SHA-256 der aktuellen CSV: `97c52328afcf4efbae0a917ac28aad6a0a2650099193bc4074d8a96e31923dfc`.

## Ausgeführte Prüfungen

| Prüffall | Status | Tatsächliches Ergebnis |
| --- | --- | --- |
| Python-Tests | `bestanden` | 15 Tests; CSV-Zeilenumbrüche, Umlaute und Anführungszeichen bleiben erhalten. Fehlerhafte Eingaben überschreiben vorhandene Ausgaben nicht. |
| Browserprüfungen | `bestanden` | 54 Fälle; Abschnitte, Daten, Wochen, Beschriftungen, Themen, Satzstarter, Editor-API-Testdouble, Verhalten ohne JavaScript sowie mobile und lange Inhalte. |
| ZIP-Archiv und Quellenvergleich | `bestanden` | Elf Dateien im Archivwurzelverzeichnis; CRC-Prüfung ohne Fehler; jede Datei bytegenau gleich der aktuellen Quelle. |
| Paket-/CSV-Schema | `bestanden` | 40 konsistente Felder; jede Feldreferenz auflösbar; Eingabevorlage enthält jedes Feld genau einmal. |
| Daten- und Linkvergleich | `bestanden` | Zehn Einträge, 21 gezielte Zelländerungen, alle übrigen Werte gleich; vier Ziel-URLs im Referenzexport belegt. |
| Build wiederholen | `bestanden` | Identische Ausgabe-Hashes und identisches Manifest. |
| Originale erhalten | `bestanden` | Die vier ursprünglichen CSVs, drei ZIPs, zwei MBZs und `data/lektionen.json` sind bytegenau unverändert. |
| Altformat-Konverter mit vorhandenen Quellen | `bestanden` | Original-MBZ mit expliziter Linkzuordnung erzeugt zehn Einträge/40 Spalten; alte CSV erzeugt elf Einträge/40 Spalten. Beide Prüfausgaben nur unter `/tmp`, nicht als weitere Lieferung abgelegt. |
| Startanleitung | `bestanden` | `server.py --help` zeigt Port und die beiden konfigurierbaren Quell-/Archivpfade. |
| Tatsächlicher Import in Moodle 5.1 | `nicht_geprueft` | Keine zugängliche Testinstanz. |
| Tatsächlicher Texteditor, Dateimanager, Speicherung und Rollen in Moodle | `nicht_geprueft` | Benötigt die konkrete Zielinstanz mit geeignetem Testkonto. |
| Erreichbarkeit der Material-, Kurs-, Teams- und Anmeldelinks | `nicht_geprueft` | Die Linkzuordnung ist belegt; Zielzugriff und Zugriffsrechte wurden nicht geprüft. |

Ausgeführte Kernbefehle aus dem Repository-Hauptverzeichnis:

```bash
python3 -B 03-datenbanken/Lektionsplaner/moodle-database-preset/build.py
python3 -B -m unittest discover -s 03-datenbanken/Lektionsplaner/tests -v
python3 -B 03-datenbanken/Lektionsplaner/tests/browser_pruefung.py
python3 -B 03-datenbanken/Lektionsplaner/server.py --help
```

Die HTTP-Tests und Chromium wurden mit Erlaubnis für die nötigen lokalen Sockets ausgeführt. Sie haben keine produktive Moodle-Aktivität verändert.

## Technische Referenzen und noch nötiger Moodle-Test

Dateistruktur und Feldverhalten beziehen sich auf [Moodle v5.1.0: Preset-Verwaltung](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/manager.php), [Textarea-Felder](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/field/textarea/field.class.php) und [CSV-Import](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/local/importer/csv_entries_importer.php). Der Zugriff auf die bereits geladene TinyMCE-Instanz berücksichtigt den [Moodle-TinyMCE-Loader](https://github.com/moodle/moodle/blob/v5.1.0/public/lib/editor/tiny/amd/src/loader.js); Moodle synchronisiert den Editor selbst ebenfalls mit `editor.save()`, siehe [Editor-Integration](https://github.com/moodle/moodle/blob/v5.1.0/public/lib/editor/tiny/amd/src/editor.js).

Vor dem Einsatz die neue ZIP in eine leere Moodle-5.1-Testaktivität importieren, die 40 Felder und übernommenen Einstellungen kontrollieren, einen synthetischen Eintrag vollständig speichern/bearbeiten und danach bei Bedarf die korrigierte CSV einmal einlesen. Datum, tatsächlichen Texteditor, Dateien, Suche/Sortierung sowie Sichtbarkeit und Links mit den vorgesehenen Rollen prüfen. Patchstand, Theme und Ergebnisse ergänzen. Erst dieser Test belegt die Funktion in Ihrer konkreten Moodle-Umgebung.
