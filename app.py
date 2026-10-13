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

# Üst kısımda hızlı filtre butonları (Şehirlere tek tıklamayla anında açma)
st.subheader("📍 Şehir Seçimi ve Bölge Haritası")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())

# Kullanıcının kolayca tıklayabilmesi için yatay seçici
secilen_sehir = st.selectbox("Haritada ve Listede Görüntülenecek Şehri Seçin:", sehirler)

# Filtreleme mantığı
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    zoom_val = 8
else:
    df_filtered = df
    zoom_val = 5

# Harita Verisi Hazırlığı (lat / lon formatı)
map_df = df_filtered.rename(columns={'enlem': 'lat', 'boylam': 'lon'})

# Temiz, hatasız ve hızlı interaktif harita
st.map(
    map_df,
    latitude='lat',
    longitude='lon',
    size=200,
    zoom=zoom_val,
    use_container_width=True
)

# Alt Bölüm: Seçilen Şehre Ait Tüm Müşteriler ve Ziyaret Geçmişi
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehrindeki Tüm Müşteri ve Bayiler ({len(df_filtered)} Kayıt)")
    st.info(f"Seçtiğiniz {secilen_sehir} iline ait tüm bayi yetkilileri, telefon numaraları ve ziyaret notları aşağıda tarihe göre listelenmiştir.")
else:
    st.subheader(f"📋 Tüm Türkiye Genelindeki Müşteri ve Bayiler ({len(df)} Kayıt)")

# Tabloyu eksiksiz göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
