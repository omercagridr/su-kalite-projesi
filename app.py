import streamlit as st
import pandas as pd

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

# CSV dosya yolu (aynı klasörde su_kalite_standartlari.csv olmalı)
CSV_FILE = "su_kalite_standartlari.txt"

@st.cache_data
def fetch_limits():
    df = pd.read_csv(CSV_FILE)
    # Sütun isimlerini düzenle (CSV zaten uygun ama garanti için)
    df.rename(columns={df.columns[0]: "Parametre",
                       df.columns[1]: "TSE",
                       df.columns[2]: "EC",
                       df.columns[3]: "WHO"}, inplace=True)
    df = df.dropna(subset=["Parametre"]).reset_index(drop=True)

    # İstenmeyen satırları filtreleyelim
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
        low, high = r.split("-")
        low = low.strip().replace(",", ".")
        high = high.strip().replace(",", ".")
        try:
            return (float(low), float(high))
        except:
            return (None, None)
    else:
        try:
            val = float(r.replace(",", "."))
            return (0.0, val)
        except:
            return (None, None)

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

# Kullanıcıdan parametre değerlerini al
input_values = {}
for p in df_limits["Parametre"]:
    v = st.number_input(f"{p} değerini giriniz:", format="%.3f", key=p)
    input_values[p] = v

st.write("---")

tabs = st.tabs(["TSE", "EC", "WHO"])

def create_results(column_name):
    results = []
    for _, row in df_limits.iterrows():
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


