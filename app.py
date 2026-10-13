import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Kahveci Otomotiv - Bayi Takip Sistemi", layout="wide")

st.title("Kahveci Otomotiv - Bayi ve Ziyaret Takip Haritası")

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

# Gitmediğin şehirleri sistemden tamamen temizle
haric_tutulacak_sehirler = ['Şanlıurfa', 'Trabzon', 'Antalya', 'Denizli', 'Urfa']
df = df[~df['sehir'].isin(haric_tutulacak_sehirler)]

# Sol Menü / Şehir Filtresi
st.sidebar.header("📍 Bölge / Şehir Seçimi")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Filtreleme mantığı
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    zoom_val = 7.5
    lat_center = df_filtered['enlem'].mean()
    lon_center = df_filtered['boylam'].mean()
else:
    df_filtered = df
    zoom_val = 5.8
    lat_center = 39.1667
    lon_center = 35.2433

st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Pydeck ile yüksek performanslı, açık tema uyumlu ve net harita
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    get_position='[boylam, enlem]',
    get_color='[255, 140, 0, 200]', # Turuncu renkli belirgin noktalar
    get_radius=25000,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=lat_center,
    longitude=lon_center,
    zoom=zoom_val,
    pitch=0,
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>Şehir:</b> {sehir}<br><b>Firma:</b> {bayi_adi}<br><b>Yetkili:</b> {yetkili}<br><b>Telefon:</b> {telefon}",
        "style": {"background": "white", "color": "black", "font-family": "Arial", "z-index": "10000"}
    },
    map_style="mapbox://styles/mapbox/light-v10" # Bembeyaz, tertemiz açık tema harita altyapısı
)

st.pydeck_chart(r)

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi ({len(df_filtered)} Kayıt)")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
else:
    st.subheader(f"📋 Tüm Türkiye ve Bölge Genelindeki Müşteri ve Bayiler ({len(df)} Kayıt)")

# Tabloyu eksiksiz göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
