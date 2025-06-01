import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

URL = "https://dobisu.marmara.edu.tr/orta-menu/yararli-bilgiler/icme-suyu-kabul-edilebilir-degerler"

@st.cache_data
def fetch_limits():
    tables = pd.read_html(URL, header=0)
    df = tables[0]  
    df.rename(columns={df.columns[0]: "Parametre",
                       df.columns[1]: "TSE",
                       df.columns[2]: "EC",
                       df.columns[3]: "WHO"}, inplace=True)
    df = df.dropna(subset=["Parametre"]).reset_index(drop=True)
    return df

limits_df = fetch_limits()

st.title("💧 İçme Suyu Kalite Testi")

st.write("🛠️ Değeri olmayan kutuyu boş bırak, sadece sayısal değer gir.")

user_vals = {}
cols = st.columns(4)
for i, row in limits_df.iterrows():
    param = row["Parametre"]
    with cols[i % 4]:
        user_vals[param] = st.number_input(param, key=param, format="%.4f",
                                           help=f"Limitler: TSE={row['TSE']}  EC={row['EC']}  WHO={row['WHO']}")
def parse_range(r):
    if pd.isna(r):
        return (None, None)
    try:
        s = str(r).replace(",", ".").strip()
        if "-" in s:
            low_str, high_str = s.split("-")
            low = float(low_str)
            high = float(high_str)
            return (low, high)
        else:
            # Tek değer varsa, düşük sınırı 0 kabul edelim
            high = float(s)
            return (0.0, high)
    except Exception:
        return (None, None)

def judge(v, rng):
    low, high = rng
    if v is None or low is None or high is None:
        return ""
    if low <= v <= high:
        if (v - low) < 0.05 * (high - low) or (high - v) < 0.05 * (high - low):
            return "⚠️ Sınırda"
        return "✅ Uygun"
    return "❌ Uygun Değil"

if st.button("💡 Hesapla"):
    results_tse = []
    results_ec = []
    results_who = []
    for _, row in limits_df.iterrows():
        p = row["Parametre"]
        v = user_vals[p]
        results_tse.append({"Parametre": p, "Değer": v, "Durum": judge(v, parse_range(row["TSE"]))})
        results_ec.append({"Parametre": p, "Değer": v, "Durum": judge(v, parse_range(row["EC"]))})
        results_who.append({"Parametre": p, "Değer": v, "Durum": judge(v, parse_range(row["WHO"]))})

    df_tse = pd.DataFrame(results_tse)
    df_ec = pd.DataFrame(results_ec)
    df_who = pd.DataFrame(results_who)

    st.subheader("TSE 266 Sonuçları")
    st.dataframe(df_tse.style.applymap(
        lambda x: "background-color:#ffcccc" if "❌" in str(x)
        else ("background-color:#fff3cd" if "⚠️" in str(x)
              else ("background-color:#d4edda" if "✅" in str(x) else ""))
        , subset=["Durum"]))

    st.subheader("EC Sonuçları")
    st.dataframe(df_ec.style.applymap(
        lambda x: "background-color:#ffcccc" if "❌" in str(x)
        else ("background-color:#fff3cd" if "⚠️" in str(x)
              else ("background-color:#d4edda" if "✅" in str(x) else ""))
        , subset=["Durum"]))

    st.subheader("WHO Sonuçları")
    st.dataframe(df_who.style.applymap(
        lambda x: "background-color:#ffcccc" if "❌" in str(x)
        else ("background-color:#fff3cd" if "⚠️" in str(x)
              else ("background-color:#d4edda" if "✅" in str(x) else ""))
        , subset=["Durum"]))

    st.success("Rapor hazır! Yukarıdaki tabloları CSV olarak indirebilirsin (⋮ menüsü).")





