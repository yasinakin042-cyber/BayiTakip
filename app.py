import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

st.set_page_config(page_title="Kahveci Otomotiv - Bayi Takip ve Harita Sistemi", layout="wide")

st.title("Kahveci Otomotiv - İl Bazlı Bayi ve Ziyaret Takip Haritası")

# Veriyi oku
@st.cache_data
def load_data():
    df = pd.read_csv("musteriler.csv")
    df['enlem'] = pd.to_numeric(df['enlem'], errors='coerce')
    df['boylam'] = pd.to_numeric(df['boylam'], errors='coerce')
    return df

try:
    df = load_data()
    st.success("Müşteri verileri başarıyla yüklendi!")
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

# Türkiye il sınırları GeoJSON verisini çek (Açık kaynak harita verisi)
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geojson/tr-cities.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

geojson_data = load_geojson()

# Ziyaret edilen şehirleri belirle
ziyaret_edilen_sehirler = df['sehir'].dropna().unique().tolist()

# GeoJSON poligonlarını renklendirmek için veri hazırlığı
if geojson_data:
    for feature in geojson_data['features']:
        il_adi = feature['properties'].get('name') or feature['properties'].get('il')
        # Eğer gidildiyse renk ver, gidilmediyse beyaz/saydam yap
        if il_adi in ziyaret_edilen_sehirler:
            feature['properties']['fill_color'] = [255, 140, 0, 160] # Gidilen yerler turuncu/renkli
        else:
            feature['properties']['fill_color'] = [255, 255, 255, 230] # Gitmediğin yerler tamamen beyaz

# Kenar çubuğu (Sidebar)
st.sidebar.header("Filtreleme")
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", ["Tümü"] + sorted(ziyaret_edilen_sehirler))

if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    center_lat = df_filtered['enlem'].mean()
    center_lon = df_filtered['boylam'].mean()
    zoom_level = 7
else:
    df_filtered = df
    center_lat = 39.0
    center_lon = 35.0
    zoom_level = 5

# Pydeck Harita Katmanları
layers = []

# 1. İl Sınırları Poligon Katmanı
if geojson_data:
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[200, 200, 200, 200],
        line_width_min_pixels=1,
    )
    layers.append(geojson_layer)

# 2. Bayi Noktaları Katmanı
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    get_position='[boylam, enlem]',
    get_color=[220, 20, 60, 220],
    get_radius=8000,
    pickable=True,
    auto_highlight=True,
)
layers.append(scatterplot_layer)

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom_level,
    pitch=0,
)

r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={
        "html": "<b>İl / Şehir:</b> {name}<br><b>Bayi/Firma:</b> {bayi_adi}<br><b>Yetkili:</b> {yetkili}<br><b>Telefon:</b> {telefon}<br><b>Not:</b> {detay}",
        "style": {"backgroundColor": "#222", "color": "white", "padding": "10px", "borderRadius": "5px"}
    }
)

st.subheader("Türkiye İl Bazlı Bölge Haritası")
st.pydeck_chart(r)

# Alt Kısım: Ziyaret Geçmişi Tablosu
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📍 {secilen_sehir} — Ziyaret Geçmişi (Tarihe Göre)")
    st.dataframe(
        df_filtered[['bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.subheader("Tüm Müşteri ve Bayi Ziyaretleri")
    st.dataframe(
        df[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
        use_container_width=True,
        hide_index=True
    )
