---
title: "Lernprodukt Mikroskopieren"
date: 2026-09-10
---

# Lernprodukt Mikroskopieren

Dieses Preset gestaltet die vorhandene Datenbank als moderierte Bildergalerie. Lernende laden ihr mikroskopiertes Präparat hoch, Lehrpersonen prüfen es und die Klasse vergleicht die freigegebenen Aufnahmen. Die aktuelle Lieferung ist [mikroskopieren-lernprodukt-preset.zip](ausgabe/mikroskopieren-lernprodukt-preset.zip).

## Import und Einrichtung

1. Legen Sie eine leere Moodle-Datenbankaktivität an und importieren Sie das ZIP als Preset.
2. Fügen Sie die [Lernendeninstruktion](instruktion.html) in die Aktivitätsbeschreibung ein und stellen Sie die Mikroskopieranleitung bereit.
3. Prüfen Sie die Freigabe-Einstellung und richten Sie Rollen sowie bei Bedarf Zweiergruppen in Moodle ein.
4. Legen Sie zulässige Bildformate, maximale Dateigrösse und den Virenschutz in der Zielinstanz fest.
5. Testen Sie mit synthetischen Konten den Ablauf: Lernende:r lädt hoch, Lehrperson prüft und gibt frei, ein zweites Lernenden-Testkonto sieht die Aufnahme in der Galerie.

## Lokale Prüfung und Build

```bash
python3 -B 03-datenbanken/mikroskopieren-lernprodukt/build.py --check
python3 -B 03-datenbanken/mikroskopieren-lernprodukt/build.py
unzip -t 03-datenbanken/mikroskopieren-lernprodukt/ausgabe/mikroskopieren-lernprodukt-preset.zip
```

Der Build prüft die unveränderte Feldstruktur, Pflichtfelder, Freigabe-Einstellung, alle Platzhalter, vollständige Eingabevorlage sowie das Fehlen von JavaScript, Inline-Eventhandlern und externen CSS-Ressourcen. Er ersetzt keinen Moodle-Import- und Nutzungstest.
