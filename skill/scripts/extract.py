"""Step 1 — READ: turn one receipt into structured fields.

PDFs with a text layer are parsed deterministically (pdfplumber).
Photos and scans have no text layer: the skill asks Claude to read the image
and write a JSON file with the same fields (see SKILL.md). That JSON is picked
up here, so every document ends up in the same shape before any rule runs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic"}
DOC_EXT = IMAGE_EXT | {".pdf"}

DOC_TYPES = {
    "rechnung": "invoice", "invoice": "invoice",
    "lieferschein": "delivery_note", "delivery note": "delivery_note",
    "angebot": "quote", "quotation": "quote", "proforma": "quote",
    "gutschrift": "credit_note", "credit note": "credit_note",
    "mahnung": "reminder",
}


# ── numbers: 1.680,00 · 80.000 · 0,021 · 1,875.00 · 150,000 ──────────────
def num(s):
    if s is None:
        return None
    s = re.sub(r"[€\s]|EUR", "", str(s).strip())
    if not re.fullmatch(r"-?[\d.,]*\d[\d.,]*", s):
        return None
    lc, ld = s.rfind(","), s.rfind(".")
    if lc > -1 and ld > -1:
        dec = "," if lc > ld else "."
        th = "." if dec == "," else ","
        return float(s.replace(th, "").replace(dec, "."))
    sep = "," if lc > -1 else "." if ld > -1 else None
    if not sep:
        return float(s)
    parts = s.split(sep)
    if len(parts) > 2:                                   # 1.500.000
        return float("".join(parts))
    if len(parts[1]) == 3 and parts[0] not in ("0", "-0"):  # 80.000 / 150,000
        return float("".join(parts))
    return float(parts[0] + "." + parts[1])               # 0,021 / 41,17


def _is_num_tok(t):
    return re.fullmatch(r"-?\d[\d.,]*", t) is not None


def empty_doc(path: Path) -> dict:
    return {
        "file": path.name, "source": None, "doc_type": None, "doc_kind": "unknown",
        "not_invoice_note": False, "vendor": None, "city": None, "invoice_number": None,
        "date": None, "po": None, "tax_id": None, "iban": None, "net": None, "vat_rate": None,
        "vat": None, "gross": None, "reverse_charge": False, "net_only_note": False,
        "payment_terms": None, "lines": [], "needs_reading": False, "read_error": None,
    }


# ── text → fields ─────────────────────────────────────────────────────────
def parse_text(lines: list[str], doc: dict) -> dict:
    text = "\n".join(lines)
    first = lines[0] if lines else ""

    m = re.search(r"\b(Gutschrift|Lieferschein|Angebot|Proforma|Mahnung|Rechnung|Invoice|Credit Note|Quotation|Delivery Note)\b", text, re.I)
    doc["doc_type"] = m.group(1) if m else None
    doc["doc_kind"] = DOC_TYPES.get(m.group(1).lower(), "unknown") if m else "unknown"
    doc["not_invoice_note"] = bool(re.search(r"nicht um eine Rechnung|not an invoice", text, re.I))

    vendor = first
    if doc["doc_type"]:
        vendor = re.sub(r"\s*\b" + re.escape(doc["doc_type"]) + r"\b\s*$", "", first, flags=re.I).strip()
    doc["vendor"] = vendor or None
    doc["city"] = re.split(r"\s+(Rechnungsnr|Invoice|Lieferschein|Angebot)", lines[1])[0].strip() if len(lines) > 1 else None

    def grab(pattern, group=1):
        r = re.search(pattern, text, re.I)
        return r.group(group).strip() if r else None

    doc["invoice_number"] = grab(r"(?:Rechnungsnr\.?|Rechnungsnummer|Rechnung Nr\.?|Invoice No\.?|Invoice Number|Lieferscheinnr\.?|Angebotsnr\.?|Beleg-?nr\.?)\s*:?\s*([A-Z0-9][A-Z0-9\-/.]*)")
    d = grab(r"(?:Rechnungsdatum|Datum|Invoice Date|Date)\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{1,2}\.\d{1,2}\.\d{2,4})")
    if d and "." in d:
        dd, mm, yy = d.split(".")
        d = f"{'20' + yy if len(yy) == 2 else yy}-{mm.zfill(2)}-{dd.zfill(2)}"
    doc["date"] = d
    po = grab(r"\b(QB-\d{3,})\b") or grab(r"(?:Bestellnr\.?|Bestellnummer|PO(?: No\.?)?|Order No\.?)\s*:?\s*([A-Z0-9\-]{4,})")
    doc["po"] = po.upper() if po else None
    tax = grab(r"(?:Steuernr\.?|Steuernummer|USt-?IdNr\.?|VAT-?ID|VAT Reg\.? No\.?)\s*:?\s*([A-Z]{2}[\s\d]{6,16}\d|\d{2,3}/\d{3}/\d{4,5})")
    doc["tax_id"] = re.sub(r"\s+", " ", tax) if tax else None
    ib = grab(r"IBAN\s*:?\s*([A-Z]{2}\d{2}(?:\s?[A-Z0-9]){10,30})")
    doc["iban"] = re.sub(r"\s+", "", ib) if ib else None

    amt = r"(-?[\d.,]*\d)"
    doc["net"] = num(grab(r"(?:Nettobetrag|Netto|Zwischensumme|Net amount|Subtotal)[^\n\d]*?(?:€|EUR)?\s*" + amt))
    doc["reverse_charge"] = bool(re.search(r"Reverse Charge|§\s*13b|Steuerschuldnerschaft des Leistungsempf", text, re.I))
    vat_line = next((l for l in lines if re.search(r"(USt|MwSt|Umsatzsteuer|VAT)\b.*\d", l, re.I)
                     and not re.search(r"VAT-?ID|USt-?IdNr|Steuernr|Recipient", l, re.I)), None)
    if vat_line:
        r = re.search(r"(\d{1,2}(?:[.,]\d)?)\s*%", vat_line)
        nums = re.findall(r"-?[\d.,]*\d", vat_line)
        doc["vat_rate"] = num(r.group(1)) if r else (0.0 if doc["reverse_charge"] else None)
        doc["vat"] = num(nums[-1]) if nums and not (r and len(nums) == 1) else None
    doc["gross"] = num(grab(r"(?:Gesamtbetrag(?: brutto)?|Rechnungsbetrag|Bruttobetrag|Total(?: due| amount)?(?: \(Reverse Charge\))?|Zu zahlen|Endbetrag)[^\n\d]*?(?:€|EUR)?\s*" + amt))
    doc["payment_terms"] = grab(r"(?:Zahlungsbedingungen|Payment terms)\s*:?\s*([^\n]+)")
    doc["net_only_note"] = bool(re.search(r"Zahlbar:\s*Nettobetrag zzgl", text, re.I))

    # line items: between the "Pos … Bezeichnung/Menge" header and the totals
    h = next((i for i, l in enumerate(lines) if re.search(r"\bPos\b", l, re.I)
              and re.search(r"Bezeichnung|Beschreibung|Artikel|Description|Menge", l, re.I)), None)
    if h is not None:
        end = next((i for i, l in enumerate(lines) if i > h and re.match(r"(Nettobetrag|Netto|Zwischensumme|Net amount|Subtotal|Summe)", l, re.I)), len(lines))
        for l in lines[h + 1:end]:
            t = l.split()
            if not t or not re.fullmatch(r"\d{1,3}", t[0]):
                if doc["lines"] and "IBAN" not in l and "·" not in l:
                    doc["lines"][-1]["description"] += " " + l      # wrapped description
                continue
            k, tail = len(t), []
            while k > 1 and _is_num_tok(t[k - 1]) and len(tail) < 3:
                k -= 1
                tail.insert(0, t[k])
            desc = " ".join(t[1:k])
            if not desc:
                continue
            row = {"pos": int(t[0]), "description": desc, "qty": None, "unit_price": None, "total": None, "unit_price_raw": None}
            if len(tail) == 3:
                row.update(qty=num(tail[0]), unit_price=num(tail[1]), total=num(tail[2]), unit_price_raw=tail[1])
            elif len(tail) == 2:
                row.update(qty=num(tail[0]), total=num(tail[1]))
                row["unit_price"] = round(row["total"] / row["qty"], 4) if row["qty"] else None
            elif len(tail) == 1:
                row["qty"] = num(tail[0])
            doc["lines"].append(row)
    return doc


def from_json(data: dict, doc: dict) -> dict:
    """Fields written by Claude (or an API vision call) after reading an image."""
    for k in ("doc_type", "vendor", "city", "invoice_number", "date", "po", "tax_id", "payment_terms"):
        if data.get(k) not in (None, ""):
            doc[k] = str(data[k]).strip()
    for k in ("net", "vat_rate", "vat", "gross"):
        if data.get(k) is not None:
            doc[k] = float(data[k])
    doc["reverse_charge"] = bool(data.get("reverse_charge", False))
    doc["not_invoice_note"] = bool(data.get("not_invoice_note", False))
    if data.get("iban"):
        doc["iban"] = re.sub(r"\s+", "", str(data["iban"])).upper()
    if doc["po"]:
        doc["po"] = doc["po"].upper()
    doc["doc_kind"] = DOC_TYPES.get((doc["doc_type"] or "").lower(), "unknown")
    for i, l in enumerate(data.get("lines") or [], 1):
        doc["lines"].append({
            "pos": int(l.get("pos") or i), "description": str(l.get("description", "")),
            "qty": None if l.get("qty") is None else float(l["qty"]),
            "unit_price": None if l.get("unit_price") is None else float(l["unit_price"]),
            "total": None if l.get("total") is None else float(l["total"]),
            "unit_price_raw": None,
        })
    return doc


def read_document(path: Path, extracted_dir: Path | None) -> dict:
    doc = empty_doc(path)
    sidecar = extracted_dir / (path.name + ".json") if extracted_dir else None
    if sidecar and sidecar.exists():                       # read by Claude (vision)
        doc["source"] = "vision:" + sidecar.name
        try:
            return from_json(json.loads(sidecar.read_text(encoding="utf-8")), doc)
        except Exception as e:                            # noqa: BLE001
            doc["read_error"] = f"bad extraction file {sidecar.name}: {e}"
            doc["needs_reading"] = True
            return doc
    if path.suffix.lower() in IMAGE_EXT:
        doc["needs_reading"] = True
        doc["source"] = "image"
        return doc
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            lines = []
            for page in pdf.pages:
                lines += [l.strip() for l in (page.extract_text() or "").splitlines() if l.strip()]
    except Exception as e:                                # noqa: BLE001
        doc["read_error"] = str(e)
        doc["needs_reading"] = True
        return doc
    if sum(len(l) for l in lines) < 40:                    # scanned PDF: no usable text layer
        doc["needs_reading"] = True
        doc["source"] = "scanned-pdf"
        return doc
    doc["source"] = "pdf-text"
    return parse_text(lines, doc)
