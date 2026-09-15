---
title: "Spezifikation Sitzplan"
date: 2026-09-14
---

# Spezifikation Sitzplan

## Zweck und Umfang

Organisationshilfe für Lehrpersonen: Sitzplätze mit Namen und optionalen Fotos der Lernenden darstellen. Ein Datensatz bildet ein ganzes Schulzimmer ab; weitere Datensätze erlauben verschiedene Klassen, Zimmer oder Planstände. Ein pädagogischer Abgabeauftrag an Lernende oder eine Bewertung ist nicht vorgesehen.

Die Raumaufteilung ist je Eintrag wählbar: 1 bis 8 **Querreihen** mit je 1 bis 16 Einzeltischen; jede Reihe kann unterschiedlich lang sein und beginnt links. Ohne Auswahl gelten drei Reihen mit je sieben Tischen. Reihe 1 liegt am Pult, die höchste gewählte Reihe an der Rückwand. Plätze laufen von links nach rechts aus Lehrpersonensicht. In der Darstellung steht die hinterste Reihe oben, Reihe 1 unten, danach folgen Blickrichtung, mittiges Lehrer:innen-Pult und Wandtafel. So liegen beide vorderen Raumelemente unten auf dem Plan, wenn die Lehrperson in die Klasse blickt. Namen und Fotos werden nicht rotiert oder gespiegelt.

## Nutzung und Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde gelesen. Die [Instruktion](instruktion.html) richtet sich hier an Lehrpersonen und enthält **Einführung** sowie **Auftrag** mit dem Ergebnis «gespeicherter Sitzplan». Lernziele, Aufwand, Leistungsnachweis, Termin und Reflexion entfallen, weil es um Raumorganisation geht. Literatur entfällt in der Bedienungsanleitung; technische Quellen stehen unten. Überschriften ohne Icon-Kürzel vermeiden eine Abhängigkeit von einem Moodle-Filter; die h3-Struktur bleibt erhalten.

Lehrpersonen erfassen, lesen und bearbeiten Pläne. Zugriff der Lernenden ist nicht beauftragt und zunächst nicht vorgesehen. Kommentare, RSS, Mindestanzahl an Beiträgen und Freigabeverfahren werden nicht benötigt. Gruppenmodus und Abschlussbedingungen: keine vorgesehen; die tatsächlichen Aktivitätseinstellungen in Moodle kontrollieren. Eine Raum- oder Klassenbezeichnung ist kein Zugriffsschutz.

## Zielumgebung und Datenmodell

Referenz für Felder und Paketstruktur: Moodle **v5.1.0**, keine Zusicherung für eine bereits geprüfte Zielinstanz. Tatsächliche Moodle-Version, Patchstand, Theme, Testaktivität und Rollenkonfiguration: **offen**. Benötigt werden nur die Standardfeldtypen Text und Bild.

[Vollständige Feldliste](felder.md): 267 Felder. `Plan` ist Text und Pflicht; `Raum` ist optionaler Text. `Reihen` und `rR_tische` sind optionale Auswahlfelder für die Raumaufteilung (leer entspricht 3 beziehungsweise 7). Für jeden möglichen Platz existieren `rR_pP_name` als Text und `rR_pP_foto` als Bild, mit R = 1–8 und P = 1–16. Alle Platzfelder sind optional, damit leere Plätze und reine Namenspläne möglich sind. Textfelder erzwingen keine Auswahl aus Kurskonten. Ein Namensfeld referenziert nicht das Moodle-Profil der Person.

Fotoparameter: Einzelansicht-Breite 160 px, proportionale Höhe; Thumbnailbreite 160 px, proportionale Höhe; maximal 2 MiB. Die Vorschaugrössen werden von CSS begrenzt, das Bild wird vollständig eingepasst. Das Moodle-Bildfeld liefert Upload und Alternativtext. Eine fachliche Regel (nicht technisch erzwungen): Foto nur am Platz des zugehörigen Namens erfassen, bei Umplatzierungen beide Felder pflegen. Es findet keine Gesichtserkennung statt.

## Ansichten und Umsetzung

Die Einzelansicht enthält 128 dauerhaft vorhandene mögliche Tische in einem CSS-Raster. Das Sitzplan-JavaScript zeigt anhand der gespeicherten Raumaufteilung nur die gewählten Reihen und Plätze; ohne oder mit ungültigem JavaScript bleibt bewusst die vollständige Ansicht mit Hinweis sichtbar. Leere Bildcontainer verschwinden mit `:empty`; Namen sind unabhängig von Fotos sichtbar. Ein leerer Name wird mit «Unbesetzt» dargestellt; zu einem unbesetzten Platz gehört auch ein leeres Foto. Die Reihenfolge ist im HTML und CSS gleich. Auf kleinen Bildschirmen bleibt das Raster im benannten, fokussierbaren Scrollbereich erhalten, damit kein falscher Sitzplan durch Umbruch entsteht.

