import pandas as pd
import streamlit as st

st.set_page_config(page_title="Bayi Takip Sistemi", layout="wide")

# Şifre koruması ve temel uygulama başlığı
st.title("Kahveci Otomotiv - Bayi Takip ve Harita Sistemi")
st.write("Uygulama başarıyla yüklendi ve çalışıyor!")

# CSV dosyasını okuma kontrolü
try:
    df = pd.read_csv("musteriler.csv")
    st.success("Müşteri verileri başarıyla yüklendi!")
    st.dataframe(df)
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
