# Receipt review — 2026-11-02T18:35:24

16 documents · **0 approve** · **16 investigate** · orders: `bestellungen.csv`

| File | Decision | Vendor | Gross € | Why |
|---|---|---|---:|---|
| b01_etikett_soehne_re-4471.pdf | 🔴 INVESTIGATE (high) | Etikett & Söhne GmbH | 3.843,70 | Do not pay: Bank account shared with other vendors (+2 more) |
| b03_sued_zucker_re-8841.pdf | 🔴 INVESTIGATE (high) | Süddeutsche Zucker-Handels GmbH | 8.958,02 | Do not pay: Arithmetic error; Bank account shared with other vendors (+1 more) |
| b04_kraeuterhof_allgaeu_re-2026-0331.pdf | 🔴 INVESTIGATE (high) | Kräuterhof Allgäu eG | 4.591,23 | Do not pay: VAT miscalculated; Bank account shared with other vendors (+1 more) |
| b05_brenner_logistik_re-fr-11029.pdf | 🔴 INVESTIGATE (high) | Brenner Logistik GmbH | 1.773,10 | Do not pay: IBAN is not a valid account (+1 more) |
| b06_kolb_re-2026-0447.pdf | 🔴 INVESTIGATE (high) | Maschinenservice Kolb | 2.992,85 | Do not pay: Bank account shared with other vendors (+3 more) |
| b07_kronkorken_mueller_re-5567.pdf | 🔴 INVESTIGATE (high) | Kronkorken Müller KG | 5.414,50 | Do not pay: Bank account shared with other vendors (+2 more) |
| b08_getraenke_ostbayern_re-2026-771.jpg | 🔴 INVESTIGATE (high) | Getränkefachgroßhandel Ostbayern | 1.278,06 | Do not pay: Bank account shared with other vendors (+1 more) |
| b09_federkiel_design_re-2026-14.pdf | 🔴 INVESTIGATE (high) | Federkiel Design Studio · Lena Vogt | 3.284,40 | Do not pay: Bank account shared with other vendors (+2 more) |
| b10_kolb_re-2026-0489.pdf | 🔴 INVESTIGATE (high) | Maschinenservice Kolb | 2.992,85 | Do not pay: Bank account shared with other vendors; Duplicate invoice (+2 more) |
| b11_hopfen_etikett_re-3390.pdf | 🔴 INVESTIGATE (high) | Hopfen & Etikett Druck GmbH | — | Do not pay: Bank account shared with other vendors (+2 more) |
| b12_kartonagen_beck_ls-2210.pdf | 🔴 INVESTIGATE (high) | Kartonagen Beck GmbH | — | Do not pay: Delivery note, not an invoice (+1 more) |
| b14_fruchtkontor_bodensee_re-2026-902.pdf | 🔴 INVESTIGATE (high) | Fruchtkontor Bodensee GmbH | 10.817,70 | Do not pay: Bank account shared with other vendors (+2 more) |
| b15_tankreinigung_sued_an-2026-118.pdf | 🔴 INVESTIGATE (high) | Tankreinigung Süddeutschland GmbH | 4.760,00 | Do not pay: Quote, not an invoice; Bank account shared with other vendors (+2 more) |
| b16_brauereibedarf_hartmann_re-7712.pdf | 🔴 INVESTIGATE (high) | Brauereibedarf Hartmann GmbH | 2.655,37 | Do not pay: Bank account shared with other vendors (+1 more) |
| b02_glashuette_weiden_re-2026-559.pdf | 🟠 INVESTIGATE | Glashütte Weiden GmbH | 25.235,62 | Clarify before paying: Items not on the order; Net exceeds order value |
| b13_nordic_caps_inv-2026-338.pdf | 🟠 INVESTIGATE | Nordic Bottle Caps ApS | 1.875,00 | Clarify before paying: No purchase order |

## Findings per document

### b01_etikett_soehne_re-4471.pdf — INVESTIGATE (HIGH)
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 3 "Druckvorlagen-Setup einmalig" €290,00 — €290,00 not covered by QB-10387
- **Net exceeds order value** `OVER_PO_VALUE` — Order €2.940,00, document €3.230,00 (+€290,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b02_glashuette_weiden_re-2026-559.pdf — INVESTIGATE (NORMAL)
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Kronkork-kompatibel Muendung, Aufpreis" €806,40 — €806,40 not covered by QB-10391
- **Net exceeds order value** `OVER_PO_VALUE` — Order €20.400,00, document €21.206,40 (+€806,40)
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b03_sued_zucker_re-8841.pdf — INVESTIGATE (HIGH)
- **Arithmetic error** `MATH_ERROR` — lines add up to €8.359,51, document states net €8.371,98 (Δ €12,47)
- **Order has no approved value** `PO_NO_VALUE` — QB-10412 ("Bio-Rohrzucker Sammelbestellung") is a framework order at €0,00 — net €8.371,98 over 22 items has no budget approval.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), VAT, Gross total, Purchase order, IBAN checksum

