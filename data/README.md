# Sample data

The 16 receipts from the test assignment plus the purchase-order master. Drop them onto the queue in `index.html`.

| File | Content |
|------|---------|
| `bestellungen.csv` | Purchase-order master (9 POs, `;`-separated). Embedded in the app by default; dropping it again replaces the PO list. |
| `b01` … `b16` (except b08) `*.pdf` | 15 supplier documents as PDFs: invoices, one delivery note (b12), one quote (b15). |
| `b08_getraenke_ostbayern_re-2026-771.jpg` | The 16th receipt: a photographed invoice with no text layer (renamed here; original filename not available). |

Expected result for the 15 PDFs uploaded together: 13 Critical, 2 Hold (b02, b13), 0 Approve.
b08 is flagged for manual review, because this build has no OCR. Read by hand, it carries the shared IBAN DE89 3704 0044 0532 0130 00 and no PO, so it belongs with the Critical group.
