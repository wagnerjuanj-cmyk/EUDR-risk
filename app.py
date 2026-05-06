st.title("EUDR Risk Assessment")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

# ----------------------------
# RISK TABLE (BASE DATA)
# ----------------------------
risk_table = pd.DataFrame({
    "country": ["argentina","brazil","colombia","costa rica","france","indonesia","mexico","spain"],
    "crop": ["soybean","coffee","coffee","coffee","cattle","oil palm","coffee","olives"],
    "risk_score": [3,3,2,1,1,3,2,1],
    "risk_level": ["high","high","medium","low","low","high","medium","low"],
    "deforestation": [1,1,1,0,0,1,1,0]
})

# ----------------------------
# SIMPLE COUNTRY NORMALIZER (mini-AI rules)
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
# RISK FUNCTION
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
# APP
# ----------------------------
if uploaded_file:

    df = pd.read_csv(uploaded_file, sep=None, engine="python")

    df.columns = df.columns.str.strip().str.lower()

    st.write("Detected columns:", df.columns.tolist())

    if "country" not in df.columns or "crop" not in df.columns:
        st.error("CSV must contain: country, crop")
        st.stop()

    # ----------------------------
    # NORMALIZATION (KEY FIX)
    # ----------------------------
    df["country"] = df["country"].apply(normalize_country)
    df["crop"] = df["crop"].apply(normalize_crop)

    risk_table["country"] = risk_table["country"].str.lower()
    risk_table["crop"] = risk_table["crop"].str.lower()

    # ----------------------------
    # MERGE
    # ----------------------------
    df = df.merge(risk_table, on=["country","crop"], how="left")

    # ----------------------------
    # IF NO MATCH → fallback risk (IMPORTANT)
    # ----------------------------
    df["risk_score"] = df["risk_score"].fillna(2)
    df["risk_level"] = df["risk_level"].fillna("medium")
    df["deforestation"] = df["deforestation"].fillna(0)

    # ----------------------------
    # RISK CALCULATION
    # ----------------------------
    df[["final_score","final_risk","explanation"]] = df.apply(
        calculate_risk,
        axis=1
    )

    # ----------------------------
    # OUTPUT
    # ----------------------------
    st.write("### Results")
    st.dataframe(df)
