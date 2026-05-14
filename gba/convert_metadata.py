import pandas as pd
import re

# =========================
# READ TXT FILE
# =========================

with open(
    "biosample_result.txt",
    "r",
    encoding="utf-8"
) as f:

    text = f.read()

# =========================
# SPLIT SAMPLES
# =========================

samples = text.split(
    "MIMS Environmental/Metagenome sample"
)

data = []

# =========================
# EXTRACT FEATURES
# =========================

for sample in samples:

    if "/Case_status=" not in sample:
        continue

    row = {}

    # -------------------------
    # SAMPLE NAME
    # -------------------------

    sample_name = re.search(
        r"Sample name: ([^;\n]+)",
        sample
    )

    if sample_name:
        row["sample_name"] = (
            sample_name.group(1).strip()
        )

    # -------------------------
    # CASE STATUS
    # -------------------------

    case_status = re.search(
        r'/Case_status=\"([^\"]+)\"',
        sample
    )

    if case_status:
        row["Case_status"] = (
            case_status.group(1)
        )

    # -------------------------
    # SEX
    # -------------------------

    sex = re.search(
        r'/sex=\"([^\"]+)\"',
        sample
    )

    if sex:
        row["sex"] = sex.group(1)

    # -------------------------
    # AGE
    # -------------------------

    age = re.search(
        r'/Age_at_collection=\"([^\"]+)\"',
        sample
    )

    if age:
        row["age"] = age.group(1)

    # -------------------------
    # BMI
    # -------------------------

    bmi = re.search(
        r'/body mass index=\"([^\"]+)\"',
        sample
    )

    if bmi:
        row["bmi"] = bmi.group(1)

    # =========================
    # FEATURE PATTERNS
    # =========================

    features = {

        "IBS":
        r'/IBS=\"([^\"]+)\"',

        "IBD":
        r'/IBD=\"([^\"]+)\"',

        "Constipation":
        r'/Constipation=\"([^\"]+)\"',

        "Depression_anxiety_mood_med":
        r'/Depression_anxiety_mood_med=\"([^\"]+)\"',

        "Sleep_aid":
        r'/Sleep_aid=\"([^\"]+)\"',

        "Probiotic":
        r'/Probiotic=\"([^\"]+)\"',

        "PPI":
        r'/PPI=\"([^\"]+)\"',

        "Anti_inflammatory_drugs":
        r'/Anti_inflammatory_drugs=\"([^\"]+)\"',

        "Antibiotics_current":
        r'/Antibiotics_current=\"([^\"]+)\"',

        "Antibiotics_past_3_months":
        r'/Antibiotics_past_3_months=\"([^\"]+)\"'
    }

    # =========================
    # EXTRACT FEATURES
    # =========================

    for key, pattern in features.items():

        result = re.search(
            pattern,
            sample
        )

        if result:
            row[key] = result.group(1)

    data.append(row)

# =========================
# CREATE DATAFRAME
# =========================

df = pd.DataFrame(data)

# =========================
# DISPLAY RAW COLUMNS
# =========================

print("\nRAW COLUMNS FOUND:\n")

print(df.columns)

# =========================
# BINARY COLUMNS
# =========================

binary_cols = [

    "IBS",
    "IBD",
    "Constipation",

    "Depression_anxiety_mood_med",
    "Sleep_aid",

    "Probiotic",
    "PPI",

    "Anti_inflammatory_drugs",

    "Antibiotics_current",
    "Antibiotics_past_3_months"
]

# =========================
# CLEAN BINARY VALUES
# =========================

for col in binary_cols:

    # Skip missing columns
    if col not in df.columns:
        continue

    df[col] = (
        df[col]
        .astype(str)
        .str.upper()
        .map({
            "Y": 1,
            "N": 0,
            "YES": 1,
            "NO": 0
        })
    )

# =========================
# TARGET ENCODING
# =========================

if "Case_status" in df.columns:

    df["target"] = (
        df["Case_status"]
        .astype(str)
        .str.upper()
        .map({
            "PD": 1,
            "CONTROL": 0
        })
    )

# =========================
# SEX ENCODING
# =========================

if "sex" in df.columns:

    df["sex"] = (
        df["sex"]
        .astype(str)
        .str.lower()
        .map({
            "male": 1,
            "female": 0
        })
    )

# =========================
# NUMERIC CONVERSION
# =========================

if "age" in df.columns:

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

if "bmi" in df.columns:

    df["bmi"] = pd.to_numeric(
        df["bmi"],
        errors="coerce"
    )

# =========================
# CREATE MISSING AMR COLUMNS
# =========================

needed_cols = [

    "Antibiotics_current",

    "Antibiotics_past_3_months",

    "PPI",

    "Anti_inflammatory_drugs",

    "Probiotic"
]

for col in needed_cols:

    if col not in df.columns:
        df[col] = 0

# =========================
# FILL NULLS
# =========================

df = df.fillna(0)

# =========================
# CREATE AMR SCORE
# =========================

df["amr_burden_score"] = (

    df["Antibiotics_current"] * 40 +

    df["Antibiotics_past_3_months"] * 30 +

    df["PPI"] * 10 +

    df["Anti_inflammatory_drugs"] * 10 +

    (1 - df["Probiotic"]) * 10
)

# =========================
# CREATE GUT-BRAIN SCORE
# =========================

gut_cols = [

    "IBS",
    "IBD",
    "Constipation",

    "Depression_anxiety_mood_med",

    "Sleep_aid"
]

for col in gut_cols:

    if col not in df.columns:
        df[col] = 0

df["gut_brain_score"] = (

    df["IBS"] * 20 +

    df["IBD"] * 20 +

    df["Constipation"] * 20 +

    df["Depression_anxiety_mood_med"] * 20 +

    df["Sleep_aid"] * 20
)

# =========================
# SAVE CSV
# =========================

df.to_csv(
    "metadata_features.csv",
    index=False
)

# =========================
# DISPLAY RESULTS
# =========================

print("\nDATASET CREATED SUCCESSFULLY\n")

print(df.head())

print("\nFINAL COLUMNS:\n")

print(df.columns)

print("\nDATASET SHAPE:")

print(df.shape)

print("\nCSV SAVED AS:")

print("metadata_features.csv")
