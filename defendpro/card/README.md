# Defend Pro Visitenkarte

Zweiseitige Visitenkarte im europäischen Standardformat, gebaut aus
denselben Farben, Schriften und Zeichen wie die Homepage.

| | |
|---|---|
| Endformat | 85 × 55 mm |
| Beschnitt | 3 mm ringsum |
| Datenformat | 91 × 61 mm |
| Sicherheitsabstand | 4 mm innerhalb der Schnittkante |
| Seiten | 2, Vorderseite Navy, Rückseite Bone |
| Schrift | Inter, als Subset eingebettet |

## Bauen

```bash
python3 card/trace_assets.py    # nur nötig, wenn sich das Logo ändert
python3 card/build_card.py      # erzeugt card/karte.html
node card/render_card.js        # erzeugt PDF und Kontrollbilder
```

`render_card.js` endet mit Exit 1, sobald ein Element den
Sicherheitsabstand verletzt.

| Datei | Inhalt |
|---|---|
| `src/karte.html` | Layout und Text, mit Platzhaltern |
| `build_card.py` | setzt Schriften und Grafiken als base64 ein |
| `trace_assets.py` | vektorisiert Wortmarke und Emblem |
| `render_card.js` | PDF, Kontrollbilder, Maßprüfung |
| `assets/*.svg` | Wortmarke und Emblem als Pfad |
| `assets/fonts/` | Inter, Latin-Subset, SIL Open Font License 1.1 |

## Was die Druckerei bekommt

`defendpro_visitenkarte.pdf`, zwei Seiten, je 91 × 61 mm.

Das entspricht dem Endformat plus 3 mm Beschnitt ringsum, ohne
Schnittmarken. Das ist die übliche Anlieferungsform bei Onlinedruckereien.
Verlangt Ihre Druckerei Schnittmarken auf einem größeren Bogen, sagen Sie
Bescheid, dann liefere ich diese Variante zusätzlich.

Die Vorderseite läuft vollflächig in den Beschnitt, das Emblem ist
bewusst angeschnitten. Auf der Rückseite steht kein Element näher als
4 mm an der Schnittkante.

## Farbraum

Das PDF liegt in RGB vor. Die meisten Onlinedruckereien nehmen das an und
konvertieren selbst. Verlangt Ihre Druckerei CMYK, lassen Sie die
Konvertierung dort mit einem Profil für gestrichenes Papier durchführen.

Das tiefe Navy `#172A4E` ist die kritische Farbe. Bei einer automatischen
Konvertierung kann es matt und leicht violett kippen. Fordern Sie dafür
einen Andruck oder zumindest ein Farbmuster an, bevor die volle Auflage
läuft.

## Noch nicht auf der Karte

Telefonnummer und Anschrift liegen nicht vor. Die Karte ist ohne sie
vollständig und druckbar. Zum Ergänzen steht die Anleitung als Kommentar
direkt im Kontaktblock in `src/karte.html`. Es sind zwei Zeilen.

## Kontrollbilder

`shots/` enthält je Seite ein PNG in 600 dpi, dazu eine Fassung mit
eingezeichneten Hilfslinien. Rot ist die Schnittkante bei 85 × 55 mm,
grün der Sicherheitsabstand. Diese Bilder gehen nicht in den Druck.
