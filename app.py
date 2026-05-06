import streamlit as st
import pandas as pd

st.title("EUDR Risk Assessment")

st.markdown("Upload a CSV file with supplier data")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# RISK REFERENCE TABLE
# ----------------------------
risk_table = pd.DataFrame({
    "country": ["argentina","argentina","brazil","brazil","brazil","colombia",
                "costa rica","france","indonesia","indonesia","mexico","spain"],
    "crop": ["soybean","cattle","coffee","soybean","cattle","coffee",
             "coffee","cattle","oil palm","rubber","coffee","olives"],
    "risk_level": ["high","high","high","high","high","medium",
                   "low","low","high","high","medium","low"],
    "risk_score": [3,3,3,3,3,2,1,1,3,3,2,1],
    "deforestation": [1,1,1,1,1,1,0,0,1,1,1,0],
    "coordinates": [0,0,0,0,0,0,1,1,0,0,0,1]
})

# ----------------------------
# RISK FUNCTION
# ----------------------------
def calculate_risk(row):
    score = row.get("risk_score", 0)
    explanation = [f"Base risk: {row.get('risk_level', 'unknown')}"]

    if row.get("has_coordinates", 1) == 0:
        score += 2
        explanation.append("Missing coordinates")

    if row.get("deforestation", 0) == 1:
        score += 2
        explanation.append("Deforestation risk")

    if score <= 2:
        level = "Low"
    elif score <= 5:
        level = "Medium"
    else:
        level = "High"

    return pd.Series([score, level, ", ".join(explanation)])

# ----------------------------
# APP LOGIC
# ----------------------------
if uploaded_file:

    # Read CSV safely
    df = pd.read_csv(uploaded_file, sep=None, engine="python")

    # Clean columns
    df.columns = df.columns.str.strip().str.lower()

    # Remove Excel garbage columns
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]

    st.write("Detected columns:", df.columns.tolist())

    # Validate required columns
    if "country" not in df.columns or "crop" not in df.columns:
        st.error("Missing required columns: country, crop")
        st.stop()

    # Normalize text
    df["country"] = df["country"].astype(str).str.strip().str.lower()
    df["crop"] = df["crop"].astype(str).str.strip().str.lower()

    risk_table["country"] = risk_table["country"].str.strip().str.lower()
    risk_table["crop"] = risk_table["crop"].str.strip().str.lower()

    # ----------------------------
    # MERGE (FIXED: avoid column conflicts)
    # ----------------------------
    df = df.merge(
        risk_table,
        on=["country", "crop"],
        how="left",
        suffixes=("", "_ref")
    )

    # If duplicates exist, prefer risk_table values
    for col in ["risk_score", "risk_level", "deforestation", "coordinates"]:
        ref_col = f"{col}_ref"
        if ref_col in df.columns:
            df[col] = df[ref_col]
            df.drop(columns=[ref_col], inplace=True)

    # Fill missing values safely
    df["risk_score"] = df["risk_score"].fillna(0)
    df["risk_level"] = df["risk_level"].fillna("unknown")
    df["deforestation"] = df["deforestation"].fillna(0)
    df["coordinates"] = df["coordinates"].fillna(0)

    # Ensure optional column exists
    if "has_coordinates" not in df.columns:
        df["has_coordinates"] = 1

    # ----------------------------
    # CALCULATE RISK
    # ----------------------------
    df[["final_score", "final_risk", "explanation"]] = df.apply(
        calculate_risk,
        axis=1
    )

    # ----------------------------
    # OUTPUT
    # ----------------------------
    st.write("### Results")
    st.dataframe(df)
    st.write("### Results")
    st.dataframe(df)
