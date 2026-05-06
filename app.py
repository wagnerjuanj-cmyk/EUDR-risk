# app.py
import streamlit as st
import pandas as pd

# ----------------------------
# APP TITLE
# ----------------------------
st.title("EUDR Risk Assessment")
st.markdown("Upload a CSV file with supplier data")

# ----------------------------
# FILE UPLOADER
# ----------------------------
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# RISK TABLE (REFERENCE DATA)
# ----------------------------
risk_table = pd.DataFrame({
    "country": ["argentina","brazil","colombia","costa rica","france","indonesia","mexico","spain"],
    "crop": ["soybean","coffee","coffee","coffee","cattle","oil palm","coffee","olives"],
    "risk_score": [3,3,2,1,1,3,2,1],
    "risk_level": ["high","high","medium","low","low","high","medium","low"],
    "deforestation": [1,1,1,0,0,1,1,0]
})

# ----------------------------
# NORMALIZATION FUNCTIONS
# ----------------------------
def normalize_country(x):
    x = str(x).strip().lower()
    mapping = {
        "brasil": "brazil",
        "brazil": "brazil",
        "arg": "argentina",
        "argentina": "argentina",
        "colombia": "colombia",
        "costa rica": "costa rica",
        "france": "france",
        "francia": "france",
        "indonesia": "indonesia",
        "mexico": "mexico",
        "méxico": "mexico",
        "spain": "spain",
        "españa": "spain"
    }
    return mapping.get(x, x)

def normalize_crop(x):
    x = str(x).strip().lower()
    mapping = {
        "coffee beans": "coffee",
        "coffee": "coffee",
        "soy beans": "soybean",
        "soybean": "soybean",
        "cattle": "cattle",
        "beef": "cattle",
        "oil palm": "oil palm",
        "palm oil": "oil palm",
        "olives": "olives"
    }
    return mapping.get(x, x)

# ----------------------------
# RISK CALCULATION FUNCTION
# ----------------------------
def calculate_risk(row):
    score = row.get("risk_score", 1)
    explanation = [f"Base risk: {row.get('risk_level', 'unknown')}"]

    if row.get("deforestation", 0) == 1:
        score += 2
        explanation.append("Deforestation risk")

    if score <= 2:
        level = "low"
    elif score <= 4:
        level = "medium"
    else:
        level = "high"

    return pd.Series([score, level, ", ".join(explanation)])

# ----------------------------
# MAIN LOGIC
# ----------------------------
if uploaded_file:
    # Read CSV safely
    df = pd.read_csv(uploaded_file, sep=None, engine="python")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Remove Excel garbage columns
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]

    st.write("Detected columns:", df.columns.tolist())

    # Validate required columns
    if "country" not in df.columns or "crop" not in df.columns:
        st.error("CSV must contain columns: country, crop")
        st.stop()

    # Normalize input data
    df["country"] = df["country"].apply(normalize_country)
    df["crop"] = df["crop"].apply(normalize_crop)

    # Normalize risk table
    risk_table["country"] = risk_table["country"].str.strip().str.lower()
    risk_table["crop"] = risk_table["crop"].str.strip().str.lower()

    # Merge with risk table
    df = df.merge(risk_table, on=["country","crop"], how="left")

    # Fill missing risk values
    df["risk_score"] = df["risk_score"].fillna(2)
    df["risk_level"] = df["risk_level"].fillna("medium")
    df["deforestation"] = df["deforestation"].fillna(0)

    # Calculate final risk
    df[["final_score","final_risk","explanation"]] = df.apply(
        calculate_risk,
        axis=1
    )

    # Output
    st.write("### Results")
    st.dataframe(df)
