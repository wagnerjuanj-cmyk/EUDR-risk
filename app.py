import streamlit as st
import pandas as pd

st.title("EUDR Risk Assessment")

st.markdown("Upload a CSV file with supplier data")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# RISK TABLE (REFERENCE DATA)
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
# RISK CALCULATION
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
# MAIN APP
# ----------------------------
if uploaded_file:

    # READ CSV (ROBUST)
    df = pd.read_csv(uploaded_file, sep=None, engine="python")

    # CLEAN COLUMN NAMES
    df.columns = df.columns.str.strip().str.lower()

    # REMOVE EXCEL GARBAGE COLUMNS
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]

    st.write("Detected columns:", df.columns.tolist())

    # ----------------------------
    # VALIDATION
    # ----------------------------
    if "country" not in df.columns or "crop" not in df.columns:
        st.error("Missing required columns: country, crop")
        st.stop()

    # ----------------------------
    # NORMALIZATION (CRITICAL FIX)
    # ----------------------------
    df["country"] = df["country"].astype(str).str.strip().str.lower()
    df["crop"] = df["crop"].astype(str).str.strip().str.lower()

    risk_table["country"] = risk_table["country"].str.strip().str.lower()
    risk_table["crop"] = risk_table["crop"].str.strip().str.lower()

    # ----------------------------
    # MERGE (SAFE)
    # ----------------------------
    df = df.merge(
        risk_table,
        on=["country", "crop"],
        how="left",
        suffixes=("", "_ref")
    )

    # FIX duplicated columns from merge
    for col in ["risk_score", "risk_level", "deforestation", "coordinates"]:
        ref_col = f"{col}_ref"
        if ref_col in df.columns:
            df[col] = df[ref_col]
            df.drop(columns=[ref_col], inplace=True)

    # ----------------------------
    # HANDLE MISSING VALUES
    # ----------------------------
    df["risk_score"] = df["risk_score"].fillna(0)
    df["risk_level"] = df["risk_level"].fillna("unknown")
    df["deforestation"] = df["deforestation"].fillna(0)
    df["coordinates"] = df["coordinates"].fillna(0)

    if "has_coordinates" not in df.columns:
        df["has_coordinates"] = 1

    # ----------------------------
    # DEBUG (IMPORTANT)
    # ----------------------------
    st.write("### Debug - After merge")
    st.dataframe(df)

    st.write("### Missing values check")
    st.write(df.isna().sum())

    # ----------------------------
    # RISK CALCULATION
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
