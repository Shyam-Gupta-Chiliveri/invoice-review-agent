#!/usr/bin/env python3
"""Generate unseen test receipts with ONE known, planted problem each (or none).

Two layouts (German / English, different labels, number and date formats) so the
reader is not tuned to the 16 sample files. Ground truth goes to eval/unseen/expected.json.

    python eval/make_unseen.py          # writes eval/unseen/
"""
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OUT = Path(__file__).resolve().parent / "unseen"
W, H = A4


def iban_de(blz, kto):
    bban = blz + kto.zfill(10)
    return f"DE{98 - int(bban + '131400') % 97:02d}{bban}"


def de(n, dec=2):
    s = f"{n:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def en(n, dec=2):
    return f"{n:,.{dec}f}"


ORDERS = """Bestellnummer;Lieferant;Artikel;Menge;Einzelpreis_netto_EUR
QB-20001;Druckpartner Süd GmbH;Werbeflyer Herbstaktion A5;20000;0.038
QB-20002;Baltic Closures OÜ;Crown caps matte black 26mm;100000;0.0125
QB-20003;Etikettenwerk Lindau GmbH;Rollenetikett Ingwer 0,33l;50000;0.019
QB-20004;Kistenbau Oberpfalz GmbH;Mehrwegkiste 24x0,33l blau;800;6.40
QB-20005;Sirupmanufaktur Allgäu GmbH;Holunderblütensirup Bio 10l;40;58.00
QB-20006;Etikettenwerk Lindau GmbH;Rollenetikett Minze 0,5l;30000;0.022
QB-20007;Tankservice Mitte GmbH;CIP-Reinigung Abfülllinie;2;890.00
"""

V = {  # vendor → (city, tax id, iban)
    "Druckpartner Süd GmbH": ("München", "DE 297 114 562", iban_de("70020270", "15384920")),
    "Baltic Closures OÜ": ("Tallinn, Estland", "EE 102 334 556", "EE382200221020145685"),
    "Etikettenwerk Lindau GmbH": ("Lindau", "DE 311 208 774", iban_de("73350000", "310044")),
    "Kistenbau Oberpfalz GmbH": ("Amberg", "DE 145 662 019", iban_de("75250000", "190077823")),
    "Sirupmanufaktur Allgäu GmbH": ("Kempten", "DE 219 554 803", iban_de("73350000", "514221")),
    "Tankservice Mitte GmbH": ("Fulda", "DE 266 401 117", iban_de("53050180", "49920113")),
    "Getränkelogistik Weber KG": ("Deggendorf", "DE 158 337 640", iban_de("74150000", "380011")),
}


def german(path, vendor, no, date, po, lines, rate=19, vat_override=None, net_override=None, title="Rechnung",
           iban=None, gross=True, priced=True):
    city, tax, ib = V[vendor]
    iban = iban or ib
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont("Helvetica-Bold", 17); c.drawString(50, H - 60, vendor)
    c.setFont("Helvetica-Bold", 16); c.drawRightString(W - 50, H - 60, title)
    c.setFont("Helvetica", 9); c.drawString(50, H - 76, city)
    y = H - 80
    for t in [f"{'Lieferscheinnr.' if title == 'Lieferschein' else 'Rechnungsnummer:'} {no}", f"Rechnungsdatum: {date}"] + ([f"Bestellnummer: {po}"] if po else []):
        y -= 13; c.drawRightString(W - 50, y, t)
    c.drawString(50, H - 140, f"USt-IdNr.: {tax}")
    c.drawString(50, H - 168, "An: Quellberg GmbH, Getränkemanufaktur, Limonadenweg 3, 94032 Passau")
    y = H - 205; c.setFont("Helvetica-Bold", 9)
    for x, t in [(50, "Pos"), (80, "Beschreibung"), (360, "Menge"), (425, "Einzelpreis"), (505, "Gesamt")]:
        c.drawString(x, y, t)
    c.setFont("Helvetica", 9)
    net = 0
    for i, (d, q, u) in enumerate(lines, 1):
        y -= 17; t = round(q * u, 2); net += t
        c.drawString(50, y, str(i)); c.drawString(80, y, d); c.drawString(360, y, de(q, 0))
        if priced:
            c.drawString(425, y, de(u, 4 if u < 0.1 else 2)); c.drawString(505, y, de(t))
    if priced:
        net = round(net_override if net_override is not None else net, 2)
        vat = round(vat_override if vat_override is not None else net * rate / 100, 2)
        y -= 36; c.drawString(370, y, "Nettobetrag"); c.drawRightString(W - 50, y, f"€ {de(net)}")
        y -= 15; c.drawString(370, y, f"zzgl. {rate}% MwSt"); c.drawRightString(W - 50, y, f"€ {de(vat)}")
        if gross:
            y -= 16; c.setFont("Helvetica-Bold", 10); c.drawString(370, y, "Rechnungsbetrag"); c.drawRightString(W - 50, y, f"€ {de(net + vat)}")
    c.setFont("Helvetica", 8)
    c.drawString(50, 60, f"{vendor} · {city}" + (f" · IBAN: {' '.join(iban[i:i + 4] for i in range(0, len(iban), 4))}" if priced else ""))
    c.save()


