import os
import openai
import pandas as pd
openai.api_key = os.getenv("OPENAI_API_KEY")

def parse_range(r):
    if pd.isna(r):
        return (None, None)
    r = str(r).strip()
    if "-" in r:
        low, high = r.split("-")
        return (float(low.replace(",", ".")), float(high.replace(",", ".")))
    try:
        val = float(r.replace(",", "."))
        return (0.0, val)
    except:
        return (None, None)
    
def get_ai_comment(input_values, df_limits):
    messages = [
        {"role": "system", "content": "Sen uzman bir çevre mühendisisin. Girdiğin verilere göre suyun kalitesi hakkında teknik ve anlaşılır bir yorum yap."},
        {"role": "user", "content": f"Kullanıcı tarafından girilen su değerleri şunlardır: {input_values}. Standart limitler şunlardır: {df_limits.to_dict(orient='records')}"}
    ]

    client = openai(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content