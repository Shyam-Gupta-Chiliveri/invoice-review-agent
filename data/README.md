# Sample data

The 16 receipts from the test assignment plus the purchase-order master. Drop them onto the queue in `index.html`.

| File | Content |
|------|---------|
| `bestellungen.csv` | Purchase-order master (9 POs, `;`-separated). Embedded in the app by default; dropping it again replaces the PO list. |
| `b01` … `b16` (except b08) `*.pdf` | 15 supplier documents as PDFs: invoices, one delivery note (b12), one quote (b15). |
| `b08_getraenke_ostbayern_re-2026-771.jpg` | The 16th receipt: a photographed invoice with no text layer (renamed here; original filename not available). |

Result of the skill on all 16: 0 approve, 16 investigate — see `../results/report.md`.
