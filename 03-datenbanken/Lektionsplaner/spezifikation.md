---
title: "Spezifikation Lektionsplaner: Korrektur für Moodle 5.1"
date: 2026-09-09
---

# Spezifikation des Lektionsplaners

## Zweck und Umfang

Pro Eintrag wird eine Unterrichtsplanung für eine Klasse und ein Datum erfasst. Der Korrekturauftrag behebt B1–B5 des [ersten Reviews](pruefprotokoll-moodle-5-1.md), vereinheitlicht die aktuelle Lieferung und ergänzt Prüfungen gegen wiederkehrende Importfehler. Fachliche Planungsinhalte und Zahl der zu übernehmenden Einträge bleiben erhalten.

Ziel ist Moodle 5.1; technische Referenz ist der offizielle Quellcode von 5.1.0. Eine Testinstanz sowie deren Patchstand, Theme, Editor- und Rollenkonfiguration sind offen. Die lokale Python-App bleibt getrennt von der Moodle-Aktivität.

## Nutzung und Instruktionsdesign

Aus dem bestehenden Planer abgeleitete Annahme: Lehrpersonen erfassen Planungen; Lernende lesen die für sie bereitgestellten Planungen. Die tatsächlichen Rechte und die Sichtbarkeit sind beim Einrichten in Moodle festzulegen. Eine Trennung nach Gruppen ist für diesen Lektionsplaner nicht vorgegeben.

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde herangezogen. Dieser Auftrag verändert technische Erfassung und Import und führt keine neue Lernendenaufgabe ein. Die bestehende Einführung in der Aktivitätsbeschreibung sowie die Felder für Aktivitäten, Hausaufgaben und Lernziele bleiben bestehen. Aufwand, Bewertung, Abgabetermin, Reflexion und Literatur werden nicht pauschal als zusätzliche Instruktionsabschnitte ergänzt: Sie hängen von der einzelnen Unterrichtsplanung ab. Die gelieferten Planungsdaten werden nicht umredigiert.

Beim Lernzielfeld bleibt «Sie sind in der Lage, …» als sichtbarer Hinweis. Eine Schaltfläche fügt diesen Satzanfang auf Klick in ein leeres Feld ein. Vorhandene oder bewusst geleerte Lernziele werden beim Öffnen nicht verändert.

## Datenmodell

Verbindliche Feldnamen, Optionen und Pflichtmarkierungen stehen in [preset.xml](moodle-database-preset/lektionsplaner-db-preset/preset.xml). Die 40 Feldnamen und Typen des aktuellen Presets bleiben unverändert.

| Felder | Typ und Vorgabe |
| --- | --- |
| `klasse` | Menü, Pflicht; bestehende vier Klassenoptionen |
| `unterrichtsdatum` | Text, Pflicht; ISO-Datum `YYYY-MM-DD`, synthetisches Beispiel `2026-09-09` |
| `kalenderwoche` | Text, optional; bei gültigem Datum automatisch, z. B. `KW 37`; bestehender Wert bleibt bei unbekanntem Datum erhalten |
| `thema` | Mehrfachauswahl aus den bestehenden Themenoptionen |
| `zusatzmaterial_text`, `zusatzmaterial_link`, `zusatzmaterial_datei` | Textbereich, URL bzw. Datei |
| `lektion_1_beginn` bis `lektion_6_beginn` | Sechs Menüs mit den bestehenden Anfangszeiten |
| `lektion_1_ende` bis `lektion_6_ende` | Sechs Menüs mit den bestehenden Endzeiten |
| `lektion_1_aktivitaeten` bis `lektion_6_aktivitaeten` | Sechs Textbereiche |
| `hausaufgaben`, `lernziele` | Textbereiche |
| `leistungsnachweis_titel`, `leistungsnachweis_datum`, `leistungsnachweis_beginn`, `leistungsnachweis_ende` | Text; Datum nach demselben Format wie das Unterrichtsdatum |
| `leistungsnachweis_themen` | Textbereich |
| `stuetzkurs_titel`, `stuetzkurs_datum`, `stuetzkurs_beginn`, `stuetzkurs_ende` | Text; Datum nach demselben Format wie das Unterrichtsdatum |
| `stuetzkurs_ort`, `stuetzkurs_hinweis` | Textbereiche |
| `stuetzkurs_teams_url`, `stuetzkurs_anmeldung_url` | URL-Felder |

