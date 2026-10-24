# Defend Pro Angebot

Vorlage für das schriftliche Angebot nach dem Erstgespräch. Die Website
verspricht es „in wenigen Tagen", und für die drei laufenden Gespräche
ist es der nächste Schritt.

## Ein Angebot schreiben

```bash
cp angebot/angebot.json angebot/2026-002-hausname.json
$EDITOR angebot/2026-002-hausname.json
python3 angebot/build_angebot.py angebot/2026-002-hausname.json
node angebot/render_angebot.js angebot/2026-002-hausname.json
```

Ergebnis: `angebot/defendpro_angebot.pdf`, zwei Seiten A4. Die Datei muss
beiden Schritten übergeben werden. Die Prüfung liest daraus die
Angebotsart, und ohne Argument prüft sie gegen `angebot.json` statt gegen
Ihr Angebot.

Firmendaten kommen aus `../kontakt.json` und stehen nicht noch einmal in
der Angebotsdatei. Anschrift, Gewerbewortlaut und GISA-Zahl müssen dort
gefüllt sein, sonst stehen sie im Fuß als Platzhalter.

## Was auszufüllen ist

| Feld | Anmerkung |
|---|---|
| `art` | `training` oder `vortrag`. Steuert Inhalt und Prüfung, siehe unten |
| `angebotsnummer`, `datum`, `gueltig_bis` | Bindefrist, üblich sind vier Wochen |
| `empfaenger_*` | Haus, Person, Funktion, Anschrift |
| `anrede` | Ganze Zeile, wie sie im Brief steht. Leer ergibt „Sehr geehrte Damen und Herren" |
| `einleitung` | Zwei bis drei Sätze aus dem Erstgespräch, in deren Worten |
| `positionen` | Beliebig viele. `preis` ist netto je Einheit |
| `ust_modus` | `kleinunternehmer` oder ein Steuersatz als Zahl |
| `teilnehmerzahl`, `termin`, `ort` | Rahmen |
| `bereitstellung` | Was das Haus beisteuert. Leer lässt die Zeile weg |
| `bildaufnahmen` | Regelung für Foto, Video und Nachbericht |
| `zahlungsziel_tage`, `storno_frist_tage` | Vorschläge, siehe unten |
| `storno_satz_danach` | Was nach Ablauf der Frist verrechnet wird |

`anrede` wird nicht geraten. Aus Vorname und Nachname eine Anrede zu
bauen ging schief, sobald ein Titel oder ein zweiter Name im Spiel war.
Schreiben Sie die Zeile, die im Brief stehen soll.

`bildaufnahmen` ist das Feld, an das man am ehesten nicht denkt. Bei
einem Haus fällt meist nichts an. Bei einer Veranstaltung mit
Nachbericht entscheidet dieser Satz, ob Ihr Name und Ihr Gesicht
hinterher öffentlich auffindbar sind.

Zwischensumme, Steuer und Endbetrag werden gerechnet, nicht abgetippt.
Beträge erscheinen in österreichischer Schreibweise, das Datum
ausgeschrieben mit Jänner statt Januar.

## Was geprüft wird

`render_angebot.js` bricht mit Exit 1 ab, sobald etwas davon fehlt. Ein
Angebot ist ein Vertragsdokument, deshalb wird nicht nur die Technik
geprüft, sondern auch der Inhalt.

Immer, bei jeder Angebotsart:

- Schriften als `/FontFile2` eingebettet
- keine externen Requests, das Dokument geht per Mail
- Bindefrist und Unterschriftsfeld sind enthalten
- Storno und Verschiebung sind geregelt
- der Ausfall meinerseits ist geregelt
- Bildaufnahmen sind geregelt
- keine der öffentlich gesperrten Bezeichnungen taucht auf

Zusätzlich bei `art: training`:

- **die Abgrenzung zum Safety Check ist enthalten.** Wer sie beim
  Redigieren löscht, bekommt kein PDF
- die Teilnahme ist ausdrücklich freiwillig
- gesundheitliche Einschränkungen sind angesprochen

Offene Platzhalter aus beiden Datendateien werden aufgelistet.

## Warum die Angebotsart zählt

Die eigene Vorgabe lautet, die Abgrenzung zum Safety Check steht in
jedem Angebot. Gemeint ist jedes Angebot, das einen Safety Check
enthalten kann. Ein reiner Vortrag enthält keinen, und er enthält auch
keine Übungen. Dort sind der Gesundheitshinweis und die Abgrenzung
sachlich falsch.

Die Prüfung verlangte beides zunächst immer. Ein korrekt geschriebenes
Vortragsangebot hätte sie abgelehnt. `art` trennt das, und sie steuert
außerdem, was unter Enthalten und Nicht enthalten steht. Ein Vortrag
braucht Raum, Beamer und Mikrofon. Ein Training braucht Platz für eine
Gruppe in Bewegung und bequeme Kleidung. Beides in einem Dokument wäre
in jedem Fall zur Hälfte verkehrt.

## Was hier keine geprüfte Rechtsberatung ist

Zahlungsziel, Stornofrist, die Formulierung zum Ausfall und der Satz zu
Bildaufnahmen sind handelsübliche Vorschläge, keine juristisch
geprüften Klauseln. Lassen
Sie sie vor dem ersten echten Angebot einmal von der Wirtschaftskammer
oder einer Juristin ansehen. Danach stehen sie in der Vorlage und Sie
müssen nicht mehr daran denken.

Dasselbe gilt für `ust_modus`. Ob die Kleinunternehmerregelung für Sie
gilt, klärt die Wirtschaftskammer oder Ihre Steuerberatung. Die Vorlage
rät nicht, sie setzt um, was Sie eintragen.

## Aufbau

Seite 1 trägt Empfänger, Anlass, Leistung mit Preis und den Rahmen.
Seite 2 trägt Enthalten, Nicht enthalten, die Konditionen und die
Annahme mit Unterschriftsfeld. Bei einem Training kommen dort Teilnahme
und Abgrenzung hinzu.

Die Trennung ist Absicht. Wer nur wissen will, was es kostet, findet das
auf Seite 1. Wer unterschreiben soll, liest Seite 2.
