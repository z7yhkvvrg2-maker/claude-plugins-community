#!/usr/bin/env python3
"""Baut ein Angebot aus angebot.json und ../kontakt.json.

    python3 angebot/build_angebot.py [angebot.json]

Ergebnis: angebot/angebot.html, Grundlage fuer das PDF.

Firmendaten kommen aus ../kontakt.json und werden hier nicht wiederholt.
Die Angaben zum konkreten Geschaeft stehen in angebot.json. Fuer mehrere
Angebote eine Kopie anlegen und den Pfad uebergeben.

Betraege werden gerechnet, nicht abgetippt. Zwischensumme, Steuer und
Endbetrag ergeben sich aus den Positionen.
"""

import base64
import html as htmlmod
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "angebot.html"
ASSETS = ROOT.parent / "assets"
OUT = ROOT / "angebot.html"

FONTS = {f"FONT_{w}": f"fonts/inter-latin-{w}-normal.woff2" for w in (400, 600, 700, 800)}
VECTORS = {"LOGO": "logo.svg", "EMBLEM": "emblem.svg"}

esc = htmlmod.escape


def read(rel: str) -> bytes:
    p = ASSETS / rel
    if not p.exists():
        raise SystemExit(f"Asset fehlt: {p}")
    return p.read_bytes()


def euro(x: float) -> str:
    """1234.5 -> '1.234,50'. Oesterreichische Schreibweise."""
    return f"{x:,.2f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def datum_lang(iso: str) -> str:
    monate = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli",
              "August", "September", "Oktober", "November", "Dezember"]
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{d.day}. {monate[d.month - 1]} {d.year}"