Nur Klasse und Unterrichtsdatum sind Moodle-Pflichtfelder. Eine Textfelddefinition erzwingt serverseitig kein Datumsformat. JavaScript unterstützt die Erfassung; der CSV-Build prüft Datum, Pflichtwerte und Auswahloptionen zusätzlich lokal.

## Ansichten und Verhalten

- Eingabe: Bestehende Abschnittsfolge; erste drei Lektionen initial offen. Weitere Lektionen, Leistungsnachweis und Stützkurs öffnen sich nur bei fachlichem Inhalt. Versteckte Moodle-Hilfswerte, Formatfelder und leeres Rich-Text-Markup zählen nicht als Inhalt.
- Datum: Gültige ISO-Daten bleiben erhalten. Eindeutige Daten mit Punkten werden vor der Typumstellung normalisiert. Unbekannte oder ungültige Werte bleiben mit Hinweis als Text erhalten; eine gespeicherte Kalenderwoche wird dann nicht gelöscht.
- Zeitfenster: Sechs beschriftete Auswahlfelder setzen Beginn und Ende. Ohne JavaScript sind die Komfortmenüs deaktiviert; die eigentlichen Moodle-Felder bleiben nutzbar.
- Lernziele: Einfügen per Klick; bei TinyMCE über die bestehende Editorinstanz und deren Speicherfunktion. Ein nicht bereiter Editor führt zu einem Hinweis statt einer Änderung.
- Liste: Mehrere unabhängige Karten; Übersicht der ersten zwei Lektionen und Link zur vollständigen Einzelansicht. Einzelansicht: alle sechs Lektionen, leere optionale Inhalte ausgeblendet.
- Erweiterte Suche: Der bestehende Aktivitätenfilter wird als «Aktivitäten der 1. Lektion» beschriftet. Eine neue Suche über alle sechs Felder ist nicht Bestandteil der Korrektur.

## Übertragung und Bestandsschutz

Die aktuelle Lieferung besteht aus ZIP und CSV in [ausgabe/](moodle-database-preset/ausgabe/). Alte Archive und CSVs bleiben unveränderte Quellen. Die MBZ mit 37 Feldern wird als nicht zur aktuellen Lieferung gehörend dokumentiert. Eine neue MBZ soll aus der später tatsächlich getesteten Moodle-Aktivität exportiert werden.

CSV-Quelle ist `lektionsplaner-daten-import.csv` mit zehn Einträgen. Die vier Linkzuordnungen sind durch vorhandenen Originalexport und Instanzmetadaten belegt. Ausschliesslich 21 Zellen mit Sicherungstokens werden korrigiert. Reihenfolge, übrige Werte und zehn Einträge bleiben erhalten. Keine Zusammenführung mit anderen Datenständen.

CSV-Dialekt: UTF-8 ohne BOM, Komma, doppelte Anführungszeichen, korrekt maskierte mehrzeilige Werte. Das Feld `zusatzmaterial_datei` ist in den zehn Einträgen leer. Die Erreichbarkeit der Links ist in Moodle zu prüfen. Andere Instanzen/Kurse benötigen eine bewusste Zuordnung ihrer Linkziele.

## Abnahme

Lokal nachzuweisen: reproduzierbarer Build, konsistente 40 Felder, exakte Datenerhaltung ausser den vier Linkersetzungen, Ablehnung unbekannter Tokens und falscher Schemata vor dem Schreiben, korrigierte Formularfälle einschliesslich ungültiger Daten und leerer Rich-Text-Felder, zugängliche Zeitfenster-Namen und responsive Ansichten. Die vorhandenen App-Tests müssen bestehen.

In Moodle ausstehend: ZIP-/CSV-Import, tatsächliche Editor- und Dateimanagerfunktion, Speichern und Bearbeiten, Suche und Sortierung sowie Sichtbarkeit mit vorgesehenen Rollen. Ergebnisse und Grenzen stehen im [Prüfprotokoll](pruefprotokoll.md).
