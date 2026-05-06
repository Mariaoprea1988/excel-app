# bnm-streamlit

Ești asistent specializat pentru proiectul **AI Bank BNM Dashboard** — aplicație Streamlit cu date de la Banca Națională a Moldovei.

## Informații proiect

| Element | Valoare |
|---|---|
| Aplicație live | https://ai-bank.streamlit.app/ |
| GitHub repo | https://github.com/Mariaoprea1988/excel-app |
| Fișier principal | `app.py` |
| Folder date locale | `C:\Users\Asus\Documents\Ai learning\Excel bnm` |
| Folder date în repo | `data/` |

## Structura repo

```
excel-app/
├── app.py                          # aplicația Streamlit principală
├── requirements.txt
├── Capital.xlsx
└── data/
    ├── Capital Martie 2026.xls     # Capital bancar (luna curentă)
    ├── Capital decembrie.xls
    ├── Capital Februarie 2026.xls
    ├── Credit_report_12_2025.csv.txt
    └── Reports interest rate.xls
```

## Fișiere locale disponibile

```
C:\Users\Asus\Documents\Ai learning\Excel bnm\
├── streamlit_app.py
├── Capital Martie 2026.xls
├── Capital decembrie.xls
├── Credit_report_12_2025.csv.txt
├── credite ramuri.xls
├── Depozite decembrie 2025.xls
├── Depozite pentru Martie.xls
├── Reports interest rate.xls
└── Reports interest rate.pdf
```

## Variabile cheie în app.py

```python
CAPITAL_LOCAL    = "data/Capital Martie 2026.xls"   # linia ~334
CREDIT_REPORT_LOCAL  = "data/Credit_report_12_2025.csv.txt"
INTEREST_RATE_LOCAL  = "data/Reports interest rate.xls"
```

## Structura Excel Capital (sheet: BNM)

- **Row 1** — titlu + perioadă (ex: "Martie, 2026")
- **Row 3** — numele băncilor (col 5–15): Total Sector Bancar + 10 bănci
- **Row 4** — 1.1 Capital Social (mil. lei)
- **Row 5** — 1.2 Fonduri Proprii Nivel 1
- **Row 6** — 1.3 Fonduri Proprii Nivel 2
- **Row 7** — 1.4 Fonduri Proprii Totale
- **Row 8** — 1.5 Capital Eligibil
- **Row 9** — 1.6 Expunere la Risc
- **Row 10** — 1.7 Rata Fonduri Proprii (%)
- **Row 11** — 1.8 Fonduri Proprii / Total Active (%)

## Workflow actualizare lună nouă

1. Descarcă noul fișier Excel de pe BNM.md
2. Copiază în `C:\Users\Asus\Documents\excel-app\data\`
3. Actualizează `CAPITAL_LOCAL` în `app.py` cu noul nume fișier
4. Înlocuiește toate referințele la luna veche cu luna nouă
5. Push pe GitHub — Streamlit Cloud se redeploya automat

```bash
cd "C:\Users\Asus\Documents\excel-app"
git add data/<fisier-nou>.xls app.py
git commit -m "Actualizare date: <Luna Veche> → <Luna Noua>"
git push origin main
```

## Notă afișare bănci

`len(banks)` returnează 11 (include Total Sector Bancar).
În caption se folosește `len(banks) - 1` pentru a afișa **10 bănci**.
Calculele și graficele folosesc toate cele 11 rânduri.

---

$ARGUMENTS
