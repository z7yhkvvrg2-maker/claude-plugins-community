# Defend Pro Homepage

Einseitige Website für Defend Pro, Matthias Gastgeb, Wien.
Eine eigenständige HTML-Datei ohne externe Requests.

## Bauen

```bash
python3 build.py
```

Setzt `defendpro_homepage.html` aus den Teilen in `src/` zusammen und
schreibt die Bilder aus `assets/` als base64 hinein.
Keine Abhängigkeiten, nur die Standardbibliothek.

| Quellteil | Inhalt |
|---|---|
| `src/01_head.html` | Meta, Open Graph, Favicon, JSON-LD für Organisation, Person und Buch |
| `src/02_base.css` | Farbtokens, Assetpfade, Typografie, Layoutraster, Fokus, Reduced Motion |
| `src/03_components.css` | Navigation, Hero, Bausteine, Formular, Footer, Druckausgabe |
| `src/04_body.html` | Seitenkörper, Abschnitte 00 bis 14 |

## Assets

| Datei | Verwendung |
|---|---|
| `assets/logo.svg` | Wortmarke, Lockup mit Emblem, in Navigation und Footer |
| `assets/emblem.svg` | Emblem, Wasserzeichen, Aufzählungszeichen, Buchcover |
| `assets/portrait.jpg` | Porträt, Abschnitt 10 |
| `assets/favicon.png` | Favicon, Emblem auf Navy |
| `assets/fonts/` | Inter, SIL Open Font License 1.1 |
| `assets/logo.png`, `assets/emblem.png` | PNG-Quellen, nur Vorlage für `trace_assets.py` |

Die beiden SVG entstehen aus den PNG-Quellen:

```bash
python3 trace_assets.py
```

Nötig nur, wenn sich das Logo ändert. Als Pfad bleibt das Emblem in jeder
Größe scharf, vom 14-px-Aufzählungszeichen bis zum Wasserzeichen im Hero,
und dient zugleich der Visitenkarte als Druckvorlage.

Logo und Emblem liegen als CSS-Maske über die Custom Properties `--logo`
und `--emblem`. Ausgewertet wird allein der Alphakanal,
die Farbe kommt aus dem Designsystem. Dieselbe Datei trägt dadurch die
weiße Fassung auf Navy und die dunkle auf Bone, und die
Aufzählungszeichen nehmen auf Bone automatisch `--gold-d`.

Wer das Logo austauscht, legt eine PNG mit transparentem Hintergrund ab.
Die Eigenfarbe der Datei spielt keine Rolle.

## Prüfen

```bash
npm install          # einmalig, nur Playwright
node deep.js         # Überlauf, Klickziele, tote Anker, Konsole, externe Requests
node shot.js         # Screenshots je Abschnitt nach shots/
```

`deep.js` prüft 390, 834, 1180, 1440 und 1600 px und endet mit Exit 1,
sobald eine Breite auffällt.

## Aufbau der Seite

| Nr | ID | Fläche | Inhalt |
|---|---|---|---|
| 00 | – | Navy | Navigation, mobiler Dauer-CTA |
| 01 | `start` | Navy | Hero, zwei CTAs, vier Belege |
| 02 | – | Navy-d | Werteband |
| 03 | `situation` | Bone | Ausgangslage, sechs Anlässe |
| 04 | `leistungen` | Bone-d | Safety Check, Training, Transfer |
| 05 | `bereiche` | Bone | Care, Core, Education |
| 06 | `system` | Navy-d | Organisation, Team, Mensch |
| 07 | `ablauf` | Bone | Vier Schritte, Preisrahmen |
| 08 | `formate` | Bone-d | Vier Formate |
| 09 | `fragen` | Bone | Sechs häufige Fragen |
| 10 | `person` | Navy | Porträt, Bio, vier Belege |
| 11 | `buch` | Bone | Buchabschnitt, Serife über `.ed` |
| 12 | `kontakt` | Navy | Ansprache, Formular |
| 13 | `rechtliches` | Bone | Impressum, Datenschutz |
| 14 | – | Navy-d | Footer |

## Gestaltung

Farben, Typografie und Abstände liegen als Custom Properties in
`src/02_base.css`. Änderungen dort wirken auf die ganze Seite.

Gold `#B8A05C` trägt Text ausschließlich auf Navy, wo es 5,56:1 erreicht.
Auf Bone kommt Gold nur auf 2,39:1 und ist als Textfarbe ausgeschlossen.
Dort gilt `--gold-d` `#7D692E` mit 5,00:1 auf Bone und 4,54:1 auf Bone-d.

