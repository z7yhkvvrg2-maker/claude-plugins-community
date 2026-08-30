#!/usr/bin/env python3
"""Setzt die Homepage aus den Quellteilen zu einer eigenstaendigen Datei zusammen.

    python3 build.py

Ergebnis: defendpro_homepage.html im selben Ordner.
Alle Bilder wandern als base64 in die Datei. Kein externer Request,
keine Abhaengigkeiten ausserhalb der Standardbibliothek.

Platzhalter in den Quellteilen:

    {{LOGO}}       Wortmarke Defend Pro, Lockup mit Emblem, Vektor
    {{EMBLEM}}     Emblem, Vektor, Wasserzeichen und Aufzaehlungszeichen
    {{PORTRAIT}}   Portraet Matthias Gastgeb
    {{FAVICON}}    Favicon, Emblem auf Navy
    {{FONT}}       Inter, Variable Font, Latin-Subset

Logo und Emblem werden als CSS-Maske eingesetzt. Ausgewertet wird nur der
Alphakanal, die Farbe kommt aus dem Designsystem. Dadurch traegt dieselbe
Datei die weisse Fassung auf Navy und die dunkle auf Bone.

Als Maske dienen die Vektorfassungen aus trace_assets.py. Sie bleiben in
jeder Groesse scharf, vom 14-px-Aufzaehlungszeichen bis zum
Wasserzeichen im Hero, und sind zusammen kleiner als die PNG-Quellen.
"""

import base64
import html as htmlmod
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
OUT = ROOT / "defendpro_homepage.html"

PARTS = ["01_head.html", "02_base.css", "03_components.css", "04_body.html"]

BINARY = {
    "PORTRAIT": ("portrait.jpg", "image/jpeg"),
    "FAVICON": ("favicon.png", "image/png"),
    "FONT": ("fonts/inter-latin-wght-normal.woff2", "font/woff2"),
}

VECTOR = {
    "LOGO": "logo.svg",
    "EMBLEM": "emblem.svg",
}


def read(name: str) -> bytes:
    path = ASSETS / name
    if not path.exists():
        raise SystemExit(f"Asset fehlt: {path}")
    return path.read_bytes()


