import streamlit as st
import pandas as pd

st.title("EUDR Risk Assessment")

st.markdown("Upload a CSV file with supplier data")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# Risk reference table
# ----------------------------
risk_table = pd.DataFrame({
    "country": ["Brazil","Brazil","France","Colombia","Costa Rica","Mexico",
                "Spain","Argentina","Argentina","Brazil","Indonesia","Indonesia"],
    "crop": ["Coffee","Soybean","Cattle","Coffee","Coffee","Coffee",
             "Olives","Soybean","Cattle","Cattle","Oil Palm","Rubber"],
    "risk_level": ["High","High","Low","Medium","Low","Medium",
                   "Low","High","High","High","High","High"],
    "risk_score": [3,3,1,2,1,2,1,3,3,3,3,3],
    "deforestation": [1,1,0,1,0,1,0,1,1,1,1,1],
    "coordinates": [0,0,1,0,1,0,1,0,0,0,0,0]
})

# ----------------------------
# Risk function
# ----------------------------
def calculate_risk(row):
    score = row.get("risk_score", 0)
    explanation = [f"Base risk: {row.get('risk_level', 'unknown')}"]

    if row.get("has_coordinates", 1) == 0:
        score += 2
        explanation.append("Missing supplier coordinates")

    if row.get("deforestation", 0) == 1:
        score += 2
        explanation.append("Deforestation risk area")

    if score <= 2:
        level = "Low"
    elif score <= 5:
        level = "Medium"
    else:
        level = "High"

    return pd.Series([score, level, ", ".join(explanation)])

# ----------------------------
# App logic
# ----------------------------
if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # ----------------------------
    # CLEAN COLUMN NAMES (CRITICAL FIX)
    # ----------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    risk_table.columns = risk_table.columns.str.lower()

    # ----------------------------
    # OPTIONAL COLUMN FLEXIBILITY
    # ----------------------------
    rename_map = {
        "countries": "country",
        "country_name": "country",
        "crop type": "crop",
        "product": "crop"
    }

    df = df.rename(columns=rename_map)

    # ----------------------------
    # VALIDATION
    # ----------------------------
    required_cols = {"country", "crop"}
    missing = required_cols - set(df.columns)

    if missing:
        st.error(f"Missing required columns: {missing}")
        st.write("Your file columns:", df.columns.tolist())
        st.stop()

    # ----------------------------
    # MERGE RISK DATA
    # ----------------------------
    df = df.merge(risk_table, on=["country", "crop"], how="left")

    # Fill missing values safely
    df["risk_score"] = df["risk_score"].fillna(0)
    df["risk_level"] = df["risk_level"].fillna("Unknown")
    df["deforestation"] = df["deforestation"].fillna(0)

    # ----------------------------
    # OPTIONAL INPUT COLUMN
    # ----------------------------
    if "has_coordinates" not in df.columns:
        df["has_coordinates"] = 1

    # ----------------------------
    # CALCULATE FINAL RISK
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
