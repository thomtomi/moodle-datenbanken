---
title: "Spezifikation Lernprodukt Mikroskopieren"
date: 2026-09-10
---

# Spezifikation Lernprodukt Mikroskopieren

## Zweck und Nutzung

Die Datenbank ist eine aktive, moderierte Bildergalerie für Lernprodukte zum Mikroskopieren. Lernende laden eine scharfe Aufnahme ihres Präparats hoch und vergleichen nach der Freigabe die Ergebnisse der Klasse. Lehrpersonen prüfen und geben Beiträge frei.

Die Freigabe vor der gemeinsamen Sichtbarkeit ist eine bewusste Sicherheitsannahme der Lieferung. Moodle-Version, Theme, Gruppenmodus, Dateigrösse, erlaubte Dateitypen, Virenschutz, Rollenmodell, die konkrete Mikroskopieranleitung und eine Testaktivität sind offen.

Der ursprüngliche Auftrag nennt Zweiergruppen. Die Gruppeneinstellung wird nicht durch ein Datenbank-Preset übertragen und muss in Moodle separat konfiguriert werden. Ebenso enthält das Preset keine Anleitung-PDF; die Lehrperson stellt sie in der Aktivitätsbeschreibung oder als separate Moodle-Ressource bereit.

## Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde herangezogen. Die [Lernendeninstruktion](instruktion.html) verwendet in dieser Reihenfolge **Einführung**, **Lernziele**, **Auftrag** und **Reflexion & Auswertung**. Diese Abschnitte unterstützen die praktische Arbeit, den Upload und das Vergleichen der Präparate. Aufwand, Bewertung, Termin und Literatur sind nicht vorgegeben und deshalb nicht ergänzt.

Die Instruktion gehört in die Aktivitätsbeschreibung vor der Datenbankansicht. Die Darstellung der `[fa-…]`-Kürzel ist in der Zielinstanz zu prüfen; der Inhalt bleibt auch ohne Icons verständlich.

## Datenmodell

Feldnamen, Typen, Pflichtwerte und Optionen entsprechen dem Rohpreset `02-rohdaten/Mikroskopieren Lernprodukt hier hochladen!-preset-20260910_1013.zip`. Nur die Feldbeschreibungen wurden verständlicher formuliert.

| Feld | Typ | Zweck | Pflicht | Beispiel |
| --- | --- | --- | --- | --- |
| Präparat | Text | Eindeutige Bezeichnung des Präparats | ja | Zwiebelhaut |
| Bild-Videodatei | Bild | Scharfe Aufnahme des Präparats | ja | zwiebelhaut-400x.jpg |

Das Bildfeld ist im Rohpreset als Moodle-Typ **picture** definiert. Ob die konkrete Zielinstanz zusätzlich Videodateien unterstützt, ist offen und vor einem entsprechenden Auftrag zu prüfen. Die Feldbezeichnung bleibt wegen der Datenübernahme unverändert.

## Ansichten und Gestaltung

- **Liste:** Responsive Galerie mit Präparatname, Aufnahme, rollenabhängigem Aktionsmenü und Detailansicht.
- **Einzelansicht:** Aufnahme in grösserer Ansicht sowie Moodle-eigene Angaben zur einreichenden Person und letzten Änderung.
- **Suche:** Filter über den Präparatnamen.
- **Eingabe:** Beide Pflichtfelder genau einmal mit klaren Hinweisen zu Aufnahme und Datenschutz.

Die Gestaltung übernimmt die Palette und Kartenstruktur des Lektionsplaners: dunkles Petrol, Gold als Akzent, helle Flächen und sichtbarer Tastaturfokus. Das CSS ist auf `.ml-db` begrenzt, enthält Regeln für Galerie und Mobilansicht und lädt keine externen Ressourcen. Das JavaScript-Template ist bewusst leer.

Die Feldplatzhalter sowie `##moreurl##`, `##actionsmenu##`, `##user##` und `##timemodified##` sind dokumentierte Moodle-Datenbanktags. `##actionsmenu##` zeigt nur die Aktionen der jeweiligen Rolle. Quelle: [MoodleDocs: Datenbankvorlagen](https://docs.moodle.org/502/de/Datenbankvorlagen).

## Rollen, Freigabe und Sicherheit

| Rolle | Vorgabe |
| --- | --- |
| Lernende | Beiträge lesen und suchen; eigene Beiträge erfassen und nur gemäss der festgelegten Moodle-Berechtigung bearbeiten. Keine Freigabe fremder Beiträge. |
| Lehrpersonen | Beiträge prüfen, freigeben, bearbeiten oder bei Bedarf löschen; Aufnahme, Datenschutz und Darstellung kontrollieren. |

Die Rollen werden in Moodle gesetzt; die Vorlage bietet keinen Zugriffsschutz. Vor der Freigabe sind mindestens diese Prüfpunkte erforderlich:

1. Als Lernende:r einen synthetischen Beitrag erstellen und als Lehrperson freigeben. Ein zweites Lernenden-Testkonto darf ihn erst danach in der Galerie sehen.
2. Erlaubte Bildformate, Dateigrösse und den Virenschutz in Moodle bzw. auf dem Server festlegen und prüfen.
3. Nur scharfe, fachlich passende Aufnahmen ohne Personen, Gesichter, Namen oder andere personenbezogene Angaben freigeben.
4. Unzulässige Aktionen in der Lernendenrolle prüfen, besonders das Freigeben, Bearbeiten und Löschen fremder Beiträge.

Die Vorlage bindet weder Skripte noch externe Ressourcen ein. Die sichere Verarbeitung der Uploads und Feldwerte bleibt Aufgabe von Moodle und der Instanzkonfiguration.

## Übertragung und Abnahme

`ausgabe/mikroskopieren-lernprodukt-preset.zip` enthält Struktur, Felder, Vorlagen und Einstellungen, aber keine Datensätze oder Bilddateien. Nach dem Import die Aktivitätsbeschreibung mit [instruktion.html](instruktion.html) ergänzen und die separate Mikroskopieranleitung verlinken oder bereitstellen.

Lokal sind XML, Feldsignatur, bekannte Platzhalter, Freigabe-Einstellung, leeres JavaScript-Template, fehlende externe Ressourcen und ZIP-Struktur zu prüfen. In Moodle bleiben Import, Gruppenmodus, Rollen, Freigabe, Bild-Upload, Medienanzeige und mobile Bedienung offen.
