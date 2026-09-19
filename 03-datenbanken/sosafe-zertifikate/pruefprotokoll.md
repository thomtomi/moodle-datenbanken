---
title: "Prüfprotokoll SoSafe-Zertifikate"
date: 2026-09-17
---

# Prüfprotokoll SoSafe-Zertifikate

## Prüfgegenstand und Umgebung

- **Prüfgegenstand:** Initiale lokale Lieferung in
  `03-datenbanken/sosafe-zertifikate/`; SHA-256 des geprüften ZIP:
  `19a665989da4d9f2072fd7d7b63c4a269524f252316c779808302e94459eaa3e`.
- **Datum:** 2026-09-17.
- **Lokale Werkzeuge:** Python 3 mit Standardbibliothek.
- **Moodle-Zielumgebung:** Moodle 5.0.4; Theme, Testinstanz und Browser:
  offen.

## Prüfungen

| Prüffall                           | Erwartetes Ergebnis                                                                                                            |     Status     | Befund und nächster Schritt                                          |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | :------------: | -------------------------------------------------------------------- |
| `python3 -B build.py`              | Preset-ZIP, UTF-8-CSV und lokale Vorschau werden erzeugt.                                                                      | bestanden | Am 2026-09-17 lokal ausgeführt; ZIP, CSV und Vorschau erzeugt.       |
| `python3 -B pruefen.py`            | XML, drei Felder, acht Klassen, zwei Statuswerte, Platzhalter, CSS, JavaScript, ZIP und CSV-Rundlauf sind konsistent.          | bestanden | Am 2026-09-17 lokal ausgeführt; keine Befunde. ZIP-SHA-256 siehe oben. |
| Lokale Vorschau                    | Vollständiger und unvollständiger Status, Hinweis, Ersteller:in und Änderungszeit sind lesbar.                                 | nicht_geprueft | `vorschau.html` in einem Browser prüfen.                             |
| Moodle-Import                      | Das Preset wird in eine neue leere Moodle-5.0.4-Datenbank importiert.                                                          | nicht_geprueft | Mit dem ZIP in einer benannten Testinstanz importieren.              |
| Moodle-Nutzung als Lehrperson      | Einträge erstellen, bearbeiten, suchen und beide Ansichten nutzen; `##user##` und `##timemodified##` werden korrekt angezeigt. | nicht_geprueft | Mit einem Lehrpersonenkonto und synthetischen Einträgen prüfen.      |
| Moodle-Nutzung als lernende Person | Keine Einsicht, Erfassung oder Bearbeitung möglich.                                                                            | nicht_geprueft | Mit einem getrennten Lernenden-Testkonto und Rollen-Override prüfen. |

## Offene Arbeit

Moodle-Import und Moodle-Nutzung sind noch auszuführen. Ein lokaler Erfolg
belegt weder den Import noch die Rechtekonfiguration in der Zielinstanz.
