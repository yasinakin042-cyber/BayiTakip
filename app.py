import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Kahveci Otomotiv - Bayi ve Ziyaret Takip Sistemi", layout="wide")

st.title("Kahveci Otomotiv - Müşteri ve Bayi Ziyaret Takip Haritası")

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
else:
    df_filtered = df

# Harita Görünümü Başlığı
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Bembeyaz arka planlı, harici dosya istemeyen profesyonel Plotly haritası
fig = px.scatter_geo(
    df_filtered,
    lat="enlem",
    lon="boylam",
    color="sehir",
    hover_name="bayi_adi",
    hover_data=["yetkili", "telefon", "adres", "detay"],
    projection="mercator",
    height=550
)

fig.update_geos(
    visible=True,
    resolution=50,
    showcountries=True, countrycolor="#444444",
    showsubunits=True, subunitcolor="#dddddd",
    showland=True, landcolor="white",    # Kara parçaları tamamen beyaz
    showocean=True, oceancolor="#f8f9fa",  # Denizler sade açık gri
    lonaxis_range=[25, 45],
    lataxis_range=[35, 43]
)

fig.update_layout(
    template="plotly_white",
    margin={"r":0,"t":0,"l":0,"b":0},
    legend_title_text="Şehirler"
)

st.plotly_chart(fig, use_container_width=True)

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi ({len(df_filtered)} Kayıt)")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
else:
    st.subheader(f"📋 Tüm Türkiye ve Bölge Genelindeki Müşteri dan Bayiler ({len(df)} Kayıt)")

# Tabloyu eksiksiz göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
