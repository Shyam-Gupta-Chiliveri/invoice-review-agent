# Sample data

Test set for the invoice review app. Drop these files onto the queue in `index.html`.

| File | Content |
|------|---------|
| `bestellungen.csv` | Purchase-order master (9 POs, `;`-separated). Embedded in the app by default; dropping it again replaces the PO list. |
| `b01` … `b16` `*.pdf` | 15 supplier documents (invoices, one delivery note, one quote). b08 is not part of the set. |
| `getraenkefachgrosshandel_ostbayern_re-2026-771.jpg` | Photographed invoice without a text layer — shows the manual-review path (no OCR). |

Expected result when all 15 PDFs are uploaded together: 13 Critical, 2 Hold (b02, b13), 0 Approve.
