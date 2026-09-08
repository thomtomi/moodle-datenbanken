---
title: "Instruktionsdesign Template"
date: 2026-09-08
---

# Redaktionsvorlage für das Instruktionsdesign

Diese vom Nutzer bereitgestellte Vorlage bildet die gemeinsame Ausgangsbasis für die Anleitung der Lernenden in Moodle-Datenbank-Aktivitäten. Sie zeigt alle vorgesehenen Abschnitte. Auswahl, Anpassung und Prüfung richten sich nach dem Abschnitt «Einheitliches Instruktionsdesign für Lernende» in [agent_instruction.md](agent_instruction.md).

Der folgende HTML-Block ist eine Redaktionsvorlage, keine fertige Lernendeninstruktion. Er enthält Hinweise an die verfassende Person, Platzhalter und Beispiele. Die verwendeten Abschnitte werden für die konkrete Aktivität ausformuliert; nicht benötigte Abschnitte entfallen vollständig. Die Angaben zu Aufwand, Benotung, Abgabepflicht und Literatur sind keine allgemeinen Projektvorgaben.

## HTML-Vorlage

```html
<h3 style="color: #000000;">[fa-circle-info] Einführung</h3>
<p>Verdichten Sie die Zielsetzung der Aufgabe in ein bis zwei pointierten
  Sätzen, um die Lernenden unmittelbar anzusprechen und ihre Aufmerksamkeit zu
  aktivieren.</p>
<h3 style="color: #000000;">[fa-bullseye] Lernziel(-e)</h3>
<p>Sie sind in der Lage ...</p>
<ol>
  <li>Lernziel (1) der Aufgabe.</li>
  <li>Lernziel (2) der Aufgabe.</li>
  <li>Lernziel (3) der Aufgabe.</li>
</ol>
<h3 style="color: #000000;">[fa-tasks] Auftrag</h3>
<ul>
  <li>Auftrag ausformuliert.</li>
  <li>Möglichst genau auf die Bewertungskriterien hin formuliert.</li>
  <li>Im letzten Satz muss die Anweisung stehen, was abgegeben werden muss.</li>
</ul>
<h3 style="color: #000000;">[fa-clock-o] Aufwand</h3>
<p>Ca. xy Stunden</p>
<h3 style="color: #000000;">[fa-trophy] Bewertung Leistungsnachweis</h3>
<p>Die Note wird auf 0.1 Notenpunkte gerundet.</p>
<h3 style="color: #000000;">[fa-calendar] (Abgabe-)Termin</h3>
<p>Den Abgabetermin finden Sie oben. Die Abgabe ist Pflicht und der Termin
  verbindlich.</p>
<h3 style="color: #000000;">[fa-comments] Reflexion &amp; Auswertung</h3>
<p>Schreiben Sie, für welche weiteren Aufgaben diese hilfreich sein kann.</p>
<h3 style="color: #000000;">[fa-book] Literatur</h3>
<p>Falls Literatur verwendet wird, kann hier eine Quellenangabe erfolgen:</p>
<ul>
  <li>Müller et al. 2022 als Link</li>
</ul>
```

## Redaktionelle Bereinigungen gegenüber der bereitgestellten Fassung

- Den ungültigen Farbwert `#00000` zu `#000000` korrigiert; die vorgesehene schwarze Farbe beibehalten.
- «Den Abgabetermin finden siehe oben» grammatisch zu «Den Abgabetermin finden Sie oben» korrigiert. In der ausgearbeiteten Instruktion ist ein solcher Verweis durch eine tatsächlich auffindbare Terminangabe zu konkretisieren.
- Das überflüssige Komma im Satz zu Reflexion und Auswertung entfernt.
- Den Codeblock als HTML ausgezeichnet, da es sich um ein HTML-Fragment für die Inhaltsgestaltung handelt.
