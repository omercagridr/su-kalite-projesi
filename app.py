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

# Debug için çekilen limitlerin durumunu göster
st.write("Limits DF ilk 5 satır")
st.dataframe(limits_df.head())

st.write("TSE sütunundaki veriler:")
st.write(limits_df["TSE"].tolist())

st.write("EC sütunundaki veriler:")
st.write(limits_df["EC"].tolist())

st.write("WHO sütunundaki veriler:")
st.write(limits_df["WHO"].tolist())

st.title("💧 İçme Suyu Kalite Testi")
st.write("🛠️ Değeri olmayan kutuyu boş bırak, sadece sayısal değer gir.")

user_vals = {}
cols = st.columns(4)
for i, row in limits_df.iterrows():
    param = row["Parametre"]
    with cols[i % 4]:
        user_vals[param] = st.number_input(param, key=param, format="%.4f",
                                           help=f"Limitle: TSE={row['TSE']}  EC={row['EC']}  WHO={row['WHO']}")

def parse_range(r):
    if pd.isna(r):
        return (None, None)
    s = str(r).strip().replace(",", ".")
    if s in ["-", "ND", "N/A", "—", ""]:
        return (None, None)
    try:
        if "-" in s:
            parts = s.split("-")
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low, high)
        else:
            high = float(s)
            return (0.0, high)
    except Exception as e:
        st.write(f"Hata parse_range'de: {e} -- girdi: {r}")
        return (None, None)

def judge(v, rng):
    low, high = rng
    if v is None or (v == 0 and v != 0):  # Bu satır biraz garip ama senin koddan aynen aldım
        return ""
    if low is None or high is None:
        return "⚠️ Limit yok"
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
        tse_rng = parse_range(row["TSE"])
        ec_rng = parse_range(row["EC"])
        who_rng = parse_range(row["WHO"])

        if tse_rng == (None, None):
            st.write(f"TSE limiti yok veya okunamadı: {p} -> {row['TSE']}")
        if ec_rng == (None, None):
            st.write(f"EC limiti yok veya okunamadı: {p} -> {row['EC']}")

        tse_res = judge(v, tse_rng)
        ec_res = judge(v, ec_rng)
        who_res = judge(v, who_rng)

        results_tse.append({"Parametre": p, "Değer": v, "Durum": tse_res})
        results_ec.append({"Parametre": p, "Değer": v, "Durum": ec_res})
        results_who.append({"Parametre": p, "Değer": v, "Durum": who_res})

    st.subheader("TSE Sonuçları")
    st.dataframe(pd.DataFrame(results_tse))

    st.subheader("EC Sonuçları")
    st.dataframe(pd.DataFrame(results_ec))

    st.subheader("WHO Sonuçları")
    st.dataframe(pd.DataFrame(results_who))
