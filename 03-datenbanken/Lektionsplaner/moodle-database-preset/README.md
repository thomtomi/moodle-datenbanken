---
title: "Lektionsplaner-Preset für Moodle 5.1"
date: 2026-09-09
---

# Lektionsplaner-Preset für Moodle 5.1

Die aktuelle Lieferung liegt in **[ausgabe/](ausgabe/)**. Sie umfasst ein Preset mit 40 Feldern und eine dazu passende CSV mit zehn Einträgen. Die ursprünglichen ZIPs, CSVs und MBZs in diesem Verzeichnis bleiben als Ausgangsdaten erhalten; ihre Einordnung steht unten.

| Datei | Zweck |
| --- | --- |
| [lektionsplaner-moodle-5-1.zip](ausgabe/lektionsplaner-moodle-5-1.zip) | Aktuelle Felder, HTML-Vorlagen, CSS und JavaScript |
| [lektionsplaner-daten-moodle-5-1.csv](ausgabe/lektionsplaner-daten-moodle-5-1.csv) | Korrigierter Import der bisherigen zehn Datensätze |
| [manifest.json](ausgabe/manifest.json) | SHA-256 von Quellen und Ausgaben, Eintragszahlen und korrigierte Zellen |
| [Prüfprotokoll](../pruefprotokoll.md) | Ausgeführte Prüfungen und noch offene Moodle-Tests |

Die Dateien sind lokal gegen das Format von Moodle 5.1.0 und in einem Browsernachbau geprüft. Ein Import- und Nutzungstest in Ihrer konkreten Moodle-5.1-Instanz steht noch aus.

## Import in eine neue Testaktivität

1. Eine leere Aktivität **Datenbank** anlegen und über **Vorlagensätze/Presets** das ZIP aus `ausgabe/` importieren. Neue Felder anlegen lassen.
2. Kontrollieren, dass 40 Felder vorhanden sind. Klasse, Themen und Lektionszeiten müssen Auswahlfelder sein. Die Sortierung erfolgt nach `unterrichtsdatum` absteigend. Übernommene Aktivitätseinstellungen prüfen.
3. Festlegen, wer Planungen sehen und erfassen darf. Das Preset setzt keine vollständige Rollen- oder Gruppenkonfiguration. Die Beschreibung erklärt den Planungszweck; Kommentare, Freigabepflicht und RSS sind im Preset ausgeschaltet.
4. Einen synthetischen Eintrag erfassen, speichern und bearbeiten. Optionale Lektionen, Datum, Themen, Lernziele und einen Dateianhang prüfen. **Satzanfang einfügen** ergänzt ein leeres Lernzielfeld auf Klick; bestehende Inhalte bleiben erhalten.
5. Falls die zehn bisherigen Einträge benötigt werden: **Einträge importieren** öffnen und die CSV aus `ausgabe/` mit **UTF-8** und **Komma** als Trennzeichen importieren. Bei einer angebotenen Einstellung für Textbegrenzung das **doppelte Anführungszeichen** wählen. Die Datei verwendet solche Begrenzungen und echte Zeilenumbrüche innerhalb von Feldwerten.
6. Zehn zusätzliche Einträge und ihre Inhalte kontrollieren. Kurs-, Material-, Teams- und Anmeldelinks sowie Dateien mit den vorgesehenen Rollen öffnen. Ein zweiter CSV-Import legt weitere Datensätze an; er aktualisiert bestehende Einträge nicht.

Bei einer gefüllten Datenbank zuerst eine Sicherung erstellen und die Feldzuordnung in einer Kopie prüfen. Das ältere 37-Feld-Schema der MBZ unterscheidet sich vom aktuellen Preset. Vorlagen nicht ungezielt zurücksetzen.

## Datenformate und Linkherkunft

Die Feldnamen entsprechen exakt der [preset.xml](lektionsplaner-db-preset/preset.xml). Datumswerte werden als `YYYY-MM-DD` gespeichert; das Formular kann bestehende Werte der Form `TT.MM.JJJJ` umwandeln. Nicht erkannte Werte bleiben als Text mit Hinweis erhalten. Themen werden in einer CSV-Zelle mit `##` getrennt. URL-Felder speichern `URL Linktext`. Leere optionale Felder bleiben leer. Ein Dateiname in einer CSV überträgt keine Datei.

