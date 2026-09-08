---
title: "Hausarbeit-Gruppenerfassung"
date: 2026-09-08
---

# Hausarbeiten als Gruppe erfassen

Das [Preset für Moodle 5.0](hausarbeit-gruppenerfassung-moodle50.zip) richtet vier Pflichtfelder, eine geführte Erfassungsansicht, responsive Karten, eine Einzelansicht und eine Suchvorlage ein. Pro Gruppe übernimmt eine Person die Erfassung. **Für die Sichtbarkeit nur innerhalb der eigenen Gruppe müssen nach dem Import die unten beschriebenen Moodle-Gruppeneinstellungen gesetzt werden.**

Die [lokale Vorschau](vorschau.html) zeigt Karten, Erfassung und Lernendenanleitung mit erfundenen Beispieldaten. Sie enthält keine Moodle-Anbindung. Die Karten mit mehreren Gruppen veranschaulichen die Ansicht der Lehrperson.

## Import in Moodle 5.0

1. Im Kurs die Hausarbeitsgruppen mit eindeutigen Namen, zum Beispiel «Gruppe 01», anlegen und alle Mitglieder zuweisen. Für diese Aufgabe soll jede lernende Person genau einer Hausarbeitsgruppe angehören. Bei weiteren Gruppeneinteilungen im Kurs eine eigene Gruppierung für die Hausarbeitsgruppen verwenden.
2. Eine neue, leere Aktivität «Datenbank» anlegen, zum Beispiel «Hausarbeiten – Gruppen und Forschungsfragen». Die Aktivität zunächst für Lernende verbergen.
3. Über «Vorlagen/Presets» bzw. «Vorlagensatz importieren» die Datei `hausarbeit-gruppenerfassung-moodle50.zip` hochladen. Die genaue Bezeichnung kann vom Sprachpaket abhängen. Das ZIP unverändert hochladen, ohne zusätzlichen Ordner darum.
4. Beim Import **aktuelle Einstellungen überschreiben/übernehmen** aktivieren. So werden auch die Lernendenanleitung, Begrenzungen und Sortierung übernommen. Diese Anleitung gilt für eine neue, leere Aktivität; ein Import in vorhandene Datenbanken kann bestehende Felder und Daten verändern.
5. Prüfen, ob die Aktivitätsbeschreibung als HTML angezeigt wird. Falls sie fehlt oder als HTML-Quelltext erscheint, den Inhalt von [instruktion.html](instruktion.html) in der HTML-Ansicht des Beschreibungseditors einsetzen. Die Beschreibung muss vor der Bearbeitung erreichbar sein.
6. Die folgenden Aktivitätseinstellungen kontrollieren, bevor Lernende die Aktivität nutzen.

| Einstellung | Gewünschter Wert | Herkunft |
| --- | --- | --- |
| Gruppenmodus | **Getrennte Gruppen** | Manuell in den weiteren Moduleinstellungen setzen; kein Bestandteil des Presets. |
| Gruppierung | Hausarbeitsgruppen, falls eine eigene Gruppierung verwendet wird | Manuell zuordnen. |
| Erzwungener Kursgruppenmodus | Muss «Getrennte Gruppen» zulassen bzw. selbst erzwingen | Bei abweichender Kurseinstellung zuerst dort klären. |
| Erforderliche Einträge | 0 | Im Preset; die übrigen Mitglieder müssen keinen eigenen Eintrag erstellen. |
| Einträge vor der Ansicht erforderlich | 0 | Im Preset; Mitglieder können den Eintrag der erfassenden Person sehen. |
| Maximale Einträge | 1 pro Person | Im Preset; keine gruppenweite Sperre. |
| Freigabe erforderlich | Nein | Im Preset; Einträge sollen sofort innerhalb der eigenen Gruppe lesbar sein. |
| Kommentare | Nein | Im Preset. |
| RSS | 0 / deaktiviert | Im Preset. |
| Standardsortierung | Gruppenname, aufsteigend | Im Preset. |
| Bewertung und Aktivitätsabschluss | Keine Bewertung für diese Erfassung; keinen eigenen Eintrag von jedem Gruppenmitglied als Abschluss verlangen | Manuell prüfen; keine entsprechende Gruppenbewertung oder Gruppenabschlusslogik im Preset. |