Der frühere Wert `#8A7433` lag mit 4,25:1 und 3,86:1 unter den 4,5:1, die
WCAG AA für Text dieser Größe verlangt. Die 3:1-Ausnahme greift erst ab
18,66 px fett und hilft den 11-px-Eyebrows nicht.

Radius durchgehend 3 px, keine Schatten, Trennlinien statt Karten.

Serife liegt allein im Buchabschnitt über die Klasse `.ed`.

## Vor dem Livegang

Alle fehlenden Angaben stehen in **einer** Datei: `kontakt.json`.
Ausfüllen, `python3 build.py`, fertig. Kein Suchen im Markup.

```bash
$EDITOR kontakt.json
python3 build.py
```

Der Build sagt danach, wie viele Angaben noch offen sind, und weist
gesondert auf den teuersten hin.

Ein leeres Feld erscheint auf der Seite als gelbe Marke, damit nichts
unbemerkt live geht.

| Feld | Wirkt auf |
|---|---|
| `anschrift` | Impressum und Verantwortlicher |
| `gewerbewortlaut`, `gisa`, `behoerde` | Impressum |
| `hosting` | Datenschutzerklärung |
| `linkedin_url`, `instagram_url` | Kontaktblock |
| `formular_endpoint` | Formular, siehe Warnung unten |

Zwei Punkte liegen außerhalb von `kontakt.json`:

- [ ] Amazon-Link auf die kanonische Form `amazon.de/dp/ASIN` wechseln
- [ ] Datenschutzerklärung anpassen, sobald ein Formulardienst gesetzt ist

## Keine Telefonnummer, und warum

Auf der Seite steht bewusst keine Telefonnummer. Sie wird aus
Sicherheitsgründen auf keinem öffentlichen Material geführt und nur
persönlich per E-Mail weitergegeben. Eine einmal veröffentlichte
Mobilnummer lässt sich nicht zurückholen.

Das ist eine Entscheidung, kein offener Punkt. `kontakt.json` hat
deshalb kein Telefonfeld, und im Markup gibt es keine Stelle dafür. Wer
das ändert, hebt die Entscheidung auf.

**Damit trägt das Formular allein.** Ohne Telefon ist es neben der
E-Mail-Adresse der einzige Weg zu Defend Pro. Solange
`formular_endpoint` leer ist, läuft es auf den `mailto`-Fallback und
liefert nichts zuverlässig aus. Das ist der teuerste offene Punkt der
ganzen Seite.

## Technische Hinweise

**Formular.** Läuft als `mailto`-Fallback und liefert damit nichts
zuverlässig aus: ohne registriertes Mailprogramm passiert beim Absenden
sichtbar nichts, und es kommt auch nichts an. Für den Betrieb `action`
auf ein echtes Endpoint umstellen, `method="post"` bleibt.

Achtung, das ist keine reine Technikänderung. Die Datenschutzerklärung
sagt derzeit „keine Verbindung zu Dritten" und „Weitergabe erfolgt nur
an den Hostinganbieter". Jeder externe Formulardienst ist ein weiterer
Auftragsverarbeiter. Beides muss am selben Tag angepasst werden, sonst
wird die Erklärung mit der Umstellung falsch.

**Schrift.** Inter liegt als Variable Font eingebettet in der Datei,
Achse `wght` 100 bis 900. Dadurch treffen auch die Zwischenschnitte 650
und 750 aus dem Designsystem exakt. Es entsteht keine Verbindung zu
Google Fonts.

Das gilt für die Grotesk, also den ganzen Fließtext und alle
Überschriften. Die Serife im Buchabschnitt läuft weiter über einen
System-Stack aus Georgia und Times und hängt damit am Gerät. Für einen
Abschnitt von 55 Wörtern ist das vertretbar, es ist aber keine
vollständige Unabhängigkeit.

Die Visitenkarte verwendet bewusst die vier statischen Schnitte im selben
Ordner. Grund steht in `card/README.md`.

**Assets.** Alle Bilder liegen als base64 in der Datei. Die Seite lädt
nichts nach.

`deep.js` überwacht das über `page.on('request')` und bricht mit Exit 1
ab, sobald eine Anfrage weder `file:` noch `data:` ist. Der Wächter ist
gegen eine absichtlich eingebaute externe Ressource getestet. Vorher
behauptete diese Zeile die Prüfung, ohne dass sie stattfand.

**Maskenunterstützung.** `mask-image` ist mit `-webkit-`-Präfix notiert.
Für Browser ohne Maskenunterstützung liegt in `03_components.css` ein
`@supports`-Block: die Wortmarke erscheint dort als gesetzter Text, das
Wasserzeichen entfällt, und die Aufzählungszeichen fallen auf den
ursprünglichen Strich zurück.