In der Listenansicht stehen nur Planname, Raum, rollenabhängiges Aktionsmenü und der Link zur Einzelansicht. Die Eingabe gruppiert Plätze nach Reihen; jedes Feld ist genau einmal vorhanden. Native `details` halten optionale Fotofelder übersichtlich. Moodle-eigene Uploadsteuerung und Beschriftungen bleiben erhalten. Die erweiterte Suche enthält nur Plan und Raum. Drucken erfolgt über den Browser; Druckregeln betreffen nur `.sp-db`.

Gestaltung: Petrol, Gold und helle Flächen wie bei den Kursunterlagen und dem Lektionsplaner. Jeder CSS-Selektor ist auf `.sp-db` begrenzt. Das JavaScript liest ausschliesslich die Moodle-Ausgabe der Raumaufteilungsfelder und blendet vorhandene Elemente ein oder aus; es verändert weder Namen, Bilder, Uploads noch Feldwerte. Der Sitzplan verwendet keine externen Ressourcen, selbst erzeugten Feld-URLs, dynamischen HTML-Code oder Abhängigkeiten von Bootstrap-/Theme-Klassen. Standardbrowserfunktionen übernehmen Aufklappen, Scrollen und Drucken. Moodle kann für seine eigenen Uploadfelder JavaScript benötigen.

## Zugriffsrechte und Übertragung

Die Aktivität zunächst für Lernende verborgen erstellen und anschliessend ausdrücklich nur berechtigten Lehrpersonen zugänglich machen. `mod/data:viewentry` und `mod/data:writeentry` sind in Moodle standardmässig auch Lernenden erlaubt; deshalb die Aktivitätsrechte wie in der [Einrichtung](README.md) beschrieben anpassen und mit getrennten Konten testen. Das Preset setzt keine Rollen und sichert Namen/Fotos nicht durch die Darstellung ab.

Keine Namen oder Bilder aus vorhandenen Kursen werden übernommen; alle lokalen Tests sind synthetisch. Das Preset enthält weder Datensätze noch Fotos. Ein späterer Import von Daten, Kontoabgleich und automatische Sitzplatzwechsel gehören nicht zum Umfang.

## Abnahme

Lokal nachweisen: 267 konsistente Felder, 128 eindeutige Platzzuordnungen, jedes Feld einmal im Eingabeformular und Sitzplan; korrekte Darstellung für Standard (3 × 7), eine, unterschiedlich lange und maximale Reihen (8 × 16); Orientierung mit Pult und Tafel unten, links/rechts unvertauscht; leere Namen/Fotos, lange Texte und mehrere Listen-Einträge; mobile Scrollbarkeit, sichtbarer Fokus, Druck-CSS, gültige HTML-Zusammensetzung; lesbares und reproduzierbares ZIP. Kein Personeninhalt in HTML-Attributen oder JavaScript; CSS bleibt im Aktivitätscontainer.

In Moodle offen: Import aller Felder und Einstellungen, Erstellen/Bearbeiten/Speichern, Pflichtfeld, Aus- und Einblenden der Raumaufteilung, 128 echte Dateiverwaltungen samt Initialisierung in geschlossenen Fotoabschnitten, Bilder mit Alternativtext, Entfernen und Ersetzen von Fotos, Suche und Sortierung, Namens-/Foto-Zuordnung nach Neuladen, Zugriff auf Einträge und direkte Bild-URLs mit passenden beziehungsweise unberechtigten Konten sowie Theme-/Mobil-/Druckansicht. Nach Upgrades dieselben relevanten Fälle wiederholen; zukünftige Versionen lassen sich nicht pauschal garantieren.

## Technische Quellen

Am 2026-09-12 geprüft:

- [Moodle 5.1: Datenbankvorlagen](https://docs.moodle.org/501/en/Database_templates): Feldplatzhalter, `##moreurl##`, `##actionsmenu##`.
- [Moodle 5.1: Building Database](https://docs.moodle.org/501/en/Building_Database): Text-/Bildfelder, Pflichtangaben und Preset-Übertragung.
- [Moodle v5.1.0: manager.php](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/classes/manager.php): zehn Vorlagendateien gemäss `TEMPLATES_LIST`, ergänzt durch `preset.xml`. Gleiche Paketstruktur wie die lokalen Originalexporte in `02-rohdaten/`.
- [Moodle v5.1.0: picture/field.class.php](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/field/picture/field.class.php): ein Bild je Feld, interner Upload, Alternativtext, Parameter 1–5, leere Ausgabe ohne Bild und Moodle-generierte Bildlinks.
- [Moodle v5.1.0: db/access.php](https://github.com/moodle/moodle/blob/v5.1.0/public/mod/data/db/access.php): Fähigkeiten zum Lesen und Erfassen sowie ihre Standardrollen.
