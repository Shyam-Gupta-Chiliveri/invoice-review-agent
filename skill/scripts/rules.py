"""Steps 2–4 — CHECK and DECIDE. Deterministic: same input, same verdict, every finding explained.

Every finding has a stable `code` (used by the evaluation) and a severity:
  block  → money must not leave (wrong account, not an invoice, wrong math, duplicate)
  review → a person has to clarify something before payment
  ok     → check passed (kept so the report shows what was verified)
Decision: no block/review findings → APPROVE, otherwise INVESTIGATE.
"""
from __future__ import annotations

import csv
import io
import re

IBAN_LEN = {"DE": 22, "AT": 20, "CH": 21, "DK": 18, "NL": 18, "FR": 27, "IT": 27, "BE": 16, "PL": 28, "CZ": 24, "LU": 20}
STOP = {"gmbh", "und", "mit", "der", "die", "das", "fuer", "stk", "pcs", "the", "and"}
TOL = 0.02  # € tolerance for rounding


def fold(s):
    return (s or "").lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def tokens(s):
    return [t for t in re.split(r"[^a-z0-9]+", fold(s).replace("-", "")) if len(t) >= 3 and t not in STOP]


def same_vendor(a, b):
    ta, tb = tokens(a), tokens(b)
    return bool(ta) and sum(t in tb for t in ta) / len(ta) >= 0.6


def eur(n):
    if n is None:
        return "—"
    dec = 4 if n and abs(n) < 0.1 else 2
    s = f"{n:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def iban_valid(iban):
    if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{10,30}", iban or ""):
        return False
    r = "".join(str(ord(c) - 55) if c.isalpha() else c for c in iban[4:] + iban[:4])
    return int(r) % 97 == 1


def load_orders(text: str) -> dict:
    """bestellungen.csv → {po: {vendor, lines:[{article, qty, unit}]}}; ; or , separated."""
    sample = text.splitlines()[0]
    reader = csv.DictReader(io.StringIO(text), delimiter=";" if ";" in sample else ",")
    col = lambda row, prefix: next((v for k, v in row.items() if k and k.strip().lower().startswith(prefix)), "")
    orders = {}
    for row in reader:
        po = col(row, "bestell").strip().upper()
        if not po:
            continue
        o = orders.setdefault(po, {"po": po, "vendor": col(row, "liefer").strip(), "lines": []})
        o["lines"].append({"article": col(row, "artikel").strip(),
                           "qty": float(col(row, "menge").replace(",", ".") or 0),
                           "unit": float(col(row, "einzelpreis").replace(",", ".") or 0)})
    return orders


