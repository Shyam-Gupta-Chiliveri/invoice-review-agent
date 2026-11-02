# DECAID Academy — Quellberg Invoice Review

A **Forward Deployed AI Engineer** demo: an intelligent accounts-payable review tool that simulates a multi-agent pipeline for invoice processing.

## Live Demo

Open `index.html` in any modern browser — no server required.  
Or view the hosted version: [Quellberg Invoice Review](https://claude.ai/artifact/Tv6fpSmZQkfqYbUAK5Vyvn)

## What it does

- **16 pre-loaded demo invoices** with realistic German Rechnung data (vendors, IBANs, VAT calculations, PO matching)
- **Multi-agent pipeline** with animated step-by-step processing: Reader → Validation → IBAN Ring → Verdict → Audit Trail → Email
- **Real-time document viewer** — upload a PDF or image and see it rendered alongside extracted fields
- **IBAN Ring detection** — flags invoices sharing bank accounts across vendors (fraud signal)
- **Fuzzy vendor matching** — uploaded files are matched to existing invoices by vendor keyword
- **Audit trail & email draft** generated per invoice
- **Dark / light theme**, bilingual UI (EN / DE), search + filter queue

## Agent pipeline tabs

| Tab | Agent | Purpose |
|-----|-------|---------|
| Extracted Fields | READER | OCR field extraction with confidence scores |
| Validation | VALIDATION | VAT calc, PO qty match, anomaly flags |
| IBAN Ring | IBAN RING | Cross-vendor IBAN deduplication |
| Verdict | VERDICT | Risk score + approve / hold / critical decision |
| Audit Trail | AUDIT TRAIL | Timestamped event log |
| Email | EMAIL | Drafted supplier communication |

## How to run

```bash
# Just open the file — no build step, no dependencies
open index.html
```

Or serve locally:
```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

## Upload your own invoices

Drop a PDF, TIFF, PNG, or JPG into the **Document Queue** drop zone.  
The pipeline runs with animated steps and auto-matches to demo vendor data where possible.

## Deliberate omissions

- **No real LLM calls** — all extraction is pre-baked demo data; the pipeline animation simulates agent latency
- **No backend** — fully client-side, single HTML file
- **No persistence** — state resets on refresh (by design for a demo)
- **PDF rendering** — uses PDF.js (cdnjs) to render page 1; multi-page navigation not implemented

## Quality measurement

The demo measures quality through UI signals that mirror what a real AP system would track:

- **Field confidence badges** (green / amber / red) on each extracted field
- **Check pass/fail counts** in the Validation tab
- **IBAN Ring exposure** shown in the top bar (€ value at risk)
- **Verdict distribution** (approve / hold / critical) across the invoice batch

---

Built with: vanilla JS · PDF.js · Inter & IBM Plex Mono (Google Fonts)  
No frameworks, no build toolchain.
