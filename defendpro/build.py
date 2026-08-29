#!/usr/bin/env python3
"""Setzt die Homepage aus den Quellteilen zu einer eigenstaendigen Datei zusammen.

    python3 build.py

Ergebnis: defendpro_homepage.html im selben Ordner.
Keine externen Requests, keine Abhaengigkeiten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "defendpro_homepage.html"

PARTS = [
    "01_head.html",
    "02_base.css",
    "03_components.css",
    "04_body.html",
]


def main() -> None:
    chunks = []
    for name in PARTS:
        path = SRC / name
        if not path.exists():
            raise SystemExit(f"Quellteil fehlt: {path}")
        chunks.append(path.read_text(encoding="utf-8"))

    html = "\n".join(chunks)
    OUT.write_text(html, encoding="utf-8")

    kb = len(html.encode("utf-8")) / 1024
    print(f"geschrieben: {OUT}")
    print(f"groesse:     {kb:.1f} KB")
    print(f"zeilen:      {html.count(chr(10)) + 1}")


if __name__ == "__main__":
    main()
