# Quellberg receipt review — Claude Skill

Decides for every receipt in a folder: **APPROVE** (pay) or **INVESTIGATE** (a person looks), with the reason.
Claude reads what scripts can't (photos, scans); fixed rules in Python make the decision, so every verdict is reproducible and explained.

```
skill/            the skill — SKILL.md, scripts/ (extract, rules, review), assets/ (bestellungen.csv, extraction schema)
data/             the 16 test receipts + bestellungen.csv
results/          output of the skill on data/ — results.csv, report.md, results.json, extracted/ (Claude's reading of b08)
eval/             quality measurement — labels for the 16, generator for unseen receipts, evaluate.py
index.html        optional browser viewer (live: https://shyam-gupta-chiliveri.github.io/invoice-review-agent/)
```

## How to run

**As a Claude Skill** (Claude Code, or upload `skill/` as a skill in Claude): ask *"Review the receipts in `data/`"*. Claude runs the script, reads any photo/scan it reports, writes the fields to `results/extracted/`, runs again and summarises.

**Without Claude** (PDFs only; photos are flagged "needs reading"):
```
pip install -r skill/requirements.txt
python skill/scripts/review.py data --out results
```

## Pipeline

1. **Read** — PDFs: text layer via pdfplumber → fields + line items (German/English formats). Photos/scans: Claude reads the image into the same JSON schema; it copies what is printed and never corrects numbers.
2. **Check** — against `bestellungen.csv` (order exists, right vendor, quantity, unit price, items not ordered, value), arithmetic (lines, VAT, gross), §14 UStG fields, document type (Lieferschein/Angebot are not payable), IBAN checksum, and across the batch: one IBAN used by different vendors, duplicates.
3. **Decide** — any finding → INVESTIGATE (HIGH if money must not leave), none → APPROVE. Each finding has a code (table in `skill/SKILL.md`).

**Result on the 16:** 0 approve, 16 investigate (14 high). Main findings: one IBAN on 11 vendors' documents; b05 IBAN fails the checksum (one digit off); b10 duplicates b06; b07 50,000 caps over the order; b03 net €12.47 above its own lines; b04 VAT €4.21 short; b12 delivery note and b15 quote are not invoices. Full list: `results/report.md`.

## How quality was measured

`python eval/evaluate.py data eval/expected_16.json results/extracted` — hand labels for the 16 (decision, the problem an accountant must raise, 7 printed fields each): **16/16 decisions, 32/32 required findings, 112/112 fields.**

`python eval/make_unseen.py && python eval/evaluate.py eval/unseen eval/unseen/expected.json` — 13 generated receipts in two new layouts (German/English, other labels, date and number formats), each with one planted problem or none: **13/13 decisions, 2/2 clean ones approved, 11/11 planted problems found for the right reason.**

Limit: I wrote both rules and labels, so this proves the rules do what they claim and survive layout changes — not that they match Quellberg's policy. The real measure is the false-alarm rate on Quellberg's live inbox (see below).

## Judgment calls

- **Shared IBAN = do not pay.** 11 of 16 documents carry DE89 3704 0044 0532 0130 00. Without a vendor master this is the strongest fraud signal available; with one, the rule becomes "IBAN differs from the vendor master".
- **No PO = investigate**, even for small consumables (b16). Quellberg may want an approval limit instead — one constant in `rules.py`.

## Deliberately not built

- **LLM in the decision** — verdicts must be reproducible and auditable; the model only reads.
- **Own OCR / API vision call** — inside the skill, Claude already reads images; a second path is more to maintain.
- **Vendor master, payment history, ERP connection** — not in the test data; the rules are the place they plug in.
- **Persistence and approval workflow** — the skill decides, people act on `report.md`.

## Enterprise deployment

**Access:** the skill needs read access to the inbox folder and the order export only; payment release stays a human step in the ERP. Service account with least privilege, secrets in the platform's vault. **Traceability:** `results.json` per run (input file hash, extracted fields, every finding, rule version via git commit) stored append-only. **Monitoring:** share of APPROVE per day, findings per code, documents needing reading, runtime; alert on drift (e.g. sudden 0 % approve). **Model failure:** reading errors fall back to INVESTIGATE, never APPROVE — a missing model means more manual work, not unchecked payments. **Quality in operation:** every INVESTIGATE closed by an accountant is labelled (real problem / false alarm); weekly false-alarm rate and any later-discovered bad payment (missed problem) become new eval cases.
