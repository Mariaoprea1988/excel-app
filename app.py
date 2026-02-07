import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

# Configurare pagina
st.set_page_config(
    page_title="Cursuri Valutare BNM",
    page_icon="💱",
    layout="wide"
)

st.title("📊 Cursuri Valutare - Banca Națională a Moldovei")
st.markdown("Date oficiale preluate automat de la [BNM](https://www.bnm.md)")

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

# Sidebar pentru configurare
st.sidebar.header("⚙️ Setări")

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
    st.subheader("💰 Cursul valutar de azi")

    latest_date = df_filtered['Data'].max()
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
