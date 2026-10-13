import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Kahveci Otomotiv - İl Boyalı Bayi Takip Sistemi", layout="wide")

st.title("Kahveci Otomotiv - İl Sınırları Boyalı Bölge Haritası")

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

# --- HARİTADA GÖSTERİLMESİNİ İSTEMEDİĞİN (GİTMEDİĞİN) ŞEHİRLERİ BURAYA EKLE ---
haric_tutulacak_sehirler = ['Şanlıurfa', 'Trabzon', 'Antalya', 'Denizli', 'Urfa']

# Bu şehirleri veriden filtreleyip çıkarıyoruz
df = df[~df['sehir'].isin(haric_tutulacak_sehirler)]

# Türkiye İl Sınırları GeoJSON Verisini Çek
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/geojson/tr-cities.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

geojson_data = load_geojson()

# Ziyaret edilen/veri olan şehirler listesi
ziyaret_edilenler = df['sehir'].dropna().unique().tolist()

# Sol Menü / Filtre
st.sidebar.header("📍 Bölge / Şehir Seçimi")
sehirler = ["Tümü"] + sorted(ziyaret_edilenler)
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Filtreleme
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    center_lat = df_filtered['enlem'].mean()
    center_lon = df_filtered['boylam'].mean()
    zoom_level = 7
else:
    df_filtered = df
    center_lat = 39.1667
    center_lon = 35.2433
    zoom_level = 6

# Harita Görünümü Başlığı
st.subheader(f"Harita Görünümü — {secilen_sehir}")

# Tamamen sade, beyaz zeminli temel harita
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=zoom_level, 
    tiles="cartodbpositron" # Bembeyaz arka plan
)

# İl sınırları poligonlarını boyama mantığı
if geojson_data:
    def style_function(feature):
        il_adi = feature['properties'].get('name') or feature['properties'].get('il')
        
        # Gidilen yerler turuncu/renkli, gidilmeyenler bembeyaz
        if il_adi in ziyaret_edilenler:
            fill_color = '#ff8c00'  # Gidilen şehir rengi
            fill_opacity = 0.6
        else:
            fill_color = '#ffffff'  # Gitmediğin yerler bembeyaz
            fill_opacity = 0.3
            
        return {
            'fillColor': fill_color,
            'color': '#444444',     # İl sınır çizgileri net gri/siyah
            'weight': 1.2,
            'fillOpacity': fill_opacity
        }

    def highlight_function(feature):
        return {
            'fillColor': '#ff4500',
            'color': '#000000',
            'weight': 2,
            'fillOpacity': 0.8
        }

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['İl: '], localize=True)
    ).add_to(m)

# Üzerine müşteri noktalarını ve detay popuplarını ekle
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
            icon=folium.Icon(color="red" if row['sehir'] == 'Konya' else "orange", icon="info-sign")
        ).add_to(m)

# Haritayı ekranda göster
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
