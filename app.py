import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from fpdf import FPDF
from bs4 import BeautifulSoup

# ─────────────────────────────────────────────
# CONFIGURARE PAGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Bank",
    page_icon="🏦",
    layout="wide"
)

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* ── Header banner ── */
.bank-header {
    background: linear-gradient(135deg, #0A2342 0%, #1a3a6c 60%, #2563EB 100%);
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(37,99,235,0.25);
}
.bank-header-left h1 {
    color: #ffffff;
    margin: 0 0 4px 0;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.bank-header-left p {
    color: rgba(255,255,255,0.65);
    margin: 0;
    font-size: 0.9rem;
}
.bank-header-right {
    text-align: right;
    color: rgba(255,255,255,0.55);
    font-size: 0.82rem;
    line-height: 1.6;
}

/* ── Tabs principale ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: transparent;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.97rem;
    font-weight: 600;
    padding: 10px 22px;
    border-radius: 8px 8px 0 0;
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    margin-bottom: -2px;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1e40af !important;
    border-color: #e2e8f0 !important;
    border-bottom: 2px solid white !important;
}

/* ── Sub-tabs (nested) ── */
.stTabs .stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #cbd5e1;
    margin-top: 12px;
}
.stTabs .stTabs [data-baseweb="tab"] {
    font-size: 0.88rem;
    padding: 7px 16px;
    background: #f8fafc;
}
.stTabs .stTabs [aria-selected="true"] {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-bottom: 2px solid #eff6ff !important;
}

/* ── Article cards ── */
.article-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563EB;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: box-shadow 0.2s, transform 0.15s;
}
.article-card:hover {
    box-shadow: 0 6px 20px rgba(37,99,235,0.12);
    transform: translateY(-1px);
}
.article-date {
    font-size: 0.75rem;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 5px;
}
.article-title {
    font-size: 0.97rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 6px 0;
    line-height: 1.45;
}
.article-title a {
    color: #1e293b;
    text-decoration: none;
}
.article-title a:hover {
    color: #2563EB;
    text-decoration: underline;
}
.article-summary {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.55;
    margin: 0;
}

