import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import io
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from fpdf import FPDF

# Configurare pagina
st.set_page_config(
    page_title="AI Bank",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 AI Bank")
st.markdown("AI Bank")

# ─────────────────────────────────────────────
# TAB-URI
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .stTabs [data-baseweb="tab"] {
        font-size: 1.25rem;
        padding: 10px 24px;
    }
    .stTabs [data-baseweb="tab"] p {
        font-size: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

tab2, tab1 = st.tabs(["🏦 Sectorul Bancar", "💱 Cursuri Valutare"])

# ─────────────────────────────────────────────
# FUNCȚII CURSURI VALUTARE
# ─────────────────────────────────────────────

def get_exchange_rate(date_str):
    """Preia cursul valutar pentru o anumită dată"""
    url = f"https://www.bnm.md/en/official_exchange_rates?get_xml=1&date={date_str}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.warning(f"Eroare la încărcarea datelor pentru {date_str}: {e}")
    return None

def parse_xml(xml_content):
    """Parsează XML-ul și returnează un dicționar cu cursurile"""
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
    except Exception as e:
        pass
    return rates

@st.cache_data(ttl=3600)
def get_historical_data(days=30):
    """Preia datele istorice pentru ultimele N zile"""
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

@st.cache_data
def load_capital_data():
    """Citește datele de capital din Capital.xlsx"""
    df = pd.read_excel('Capital.xlsx', sheet_name=0, header=None)
    # Row index 3 = row 4 in Excel = header with bank names
    banks = ['MAIB', 'OTP Bank', 'Moldindconbank', 'Victoriabank']
    indicators = []
    for i in range(4, 12):  # rows 5-12 in Excel (0-indexed 4-11)
        nr = df.iloc[i, 1]
        name = str(df.iloc[i, 2]).strip()
        unit = str(df.iloc[i, 3]).strip()
        values = list(df.iloc[i, 6:10])
        indicators.append({
            'nr': nr,
            'name': name,
            'unit': unit,
            'values': values
        })
    return banks, indicators

def make_bar_chart(banks, values, title, yaxis_label, color_seq=None):
    """Creează un bar chart simplu per bancă"""
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
        yaxis=dict(range=[0, max_val * 1.25])
    )
    return fig

_bold_font = dict(size=14, color='black', family='Arial Black')

def create_pdf_indicatori(df_table, banks):
    """Generează PDF pentru tabelul de indicatori"""
    def clean(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF(orientation='L')
    pdf.add_page()

    # Titlu
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, clean('Indicatori Capital Bancar - Decembrie 2025'), ln=True, align='C')
    pdf.ln(3)

    # Latimi coloane
    col_ind = 90
    col_unit = 22
    col_bank = 38

    # Header tabel
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_fill_color(52, 152, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(col_ind, 8, 'Indicator', border=1, fill=True)
    pdf.cell(col_unit, 8, 'Unitate', border=1, fill=True)
    for bank in banks:
        pdf.cell(col_bank, 8, clean(bank), border=1, fill=True, align='C')
    pdf.ln()

    # Randuri
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
            except:
                val_str = '-'
            pdf.cell(col_bank, 6, val_str, border=1, fill=True, align='C')
        pdf.ln()

    return bytes(pdf.output())

def make_grouped_bar_chart(banks, values1, values2, name1, name2, title, yaxis_label):
    """Creează un bar chart grupat pentru doi indicatori"""
    fig = go.Figure()
    fig.add_trace(go.Bar(name=name1, x=banks, y=values1, text=[f'{v:.2f}' for v in values1], textposition='outside', textfont=_bold_font))
    fig.add_trace(go.Bar(name=name2, x=banks, y=values2, text=[f'{v:.2f}' for v in values2], textposition='outside', textfont=_bold_font))
    max_val = max(max(values1), max(values2))
    fig.update_layout(
        barmode='group',
        title=title,
        xaxis_title='',
        yaxis_title=yaxis_label,
        yaxis=dict(range=[0, max_val * 1.25]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

# ═════════════════════════════════════════════
# TAB 1: CURSURI VALUTARE
# ═════════════════════════════════════════════
with tab1:
    # Sidebar pentru configurare
    st.sidebar.header("⚙️ Setări Cursuri Valutare")

    # Selectare perioadă
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

    # Monede principale
    main_currencies = ['EUR', 'USD', 'RON', 'UAH', 'GBP', 'CHF', 'RUB']

    # Selectare monede
    selected_currencies = st.sidebar.multiselect(
        "Monede de afișat:",
        options=main_currencies,
        default=['EUR', 'USD']
    )

    # Buton pentru reîncărcare date
    if st.sidebar.button("🔄 Reîncarcă datele"):
        st.cache_data.clear()
        st.rerun()

    # Încărcăm datele
    with st.spinner('Se încarcă datele de la BNM... Așteaptă câteva secunde.'):
        df = get_historical_data(days)

    if not df.empty and selected_currencies:
        # Filtrăm pentru monedele selectate
        df_filtered = df[df['Cod'].isin(selected_currencies)].copy()
        df_filtered = df_filtered.sort_values('Data', ascending=True)

        # Afișăm cursul actual
        latest_date = df_filtered['Data'].max()
        st.subheader(f"💰 Cursul valutar din {latest_date.strftime('%d.%m.%Y')}")
        latest_rates = df_filtered[df_filtered['Data'] == latest_date]

        cols = st.columns(len(selected_currencies))
        for i, currency in enumerate(selected_currencies):
            rate_data = latest_rates[latest_rates['Cod'] == currency]
            if not rate_data.empty:
                rate = rate_data['Curs'].values[0]
                cols[i].metric(
                    label=currency,
                    value=f"{rate:.4f} MDL"
                )

        st.markdown("---")

        # Grafic principal
        st.subheader("📈 Evoluția cursului valutar")

        fig = px.line(
            df_filtered,
            x='Data',
            y='Curs',
            color='Cod',
            title=f'Evoluția cursului valutar - {selected_period}',
            labels={
                'Data': 'Data',
                'Curs': 'Curs (MDL)',
                'Cod': 'Moneda'
            },
            markers=True
        )

        fig.update_layout(
            hovermode='x unified',
            xaxis=dict(
                tickformat='%d.%m.%Y',
                tickmode='auto',
                nticks=10
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        fig.update_traces(mode='lines+markers')

        st.plotly_chart(fig, use_container_width=True)

        # Tabel cu date
        st.subheader("📋 Tabel cu date")

        # Pivot tabel
        pivot_df = df_filtered.pivot_table(
            index='Data',
            columns='Cod',
            values='Curs'
        ).reset_index()
        pivot_df['Data'] = pivot_df['Data'].dt.strftime('%d.%m.%Y')
        pivot_df = pivot_df.sort_values('Data', ascending=False)

        st.dataframe(pivot_df, use_container_width=True, hide_index=True)

        # Descărcare CSV
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
# TAB 2: SECTORUL BANCAR
# ═════════════════════════════════════════════
with tab2:
    st.subheader("🏦 Capital Bancar - Decembrie 2025")
    st.markdown("Date preluate din raportul BNM privind indicatorii de capital ai băncilor comerciale.")

    try:
        banks, indicators = load_capital_data()

        # Extragem valorile pentru fiecare indicator
        # ind[0]=1.1, ind[1]=1.2, ind[2]=1.3, ind[3]=1.4, ind[4]=1.5, ind[5]=1.6, ind[6]=1.7, ind[7]=1.8
        def vals(idx):
            return [float(v) if v is not None else 0.0 for v in indicators[idx]['values']]

        # ── Grafic 1: Fonduri proprii totale (1.4)
        st.markdown("### 1. Fonduri proprii totale (mil. lei)")
        fig1 = make_bar_chart(
            banks, vals(3),
            title='Fonduri proprii totale per bancă - Decembrie 2025',
            yaxis_label='mil. lei',
            color_seq=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        # ── Grafic 2: Capitalul social (1.1)
        st.markdown("### 2. Capitalul social (mil. lei)")
        fig2 = make_bar_chart(
            banks, vals(0),
            title='Capitalul social per bancă - Decembrie 2025',
            yaxis_label='mil. lei',
            color_seq=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # ── Grafic 3: Fonduri proprii nivel 1 + nivel 2 (1.2 + 1.3) - grupat
        st.markdown("### 3. Fonduri proprii nivel 1 de bază vs nivel 2 (mil. lei)")
        fig3 = make_grouped_bar_chart(
            banks,
            vals(1), vals(2),
            'Fonduri proprii nivel 1 de bază',
            'Fonduri proprii nivel 2',
            title='Fonduri proprii nivel 1 și nivel 2 per bancă - Decembrie 2025',
            yaxis_label='mil. lei'
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")

        # ── Grafic 4: Rata fondurilor proprii totale (1.7)
        st.markdown("### 4. Rata fondurilor proprii totale ≥ 10% (%)")
        fig4 = make_bar_chart(
            banks, vals(6),
            title='Rata fondurilor proprii totale per bancă - Decembrie 2025',
            yaxis_label='%',
            color_seq=px.colors.qualitative.Safe
        )
        # Linie de referință la 10%
        fig4.add_hline(y=10, line_dash='dash', line_color='red',
                       annotation_text='Minim 10%', annotation_position='bottom right')
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")

        # ── Grafic 5: Fonduri proprii / Total active (1.8)
        st.markdown("### 5. Fonduri proprii / Total active (%)")
        fig5 = make_bar_chart(
            banks, vals(7),
            title='Fonduri proprii / Total active per bancă - Decembrie 2025',
            yaxis_label='%',
            color_seq=px.colors.qualitative.Antique
        )
        st.plotly_chart(fig5, use_container_width=True)

        # Tabel sumar
        st.markdown("---")
        st.markdown("### 📋 Tabel sumar indicatori")
        table_data = {
            'Indicator': [ind['name'] for ind in indicators],
            'Unitate': [ind['unit'] for ind in indicators],
        }
        for j, bank in enumerate(banks):
            table_data[bank] = [ind['values'][j] for ind in indicators]

        df_table = pd.DataFrame(table_data)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        # Butoane descărcare
        col_csv, col_pdf = st.columns(2)
        with col_csv:
            csv_data = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv_data,
                file_name="indicatori_capital_bancar.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_pdf:
            pdf_data = create_pdf_indicatori(df_table, banks)
            st.download_button(
                label="📄 Descarcă PDF",
                data=pdf_data,
                file_name="indicatori_capital_bancar.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    except FileNotFoundError:
        st.error("Fișierul Capital.xlsx nu a fost găsit. Asigură-te că fișierul se află în același director cu app.py.")
    except Exception as e:
        st.error(f"Eroare la încărcarea datelor: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Date oficiale de la <a href='https://www.bnm.md' target='_blank'>Banca Națională a Moldovei</a><br>
        Cursurile sunt actualizate automat
    </div>
    """,
    unsafe_allow_html=True
)
