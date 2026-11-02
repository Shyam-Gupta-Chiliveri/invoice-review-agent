# Quellberg receipt review

For every receipt in a folder the skill decides **APPROVE** (pay) or **INVESTIGATE** (a person looks), with the reason. Claude only reads photos and scans. Fixed Python rules make the decision, so every verdict is reproducible.

**Live demo:** [https://invoice.138.2.179.154.sslip.io/](https://invoice.138.2.179.154.sslip.io/) — drop the files from `data/`. Same checks as the skill. Docker on an Oracle Cloud Always Free VM, with HTTPS. Cost: €0.

```
skill/     SKILL.md, scripts (extract, rules, review), bestellungen.csv, extraction schema
data/      16 test receipts + bestellungen.csv
results/   this run: results.csv, results.json, report.md, extracted/
eval/      labels for the 16, unseen-receipt generator, evaluate.py
```

## How to run

**Claude Skill** (Claude Code, or upload `skill/`): ask *"Review the receipts in `data/`"*. Claude runs the script, reads any photo it flags, writes `results/extracted/`, runs again, and summarises.

**Without Claude** (PDFs; photos are flagged "needs reading"):

```
pip install -r skill/requirements.txt
python skill/scripts/review.py data --out results
```

**Browser:** open the live link. Locally, `docker compose up -d --build` then http://localhost:8090. Photo OCR needs http, not a double-clicked file. The chat button (bottom right) answers questions about the app and the uploaded batch: it retrieves from the app docs and one chunk per document, shared IBAN and order (BM25), then answers from those facts with sources. Inside Claude, Claude writes the answer from the retrieved facts; elsewhere it is composed without a model.

## Checks

PDFs are read from the text layer (pdfplumber) into fields and line items. Checks: purchase order (`bestellungen.csv` — order exists, vendor, quantity, unit price, extras, value), arithmetic (lines, VAT, gross), §14 UStG fields, document type (a delivery note or quote is not payable), IBAN checksum, and the batch (one IBAN across vendors, duplicates). Any finding → INVESTIGATE (HIGH if money must not leave); none → APPROVE. Finding codes are in `skill/SKILL.md`.

On the 16: **0 approve, 16 investigate (14 high).** One IBAN on 11 vendors; b05 fails the IBAN checksum; b10 duplicates b06; b07 is 50,000 caps over the order; b03 net is €12.47 above its lines; b04 VAT is €4.21 short; b12 is a delivery note and b15 is a quote (`results/report.md`). A shared IBAN is do-not-pay until a vendor master exists. No purchase order means investigate — one constant in `rules.py` if a small-amount limit is wanted.

## Quality

`python eval/evaluate.py data eval/expected_16.json results/extracted` — hand labels for the decision, the problem an accountant must raise, and 7 printed fields: **16/16 decisions, 32/32 required findings, 112/112 fields.**

`python eval/make_unseen.py && python eval/evaluate.py eval/unseen eval/unseen/expected.json` — 13 receipts in two new layouts, each with one planted problem or none: **13/13 decisions, 2/2 clean ones approved, 11/11 planted problems found for the right reason.**

I wrote both the rules and the labels, so this shows the rules survive a layout change. The live measure is the false-alarm rate on Quellberg's inbox.

## Deliberately not built

- No LLM in the decision. Verdicts must be auditable; the model only reads.
- No OCR inside the skill. Claude reads images. The browser uses Tesseract.js; arithmetic catches a misread digit.
- No vendor master, payment history, or ERP connection. Those plug into the same rules.
- No approval workflow. The skill decides; people act on `report.md`.

## Enterprise

Read access only to the inbox folder and the order export. Payment release stays a human step in the ERP. Service account, least privilege, secrets in the vault. Each run appends `results.json` (file hash, fields, findings, git commit). Monitor the APPROVE share, findings per code, documents needing reading, and runtime; alert on drift, such as a sudden 0% approve. A reading failure is INVESTIGATE, never APPROVE. Accountants label each closed case real or false alarm; that rate, and any later missed payment, become the next eval cases.
