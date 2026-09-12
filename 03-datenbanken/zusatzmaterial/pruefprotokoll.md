---
title: "Prüfprotokoll Zusatzmaterial"
date: 2026-09-10
---

# Prüfprotokoll Zusatzmaterial

## Prüfgegenstand und Umgebung

Prüfgegenstand sind die Dateien in `preset/`, der lokale Build `build.py` und die daraus erzeugte ZIP-Datei `ausgabe/zusatzmaterial-preset.zip` (SHA-256: `2c72ced4ef71cc2d4a55425418d8bdd9e04da563d493b3a4b109c6da17870071`). Als Quelle dient ausschliesslich `02-rohdaten/Zusatzmaterial-preset-20260910_0841.zip`; die Rohdatei bleibt unverändert. Moodle-Version, Theme, Browser, Dateispeicher und Testrollen sind für den Moodle-Test offen.

## Prüffälle

| Prüffall | Status | Erwartetes Ergebnis |
| --- | --- | --- |
| XML, Felder und Platzhalter | bestanden | `build.py --check` bestätigte sieben Felddefinitionen; ausser sprachlich überarbeiteten Beschreibungen stimmen sie vollständig mit dem Rohpreset überein. Alle Feldplatzhalter sind bekannt, die Eingabevorlage enthält jedes Feld genau einmal. |
| Moderierte Freigabe | bestanden | Der Prüfbefehl bestätigte `approval=1`; das nicht belegte Setting `manageapproved` ist nicht enthalten. |
| Sicherheitscheck | bestanden | Der Prüfbefehl bestätigte ein leeres JavaScript-Template sowie keine Skripte, Inline-Eventhandler und externen CSS-Ressourcen. |
| ZIP-Struktur | bestanden | Der Build erzeugte elf Preset-Dateien in der Archivwurzel; `unzip -t` bestätigte alle CRC-Prüfungen ohne Fehler. Zwei unmittelbar aufeinanderfolgende Builds lieferten denselben SHA-256-Hash. |
| Moodle-Import | nicht_geprueft | In einer leeren Testaktivität werden Felder, Vorlagen und Einstellung zur Freigabe wie erwartet übernommen. |
| Rollen und Freigabe | nicht_geprueft | Ein Lernenden-Testkonto reicht einen Beitrag ein; eine Lehrperson gibt ihn frei; ein zweites Lernenden-Testkonto sieht und öffnet ihn erst danach. |
| Datei und Link | nicht_geprueft | Datei- und Linkzugriff, Dateigrösse, zulässige Dateitypen und Virenschutz werden mit den Zielvorgaben geprüft. |
| Mobil und Tastatur | nicht_geprueft | Karten, Erfassungsformular, Suche und sichtbarer Fokus bleiben in der Zielinstanz bedienbar. |

## Lokal ausgeführte Befehle

```bash
python3 -B 03-datenbanken/zusatzmaterial/build.py --check
python3 -B 03-datenbanken/zusatzmaterial/build.py
unzip -t 03-datenbanken/zusatzmaterial/ausgabe/zusatzmaterial-preset.zip
```

## Nächster Schritt

Lokalen Build ausführen, ZIP in eine leere Moodle-Testaktivität importieren und den vollständigen Rollen- und Freigabeablauf mit synthetischen Testdaten prüfen. Ergebnisse mit Moodle-Version, Theme, Browser, Dateispeicher und Rollen ergänzen.
