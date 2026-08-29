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
| `assets/logo.png` | Wortmarke, Lockup mit Emblem, in Navigation und Footer |
| `assets/emblem.png` | Emblem groß, Wasserzeichen im Hero und auf dem Buchcover |
| `assets/emblem_mark.png` | Emblem klein, Aufzählungszeichen und Werteband |
| `assets/portrait.jpg` | Porträt, Abschnitt 10 |
| `assets/favicon.png` | Favicon, Emblem auf Navy |

Logo und Emblem liegen als CSS-Maske über den Custom Properties `--logo`,
`--emblem` und `--emblem-mark`. Ausgewertet wird allein der Alphakanal,
die Farbe kommt aus dem Designsystem. Dieselbe Datei trägt dadurch die
weiße Fassung auf Navy und die dunkle auf Bone, und die
Aufzählungszeichen nehmen auf Bone automatisch `--gold-d`.

Wer das Logo austauscht, legt eine PNG mit transparentem Hintergrund ab.
Die Eigenfarbe der Datei spielt keine Rolle.

## Prüfen

```bash
npm install          # einmalig, nur Playwright
node deep.js         # Überlauf, Klickziele, tote Anker, Konsolenfehler
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

Gold `#B8A05C` trägt Text ausschließlich auf Navy. Auf Bone gilt
`--gold-d` `#8A7433`, weil Gold auf Bone nur 2,39:1 erreicht.
Radius durchgehend 3 px, keine Schatten, Trennlinien statt Karten.

Serife liegt allein im Buchabschnitt über die Klasse `.ed`.

## Vor dem Livegang

Offene Platzhalter stehen im Markup als `[... einsetzen]` und sind auf
der Seite gelb hinterlegt, damit keiner übersehen wird.

- [ ] Anschrift im Impressum und beim Verantwortlichen
- [ ] Gewerbewortlaut, GISA-Zahl, zuständige Behörde
- [ ] Hosting-Anbieter in der Datenschutzerklärung
- [ ] LinkedIn-URL eintragen oder Zeile entfernen
- [ ] Instagram-Handle bestätigen oder Zeile entfernen
- [ ] Formular auf ein echtes Endpoint umstellen, siehe Kommentar in Abschnitt 12
- [ ] Amazon-Link auf die kanonische Form `amazon.de/dp/ASIN` wechseln

## Technische Hinweise

**Formular.** Läuft als `mailto`-Fallback. Für den Betrieb `action` auf
Formspree oder das WPForms-Endpoint umstellen, `method="post"` bleibt.

**Schrift.** Inter wird über den System-Stack angesprochen. Bei einer
Übernahme nach WordPress die Schrift selbst hosten, damit die Darstellung
stabil bleibt und keine Verbindung zu Dritten entsteht.

**Assets.** Alle Bilder liegen als base64 in der Datei. Die Seite lädt
nichts nach. `deep.js` meldet jeden externen Request.

**Maskenunterstützung.** `mask-image` ist mit `-webkit-`-Präfix notiert.
Für Browser ohne Maskenunterstützung liegt in `03_components.css` ein
`@supports`-Block: die Wortmarke erscheint dort als gesetzter Text, das
Wasserzeichen entfällt, und die Aufzählungszeichen fallen auf den
ursprünglichen Strich zurück.
