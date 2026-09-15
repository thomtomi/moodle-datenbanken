---
title: "Kursredaktions-Checkliste"
date: 2026-09-14
---

# Kursredaktions-Checkliste

Diese Moodle-Datenbank dokumentiert eine vollstaendige Funktionspruefung pro Kurs. Das [Preset](ausgabe/kursredaktions-checkliste-moodle504.zip) richtet 13 exportierbare Felder, die Listen-, Einzel-, Eingabe- und Suchansicht ein. Die [lokale Vorschau](vorschau.html) und die [CSV-Beispieldatei](beispiel-export.csv) verwenden ausschliesslich synthetische Daten; sie belegen keinen Moodle-Test.

## Import in Moodle 5.0.4

1. Eine neue, leere Aktivitaet «Datenbank» anlegen, beispielsweise «Kursredaktions-Checkliste». Die Aktivitaet vor der Konfiguration noch nicht sichtbar schalten.
2. Unter «Vorlagensaetze/Presets» das ZIP aus `ausgabe/` importieren. Das ZIP unveraendert hochladen und die Uebernahme der Einstellungen aktivieren.
3. Pruefen, ob 13 Felder in der in der [Spezifikation](spezifikation.md) beschriebenen Reihenfolge vorhanden sind. Die acht Auswahlfelder muessen die vier Werte «Erfuellt», «Korrektur noetig», «Nicht anwendbar» und «Nicht geprueft» anbieten.
4. Pruefen, ob die Aktivitaetsbeschreibung angezeigt wird. Falls sie fehlt, den Inhalt von [instruktion.html](instruktion.html) als HTML in die Aktivitaetsbeschreibung einsetzen.
5. Einen synthetischen Eintrag mit allen vier Statuswerten, einem mehrzeiligen Linkbefund und einem Hinweis erfassen, speichern, bearbeiten, suchen und als CSV exportieren. Die Aktivitaet erst nach erfolgreichen Tests bereitstellen.

Ein Import in eine bestehende Datenbank kann Felder und Vorlagen beeinflussen. Vor einer solchen Aenderung zuerst eine Moodle-Sicherung erstellen und Feldzuordnung sowie Datenuebernahme separat pruefen.

## Rollen und Sichtbarkeit

Die Vorlagen koennen keine Berechtigungen erzwingen. In Moodle sind die Rollen fuer diese Aktivitaet so zu konfigurieren:

| Rolle                                       | Vorgabe                                                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Lehrpersonen ausserhalb des Redaktionsteams | Eintraege und Einzelansichten sehen sowie suchen; keine Eintraege erstellen, bearbeiten, loeschen oder exportieren. |
| Redaktionsteam                              | Eintraege sehen, erstellen, bearbeiten, loeschen und als CSV exportieren.                                           |

Die genauen Faehigkeitsnamen und die Vererbung muessen im Rollen-Override der konkreten Moodle-5.0.4-Instanz kontrolliert werden. Mit je einem Testkonto als Lehrperson und als Mitglied des Redaktionsteams pruefen, dass die Lehrperson weder Eingabe- noch Bearbeitungs- noch Exportaktionen erhaelt, das Redaktionsteam aber alle vorgesehenen Aktionen ausfuehren kann.

## CSV-Export und Rueckmeldungen

Als Redaktionsteam nur die 13 Datenbankfelder exportieren. Je nach Moodle-Exportformular Tags, Nutzungsinformationen, Zeitangaben, Freigabestatus und Dateien abwaehlen. Das Ergebnis als UTF-8-CSV mit Komma als Trennzeichen und doppelten Anfuehrungszeichen als Textbegrenzung lesen.

Die Datenbank speichert keine Lehrpersonen-Namen oder E-Mail-Adressen und versendet keine Nachrichten. Die Vorgaben fuer eine datensparsame, nachgelagerte KI-Nutzung stehen in [ki-uebergabe.md](ki-uebergabe.md). Empfaengerzuordnung und Versand erfolgen ausschliesslich ausserhalb dieser Aktivitaet und nach einer manuellen Pruefung des E-Mail-Entwurfs.

## Lokal bauen und pruefen

Aus diesem Aktivitaetsordner:

```bash
python3 -B build.py
python3 -B pruefen.py
```

`build.py` erzeugt das ZIP, die synthetische CSV und die lokale Vorschau. `pruefen.py` prueft XML, Feldmodell, Auswahloptionen, Platzhalter, CSS-Kapselung, ZIP-Struktur und den CSV-Rundlauf. Beide Skripte verwenden nur die Python-Standardbibliothek. Ein erfolgreicher lokaler Lauf ersetzt weder den Moodle-Import noch die Rollen- und Exportpruefung.

## Dateien

- [spezifikation.md](spezifikation.md): Zweck, Datenmodell, Rollen und Abnahme.
- [instruktion.html](instruktion.html): interne Arbeitsanleitung fuer die Aktivitaetsbeschreibung.
- [ki-uebergabe.md](ki-uebergabe.md): Regeln fuer die nachgelagerte KI-Nutzung.
- `preset/`: bearbeitbare Moodle-XML-, HTML-, CSS- und JavaScript-Dateien.
- [build.py](build.py) und [pruefen.py](pruefen.py): reproduzierbarer Build und lokale Konsistenzpruefung.