def english(path, vendor, no, date, po, lines, iban=None):
    city, tax, ib = V[vendor]
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont("Helvetica-Bold", 17); c.drawString(50, H - 60, f"{vendor} Invoice")
    c.setFont("Helvetica", 9); c.drawString(50, H - 76, city)
    c.drawString(50, H - 100, f"Invoice No. {no}"); c.drawString(50, H - 113, f"Date: {date}")
    if po:
        c.drawString(50, H - 126, f"PO: {po}")
    c.drawString(330, H - 100, f"VAT-ID: {tax}"); c.drawString(330, H - 113, "Bill to: Quellberg GmbH, 94032 Passau")
    y = H - 165; c.setFont("Helvetica-Bold", 9)
    for x, t in [(50, "Pos"), (80, "Description"), (350, "Qty"), (420, "Unit price"), (505, "Amount")]:
        c.drawString(x, y, t)
    c.setFont("Helvetica", 9); net = 0
    for i, (d, q, u) in enumerate(lines, 1):
        y -= 17; t = round(q * u, 2); net += t
        c.drawString(50, y, str(i)); c.drawString(80, y, d); c.drawString(350, y, en(q, 0)); c.drawString(420, y, en(u, 4)); c.drawString(505, y, en(t))
    y -= 36; c.drawString(360, y, "Net amount"); c.drawRightString(W - 50, y, f"EUR {en(net)}")
    y -= 15; c.drawString(360, y, "VAT (Reverse Charge, §13b UStG)"); c.drawRightString(W - 50, y, "EUR 0.00")
    y -= 16; c.setFont("Helvetica-Bold", 10); c.drawString(360, y, "Total due"); c.drawRightString(W - 50, y, f"EUR {en(net)}")
    c.setFont("Helvetica", 8); c.drawString(50, 60, f"{vendor} · {city} · IBAN: {iban or ib}")
    c.save()