Die neue CSV verwendet **denselben Bestand von zehn Einträgen** wie `lektionsplaner-daten-import.csv`. In 21 Zellen wurden ausschliesslich die vier bekannten Sicherungstokens durch belegte Ziel-URLs ersetzt. Es wurden keine Einträge ergänzt, entfernt, zusammengeführt oder aus den Dateien mit 11 bzw. 13 Einträgen übernommen.

Die [Linkzuordnung](link-zuordnung.json) ist durch Linktypen und IDs sowie die vollständigen URLs in `Unterrichtsplanung-11_records-20260904_1336.csv` belegt. Die Instanzadresse stimmt mit `original_wwwroot` der ursprünglichen MBZ überein. Sie bezieht sich auf die bestehende Strickhof-Instanz; sie ist keine automatische Zuordnung zu anderen Kursen oder Servern. Erreichbarkeit und Berechtigungen der Ziele müssen in Moodle geprüft werden. Unbekannte Sicherungstokens führen beim Erzeugen einer CSV zu einem Fehler, bevor eine bestehende Ausgabedatei überschrieben wird.

## Reproduzierbar erzeugen und prüfen

Aus dem Repository-Hauptverzeichnis:

```bash
python3 -B 03-datenbanken/Lektionsplaner/moodle-database-preset/build.py
python3 -B -m unittest discover -s 03-datenbanken/Lektionsplaner/tests -v
python3 -B 03-datenbanken/Lektionsplaner/tests/browser_pruefung.py
```

Der Build benötigt Python 3.10 oder neuer und nur die Standardbibliothek. Ursprüngliche CSVs, ZIPs und MBZs werden nicht geändert. Die Browserprüfung benötigt Chromium und lokale Sockets. Sie verwendet synthetische Daten und einen Formularnachbau; TinyMCE wird als vereinfachtes API-Testdouble geprüft. Das ersetzt keinen Moodle-Test.

Für weitere Datenübernahmen stehen `convert_moodle_csv_to_current_structure.py` und `export_moodle_records_csv.py` bereit. Beide erwarten das **alte Schema mit sieben Feldern**, eine separate Ausgabedatei und bei Sicherungstokens eine explizite `--link-map`. Aktuelle CSVs dürfen nicht nochmals durch den Altformat-Konverter laufen. Feldnamen, Pflichtwerte, Daten und Auswahloptionen werden vor dem Schreiben geprüft. CSV-Quellen im Kommaformat verwenden.

## Erhaltener Altbestand

| Dateien ausserhalb von `ausgabe/` | Einordnung |
| --- | --- |
| Die drei ursprünglichen Preset-ZIPs ohne Zusatz, mit `-kompatibel` und mit `-optimiert` | Identischer ursprünglicher Stand mit den im Review gefundenen Formularfehlern. Für den korrigierten Stand das ZIP aus `ausgabe/` verwenden. |
| `lektionsplaner-datenbank-mit-daten.mbz` | Älterer umgebauter Stand mit 37 Feldern und abweichenden Feldtypen; gehört nicht zur aktuellen Lieferung. |
| `sicherung-moodle2-activity-69203-data69203-20260904-1416.mbz` | Original der alten Aktivität mit sieben Feldern und zehn Einträgen. |
| `lektionsplaner-daten-import.csv` | Ursprünglicher 40-Spalten-Import mit Sicherungstokens; Quelle des Builds, nicht die einzuspielende Ausgabe. |
| Die übrigen drei CSVs | Separate Stände mit 11 bzw. 13 Einträgen; unverändert erhalten. Überschneidungen vor einem zusätzlichen Import abgleichen. |
| `convert_mbz_to_current_architecture.py` | Historisches Umbauwerkzeug, auch Quelle der Altformat-Feldzuordnung. Kein Bestandteil des neuen ZIP/CSV-Builds; keine damit erzeugte MBZ als in Moodle getestet ansehen. |

Falls eine aktuelle vollständige MBZ benötigt wird, nach erfolgreichem ZIP-/CSV-Import und den Funktionstests eine neue Sicherung **aus Moodle** erzeugen. Sie enthält dann die tatsächlich verwendeten Felder, Vorlagen und Daten. Das Preset importiert keine Python-API, lokale JSON-Datei oder Archivierungsfunktion der lokalen App.
