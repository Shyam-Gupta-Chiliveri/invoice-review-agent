# DECAID Academy — Quellberg Invoice Review

A **Forward Deployed AI Engineer** demo: an intelligent accounts-payable review tool that simulates a multi-agent pipeline for invoice processing.

## Live Demo

Open `index.html` in any modern browser — no server required.  
Or view the hosted version: [Quellberg Invoice Review](https://htmlpreview.github.io/?https://github.com/Shyam-Gupta-Chiliveri/invoice-review-agent/blob/main/index.html)

## What it does

Nothing is pre-loaded. Every result comes from a document you upload:

1. **Reader** — PDF.js renders each page and extracts the text layer; fields (document type, vendor, invoice no., date, PO, tax no., net / VAT / gross, IBAN) and every line item are parsed from the real text, German and English number formats alike.
2. **Validation** — each document is checked against the purchase-order master (`bestellungen.csv`, embedded; drop your own CSV to replace it): PO exists and belongs to the vendor, quantity and unit price vs. order, items not on the order, total vs. authorised value, line arithmetic, VAT, gross, §14 UStG mandatory fields, document type (Lieferschein / Angebot are not payable).
3. **IBAN Ring** — ISO 13616 mod-97 checksum, plus cross-document detection of one bank account used by several vendors.
4. **Duplicates** — same vendor + same PO/amount or invoice number across the batch.
5. **Verdict** — deterministic: any error → Critical, any warning → Hold, otherwise Approve. No LLM in the verdict.
6. **Audit trail & email** — real per-step log and a vendor query listing the actual findings.

Cross-document checks re-run whenever the batch changes, so an invoice can move from Hold to Critical when a later upload reveals a shared IBAN or a duplicate.

## Agent pipeline tabs

| Tab | Agent | Purpose |
|-----|-------|---------|
| Extracted Fields | READER | Fields, line items, PO-vs-document table; highlights on the rendered PDF |
| Validation | VALIDATION | Every check with its evidence |
| IBAN Ring | IBAN RING | Checksum + vendors sharing the account |
| Verdict | VERDICT | Approve / hold / critical with reasons |
| Audit Trail | AUDIT TRAIL | Timestamped steps for this document |
| Email | EMAIL | Drafted supplier query |

## How to run

Open `index.html` in a modern browser (no build step), or `python3 -m http.server 8080`.
Drop PDF invoices (and optionally a `;`-separated PO CSV with columns `Bestellnummer;Lieferant;Artikel;Menge;Einzelpreis_netto_EUR`) onto the queue.

## Limits

- **Scans / photos** have no text layer; they are flagged for manual review (no OCR in this build).
- **No persistence** — state resets on refresh.
- Layout parsing is rule-based for German/English invoices with a `Pos … Menge … Gesamt` table.

## Quality measurement

The demo measures quality through UI signals that mirror what a real AP system would track:

- **Field confidence badges** (green / amber / red) on each extracted field
- **Check pass/fail counts** in the Validation tab
- **IBAN risk exposure** in the bottom bar (€ at risk from shared or invalid IBANs)
- **Verdict distribution** (approve / hold / critical) across the invoice batch

---

Built with: vanilla JS · PDF.js 3.11 · Inter & IBM Plex Mono (Google Fonts)  
No frameworks, no build toolchain.
