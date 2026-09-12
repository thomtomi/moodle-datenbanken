---
title: "Prüfprotokoll Hausarbeit-Gruppenerfassung"
date: 2026-09-09
---

# Prüfprotokoll der Hausarbeit-Gruppenerfassung

## Ergebnis und geprüfter Stand

**Nachweisstufe: lokal geprüft.** Paket- und Inhaltsprüfungen sowie sechs Browserfälle sind bestanden. Ein Moodle-Import, die serverseitige Gruppentrennung und ein tatsächlicher Moodle-CSV-Export wurden nicht ausgeführt, da keine Testinstanz verfügbar ist.

- Prüftag: 2026-09-09; technische Quellen am 2026-09-08 gelesen.
- Paket: [hausarbeit-gruppenerfassung-moodle50.zip](hausarbeit-gruppenerfassung-moodle50.zip).
- SHA-256 des geprüften ZIPs: `f433617a4440c5bfa9e3046ab2929487d93ce83d894deecd50d69a640ed3d99a`.
- Formatbezug: Moodle `v5.0.0`, Kernmodul `mod_data`; Quellen in der [Importanleitung](README.md).
- Lokale Werkzeuge: Python 3 mit Standardbibliothek; Chromium `152.0.7977.82` über das DevTools-Protokoll.
- Browsergrundlage: lokale HTML-Vorschau mit synthetischen Daten und nachgebildeten Moodle-Textfeldern. Die Vorschau verwendet die ausgelieferten Templates, CSS und JavaScript; Moodle-Rollen, Moodle-Aktionsmenüs, Theme und Servervalidierung werden dabei nicht ausgeführt.

## Ausgeführte Prüfungen

| Prüfung | Vorgehen und erwartetes Ergebnis | Status / Beobachtung |
| --- | --- | --- |
| Paket | `python3 pruefen.py`: Archiv öffnen, Prüfsummen der ZIP-Einträge prüfen und mit dem Ordner `preset/` vergleichen. | `bestanden`: genau elf erwartete Dateien auf oberster Ebene, keine zusätzliche Verzeichnisebene, alle Inhalte identisch. |
| XML und Einstellungen | `preset.xml` parsen, Wurzel und Felder prüfen; Aktivitätsbeschreibung mit `instruktion.html` vergleichen. | `bestanden`: Wurzel `preset`, vier Text-Pflichtfelder; Reihenfolge und Einstellungen stimmen; Anleitung vollständig eingebettet. |
| Verweise | Feldplatzhalter in Erfassung, Liste, Einzelansicht und Suche abgleichen; unterstützte Spezialtags und `#id` prüfen. | `bestanden`: alle vier Felder je Ansicht vollständig; keine unbekannten Tags und keine festen IDs in wiederholten Karten. |
| CSV-Beispiel | UTF-8-CSV mit Komma parsen; Kopfzeile und vier Werte je Zeile prüfen. Zusätzlich Komma, Anführungszeichen und Zeilenumbruch mit dem verwendeten CSV-Verfahren schreiben und zurücklesen. | `bestanden`: vier Spalten; `Gruppe 01`, `Meier; Müller` und Sonderzeichen bleiben erhalten. Dies ist kein Moodle-Exporttest. |
| Responsive Darstellung | Listen- und Erfassungsansicht jeweils bei exakt 320, 390 und 1440 CSS-Pixeln prüfen. | `bestanden`: kein horizontaler Seitenüberlauf; Karten einspaltig bei 320/390 Pixeln, mehrspaltig bei 1440 Pixeln. |
| Grenzfälle in Karten | Sehr langes Thema ohne Leerzeichen, lange Frage und leere Mitgliederanzeige in einer zusätzlichen synthetischen Karte prüfen. | `bestanden`: Inhalte umbrechen und bleiben innerhalb des Viewports. Leere Pflichtfelder sind nur ein Darstellungs-Prüffall. |
| JavaScript und Formularwerte | Vier Formularnamen und vorhandene Werte vor/nach der mehrzeiligen Erweiterung, bei wiederholter Initialisierung und nach Zurücksetzen vergleichen. | `bestanden`: Namen, IDs, Anfangswerte und bearbeitete mehrzeilige Werte bleiben erhalten; keine doppelte Umwandlung. |
| Eingabehilfen und Pflichtfelder | Sichtbare Labels und Hilfetexte über IDs zuordnen; gefülltes Formular und leeren Gruppennamen mit Browservalidierung prüfen. | `bestanden`: Zuordnungen vorhanden, ausgefülltes Formular gültig, leerer Gruppenname ungültig. Serverseitige Moodle-Prüfung weiterhin offen. |
| Tastatur | In jeder geprüften Erfassungsbreite das erste Feld fokussieren und mit einem echten Browser-Tastaturereignis Tab drücken. | `bestanden`: Fokus erreicht das Mitgliederfeld. Kein vollständiger Screenreader-Test. |
| Textkontraste | Relative Leuchtdichte der vorgesehenen Text-/Hintergrundpaare berechnen. | `bestanden`: Haupttext 12.79:1; Hinweise auf Weiss 6.41:1; Badge 8.04:1; Fragebeschriftung 6.41:1; Kopfhinweis 6.43:1. Keine allgemeine Zertifizierung der Barrierefreiheit. |
| Sichtprüfung | Desktopkarten und mobile Erfassung anhand der lokalen Screenshots durchsehen. | `bestanden`: klare Beschriftungen und Gruppenbadges, ruhige Blau-/Türkisgestaltung; Bedeutungen zusätzlich als Text. |

