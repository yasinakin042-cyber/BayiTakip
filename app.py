import streamlit as st
import pandas as pd

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

# Sol Menü (Filtreleme)
st.sidebar.header("📍 Bölge / Şehir Seçimi")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Filtreleme mantığı
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
else:
    df_filtered = df

# Üst Kısım: Streamlit Yerleşik İnteraktif Haritası (Beyaz/Açık Tema Uyumlu)
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Harita için gerekli sütun isimleri kontrolü (lat/lon)
map_df = df_filtered.rename(columns={'enlem': 'lat', 'boylam': 'lon'})

# Haritayı göster (Kullanıcı dostu, hızlı ve hatasız yerleşik harita)
st.map(map_df, latitude='lat', longitude='lon', zoom=6 if secilen_sehir != "Tümü" else 5, use_container_width=True)

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
else:
    st.subheader("📋 Tüm Müşteri ve Bayi Ziyaretleri Listesi")

# Tabloyu göster (Tüm detaylar ve telefonlar dahil)
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