def base64_uri(name: str, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(read(name)).decode("ascii")


def svg_uri(name: str) -> str:
    """SVG als URL-kodierte Data-URI. Kuerzer als base64 und lesbar.

    Die Vektoren tragen fill="currentColor", was fuer die eingebettete
    Verwendung in der Visitenkarte richtig ist. Als Maske hat die Grafik
    keinen CSS-Kontext, deshalb hier eine feste deckende Farbe. Fuer die
    Maske zaehlt ohnehin nur der Alphakanal.
    """
    svg = read(name).decode("utf-8").replace("currentColor", "#000")
    return "data:image/svg+xml," + quote(svg, safe="/:=;,()")


def kontaktfelder() -> dict:
    """Baut aus kontakt.json die Textbausteine der Seite.

    Ein leeres Feld erscheint als gelbe Marke, damit es beim Livegang
    auffaellt. Telefon, LinkedIn und Instagram verschwinden dagegen
    vollstaendig aus Navigation und Fusszeile, solange sie leer sind:
    eine Marke im Seitengeruest waere haesslicher als eine fehlende
    Zeile, und im Kontaktblock steht sie ohnehin.
    """
    cfg = json.loads((ROOT / "kontakt.json").read_text(encoding="utf-8"))
    g = lambda k: str(cfg.get(k, "")).strip()
    esc = htmlmod.escape

    def feld(key: str, label: str) -> str:
        v = g(key)
        return esc(v) if v else f'<span class="todo">[{label}]</span>'

    tel, tel_txt = g("telefon"), g("telefon_anzeige") or g("telefon")
    li, ig = g("linkedin_url"), g("instagram_url")
    endpoint = g("formular_endpoint")

    return {
        "ANSCHRIFT": feld("anschrift", "Anschrift einsetzen"),
        "GEWERBEWORTLAUT": feld("gewerbewortlaut", "Gewerbewortlaut einsetzen"),
        "GISA": feld("gisa", "GISA-Zahl einsetzen"),
        "BEHOERDE": feld("behoerde", "zuständige Bezirksverwaltungsbehörde einsetzen"),
        "HOSTING": feld("hosting", "Hosting-Anbieter einsetzen"),

        "TELEFON_NAV": (f'<a class="nav-tel" href="tel:{esc(tel)}">{esc(tel_txt)}</a>' if tel else ""),
        "TELEFON_KONTAKT": (
            f'<div>Telefon: <a href="tel:{esc(tel)}">{esc(tel_txt)}</a></div>' if tel
            else '<div>Telefon: <span class="todo">[Telefonnummer einsetzen]</span></div>'),
        "TELEFON_FOOTER": (f'<li><a href="tel:{esc(tel)}">{esc(tel_txt)}</a></li>' if tel else ""),

        "LINKEDIN_KONTAKT": (
            f'<div>LinkedIn: <a href="{esc(li)}" rel="noopener">{esc(g("linkedin_text") or li)}</a></div>' if li
            else '<div>LinkedIn: <span class="todo">[LinkedIn-URL einsetzen]</span></div>'),
        "INSTAGRAM_KONTAKT": (
            f'<div>Instagram: <a href="{esc(ig)}" rel="noopener">{esc(g("instagram_text") or ig)}</a></div>' if ig
            else '<div>Instagram: <span class="todo">[Instagram-Handle bestätigen]</span></div>'),

        # Ohne Endpoint bleibt der mailto-Fallback, der nichts zuverlaessig
        # ausliefert. Das ist bewusst kein stiller Zustand: audit.py zaehlt
        # die offenen Marken, und der Build sagt es unten noch einmal.
        "FORM_ACTION": (f'action="{esc(endpoint)}" method="post"' if endpoint
                        else 'action="mailto:matthias.gastgeb@defendpro.at" method="post" enctype="text/plain"'),
        "_endpoint_gesetzt": bool(endpoint),
        "_telefon_gesetzt": bool(tel),
    }


def main() -> None:
    chunks = []
    for name in PARTS:
        path = SRC / name
        if not path.exists():
            raise SystemExit(f"Quellteil fehlt: {path}")
        chunks.append(path.read_text(encoding="utf-8"))
    html = "\n".join(chunks)

    felder = kontaktfelder()
    replacements = {k: base64_uri(n, m) for k, (n, m) in BINARY.items()}
    replacements.update({k: svg_uri(n) for k, n in VECTOR.items()})
    replacements.update({k: v for k, v in felder.items() if not k.startswith("_")})

    for key, uri in replacements.items():
        token = "{{" + key + "}}"
        if token not in html:
            print(f"Hinweis: Platzhalter {token} kommt nicht vor")
            continue
        html = html.replace(token, uri)

    if "{{" in html:
        rest = sorted({p.split("}}")[0] for p in html.split("{{")[1:]})
        raise SystemExit(f"Platzhalter nicht ersetzt: {rest}")

    OUT.write_text(html, encoding="utf-8")
    print(f"geschrieben: {OUT}")
    print(f"groesse:     {len(html.encode('utf-8')) / 1024:.1f} KB")
    print(f"zeilen:      {html.count(chr(10)) + 1}")

    offen = html.count('class="todo"')
    print()
    print(f"offene Angaben aus kontakt.json: {offen}")
    if not felder["_telefon_gesetzt"]:
        print("  ! keine Telefonnummer. Fuer institutionelle Kunden der schnellste Kanal.")
    if not felder["_endpoint_gesetzt"]:
        print("  ! Formular laeuft auf mailto und liefert nichts zuverlaessig aus.")
    if offen == 0 and felder["_endpoint_gesetzt"]:
        print("  alles gesetzt, die Seite ist aus dieser Sicht livegangfaehig.")


if __name__ == "__main__":
    main()
