---
title: "Lokales RAG"
date: 2026-09-12
---

# Lokales RAG für Moodle-Datenbanken

Dieses Werkzeug beantwortet technische und projektbezogene Fragen mit nachvollziehbaren Quellen. Es kombiniert ausgewählte Internetdokumente mit nicht-sensiblen Dateien aus dem Repository. Die Antwortgenerierung und die Embeddings laufen lokal über Ollama; externe Quellen werden nur beim Befehl `sync` abgerufen.

Der Index liegt unter `.rag/` und ist nicht versioniert. Er enthält bereinigte Quellentexte, Hashes, URLs und Embeddings. Teilen Sie bei Problemen die Quellenliste und den Fehlerbericht, nicht den erzeugten Index.

## Einrichtung

Aus dem Repository-Hauptverzeichnis auf der VM ausführen:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r 01-kontextwissen/rag/requirements.txt
ollama pull qwen3-embedding:4b
ollama pull qwen3-coder:30b
```

Ollama muss unter `http://127.0.0.1:11434` erreichbar sein. Bei einer abweichenden Adresse verwenden Sie die globale Option `--ollama-url`, zum Beispiel `--ollama-url http://ollama:11434` vor dem jeweiligen Unterbefehl.

`qwen3-embedding:4b` ist für mehrsprachige Text- und Code-Suche vorgesehen. `qwen3-coder:30b` formuliert anschliessend die Antwort. Beide Modelle verbleiben lokal; die Anwendung sendet weder Fragen noch Quellentexte an einen Cloud-Dienst.

## Arbeitsablauf

```bash
.venv/bin/python 01-kontextwissen/rag/rag.py sync
.venv/bin/python 01-kontextwissen/rag/rag.py index
.venv/bin/python 01-kontextwissen/rag/rag.py search "Wie überträgt ein Moodle-Preset Felder und Vorlagen?"
.venv/bin/python 01-kontextwissen/rag/rag.py ask "Welche Prüfungen fehlen vor einem Moodle-Import?"
```

`sync` lädt die aktivierten Internetquellen, bereinigt HTML und erfasst die zugelassenen Projektdateien. `index` erzeugt Embeddings und verwendet bei unveränderten Chunks den vorhandenen Index weiter. `search` zeigt nur Treffer mit Quellen an. `ask` übergibt die besten Treffer an Qwen und verlangt Quellenmarker wie `[S1]` in der Antwort. Mit `ask --show-context` werden die verwendeten Textauszüge zusätzlich angezeigt.

Nach Änderungen an Quellen oder Repository-Dokumentation immer zuerst `sync` und danach `index` ausführen. `status` zeigt die Anzahl der Quellen, Dokumente und Index-Chunks.

## Kuratierte Quellen

Die versionierte [Quellenliste](sources.json) enthält Titel, URLs und Aktivierungsstatus. Standardmässig werden diese offiziellen Seiten automatisch eingelesen:

- Continue: Regeln und lokale Konfiguration
- Ollama: Embedding-API und Qwen3-Embedding-Modell

MoodleDocs-5.1-Seiten zu Datenbankaktivitäten, Vorlagen, Presets, Nutzung und Gruppen sind vorbereitet, aber standardmässig deaktiviert. Der automatische Abruf lieferte beim Einrichten HTTP 403. Dieses Werkzeug umgeht diese Zugriffsbeschränkung nicht. Speichern Sie die jeweilige Seite im Browser und importieren Sie die lokale Kopie mit der ursprünglichen URL:

```bash
.venv/bin/python 01-kontextwissen/rag/rag.py import ~/Downloads/Database_templates.html \
  --id moodledocs-database-templates-501 \
  --title "MoodleDocs 5.1: Database templates" \
  --source-url https://docs.moodle.org/501/en/Database_templates
.venv/bin/python 01-kontextwissen/rag/rag.py sync
.venv/bin/python 01-kontextwissen/rag/rag.py index
```

Für ausgewählte Moodle-Kerncode-Dateien klonen oder laden Sie nur den tatsächlich benötigten Branch und Pfad lokal und importieren ihn anschliessend. Prüfen Sie Branch, Commit und Pfad vor dem Import; die Zielversion ist in diesem Repository nicht generell festgelegt.

```bash
git clone --depth 1 --branch MOODLE_501_STABLE https://github.com/moodle/moodle.git ~/quellen/moodle-501
.venv/bin/python 01-kontextwissen/rag/rag.py import ~/quellen/moodle-501/mod/data \
  --glob "**/*.php" \
  --id moodle-mod-data-501 \
  --title "Moodle 5.1: mod_data-Quellcode" \
  --source-url https://github.com/moodle/moodle/tree/MOODLE_501_STABLE/mod/data
```

Der Import verarbeitet HTML, Markdown, Text, JSON, XML, CSS, JavaScript, Python und PHP. Geben Sie bei Internetquellen stets `--source-url` an, damit die Antwort auf den Ursprung verweisen kann.

## Datenschutz und Grenzen

Der lokale Scan schliesst `02-rohdaten/`, `data/`, Ergebnisordner, `.rag/` und übliche Abhängigkeitsordner aus. Der manuelle Import verweigert Pfade unter `02-rohdaten/`. Importieren Sie keine Dateien mit personenbezogenen Daten, Zugangsdaten oder nicht freigegebenen Kursinhalten.

Quellentexte gelten beim Beantworten als Daten, nicht als Anweisungen. Antworten sind nur mit den angegebenen Quellen begründet, nicht als Nachweis für einen Moodle-Import, eine Berechtigung oder eine Darstellung im Ziel-Theme. Beachten Sie bei manuell gespeicherten Seiten und Quellcode die jeweiligen Lizenzen; der Index ist ein lokaler Arbeitsbestand und kein Veröffentlichungsformat.

## Lokale Prüfung

```bash
.venv/bin/python -m unittest discover -s 01-kontextwissen/rag/tests -v
.venv/bin/python 01-kontextwissen/rag/rag.py sync
.venv/bin/python 01-kontextwissen/rag/rag.py status
```

Der Testlauf prüft Textextraktion, Chunking, Datenschutz-Ausschlüsse, lexikalische Suche und die Antwortregel. Ein echter Index- und Antworttest benötigt die lokal installierten Ollama-Modelle.