import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Sayfa Ayarları
st.set_page_title(page_title="Bayi Takip Sistemi", layout="wide")

# Şifre Kontrolü için Oturum Durumu
if "giris_yapildi" not in st.session_state:
    st.session_state.giris_yapildi = False

# Giriş Ekranı
def login_ekrani():
    st.subheader("Giriş Yapmanız Gerekiyor")
    kullanici_adi = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    
    if st.button("Giriş Yap"):
        if (kullanici_adi == "yonetici" and sifre == "admin123") or (kullanici_adi == "ekip" and sifre == "ekip2026"):
            st.session_state.giris_yapildi = True
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı!")

# Ana Uygulama
def ana_uygulama():
    st.title("Bayi ve Müşteri Takip Haritası")
    st.sidebar.success("Sisteme başarılı giriş yapıldı.")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.giris_yapildi = False
        st.rerun()

    # CSV Dosyasını Yükleme
    try:
        df = pd.read_csv("musteriler.csv")
    except FileNotFoundError:
        st.error("musteriler.csv dosyası bulunamadı! Lütfen dosyayı kontrol edin.")
        return

    # Durum/Kategori Filtresi
    durumlar = ["Tümü"] + list(df["durum"].unique())
    secilen_durum = st.sidebar.selectbox("Kategori/Durum Filtresi", durumlar)

    if secilen_durum != "Tümü":
        filtrelenmis_df = df[df["durum"] == secilen_durum]
    else:
        filtrelenmis_df = df

    # Harita Oluşturma (Türkiye Odaklı)
    m = folium.Map(location=[39.0, 35.0], zoom_start=6)

    # Noktaları Haritaya Ekleme (CSV'deki renge göre)
    for _, row in filtrelenmis_df.iterrows():
        # CSV dosyasındaki renk bilgisini alıyoruz (yoksa varsayılan blue yapılır)
        bayi_rengi = str(row.get('renk', 'blue')).strip().lower()

        popup_text = f"<b>{row['bayi_adi']}</b><br>Yetkili: {row['yetkili']}<br>Tel: {row['telefon']}<br><b>Durum: {row['durum']}</b>"
        
        folium.Marker(
            location=[row['enlem'], row['boylam']],
            popup=popup_text,
            tooltip=row['bayi_adi'],
            icon=folium.Icon(color=bayi_rengi, icon='info-sign', prefix='glyphicon')
        ).add_to(m)

    # Haritayı Ekranda Gösterme
    st_folium(m, width=1000, height=500)

    # Tablo Gösterimi
    st.subheader("Bayi Listesi Detayları")
    st.dataframe(filtrelenmis_df)

# Kontrol Akışı
if not st.session_state.giris_yapildi:
    login_ekrani()
else:
    ana_uygulama()