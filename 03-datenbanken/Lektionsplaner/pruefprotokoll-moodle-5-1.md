---
title: "Lektionsplaner: Kompatibilitätsprüfung für Moodle 5.1"
date: 2026-09-09
---

# Kompatibilitätsprüfung für Moodle 5.1

**Historischer Befund zum Ausgangsstand.** Korrekturen und erneute Prüfungen stehen im [aktuellen Prüfprotokoll](pruefprotokoll.md). Die unten genannten Hashes und JSON-Nachweise gelten für den Zustand vor diesen Korrekturen; verlinkte Quelldateien öffnen inzwischen deren bearbeiteten Stand.

Das aktuelle ZIP-Preset verwendet eine von Moodle 5.1 unterstützte Struktur, Standardfeldtypen und Vorlagen-Tags. Bei der statischen Prüfung wurde kein grundsätzlicher Formatkonflikt mit Moodle 5.1.0 gefunden. **Die Lieferung ist dennoch nicht uneingeschränkt einsatzbereit:** Die empfohlene CSV enthält unaufgelöste Sicherungslinks, die mitgelieferte MBZ einen älteren Strukturstand und das Formular mehrere nachvollziehbare Fehler.

Diese Befunde betreffen den vorhandenen Lektionsplaner; sie sind kein Nachweis einer durch das Upgrade auf 5.1 verursachten Regression. Ein Import oder Funktionstest in einer laufenden Moodle-Instanz wurde nicht durchgeführt. Die Prüfung hat keine vorhandenen Anwendungsdateien, Vorlagen, ZIPs, CSVs oder Sicherungen geändert.

## Prüfgrundlage und Grenzen

| Punkt | Geprüfter Stand |
| --- | --- |
| Gegenstand | Lokale App, Preset-Quellordner, drei ZIPs, vier CSVs und zwei MBZ-Dateien unter `moodle-database-preset/` |
| Moodle-Referenz | Offizielle MoodleDocs für 5.1 sowie Quellcode des Tags `v5.1.0` |
| Zielinstanz | Nicht zugänglich; genauer 5.1-Patchstand, Theme, Texteditor-Konfiguration und Rollen offen |
| Lokale Werkzeuge | Python 3.13, XML-/CSV-/ZIP-/TAR-Parser; Chromium 152.0.7977.82 |
| Browserprüfung | Originales Preset-CSS und -JavaScript; synthetische Eingaben und aus den Vorlagen zusammengesetzte Ansichten bei 320, 390 und 1440 Pixel Breite |
| Begrenzung des Browsernachweises | Formular-HTML anhand der Moodle-5.1-Feldklassen nachgebildet; kein Moodle, TinyMCE, echtes Aktionsmenü oder Dateimanager geladen |
| Nachweise | [Struktur, Mengen und SHA-256](pruefung-moodle-5-1/struktur-ergebnisse.json), [Browserergebnisse](pruefung-moodle-5-1/browser-ergebnisse.json) |

## Bestand und Formatabgleich

Alle drei ZIPs enthalten dieselben elf Dateien unmittelbar im Archivwurzelverzeichnis: `preset.xml` und die zehn von Moodle erwarteten Vorlagendateien. Die CRC-Prüfung besteht; alle enthaltenen Dateien stimmen bytegenau mit `lektionsplaner-db-preset/` überein. Die Varianten ohne Zusatz, `-kompatibel` und `-optimiert` sind somit keine unterschiedlichen Entwicklungsstände.

Gemeinsamer ZIP-SHA-256: `af94c0c883fba2a8e9725b399d6a5d3127086d608cdf75b31461a7291ad56fe7`.

