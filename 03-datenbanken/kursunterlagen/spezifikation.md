---
title: "Spezifikation Kursunterlagen"
date: 2026-09-10
---

# Spezifikation Kursunterlagen

## Zweck und Nutzung

Die Datenbank ist eine Materialsammlung für Lernende. Sie finden Arbeitsblätter, Skripte, Anleitungen und weitere Kursunterlagen über eine Kartenübersicht und die erweiterte Suche. Lernende erfassen, bearbeiten oder löschen keine Einträge. Lehrpersonen pflegen die Einträge und stellen mindestens eine Datei oder einen Link bereit.

Die fachliche Einordnung bleibt jene des bereitgestellten Rohpresets: Grundlagen, Cytologie, Asexuelle & Sexuelle Reproduktion, Reproduktionsmedizin, Ethik und Skript. Der konkrete Kursname, Moodle-Version, Theme, Rollenmodell und eine Testaktivität sind offen.

## Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde herangezogen. Die fertige [Lernendeninstruktion](instruktion.html) verwendet in dieser Reihenfolge **Einführung**, **Lernziel** und **Auftrag**. Diese Abschnitte erklären Nutzen, beobachtbare Fähigkeit und Vorgehen beim Finden von Unterlagen. Aufwand, Bewertung, Termin, Reflexion und Literatur sind nicht Bestandteil der vorliegenden reinen Materialsammlung und werden deshalb nicht ergänzt.

Die Instruktion gehört in die Aktivitätsbeschreibung vor der Datenbankansicht. Die Darstellung der `[fa-…]`-Kürzel ist in der Zielinstanz zu prüfen; sie muss für die Verständlichkeit nicht vorausgesetzt werden.

## Datenmodell

Die sieben Feldnamen, Feldtypen, Pflichtwerte und Auswahloptionen entsprechen dem Rohpreset `02-rohdaten/Unterlagen zum Kurs-preset-20260910_0753.zip`. Feldbeschreibungen wurden sprachlich vereinheitlicht. Es werden keine Datensätze oder Medien mitgeliefert.

| Feld | Typ | Zweck | Pflicht | Beispiel |
| --- | --- | --- | --- | --- |
| Titel | Text | Eindeutige Bezeichnung | ja | Zellteilung: Aufgabenblatt |
| Beschreibung | Textbereich | Kurzüberblick zum Inhalt | nein | Übungsaufgaben zur Mitose |
| Datei Hochladen | Datei | Material als Datei | nein | zellteilung-aufgaben.pdf |
| Link | URL | Externes oder kursinternes Material | nein | https://example.org/material |
| Verlag | Text | Herausgeber:in oder Verlag | nein | Beispielverlag |
| Fachbereich | Mehrfachauswahl | Fachliche Zuordnung | ja | Cytologie |
| Typ | Auswahl per Radiobutton | Art der Unterlage | ja | Aufgabe |

Technisch erzwingt Moodle nicht, dass mindestens eines der beiden optionalen Felder **Datei Hochladen** oder **Link** gefüllt ist. Dies ist daher eine verbindliche redaktionelle Prüfung für Lehrpersonen vor der Freigabe eines Eintrags.

## Ansichten und Gestaltung

- **Liste:** Kompakte responsive Karten mit **Typ**, **Titel** und einem Link, sofern einer hinterlegt ist. Der Titel führt zur Detailansicht; Fachbereich, Beschreibung, Datei und Herausgeber:in sind nur dort sichtbar.
- **Einzelansicht:** Vollständige Beschreibung, Datei und Link sowie Herausgeber:in.
- **Suche:** Filter über Titel, Fachbereich, Typ und Herausgeber:in.
- **Eingabe:** Ausschliesslich für Lehrpersonen vorgesehen; jedes Feld kommt genau einmal vor.

Die Gestaltung übernimmt die zurückhaltende Palette und Kartenstruktur des Lektionsplaners: dunkles Petrol, Gold als Akzent, helle Flächen und hohe Lesbarkeit. Das CSS ist vollständig auf `.ku-db` begrenzt, nutzt keine externen Schriften, Bilder oder Abhängigkeiten und enthält mobile Regeln. Das JavaScript-Template ist bewusst leer.

Die verwendeten Feldplatzhalter sowie `##moreurl##` und `##actionsmenu##` sind dokumentierte Moodle-Datenbanktags; `##actionsmenu##` zeigt nur die für die jeweilige Rolle verfügbaren Aktionen. Quelle: [MoodleDocs: Datenbankvorlagen](https://docs.moodle.org/502/de/Datenbankvorlagen). Damit bleibt die Vorlage auf Moodle-eigene Template-Funktionen beschränkt und vermeidet versionsanfällige DOM-Manipulationen.

## Berechtigungen und Sicherheit

Die Sichtbarkeit für Lernende wird in Moodle über Rollen und Fähigkeiten eingerichtet, nicht mit CSS oder der Vorlage:

| Rolle | Erforderliche Einstellung |
| --- | --- |
| Lernende | Einträge anzeigen und suchen; **keine** Fähigkeit zum Hinzufügen, Bearbeiten oder Löschen eigener Einträge |
| Lehrpersonen | Einträge hinzufügen, bearbeiten und löschen; Dateien nur aus vertrauenswürdigen Quellen bereitstellen |

Vor der Freigabe muss eine Lehrperson einen Eintrag als Lernende:r testen. Insbesondere sind Datei- und Linkzugriff, fehlende Bearbeitungsaktionen und die Sichtbarkeit der Aktivität zu prüfen. Die Vorlage bindet keine Skripte, externen Ressourcen oder benutzergesteuerten HTML-/JavaScript-Code ein. Feldwerte werden nicht durch eigenes JavaScript verarbeitet oder zu neuen HTML-Attributen zusammengesetzt; die Ausgabesicherheit der Moodle-Feldtypen bleibt bei Moodle.

## Übertragung und Abnahme

Das ZIP unter `ausgabe/kursunterlagen-preset.zip` enthält die Preset-Struktur, Felder und Vorlagen, jedoch keine Datensätze und keine Medien. Die Aktivitätsbeschreibung muss nach dem Import aus [instruktion.html](instruktion.html) in Moodle eingefügt oder gegen die übernommene Beschreibung geprüft werden.

Lokal zu prüfen sind XML, Feldzuordnung, alle Platzhalter, das Fehlen ausführbaren Codes und externer Ressourcen, die ZIP-Struktur sowie die unveränderte Feldsignatur gegenüber dem Rohpreset. In Moodle offen sind Import, Darstellung im Zieltheme, Suche, Datei-/Linkzugriff und die Rollenprüfung.
