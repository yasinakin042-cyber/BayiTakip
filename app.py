import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kahveci Otomotiv - Bayi Takip Sistemi", layout="wide")

st.title("Kahveci Otomotiv - Bayi ve Ziyaret Takip Haritası")

@st.cache_data
def load_data():
    df = pd.read_csv("musteriler.csv")
    df['enlem'] = pd.to_numeric(df['enlem'], errors='coerce')
    df['boylam'] = pd.to_numeric(df['boylam'], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Hata: {e}")
    st.stop()

# Gitmediğin şehirleri tamamen siliyoruz
haric_tutulacak_sehirler = ['Şanlıurfa', 'Trabzon', 'Antalya', 'Denizli', 'Urfa']
df = df[~df['sehir'].isin(haric_tutulacak_sehirler)]

st.sidebar.header("📍 Şehir Filtresi")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", sehirler)

if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
else:
    df_filtered = df

st.subheader(f"Harita — {secilen_sehir}")

fig = px.scatter_geo(
    df_filtered,
    lat="enlem",
    lon="boylam",
    color="sehir",
    hover_name="bayi_adi",
    hover_data=["yetkili", "telefon", "adres", "detay"],
    projection="mercator",
    height=500
)

fig.update_geos(
    visible=True,
    resolution=50,
    scope="europe",
    showcountries=True, countrycolor="#888888",
    showsubunits=True, subunitcolor="#dddddd",
    showland=True, landcolor="white",
    showocean=True, oceancolor="#ffffff",
    center={"lat": 39.1667, "lon": 35.2433},
    lonaxis_range=[26, 45],
    lataxis_range=[36, 42]
)

fig.update_layout(
    template="plotly_white",
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("📋 Müşteri ve Bayi Listesi")
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
