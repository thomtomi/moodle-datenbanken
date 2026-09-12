---
title: "Continue mit Qwen3 Coder 30B"
date: 2026-09-12
---

# Continue mit Qwen3 Coder 30B

Diese Einrichtung ist für VSCodium mit Continue im Agent-Modus und einen lokalen Ollama-Dienst vorbereitet. Die versionierten Regeln unter `.continue/rules/` gelten automatisch, wenn dieses Repository als Arbeitsordner geöffnet ist. Die Modellkonfiguration bleibt maschinenlokal unter `~/.continue/config.yaml`; sie wird deshalb nicht direkt in dieses Repository geschrieben.

## Einrichtung auf der VM

1. Installieren Sie Ollama und die aktuelle Continue-Erweiterung aus Open VSX für VSCodium.
2. Laden Sie das Modell und prüfen Sie seine lokale Verfügbarkeit:

   ```bash
   ollama pull qwen3-coder:30b
   ollama list
   ```

3. Sichern Sie eine vorhandene `~/.continue/config.yaml`. Kopieren Sie danach [continue-config-qwen3-coder-30b.yaml](continue-config-qwen3-coder-30b.yaml) nach `~/.continue/config.yaml` oder übernehmen Sie den Eintrag unter `models` und den Abschnitt `context` in die bestehende Konfiguration.
4. Öffnen Sie dieses Repository in VSCodium, wählen Sie **Qwen3 Coder 30B lokal** und danach den **Plan-Modus** oder **Agent-Modus**. Continue fragt standardmässig vor Werkzeugzugriffen nach einer Bestätigung.
5. Führen Sie einmal im Plan-Modus diesen reinen Leseauftrag aus:

   ```text
   Prüfen Sie die geladenen Projektregeln, ohne Dateien zu ändern.
   Nennen Sie die tatsächlich gelesenen Anweisungsdateien mit Pfad.
   Erklären Sie, welche Moodle-Artefakte dieses Projekt bearbeitet,
   wo Originale und Ergebnisse liegen, wann eine Rückfrage nötig ist
   und welche Nachweise für einen geprüften Moodle-Import erforderlich sind.
   Nennen Sie ausserdem noch offene Angaben zur Zielumgebung.
   ```

   Der Auftrag muss `00-setup/agent_instruction.md` sowie die passenden Dateien aus `.continue/rules/` nennen. Prüfen Sie die geladenen Regeln zusätzlich über das Regel-Symbol in Continue.

## Empfohlene Arbeitsweise

- Verwenden Sie den Plan-Modus für Bestandserfassung, fachliche Abgrenzung und Rückfragen.
- Wechseln Sie erst mit einem klaren Umsetzungsauftrag in den Agent-Modus. Bestätigen Sie Lese-, Änderungs- und Terminalzugriffe einzeln, bis das Verhalten auf der VM erprobt ist.
- Geben Sie immer Zielpfad, gewünschtes Ergebnis und bekannte Moodle-Zielversion an. Fehlt die Moodle-Zielumgebung, soll Qwen eine Annahme als offen dokumentieren, keine Kompatibilität behaupten.
- Nennen Sie für Änderungen an einer Aktivität den lokalen Prüfauftrag, etwa `python3 -B 03-datenbanken/zusatzmaterial/build.py --check`. Bestehende Prüfscripts sind der bevorzugte Nachweis.

## Kontext und Leistung

Die Vorlage begrenzt den Kontext auf 32'768 Token. Das entspricht der von Continue für lokale Qwen3-Coder-Modelle ausgewiesenen Grösse und hält Speicherbedarf sowie Antwortzeit auf einer VM berechenbar. Erhöhen Sie `contextLength` erst nach einem Lasttest mit Ihrer verfügbaren GPU-/RAM-Ausstattung; ein grösserer Kontext benötigt deutlich mehr Arbeitsspeicher und kann Agent-Aufgaben verlangsamen.

`temperature: 0.1` begünstigt reproduzierbare Änderungen und Prüfungen. `keepAlive: 1800` hält das Modell nach einer Anfrage 30 Minuten im Speicher, damit aufeinanderfolgende Agent-Schritte ohne erneutes Laden starten können. Der Timeout von zehn Minuten ist für lokale, längere Tool-Aufgaben vorgesehen.

## Grenzen

Die Continue-Regeln steuern das Modellverhalten, erzwingen aber keine Berechtigungen. Eine Werkzeugbestätigung in Continue ersetzt keine Sicherung produktiver Moodle-Aktivitäten. Ein lokaler Prüfstatus belegt weder einen Moodle-Import noch Rollen, Theme oder Browserdarstellung in der Zielinstanz.
