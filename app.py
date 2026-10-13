import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Kahveci Otomotiv Bayi Takip", layout="wide")

st.title("Kahveci Otomotiv - Bayi Takip ve Harita Sistemi")

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

# Kenar çubuğu (Sidebar) - Şehir seçimi ve detay paneli
st.sidebar.header("Şehir ve Ziyaret Filtresi")
secilen_sehir = st.sidebar.selectbox("Şehir Seçin", ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist()))

# Filtreleme
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

# Üst Kısım: Türkiye Haritası (Açık tonlar / Beyaz tema uyumlu)
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Pydeck ile harita katmanı (Beyaz/açık zemin için özelleştirilmiş)
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    get_position='[boylam, enlem]',
    get_color="renk == 'red' ? [220, 20, 60, 200] : (renk == 'blue' ? [30, 144, 255, 200] : [255, 140, 0, 200])",
    get_radius=12000,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom_level,
    pitch=0,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v10", # Açık / Beyaz Türkiye haritası teması
    tooltip={
        "html": "<b>Şehir:</b> {sehir}<br><b>Firma:</b> {bayi_adi}<br><b>Yetkili:</b> {yetkili}<br><b>Telefon:</b> {telefon}<br><b>Not:</b> {detay}",
        "style": {"backgroundColor": "#222", "color": "white", "padding": "10px", "borderRadius": "5px"}
    }
)

st.pydeck_chart(r)

# Alt Kısım: Seçilen Şehre Ait Ziyaretler (Tarihe Göre Sıralı)
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📍 {secilen_sehir} — Ziyaret Geçmişi ve Detaylar")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
    
    # Tabloyu göster
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
