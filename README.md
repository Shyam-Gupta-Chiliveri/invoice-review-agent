# Quellberg receipt review

A Claude Skill that decides for every receipt in a folder: **APPROVE** (pay) or **INVESTIGATE** (a person looks), with the reason. PDFs are read from their text layer, photos and scans by OCR or Claude; fixed Python rules decide, so every verdict is reproducible and traceable.

**Live demo — no installation, no terminal:** open https://invoice.138.2.179.154.sslip.io/ in any browser and drop the receipts from `data/` (PDFs and the photo) onto the queue; it reads, checks and decides each one on the spot. · **Code:** https://github.com/Shyam-Gupta-Chiliveri/invoice-review-agent

```
skill/     the skill: SKILL.md, scripts/ (extract.py, rules.py, review.py), assets/ (bestellungen.csv, extraction schema)
data/      the 16 receipts + bestellungen.csv
results/   the skill's run on data/: results.csv, report.md, results.json, extracted/ (Claude's reading of the photo b08)
eval/      quality measurement: hand labels, 13 unseen receipts with planted problems, evaluate.py
index.html browser version of the same checks (+ OCR, AI assistant); Dockerfile, docker-compose.yml, deploy/ to host it
```

## How to run

**With Claude (the skill):** in Claude Code open this folder, or upload `skill/` as a skill, and ask *"Review the receipts in data/"*. Claude runs `review.py`; any photo or scan that OCR could not read reliably is listed, Claude reads it into `results/extracted/<file>.json`, runs again and summarises the decisions.

**Without Claude** (Python 3.10+; for photos and scans also Tesseract with German: `apt install tesseract-ocr tesseract-ocr-deu` or `brew install tesseract tesseract-lang`; without it they are listed as "needs reading"):
```
pip install -r skill/requirements.txt
python skill/scripts/review.py data --out results          # any folder works: review.py <folder> [--orders file.csv]
```
Output: `results.csv` (one line per receipt), `report.md` (investigate first, with reasons), `results.json` (all fields and findings).

**Browser:** the live demo (Docker + nginx on an Oracle Cloud Always Free VM), or locally `docker compose up -d --build` → http://localhost:8090. Same rules in JavaScript, plus photo OCR (Tesseract.js, bundled), highlighted PDF fields, IBAN-ring view, vendor email drafts and an EN/DE AI assistant that answers from retrieved facts about the batch.

## How it decides

**Read** fields and line items from the PDF text layer (pdfplumber); photos and scans by OCR (Tesseract). An OCR reading is accepted only if its numbers add up (lines = net, net × rate = VAT, net + VAT = gross); otherwise Claude reads it, so a misread digit is never approved or blamed on the vendor. **Check** against `bestellungen.csv` (order exists, right vendor, quantity, unit price, items not ordered, order value), arithmetic (lines, VAT, gross), §14 UStG mandatory fields, document type (delivery note and quote are not payable), IBAN checksum, and across the batch (one IBAN used by different vendors, duplicates). **Decide:** a blocking finding → INVESTIGATE, priority HIGH; a review finding → INVESTIGATE; none → APPROVE. Codes and severities: `skill/SKILL.md`; all rules: `skill/scripts/rules.py`.

**Result on the 16: 0 approve, 16 investigate (14 high).** One IBAN on 11 vendors' receipts; b05's IBAN fails the checksum (one digit off); b10 repeats b06; b07 bills 50,000 caps more than ordered; b03's net is €12.47 above its own lines; b04's VAT is €4.21 short; b12 is a delivery note, b15 a quote; b02 and b13 are held for items not ordered / no order. Details: `results/report.md`.

## How I measured quality

- **The 16, hand-labelled** (decision, the problem an accountant must raise, 7 printed fields each): `python eval/evaluate.py data eval/expected_16.json results/extracted` → **16/16 decisions, 32/32 required findings, 112/112 fields**, identical whether the photo b08 is read by OCR or by Claude (`results/extracted`).
- **Unseen receipts:** 13 generated in two new layouts (German/English, other labels, date and number formats), each with one planted problem or none: `python eval/evaluate.py eval/unseen eval/unseen/expected.json` → **13/13 decisions, both clean ones approved, 11/11 problems found for the right reason**; a low-resolution scan that OCR misreads goes to Claude instead of being guessed (regenerate: `pip install reportlab && python eval/make_unseen.py`).
- **Limit:** I wrote both the rules and the labels, so this proves the rules do what they claim and survive layout changes, not that they match Quellberg's policy. That is measured live: the false-alarm rate on investigated receipts.

## Deliberately not built

- **No LLM in the decision.** Payments need reproducible, auditable verdicts; the model only reads.
- **No model reading of text PDFs.** The text layer is exact, fast and free; OCR and Claude are used only where there is no text.
- **No vendor master, payment history or ERP link.** Not in the test data. With a vendor master, "shared IBAN" becomes "IBAN differs from the master".
- **No approval workflow or database.** The skill decides; people act on `report.md`.
- **Two judgment calls, each one line in `rules.py`:** a shared IBAN is do-not-pay; a receipt without an order is always investigated (an amount limit can be added).

## Enterprise deployment

**Access:** read-only service account on the inbox folder and the order export; payment release stays a human step in the ERP; secrets in the client's vault. **Traceability:** every run appends `results.json` (file hash, extracted fields, each finding with its rule, git commit) to append-only storage. **Monitoring:** approve share per day, findings per code, documents needing reading, runtime; alert on drift (e.g. approve share drops to 0 %). **Model failure:** if reading fails or times out, the receipt is INVESTIGATE, never APPROVE: an outage means more manual work, not unchecked payments. **Quality in operation:** accountants mark each investigated receipt "real problem" or "false alarm"; the weekly false-alarm rate and any problem found after payment become new eval cases before the next rule change.
