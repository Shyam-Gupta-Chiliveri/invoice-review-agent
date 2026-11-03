# Quellberg Belegprüfung

[English](README.md) · **Deutsch**

Ein Claude Skill, der für jeden Beleg in einem Ordner entscheidet: **APPROVE** (zahlen) oder **INVESTIGATE** (ein Mensch prüft), jeweils mit Begründung. PDFs werden aus ihrer Textebene gelesen, Fotos und Scans per OCR oder von Claude; feste Python-Regeln entscheiden, daher ist jedes Urteil reproduzierbar und nachvollziehbar.

**Live-Demo — keine Installation, kein Terminal:** https://invoice.138.2.179.154.sslip.io/ in einem beliebigen Browser öffnen und die Belege aus `data/` (PDFs und das Foto) auf die Warteschlange ziehen; jeder Beleg wird sofort gelesen, geprüft und entschieden. · **Code:** https://github.com/Shyam-Gupta-Chiliveri/invoice-review-agent

```
skill/     der Skill: SKILL.md, scripts/ (extract.py, rules.py, review.py), assets/ (bestellungen.csv, Extraktionsschema)
data/      die 16 Belege + bestellungen.csv
results/   Lauf des Skills auf data/: results.csv, report.md, results.json, extracted/ (Claudes Lesung des Fotos b08)
eval/      Qualitätsmessung: manuelle Labels, 13 unbekannte Belege mit eingebauten Fehlern, evaluate.py
index.html Browser-Version derselben Prüfungen (+ OCR, KI-Assistent); Dockerfile, docker-compose.yml, deploy/ fürs Hosting
```

## Ausführen

**Mit Claude (der Skill):** in Claude Code diesen Ordner öffnen oder `skill/` als Skill hochladen und fragen: *„Prüfe die Belege in data/“*. Claude startet `review.py`; Fotos oder Scans, die OCR nicht sicher lesen konnte, werden aufgelistet, Claude liest sie nach `results/extracted/<datei>.json`, startet erneut und fasst die Entscheidungen zusammen.

**Ohne Claude** (Python 3.10+; für Fotos und Scans zusätzlich Tesseract mit Deutsch: `apt install tesseract-ocr tesseract-ocr-deu` oder `brew install tesseract tesseract-lang`; ohne Tesseract werden sie als „needs reading“ gelistet):
```
pip install -r skill/requirements.txt
python skill/scripts/review.py data --out results          # jeder Ordner geht: review.py <ordner> [--orders datei.csv]
```
Ausgabe: `results.csv` (eine Zeile pro Beleg), `report.md` (zu prüfende Belege zuerst, mit Gründen), `results.json` (alle Felder und Befunde).

**Browser:** die Live-Demo (Docker + nginx auf einer Oracle Cloud Always Free VM) oder lokal `docker compose up -d --build` → http://localhost:8090. Dieselben Regeln in JavaScript, dazu Foto-OCR (Tesseract.js, mitgeliefert), markierte PDF-Felder, IBAN-Ring-Ansicht, E-Mail-Entwürfe an Lieferanten und ein KI-Assistent (DE/EN), der aus gefundenen Fakten über den Stapel antwortet.

## Wie entschieden wird

**Lesen:** Felder und Positionen aus der PDF-Textebene (pdfplumber); Fotos und Scans per OCR (Tesseract).

**OCR-Absicherung:** eine OCR-Lesung gilt nur, wenn ihre Zahlen aufgehen (Positionen = Netto, Netto × Satz = USt, Netto + USt = Brutto); sonst liest Claude den Beleg, sodass eine falsch gelesene Ziffer nie genehmigt und nie dem Lieferanten angelastet wird.

**Prüfen:** gegen `bestellungen.csv` (Bestellung vorhanden, richtiger Lieferant, Menge, Einzelpreis, nicht bestellte Positionen, Bestellwert), Rechnung (Positionen, USt, Brutto), Pflichtangaben nach §14 UStG, Belegart (Lieferschein und Angebot sind nicht zahlbar), IBAN-Prüfsumme und über den Stapel (eine IBAN bei verschiedenen Lieferanten, Doubletten).

**Entscheiden:** ein blockierender Befund → INVESTIGATE, Priorität HIGH; ein Prüfbefund → INVESTIGATE; kein Befund → APPROVE. Codes und Schweregrade in `skill/SKILL.md`, alle Regeln in `skill/scripts/rules.py`.

