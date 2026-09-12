---
name: "Moodle-Datenbanken: Artefakte"
globs: ["03-datenbanken/**/*.{py,html,css,js,xml,csv,md}"]
alwaysApply: false
description: "Arbeitsregeln für Moodle-Presets, CSV-Dateien, Vorlagen, Prüfungen und Dokumentation unter 03-datenbanken."
---

# Moodle-Artefakte

- Lesen Sie vor einer Änderung den nächstgelegenen `README.md`, die `spezifikation.md` und das `pruefprotokoll.md`, soweit vorhanden. Prüfen Sie zusätzlich, ob ein `build.py`, `pruefen.py` oder ein Testordner den Arbeitsablauf vorgibt.
- Bearbeiten Sie nur die als Quelle ausgewiesenen Dateien. Verändern Sie generierte ZIP-, Vorschau- oder Ausgabedateien nicht von Hand, wenn ein vorhandener Build sie reproduzierbar erzeugt.
- Erhalten Sie Feldnamen, Feldtypen, Platzhalter, Datenreihenfolge und bestehende Werte, sofern der Auftrag keine dokumentierte Datenmigration verlangt.
- Nutzen Sie für XML und CSV passende Parser. Prüfen Sie Moodle-Platzhalter gegen die Felddefinition; behandeln Sie unbekannte Platzhalter, externe Ressourcen und nicht begründeten ausführbaren Code als Fehler.
- Unterscheiden Sie ein Preset, Datensätze und eine Moodle-Sicherung. Behaupten Sie keinen Moodle-Import, Rollen- oder Browser-Test ohne den tatsächlich ausgeführten Nachweis in der Zielumgebung.
- Führen Sie nach jeder relevanten Änderung den im Aktivitätsordner vorgesehenen engsten Check aus. Aktualisieren Sie bei wesentlichen Arbeiten die betroffenen Nachweise im `pruefprotokoll.md`.
