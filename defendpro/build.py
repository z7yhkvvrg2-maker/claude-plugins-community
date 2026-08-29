#!/usr/bin/env python3
"""Setzt die Homepage aus den Quellteilen zu einer eigenstaendigen Datei zusammen.

    python3 build.py

Ergebnis: defendpro_homepage.html im selben Ordner.
Alle Bilder wandern als base64 in die Datei. Kein externer Request,
keine Abhaengigkeiten ausserhalb der Standardbibliothek.

Platzhalter in den Quellteilen:

    {{LOGO}}         Wortmarke Defend Pro, Lockup mit Emblem
    {{EMBLEM}}       Emblem gross, Wasserzeichen und Buchcover
    {{EMBLEM_MARK}}  Emblem klein, Aufzaehlungszeichen
    {{PORTRAIT}}     Portraet Matthias Gastgeb
    {{FAVICON}}      Favicon, Emblem auf Navy

Logo und Emblem werden als CSS-Maske eingesetzt. Ausgewertet wird nur der
Alphakanal, die Farbe kommt aus dem Designsystem. Dadurch traegt dieselbe
Datei die weisse Fassung auf Navy und die dunkle auf Bone.
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
OUT = ROOT / "defendpro_homepage.html"

PARTS = ["01_head.html", "02_base.css", "03_components.css", "04_body.html"]

ASSET_MAP = {
    "LOGO": ("logo.png", "image/png"),
    "EMBLEM": ("emblem.png", "image/png"),
    "EMBLEM_MARK": ("emblem_mark.png", "image/png"),
    "PORTRAIT": ("portrait.jpg", "image/jpeg"),
    "FAVICON": ("favicon.png", "image/png"),
}


def data_uri(name: str, mime: str) -> str:
    path = ASSETS / name
    if not path.exists():
        raise SystemExit(f"Asset fehlt: {path}")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    chunks = []
    for name in PARTS:
        path = SRC / name
        if not path.exists():
            raise SystemExit(f"Quellteil fehlt: {path}")
        chunks.append(path.read_text(encoding="utf-8"))
    html = "\n".join(chunks)

    for key, (name, mime) in ASSET_MAP.items():
        token = "{{" + key + "}}"
        if token not in html:
            print(f"Hinweis: Platzhalter {token} kommt nicht vor")
            continue
        html = html.replace(token, data_uri(name, mime))

    leftover = [k for k in ASSET_MAP if "{{" + k + "}}" in html]
    if leftover:
        raise SystemExit(f"Platzhalter nicht ersetzt: {leftover}")

    OUT.write_text(html, encoding="utf-8")
    print(f"geschrieben: {OUT}")
    print(f"groesse:     {len(html.encode('utf-8')) / 1024:.1f} KB")
    print(f"zeilen:      {html.count(chr(10)) + 1}")


if __name__ == "__main__":
    main()
