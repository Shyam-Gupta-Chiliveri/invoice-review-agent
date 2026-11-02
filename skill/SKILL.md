---
name: quellberg-beleg-pruefung
description: Reviews a folder of supplier receipts (PDFs and photos) for Quellberg against bestellungen.csv and decides APPROVE or INVESTIGATE per document, with reasons. Use when asked to check, review or approve invoices/Belege/Rechnungen for payment.
---

# Quellberg receipt review

Decide for every receipt in a folder: **APPROVE** (pay it) or **INVESTIGATE** (a person must look), and say why.
Reading is done by you and the scripts; the decision is made by fixed rules in `scripts/rules.py`, so it is reproducible and every finding is traceable.

## Run

1. Install once: `pip install -r requirements.txt` (only `pdfplumber`).
2. Run the review on the folder (it finds `bestellungen.csv` in that folder, else uses `assets/bestellungen.csv`):
   ```
   python scripts/review.py <folder> --out <folder>/results
   ```
3. If the output lists **NEEDS READING**, do the reading step below for each listed file, then run step 2 again.
4. Answer the user from `<out>/report.md`: first the documents to investigate (high priority first) with their one-line reason, then the approved ones. Link the output files.

## Reading step (photos and scans)

The script cannot read images. For each file it lists:

1. Open the image (or the rendered page it names under `<out>/pages/`) and read it yourself.
2. Write `<out>/extracted/<filename>.json` following `assets/extraction_schema.json`, for example:
   ```json
   {"doc_type": "Rechnung", "vendor": "Muster GmbH", "invoice_number": "RE-1", "date": "2026-06-21",
    "po": null, "tax_id": "DE 123 456 789", "iban": "DE89370400440532013000",
    "net": 1074.00, "vat_rate": 19, "vat": 204.06, "gross": 1278.06, "reverse_charge": false,
    "lines": [{"pos": 1, "description": "…", "qty": 120, "unit_price": 4.5, "total": 540.0}]}
   ```
3. Rules for reading:
   - Copy what is **printed**. Never correct a number, never compute a missing total, never fill a field you cannot see — use `null`. The rules decide whether the printed numbers are right.
   - `doc_type` is the document's own title word: Rechnung, Invoice, Lieferschein, Angebot, Gutschrift.
   - Dates as `YYYY-MM-DD`; amounts as plain numbers (`1074.0`, not `1.074,00`); IBAN without spaces.
   - `po` only if a Quellberg order number (`QB-…`) is printed.
   - If the image is unreadable, write `{"doc_type": null}` and say so in your answer — it stays INVESTIGATE.

Do not change a decision by hand. If you disagree with a rule, say so in your answer and point to the rule in `scripts/rules.py`.

## What the checks are

| Code | Severity | Meaning |
|---|---|---|
| `NOT_AN_INVOICE` | block | Delivery note or quote — nothing to pay |
| `MATH_ERROR`, `VAT_ERROR`, `GROSS_ERROR` | block | Printed numbers do not add up |
| `IBAN_INVALID` | block | IBAN fails the ISO 13616 checksum |
| `IBAN_SHARED` | block | Same bank account on documents from different vendors in the batch |
| `DUPLICATE` | block | Same vendor + same number, or same order and amount, already in the batch |
| `PO_UNKNOWN`, `PO_WRONG_VENDOR` | block | Order number not in `bestellungen.csv` or belongs to someone else |
| `NO_PO`, `PO_NO_VALUE` | review | No approved order / framework order without value |
| `QTY_OVER`, `PRICE_DEVIATION`, `ITEMS_NOT_ORDERED`, `OVER_PO_VALUE` | review | Differs from the order |
| `MISSING_FIELDS` | review | §14 UStG content missing (tax no., gross, …) |
| `NOT_READ`, `UNKNOWN_TYPE`, `CREDIT_NOTE`, `HAS_DUPLICATE` | review | Needs a person |

Any block or review finding → INVESTIGATE (priority HIGH if any block). Otherwise → APPROVE.
Tolerance for rounding: €0.02; unit prices printed with 2 decimals are accepted if they round to the billed line total.