Gruppenmodus, Gruppierung und Mitgliedschaften gehören zu Moodle, nicht zum Textfeld «Gruppenname». Lernende dürfen keine Berechtigung «Auf alle Gruppen zugreifen» (`moodle/site:accessallgroups`) oder «Einträge verwalten» (`mod/data:manageentries`) erhalten. Für die Lehrperson sind die vorgesehenen Verwaltungs- und Gruppenrechte erforderlich. Die konkrete Rollenbelegung mit Testkonten prüfen. Die Funktion getrennter Gruppen beschreibt [MoodleDocs: Groups](https://docs.moodle.org/500/en/Groups).

7. Mit zwei Testgruppen die Fälle im [Prüfprotokoll](pruefprotokoll.md) ausführen. Dabei einen tatsächlichen Lernendenzugang je Gruppe und ein weiteres Mitglied der ersten Gruppe verwenden.
8. Nach erfolgreichen Tests die Aktivität im Kurs verfügbar machen und auf genau eine erfassende Person pro Gruppe hinweisen.

## Was das Preset bei der Gruppenarbeit leistet

Einträge werden von Moodle mit der beim Erfassen ausgewählten Moodle-Gruppe verbunden. Die Textangabe «Gruppe 01» stellt diese Zuordnung nicht selbst her. Bei einer Gruppenauswahl muss die eintragende Person die richtige Gruppe wählen. Lehrpersonen sollen keine Einträge für «Alle Teilnehmenden» anlegen, wenn diese nur einer Gruppe zugänglich sein sollen.

Die eintragende Person kann den eigenen Eintrag bearbeiten. Andere Mitglieder sehen ihn innerhalb ihrer Gruppe; sie erhalten dadurch kein Bearbeitungsrecht. Für Korrekturen wenden sie sich an die eintragende Person oder die Lehrperson.

Die Vorgabe «genau ein Datensatz pro Gruppe» wird durch Absprache und Kontrolle umgesetzt. Die Moodle-Grenze von einem Eintrag zählt pro Person. Sie verhindert keinen zweiten Eintrag durch ein anderes Gruppenmitglied. Eine strikte technische Sperre würde eine zusätzliche serverseitige Lösung erfordern. Grundlage der Begrenzung ist `data_atmaxentries()` in [Moodle v5.0.0: mod/data/lib.php](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/lib.php).

## Export mit genau vier Spalten

1. Als Lehrperson die Datenbank öffnen und für einen Gesamtexport in der Gruppenauswahl **Alle Teilnehmenden/alle Gruppen** wählen. Bei Auswahl einer einzelnen Gruppe wird der Export auf diese Gruppe beschränkt.
2. Die Funktion «Einträge exportieren» öffnen und CSV mit **Komma** als Trennzeichen wählen.
3. Genau die vier Datenbankfelder auswählen: `Gruppenname`, `Gruppenmitglieder`, `Thema der Hausarbeit`, `Forschungsfrage`.
4. Zusätzliche Optionen für **Tags, Nutzerinformationen, Zeitangaben, Freigabestatus und Dateien ausschalten**, soweit angezeigt. Tags können standardmässig ausgewählt sein.
5. Exportieren und beim Öffnen in einer Tabellenkalkulation UTF-8, Komma als Trennzeichen und `"` als Textbegrenzungszeichen verwenden. Das Mitgliederfeld nicht am Semikolon aufteilen.

Erwartete Tabellenstruktur, hier mit erfundenen Beispieldaten:

| Gruppenname | Gruppenmitglieder | Thema der Hausarbeit | Forschungsfrage |
| --- | --- | --- | --- |
| Gruppe 01 | Meier; Müller | Mikroplastik | Welchen Einfluss hat Mikroplastik im Boden auf die Keimung von Kresse? |

Die [beispiel-export.csv](beispiel-export.csv) veranschaulicht das Format; sie ist kein tatsächlich aus Moodle exportierter Nachweis. Auf einer neuen Aktivität werden die Felder in dieser Reihenfolge angelegt. Moodle exportiert nach Feld-ID-Reihenfolge; bei späterem Löschen und Neuanlegen von Feldern muss die Reihenfolge erneut geprüft werden. Grundlagen: [Exportformular](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/export_form.php), [Exportaufruf](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/export.php) und [Exportimplementierung](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/classes/local/exporter/utils.php), jeweils Moodle `v5.0.0`.

Der Gruppenname wird als Text gespeichert, damit beispielsweise «Gruppe 01» erhalten bleibt. Die Namen innerhalb einer Gruppe werden mit `; ` getrennt. Kommas, Anführungszeichen und Zeilenumbrüche in Texten müssen durch die CSV-Textbegrenzung erhalten bleiben. Für den Testimport synthetische Daten verwenden und nicht mehrfach dieselbe CSV importieren; ein CSV-Import ist keine zugesicherte Aktualisierung vorhandener Einträge.

## Dateien und Nachweise

- [spezifikation.md](spezifikation.md): Anforderungen, Feldmodell, Instruktionsauswahl und Grenzen.
- [pruefprotokoll.md](pruefprotokoll.md): ausgeführte lokale Prüfungen und ausstehende Moodle-Prüfungen.
- `preset/`: bearbeitbare XML-, HTML-, CSS- und JavaScript-Dateien; genau diese Dateien sind im ZIP enthalten.
- [instruktion.html](instruktion.html): Anleitung für die Aktivitätsbeschreibung, ebenfalls im XML enthalten.
- [build.py](build.py): reproduzierbare Erzeugung von XML, ZIP, CSV-Beispiel und Vorschau.
- [pruefen.py](pruefen.py): lokale Prüfung von Paket, Feldverweisen und Exportbeispiel.

Aus dem Aktivitätsordner ausführen:

```bash
python3 build.py
python3 pruefen.py
```

Die Paketdateinamen entsprechen `TEMPLATES_LIST` aus [Moodle v5.0.0: manager.php](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/classes/manager.php). XML und übertragbare Einstellungen wurden mit [preset.php](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/classes/preset.php) und [preset_importer.php](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/classes/local/importer/preset_importer.php) abgeglichen. Die Formularplatzhalter und Aktionen folgen [template.php](https://github.com/moodle/moodle/blob/v5.0.0/mod/data/classes/template.php). Alle Quellen wurden am 2026-09-08 gelesen.