def check(doc: dict, others: list[dict], orders: dict) -> list[dict]:
    F = []

    def add(sev, code, title, detail):
        F.append({"severity": sev, "code": code, "title": title, "detail": detail})

    if doc["needs_reading"]:
        add("review", "NOT_READ", "Document could not be read",
            doc["read_error"] or "No text layer (photo or scan). Run the skill's reading step (SKILL.md) or review manually.")
        return F

    is_inv = doc["doc_kind"] == "invoice" and not doc["not_invoice_note"]
    if doc.get("ocr_conf") is not None:
        add("ok", "OCR", "Read by OCR", f"Photo/scan read with Tesseract (confidence {doc['ocr_conf']:.0f} %); amounts are cross-checked by the arithmetic checks")
    priced = [l for l in doc["lines"] if l["total"] is not None]

    # document type
    if is_inv:
        add("ok", "DOC_TYPE", "Document type", f"{doc['doc_type']} — payable document")
    elif doc["doc_kind"] == "delivery_note":
        add("block", "NOT_AN_INVOICE", "Delivery note, not an invoice", "Lieferschein: no amounts to pay. File as goods receipt and request the invoice.")
    elif doc["doc_kind"] == "quote" or doc["not_invoice_note"]:
        add("block", "NOT_AN_INVOICE", "Quote, not an invoice", "Angebot: the document itself says it is not an invoice. Do not pay.")
    elif doc["doc_kind"] == "credit_note":
        add("review", "CREDIT_NOTE", "Credit note", "Route to credit processing, not payment.")
    else:
        add("review", "UNKNOWN_TYPE", "Unknown document type", "Could not identify the document as an invoice.")

    # §14 UStG mandatory content
    missing = [n for n, ok in [("invoice number", doc["invoice_number"]), ("invoice date", doc["date"]),
                               ("tax no. / VAT ID", doc["tax_id"])] if not ok]
    if is_inv:
        missing += [n for n, ok in [("gross total", doc["gross"] is not None),
                                    ("VAT amount", doc["vat"] is not None or doc["reverse_charge"]),
                                    ("priced line items", bool(priced)), ("IBAN", doc["iban"])] if not ok]
    if missing and is_inv:
        note = ' — only says "Nettobetrag zzgl. gesetzlicher Umsatzsteuer"' if doc["net_only_note"] else ""
        add("review", "MISSING_FIELDS", "Mandatory fields missing (§14 UStG)", "Missing: " + ", ".join(missing) + note)
    elif is_inv:
        add("ok", "MANDATORY", "Mandatory fields (§14 UStG)", "All present")

    # line arithmetic
    if priced:
        bad = []
        for l in priced:
            if l["qty"] is None or l["unit_price"] is None:
                continue
            raw = l.get("unit_price_raw") or ""
            decimals = len(re.split(r"[.,]", raw)[-1]) if raw else 4
            tol = l["qty"] * 0.005 + 0.01 if decimals <= 2 else TOL   # unit price printed rounded to 2 dp
            if abs(l["qty"] * l["unit_price"] - l["total"]) > tol:
                bad.append(f"Pos {l['pos']}: {eur(l['qty'])} × {eur(l['unit_price'])} ≠ {eur(l['total'])}")
        s = round(sum(l["total"] for l in priced), 2)
        if doc["net"] is not None and abs(s - doc["net"]) > TOL:
            bad.append(f"lines add up to €{eur(s)}, document states net €{eur(doc['net'])} (Δ €{eur(round(doc['net'] - s, 2))})")
        if bad:
            add("block", "MATH_ERROR", "Arithmetic error", "; ".join(bad))
        else:
            add("ok", "MATH", "Line arithmetic", f"{len(priced)} line(s) recomputed, sum €{eur(s)} = net")

    # VAT and gross
    if is_inv and doc["net"] is not None:
        if doc["reverse_charge"]:
            if doc["vat"]:
                add("block", "VAT_ERROR", "VAT on reverse-charge invoice", f"Reverse charge stated but €{eur(doc['vat'])} VAT charged")
            else:
                add("ok", "VAT", "VAT", f"Reverse charge §13b UStG: 0 % VAT, Quellberg self-assesses 19 % (€{eur(round(doc['net'] * .19, 2))})")
        elif doc["vat"] is not None and doc["vat_rate"] is not None:
            exp = round(doc["net"] * doc["vat_rate"] / 100, 2)
            if abs(doc["vat"] - exp) > TOL:
                add("block", "VAT_ERROR", "VAT miscalculated",
                    f"€{eur(doc['net'])} × {doc['vat_rate']:g} % = €{eur(exp)}, document states €{eur(doc['vat'])} (Δ €{eur(round(doc['vat'] - exp, 2))})")
            else:
                add("ok", "VAT", "VAT", f"€{eur(doc['net'])} × {doc['vat_rate']:g} % = €{eur(exp)}")
        if doc["gross"] is not None:
            exp = round(doc["net"] + (doc["vat"] or 0), 2)
            if abs(exp - doc["gross"]) > TOL:
                add("block", "GROSS_ERROR", "Gross total wrong", f"net + VAT = €{eur(exp)}, document states €{eur(doc['gross'])}")
            else:
                add("ok", "GROSS", "Gross total", f"€{eur(doc['gross'])}")

    # purchase order
    po = orders.get(doc["po"]) if doc["po"] else None
    doc["po_match"] = None
    if not doc["po"]:
        known = next((o for o in orders.values() if same_vendor(o["vendor"], doc["vendor"] or "")), None)
        add("review", "NO_PO", "No purchase order",
            f"No order number on the document" + (f" (vendor has open order {known['po']})" if known else "; vendor has no open order in bestellungen.csv")
            + ". Needs approval by the budget owner.")
    elif not po:
        add("block", "PO_UNKNOWN", "Unknown order number", f"{doc['po']} is not in bestellungen.csv")
    else:
        if not any(t in tokens(doc["vendor"]) for t in tokens(po["vendor"])):
            add("block", "PO_WRONG_VENDOR", "Order belongs to another vendor", f"{doc['po']} is for {po['vendor']}, not {doc['vendor']}")
        else:
            add("ok", "PO", "Purchase order", f"{doc['po']} — {po['vendor']}")
        used, match = set(), []
        for pl in po["lines"]:
            pt = tokens(pl["article"])
            hits = [l for l in doc["lines"] if pt and sum(t in tokens(l["description"]) for t in pt) / len(pt) >= 0.5]
            used.update(id(h) for h in hits)
            qty = sum(h["qty"] or 0 for h in hits)
            val = sum(h["total"] or 0 for h in hits)
            unit = val / qty if qty and all(h["total"] is not None for h in hits) else None
            match.append({"article": pl["article"], "po_qty": pl["qty"], "po_unit": pl["unit"], "doc_qty": qty,
                          "doc_unit": unit, "lines": [h["pos"] for h in hits]})
            if pl["unit"] == 0:
                add("review", "PO_NO_VALUE", "Order has no approved value",
                    f"{doc['po']} (\"{pl['article']}\") is a framework order at €0,00 — net €{eur(doc['net'])} over {len(doc['lines'])} items has no budget approval.")
                continue
            if not hits:
                add("review", "PO_ITEM_MISSING", "Ordered item not on document", f'"{pl["article"]}" not found'); continue
            if qty > pl["qty"]:
                add("review", "QTY_OVER", "More delivered/billed than ordered",
                    f"Ordered {eur(pl['qty'])}, document {eur(qty)} (+{eur(qty - pl['qty'])}, ≈ +€{eur(round((qty - pl['qty']) * (unit or pl['unit']), 2))})")
            else:
                add("ok", "QTY", "Quantity vs order", f"{eur(qty)} of {eur(pl['qty'])} ordered")
            if unit is not None:
                dev = (unit - pl["unit"]) / pl["unit"]
                if abs(dev) > 0.005:
                    add("review", "PRICE_DEVIATION", "Unit price differs from order", f"Order €{eur(pl['unit'])}, billed €{eur(round(unit, 4))} ({dev * 100:+.1f} %)")
                else:
                    add("ok", "PRICE", "Unit price vs order", f"€{eur(pl['unit'])}")
        doc["po_match"] = match
        extras = [l for l in doc["lines"] if id(l) not in used]
        if extras and not all(pl["unit"] == 0 for pl in po["lines"]):
            v = round(sum(l["total"] or 0 for l in extras), 2)
            add("review", "ITEMS_NOT_ORDERED", "Items not on the order",
                "; ".join(f'Pos {l["pos"]} "{l["description"]}"' + (f" €{eur(l['total'])}" if l["total"] is not None else "") for l in extras)
                + (f" — €{eur(v)} not covered by {doc['po']}" if v else ""))
        po_val = round(sum(l["qty"] * l["unit"] for l in po["lines"]), 2)
        if po_val and doc["net"] is not None and doc["net"] > po_val + TOL:
            add("review", "OVER_PO_VALUE", "Net exceeds order value", f"Order €{eur(po_val)}, document €{eur(doc['net'])} (+€{eur(round(doc['net'] - po_val, 2))})")

    # IBAN
    if doc["iban"]:
        cc = doc["iban"][:2]
        len_ok = cc not in IBAN_LEN or IBAN_LEN[cc] == len(doc["iban"])
        if len_ok and iban_valid(doc["iban"]):
            add("ok", "IBAN", "IBAN checksum", "ISO 13616 mod-97 valid")
        else:
            add("block", "IBAN_INVALID", "IBAN is not a valid account",
                f"{doc['iban']} — " + ("wrong length" if not len_ok else "mod-97 checksum fails") + ": tampered or mistyped.")
        ring = sorted({o["vendor"] for o in others if o.get("iban") == doc["iban"] and not same_vendor(o["vendor"] or "", doc["vendor"] or "")})
        doc["iban_shared_with"] = ring
        if ring:
            add("block", "IBAN_SHARED", "Bank account shared with other vendors",
                f"Same IBAN on documents from {len(ring)} other vendor(s): {', '.join(ring)}. Independent suppliers do not share an account — verify by phone before paying.")
    else:
        doc["iban_shared_with"] = []

    # duplicates within the batch
    if is_inv:
        for o in others:
            if o["doc_kind"] != "invoice" or not same_vendor(o["vendor"] or "", doc["vendor"] or ""):
                continue
            same_no = o["invoice_number"] and o["invoice_number"] == doc["invoice_number"]
            same_amt = o["gross"] is not None and doc["gross"] is not None and abs(o["gross"] - doc["gross"]) < 0.01 and (o["po"] or "") == (doc["po"] or "")
            if same_no or same_amt:
                later = (doc["date"] or "", doc["file"]) > (o["date"] or "", o["file"])
                if later:
                    add("block", "DUPLICATE", "Duplicate invoice",
                        f"Repeats {o['invoice_number']} ({o['date']}, {o['file']}): same vendor, same {'number' if same_no else 'order and amount'} €{eur(doc['gross'])}.")
                else:
                    add("review", "HAS_DUPLICATE", "A later duplicate exists", f"{o['invoice_number']} ({o['file']}) repeats this invoice — pay once.")
                break
    return F


def decide(doc: dict, findings: list[dict]) -> dict:
    block = [f for f in findings if f["severity"] == "block"]
    review = [f for f in findings if f["severity"] == "review"]
    if not block and not review:
        return {"decision": "APPROVE", "priority": "", "summary": f"All checks passed — release €{eur(doc['gross'])}."}
    top = (block or review)[:3]
    return {
        "decision": "INVESTIGATE",
        "priority": "HIGH" if block else "NORMAL",
        "summary": ("Do not pay: " if block else "Clarify before paying: ") + "; ".join(f["title"] for f in top)
                   + (f" (+{len(block) + len(review) - len(top)} more)" if len(block) + len(review) > len(top) else ""),
    }
