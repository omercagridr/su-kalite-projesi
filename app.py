import streamlit as st
import pandas as pd
import requests

URL = "https://raw.githubusercontent.com/omer12306/water-quality-standards/main/water-quality.csv"

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

st.title("Su Kalite Testi")

@st.cache_data
def fetch_limits():
    tables = pd.read_html(URL, header=0)
    df = tables[0]
    df.rename(columns={df.columns[0]: "Parametre",
                       df.columns[1]: "TSE",
                       df.columns[2]: "EC",
                       df.columns[3]: "WHO"}, inplace=True)
    df = df.dropna(subset=["Parametre"]).reset_index(drop=True)
    
    # Gereksiz başlık/metin satırlarını çıkaralım
    drop_keywords = ["Kabul Edilebilir", "STANDARTLAR", "Fiziksel ve Duyusal",
                     "EMS/100", "Organoleptik", "Renk", "Bulanıklık", "Koku", "Tat"]
    mask = ~df["Parametre"].str.contains("|".join(drop_keywords), na=False)
    df = df[mask].reset_index(drop=True)
    return df

def parse_range(r):
    if pd.isna(r):
        return (None, None)
    r = str(r).strip()
    if "-" in r:
        low, high = r.split("-", 1)
        low = low.strip().replace(",", ".")
        high = high.strip().replace(",", ".")
        try:
            return (float(low), float(high))
        except:
            return (None, None)
    else:
        try:
            return (0.0, float(r.replace(",", ".")))
        except:
            return (None, None)

def judge(value, limits):
    low, high = limits
    if value is None or low is None or high is None:
        return "Veri Yok"
    if low <= value <= high:
        return "Uygun ✅"
    else:
        return "Uygun Değil ❌"

df_limits = fetch_limits()

st.sidebar.header("Parametre Değerlerini Girin")
input_values = {}
for param in df_limits["Parametre"]:
    val = st.sidebar.text_input(f"{param} değeri", "")
    if val.strip() == "":
        input_values[param] = None
    else:
        try:
            input_values[param] = float(val.replace(",", "."))
        except:
            input_values[param] = None

# Sonuçları tablo halinde göstermek için:
tabs = st.tabs(["TSE", "EC", "WHO"])

for i, std in enumerate(["TSE", "EC", "WHO"]):
    with tabs[i]:
        results = []
        for idx, row in df_limits.iterrows():
            p = row["Parametre"]
            v = input_values.get(p, None)
            limits = parse_range(row[std])
            status = judge(v, limits)
            results.append({"Parametre": p, "Değer": v if v is not None else "-", "Durum": status})
        st.table(pd.DataFrame(results))


