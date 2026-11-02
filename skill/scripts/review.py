#!/usr/bin/env python3
"""Quellberg receipt review — run on a folder, decide APPROVE / INVESTIGATE per document.

    python skill/scripts/review.py <folder> [--orders bestellungen.csv] [--out results]

Reads every PDF/image in <folder>, checks it against the open orders and the rest of
the batch, and writes <out>/results.csv, results.json and report.md.
Photos and scans are listed under "needs reading": Claude reads them (see SKILL.md),
writes <out>/extracted/<file>.json, and this script is run again.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract import DOC_EXT, read_document  # noqa: E402
from rules import check, decide, eur, load_orders  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parent.parent


def find_orders(folder: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    for cand in [folder / "bestellungen.csv", *folder.glob("*.csv"), SKILL_DIR / "assets" / "bestellungen.csv"]:
        if cand.exists():
            return cand
    sys.exit("No bestellungen.csv found — pass --orders")


def render_scan(path: Path, out: Path) -> str | None:
    """For scanned PDFs: render page 1 to PNG so Claude can look at it."""
    if path.suffix.lower() != ".pdf":
        return str(path)
    try:
        import pdfplumber
        out.mkdir(parents=True, exist_ok=True)
        png = out / (path.stem + ".png")
        with pdfplumber.open(path) as pdf:
            pdf.pages[0].to_image(resolution=150).save(png)
        return str(png)
    except Exception:  # noqa: BLE001
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder with receipts (PDF, JPG, PNG)")
    ap.add_argument("--orders", help="purchase orders CSV (default: bestellungen.csv in folder, else bundled)")
    ap.add_argument("--out", default="results", help="output folder (default: results)")
    ap.add_argument("--extracted", help="folder with Claude's extraction JSONs (default: <out>/extracted)")
    a = ap.parse_args(argv)

    folder, out = Path(a.folder), Path(a.out)
    extracted = Path(a.extracted) if a.extracted else out / "extracted"
    out.mkdir(parents=True, exist_ok=True)
    orders_path = find_orders(folder, a.orders)
    orders = load_orders(orders_path.read_text(encoding="utf-8-sig"))

    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in DOC_EXT and not p.name.startswith("."))
    if not files:
        sys.exit(f"No receipts in {folder}")
    docs = [read_document(p, extracted) for p in files]

    results = []
    for d in docs:
        others = [o for o in docs if o is not d and not o["needs_reading"]]
        findings = check(d, others, orders)
        verdict = decide(d, findings)
        results.append({**verdict, "file": d["file"], "read_by": d["source"], "document": {k: v for k, v in d.items() if k != "file"},
                        "findings": findings})

    # ── outputs ──
    with open(out / "results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["file", "decision", "priority", "vendor", "invoice_number", "date", "po", "gross_eur", "issues", "summary"])
        for r in results:
            d = r["document"]
            issues = ",".join(f["code"] for f in r["findings"] if f["severity"] != "ok")
            w.writerow([r["file"], r["decision"], r["priority"], d["vendor"] or "", d["invoice_number"] or "", d["date"] or "",
                        d["po"] or "", "" if d["gross"] is None else f"{d['gross']:.2f}", issues, r["summary"]])
    meta = {"run_at": datetime.now().isoformat(timespec="seconds"), "folder": str(folder), "orders": str(orders_path),
            "documents": len(results), "approve": sum(r["decision"] == "APPROVE" for r in results),
            "investigate": sum(r["decision"] == "INVESTIGATE" for r in results)}
    (out / "results.json").write_text(json.dumps({"meta": meta, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    need = [r for r in results if r["document"]["needs_reading"]]
    md = [f"# Receipt review — {meta['run_at']}", "",
          f"{meta['documents']} documents · **{meta['approve']} approve** · **{meta['investigate']} investigate** · orders: `{orders_path.name}`", "",
          "| File | Decision | Vendor | Gross € | Why |", "|---|---|---|---:|---|"]
    order = {"HIGH": 0, "NORMAL": 1, "": 2}
    for r in sorted(results, key=lambda r: (order[r["priority"]], r["file"])):
        d = r["document"]
        label = "✅ APPROVE" if r["decision"] == "APPROVE" else ("🔴 INVESTIGATE (high)" if r["priority"] == "HIGH" else "🟠 INVESTIGATE")
        md.append(f"| {r['file']} | {label} | {d['vendor'] or '—'} | {eur(d['gross'])} | {r['summary']} |")
    md += ["", "## Findings per document", ""]
    for r in results:
        md.append(f"### {r['file']} — {r['decision']}{' (' + r['priority'] + ')' if r['priority'] else ''}")
        for f in r["findings"]:
            if f["severity"] != "ok":
                md.append(f"- **{f['title']}** `{f['code']}` — {f['detail']}")
        passed = [f["title"] for f in r["findings"] if f["severity"] == "ok"]
        if passed:
            md.append(f"- Passed: {', '.join(passed)}")
        md.append("")
    if need:
        md += ["## Needs reading (photo / scan)", ""] + [
            f"- `{r['file']}` → look at `{render_scan(folder / r['file'], out / 'pages') or r['file']}`, write `{extracted / (r['file'] + '.json')}`"
            for r in need]
    (out / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ── console ──
    for r in results:
        tag = "APPROVE    " if r["decision"] == "APPROVE" else f"INVESTIGATE{'!' if r['priority'] == 'HIGH' else ' '}"
        print(f"{tag} {r['file']:<46} {r['summary']}")
    print(f"\n{meta['approve']} approve · {meta['investigate']} investigate → {out}/results.csv, report.md, results.json")
    if need:
        print("\nNEEDS READING (no text layer) — read these images and write the JSON, then run again:")
        for r in need:
            print(f"  {folder / r['file']}  →  {extracted / (r['file'] + '.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
