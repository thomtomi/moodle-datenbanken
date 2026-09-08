---
title: "Moodle-Datenbanken"
date: 2026-09-08
---

# Moodle-Datenbanken

Moodle-Datenbank-Aktivitäten für die Berufsmaturitätsschule: Felddefinitionen, Vorlagen, Presets und Importdateien.

## Regeln für Agents

Die gemeinsamen Regeln und der vollständige Workflow stehen in [00-setup/agent_instruction.md](00-setup/agent_instruction.md). [AGENTS.md](AGENTS.md) und [.github/copilot-instructions.md](.github/copilot-instructions.md) verweisen für Codex und GitHub Copilot auf diese zentrale Datei.

Die [Beispieldatei](00-setup/agent_instruction_example.md) dient nur als Referenz aus einem anderen Projekt.

Die [Redaktionsvorlage zum Instruktionsdesign](00-setup/instruktionsdesign_template.md) bildet die gemeinsame Grundlage für das Vorgehen der Lernenden. Die Agents wählen je Datenbank die passenden Abschnitte aus und dokumentieren die Auswahl kurz in der Aktivitätsspezifikation.

## Einbindung überprüfen

Das Repository als Projektordner öffnen und in Codex sowie GitHub Copilot jeweils eine neue Sitzung starten. Diesen Auftrag ohne manuelles Anhängen der Regeldatei verwenden:

```text
Prüfen Sie die Projektregeln, ohne Dateien zu ändern.
Nennen Sie die tatsächlich gelesenen Anweisungsdateien mit Pfad.
Erklären Sie, welche Moodle-Artefakte dieses Projekt bearbeitet,
wo Originale und Ergebnisse liegen, wann eine Rückfrage nötig ist
und welche Nachweise für einen geprüften Moodle-Import erforderlich sind.
Nennen Sie ausserdem noch offene Angaben zur Zielumgebung.
```

Erwartung: Der Agent liest `00-setup/agent_instruction.md`, nennt Datenbank-Aktivitäten, erhält Originale in `02-rohdaten/`, legt Ergebnisse in `03-datenbanken/` ab und unterscheidet lokale Prüfungen von Moodle-Tests. Moodle-Version und Testumgebung dürfen ohne neue Angaben nicht als bekannt erscheinen.

Die Lesezugriffe beziehungsweise die angezeigten Kontextreferenzen mitprüfen; eine passende Antwort allein beweist die automatische Einbindung nicht. Bei Copilot in VS Code lassen sich geladene Anweisungen in der Chat-Diagnose kontrollieren. Falls verlinkte Anweisungen fehlen, insbesondere `chat.includeReferencedInstructions` prüfen oder die zentrale Datei ausdrücklich als Kontext hinzufügen. Siehe [VS Code: Custom Instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions). Für Codex siehe [OpenAI: AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Erste Aktivität beginnen

Thema, Zielgruppe, gewünschte Felder, benötigte Ansichten und die bekannte Moodle-Zielversion nennen. Vorhandene Originalexporte gehören nach `02-rohdaten/`; der Agent erstellt die beauftragten Ergebnisse mit Spezifikation und Prüfprotokoll unter `03-datenbanken/`.

Möglicher Startauftrag mit zu ersetzenden Angaben:

```text
Erstellen Sie eine Moodle-Datenbank-Aktivität zum Thema [Thema]
für [Zielgruppe] mit dem Lernziel [Lernziel].
Benötigte Felder und Ansichten: [Anforderungen].
Zielumgebung: [Moodle-Version, Theme, Testmöglichkeit oder offen].
Quellen: [vorhandene Dateien oder keine].
Lieferumfang: Spezifikation und lokal geprüfte Vorlagen.
Dokumentieren Sie ausstehende Moodle-Tests und die Schritte zum Testimport.
```

Der technische Einbindungstest in beiden Werkzeugen und der erste vollständige Durchlauf mit einer Moodle-Testaktivität stehen beim Einrichtungsstand vom 2026-09-08 noch aus.
