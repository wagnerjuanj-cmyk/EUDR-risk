import streamlit as st
import pandas as pd

st.title("EUDR Risk Assessment")

st.markdown("Upload a CSV file with supplier data")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# Risk reference table
# ----------------------------
risk_table = pd.DataFrame({
    "country": ["brazil","brazil","france","colombia","costa rica","mexico",
                "spain","argentina","argentina","brazil","indonesia","indonesia"],
    "crop": ["coffee","soybean","cattle","coffee","coffee","coffee",
             "olives","soybean","cattle","cattle","oil palm","rubber"],
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

    # Read CSV (MOST IMPORTANT FIX)
    df = pd.read_csv(uploaded_file, sep=None, engine="python")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Show columns for debugging
    st.write("Detected columns:", df.columns.tolist())

    # Validate required columns
    if "country" not in df.columns or "crop" not in df.columns:
        st.error("Your CSV must contain columns: Country and Crop")
        st.stop()

    # Merge risk table
    df = df.merge(risk_table, on=["country", "crop"], how="left")

    # Fill missing values
    df["risk_score"] = df["risk_score"].fillna(0)
    df["risk_level"] = df["risk_level"].fillna("Unknown")
    df["deforestation"] = df["deforestation"].fillna(0)

    # Add default column if missing
    if "has_coordinates" not in df.columns:
        df["has_coordinates"] = 1

    # Calculate risk
    df[["final_score", "final_risk", "explanation"]] = df.apply(
        calculate_risk,
        axis=1
    )

    # Output
    st.write("### Results")
    st.dataframe(df)