/* ── Section label badge ── */
.section-badge {
    display: inline-block;
    background: #EFF6FF;
    color: #1D4ED8;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 6px;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── Info box ── */
.info-box {
    background: #F0F7FF;
    border: 1px solid #BFDBFE;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.875rem;
    color: #1e40af;
    margin-bottom: 16px;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.78rem;
    padding: 20px;
    border-top: 1px solid #e2e8f0;
    margin-top: 24px;
}
.footer a { color: #2563EB; text-decoration: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    font-weight: 600;
    color: #334155;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="bank-header">
    <div class="bank-header-left">
        <h1>🏦 AI Bank</h1>
        <p>Tablou de bord · Date oficiale BNM</p>
    </div>
    <div class="bank-header-right">
        Actualizat la<br>
        <strong style="color:rgba(255,255,255,0.85)">{datetime.now().strftime('%d.%m.%Y · %H:%M')}</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB-URI
# ─────────────────────────────────────────────
tab_bancar, tab_cursuri, tab_comunicate = st.tabs([
    "🏦 Sectorul Bancar",
    "💱 Cursuri Valutare",
    "📰 Comunicate BNM"
])

# ─────────────────────────────────────────────
# FUNCȚII CURSURI VALUTARE
# ─────────────────────────────────────────────

def get_exchange_rate(date_str):
    url = f"https://www.bnm.md/en/official_exchange_rates?get_xml=1&date={date_str}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.warning(f"Eroare la încărcarea datelor pentru {date_str}: {e}")
    return None

def parse_xml(xml_content):
    rates = {}
    try:
        root = ET.fromstring(xml_content)
        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            name = valute.find('Name').text
            value = float(valute.find('Value').text)
            nominal = int(valute.find('Nominal').text)
            rates[code] = {
                'name': name,
                'value': value / nominal,
                'nominal': nominal
            }
    except Exception:
        pass
    return rates

@st.cache_data(ttl=3600)
def get_historical_data(days=30):
    data = []
    end_date = datetime.now()
    for i in range(0, days, 1):
        date = end_date - timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        xml_content = get_exchange_rate(date_str)
        if xml_content:
            rates = parse_xml(xml_content)
            if rates:
                for code, info in rates.items():
                    data.append({
                        'Data': date.date(),
                        'Cod': code,
                        'Moneda': info['name'],
                        'Curs': info['value']
                    })
    if data:
        df = pd.DataFrame(data)
        df['Data'] = pd.to_datetime(df['Data'])
        df = df.sort_values('Data', ascending=True)
        return df
    return pd.DataFrame()

# ─────────────────────────────────────────────
# FUNCȚII CAPITAL BANCAR
# ─────────────────────────────────────────────

def _parse_capital_df(df):
    """Parsează orice DataFrame Excel cu structura BNM: detectează bănci și indicatori."""
    # Detectează rândul cu numele băncilor (rândul cu cele mai multe celule text în col 5+)
    banks, bank_cols = [], []
    for row_idx in range(min(8, len(df))):
        vals_, cols_ = [], []
        for col_idx in range(5, len(df.columns)):
            v = str(df.iloc[row_idx, col_idx]).strip()
            if v and v.lower() not in ('nan', 'none', ''):
                vals_.append(v)
                cols_.append(col_idx)
        if len(vals_) > len(banks):
            banks, bank_cols = vals_, cols_

    if not banks:
        banks = ['MAIB', 'OTP Bank', 'Moldindconbank', 'Victoriabank']
        bank_cols = list(range(6, 10))

    indicators = []
    for i in range(len(df)):
        name = str(df.iloc[i, 2]).strip() if df.shape[1] > 2 else ''
        unit = str(df.iloc[i, 3]).strip() if df.shape[1] > 3 else ''
        if not name or name.lower() in ('nan', 'none', ''):
            continue
        values = []
        has_num = False
        for c in bank_cols:
            try:
                values.append(float(df.iloc[i, c]))
                has_num = True
            except (ValueError, TypeError):
                values.append(0.0)
        if has_num:
            indicators.append({'nr': i, 'name': name, 'unit': unit, 'values': values})

    return banks, indicators


CAPITAL_LOCAL = "data/Capital decembrie.xls"

@st.cache_data
def load_capital_data():
    """Încarcă Capital decembrie.xls și auto-detectează toate băncile și indicatorii."""
    df = pd.read_excel(CAPITAL_LOCAL, sheet_name=0, header=None, engine='xlrd')
    return _parse_capital_df(df)


@st.cache_data(ttl=3600)
def fetch_bnm_capital():
    """Descarcă datele despre capitalul bancar direct de pe BNM.md."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    search_urls = [
        "https://www.bnm.md/ro/content/indicatorii-de-capital-ai-bancilor",
        "https://www.bnm.md/ro/content/capitalul-bancilor",
        "https://www.bnm.md/ro/content/indicatorii-sectorului-bancar",
        "https://www.bnm.md/ro/content/sectorul-bancar-statistici",
    ]
    for url in search_urls:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.content, 'html.parser')
            # Caută linkuri spre fișiere Excel
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ('.xlsx', '.xls')):
                    if not href.startswith('http'):
                        href = 'https://www.bnm.md' + href
                    er = requests.get(href, headers=headers, timeout=30)
                    if er.status_code == 200:
                        raw = pd.read_excel(io.BytesIO(er.content), sheet_name=0, header=None)
                        banks, indicators = _parse_capital_df(raw)
                        if banks and indicators:
                            return banks, indicators, url
            # Dacă nu e Excel, încearcă tabel HTML
            tables = soup.find_all('table')
            if tables:
                dfs = pd.read_html(io.StringIO(str(tables[0])))
                if dfs:
                    banks, indicators = _parse_capital_df(dfs[0])
                    if banks and indicators:
                        return banks, indicators, url
        except Exception:
            continue
    return None, None, None

def make_bar_chart(banks, values, title, yaxis_label, color_seq=None):
    fig = px.bar(
        x=banks,
        y=values,
        title=title,
        labels={'x': 'Bancă', 'y': yaxis_label},
        color=banks,
        color_discrete_sequence=color_seq or px.colors.qualitative.Set2,
        text_auto='.2f'
    )
    fig.update_traces(
        textposition='outside',
        textfont=dict(size=15, color='black', family='Arial Black')
    )
    max_val = max(v for v in values if v is not None)
    fig.update_layout(
        showlegend=False,
        xaxis_title='',
        yaxis_title=yaxis_label,
        yaxis=dict(range=[0, max_val * 1.25]),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, Arial'),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#f1f5f9')
    return fig

_bold_font = dict(size=14, color='black', family='Arial Black')

def create_pdf_indicatori(df_table, banks):
    def clean(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF(orientation='L')
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, clean('Indicatori Capital Bancar - Decembrie 2025'), ln=True, align='C')
    pdf.ln(3)

    page_w = 277  # A4 landscape utilizabil (mm)
    col_ind = 80
    col_unit = 18
    col_bank = max(14, int((page_w - col_ind - col_unit) / max(len(banks), 1)))

    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_ind, 8, 'Indicator', border=1, fill=True)
    pdf.cell(col_unit, 8, 'Unitate', border=1, fill=True)
    for bank in banks:
        pdf.cell(col_bank, 8, clean(bank), border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(0, 0, 0)
    for i, row in df_table.iterrows():
        if i % 2 == 0:
            pdf.set_fill_color(235, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_ind, 6, clean(str(row['Indicator'])[:55]), border=1, fill=True)
        pdf.cell(col_unit, 6, clean(str(row['Unitate'])), border=1, fill=True, align='C')
        for bank in banks:
            val = row[bank]
            try:
                val_str = f'{float(val):.2f}'
            except Exception:
                val_str = '-'
            pdf.cell(col_bank, 6, val_str, border=1, fill=True, align='C')
        pdf.ln()

    return bytes(pdf.output())

def make_grouped_bar_chart(banks, values1, values2, name1, name2, title, yaxis_label):
    fig = go.Figure()
    fig.add_trace(go.Bar(name=name1, x=banks, y=values1,
                         text=[f'{v:.2f}' for v in values1],
                         textposition='outside', textfont=_bold_font))
    fig.add_trace(go.Bar(name=name2, x=banks, y=values2,
                         text=[f'{v:.2f}' for v in values2],
                         textposition='outside', textfont=_bold_font))
    max_val = max(max(values1), max(values2))
    fig.update_layout(
        barmode='group',
        title=title,
        xaxis_title='',
        yaxis_title=yaxis_label,
        yaxis=dict(range=[0, max_val * 1.25]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, Arial'),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#f1f5f9')
    return fig

# ─────────────────────────────────────────────
# FUNCȚII COMUNICATE BNM
# ─────────────────────────────────────────────

@st.cache_data(ttl=1800)
def get_bnm_comunicate():
    """Preia comunicatele de presă din RSS-ul oficial BNM"""
    url = "https://www.bnm.md/ro/rss.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        channel = root.find('channel')
        if channel is None:
            return {'error': 'Format RSS nerecunoscut'}

        articles = []
        for item in channel.findall('item'):
            titlu = item.findtext('title', '').strip()
            link  = item.findtext('link', '').strip()
            data  = item.findtext('pubDate', '').strip()
            desc  = item.findtext('description', '').strip()

            # Curăță HTML din descriere
            if desc:
                soup_desc = BeautifulSoup(desc, 'html.parser')
                desc = soup_desc.get_text(separator=' ', strip=True)[:200]

            # Formatează data
            try:
                dt = datetime.strptime(data, '%a, %d %b %Y %H:%M:%S %z')
                data = dt.strftime('%d.%m.%Y')
            except Exception:
                pass

            if titlu:
                articles.append({
                    'titlu': titlu,
                    'link': link,
                    'data': data,
                    'rezumat': desc
                })

        return articles

    except Exception as e:
        return {'error': str(e)}


# ─────────────────────────────────────────────
# FUNCȚII PORTOFOLIU CREDITE & RATA DOBÂNZII
# ─────────────────────────────────────────────

CREDIT_REPORT_LOCAL = "data/Credit_report_12_2025.csv.txt"
INTEREST_RATE_LOCAL = "data/Reports interest rate.xls"

_BNM_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


@st.cache_data
def load_credit_local():
    try:
        df = pd.read_csv(CREDIT_REPORT_LOCAL)
        df.columns = df.columns.str.strip()
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).replace({'nan': ''})
        return df, None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=3600)
def fetch_bnm_credit():
    """Extrage portofoliul de credite de pe BNM.md (încearcă mai multe URL-uri)."""
    urls = [
        "https://www.bnm.md/ro/content/portofoliul-de-credite-al-sectorului-bancar-rezident-consolidat",
        "https://www.bnm.md/ro/content/portofoliul-credite-sector-bancar",
        "https://www.bnm.md/ro/content/credite",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=_BNM_HEADERS, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                tables = soup.find_all('table')
                if tables:
                    dfs = pd.read_html(io.StringIO(str(tables[0])))
                    if dfs and len(dfs[0].columns) >= 2:
                        return dfs[0], None
        except Exception:
            continue
    return None, "Pagina BNM.md nu a putut fi accesată"


@st.cache_data
def load_interest_local():
    def _clean(df):
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).replace({'nan': ''})
        return df

    try:
        df = pd.read_excel(INTEREST_RATE_LOCAL, engine='xlrd')
        return _clean(df), None
    except Exception:
        try:
            df = pd.read_excel(INTEREST_RATE_LOCAL)
            return _clean(df), None
        except Exception as e:
            return None, str(e)


@st.cache_data(ttl=3600)
def fetch_bnm_dobanzi():
    """Extrage ratele dobânzilor de pe BNM.md."""
    urls = [
        "https://www.bnm.md/ro/content/ratele-dobanzilor-in-sectorul-bancar",
        "https://www.bnm.md/ro/content/rata-dobanzii-in-sectorul-bancar",
        "https://www.bnm.md/ro/content/rata-dobanzii",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=_BNM_HEADERS, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                tables = soup.find_all('table')
                if tables:
                    dfs = pd.read_html(io.StringIO(str(tables[0])))
                    if dfs and len(dfs[0].columns) >= 2:
                        return dfs[0], None
        except Exception:
            continue
    return None, "Pagina BNM.md nu a putut fi accesată"


# ═════════════════════════════════════════════
# TAB 1: SECTORUL BANCAR
# ═════════════════════════════════════════════
with tab_bancar:
    sub_capital, sub_credite, sub_dobanzi = st.tabs([
        "💰 Capital Bancar",
        "📊 Portofoliu Credite",
        "📈 Rata Dobânzii",
    ])

    # ── SUB-TAB 1: Capital Bancar ──────────────────────────────────────
    with sub_capital:
        st.markdown('<span class="section-badge">Capital Bancar</span>', unsafe_allow_html=True)
        st.markdown("### 🏦 Capital Bancar")

        col_r0, _ = st.columns([1, 4])
        with col_r0:
            if st.button("🔄 Actualizează", key="btn_capital_refresh"):
                st.cache_data.clear()
                st.rerun()

        banks, indicators, source_cap = None, None, None

        with st.spinner("Se extrag datele despre capitalul bancar..."):
            bnm_banks, bnm_indicators, bnm_url = fetch_bnm_capital()
            if bnm_banks and bnm_indicators:
                banks, indicators = bnm_banks, bnm_indicators
                source_cap = f"🌐 BNM.md (live) — {bnm_url}"
            else:
                try:
                    banks, indicators = load_capital_data()
                    source_cap = "📁 Capital.xlsx (local)"
                except FileNotFoundError:
                    st.error("Fișierul Capital decembrie.xls nu a fost găsit și BNM.md nu este accesibil.")
                except Exception as e:
                    st.error(f"Eroare la încărcarea datelor: {e}")

        if banks and indicators:
            st.caption(f"Sursă: {source_cap} · {len(banks)} bănci · {len(indicators)} indicatori")

            def vals(idx):
                if idx >= len(indicators):
                    return [0.0] * len(banks)
                return [float(v) if v is not None else 0.0 for v in indicators[idx]['values']]

            n = len(indicators)
            color_cycle = [
                px.colors.qualitative.Bold,
                px.colors.qualitative.Pastel,
                px.colors.qualitative.Safe,
                px.colors.qualitative.Antique,
                px.colors.qualitative.Set2,
            ]

            # ── Grafice pentru primii 5 indicatori disponibili
            for i, ind in enumerate(indicators[:5]):
                st.markdown(f"#### {i+1}. {ind['name']} ({ind['unit']})")
                fig = make_bar_chart(
                    banks, vals(i),
                    title=f"{ind['name']} per bancă",
                    yaxis_label=ind['unit'] or 'valoare',
                    color_seq=color_cycle[i % len(color_cycle)]
                )
                # Linie de referință la 10% pentru indicatori de rată
                if '%' in str(ind['unit']) and max(vals(i), default=0) > 0:
                    fig.add_hline(y=10, line_dash='dash', line_color='red',
                                  annotation_text='Minim 10%',
                                  annotation_position='bottom right')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")

            # ── Grafic grupat nivel 1 vs nivel 2 (dacă există cel puțin 3 indicatori)
            if n >= 3:
                st.markdown(f"#### {indicators[1]['name']} vs {indicators[2]['name']}")
                fig_grp = make_grouped_bar_chart(
                    banks, vals(1), vals(2),
                    indicators[1]['name'], indicators[2]['name'],
                    title=f"{indicators[1]['name']} vs {indicators[2]['name']} per bancă",
                    yaxis_label=indicators[1]['unit'] or 'mil. lei'
                )
                st.plotly_chart(fig_grp, use_container_width=True)
                st.markdown("---")

            # ── Tabel sumar
            st.markdown("#### 📋 Tabel sumar indicatori")
            table_data = {
                'Indicator': [ind['name'] for ind in indicators],
                'Unitate':   [ind['unit'] for ind in indicators],
            }
            for j, bank in enumerate(banks):
                table_data[bank] = [
                    ind['values'][j] if j < len(ind['values']) else None
                    for ind in indicators
                ]
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, width='stretch', hide_index=True)

            col_csv, col_pdf = st.columns(2)
            with col_csv:
                st.download_button(
                    label="📥 Descarcă CSV",
                    data=df_table.to_csv(index=False).encode('utf-8'),
                    file_name="indicatori_capital_bancar.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_pdf:
                st.download_button(
                    label="📄 Descarcă PDF",
                    data=create_pdf_indicatori(df_table, banks),
                    file_name="indicatori_capital_bancar.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    # ── SUB-TAB 2: Portofoliu Credite ─────────────────────────────────
    with sub_credite:
        st.markdown('<span class="section-badge">Portofoliu Credite</span>', unsafe_allow_html=True)
        st.markdown("### 📊 Portofoliu de Credite — Sector Bancar")
        st.markdown(
            '<div class="info-box">Date privind portofoliul de credite al sectorului bancar. '
            'Se încearcă extragerea live de pe <strong>bnm.md</strong>; '
            'dacă nu este disponibil, se folosesc datele locale.</div>',
            unsafe_allow_html=True
        )

        col_r1, _ = st.columns([1, 4])
        with col_r1:
            if st.button("🔄 Actualizează", key="btn_credit_refresh"):
                st.cache_data.clear()
                st.rerun()

        with st.spinner("Se extrag datele despre portofoliul de credite..."):
            df_credit, _err_cr_bnm = fetch_bnm_credit()
            source_credit = "🌐 BNM.md (live)"
            if df_credit is None:
                df_credit, _err_cr_local = load_credit_local()
                source_credit = "📁 Fișier local"

        if df_credit is not None:
            st.caption(f"Sursă date: {source_credit}")

            # Detectează coloanele
            col_cat = next(
                (c for c in df_credit.columns if any(k in c for k in ['Borrower', 'Category', 'Categor', 'Debitor'])),
                df_credit.columns[0]
            )
            col_cur = next(
                (c for c in df_credit.columns if any(k in c for k in ['Currency', 'Valut', 'Tip'])),
                df_credit.columns[1] if len(df_credit.columns) > 1 else None
            )
            col_vol = next(
                (c for c in df_credit.columns if any(k in c for k in ['MDL', 'Volume', 'Volum', 'Mil.'])),
                df_credit.columns[2] if len(df_credit.columns) > 2 else None
            )

            if col_vol and col_cat:
                df_det = df_credit[~df_credit[col_cat].astype(str).str.contains('Total', na=False)].copy()
                if not df_det.empty:
                    st.markdown("#### Volum credite după categoria debitorului (Mil. MDL)")
                    bar_kwargs = dict(
                        x=col_cat,
                        y=col_vol,
                        title='Portofoliu Credite — volum după categoria debitorului',
                        labels={col_vol: 'Volum (Mil. MDL)', col_cat: 'Categorie Debitor'},
                        text_auto='.2f',
                        color_discrete_sequence=px.colors.qualitative.Bold,
                    )
                    if col_cur:
                        bar_kwargs['color'] = col_cur
                        bar_kwargs['barmode'] = 'group'
                    fig_cr = px.bar(df_det, **bar_kwargs)
                    fig_cr.update_layout(
                        xaxis_tickangle=-20,
                        plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Inter, Arial'),
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    )
                    fig_cr.update_yaxes(gridcolor='#f1f5f9')
                    fig_cr.update_xaxes(showgrid=False)
                    st.plotly_chart(fig_cr, use_container_width=True)

                if col_cur:
                    df_tot = df_credit[df_credit[col_cat].astype(str).str.contains('Total', na=False)].copy()
                    if not df_tot.empty:
                        st.markdown("---")
                        st.markdown("#### Distribuția creditelor după tipul valutei")
                        fig_pie = px.pie(
                            df_tot,
                            values=col_vol,
                            names=col_cur,
                            title='Distribuția după tipul valutei (Total Sector Bancar)',
                            color_discrete_sequence=px.colors.qualitative.Set2,
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
                        st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📋 Date complete")
            st.dataframe(df_credit, width='stretch', hide_index=True)
            st.download_button(
                label="📥 Descarcă CSV",
                data=df_credit.to_csv(index=False).encode('utf-8'),
                file_name="portofoliu_credite_sector_bancar.csv",
                mime="text/csv",
            )
        else:
            st.error("Nu s-au putut încărca datele despre portofoliul de credite.")
            st.info(
                "Asigură-te că fișierul `Credit_report_12_2025.csv.txt` există la calea configurată "
                "sau că BNM.md este accesibil."
            )

    # ── SUB-TAB 3: Rata Dobânzii ──────────────────────────────────────
    with sub_dobanzi:
        st.markdown('<span class="section-badge">Rata Dobânzii</span>', unsafe_allow_html=True)
        st.markdown("### 📈 Ratele Dobânzilor — Sector Bancar")
        st.markdown(
            '<div class="info-box">Ratele dobânzilor în sectorul bancar din Republica Moldova, '
            'extrase de pe <strong>bnm.md</strong> sau din fișierul local.</div>',
            unsafe_allow_html=True
        )

        col_r2, _ = st.columns([1, 4])
        with col_r2:
            if st.button("🔄 Actualizează", key="btn_dobanzi_refresh"):
                st.cache_data.clear()
                st.rerun()

        with st.spinner("Se extrag ratele dobânzilor..."):
            df_dobanzi, _err_db_bnm = fetch_bnm_dobanzi()
            source_dobanzi = "🌐 BNM.md (live)"
            if df_dobanzi is None:
                df_dobanzi, _err_db_local = load_interest_local()
                source_dobanzi = "📁 Fișier local"

        if df_dobanzi is not None:
            st.caption(f"Sursă date: {source_dobanzi}")
            st.dataframe(df_dobanzi, width='stretch')

            # Grafic automat dacă există coloane numerice și de dată
            numeric_cols = df_dobanzi.select_dtypes(include='number').columns.tolist()
            date_cols = [
                c for c in df_dobanzi.columns
                if any(k in str(c).lower() for k in ['dat', 'period', 'an', 'luna', 'year', 'month'])
            ]
            if numeric_cols and date_cols:
                st.markdown("---")
                st.markdown("#### Evoluție rate dobânzi (%)")
                fig_db = px.line(
                    df_dobanzi,
                    x=date_cols[0],
                    y=numeric_cols[:5],
                    title='Evoluția ratelor dobânzilor în sectorul bancar (%)',
                    markers=True,
                )
                fig_db.update_layout(
                    plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family='Inter, Arial'),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                )
                fig_db.update_yaxes(gridcolor='#f1f5f9')
                fig_db.update_xaxes(showgrid=False)
                st.plotly_chart(fig_db, use_container_width=True)

            st.download_button(
                label="📥 Descarcă CSV",
                data=df_dobanzi.to_csv(index=False).encode('utf-8'),
                file_name="ratele_dobanzilor_sector_bancar.csv",
                mime="text/csv",
            )
        else:
            st.error("Nu s-au putut încărca datele despre ratele dobânzilor.")
            st.info(
                "Asigură-te că fișierul `Reports interest rate.xls` există la calea configurată "
                "sau că BNM.md este accesibil."
            )


# ═════════════════════════════════════════════
# TAB 2: CURSURI VALUTARE
# ═════════════════════════════════════════════
with tab_cursuri:
    st.markdown('<span class="section-badge">Cursuri Valutare</span>', unsafe_allow_html=True)

    st.sidebar.header("⚙️ Setări Cursuri Valutare")

    period_options = {
        "Ultima săptămână": 7,
        "Ultimele 2 săptămâni": 14,
        "Ultima lună": 30
    }
    selected_period = st.sidebar.selectbox(
        "Perioada:",
        options=list(period_options.keys()),
        index=0
    )
    days = period_options[selected_period]

    main_currencies = ['EUR', 'USD', 'RON', 'UAH', 'GBP', 'CHF', 'RUB']
    selected_currencies = st.sidebar.multiselect(
        "Monede de afișat:",
        options=main_currencies,
        default=['EUR', 'USD']
    )

    if st.sidebar.button("🔄 Reîncarcă datele"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner('Se încarcă datele de la BNM...'):
        df = get_historical_data(days)

    if not df.empty and selected_currencies:
        df_filtered = df[df['Cod'].isin(selected_currencies)].copy()
        df_filtered = df_filtered.sort_values('Data', ascending=True)

        latest_date = df_filtered['Data'].max()
        st.markdown(f"### 💰 Cursul valutar din {latest_date.strftime('%d.%m.%Y')}")
        latest_rates = df_filtered[df_filtered['Data'] == latest_date]

        cols = st.columns(len(selected_currencies))
        for i, currency in enumerate(selected_currencies):
            rate_data = latest_rates[latest_rates['Cod'] == currency]
            if not rate_data.empty:
                rate = rate_data['Curs'].values[0]
                cols[i].metric(label=currency, value=f"{rate:.4f} MDL")

        st.markdown("---")
        st.markdown("### 📈 Evoluția cursului valutar")

        fig = px.line(
            df_filtered,
            x='Data',
            y='Curs',
            color='Cod',
            title=f'Evoluția cursului valutar — {selected_period}',
            labels={'Data': 'Data', 'Curs': 'Curs (MDL)', 'Cod': 'Moneda'},
            markers=True
        )
        fig.update_layout(
            hovermode='x unified',
            xaxis=dict(tickformat='%d.%m.%Y', tickmode='auto', nticks=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Inter, Arial'),
        )
        fig.update_yaxes(gridcolor='#f1f5f9')
        fig.update_xaxes(showgrid=False)
        fig.update_traces(mode='lines+markers')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Tabel cu date")
        pivot_df = df_filtered.pivot_table(
            index='Data', columns='Cod', values='Curs'
        ).reset_index()
        pivot_df['Data'] = pivot_df['Data'].dt.strftime('%d.%m.%Y')
        pivot_df = pivot_df.sort_values('Data', ascending=False)
        st.dataframe(pivot_df, width='stretch', hide_index=True)

        csv = pivot_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descarcă CSV",
            data=csv,
            file_name="cursuri_valutare_bnm.csv",
            mime="text/csv"
        )

    else:
        if df.empty:
            st.error("Nu s-au putut încărca datele de la BNM. Încearcă să reîncarci pagina.")
        else:
            st.warning("Selectează cel puțin o monedă din meniul din stânga.")


# ═════════════════════════════════════════════
# TAB 3: COMUNICATE BNM
# ═════════════════════════════════════════════
with tab_comunicate:
    st.markdown('<span class="section-badge">Comunicate de Presă</span>', unsafe_allow_html=True)
    st.markdown("### 📰 Comunicate BNM")
    st.markdown(
        '<div class="info-box">Comunicate oficiale publicate de Banca Națională a Moldovei. '
        'Date preluate automat de pe <strong>bnm.md</strong> · Actualizare la 30 min.</div>',
        unsafe_allow_html=True
    )

    col_refresh, col_link = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Actualizează", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_link:
        st.markdown(
            "🔗 [Deschide pagina BNM](https://www.bnm.md/ro/search?partitions%5B0%5D=676)",
            unsafe_allow_html=False
        )

    with st.spinner('Se încarcă comunicatele de la BNM...'):
        rezultate = get_bnm_comunicate()

    if isinstance(rezultate, dict) and 'error' in rezultate:
        st.error(f"Nu s-au putut încărca comunicatele: {rezultate['error']}")
        st.info("Verifică conexiunea la internet sau încearcă din nou mai târziu.")

    elif not rezultate:
        st.warning("Nu s-au găsit comunicate. Structura paginii BNM poate fi diferită.")
        st.markdown(
            "Poți accesa direct: [bnm.md/ro/search?partitions[0]=676](https://www.bnm.md/ro/search?partitions%5B0%5D=676)"
        )

    else:
        st.markdown(f"**{len(rezultate)} comunicate găsite**")
        st.markdown("")

        # Câmp de căutare
        search_term = st.text_input(
            "🔍 Caută în comunicate:",
            placeholder="ex: politică monetară, inflație, curs valutar..."
        )

        articles_to_show = rezultate
        if search_term:
            search_lower = search_term.lower()
            articles_to_show = [
                a for a in rezultate
                if search_lower in a['titlu'].lower() or search_lower in a['rezumat'].lower()
            ]
            if not articles_to_show:
                st.info(f"Nu s-au găsit rezultate pentru '{search_term}'.")

        for art in articles_to_show:
            titlu  = art['titlu']
            link   = art['link']
            data   = art['data']
            rezumat = art['rezumat']

            date_html    = f'<span class="article-date">📅 {data}</span>' if data else ''
            link_open    = f'<a href="{link}" target="_blank">' if link else ''
            link_close   = '</a>' if link else ''
            summary_html = f'<p class="article-summary">{rezumat}</p>' if rezumat else ''

            st.markdown(f"""
            <div class="article-card">
                {date_html}
                <div class="article-title">{link_open}{titlu}{link_close}</div>
                {summary_html}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Date oficiale de la <a href="https://www.bnm.md" target="_blank">Banca Națională a Moldovei</a> ·
    Cursurile și comunicatele sunt actualizate automat
</div>
""", unsafe_allow_html=True)
