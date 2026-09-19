---
title: "SoSafe-Zertifikate"
date: 2026-09-17
---

# SoSafe-Zertifikate

Diese Moodle-Datenbank zeigt pro Klasse den aktuellen Stand der
SoSafe-Zertifikatsabgaben. Das [Preset](ausgabe/sosafe-zertifikate-moodle504.zip)
richtet drei Felder und Listen-, Einzel-, Eingabe- sowie Suchansicht ein. Die
[lokale Vorschau](vorschau.html) und die [CSV-Beispieldatei](beispiel-export.csv)
verwenden ausschliesslich synthetische Daten; sie belegen keinen Moodle-Test.

## Import in Moodle 5.0.4

1. Legen Sie eine neue, leere Aktivität «Datenbank» an, beispielsweise
   «SoSafe-Zertifikate». Schalten Sie sie vor der Konfiguration noch nicht
   sichtbar.
2. Importieren Sie unter «Vorlagensätze/Presets» das ZIP aus `ausgabe/` und
   übernehmen Sie die Einstellungen.
3. Prüfen Sie drei Felder in der in der [Spezifikation](spezifikation.md)
   beschriebenen Reihenfolge. Das Auswahlfeld «Klasse» muss genau die acht
   vorgegebenen Klassen enthalten; «Abgabestatus» muss genau die zwei
   festgelegten Werte anbieten.
4. Prüfen Sie die Aktivitätsbeschreibung. Fehlt sie, fügen Sie den Inhalt von
   [instruktion.html](instruktion.html) als HTML in die
   Aktivitätsbeschreibung ein.
5. Erfassen Sie einen synthetischen vollständigen und einen unvollständigen
   Klassenstatus. Prüfen Sie Speichern, Bearbeiten, Suche, Listenansicht,
   Einzelansicht sowie die sichtbare eintragende Person und letzte Änderung.
   Schalten Sie die Aktivität erst nach erfolgreichen Tests bereit.

Ein Import in eine bestehende Datenbank kann Felder und Vorlagen beeinflussen.
Erstellen Sie zuvor eine Moodle-Sicherung und prüfen Sie Datenübernahme sowie
Feldzuordnung separat.

## Rollen und Sichtbarkeit

Das Preset erzwingt keine Berechtigungen. Konfigurieren und testen Sie in der
Zielinstanz folgende Vorgaben:

| Rolle        | Vorgabe                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------- |
| Lehrpersonen | Einträge und Details sehen, nach Klasse oder Status suchen sowie Einträge erstellen und bearbeiten. |
| Lernende     | Keine Einträge, Hinweise oder Bearbeitungsfunktionen sehen.                                         |

Prüfen Sie mit getrennten Testkonten, ob eine Lehrperson die vorgesehenen
Aktionen ausführen kann und ein Lernendenkonto keine Einsicht oder Bearbeitung
erhält. Die genauen Fähigkeitsnamen und ihre Vererbung hängen von der
konkreten Moodle-5.0.4-Instanz ab und müssen im Rollen-Override geprüft werden.

## Arbeitsregel pro Klasse

Die Moodle-Datenbank verhindert doppelte Klassenwerte nicht automatisch.
Darum zuerst nach der Klasse suchen und einen vorhandenen Eintrag bearbeiten.
Es gilt genau ein aktueller Eintrag pro Klasse. `##user##` zeigt dabei die
ursprünglich eintragende Lehrperson; die letzte Änderung zeigt
`##timemodified##`.

## Lokal bauen und prüfen

Führen Sie im Aktivitätsordner aus:

```bash
python3 -B build.py
python3 -B pruefen.py
```

`build.py` erzeugt das ZIP, die synthetische CSV und die lokale Vorschau.
`pruefen.py` prüft XML, Feldmodell, Auswahlwerte, Platzhalter, CSS,
JavaScript, ZIP-Struktur und CSV-Rundlauf. Beide Skripte verwenden nur die
Python-Standardbibliothek. Ein erfolgreicher lokaler Lauf ersetzt weder den
Moodle-Import noch die Rollen- und Nutzungsprüfung.

## Dateien

- [spezifikation.md](spezifikation.md): Zweck, Datenmodell, Rollen und
  Abnahme.
- [instruktion.html](instruktion.html): Arbeitsanleitung für die
  Aktivitätsbeschreibung.
- [pruefprotokoll.md](pruefprotokoll.md): ausgeführte und noch offene
  Prüfungen.
- `preset/`: bearbeitbare Moodle-XML-, HTML-, CSS- und JavaScript-Dateien.
- [build.py](build.py) und [pruefen.py](pruefen.py): reproduzierbarer Build
  und lokale Konsistenzprüfung.