Browserergebnisse je Fall: [browser-ergebnisse.json](pruefung/browser-ergebnisse.json). Die Werte wurden über `Emulation.setDeviceMetricsOverride` eingestellt und mit `window.innerWidth` kontrolliert. Frühere Prüfstände mit noch nicht exakt gesetzter Fensterbreite wurden durch diese endgültigen Fälle ersetzt.

Gestaltungsnachweise aus der lokalen Vorschau:

- [Karten auf Desktop](pruefung/vorschau-desktop.png).
- [Karten bei 390 Pixeln](pruefung/vorschau-mobil.png).
- [Erfassung bei 390 Pixeln](pruefung/vorschau-erfassung.png), Ausschnitt des Formulars.

## Ausstehende Prüfung in Moodle 5.0

Die folgenden Fälle in einer neuen Testaktivität mit zwei getrennten Moodle-Gruppen ausführen. Gruppe A benötigt eine eintragende Person A1 und ein weiteres Mitglied A2; Gruppe B benötigt B1. Lehrperson und Lernende müssen ihre tatsächlichen Rollen verwenden.

| Prüffall | Schritte und erwartetes Ergebnis | Status |
| --- | --- | --- |
| Import und Feldbestand | ZIP in eine leere Aktivität importieren, Einstellungen übernehmen. Vier Felder in der vereinbarten Reihenfolge, Pflichtstatus und Beschreibung prüfen; keine Importfehler. | `nicht_geprueft`: Testinstanz fehlt. |
| Einrichtung der Gruppentrennung | «Getrennte Gruppen», Gruppierung und Mitgliedschaften gemäss README setzen; Lernende ohne Verwaltungsrechte und ohne Zugriff auf alle Gruppen. | `nicht_geprueft`: Zielkonfiguration fehlt. |
| Eintrag und Gruppe | A1 erfasst einen Eintrag für Gruppe A. Dieser gehört technisch Gruppe A; das Textfeld enthält denselben Gruppennamen. | `nicht_geprueft`. |
| Sichtbarkeit im eigenen Team | A2 kann den Eintrag ohne eigenen Beitrag lesen; die Lehrperson sieht ihn ebenfalls. A2 erhält kein unberechtigtes Bearbeitungsrecht. | `nicht_geprueft`. |
| Andere Gruppe und Direktzugriff | B1 sieht den Eintrag von A weder in Liste noch Suche; auch die direkte Einzelansicht und ein Bearbeitungsaufruf sind nicht zugänglich. Dieselbe Prüfung mit vertauschten Gruppen durchführen. | `nicht_geprueft`. |
| Bearbeitung | A1 kann den eigenen Eintrag ändern; die Lehrperson kann mit ihren Verwaltungsrechten korrigieren. | `nicht_geprueft`. |
| Begrenzung und Arbeitsregel | Zweiten Beitrag von A1 prüfen: serverseitig abgewiesen. Beachten, dass A2 grundsätzlich einen eigenen ersten Beitrag anlegen könnte; die Anleitung verlangt deshalb vorherige Gruppenabsprache und Kontrolle. | `nicht_geprueft`; keine gruppenweite Eindeutigkeit zugesichert. |
| Pflichtfelder und JavaScript-Ausfall | Jeweils ein Feld leer speichern, auch mit deaktiviertem JavaScript: Moodle muss den fehlenden Pflichtwert melden. Ohne JavaScript bleibt die Forschungsfrage als natives Textfeld ausfüllbar. | `nicht_geprueft`. |
| Mehrzeilige Frage | Mit aktivem JavaScript mehrere Zeilen eingeben, speichern, erneut öffnen und exportieren. Wert muss vollständig erhalten bleiben. | `nicht_geprueft`: lokale FormData-Prüfung allein reicht nicht. |
| Theme und Bedienung | Beschreibung, Aktionen, Suche, Fokus und Erfassung im tatsächlichen Theme bei schmaler Breite und mit Tastatur prüfen. | `nicht_geprueft`. |
| Vier-Spalten-Export | Als Lehrperson alle Gruppen wählen, vier Felder exportieren, Zusatzspalten deaktivieren. CSV als UTF-8 mit Komma lesen: exakte Kopfzeile und ein Datensatz je tatsächlich erfasster Gruppe. | `nicht_geprueft`. |

Moodle-Prüfergebnisse mit Datum, genauer Moodle-/Theme-Version und Dateistand ergänzen. Falls Dateien danach angepasst werden, die davon betroffenen Prüfungen erneut ausführen und den Paket-Hash aktualisieren.