def scanned(src_pdf, path):
    """Image-only PDF (simulates a scan): render the page and embed only the picture."""
    import pdfplumber
    png = path.with_suffix(".tmp.png")
    with pdfplumber.open(src_pdf) as pdf:
        pdf.pages[0].to_image(resolution=110).save(png)
    c = canvas.Canvas(str(path), pagesize=A4); c.drawImage(str(png), 0, 0, W, H); c.save(); png.unlink()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in OUT.glob("*"):
        p.unlink()
    (OUT / "bestellungen.csv").write_text(ORDERS, encoding="utf-8")
    exp = {}

    def case(name, decision, codes, note):
        exp[name] = {"decision": decision, "must_find": codes, "planted": note}

    german(OUT / "u01_druckpartner_clean.pdf", "Druckpartner Süd GmbH", "R-26-0815", "03.07.2026", "QB-20001",
           [("Werbeflyer Herbstaktion A5, 4/4-farbig", 20000, 0.038)])
    case("u01_druckpartner_clean.pdf", "APPROVE", [], "nothing — matches order exactly")
    english(OUT / "u02_baltic_clean_reverse_charge.pdf", "Baltic Closures OÜ", "BC-2026-0412", "2026-07-04", "QB-20002",
            [("Crown caps matte black 26mm", 100000, 0.0125)])
    case("u02_baltic_clean_reverse_charge.pdf", "APPROVE", [], "nothing — EU reverse charge, 0 % VAT is correct")
    german(OUT / "u03_etikettenwerk_vat.pdf", "Etikettenwerk Lindau GmbH", "EL-55120", "05.07.2026", "QB-20003",
           [("Rollenetikett Ingwer 0,33l", 50000, 0.019)], vat_override=185.50)
    case("u03_etikettenwerk_vat.pdf", "INVESTIGATE", ["VAT_ERROR"], "VAT €185,50 instead of €180,50")
    german(OUT / "u04_kistenbau_qty.pdf", "Kistenbau Oberpfalz GmbH", "KO-2026-311", "06.07.2026", "QB-20004",
           [("Mehrwegkiste 24x0,33l blau", 950, 6.40)])
    case("u04_kistenbau_qty.pdf", "INVESTIGATE", ["QTY_OVER"], "950 crates billed, 800 ordered")
    german(OUT / "u05_sirup_price.pdf", "Sirupmanufaktur Allgäu GmbH", "SA-7781", "07.07.2026", "QB-20005",
           [("Holunderblütensirup Bio 10l Kanister", 40, 63.50)], rate=7)
    case("u05_sirup_price.pdf", "INVESTIGATE", ["PRICE_DEVIATION"], "unit price €63,50 vs ordered €58,00")
    german(OUT / "u06_tankservice_iban.pdf", "Tankservice Mitte GmbH", "TM-1190", "08.07.2026", "QB-20007",
           [("CIP-Reinigung Abfülllinie", 2, 890.00)], iban=V["Tankservice Mitte GmbH"][2][:-3] + "117")
    case("u06_tankservice_iban.pdf", "INVESTIGATE", ["IBAN_INVALID"], "one digit of the IBAN changed")
    german(OUT / "u07_etikettenwerk_minze.pdf", "Etikettenwerk Lindau GmbH", "EL-55131", "09.07.2026", "QB-20006",
           [("Rollenetikett Minze 0,5l", 30000, 0.022)])
    case("u07_etikettenwerk_minze.pdf", "INVESTIGATE", ["HAS_DUPLICATE"], "original of a duplicate (u08)")
    german(OUT / "u08_etikettenwerk_minze_dup.pdf", "Etikettenwerk Lindau GmbH", "EL-55131", "16.07.2026", "QB-20006",
           [("Rollenetikett Minze 0,5l", 30000, 0.022)])
    case("u08_etikettenwerk_minze_dup.pdf", "INVESTIGATE", ["DUPLICATE"], "same invoice number sent again a week later")
    german(OUT / "u09_kistenbau_lieferschein.pdf", "Kistenbau Oberpfalz GmbH", "LS-4410", "10.07.2026", "QB-20004",
           [("Mehrwegkiste 24x0,33l blau", 800, 6.40)], title="Lieferschein", priced=False)
    case("u09_kistenbau_lieferschein.pdf", "INVESTIGATE", ["NOT_AN_INVOICE"], "delivery note")
    german(OUT / "u10_weber_no_po.pdf", "Getränkelogistik Weber KG", "W-2026-090", "11.07.2026", None,
           [("Palettentransport Passau–Regensburg", 12, 58.00), ("Mautpauschale", 1, 96.00)])
    case("u10_weber_no_po.pdf", "INVESTIGATE", ["NO_PO"], "no purchase order")
    german(OUT / "u11_sirup_sum.pdf", "Sirupmanufaktur Allgäu GmbH", "SA-7790", "12.07.2026", "QB-20005",
           [("Holunderblütensirup Bio 10l Kanister", 40, 58.00)], rate=7, net_override=2370.00)
    case("u11_sirup_sum.pdf", "INVESTIGATE", ["MATH_ERROR"], "net printed €2.370,00, lines add up to €2.320,00")
    german(OUT / "u12_druckpartner_extra.pdf", "Druckpartner Süd GmbH", "R-26-0844", "13.07.2026", "QB-20001",
           [("Werbeflyer Herbstaktion A5, 4/4-farbig", 20000, 0.038), ("Expresszuschlag", 1, 120.00)])
    case("u12_druckpartner_extra.pdf", "INVESTIGATE", ["ITEMS_NOT_ORDERED"], "express surcharge not on the order")
    german(OUT / "_src_scan.pdf", "Tankservice Mitte GmbH", "TM-1201", "14.07.2026", "QB-20007",
           [("CIP-Reinigung Abfülllinie", 1, 890.00)])
    scanned(OUT / "_src_scan.pdf", OUT / "u13_tankservice_scan.pdf"); (OUT / "_src_scan.pdf").unlink()
    case("u13_tankservice_scan.pdf", "INVESTIGATE", ["NOT_READ"], "low-resolution scan: OCR misreads digits, so it must go to Claude's reading step, never be guessed")

    (OUT / "expected.json").write_text(json.dumps(exp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(exp)} receipts + bestellungen.csv to {OUT}")


if __name__ == "__main__":
    main()