Die XML definiert 40 eindeutige Felder mit den Standardtypen `text`, `textarea`, `menu`, `multimenu`, `url` und `file`. Alle Feldverweise der HTML-Vorlagen sind auflösbar; die Eingabevorlage enthält jedes Feld genau einmal. Die verwendeten Sonder-Tags `##actionsmenu##` und `##moreurl##` werden von Moodle 5.1 unterstützt. Grundlage: [Moodle 5.1: Vorlagen](https://docs.moodle.org/501/en/Database_templates) und [Moodle v5.1.0: erwartete Vorlagendateien](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/manager.php#L47).

Das Feld `unterrichtsdatum` ist ein Textfeld mit ISO-Datum. Seine Verwendung als Sortierfeld ist bei konsistentem `YYYY-MM-DD` plausibel. Das Preset-Setting `manageapproved` steht allerdings nicht auf der Import-Allowlist und wird nicht übernommen; bei der enthaltenen Einstellung `approval=0` ist dies kein Importblocker. Weitere Aktivitätseinstellungen müssen in Moodle geprüft werden. Quelle: [Preset-Importer v5.1.0](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/local/importer/preset_importer.php#L158).

| Datendatei | Einträge | Felder/Spalten | Ergebnis des Strukturvergleichs |
| --- | ---: | ---: | --- |
| `lektionsplaner-daten-import.csv` | 10 | 40 | Aktuelles Schema; Sicherungsplatzhalter in Links, siehe B1 |
| `lektionsplaner-daten-import-aus-unterrichtsplanung.csv` | 11 | 40 | Aktuelles Schema; keine Sicherungsplatzhalter gefunden |
| `Unterrichtsplanung-13_records-20260907_1446.csv` | 13 | 40 | Aktuelles Schema; keine Sicherungsplatzhalter gefunden |
| `Unterrichtsplanung-11_records-20260904_1336.csv` | 11 | 7 | Altes Schema; nicht direkt in das aktuelle Preset importieren |
| `lektionsplaner-datenbank-mit-daten.mbz` | 10 | 37 | Älterer umgebauter Stand, siehe B2 |
| `sicherung-moodle2-activity-69203-data69203-20260904-1416.mbz` | 10 | 7 | Originalstruktur der alten Aktivität |

Die CSVs lassen sich als UTF-8, mit Komma als Trennzeichen und doppelten Anführungszeichen als Textbegrenzung vollständig lesen. Alle drei CSVs mit 40 Spalten haben die exakten aktuellen Feldnamen und deren Reihenfolge; ihre belegten Datumswerte sind gültige ISO-Daten und die Auswahlwerte passen zu den Optionen. Mehrfachauswahlen verwenden `##`; URL-Felder können URL und Linktext durch ein Leerzeichen getrennt enthalten. Diese Formate passen zu den geprüften [Mehrfachauswahl-](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/field/multimenu/field.class.php) und [URL-Feldklassen](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/field/url/field.class.php#L193).

Beide MBZs sind lesbare komprimierte TAR-Archive. Ihre Metadaten nennen Moodle `5.0.7 (Build: 20260420)`. Die Prüfung der Dateimanifeste fand keine fehlenden Binärdateien und keine Dateien im Inhaltsbereich `mod_data/content`. Daraus folgt keine Bestätigung, dass verlinkte externe Materialien in der Zielinstanz erreichbar sind.

## Befunde mit Korrekturempfehlung

### B1 – Hohe Priorität: Empfohlene CSV enthält nicht aufgelöste Moodle-Sicherungslinks

Die [Preset-Anleitung](moodle-database-preset/README.md), Zeilen 19–27, empfiehlt `lektionsplaner-daten-import.csv`. Darin enthalten **21 Zellen** noch Tokens der Formen `$@COURSEVIEWBYID…@$` und `$@SCHEDULERVIEWBYID…@$`. Betroffen sind `lektion_1_aktivitaeten` (3 Zellen), `stuetzkurs_anmeldung_url` (10), `stuetzkurs_hinweis` (7) und `hausaufgaben` (1).

Der [CSV-Importer von Moodle 5.1.0](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/local/importer/csv_entries_importer.php) führt keine Sicherungs-Linkdekodierung durch. Diese ist Teil der Wiederherstellung, siehe [Restore-Dekodierung für Datenbankinhalte](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/backup/moodle2/restore_data_activity_task.class.php#L54). HTML-Links bleiben dadurch unbrauchbar; im URL-Feld können ungültige Werte zusätzlich bereinigt werden. Ein erfolgreicher CSV-Upload wäre kein Beleg für funktionierende Links.

**Empfehlung:** Die fachlich gewünschte Datenbasis auswählen und Sicherungstokens vor dem CSV-Import anhand bekannter Zieladressen auflösen. Die vorhandenen Dateien mit 11 bzw. 13 Einträgen enthalten keine solchen Tokens und sind Kandidaten; sie haben unterschiedliche Datenstände und dürfen nicht ungeprüft ausgetauscht oder zusammengeführt werden. Auch ihre absoluten Kurs- und Aktivitätslinks müssen in der Zielumgebung geprüft werden. Der [MBZ-zu-CSV-Exporter](moodle-database-preset/export_moodle_records_csv.py), Zeilen 35–53, benötigt eine Prüfung, die nicht aufgelöste Tokens vor der Ausgabe meldet.

### B2 – Hohe Priorität bei Wiederherstellung: MBZ und aktuelles Preset bilden unterschiedliche Datenbanken ab

`lektionsplaner-datenbank-mit-daten.mbz` enthält 37 Felder. Es fehlen `zusatzmaterial_text`, `zusatzmaterial_link` und `zusatzmaterial_datei`. Zudem sind **14 Feldtypen abweichend**: Klasse, Thema und alle zwölf Lektionszeitfelder sind dort Textfelder; im ZIP sind es Menü- bzw. Mehrfachauswahlfelder. Auch die Vorlagen entsprechen nicht dem aktuellen Quellordner.

Die MBZ ist deshalb kein gleichwertiger Ersatz für «aktuelles ZIP plus CSV». Die CSV mit 40 Spalten würde in einer allein aus dieser MBZ wiederhergestellten Aktivität unbekannte Spalten vorfinden; der Moodle-CSV-Importer bricht bei solchen Feldnamen ab.

**Empfehlung:** Einen nachvollziehbaren Lieferstand festlegen. Für die aktuelle Struktur das ZIP als Ausgangspunkt verwenden und den gewählten Datenimport korrigieren. Falls eine vollständige MBZ benötigt wird, diese nach erfolgreichem Import aus einer geprüften Moodle-Testaktivität neu sichern. Die vorhandene MBZ als älteren Stand kennzeichnen und erhalten. Ein blosses Überschreiben der Vorlagen behebt die Feldtypenunterschiede nicht.

### B3 – Mittlere Priorität: Leere optionale Abschnitte werden geöffnet

In [jstemplate.js](moodle-database-preset/lektionsplaner-db-preset/jstemplate.js), Zeilen 289–295, untersucht `openFilledDetails()` sämtliche `input`, `textarea` und `select`. `controlHasContent()` berücksichtigt auch versteckte Werte und Format-Auswahlfelder. Moodle erzeugt bei Textbereichen beispielsweise eine versteckte Draft-ID und ein Feld für das Textformat; siehe [Textarea-Feldklasse v5.1.0](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/field/textarea/field.class.php#L229).

**Reproduziert:** Ein ansonsten leeres Formular mit solchen Moodle-Hilfsfeldern öffnet die 4., 5. und 6. Lektion sowie Leistungsnachweis und Stützkurs. Alle fünf optionalen Bereiche sind in den drei geprüften Breiten offen.

**Empfehlung:** Nur fachliche Eingabewerte zur Entscheidung heranziehen. Hidden-Inputs und Formatfelder ausschliessen; beim Rich-Text-Editor den tatsächlichen Inhalt berücksichtigen. Nach der Korrektur sowohl leere als auch bereits ausgefüllte Abschnitte prüfen.

### B4 – Mittlere Priorität bei abweichenden Datumsformaten: Umstellung auf Datumseingabe leert vorhandene Werte

[jstemplate.js](moodle-database-preset/lektionsplaner-db-preset/jstemplate.js), Zeilen 153–164, setzt den Eingabetyp ohne Vorprüfung auf `date`. Im synthetischen Test wird ein gespeicherter Textwert `09.09.2026` beim Laden zu einem leeren Eingabewert; die berechnete Kalenderwoche wird ebenfalls geleert. Der Datensatz auf dem Server wird durch das Öffnen allein noch nicht verändert. Beim anschliessenden Speichern können Werte verloren gehen.

Die gelieferten CSVs mit aktuellem Schema enthalten ausschliesslich gültige ISO-Daten; für diese konkreten Werte tritt der Fehler nicht auf. Relevant wird er bei weiteren Altimporten oder Eingaben ohne die JavaScript-Erweiterung.

**Empfehlung:** Bestehende Werte vor der Typumstellung prüfen, unterstützte Datumsformate eindeutig umwandeln und sonst den Textwert mit einem verständlichen Hinweis erhalten.

### B5 – Mittlere Priorität: Eigene Zeitfenster-Menüs haben keinen zugänglichen Namen

In [addtemplate.html](moodle-database-preset/lektionsplaner-db-preset/addtemplate.html), erstmals Zeilen 51–54, steht die sichtbare Beschriftung «Zeitfenster» in einem `span`. Die sechs selbst erzeugten `select`-Elemente besitzen weder eine verknüpfte Beschriftung noch `aria-label` oder `aria-labelledby`. Der DOM-Test bestätigt sechs unbeschriftete Auswahlfelder.

**Empfehlung:** Eindeutige IDs und zugehörige `label`-Elemente verwenden, beispielsweise «Zeitfenster der 1. Lektion». Anschliessend Namen und Tastaturbedienung im tatsächlichen Moodle-Formular prüfen.

## Weitere Beobachtungen und offene Punkte

| Punkt | Einordnung und nächster Schritt |
| --- | --- |
| Lernziel-Satzstarter und TinyMCE | `setLearningGoalStarter()` bearbeitet eine Textarea oder ein direkt enthaltenes `contenteditable`-Element. Die tatsächliche Synchronisation mit dem Moodle-Editor und dessen asynchronem Start ist nicht geprüft. In Moodle neue und bestehende Einträge testen, einschliesslich bewusst leerer Lernziele; keinen bestätigten TinyMCE-Fehler aus dem lokalen Nachbau ableiten. |
| Erweiterte Suche | «Aktivitäten» in [asearchtemplate.html](moodle-database-preset/lektionsplaner-db-preset/asearchtemplate.html), Zeile 13, bezieht sich nur auf `lektion_1_aktivitaeten`. Die Beschriftung präzisieren oder die gewünschte Suche für alle Lektionen konzipieren. Dies betrifft diesen Filter, nicht pauschal die allgemeine Moodle-Suche. |
| Lokale App im neuen Repository | Die [App-README](README.md) verweist auf das nicht vorhandene `start-lektionsplaner.sh` und einen nicht mehr passenden Testpfad. `server.py` setzt `REPOSITORY_DIR` auf das Elternverzeichnis, hier `03-datenbanken/`; die dort erwarteten HTML-Quellverzeichnisse fehlen. Startanleitung und Quellpfade an diesen Ablageort anpassen. |
| Einstellungen und Rollen | Das Preset überträgt keine vollständige Nutzungskonfiguration. Wer Planungen erfassen und sehen darf, muss für diesen Lektionsplaner festgelegt und in Moodle geprüft werden; keine Rollenannahmen aus anderen Datenbanken übertragen. |
| Dateifeld und Medien | Ein Dateiname in einer CSV überträgt keinen Dateiinhalt. Datei hochladen, speichern, anzeigen und gegebenenfalls erneut exportieren/importieren: noch in Moodle zu prüfen. |

Die neue `/public`-Verzeichnisstruktur von Moodle 5.1 betrifft die Serverinstallation. Die geprüften Vorlagen enthalten keine PHP-Dateisystemintegration, die deswegen umgebaut werden müsste. Aus den [offiziellen Upgrade-Hinweisen](https://moodledev.io/general/releases/5.1) ergibt sich insbesondere kein Anlass, `/public` pauschal in bestehende Moodle-Links einzufügen. Die lokale Python-App bleibt eine separate Anwendung; ihr HTML-Export kann nicht als vollständige Datenbankaktivität importiert werden.

## Durchgeführte Prüfungen

| Prüffall | Status | Nachweis und Aussagegrenze |
| --- | --- | --- |
| ZIP-Lesbarkeit, erwartete Dateinamen, Übereinstimmung mit Quellordner | `bestanden` | Drei lesbare, identische ZIPs; siehe Struktur-JSON |
| XML-Wohlgeformtheit, eindeutige Felder, Vorlagenverweise | `bestanden` | 40 Felder; keine unbekannten Feldverweise; Formatabgleich mit Moodle v5.1.0 |
| Aktuelle CSV-Struktur, Datums- und Auswahlwerte | `bestanden` | Drei CSVs mit 40 vollständigen Spalten; keine ungültigen Datums- oder Auswahlwerte |
| Empfohlene CSV frei von Sicherungsplatzhaltern | `fehlgeschlagen` | 21 betroffene Zellen, B1 |
| MBZ entspricht aktuellem Preset | `fehlgeschlagen` | 37 statt 40 Felder, 14 Typabweichungen, B2 |
| Kalenderwoche, Zeitfenster und Themenauswahl | `bestanden` | Synthetisch: `2026-09-09` ergibt `KW 37`; Zeitfenster setzt `07:40` und `08:25`; Themenbutton setzt Auswahl und `aria-pressed` |
| Optionale Formularabschnitte bleiben leer geschlossen | `fehlgeschlagen` | Fünf leere Bereiche werden geöffnet, B3 |
| Nicht-ISO-Datum bleibt beim Bearbeiten erhalten | `fehlgeschlagen` | Synthetischer Wert `09.09.2026` wird geleert, B4 |
| Zugängliche Namen der sechs Zeitfenster-Menüs | `fehlgeschlagen` | Keine zugeordneten Labels oder ARIA-Namen, B5 |
| Eingabe-, Listen- und Einzelansicht bei 320/390/1440 Pixel | `bestanden` | In den geprüften synthetischen Fällen kein horizontaler Seitenüberlauf; Liste mit drei Karten. Kein Nachweis für echtes Theme, lange Inhalte oder Editoroberfläche |
| Ausblenden leerer Anzeigeabschnitte | `bestanden` | Synthetische Einzelansicht zeigt belegte Lektionen 1 und 6; leere Lektionen werden ausgeblendet |
| Vorhandene Tests der lokalen App | `bestanden` | 7 Tests, siehe Befehl unten; temporäre Testdaten, keine Moodle-Integration |
| Tatsächlicher ZIP-/CSV-Import und MBZ-Restore in Moodle 5.1 | `nicht_geprueft` | Keine Testinstanz verfügbar |
| TinyMCE, Dateimanager, Speicherung, Suche, Rollen und Links in Moodle | `nicht_geprueft` | Erfordert echte Zielumgebung und passende Testkonten |

Ausgeführter App-Testbefehl aus dem Repository-Hauptverzeichnis:

```bash
python3 -B -m unittest discover -s 03-datenbanken/Lektionsplaner/tests -v
```

Ergebnis: `Ran 7 tests … OK`. Die erste Ausführung in der Sandbox konnte drei lokale HTTP-Tests wegen gesperrter Sockets nicht starten; die anschliessend erlaubte Ausführung bestand alle sieben Tests. Auch der Browser benötigte die Freigabe für lokale Sockets. Diese Umgebungsbeschränkungen wurden nicht als Produktfehler gewertet.

## Empfohlener Weg zum belegten Einsatz

1. Datenbasis mit gewünschtem Eintragsstand bestimmen, B1 beheben und den zugehörigen CSV-Dialekt in der Importanleitung festhalten.
2. Formularfehler B3–B5 korrigieren; ZIP aus dem dann geprüften Quellstand neu erzeugen. Die ältere MBZ eindeutig kennzeichnen oder aus einer getesteten Aktivität neu erstellen.
3. In einer leeren Moodle-5.1-Testaktivität das konkrete ZIP importieren. Patchstand und Theme protokollieren, 40 Felder sowie übernommene Einstellungen kontrollieren.
4. Einen synthetischen Eintrag mit allen sechs Lektionen, Umlauten, HTML, mehreren Themen, Links und einer Datei erstellen, speichern und erneut bearbeiten. Leere optionale Bereiche und den Lernziel-Satzstarter mit dem tatsächlichen Texteditor prüfen.
5. Den ausgewählten, korrigierten CSV-Stand einmal importieren; Sollzahl der Einträge, Links und Feldwerte vergleichen. Wiederholte CSV-Importe legen neue Datensätze an und sind kein Aktualisierungsverfahren, wie der [Moodle-CSV-Importer](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/local/importer/csv_entries_importer.php) zeigt.
6. Listen-, Einzel- und Suchansicht auf Desktop und Mobilgerät sowie die vorgesehenen Lehrpersonen- und Lernendenrechte prüfen. Erst mit diesen Nachweisen den Stand als in dieser Moodle-Umgebung getestet bezeichnen.
