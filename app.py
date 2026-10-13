import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kahveci Otomotiv - Bayi Takip ve Harita Sistemi", layout="wide")

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

# Kenar çubuğu (Sidebar) - Şehir seçimi
st.sidebar.header("📍 Bölge / Şehir Filtresi")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Filtreleme mantığı
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
else:
    df_filtered = df

# Üst Kısım: Plotly ile Profesyonel ve Türkçe Uyumlu Harita
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Plotly Scattermapbox (Türkçe etiketler, KKTC ve Türkiye uyumlu altlık)
fig = px.scatter_mapbox(
    df_filtered,
    lat="enlem",
    lon="boylam",
    color="sehir",
    hover_name="bayi_adi",
    hover_data=["yetkili", "telefon", "adres", "detay"],
    zoom=6 if secilen_sehir != "Tümü" else 5,
    center={"lat": 39.1667, "lon": 35.2433} if secilen_sehir == "Tümü" else None,
    height=600
)

# Harita stilini ayarla (OpenStreetMap tabanlı, Türkçe ve doğru coğrafi sınırlar)
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend_title_text="Şehirler"
)

# Eğer tek şehir seçildiyse haritayı o şehre odakla
if secilen_sehir != "Tümü" and not df_filtered.empty:
    fig.update_layout(
        mapbox_center={"lat": df_filtered['enlem'].mean(), "lon": df_filtered['boylam'].mean()},
        mapbox_zoom=7
    )

st.plotly_chart(fig, use_container_width=True)

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda tarihe/sıraya göre listelenmiştir.")
else:
    st.subheader("📋 Tüm Müşteri ve Bayi Ziyaretleri Listesi")

# Tabloyu göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
