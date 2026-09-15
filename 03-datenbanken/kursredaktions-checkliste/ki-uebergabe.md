---
title: "KI-Uebergabe Kursredaktions-Checkliste"
date: 2026-09-14
---

# KI-Uebergabe der Kursredaktions-Checkliste

## Zweck

Die CSV aus der Datenbank kann als strukturierte Grundlage fuer freundliche E-Mail-Entwuerfe dienen. Die Datenbank erzeugt, adressiert oder versendet keine E-Mails. Empfaengerzuordnung und Versand bleiben ein separater, zu autorisierender Prozess.

## Export und Datenminimierung

Beim Moodle-Export nur die 13 Datenbankfelder auswaehlen. Tags, Nutzungsinformationen, Zeitangaben, Freigabestatus und Dateien ausschalten. Die CSV wird in UTF-8, mit Komma als Trennzeichen und doppelten Anfuehrungszeichen als Textbegrenzung gelesen.

Die CSV enthaelt absichtlich weder Namen noch E-Mail-Adressen von Lehrpersonen. Vor einer Uebergabe an ein KI-System ist zu pruefen, ob dessen Einsatz fuer die konkreten Kursdaten datenschutzrechtlich freigegeben ist. Fuer Tests ausschliesslich die synthetische Beispieldatei verwenden.

## Regeln fuer E-Mail-Entwuerfe

- Ausschliesslich Kriterien mit `Korrektur noetig` als zu bearbeitende Punkte nennen.
- `Nicht geprueft` als offene interne Kontrolle behandeln und nicht als Mangel behaupten.
- `Nicht anwendbar` nicht erwaehnen.
- Die Befunde aus «Nicht funktionierende externe Links» und «Besondere Hinweise» nur sachlich und im notwendigen Umfang uebernehmen.
- Bei `Kursstruktur und Kursfuehrung = Korrektur noetig` freundlich einen Beratungstermin anbieten.
- Keine Aussagen ueber Personen, Berechtigungen oder Kursinhalte erfinden, die nicht in der CSV stehen.
- Den Entwurf vor dem Versand durch eine verantwortliche Person pruefen; erst danach erfolgt ausserhalb dieser Datenbank die Empfaengerzuordnung und der Versand.

## Beispiel einer Aufgabenbeschreibung fuer ein freigegebenes KI-System

```text
Erstelle aus einer CSV-Zeile einen freundlichen E-Mail-Entwurf auf Deutsch in der Sie-Form. Nenne nur die Kriterien mit dem Status "Korrektur noetig" und die dazu vorhandenen Textbefunde. Stelle "Nicht geprueft" als offenen internen Pruefpunkt dar, nicht als Fehler. Erwaehne "Nicht anwendbar" nicht. Biete bei "Kursstruktur und Kursfuehrung" mit dem Status "Korrektur noetig" einen Beratungstermin an. Erfinde keine Empfaengernamen, E-Mail-Adressen oder fachlichen Details. Der Entwurf wird vor einem Versand manuell geprueft.
```
