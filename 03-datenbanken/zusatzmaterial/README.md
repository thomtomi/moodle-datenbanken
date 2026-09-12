---
title: "Zusatzmaterial"
date: 2026-09-10
---

# Zusatzmaterial

Dieses Preset gestaltet die vorhandene Datenbank als moderierte Materialbörse: Lernende reichen Zusatzmaterial ein, Lehrpersonen prüfen es vor der gemeinsamen Veröffentlichung. Die aktuelle Lieferung ist [zusatzmaterial-preset.zip](ausgabe/zusatzmaterial-preset.zip).

## Import und Einrichtung

1. Legen Sie eine leere Moodle-Datenbankaktivität an und importieren Sie das ZIP als Preset.
2. Fügen Sie die [Lernendeninstruktion](instruktion.html) in die Aktivitätsbeschreibung ein.
3. Prüfen Sie die Einstellung zur Freigabe und richten Sie die Moodle-Rollen gemäss [Spezifikation](spezifikation.md) ein.
4. Legen Sie zulässige Dateitypen, die maximale Dateigrösse und den Virenschutz in der Zielinstanz fest.
5. Testen Sie mit synthetischen Konten den vollständigen Ablauf: Lernende:r reicht ein, Lehrperson prüft und gibt frei, eine weitere lernende Person findet und öffnet den Beitrag.

## Lokale Prüfung und Build

```bash
python3 -B 03-datenbanken/zusatzmaterial/build.py --check
python3 -B 03-datenbanken/zusatzmaterial/build.py
unzip -t 03-datenbanken/zusatzmaterial/ausgabe/zusatzmaterial-preset.zip
```

Der Build prüft die unveränderte Feldstruktur, die moderierte Freigabe, alle Feldplatzhalter, vollständige Eingabevorlage sowie das Fehlen von JavaScript, Inline-Eventhandlern und externen CSS-Ressourcen. Er ersetzt keinen Moodle-Import- und Rollentest.
