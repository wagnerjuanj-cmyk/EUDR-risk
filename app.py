import streamlit as st
import pandas as pd
import openai
import os

# ----------------------------
# CONFIGURACIÓN OPENAI
# ----------------------------
# Guarda tu API Key como variable de entorno en Streamlit Cloud
# Ej: OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# ----------------------------
# APP TITLE
# ----------------------------
st.title("EUDR Risk Assessment with AI")
st.markdown("Upload a CSV of suppliers with country and crop.")

# ----------------------------
# FILE UPLOADER
# ----------------------------
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# ----------------------------
# FUNCIONES DE IA
# ----------------------------

def ai_normalize_name(name, entity_type="country"):
    """
    Usa GPT para corregir nombres de países o cultivos.
    """
    prompt = f"Correct the {entity_type} name: '{name}' to a standard form. Respond with only the corrected name."
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=10
        )
        corrected = response.choices[0].text.strip()
        return corrected
    except Exception as e:
        st.warning(f"AI normalization failed for {name}: {e}")
        return name

# ----------------------------
# FUNCION CALCULO DE RIESGO
# ----------------------------
def calculate_risk(row):
    """
    Calcula un score base de riesgo según país y crop.
    """
    high_risk_countries = ["brazil", "indonesia", "argentina", "colombia"]
    high_risk_crops = ["soybean", "cattle", "coffee", "oil palm"]

    score = 1
    explanation = []

    if row["country"].lower() in high_risk_countries:
        score += 2
        explanation.append("Country high risk")

    if row["crop"].lower() in high_risk_crops:
        score += 1
        explanation.append("Crop high risk")

    if row.get("deforestation", 0) == 1:
        score += 2
        explanation.append("Deforestation history")

    if score <= 2:
        level = "Low"
    elif score <= 4:
        level = "Medium"
    else:
        level = "High"

    explanation_text = ", ".join(explanation) if explanation else "No additional risk"
    return pd.Series([score, level, explanation_text])

# ----------------------------
# MAIN LOGIC
# ----------------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Detect required columns
    required_cols = ["country", "crop"]
    if not all(col in df.columns.str.lower() for col in required_cols):
        st.error(f"CSV must contain columns: {required_cols}")
        st.stop()

    df.columns = df.columns.str.lower()

    # Normalizar con IA
    with st.spinner("Normalizing names with AI..."):
        df["country"] = df["country"].apply(lambda x: ai_normalize_name(x, "country"))
        df["crop"] = df["crop"].apply(lambda x: ai_normalize_name(x, "crop"))

    # Calcular riesgo
    df[["risk_score", "risk_level", "explanation"]] = df.apply(calculate_risk, axis=1)

    # Mostrar resultados
    st.write("### Results")
    st.dataframe(df)
    st.write("### Results")
    st.dataframe(df)
