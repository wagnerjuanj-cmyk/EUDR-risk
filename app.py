import streamlit as st
import pandas as pd

st.title("EUDR Risk Assessment")

st.markdown("Upload a CSV file with supplier data")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# Risk reference table
risk_table = pd.DataFrame({
    "Country": ["Brazil","Brazil","France","Colombia","Costa Rica","Mexico",
                "Spain","Argentina","Argentina","Brazil","Indonesia","Indonesia"],
    "Crop": ["Coffee","Soybean","Cattle","Coffee","Coffee","Coffee",
             "Olives","Soybean","Cattle","Cattle","Oil Palm","Rubber"],
    "Risk_Level": ["High","High","Low","Medium","Low","Medium",
                   "Low","High","High","High","High","High"],
    "Risk_Score": [3,3,1,2,1,2,1,3,3,3,3,3],
    "Deforestation": [1,1,0,1,0,1,0,1,1,1,1,1],
    "Coordinates": [0,0,1,0,1,0,1,0,0,0,0,0]
})

def calculate_risk(row):
    score = row['Risk_Score']
    explanation = [f"Base risk: {row['Risk_Level']}"]

    if row.get('has_coordinates', 1) == 0:
        score += 2
        explanation.append("Missing supplier coordinates")

    if row['Deforestation'] == 1:
        score += 2
        explanation.append("Deforestation risk")

    if score <= 2:
        level = "Low"
    elif score <= 5:
        level = "Medium"
    else:
        level = "High"

    return pd.Series([score, level, ", ".join(explanation)])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Merge with risk table
    df = df.merge(risk_table, on=["Country", "Crop"], how="left")

    # Calculate risk
    df[['Final_Score', 'Final_Risk', 'Explanation']] = df.apply(calculate_risk, axis=1)

    st.write("### Results")
    st.write(df)
    st.write("### Distribución de riesgo")
    st.bar_chart(df['riesgo'].value_counts())
