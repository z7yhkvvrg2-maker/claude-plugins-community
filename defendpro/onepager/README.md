# Defend Pro Einseiter

Ein A4-Blatt zum Weitergeben. Zwei Verwendungen, dasselbe Dokument: die
Mitarbeiterin reicht es an ihre Leitung weiter, und es hängt als Anlage
an einer Anfrage.

Die Website verspricht diesen Einseiter im Kontaktbereich. Bis er
existierte, war das eine ungedeckte Zusage.

## Bauen

```bash
python3 onepager/build_onepager.py    # erzeugt einseiter.html
node onepager/render_onepager.js      # erzeugt PDF und Kontrollbild
```

Schriften, Wortmarke und Emblem kommen aus `../assets` und werden mit
Homepage und Visitenkarte geteilt.

| Datei | Inhalt |
|---|---|
| `src/einseiter.html` | Layout und Text, mit Platzhaltern |
| `build_onepager.py` | setzt Schriften und Vektoren als Data-URI ein |
| `render_onepager.js` | PDF, Kontrollbild, drei Prüfungen |

## Was geprüft wird

`render_onepager.js` bricht mit Exit 1 ab, sobald eine der drei
Bedingungen verletzt ist. Jede davon kann still schiefgehen.

**Genau eine Seite.** Ein Umbruch wäre hier kein Layoutdetail, sondern
ein Fehler: ein Einseiter mit zwei Seiten ist keiner. Beim ersten Bau
lief der Inhalt 341 mm hoch und ergab zwei Seiten.

**Schriften eingebettet.** Gezählt werden die `/FontFile2`-Einträge im
PDF. Deshalb stehen hier die vier statischen Inter-Schnitte und nicht
der Variable Font der Homepage, Begründung in `card/README.md`.

**Nichts wird nachgeladen.** Ein Blatt, das per Mail weitergeht, muss
offline gleich aussehen.

## Höhenreserve

Der Inhalt misst rund 286 mm von 297 mm, also etwa 11 mm Reserve. Wer
Text ergänzt, prüft mit `render_onepager.js` nach. Unter etwa 5 mm
Reserve kippt das Blatt bei kleinen Renderer-Unterschieden auf zwei
Seiten.

## Inhaltliche Bindungen

Drei Dinge stehen aus Gründen auf dem Blatt und dürfen nicht wegfallen:

- Der Preisrahmen „vierstelliger Bereich", ohne Fixpreis.
- Die Abgrenzung, dass der Safety Check keine gesetzliche
  Arbeitsplatzevaluierung, keine Rechtsprüfung und keine Zertifizierung
  ist. Derselbe Satz steht auf der Website und gehört in jedes Angebot.
- Der Hinweis, dass die Teilnahme freiwillig ist und gesundheitliche
  Einschränkungen vorab berücksichtigt werden.

Es stehen keine Referenzen, keine Testimonials und keine Statistiken
darauf. Die vier Qualifikationen sind die einzigen Belege, und sie sind
überprüfbar.

## Kein Beschnitt

Anders als die Visitenkarte ist das hier kein Druckereiprodukt. Das
Blatt geht per Mail und durch Bürodrucker, deshalb ohne Beschnitt und
mit 18 mm Rand. Der Navy-Kopf läuft bis an die Blattkante; ein Drucker
ohne randlosen Druck setzt dort einen weißen Rand, was der Lesbarkeit
nicht schadet.
