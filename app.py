import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
from PIL import Image
import base64

st.set_page_config(page_title="Su Kalite Testi", layout="wide")

CSV_FILE = "su_kalite_standartlari.txt"
LOGO_PATH = "mar_logo.png"  # Bu logo dosyasını uygulama klasörüne koy

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
        diff = high - low
        if (value - low) < 0.05 * diff or (high - value) < 0.05 * diff:
            return "Sınırda"
        return "Uygun"
    else:
        return "Uygun Değil"

df_limits = fetch_limits()

st.title("💧 Su Kalite Testi")
st.markdown("🛠️ **Lütfen sadece sayısal değerleri girin. Bilinmeyenleri boş bırakabilirsiniz.**")

# Giriş alanları 4 sütun halinde
input_values = {}
cols = st.columns(4)
for i, param in enumerate(df_limits["Parametre"]):
    with cols[i % 4]:
        v = st.number_input(f"{param}", format="%.3f", key=param)
        input_values[param] = v

st.write("---")

if st.button("💡 Hesapla"):
    tabs = st.tabs(["TSE", "EC", "WHO"])

    def create_results(column_name):
        results = []
        for _, row in df_limits.iterrows():
            param = row["Parametre"]
            user_val = input_values.get(param)
            limit_range = parse_range(row[column_name])
            durum = judge(user_val, limit_range)
            results.append({"Parametre": param, "Değer": user_val, "Durum": durum})
        return pd.DataFrame(results)

    def color_row(val):
        if val == "Uygun":
            return "background-color: #d4edda"  # Yeşil
        elif val == "Sınırda":
            return "background-color: #fff3cd"  # Sarı
        elif val == "Uygun Değil":
            return "background-color: #f8d7da"  # Kırmızı
        else:
            return ""

    df_tse = create_results("TSE")
    df_ec = create_results("EC")
    df_who = create_results("WHO")

    with tabs[0]:
        st.subheader("📋 TSE 266 Sonuçları")
        st.dataframe(df_tse.style.applymap(color_row, subset=["Durum"]))

    with tabs[1]:
        st.subheader("📋 EC (Avrupa Komisyonu) Sonuçları")
        st.dataframe(df_ec.style.applymap(color_row, subset=["Durum"]))

    with tabs[2]:
        st.subheader("📋 WHO (Dünya Sağlık Örgütü) Sonuçları")
        st.dataframe(df_who.style.applymap(color_row, subset=["Durum"]))

    # PDF oluşturucu
    def create_pdf(df1, df2, df3):
        buf = BytesIO()
        with PdfPages(buf) as pdf:
            fig, ax = plt.subplots(figsize=(8.3, 11.7))  # A4 boyut
            ax.axis("off")

            y_pos = 1.0

            # Logo ekle
            try:
                logo = Image.open(LOGO_PATH)
                fig.figimage(logo, 50, 750, zorder=1, alpha=0.7)
            except:
                pass  # Logo yoksa geç

            ax.text(0.5, y_pos, "Su Kalitesi Test Raporu", ha='center', fontsize=18, weight='bold')
            y_pos -= 0.05

            def draw_table(ax, df, title, ypos):
                ax.text(0.5, ypos, title, ha='center', fontsize=14, weight='bold')
                ypos -= 0.03
                table = ax.table(cellText=df.values,
                                 colLabels=df.columns,
                                 loc='center',
                                 cellLoc='center')
                table.scale(1, 1.2)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                return ypos - 0.3

            y_pos = draw_table(ax, df1, "TSE 266 Sonuçları", y_pos - 0.05)
            y_pos = draw_table(ax, df2, "EC (Avrupa Komisyonu) Sonuçları", y_pos - 0.05)
            draw_table(ax, df3, "WHO (Dünya Sağlık Örgütü) Sonuçları", y_pos - 0.05)

            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

        buf.seek(0)
        return buf

    pdf_buffer = create_pdf(df_tse, df_ec, df_who)

    st.download_button(
        label="📥 Tüm Sonuçları PDF Olarak İndir",
        data=pdf_buffer,
        file_name="su_kalite_sonuclari.pdf",
        mime="application/pdf"
    )





