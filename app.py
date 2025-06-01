import streamlit as st
import pandas as pd

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

URL = "https://dobisu.marmara.edu.tr/orta-menu/yararli-bilgiler/icme-suyu-kabul-edilebilir-degerler"

@st.cache_data
def fetch_limits():
    # Sayfadaki tüm tabloları çek
    tables = pd.read_html(URL)
    
    # İlk tabloyu (TSE) dataframe olarak al
    df_tse = tables[0]
    df_ec = tables[1]
    df_who = tables[2]
    
    # Burada sadece ilk tabloyu baz alarak işleyelim
    # Parametre kolonuna göre filtreleme yapacağız
    
    # Parametre listesini ortak alalım (hepsi aynı sırada ve isimde)
    parametreler = df_tse.iloc[:,0].tolist()
    
    # Fonksiyon ile tabloları düzenle
    def clean_table(df):
        df = df.rename(columns={df.columns[0]: "Parametre",
                                df.columns[1]: "Değer"})
        df = df.dropna(subset=["Parametre"])
        drop_keywords = ["Kabul Edilebilir", "STANDARTLAR", "Fiziksel ve Duyusal",
                         "EMS/100", "Organoleptik", "Renk", "Bulanıklık", "Koku", "Tat"]
        mask = ~df["Parametre"].str.contains("|".join(drop_keywords), na=False)
        df = df[mask].reset_index(drop=True)
        return df
    
    df_tse_clean = clean_table(df_tse)
    df_ec_clean = clean_table(df_ec)
    df_who_clean = clean_table(df_who)
    
    # Birleştirirken sadece Parametre ve değer sütunlarını alıyoruz
    df_limits = pd.DataFrame({
        "Parametre": df_tse_clean["Parametre"],
        "TSE": df_tse_clean["Değer"],
        "EC": df_ec_clean["Değer"],
        "WHO": df_who_clean["Değer"],
    })
    return df_limits

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
        val = r.replace(",", ".")
        try:
            return (0.0, float(val))
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

# Kullanıcıdan parametre bazında değer al
input_values = {}
for p in df_limits["Parametre"]:
    v = st.number_input(f"{p} değerini giriniz:", format="%.3f", key=p)
    input_values[p] = v

st.write("---")

tabs = st.tabs(["TSE", "EC", "WHO"])

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


