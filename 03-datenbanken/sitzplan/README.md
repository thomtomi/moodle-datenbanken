---
title: "Sitzplan"
date: 2026-09-14
---

# Sitzplan

Ein Datenbankeintrag enthält einen vollständigen Sitzplan mit **1 bis 8 Querreihen** und **1 bis 16 Tischen je Reihe**, Name und optionalem Foto pro Platz. Standardmässig sind drei Reihen mit je sieben Tischen eingestellt. Wandtafel und mittiges Lehrer:innen-Pult liegen im Plan unten. Reihe 1 ist dem Pult am nächsten, Platz 1 liegt links aus Sicht der Lehrperson.

[Preset herunterladen](ausgabe/sitzplan-preset.zip) · [Sitzplan-Vorschau](vorschau.html) · [Eingabevorschau](vorschau-eingabe.html) · [Prüfprotokoll](pruefprotokoll.md)

## In Moodle einrichten

1. Eine neue, zunächst für Lernende verborgene Datenbankaktivität anlegen. Dieses Preset ist als Arbeitsmittel für Lehrpersonen vorgesehen.
2. `ausgabe/sitzplan-preset.zip` importieren und die 267 Felder kontrollieren: Plan, Raum, neun Felder für die Raumaufteilung sowie 128 Name-/Foto-Paare. Die technische Referenz ist Moodle 5.1.0; Version und Theme Ihrer Zielinstanz sind noch offen.
3. Die [Anleitung](instruktion.html) in der Aktivitätsbeschreibung prüfen beziehungsweise einfügen. Sie ist auch im Preset enthalten; die tatsächliche Übernahme kontrollieren.
4. Nur den vorgesehenen Lehrpersonen Zugriff geben. Für Lernende und Gäste `mod/data:viewentry` und `mod/data:writeentry` in dieser Aktivität unterbinden und die tatsächliche Wirkung mit Testkonten prüfen. Ein Preset überträgt diese Rollenregel nicht. Keine Freigabe eines Eintrags als Ersatz für die Zugriffsbeschränkung verwenden.
5. Einen Eintrag erstellen, zum Beispiel «Klasse BMS · September», und den Raum ergänzen. Unter «Raumaufteilung» 1 bis 8 Reihen und 1 bis 16 Tische je Reihe wählen; ohne Auswahl gelten 3 × 7. Pro Tisch den Namen eintragen. Unbesetzte Plätze bleiben leer. Über «Foto · optional» kann je Tisch ein Porträt mit Alternativtext hochgeladen werden.
6. Speichern, den Sitzplan öffnen und die Platzzuordnung prüfen. Bei einer Umplatzierung immer Name **und** Foto an beiden betroffenen Plätzen ändern. Zum Entfernen eines Fotos die Moodle-Dateiverwaltung öffnen, die Datei entfernen und den ganzen Eintrag speichern.

Fotos sind einzelne Moodle-Bildfelder; eine automatische Zuordnung zu Kurskonten oder Profilbildern ist nicht enthalten. Es gibt keinen Drag-and-drop-Umzug von Personen. Pro Foto sind 2 MiB vorgesehen; Moodle-/Servergrenzen können niedriger sein. Nutzen Sie nur die für diesen Unterrichtszweck vorgesehenen Namen und Bilder und halten Sie den Zugriff auf den vorgesehenen Personenkreis beschränkt.

## Ansichten

- Einzelansicht: vollständiger Sitzplan mit Namen und vorhandenen Fotos. Die gewählte Raumaufteilung bleibt auf dem Handy erhalten; der Plan ist mit Tastatur oder Berührung seitlich scrollbar.
- Listenansicht: nur Planname, Raum und «Sitzplan öffnen».
- Eingabe: bis zu acht Abschnitte mit je sechzehn nummerierten Plätzen. Nicht verwendete Reihen und Plätze werden ausgeblendet; Fotos lassen sich bei Bedarf aufklappen.
- Suche: nach Planname und Raum.

Die Texte stehen aus Sicht der Lehrperson aufrecht. Auf Papier liegen Wandtafel und Pult an der Ihnen zugewandten unteren Kante. Für einen Ausdruck die Einzelansicht im Browser drucken und Querformat wählen. Die CSS-Druckansicht formatiert den Sitzplan; Moodle-Seitenleisten oder Kopfzeilen können abhängig vom Theme zusätzlich erscheinen. Die exakte Druckausgabe in der Zielinstanz ist noch zu prüfen.

## Erzeugen und prüfen

```bash
python3 -B 03-datenbanken/sitzplan/build.py
python3 -B 03-datenbanken/sitzplan/pruefen.py
python3 -B 03-datenbanken/sitzplan/browser_pruefung.py
```

Quellen für die Generierung sind `build.py`, `instruktion.html` und `preset/csstemplate.css`. Alle weiteren Preset-Dateien, die Feldliste und Vorschauen werden durch den Build erzeugt. Vorschauen verwenden ausschliesslich synthetische Namen und neutrale Symbolbilder. Der Browsercheck verwendet die vorhandene Chromium-Anbindung aus dem Lektionsplaner und benötigt lokale Sockets.

Das ZIP überträgt Felder, Vorlagen und bestimmte Einstellungen, aber **keine Sitzpläne, Namen, Fotos oder Zugriffsrechte**. Bestehende Aktivitäten vor Änderungen vollständig sichern; dieses neue Datenmodell zuerst separat testen. Für eine spätere Übertragung ausgefüllter Pläne eine passende Moodle-Sicherung mit den nötigen Daten und Dateien verwenden und deren Wiederherstellung testen. Keine Dateien mit Lernendendaten hier im Repository ablegen.

Die Raumaufteilung ist im Preset auf höchstens 8 × 16 ausgelegt. Das Preset ergänzt gegenüber einem älteren 3 × 7-Stand Felder; daher bestehende produktive Aktivitäten nicht unkontrolliert überschreiben. Vor einer Migration sichern und den Import zunächst separat testen.
