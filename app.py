import streamlit as st
import pandas as pd

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

CSV_FILE = "su_kalite_standartlari.txt"

@st.cache_data
def fetch_limits():
    df = pd.read_csv(CSV_FILE)
    df.rename(columns={df.columns[0]: "Parametre",
                       df.columns[1]: "TSE",
                       df.columns[2]: "EC",
                       df.columns[3]: "WHO"}, inplace=True)
    df = df.dropna(subset=["Parametre"]).reset_index(drop=True)
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
        if (value - low) < 0.05 * (high - low) or (high - value) < 0.05 * (high - low):
            return "Sınırda"
        return "Uygun"
    return "Uygun Değil"

def style_status(val):
    if "Uygun Değil" in val:
        return "background-color:#ffcccc; color:black;"
    elif "Sınırda" in val:
        return "background-color:#fff3cd; color:black;"
    elif "Uygun" in val:
        return "background-color:#d4edda; color:black;"
    else:
        return ""

st.title("💧 Su Kalite Testi")

df_limits = fetch_limits()

# Giriş alanları: 4 sütun olarak
st.markdown("### 🔢 Değerleri Giriniz")
input_values = {}
cols = st.columns(4)
for i, p in enumerate(df_limits["Parametre"]):
    with cols[i % 4]:
        input_values[p] = st.number_input(f"{p}:", format="%.3f", key=p)

st.markdown("---")

# Hesapla butonu
if st.button("💡 Hesapla"):
    st.markdown("## 📊 Sonuçlar")
    st.markdown("Aşağıdan **TSE**, **EC** ve **WHO** standartlarına göre değerlendirme sonuçlarını görebilirsin.")

    # Büyük ve göze çarpan sekmeler
    tabs = st.tabs([
        "🔬 **TSE 266 Standartları**", 
        "🌍 **EC (Avrupa Komisyonu)**", 
        "🩺 **WHO (Dünya Sağlık Örgütü)**"
    ])

    def create_results(column_name):
        results = []
        for _, row in df_limits.iterrows():
            param = row["Parametre"]
            user_val = input_values.get(param)
            limit_range = parse_range(row[column_name])
            durum = judge(user_val, limit_range)
            results.append({"Parametre": param, "Değer": user_val, "Durum": durum})
        return pd.DataFrame(results)

    with tabs[0]:
        st.markdown("### ✅ TSE Sonuçları")
        df = create_results("TSE")
        st.dataframe(df.style.applymap(style_status, subset=["Durum"]), use_container_width=True)

    with tabs[1]:
        st.markdown("### 🌍 EC Sonuçları")
        df = create_results("EC")
        st.dataframe(df.style.applymap(style_status, subset=["Durum"]), use_container_width=True)

    with tabs[2]:
        st.markdown("### 🩺 WHO Sonuçları")
        df = create_results("WHO")
        st.dataframe(df.style.applymap(style_status, subset=["Durum"]), use_container_width=True)




