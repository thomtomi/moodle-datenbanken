---
title: "Spezifikation Hausarbeit-Gruppenerfassung"
date: 2026-09-08
---

# Spezifikation der Hausarbeit-Gruppenerfassung

## Zweck und Nutzung

Eine Person pro Hausarbeitsgruppe dokumentiert Gruppenname, sämtliche Mitglieder, Thema und Forschungsfrage in einem gemeinsamen Eintrag. Die eigene Gruppe und die Lehrperson dürfen ihn sehen. Die Kartenübersicht der Lehrperson kann die Arbeiten mehrerer Gruppen zeigen; Lernende sehen nur die Einträge ihrer eigenen Moodle-Gruppe.

Die eintragende Person bearbeitet ihren Eintrag. Andere Gruppenmitglieder erhalten durch die Gruppenzugehörigkeit kein gemeinsames Bearbeitungsrecht. Die Lehrperson verwaltet die Einträge mit den dafür vorgesehenen Moodle-Rechten.

Die Gruppen stimmen ab, wer erfasst, und prüfen vor dem Anlegen auf einen vorhandenen Eintrag. `maxentries=1` begrenzt Beiträge pro Person, nicht pro Gruppe. Eine automatische Eindeutigkeitsregel über alle Gruppenmitglieder ist mit diesem Standard-Preset nicht umgesetzt. Der Feldwert «Gruppenname» ist eine exportierbare Angabe, keine technische Gruppenzuordnung.

## Zielumgebung

- Moodle 5.0; Format und Kernfunktionen gegen den offiziellen Quellstand `v5.0.0` geprüft.
- Standardmodul `mod_data`, ausschliesslich Kernfeldtyp `text`; keine zusätzlichen Plugins, Schriften oder externen Dienste.
- Theme und konkrete Patchversion der Zielinstanz: offen. Die lokale Vorschau verwendet Systemschriften; Moodle übernimmt die Schrift des Themes.
- Testinstanz und Testkonten: bisher nicht verfügbar. Import, echte Gruppentrennung und tatsächlicher Moodle-Export sind noch zu prüfen.

## Felder und Exportvertrag

Die Reihenfolge gilt bei Import in eine neue, leere Aktivität. Die Feldnamen dürfen für den gewünschten Export nicht umbenannt werden.

| Reihenfolge | Exakter Feldname | Moodle-Typ | Pflicht | Inhalt und Beispiel |
| --- | --- | --- | --- | --- |
| 1 | Gruppenname | `text` | Ja | Zugewiesener Gruppenname, z. B. `Gruppe 01`; führende Null erhalten. |
| 2 | Gruppenmitglieder | `text` | Ja | Alle Namen einschliesslich der eintragenden Person; Trennung `; `, z. B. `Meier; Müller`. |
| 3 | Thema der Hausarbeit | `text` | Ja | Kurzer, aussagekräftiger Titel, z. B. `Mikroplastik`. |
| 4 | Forschungsfrage | `text` | Ja | Konkrete, eingegrenzte Frage im Klartext. |

Die Pflichtfelder sind in den Moodle-Felddefinitionen gesetzt. Inhaltliche Vollständigkeit, identischer Gruppenname und die Namenstrennung bleiben zusätzlich fachlich zu prüfen. Es wird keine automatische Synchronisation mit der Moodle-Mitgliederliste behauptet.

Alle vier Felder speichern Text ohne Rich-Text-Editor. JavaScript ersetzt nur das Eingabeelement der Forschungsfrage durch ein mehrzeiliges Textfeld und erhält Name, ID und Wert. Ohne JavaScript bleibt das native einzeilige Textfeld benutzbar. Das Skript setzt zusätzlich Pflichtfeldattribute und verknüpft Eingabehilfen; es speichert oder überträgt selbst keine Daten. Mehrzeilige CSV-Werte benötigen einen CSV-Parser, keine zeilenweise Aufteilung.

Ausgabe: UTF-8-CSV mit Komma als Spaltentrenner und doppeltem Anführungszeichen als Textbegrenzung. Semikolons innerhalb des Mitgliederfeldes bleiben Bestandteil dieses einen Feldes. Genau vier Spalten erfordern den Export ohne zusätzliche Tags, Autoren-, Zeit- und Freigabeangaben. Das [CSV-Beispiel](beispiel-export.csv) enthält ausschliesslich erfundene Daten und wurde lokal erzeugt.

