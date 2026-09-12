---
title: "Lektionsplaner"
date: 2026-09-09
---

# Lektionsplaner

Der Lektionsplaner umfasst eine lokale Python-Anwendung und ein eigenständiges [Moodle-Datenbank-Preset](moodle-database-preset/README.md). Für Moodle 5.1 verwenden Sie ZIP und CSV im dort beschriebenen Ausgabeordner. Umfang und Nachweise stehen in der [Spezifikation](spezifikation.md) und im [aktuellen Prüfprotokoll](pruefprotokoll.md).

## Lokale Anwendung starten

Aus dem Repository-Hauptverzeichnis mit Python 3.10 oder neuer:

```bash
python3 -B 03-datenbanken/Lektionsplaner/server.py
```

Öffnen Sie anschliessend `http://127.0.0.1:8765` im Browser. Mit `--port 8766` lässt sich ein anderer Port wählen. Die App lauscht auf `127.0.0.1`; zum Beenden im Terminal `Ctrl+C` drücken.

## Arbeitsablauf

1. Klasse und Unterrichtsdatum erfassen.
2. Lektionsblöcke, Aktivitäten, Hausaufgaben und bei Bedarf Leistungsnachweis, Stützkurs sowie Lernziele ergänzen.
3. Bei vorhandenen Wochenplänen über die Suche Aktivitäten übernehmen.
4. Speichern und die Vorschau kontrollieren.
5. Mit **Moodle-HTML kopieren** das HTML-Fragment in die HTML-Ansicht eines geeigneten Moodle-Textbereichs einfügen. Dies ersetzt keinen strukturierten Datensatzimport in die 40 Felder des Presets.
6. Mit **HTML archivieren** eine vollständige HTML-Datei unter `data/archiv/Einzelplanungen/JAHR/` ablegen.

## Daten und Quellverzeichnisse

Alle folgenden Standardpfade liegen im Ordner des Lektionsplaners:

| Pfad | Verwendung |
| --- | --- |
| `data/lektionen.json` | Gespeicherte Planungen |
| `data/wochenplaene/` | Optionale aktuelle Wochen-HTML-Dateien; werden nur gelesen |
| `data/archiv/` | Optionale historische Wochen-HTML-Dateien; neue Einzelplanungen entstehen im Unterordner `Einzelplanungen/` |

Fehlende Quellverzeichnisse sind erlaubt; die Suche findet darin dann keine Altaktivitäten. Eigene HTML-Bestände lassen sich beim Start über `--active-html-dir PFAD` und `--archive-dir PFAD` angeben. Pfade mit Leerzeichen in Anführungszeichen setzen. Die Archivfunktion schreibt auch bei einem selbst gewählten Archivpfad Einzelplanungen im dafür vorgesehenen Unterordner; generierte Einzelplanungen werden nicht als Altaktivitäten eingelesen.

Die App unterstützt in Textfeldern Listen, Absätze, Hervorhebungen, Tabellen und Links. Skripte und unsichere Link-Schemata werden abgelehnt. Sie benötigt keine Verbindung zu einer Moodle-API; die Übertragung bleibt manuell.

## Tests

Aus dem Repository-Hauptverzeichnis:

```bash
python3 -B -m unittest discover -s 03-datenbanken/Lektionsplaner/tests -v
python3 -B 03-datenbanken/Lektionsplaner/tests/browser_pruefung.py
```

Die erste Prüfung nutzt temporäre Daten und lokale Testserver. Die zweite benötigt Chromium und prüft die Preset-Vorlagen mit synthetischen Moodle-Feldern. Ein echter Moodle-Import ist damit nicht geprüft.
