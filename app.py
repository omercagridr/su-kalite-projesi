import streamlit as st
import pandas as pd

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
    r_str = str(r).replace(",", ".").strip()
    if r_str == "" or r_str.lower() == "nan":
        return (None, None)
    if "-" in r_str:
        try:
            low, high = r_str.split("-")
            return (float(low), float(high))
        except:
            return (None, None)
    else:
        try:
            return (0.0, float(r_str))
        except:
            return (None, None)

def judge(v, rng):
    if v is None or rng == (None, None):
        return ""
    low, high = rng
    if low is None or high is None:
        return ""
    if low <= v <= high:
        if (v - low) < 0.05 * (high - low) or (high - v) < 0.05 * (high - low):
            return "⚠️ Sınırda"
        return "✅ Uygun"
    return "❌ Uygun Değil"

if st.button("💡 Hesapla"):
    results = []
    for _, row in limits_df.iterrows():
        p = row["Parametre"]
        v = user_vals[p]
        tse_res = judge(v, parse_range(row["TSE"]))
        ec_res  = judge(v, parse_range(row["EC"]))
        who_res = judge(v, parse_range(row["WHO"]))
        results.append({"Parametre": p,
                        "Değer": v,
                        "TSE 266": tse_res,
                        "EC": ec_res,
                        "WHO": who_res})
    out_df = pd.DataFrame(results)
    st.dataframe(out_df.style.applymap(
        lambda x: "background-color:#ffcccc" if "❌" in str(x)
        else ("background-color:#fff3cd" if "⚠️" in str(x)
              else ("background-color:#d4edda" if "✅" in str(x) else ""))))
    st.success("Rapor hazır! Yukarıdaki tabloyu CSV olarak indirebilirsin (⋮ menüsü).")




