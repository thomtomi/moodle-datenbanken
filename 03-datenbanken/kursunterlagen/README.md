---
title: "Kursunterlagen"
date: 2026-09-10
---

# Kursunterlagen

Dieses Preset gestaltet die vorhandene Datenbankstruktur als übersichtliche, responsive Materialsammlung für Lernende. Die aktuelle Lieferung ist [kursunterlagen-preset.zip](ausgabe/kursunterlagen-preset.zip).

## Import und Einrichtung

1. Legen Sie in Moodle eine leere Datenbankaktivität an und importieren Sie das ZIP als Preset.
2. Fügen Sie die [Lernendeninstruktion](instruktion.html) in die Aktivitätsbeschreibung ein oder prüfen Sie die übernommene Beschreibung.
3. Richten Sie die Rollen gemäss [Spezifikation](spezifikation.md) ein: Lernende dürfen nur lesen und suchen.
4. Erstellen Sie als Lehrperson einen synthetischen Testeintrag mit Datei und/oder Link und prüfen Sie ihn als Lernende:r.
5. Erst danach die tatsächlichen Unterlagen eintragen und ihre Zugriffsrechte kontrollieren.

## Lokale Prüfung und Build

```bash
python3 -B 03-datenbanken/kursunterlagen/build.py --check
python3 -B 03-datenbanken/kursunterlagen/build.py
unzip -t 03-datenbanken/kursunterlagen/ausgabe/kursunterlagen-preset.zip
```

Der Build prüft Feldsignatur, XML, Platzhalter, vollständige Eingabevorlage sowie das Fehlen von JavaScript, Inline-Eventhandlern und externen CSS-Ressourcen. Er ersetzt keinen Moodle-Import- und Rollentest.

Details zu Herkunft, Feldern, Sicherheitsmassnahmen und offenen Prüfungen stehen in der [Spezifikation](spezifikation.md) und im [Prüfprotokoll](pruefprotokoll.md).