### b04_kraeuterhof_allgaeu_re-2026-0331.pdf — INVESTIGATE (HIGH)
- **VAT miscalculated** `VAT_ERROR` — €4.294,80 × 7 % = €300,64, document states €296,43 (Δ €-4,21)
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, Gross total, IBAN checksum

### b05_brenner_logistik_re-fr-11029.pdf — INVESTIGATE (HIGH)
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **IBAN is not a valid account** `IBAN_INVALID` — DE89370400940532013000 — mod-97 checksum fails: tampered or mistyped.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total

### b06_kolb_re-2026-0447.pdf — INVESTIGATE (HIGH)
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Ersatz Dichtungssatz Füllventil" €285,00; Pos 3 "Anfahrt/Techniker 4h" €380,00 — €665,00 not covered by QB-10402
- **Net exceeds order value** `OVER_PO_VALUE` — Order €1.850,00, document €2.515,00 (+€665,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- **A later duplicate exists** `HAS_DUPLICATE` — RE-2026-0489 (b10_kolb_re-2026-0489.pdf) repeats this invoice — pay once.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b07_kronkorken_mueller_re-5567.pdf — INVESTIGATE (HIGH)
- **More delivered/billed than ordered** `QTY_OVER` — Ordered 200.000,00, document 250.000,00 (+50.000,00, ≈ +€910,00)
- **Net exceeds order value** `OVER_PO_VALUE` — Order €3.640,00, document €4.550,00 (+€910,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Unit price vs order, IBAN checksum

### b08_getraenke_ostbayern_re-2026-771.jpg — INVESTIGATE (HIGH)
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, IBAN checksum

### b09_federkiel_design_re-2026-14.pdf — INVESTIGATE (HIGH)
- **Mandatory fields missing (§14 UStG)** `MISSING_FIELDS` — Missing: tax no. / VAT ID
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Line arithmetic, VAT, Gross total, IBAN checksum

### b10_kolb_re-2026-0489.pdf — INVESTIGATE (HIGH)
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Dichtungssatz Füllventil (6 Stk)" €285,00; Pos 3 "Technikereinsatz Anfahrt 4h" €380,00 — €665,00 not covered by QB-10402
- **Net exceeds order value** `OVER_PO_VALUE` — Order €1.850,00, document €2.515,00 (+€665,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- **Duplicate invoice** `DUPLICATE` — Repeats RE-2026-0447 (2026-06-15, b06_kolb_re-2026-0447.pdf): same vendor, same order and amount €2.992,85.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b11_hopfen_etikett_re-3390.pdf — INVESTIGATE (HIGH)
- **Mandatory fields missing (§14 UStG)** `MISSING_FIELDS` — Missing: gross total — only says "Nettobetrag zzgl. gesetzlicher Umsatzsteuer"
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Line arithmetic, VAT, IBAN checksum

### b12_kartonagen_beck_ls-2210.pdf — INVESTIGATE (HIGH)
- **Delivery note, not an invoice** `NOT_AN_INVOICE` — Lieferschein: no amounts to pay. File as goods receipt and request the invoice.
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Zwischenlage Wellpappe"
- Passed: Purchase order, Quantity vs order

### b13_nordic_caps_inv-2026-338.pdf — INVESTIGATE (NORMAL)
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, IBAN checksum

### b14_fruchtkontor_bodensee_re-2026-902.pdf — INVESTIGATE (HIGH)
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Ascorbinsäure-Zusatz (Antioxidans)" €190,00 — €190,00 not covered by QB-10416
- **Net exceeds order value** `OVER_PO_VALUE` — Order €9.920,00, document €10.110,00 (+€190,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b15_tankreinigung_sued_an-2026-118.pdf — INVESTIGATE (HIGH)
- **Quote, not an invoice** `NOT_AN_INVOICE` — Angebot: the document itself says it is not an invoice. Do not pay.
- **Items not on the order** `ITEMS_NOT_ORDERED` — Pos 2 "Desinfektion & Protokoll" €600,00 — €600,00 not covered by QB-10421
- **Net exceeds order value** `OVER_PO_VALUE` — Order €3.400,00, document €4.000,00 (+€600,00)
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Brauereibedarf Hartmann GmbH, Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Line arithmetic, Purchase order, Quantity vs order, Unit price vs order, IBAN checksum

### b16_brauereibedarf_hartmann_re-7712.pdf — INVESTIGATE (HIGH)
- **No purchase order** `NO_PO` — No order number on the document; vendor has no open order in bestellungen.csv. Needs approval by the budget owner.
- **Bank account shared with other vendors** `IBAN_SHARED` — Same IBAN on documents from 10 other vendor(s): Etikett & Söhne GmbH, Federkiel Design Studio · Lena Vogt, Fruchtkontor Bodensee GmbH, Getränkefachgroßhandel Ostbayern, Hopfen & Etikett Druck GmbH, Kronkorken Müller KG, Kräuterhof Allgäu eG, Maschinenservice Kolb, Süddeutsche Zucker-Handels GmbH, Tankreinigung Süddeutschland GmbH. Independent suppliers do not share an account — verify by phone before paying.
- Passed: Document type, Mandatory fields (§14 UStG), Line arithmetic, VAT, Gross total, IBAN checksum