**Ergebnis für die 16:** 0 approve, 16 investigate (14 high). Details in `results/report.md`.

**Wichtigste Befunde:** eine IBAN auf Belegen von 11 Lieferanten; die IBAN von b05 besteht die Prüfsumme nicht (eine Ziffer abweichend); b10 wiederholt b06; b07 berechnet 50.000 Kronkorken mehr als bestellt; der Nettobetrag von b03 liegt 12,47 € über seinen eigenen Positionen; bei b04 fehlen 4,21 € Umsatzsteuer; b12 ist ein Lieferschein, b15 ein Angebot; b02 und b13 werden wegen nicht bestellter Positionen bzw. fehlender Bestellung gehalten.

## Wie die Qualität gemessen wurde

- **Die 16, manuell gelabelt** (Entscheidung, das Problem, das die Buchhaltung ansprechen muss, je 7 gedruckte Felder): `python eval/evaluate.py data eval/expected_16.json results/extracted` → **16/16 Entscheidungen, 32/32 geforderte Befunde, 112/112 Felder**, identisch, ob das Foto b08 per OCR oder von Claude gelesen wird (`results/extracted`).
- **Unbekannte Belege:** 13 erzeugt in zwei neuen Layouts (Deutsch/Englisch, andere Bezeichnungen, Datums- und Zahlenformate), jeder mit genau einem eingebauten Problem oder keinem: `python eval/evaluate.py eval/unseen eval/unseen/expected.json` → **13/13 Entscheidungen, beide sauberen genehmigt, 11/11 Probleme aus dem richtigen Grund gefunden**; ein niedrig aufgelöster Scan, den OCR falsch liest, geht an Claude, statt geraten zu werden (neu erzeugen: `pip install reportlab && python eval/make_unseen.py`).
- **Grenze:** Regeln und Labels stammen beide von mir. Das belegt, dass die Regeln tun, was sie versprechen, und Layoutwechsel überstehen, nicht aber, dass sie Quellbergs Richtlinien treffen. Das misst man im Betrieb: die Fehlalarmquote bei geprüften Belegen.

## Bewusst nicht gebaut

- **Kein Sprachmodell in der Entscheidung.** Zahlungen brauchen reproduzierbare, prüfbare Urteile; das Modell liest nur.
- **Kein Modell zum Lesen von Text-PDFs.** Die Textebene ist exakt, schnell und kostenlos; OCR und Claude kommen nur zum Einsatz, wo es keinen Text gibt.
- **Keine Lieferantenstammdaten, Zahlungshistorie oder ERP-Anbindung.** Nicht in den Testdaten. Mit Stammdaten wird aus „geteilte IBAN“ die Regel „IBAN weicht vom Stammsatz ab“.
- **Kein Freigabe-Workflow, keine Datenbank.** Der Skill entscheidet; Menschen handeln anhand von `report.md`.
- **Zwei bewusste Entscheidungen, je eine Zeile in `rules.py`:** eine geteilte IBAN heißt „nicht zahlen“; ein Beleg ohne Bestellung wird immer geprüft (eine Betragsgrenze lässt sich ergänzen).

## Einsatz beim Unternehmenskunden

**Zugriff:** Service-Account nur mit Leserechten auf den Eingangsordner und den Bestellexport; die Zahlungsfreigabe bleibt ein menschlicher Schritt im ERP; Zugangsdaten im Tresor des Kunden.

**Nachvollziehbarkeit:** jeder Lauf schreibt `results.json` (Datei-Hash, gelesene Felder, jeder Befund mit seiner Regel, Git-Commit) in einen nur anfügbaren Speicher.

**Monitoring:** Genehmigungsquote pro Tag, Befunde pro Code, Belege mit Lesebedarf, Laufzeit; Alarm bei Abweichungen (z. B. Genehmigungsquote fällt auf 0 %).

**Ausfall des Modells:** schlägt das Lesen fehl oder läuft in ein Timeout, wird der Beleg INVESTIGATE, nie APPROVE: ein Ausfall bedeutet mehr Handarbeit, keine ungeprüften Zahlungen.

**Qualität im Betrieb:** die Buchhaltung markiert jeden geprüften Beleg als „echtes Problem“ oder „Fehlalarm“; die wöchentliche Fehlalarmquote und jedes erst nach der Zahlung entdeckte Problem werden zu neuen Testfällen, bevor eine Regel geändert wird.
