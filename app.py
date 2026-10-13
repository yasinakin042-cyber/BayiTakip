import streamlit as st
import pandas as pd

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
    zoom_level = 7
else:
    df_filtered = df
    zoom_level = 5

# Harita Görünümü Başlığı
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Streamlit yerleşik hızlı ve asla hata vermeyen harita altyapısı (lat/lon uyumlu)
map_df = df_filtered.rename(columns={'enlem': 'lat', 'boylam': 'lon'})

st.map(
    map_df,
    latitude='lat',
    longitude='lon',
    size=300,
    zoom=zoom_level,
    use_container_width=True
)

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
