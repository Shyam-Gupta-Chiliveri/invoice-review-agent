#!/usr/bin/env python3
"""Measure the skill: decisions, required findings, false alarms, field reading.

    python eval/evaluate.py data eval/expected_16.json
    python eval/make_unseen.py && python eval/evaluate.py eval/unseen eval/unseen/expected.json

Runs skill/scripts/review.py on the folder, then compares with the labels.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(folder, labels_path, extracted=None):
    labels = {k: v for k, v in json.loads(Path(labels_path).read_text(encoding="utf-8")).items() if not k.startswith("_")}
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(ROOT / "skill/scripts/review.py"), folder, "--out", tmp]
        if extracted:
            cmd += ["--extracted", extracted]
        subprocess.run(cmd, check=True, capture_output=True)
        res = {r["file"]: r for r in json.loads((Path(tmp) / "results.json").read_text(encoding="utf-8"))["results"]}

    tp = fp = fn = tn = 0
    found = missed = 0
    field_ok = field_all = 0
    rows = []
    for name, lab in labels.items():
        r = res.get(name)
        if not r:
            rows.append(f"  MISSING  {name}"); fn += 1; continue
        got, want = r["decision"], lab["decision"]
        if want == "INVESTIGATE":
            tp, fn = tp + (got == want), fn + (got != want)
        else:
            tn, fp = tn + (got == want), fp + (got != want)
        codes = {f["code"] for f in r["findings"] if f["severity"] != "ok"}
        miss = [c for c in lab["must_find"] if c not in codes]
        found += len(lab["must_find"]) - len(miss); missed += len(miss)
        extra = sorted(codes - set(lab["must_find"]))
        bad_fields = []
        for k, v in (lab.get("fields") or {}).items():
            gv = r["document"].get(k)
            ok = (gv is None and v is None) or (isinstance(v, float) and gv is not None and abs(gv - v) < 0.005) or gv == v
            field_all += 1; field_ok += ok
            if not ok:
                bad_fields.append(f"{k}={gv!r}≠{v!r}")
        mark = "ok " if got == want and not miss else "ERR"
        rows.append(f"  {mark} {name:<44} {got:<11} (want {want})"
                    + (f"  missed {miss}" if miss else "") + (f"  also {extra}" if extra else "")
                    + (f"  fields {bad_fields}" if bad_fields else ""))

    n = len(labels)
    print(f"\n{folder}: {n} receipts")
    print("\n".join(rows))
    print(f"\nDecision accuracy      {tp + tn}/{n}")
    print(f"Problem docs caught    {tp}/{tp + fn}   (recall on INVESTIGATE — a miss means money leaves)")
    print(f"Clean docs approved    {tn}/{tn + fp}" if tn + fp else "Clean docs approved    n/a (no clean docs labelled)")
    print(f"Required findings      {found}/{found + missed}   (right decision for the right reason)")
    if field_all:
        print(f"Fields read correctly  {field_ok}/{field_all}")
    return 0 if fn == 0 and missed == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:4]))
