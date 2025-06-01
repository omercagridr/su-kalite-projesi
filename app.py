import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

# Veri URL'si (CSV dosyası)
URL = "https://dobisu.marmara.edu.tr/orta-menu/yararli-bilgiler/icme-suyu-kabul-edilebilir-degerler"

@st.cache_data
def fetch_limits():
    df = pd.read_csv(URL)
    # Sütun isimlerini düzenle
    df.rename(columns={df.columns[0]: "Parametre",
                       df.columns[1]: "TSE",
                       df.columns[2]: "EC",
                       df.columns[3]: "WHO"}, inplace=True)
    df = df.dropna(subset=["Parametre"]).reset_index(drop=True)

    # İstenmeyen satırların filtrelenmesi
    drop_keywords = ["Kabul Edilebilir", "STANDARTLAR", "Fiziksel ve Duyusal",
                     "EMS/100", "Organoleptik", "Renk", "Bulanıklık", "Koku", "Tat"]
    mask = ~df["Parametre"].str.contains("|".join(drop_keywords), na=False)
    df = df[mask].reset_index(drop=True)
    return df

def parse_range(r):
    if pd.isna(r):
        return (None, None)
    # Aralık örneği: "0,0 - 0,5" veya sadece tek sayı "0,5"
    r = str(r).strip()
    if "-" in r:
        low, high = r.split("-")
        low = low.strip().replace(",", ".")
        high = high.strip().replace(",", ".")
        return (float(low), float(high))
    else:
        val = r.replace(",", ".")
        return (0.0, float(val))

def judge(value, limit_range):
    if value is None or limit_range == (None, None):
        return "Veri Yok"
    low, high = limit_range
    if low is None or high is None:
        return "Veri Yok"
    if low <= value <= high:
        return "Uygun"
    else:
        return "Uygun Değil"

st.title("Su Kalite Testi")

df_limits = fetch_limits()

# Kullanıcıdan değer girişi (parametreler için)
input_values = {}
for p in df_limits["Parametre"]:
    v = st.number_input(f"{p} değerini giriniz:", format="%.3f", key=p)
    input_values[p] = v

st.write("---")

# Tabloları üç sekmede göstermek için
tabs = st.tabs(["TSE", "EC", "WHO"])

# Fonksiyon sonuçları için ortak yapı
def create_results(column_name):
    results = []
    for i, row in df_limits.iterrows():
        param = row["Parametre"]
        user_val = input_values.get(param)
        limit_range = parse_range(row[column_name])
        durum = judge(user_val, limit_range)
        results.append({"Parametre": param, "Değer": user_val, "Durum": durum})
    return results

results_tse = create_results("TSE")
results_ec = create_results("EC")
results_who = create_results("WHO")

with tabs[0]:
    st.subheader("TSE Sonuçları")
    st.table(pd.DataFrame(results_tse))

with tabs[1]:
    st.subheader("EC Sonuçları")
    st.table(pd.DataFrame(results_ec))

with tabs[2]:
    st.subheader("WHO Sonuçları")
    st.table(pd.DataFrame(results_who))


