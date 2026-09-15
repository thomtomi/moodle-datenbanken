---
title: "Prüfprotokoll Sitzplan"
date: 2026-09-14
---

# Prüfprotokoll Sitzplan

Die lokale Prüfung ist abgeschlossen: Strukturprüfung und **87 Browserprüfungen bestanden**. Geprüft am 2026-09-14 unter Python 3.13.5, html5lib und Chromium 152.0.7977.82. Die Browserprüfung wurde mit Freigabe für lokale Sockets ausgeführt und verwendet synthetische Namen sowie ein neutrales SVG-Symbolbild.

Prüfgegenstand: generiertes Preset und Vorlagen in `preset/`; einzelne SHA-256-Hashes stehen im [Manifest](ausgabe/manifest.json). ZIP-Hash: `6f49bd148f7144208a1b07f9804f449d2ef69921067fb0e4b1a8b723dcafa86d`. Moodle-Zielinstanz, Patchstand, Theme und Testrollen sind offen.

| Prüffall | Status | Nachweis / nächster Schritt |
| --- | --- | --- |
| Felder, Platzzuordnung, Pflichtstatus | bestanden | 267 Felder: Plan, Raum, neun Konfigurationsfelder sowie 128 Name-/Foto-Paare; nur Planname ist Pflicht. Eingabe und Einzelansicht enthalten jedes Feld genau einmal. Pro Tisch sind die richtigen Foto- und Namenstokens zugeordnet. |
| Preset- und HTML-Struktur | bestanden | XML geparst; alle Platzhalter bekannt. Die sechs generierten HTML-Vorschauen mit html5lib ohne Parsefehler gelesen; keine doppelten IDs. Zwei Listen-Einträge zusammen geprüft. |
| Lokaler Sicherheitscheck | bestanden | Kein eigenes JavaScript, keine Skripte oder Eventhandler in den Vorlagen, keine Feldwerte in HTML-Attributen, keine externen CSS-Ressourcen. Alle CSS-Selektoren auf `.sp-db` begrenzt. Dies ist kein serverseitiger Penetrationstest. |
| Raumaufteilung und Lehrpersonenperspektive | bestanden | Standard 3 × 7 bei 1200, 390 und 320 px sowie 4 × 5, ungleich lange Reihen (6/5/4/3), 1 × 1 und 8 × 16 geprüft. Nicht gewählte Reihen und Plätze sind nicht sichtbar; bei ungültiger Aufteilung erscheinen Hinweis und alle 128 Plätze. Reihe 1 liegt nahe am Pult, Platz 1 links, Pult mittig und unter den Tischen, Tafel unter dem Pult. |
| Leere Namen und Fotos, lange Inhalte | bestanden | Normale, leere und überlange Beispieldaten bei 1200, 390 und 320 px geprüft; alle 21 Standardplätze bleiben sichtbar, leere Fotobereiche sind ausgeblendet. Namen werden nicht abgeschnitten. Geladene Symbolbilder mit Alternativtext geprüft. |
| Mobil, Eingabe und Tastatur | bestanden | Kein horizontaler Überlauf der Gesamtseite; das Raster scrollt im eigenen Bereich. Der Foto-Upload-Testnachbau passt auch geöffnet bei 320 px. Sichtbarer Fokus, Scrollen mit Pfeiltasten und Öffnen eines Fotoabschnitts per Enter geprüft. |
| Druck-CSS | bestanden | Im emulierten Druckmedium bei 1120 px passt der Standardplan ohne Scrollen; alle 21 Standardplätze bleiben erhalten. Kein physischer Ausdruck und keine echte Moodle-Druckseite geprüft. |
| Visuelle Durchsicht | bestanden | Die Screenshots für Desktop und Mobil wurden angesehen: richtige Orientierung, lesbare Namen und zusammenhängende Raumaufteilung. Die Mobilansicht zeigt einen seitlich verschiebbaren Ausschnitt. |
| ZIP und reproduzierbarer Build | bestanden | Elf Dateien in der Archivwurzel, CRC-Prüfung ohne Fehler, Inhalte bytegenau zu den Vorlagendateien. Erneuter Build des endgültigen Stands ergibt denselben oben genannten ZIP-Hash. |
| Instruktion und Dokumentation | bestanden | Einführung und Auftrag in h3-Struktur; Orientierung, Fotoverwendung und Speichern passen zur Vorlage. Die Instruktion entspricht dem XML-Intro. Lokale Dokumentlinks und Feldliste geprüft. |
| Moodle-Import, Felder, Pflichtprüfung | nicht_geprueft | Keine zugängliche Testinstanz; ZIP zunächst in eine leere, geschützte Aktivität importieren und 267 Felder vergleichen. |
| Echte Foto-Uploads, Speichern und Bearbeiten | nicht_geprueft | Lokale Uploadfelder sind Nachbauten. In Moodle insbesondere 128 Dateiverwaltungen in aufklappbaren Bereichen, tatsächliche Uploadgrenzen, Alternativtext, Entfernen/Ersetzen und Zuordnung nach Neuladen prüfen. |
| Rollen und direkter Fotozugriff | nicht_geprueft | Aktivitätsrechte konfigurieren und mit Lehrpersonen-, Lernenden- und Gastzugriff prüfen. Vor realen Namen und Fotos erforderlich. |
| Theme, Bilddarstellung, Suche und Druck in Moodle | nicht_geprueft | Benötigt die tatsächliche Zielversion und das Theme. Nach Import und nach Upgrades gemäss Spezifikation testen. |

## Nachweise

[Browserergebnisse](pruefung/browser-ergebnisse.json), [Desktop-Screenshot](pruefung/sitzplan-desktop.png), [Mobil-Screenshot](pruefung/sitzplan-mobil.png), [Manifest](ausgabe/manifest.json).

```bash
python3 -B 03-datenbanken/sitzplan/build.py
python3 -B 03-datenbanken/sitzplan/pruefen.py
python3 -B 03-datenbanken/sitzplan/browser_pruefung.py
```

Ein erster Browserlauf deckte einen Überlauf des aufgeklappten Foto-Nachbaus bei 320 px auf; die Breitenbegrenzung wurde korrigiert und alle Fälle erneut geprüft. Für Tastaturtests erhält der Headless-Browser ausdrücklich Fokus und ein vollständiges Enter-Ereignis. Der Sitzplan verwendet eigenes, auf die Raumaufteilung begrenztes JavaScript; es verändert keine Namen, Bilder, Uploads oder Feldwerte.

## Nächster Schritt

Die [Einrichtung](README.md) in einer leeren Testaktivität durchführen. Erst der Import-, Upload- und Rollentest belegt die Nutzung in der tatsächlichen Moodle-Umgebung. Die lokale Vorschau bildet keine Rollen, echte Dateiverwaltung oder Moodle-Persistenz ab.