## Instruktionsdesign

Grundlage ist die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md). Die [ausformulierte Instruktion](instruktion.html) wird als `intro` in `preset.xml` eingebettet und zusätzlich einzeln bereitgestellt. Beim Import muss die Übernahme der Einstellungen gewählt bzw. die Beschreibung manuell ergänzt werden.

| Abschnitt | Entscheidung und Begründung |
| --- | --- |
| Einführung | Übernommen: Zweck und eine erfassende Person pro Gruppe erklären. |
| Lernziele | Übernommen: Thema eingrenzen, Forschungsfrage formulieren und gemeinsame Arbeitsgrundlage dokumentieren; aus dem Auftrag abgeleitet. |
| Auftrag | Übernommen: gemeinsame Abstimmung, vorhandenen Eintrag prüfen, Gruppe wählen, vier Felder ausfüllen, gemeinsam prüfen, einmal speichern. Der letzte Satz nennt den Datenbankeintrag als Ergebnis. |
| Aufwand | Weggelassen: keine belastbare Dauer vorgegeben. |
| Bewertung Leistungsnachweis | Weggelassen: die Erfassung ist nicht als bewerteter Leistungsnachweis beauftragt; Bewertung der Hausarbeit nicht ableiten. |
| (Abgabe-)Termin | Weggelassen: kein Termin vorgegeben. |
| Reflexion & Auswertung | Weggelassen: keine zusätzliche Reflexionsaufgabe beauftragt; die gemeinsame Kontrolle ist Teil des Auftrags. |
| Literatur | Weggelassen: die Erfassung verlangt keine Literaturangaben; das Beispiel ist synthetisch. |

Die Überschriften behalten Reihenfolge und `h3`-Ebene der Vorlage. Icons entfallen einheitlich, weil kein Filter für die `[fa-…]`-Schreibweise nachgewiesen ist. Die Anleitung bleibt ohne Erweiterung verständlich. Der vollständige Auftrag steht in der Aktivitätsbeschreibung, die Erfassungsansicht ergänzt kurze Schritte und Hilfen am jeweiligen Feld.

## Darstellung

- Geführte Erfassung mit vier nummerierten Feldern, sichtbaren Beschriftungen, Formatbeispielen und Kontrolle vor dem Speichern.
- Responsive Karten mit Gruppenbadge, prominentem Thema, separat beschrifteter Forschungsfrage und Mitgliederliste. Text wird vollständig angezeigt und kann umbrechen.
- Einzelansicht und erweiterte Suche verwenden dieselben Feldnamen und Farben.
- Blau für Orientierung und Links, Türkis für Hinweise; Bedeutungen sind immer zusätzlich durch Text bezeichnet.
- CSS ist auf `.ha-db` beschränkt. Karten enthalten keine festen IDs. Die native Moodle-Aktionsauswahl bleibt erhalten und folgt Moodle-Berechtigungen.
- System-/Theme-Schrift, sichtbarer Tastaturfokus, verknüpfte Labels und Eingabehilfen; Farbkontrast und schmale Ansichten werden lokal geprüft.
- RSS ist deaktiviert. Die erforderlichen RSS-Vorlagendateien enthalten keine Gruppen- oder Personendaten.

## Abnahme und Betrieb

Lokal prüfen: Paketbestand, XML, Pflichtfelder, Feldreihenfolge, Platzhalter und `#id`-Verweise, eingebettete Instruktion, CSV-Beispiel, responsive Darstellung und JavaScript mit unveränderten Formularwerten. In Moodle prüfen: Testimport, Eingabe ohne und mit JavaScript, Pflichtfeldfehler, Bearbeitung durch die eintragende Person, Sichtbarkeit mit zwei Gruppen, unzulässiger Direktzugriff aus einer anderen Gruppe, Suche und CSV-Export über alle Gruppen als Lehrperson.

Die [Importanleitung](README.md) führt die Einstellungen auf, die nicht im Preset enthalten sind. Der aktuelle Nachweisstand steht im [Prüfprotokoll](pruefprotokoll.md). Originalquellen werden nicht überschrieben; ein bestehender Moodle-Datenbestand muss vor einer später beauftragten Umstellung gesichert und die Feldzuordnung gesondert geprüft werden.
