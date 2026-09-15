---
title: "Pruefprotokoll Kursredaktions-Checkliste"
date: 2026-09-14
---

# Pruefprotokoll der Kursredaktions-Checkliste

## Ergebnis und gepruefter Stand

**Nachweisstufe: lokal geprueft.** Der reproduzierbare Build und die lokale Konsistenzpruefung sind am 2026-09-14 unter Python 3 mit der Standardbibliothek erfolgreich ausgefuehrt worden. Die Lieferung umfasst ein Moodle-Preset fuer 5.0.4, eine synthetische CSV-Beispieldatei und eine lokale HTML-Vorschau. Ein Import in Moodle, ein Rollenpruefung und ein tatsaechlicher Moodle-CSV-Export wurden nicht ausgefuehrt.

- Paket: [kursredaktions-checkliste-moodle504.zip](ausgabe/kursredaktions-checkliste-moodle504.zip)
- SHA-256 des geprueften ZIPs: `79bc118e636cbfade171f1f50503a7acb0d86ecd6f40da9b075924edaf84c40b`
- Formatbezug: Moodle 5.0.4, Kernaktivitaet `mod_data`; Theme, Patchstand der Testinstanz und Testkonten sind offen.
- Lokale Beispielwerte: ausschliesslich synthetisch in [beispiel-export.csv](beispiel-export.csv) und [vorschau.html](vorschau.html).

## Ausgefuehrte Pruefungen

| Pruefung                      | Vorgehen und erwartetes Ergebnis                                                                                                                                        | Status / Beobachtung                                                                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Build                         | `python3 -B build.py` erzeugt das ZIP, die CSV und die Vorschau. Die Aktivitaetsbeschreibung wird vor dem Build aus `instruktion.html` ins Preset synchronisiert.       | `bestanden`: alle drei Ausgaben erstellt; kein Python-Fehler.                                                                                 |
| XML, Felder und Einstellungen | `python3 -B pruefen.py` parst die XML-Datei und gleicht Namen, Reihenfolge, Typen, Pflichtstatus, Statusoptionen sowie Einstellungen ab.                                | `bestanden`: 13 Felder; acht Auswahlfelder mit `Erfuellt`, `Korrektur noetig`, `Nicht anwendbar`, `Nicht geprueft`; Beschreibung eingebettet. |
| Vorlagen und CSS              | Platzhalter, Moodle-Spezialtags, vollstaendige Eingabevorlage, feste IDs in wiederholten Karten, leeres JavaScript und gekapseltes CSS ohne externe Ressourcen pruefen. | `bestanden`: nur bekannte Feldplatzhalter sowie `##moreurl##` und `##actionsmenu##`; keine festen Karten-IDs und keine externen Ressourcen.   |
| ZIP                           | Archivstruktur, CRC und Inhaltsgleichheit mit allen Preset-Quelldateien pruefen.                                                                                        | `bestanden`: genau elf Dateien direkt im ZIP; ZIP lesbar, Inhalte identisch.                                                                  |
| CSV                           | Beispiel-CSV mit UTF-8 und Komma lesen; einen Rundlauf mit Komma, Anfuehrungszeichen, Umlaut und mehrzeiligem Hinweis pruefen.                                          | `bestanden`: 13 Feldspalten; Linkbefunde bleiben mehrzeilig, Sonderzeichen bleiben erhalten.                                                  |

## Offene Moodle-5.0.4-Pruefungen

| Prueffall                 | Erwartetes Ergebnis                                                                                                                                                                                                | Status                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Preset-Import             | ZIP in eine neue, leere Datenbank importieren; 13 Felder, acht Statusauswahlen, Beschreibung und Standardsortierung gegen die Spezifikation kontrollieren.                                                         | `nicht_geprueft`: Keine benannte Testinstanz.                             |
| Eingabe und Pflichtfelder | Einen synthetischen Eintrag speichern und bearbeiten; jedes Pflichtfeld einmal leer lassen. Moodle meldet fehlende Werte, lange und mehrzeilige Hinweise bleiben erhalten.                                         | `nicht_geprueft`: Benötigt Moodle-Testaktivität.                          |
| Ansichten und Suche       | Liste, Einzelansicht und Suche mit mehreren Einträgen sowie bei schmaler Ansicht im tatsächlichen Theme prüfen.                                                                                                    | `nicht_geprueft`: Theme und Testinstanz offen.                            |
| Rollen                    | Als Lehrperson ausserhalb des Redaktionsteams nur Einsicht und Suche; als Redaktionsteam Erstellen, Bearbeiten, Löschen und Export. Direkte Bearbeitungs- und Exportaufrufe der Lehrperson müssen verweigert sein. | `nicht_geprueft`: Benötigt zwei geeignete Testkonten und Rollen-Override. |
| CSV-Export                | Als Redaktionsteam nur die 13 Feldspalten exportieren; Zusatzspalten deaktivieren. UTF-8, Komma, Kopfzeile und mehrzeilige Befunde mit einem CSV-Parser abgleichen.                                                | `nicht_geprueft`: Tatsächliches Moodle-Exportformular nicht geprüft.      |

Die lokale Prüfung belegt weder den Moodle-Import noch die Moodle-Rollen, die Theme-Darstellung oder den tatsächlichen CSV-Export. Nach erfolgreichem Test in einer konkreten Moodle-5.0.4-Instanz sind Datum, Moodle-Patchstand, Theme, Testrollen und Beobachtungen zu ergänzen. Bei Änderungen an Preset, CSV oder Vorlagen müssen die betroffenen lokalen Prüfungen erneut ausgeführt und der ZIP-Hash aktualisiert werden.
