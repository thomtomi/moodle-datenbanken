---
title: "Spezifikation Kursredaktions-Checkliste"
date: 2026-09-14
---

# Spezifikation der Kursredaktions-Checkliste

## Zweck und Nutzung

Die Datenbank dokumentiert die Funktionspruefung eines Moodle-Kurses vor oder waehrend der Kursredaktion. Ein Eintrag bildet eine vollstaendige Pruefung eines Kurses ab. Das Redaktionsteam erfasst die Ergebnisse strukturiert und exportiert sie bei Bedarf als CSV. Die exportierten Daten dienen ausschliesslich als Grundlage fuer spaeter separat erstellte E-Mail-Entwuerfe an die zustaendigen Lehrpersonen.

Die Aktivitaet speichert keine Namen oder E-Mail-Adressen von Lehrpersonen und versendet keine Nachrichten. Sie prueft keine Kurse automatisch; die Statuswerte beruhen auf einer manuellen Kontrolle durch das Redaktionsteam.

## Zielumgebung und Rollen

- Moodle 5.0.4, Kernaktivitaet `mod_data`; Theme und konkrete Testinstanz: offen.
- Alle Lehrpersonen duerfen die Eintraege einsehen.
- Ausschliesslich das Redaktionsteam darf Eintraege erstellen, bearbeiten, loeschen und als CSV exportieren.
- Diese Berechtigungen werden in Moodle ueber Rollen und Faehigkeiten eingerichtet. Das Preset und seine Vorlagen sichern keine Zugriffe ab.

## Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde herangezogen. Die [Instruktion](instruktion.html) verwendet die Abschnitte **Einfuehrung** und **Auftrag**: Die Datenbank ist eine interne Arbeitsgrundlage und keine Lernaufgabe. Lernziele, Aufwand, Bewertung, Termin, Reflexion und Literatur sind deshalb nicht passend und werden nicht verwendet.

Die Instruktion wird als Aktivitaetsbeschreibung im Preset eingebettet und liegt zusaetzlich als HTML-Datei vor. Bei einem Import ist ihre Uebernahme zu pruefen.

## Datenmodell

Jedes Statusfeld verwendet genau diese Optionen: `Erfuellt`, `Korrektur noetig`, `Nicht anwendbar`, `Nicht geprueft`.

| Reihenfolge | Feld                                | Moodle-Typ  | Pflicht | Zweck und Regel                                                                                                                                                     |
| ----------: | ----------------------------------- | ----------- | :-----: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|           1 | Kursname                            | Text        |   Ja    | Eindeutige, verstaendliche Bezeichnung des geprueften Kurses.                                                                                                       |
|           2 | Moodle-Kurslink                     | URL         |   Ja    | Direkter Link zum Kurs. Die Instanzadresse wird als Eintragswert, nicht im Preset hinterlegt.                                                                       |
|           3 | Pruefdatum                          | Text        |   Ja    | Datum im ISO-Format `YYYY-MM-DD`.                                                                                                                                   |
|           4 | Klassen und Berechtigungen          | Auswahl     |   Ja    | `Erfuellt`, wenn Klassen eingetragen sind oder die Lehrperson die benoetigten Manager:innen-Rechte besitzt.                                                         |
|           5 | Rollenbezeichnungen                 | Auswahl     |   Ja    | Prueft: Trainer/innen = Lehrperson(en), Trainer/in ohne Bearbeitungsrecht = Leitung/Team, Teilnehmer/in = Lernende.                                                 |
|           6 | Willkommensnachricht                | Auswahl     |   Ja    | Prueft, ob im Forum «Nachrichten der Lehrperson(-en)» eine einladungsbereite Nachricht vorhanden ist.                                                               |
|           7 | Termine in der Planung              | Auswahl     |   Ja    | Prueft die Anpassung aller Planungstermine an das neue Schuljahr.                                                                                                   |
|           8 | Externe Links                       | Auswahl     |   Ja    | Prueft alle externen Links. Bei `Korrektur noetig` muss das Feld «Nicht funktionierende externe Links» ausgefuellt werden.                                          |
|           9 | Abgabefenster                       | Auswahl     |   Ja    | Prueft Beginn, Ende und zeitliche Geltung vorhandener Abgabefenster. Ohne Abgabefenster: `Nicht anwendbar`.                                                         |
|          10 | Abgabetermine                       | Auswahl     |   Ja    | Prueft die im Kurs erfassten Abgabetermine. Ohne Abgabetermine: `Nicht anwendbar`.                                                                                  |
|          11 | Kursstruktur und Kursfuehrung       | Auswahl     |   Ja    | Prueft, ob der Kurs verstaendlich strukturiert ist und durch den Kurs fuehrt. Bei `Korrektur noetig` soll die spaetere Rueckmeldung einen Beratungstermin anbieten. |
|          12 | Nicht funktionierende externe Links | Textbereich |  Nein   | Pro Befund URL und kurze Fehlerbeschreibung, beispielsweise `https://example.org/material - Seite nicht gefunden`.                                                  |
|          13 | Besondere Hinweise                  | Textbereich |  Nein   | Weitere fuer die Rueckmeldung relevante Beobachtungen ohne Statusbewertung.                                                                                         |

Die Pflichtfelder erzwingen nur das Vorhandensein eines Werts. Die fachliche Bedeutung des Status und die vollstaendige Linkpruefung bleiben Aufgabe des Redaktionsteams.

## Ansichten und Gestaltung

- **Liste:** Kompakte Karten mit Kursname, Pruefdatum, einer deutlich sichtbaren Zusammenfassung der offenen Punkte und dem Kurslink.
- **Einzelansicht:** Alle Statuswerte sowie Linkbefunde und besondere Hinweise.
- **Suche:** Filter nach Kursname, Pruefdatum und allen acht Statusfeldern.
- **Eingabe:** Kurszuordnung, acht Statusfelder sowie die beiden optionalen Hinweisfelder. Jedes Feld erscheint genau einmal.

Das CSS ist auf `.kc-db` begrenzt, verwendet keine externen Ressourcen und bleibt auf schmalen Ansichten lesbar. JavaScript ist nicht erforderlich und bleibt leer. Die Vorlagen verwenden nur Moodle-Feldplatzhalter sowie `##moreurl##` und `##actionsmenu##`.

## CSV und KI-Uebergabe

Der Export umfasst ausschliesslich die 13 Feldspalten in dieser Reihenfolge, ohne Moodle-Zusatzdaten wie Tags, Nutzungsinformationen, Zeitangaben, Freigabestatus oder Dateien. Das Format ist UTF-8, Komma als Trennzeichen und doppeltes Anfuehrungszeichen als Textbegrenzung.

Die genaue Verwendung nach dem Export steht in [ki-uebergabe.md](ki-uebergabe.md). Namen, E-Mail-Adressen, Empfaengerzuordnung und Versand bleiben ausserhalb der Datenbank und erfordern einen separaten, datenschutzkonformen Prozess.

## Abnahme

Lokal zu pruefen sind XML, Feldnamen, Feldtypen, Pflichtstatus, Auswahlwerte, Vorlagenplatzhalter, CSS-Kapselung, ZIP-Struktur und CSV-Rundlauf mit Umlauten, Kommas, Anfuehrungszeichen und mehrzeiligen Hinweisen. In Moodle 5.0.4 offen sind der Import, die Darstellung im Zieltheme, die Suche, die Pflichtfeldpruefung, der CSV-Export sowie die Rollenpruefung mit einem Lehrpersonenkonto und einem Konto des Redaktionsteams.
