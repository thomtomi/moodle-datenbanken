---
title: "Spezifikation SoSafe-Zertifikate"
date: 2026-09-17
---

# Spezifikation SoSafe-Zertifikate

## Zweck und Nutzung

Die Datenbank dokumentiert pro Klasse den aktuellen Stand der
SoSafe-Zertifikatsabgaben. Lehrpersonen wählen ihre Klasse, bestätigen den
Abgabestatus und ergänzen bei Bedarf einen Hinweis. Die Listenansicht macht
vollständige und unvollständige Klassen rasch unterscheidbar und zeigt die
ursprünglich eintragende Lehrperson sowie die letzte Änderung.

Die Datenbank prüft keine Zertifikate automatisch und versendet keine
Benachrichtigungen. Ein Eintrag bildet den aktuellen Status einer Klasse ab,
nicht eine Historie von Meldungen.

## Zielumgebung und Rollen

- Moodle 5.0.4, Kernaktivität `mod_data`; Theme und konkrete Testinstanz:
  offen.
- Alle Lehrpersonen dürfen Einträge sehen, erstellen und bearbeiten.
- Lernende dürfen keine Einträge oder Hinweise sehen, erstellen oder
  bearbeiten.
- Die Rollen werden im Kurs beziehungsweise in der Aktivität konfiguriert.
  Das Preset und seine Vorlagen können diese Berechtigungen nicht erzwingen.

`##user##` zeigt Moodles ursprünglich eintragende Person; `##timemodified##`
zeigt die letzte Änderung. Bearbeitet eine andere Lehrperson einen bestehenden
Eintrag, bleibt die eintragende Person sichtbar.

## Instruktionsdesign

Die [Redaktionsvorlage](../../00-setup/instruktionsdesign_template.md) wurde
herangezogen. Die [Instruktion](instruktion.html) verwendet die Abschnitte
**Einführung** und **Auftrag**, weil die Aktivität eine interne administrative
Erfassung und keine Lernaufgabe ist. Lernziele, Aufwand, Bewertung, Termin,
Reflexion und Literatur sind deshalb nicht passend und entfallen.

Die Instruktion wird in der Preset-Einstellung als Aktivitätsbeschreibung
eingebettet. Beim Moodle-Import ist diese Übernahme zu prüfen.

## Datenmodell

| Reihenfolge | Feld                         | Moodle-Typ  | Pflicht | Zweck und Regel                                                                                                                             |
| ----------: | ---------------------------- | ----------- | :-----: | ------------------------------------------------------------------------------------------------------------------------------------------- |
|           1 | Klasse                       | Auswahl     |   Ja    | Genau eine der acht vorgegebenen Klassen wählen.                                                                                            |
|           2 | Abgabestatus                 | Auswahl     |   Ja    | Aktueller Klassenstatus mit den zwei untenstehenden Werten.                                                                                 |
|           3 | Hinweis zur fehlenden Abgabe | Textbereich |  Nein   | Bei genau einer fehlenden Abgabe den Namen der betreffenden lernenden Person; bei mehreren fehlenden Abgaben ein kurzer sachlicher Hinweis. |

Klassenoptionen in dieser Reihenfolge:

1. `BM1-2427`
2. `BM1-2528`
3. `BM1-2629`
4. `BMLMT-2427`
5. `BMLMT-2326`
6. `BM2tz-2527`
7. `BM2tz-2628`
8. `BM2vz-2627`

Abgabestatus:

1. `Alle Zertifikate abgegeben`
2. `Nicht alle Zertifikate abgegeben`

Das optionale Hinweisfeld darf Namen enthalten und ist damit für alle
berechtigten Lehrpersonen sichtbar. Es werden keine unnötigen zusätzlichen
Personendaten erfasst.

Die Kernaktivität `mod_data` erzwingt nicht, dass ein Auswahlwert nur einmal
über alle Einträge vorkommt. Deshalb gilt organisatorisch: **Genau ein
aktueller Eintrag pro Klasse.** Vor dem Erstellen suchen Lehrpersonen nach der
Klasse und bearbeiten einen vorhandenen Eintrag.

## Ansichten und Gestaltung

- **Liste:** Responsives Raster mit Klasse, deutlich sichtbarem Status,
  optionalem Hinweis, eintragender Lehrperson und letzter Änderung. JavaScript
  markiert die zwei bekannten Statuswerte zusätzlich grün beziehungsweise
  bernsteinfarben; der Text bleibt die massgebliche Information.
- **Einzelansicht:** Vollständige Status- und Metadaten eines Eintrags.
- **Suche:** Filter nach Klasse und Abgabestatus.
- **Eingabe:** Jedes der drei Felder erscheint genau einmal mit feldbezogener
  Hilfe und einem Datenschutzhinweis.

Das CSS ist auf `.ss-db` und `.ss-list` begrenzt, lädt keine externen
Ressourcen und bleibt auf schmalen Ansichten einspaltig. JavaScript verarbeitet
nur den angezeigten Statustext, verwendet keine Feldwerte als HTML und greift
nicht auf externe Dienste zu.

## Datenaustausch

Das mitgelieferte CSV-Beispiel enthält nur die drei Datenbankfelder in dieser
Reihenfolge. Es verwendet UTF-8, Komma als Trennzeichen und doppelte
Anführungszeichen als Textbegrenzung. Die Beispieldaten sind synthetisch;
insbesondere sind Namen darin keine echten Personendaten.

`##user##` und `##timemodified##` sind Moodle-Systemmetadaten und nicht Teil
der drei exportierbaren Feldspalten. Bei einem Moodle-CSV-Export müssen die
konkreten Optionen der Zielinstanz kontrolliert werden.

## Abnahme

Lokal sind XML, Feldnamen, Feldtypen, Pflichtstatus, Klassen- und
Statusoptionen, eingebettete Instruktion, Feld- und Systemplatzhalter,
CSS-Kapselung, JavaScript-Grenzen, ZIP-Struktur und CSV-Rundlauf mit Umlauten,
Kommas, Anführungszeichen und Zeilenumbruch zu prüfen.

In Moodle 5.0.4 offen sind der Import, die Darstellung im Zieltheme, die
Suche, Pflichtfeldprüfung, Bearbeitung, Sichtbarkeit von `##user##` und
`##timemodified##`, sowie die Rollenprüfung mit je einem Lehrpersonen- und
Lernenden-Testkonto.
