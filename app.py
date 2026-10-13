import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Kahveci Otomotiv - İl Sınırları Boyalı Takip Sistemi", layout="wide")

st.title("Kahveci Otomotiv - İl Sınırları Boyalı Bölge Takip Haritası")

# Veriyi oku
@st.cache_data
def load_data():
    df = pd.read_csv("musteriler.csv")
    return df

try:
    df = load_data()
    st.success("Müşteri verileri başarıyla yüklendi!")
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

# Gitmediğin şehirleri filtreleyip çıkarıyoruz
haric_tutulacak_sehirler = ['Şanlıurfa', 'Trabzon', 'Antalya', 'Denizli', 'Urfa']
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

# Ziyaret edilen şehirleri ve durumlarını hazırla
ziyaret_edilenler = df['sehir'].dropna().unique().tolist()

# Harita için il bazlı durum tablosu oluşturalım
map_data = []
if geojson_data:
    for feature in geojson_data['features']:
        il_adi = feature['properties'].get('name') or feature['properties'].get('il')
        if il_adi in ziyaret_edilenler:
            durum = "Ziyaret Edildi (Renkli)"
        else:
            durum = "Gitmedi (Beyaz)"
        map_data.append({'sehir': il_adi, 'durum': durum})

df_map = pd.DataFrame(map_data)

# Sol Menü / Filtre
st.sidebar.header("📍 Bölge / Şehir Seçimi")
sehirler = ["Tümü"] + sorted(ziyaret_edilenler)
secilen_sehir = st.sidebar.selectbox("Görüntülenecek Şehri Seçin", sehirler)

# Harita Görünümü Başlığı
st.subheader(f"Harita Görünümü — {secilen_sehir}")

if geojson_data:
    # Plotly Choropleth ile il sınırlarını tam boyama
    fig = px.choropleth(
        df_map,
        geojson=geojson_data,
        locations='sehir',
        featureidkey="properties.name",
        color='durum',
        color_discrete_map={
            'Ziyaret Edildi (Renkli)': '#ff8c00', # Gidilen yerler turuncu
            'Gitmedi (Beyaz)': '#ffffff'         # Gitmediğin yerler tamamen beyaz
        },
        scope="europe",
        height=600
    )

    # Harita görünümünü Türkiye'ye sabitle ve arka planı beyaz yap
    fig.update_geos(
        visible=True,
        resolution=50,
        showcountries=True, countrycolor="#bbbbbb",
        showsubunits=True, subunitcolor="#cccccc",
        showland=True, landcolor="white",
        center={"lat": 39.1667, "lon": 35.2433},
        lonaxis_range=[26, 45],
        lataxis_range=[35, 42]
    )

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        legend_title_text="Durum",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("İl sınırları harita verisi yüklenemedi.")

# Alt Kısım: Seçilen Şehre Ait Ziyaret Geçmişi ve Detaylar
st.markdown("---")
if secilen_sehir != "Tümü":
    df_filtered = df[df['sehir'] == secilen_sehir]
    st.subheader(f"📋 {secilen_sehir} Şehri Ziyaret ve Müşteri Geçmişi ({len(df_filtered)} Kayıt)")
    st.info("Bu şehirde gerçekleştirilen tüm bayi ziyaretleri ve görüşme notları aşağıda listelenmiştir.")
else:
    df_filtered = df
    st.subheader(f"📋 Tüm Türkiye ve Bölge Genelindeki Müşteri ve Bayiler ({len(df)} Kayıt)")

# Tabloyu göster
st.dataframe(
    df_filtered[['sehir', 'bayi_adi', 'yetkili', 'telefon', 'adres', 'detay']],
    use_container_width=True,
    hide_index=True
)
