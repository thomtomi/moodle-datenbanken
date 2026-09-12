---
title: "Prüfprotokoll Lernprodukt Mikroskopieren"
date: 2026-09-10
---

# Prüfprotokoll Lernprodukt Mikroskopieren

## Prüfgegenstand und Umgebung

Prüfgegenstand sind die Dateien in `preset/`, der lokale Build `build.py` und die daraus erzeugte ZIP-Datei `ausgabe/mikroskopieren-lernprodukt-preset.zip` (SHA-256: `d0e1660a3f83f194bcd543b47fe5ed3226136554f9df24a2d457de77512bf5c5`). Als Quelle dient ausschliesslich `02-rohdaten/Mikroskopieren Lernprodukt hier hochladen!-preset-20260910_1013.zip`; die Rohdatei bleibt unverändert. Moodle-Version, Theme, Browser, Dateispeicher, Gruppenmodus und Testrollen sind offen.

## Prüffälle

| Prüffall | Status | Erwartetes Ergebnis |
| --- | --- | --- |
| XML, Felder und Platzhalter | bestanden | `build.py --check` bestätigte beide Felddefinitionen; ausser überarbeiteten Beschreibungen stimmen sie vollständig mit dem Rohpreset überein. Alle Feldplatzhalter sind bekannt, die Eingabevorlage enthält jedes Feld genau einmal. |
| Pflichtfelder und Freigabe | bestanden | Der Prüfbefehl bestätigte beide Pflichtfelder sowie `approval=1`, Kommentare, 20 Maximaleinträge und die Standardsortierung nach Präparat. Das nicht belegte Setting `manageapproved` ist nicht enthalten. |
| Sicherheitscheck | bestanden | Der Prüfbefehl bestätigte ein leeres JavaScript-Template sowie keine Skripte, Inline-Eventhandler und externen CSS-Ressourcen. |
| ZIP-Struktur | bestanden | Der Build erzeugte elf Preset-Dateien in der Archivwurzel; `unzip -t` bestätigte alle CRC-Prüfungen ohne Fehler. Zwei unmittelbar aufeinanderfolgende Builds lieferten denselben SHA-256-Hash. |
| Moodle-Import | nicht_geprueft | In einer leeren Testaktivität werden Felder, Vorlagen und Einstellungen wie erwartet übernommen. |
| Rollen, Freigabe und Gruppen | nicht_geprueft | Ein Lernenden-Testkonto lädt ein Bild hoch; eine Lehrperson gibt es frei; ein weiteres Lernenden-Testkonto sieht es erst danach. Bei Zweiergruppen ist die gewünschte Gruppensichtbarkeit zu prüfen. |
| Bild-Upload und Datenschutz | nicht_geprueft | Zulässige Formate, Dateigrösse, Virenschutz, Bildanzeige und Ausschluss personenbezogener Angaben sind zu prüfen. |
| Mobil und Tastatur | nicht_geprueft | Galerie, Formular, Suche und Fokus bleiben in der Zielinstanz bedienbar. |

## Lokal ausgeführte Befehle

```bash
python3 -B 03-datenbanken/mikroskopieren-lernprodukt/build.py --check
python3 -B 03-datenbanken/mikroskopieren-lernprodukt/build.py
unzip -t 03-datenbanken/mikroskopieren-lernprodukt/ausgabe/mikroskopieren-lernprodukt-preset.zip
```

## Nächster Schritt

Lokalen Build ausführen, ZIP in eine leere Moodle-Testaktivität importieren und den vollständigen Upload-, Freigabe- und Galerieablauf mit synthetischen Testdaten prüfen. Ergebnisse mit Moodle-Version, Theme, Browser, Dateispeicher, Gruppenmodus und Rollen ergänzen.
