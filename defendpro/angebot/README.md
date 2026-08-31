# Defend Pro Angebot

Vorlage für das schriftliche Angebot nach dem Erstgespräch. Die Website
verspricht es „in wenigen Tagen", und für die drei laufenden Gespräche
ist es der nächste Schritt.

## Ein Angebot schreiben

```bash
cp angebot/angebot.json angebot/2026-002-hausname.json
$EDITOR angebot/2026-002-hausname.json
python3 angebot/build_angebot.py angebot/2026-002-hausname.json
node angebot/render_angebot.js
```

Ergebnis: `angebot/defendpro_angebot.pdf`, zwei Seiten A4.

Firmendaten kommen aus `../kontakt.json` und stehen nicht noch einmal in
der Angebotsdatei. Anschrift, Gewerbewortlaut und GISA-Zahl müssen dort
gefüllt sein, sonst stehen sie im Fuß als Platzhalter.

## Was auszufüllen ist

| Feld | Anmerkung |
|---|---|
| `angebotsnummer`, `datum`, `gueltig_bis` | Bindefrist, üblich sind vier Wochen |
| `empfaenger_*` | Haus, Person, Funktion, Anschrift |
| `einleitung` | Zwei bis drei Sätze aus dem Erstgespräch, in deren Worten |
| `positionen` | Beliebig viele. `preis` ist netto je Einheit |
| `ust_modus` | `kleinunternehmer` oder ein Steuersatz als Zahl |
| `teilnehmerzahl`, `termin`, `ort` | Rahmen |
| `zahlungsziel_tage`, `storno_frist_tage` | Vorschläge, siehe unten |

Zwischensumme, Steuer und Endbetrag werden gerechnet, nicht abgetippt.
Beträge erscheinen in österreichischer Schreibweise, das Datum
ausgeschrieben mit Jänner statt Januar.

## Was geprüft wird

`render_angebot.js` bricht mit Exit 1 ab, sobald etwas davon fehlt. Ein
Angebot ist ein Vertragsdokument, deshalb wird nicht nur die Technik
geprüft, sondern auch der Inhalt.

- Schriften als `/FontFile2` eingebettet
- keine externen Requests, das Dokument geht per Mail
- **die Abgrenzung zum Safety Check ist enthalten.** Sie gehört laut
  eigener Vorgabe in jedes Angebot. Wer sie beim Redigieren löscht,
  bekommt kein PDF
- der Teilnahme- und Gesundheitshinweis ist enthalten
- Bindefrist und Unterschriftsfeld sind enthalten
- keine der öffentlich gesperrten Bezeichnungen taucht auf

Offene Platzhalter aus beiden Datendateien werden aufgelistet.

## Was hier keine geprüfte Rechtsberatung ist

Zahlungsziel, Stornofrist und die Formulierung zum Ausfall sind
handelsübliche Vorschläge, keine juristisch geprüften Klauseln. Lassen
Sie sie vor dem ersten echten Angebot einmal von der Wirtschaftskammer
oder einer Juristin ansehen. Danach stehen sie in der Vorlage und Sie
müssen nicht mehr daran denken.

Dasselbe gilt für `ust_modus`. Ob die Kleinunternehmerregelung für Sie
gilt, klärt die Wirtschaftskammer oder Ihre Steuerberatung. Die Vorlage
rät nicht, sie setzt um, was Sie eintragen.

## Aufbau

Seite 1 trägt Empfänger, Anlass, Leistung mit Preis und den Rahmen.
Seite 2 trägt Enthalten, Nicht enthalten, Teilnahme, die Abgrenzung, die
Konditionen und die Annahme mit Unterschriftsfeld.

Die Trennung ist Absicht. Wer nur wissen will, was es kostet, findet das
auf Seite 1. Wer unterschreiben soll, liest Seite 2.