def main() -> None:
    quelle = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "angebot.json"
    if not quelle.exists():
        raise SystemExit(f"Angebotsdaten fehlen: {quelle}")
    a = json.loads(quelle.read_text(encoding="utf-8"))
    firma = json.loads((ROOT.parent / "kontakt.json").read_text(encoding="utf-8"))

    g = lambda d, k, alt="": str(d.get(k, alt)).strip()

    # --- Positionen und Betraege ---------------------------------------
    zeilen, netto = [], 0.0
    for pos in a.get("positionen", []):
        menge = float(pos.get("menge", 1))
        preis = float(pos.get("preis", 0))
        summe = menge * preis
        netto += summe
        einheit = esc(g(pos, "einheit"))
        besch = g(pos, "beschreibung")
        zeilen.append(
            "<tr><td>"
            f'<div class="bez">{esc(g(pos, "bezeichnung"))}</div>'
            + (f'<div class="besch">{esc(besch)}</div>' if besch else "")
            + "</td>"
            f'<td class="r">{menge:g} {einheit}</td>'
            f'<td class="r">{euro(preis)}</td>'
            f'<td class="r">{euro(summe)}</td></tr>'
        )
    if not zeilen:
        raise SystemExit("Keine Positionen in angebot.json.")

    ust_modus = g(a, "ust_modus", "kleinunternehmer").lower()
    if ust_modus == "kleinunternehmer":
        summe_html = (
            f'<tr><td>Summe</td><td class="r">{euro(netto)}</td></tr>'
            f'<tr class="total"><td>Gesamtbetrag</td><td class="r">{euro(netto)} EUR</td></tr>'
        )
        ust_hinweis = ("Kleinunternehmer nach dem Umsatzsteuergesetz, daher wird keine "
                       "Umsatzsteuer in Rechnung gestellt. Alle Beträge in Euro.")
    else:
        try:
            satz = float(ust_modus)
        except ValueError:
            raise SystemExit(f"ust_modus muss 'kleinunternehmer' oder eine Zahl sein, nicht {ust_modus!r}")
        steuer = netto * satz / 100
        summe_html = (
            f'<tr><td>Nettobetrag</td><td class="r">{euro(netto)}</td></tr>'
            f'<tr><td>Umsatzsteuer {satz:g} %</td><td class="r">{euro(steuer)}</td></tr>'
            f'<tr class="total"><td>Gesamtbetrag</td><td class="r">{euro(netto + steuer)} EUR</td></tr>'
        )
        ust_hinweis = "Alle Beträge in Euro."

    # --- Empfaenger -----------------------------------------------------
    teile = [g(a, "empfaenger_haus"), g(a, "empfaenger_person"),
             g(a, "empfaenger_funktion"), g(a, "empfaenger_anschrift")]
    if not any(teile):
        empf = '<span style="color:#B00">[Empfänger in angebot.json eintragen]</span>'
    else:
        haus = f"<b>{esc(teile[0])}</b>" if teile[0] else ""
        rest = "<br>".join(esc(t) for t in teile[1:] if t)
        empf = "<br>".join(x for x in (haus, rest) if x)

    einleitung = g(a, "einleitung") or (
        "vielen Dank für das Gespräch. Auf dieser Grundlage habe ich Ihnen "
        "das folgende Angebot zusammengestellt.")
    # Anrede nicht aus dem Namen raten. Wer sie setzen will, setzt sie.
    anrede = esc(g(a, "anrede")) or "Sehr geehrte Damen und Herren"
    anrede = f"{anrede},<br><br>"

    zahlungsziel = int(a.get("zahlungsziel_tage", 14))
    storno = int(a.get("storno_frist_tage", 14))
    satz = int(a.get("storno_satz_danach", 50))

    # Die Angebotsart steuert, welche Klauseln gehoeren. Ein Vortrag ohne
    # Uebungen braucht keinen Gesundheitshinweis, und die Abgrenzung zum
    # Safety Check gehoert nur in Angebote, die einen enthalten koennen.
    art = g(a, "art", "training").lower()
    if art not in ("training", "vortrag"):
        raise SystemExit(f"art muss 'training' oder 'vortrag' sein, nicht {art!r}")

    teilnahme = "" if art == "vortrag" else (
        "<section><h2>Teilnahme</h2><p>Die Teilnahme ist freiwillig. Gesundheitliche "
        "Einschränkungen teilen Sie mir vorab mit, dann passe ich den Ablauf an oder lasse "
        "einzelne Übungen weg. Die Übungen lassen sich an unterschiedliche körperliche "
        "Voraussetzungen anpassen.</p></section>")

    abgrenzung = "" if art == "vortrag" else (
        '<section><p class="hinweis"><b>Abgrenzung.</b> Der Safety Check ist ausdrücklich keine '
        "gesetzliche Arbeitsplatzevaluierung, keine Rechtsprüfung und keine Zertifizierung. Er "
        "ersetzt keine dieser Leistungen. Dasselbe gilt für das Training.</p></section>")

    def liste(titel, punkte):
        li = "".join(f"<li>{esc(x)}</li>" for x in punkte)
        return f"<section><h2>{titel}</h2><ul>{li}</ul></section>"

    if art == "vortrag":
        enthalten = liste("Enthalten", [
            "Abstimmung der Inhalte vorab mit dem Veranstalter.",
            "Vortrag vor Ort in der vereinbarten Dauer.",
            "Fragen und Diskussion im Anschluss.",
            "Rückfragen per E-Mail in den vier Wochen danach.",
        ])
        nicht = liste("Nicht enthalten", [
            "Aufzeichnung oder Verbreitung des Vortrags ohne gesonderte Absprache.",
            "Schriftliche Unterlagen für die Teilnehmenden, sofern nicht eigens vereinbart.",
        ])
    else:
        enthalten = liste("Enthalten", [
            "Abstimmung vorab, damit die Übungen zu Ihren Rollen und Situationen passen.",
            "Durchführung vor Ort, in normaler Arbeitskleidung, ohne Vorkenntnisse.",
            "Kurze schriftliche Zusammenfassung der vereinbarten Abläufe nach dem Termin.",
            "Rückfragen per E-Mail in den vier Wochen danach.",
        ])
        nicht = liste("Nicht enthalten", [
            "Eine gesetzliche Arbeitsplatzevaluierung, eine Rechtsprüfung oder eine Zertifizierung.",
            "Raum und Ausstattung. Sie brauchen einen Raum, in dem sich die Gruppe bewegen kann.",
        ])

    bereit = g(a, "bereitstellung")
    bereitstellung = "" if not bereit else (
        f"<section><h2>Was Sie bereitstellen</h2><p>{esc(bereit)}</p></section>")

    ersetzungen = {
        "BETREFF": esc(g(a, "betreff")),
        "NUMMER": esc(g(a, "angebotsnummer")),
        "DATUM": esc(datum_lang(g(a, "datum"))),
        "GUELTIG": esc(datum_lang(g(a, "gueltig_bis"))),
        "EMPFAENGER": empf,
        "EINLEITUNG": anrede + esc(einleitung),
        "POSITIONEN": "\n        ".join(zeilen),
        "SUMME": summe_html,
        "UST_HINWEIS": esc(ust_hinweis),
        "TEILNEHMER": esc(g(a, "teilnehmerzahl", "nach Absprache")),
        "ORT": esc(g(a, "ort", "in Ihrem Haus")),
        "TERMIN": esc(g(a, "termin", "nach Vereinbarung")),
        "ANREISE": "im Preis enthalten" if a.get("anreise_enthalten", True) else "wird gesondert verrechnet",
        "ZAHLUNG": f"{zahlungsziel} Tage nach Rechnung, ohne Abzug",
        "STORNO": f"kostenfrei bis {storno} Tage vor dem Termin, danach {satz} % des Honorars",
        "BILDAUFNAHMEN": esc(g(a, "bildaufnahmen", "nach vorheriger Absprache")),
        "ENTHALTEN_BLOCK": enthalten,
        "NICHT_BLOCK": nicht,
        "TEILNAHME_BLOCK": teilnahme,
        "ABGRENZUNG_BLOCK": abgrenzung,
        "BEREITSTELLUNG_BLOCK": bereitstellung,
        "FIRMA_ANSCHRIFT": esc(g(firma, "anschrift")) or "[Anschrift in kontakt.json]",
        "FIRMA_GEWERBE": esc(g(firma, "gewerbewortlaut")) or "[Gewerbewortlaut in kontakt.json]",
        "FIRMA_GISA": ("GISA " + esc(g(firma, "gisa"))) if g(firma, "gisa") else "[GISA-Zahl in kontakt.json]",
    }

    html = SRC.read_text(encoding="utf-8")
    for key, rel in FONTS.items():
        html = html.replace("{{" + key + "}}",
                            "data:font/woff2;base64," + base64.b64encode(read(rel)).decode("ascii"))
    for key, rel in VECTORS.items():
        svg = read(rel).decode("utf-8").replace("currentColor", "#000")
        html = html.replace("{{" + key + "}}", "data:image/svg+xml," + quote(svg, safe="/:=;,()"))
    for key, val in ersetzungen.items():
        html = html.replace("{{" + key + "}}", val)

    if "{{" in html:
        rest = sorted({p.split("}}")[0] for p in html.split("{{")[1:]})
        raise SystemExit(f"Platzhalter nicht ersetzt: {rest}")

    OUT.write_text(html, encoding="utf-8")
    print(f"geschrieben: {OUT}")
    print(f"Angebot {g(a, 'angebotsnummer')} an {g(a, 'empfaenger_haus') or '[kein Empfänger]'}")
    print(f"Art: {art}, Positionen: {len(zeilen)}, Nettosumme {euro(netto)} EUR, Modus {ust_modus}")
    if netto == 0:
        print("  ! Alle Preise stehen auf 0. In angebot.json eintragen.")
    if not any(teile):
        print("  ! Kein Empfänger eingetragen.")


if __name__ == "__main__":
    main()
