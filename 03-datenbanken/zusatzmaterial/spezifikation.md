---
title: "Spezifikation Zusatzmaterial"
date: 2026-09-10
---

# Spezifikation Zusatzmaterial

## Zweck und Nutzung

Die Datenbank ist eine aktive, moderierte Materialbörse für Lernende. Sie suchen vorhandene Unterlagen und reichen eigene fachlich passende Beiträge als Datei oder Link ein. Lehrpersonen prüfen und geben Beiträge frei. Diese Freigabe ist eine deklarierte Sicherheitsannahme für die vorliegende Lieferung: Neue Beiträge sind erst nach der Prüfung in der gemeinsamen Sammlung sichtbar.

Moodle-Version, Theme, Dateigrössenlimit, erlaubte Dateitypen, Virenschutz, Rollenmodell und Testaktivität sind offen. Diese Angaben müssen vor dem produktiven Einsatz in der Zielinstanz festgelegt und geprüft werden.

## Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde herangezogen. Die [Lernendeninstruktion](instruktion.html) verwendet in dieser Reihenfolge **Einführung**, **Lernziele** und **Auftrag**. Sie erklärt den Nutzen der Sammlung, das Beurteilen und Dokumentieren von Material sowie die konkreten Qualitätsschritte für einen Beitrag. Aufwand, Bewertung, Termin, Reflexion und Literatur sind nicht vorgegeben und deshalb nicht ergänzt.

Die Instruktion gehört in die Aktivitätsbeschreibung vor der Datenbankansicht. Die `[fa-…]`-Kürzel sind in der Zielinstanz zu prüfen; die Aussage bleibt auch ohne Icon verständlich.

## Datenmodell

Feldnamen, Typen, Pflichtwerte und Optionen entsprechen dem Rohpreset `02-rohdaten/Zusatzmaterial-preset-20260910_0841.zip`. Nur Feldbeschreibungen wurden verständlicher und inklusiv formuliert. Die Rohdaten und alle Felder bleiben erhalten.

| Feld | Typ | Zweck | Pflicht | Beispiel |
| --- | --- | --- | --- | --- |
| Titel | Text | Aussagekräftiger Beitragstitel | nein | Erklärvideo zur Meiose |
| Beschreibung | Textbereich | Inhalt und Nutzen für den Kurs | nein | Visualisiert die Phasen der Meiose. |
| Link | URL | Materialquelle im Web oder Kurs | nein | https://example.org/meiose |
| Datei | Datei | Datei zum Material | nein | meiose-ueberblick.pdf |
| Relevanz | Auswahl per Radiobutton | Einordnung für das Modul | nein | zur Vertiefung |
| Autor | Text | Autor:in des Inhalts | nein | Beispielautor:in |
| Erscheinungsjahr | Zahl | Jahr des Inhalts | nein | 2025 |

Das bestehende Feldmodell erzwingt weder Pflichtangaben noch mindestens eine Datei oder einen Link. Die [Instruktion](instruktion.html) macht diese Qualitätsanforderung sichtbar; die Lehrperson prüft sie vor der Freigabe. Eine Änderung der Feld-Pflichtwerte oder ein eigenes Validierungsskript sind nicht Teil dieses Auftrags.

## Ansichten und Gestaltung

- **Liste:** Responsive Karten mit Relevanz, Titel, Autor:in, Jahr, Kurzbeschreibung, Datei-/Link-Schaltflächen und Detailansicht.
- **Einzelansicht:** Vollständiger Beitrag, Datei und Link sowie Moodle-eigene Angaben zur einreichenden Person und letzten Änderung.
- **Suche:** Filter über Titel, Relevanz, Autor:in, Erscheinungsjahr und Beschreibung.
- **Eingabe:** Alle sieben Felder werden einmal dargestellt; der Ablauf erinnert an Quelle, Datei oder Link und die spätere Prüfung.

Die Gestaltung übernimmt die Palette und Kartenstruktur des Lektionsplaners und der Kursunterlagen: dunkles Petrol, Gold als Akzent, helle Flächen und gut sichtbarer Tastaturfokus. Das CSS ist auf `.zm-db` begrenzt, enthält mobile Regeln und lädt keine externen Ressourcen. Das JavaScript-Template ist absichtlich leer.

Die Feldplatzhalter sowie `##moreurl##`, `##actionsmenu##`, `##user##` und `##timemodified##` sind dokumentierte Moodle-Datenbanktags. `##actionsmenu##` bietet nur die zur Rolle passenden Aktionen an. Quelle: [MoodleDocs: Datenbankvorlagen](https://docs.moodle.org/502/de/Datenbankvorlagen).

## Rollen, Freigabe und Sicherheit

| Rolle | Vorgabe |
| --- | --- |
| Lernende | Beiträge lesen und suchen; eigene Beiträge erfassen und nur gemäss der festgelegten Moodle-Berechtigung bearbeiten. Keine Freigabe fremder Beiträge. |
| Lehrpersonen | Beiträge prüfen, freigeben, bearbeiten oder bei Bedarf löschen; Datei- und Linkzugriffe sowie Quellenangaben kontrollieren. |

Die Rollen müssen direkt in Moodle gesetzt werden; die Vorlage ist kein Zugriffsschutz. Vor der Freigabe sind mindestens diese Prüfpunkte erforderlich:

1. Als Lernende:r einen synthetischen Beitrag mit Datei und Link erstellen und prüfen, dass er erst nach Lehrpersonenfreigabe für andere Lernende sichtbar ist.
2. Unzulässige Aktionen in der Lernendenrolle prüfen, besonders das Freigeben, Bearbeiten und Löschen fremder Beiträge.
3. Zulässige Dateitypen, Dateigrösse und den Virenschutz in Moodle bzw. auf dem Server festlegen. Dateien und Links auf Schadsoftware, Urheberrecht, personenbezogene Daten und tatsächlichen Zugriff prüfen.
4. Nur Beiträge freigeben, die Titel, Nutzen, Relevanz, Quelle und mindestens eine funktionierende Datei oder einen funktionierenden Link enthalten.

Die Vorlage bindet keine Skripte, externen Ressourcen oder eigenen HTML-/JavaScript-Code aus Eingaben ein. Die sichere Speicherung und Ausgabe der Moodle-Feldwerte bleibt Aufgabe der Moodle-Feldtypen und der Instanzkonfiguration.

## Übertragung und Abnahme

`ausgabe/zusatzmaterial-preset.zip` enthält Struktur, Felder, Vorlagen und die moderierte Einstellung, aber keine Datensätze oder Dateien. Nach dem Import die Aktivitätsbeschreibung mit [instruktion.html](instruktion.html) ergänzen oder die übernommene Kurzbeschreibung gegen die Instruktion prüfen.

Lokal sind XML, Feldsignatur, bekannte Platzhalter, leeres JavaScript-Template, fehlende externe Ressourcen, Freigabe-Einstellung und ZIP-Struktur zu prüfen. Ein Moodle-Import sowie der Rollen-, Datei-, Link- und Freigabeablauf bleiben bis zu einem Test in der Zielinstanz offen.
