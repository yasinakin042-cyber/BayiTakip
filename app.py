import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Kahveci Otomotiv - Bayi Takip ve Harita Sistemi", layout="wide")

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

# Sol Menü / Filtre
st.sidebar.header("📍 Bölge / Şehir Seçimi")
sehirler = ["Tümü"] + sorted(df['sehir'].dropna().unique().tolist())
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Filtreleme
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    center_lat = df_filtered['enlem'].mean()
    center_lon = df_filtered['boylam'].mean()
    zoom_level = 8
else:
    df_filtered = df
    center_lat = 39.1667
    center_lon = 35.2433
    zoom_level = 6

# Tertemiz Beyaz/Açık Tema Folium Haritası
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Harita nesnesi oluştur (OpenStreetMap altyapısı: Türkçe etiketler, beyaz/açık zemin, KKTC dahil)
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles="OpenStreetMap")

# Müşteri/Bayi noktalarını haritaya ekle
for _, row in df_filtered.iterrows():
    if pd.notna(row['enlem']) and pd.notna(row['boylam']):
        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; width: 220px;">
            <b>Şehir:</b> {row['sehir']}<br>
            <b>Firma:</b> {row['bayi_adi']}<br>
            <b>Yetkili:</b> {row['yetkili']}<br>
            <b>Telefon:</b> {row['telefon']}<br>
            <b>Adres:</b> {row['adres']}<br>
            <b>Not:</b> {row['detay']}
        </div>
        """
        folium.Marker(
            location=[row['enlem'], row['boylam']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['bayi_adi']} ({row['sehir']})",
            icon=folium.Icon(color="red" if row['sehir'] == 'Konya' else ("blue" if row['sehir'] == 'İstanbul' else "orange"), icon="info-sign")
        ).add_to(m)

# Haritayı Streamlit üzerinde göster
st_folium(m, width=1200, height=550)

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi ({len(df_filtered)} Kayıt)")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
else:
    st.subheader(f"📋 Tüm Türkiye ve Bölge Genelindeki Müşteri ve Bayiler ({len(df)} Kayıt)")

# Tabloyu göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
