# import pandas as pd

# # Load dataset
# df = pd.read_csv("microbiome_rel_abundance.csv")

# # View shape
# print(df.shape)

# # Remove completely empty rows
# df = df.dropna(how='all')

# # Remove completely empty columns
# df = df.dropna(axis=1, how='all')

# # Rename first column
# df = df.rename(columns={df.columns[0]: "taxonomy"})

# # Remove duplicate taxonomy rows
# df = df.drop_duplicates(subset=["taxonomy"])

# # Fill missing abundance values with 0
# df = df.fillna(0)

# # Convert abundance columns to numeric
# abundance_cols = df.columns[1:]

# df[abundance_cols] = df[abundance_cols].apply(
#     pd.to_numeric,
#     errors='coerce'
# )

# # Replace conversion NaNs with 0
# df[abundance_cols] = df[abundance_cols].fillna(0)

# # Remove taxa with extremely low abundance
# df = df[
#     df[abundance_cols].sum(axis=1) > 0.001
# ]

# # Optional: remove higher taxonomic levels
# # Keep only species-level entries
# df = df[
#     df["taxonomy"].str.contains("s__")
# ]

# # Reset index
# df = df.reset_index(drop=True)

# # Save cleaned dataset
# df.to_csv(
#     "clean_microbiome_rel_abundance.csv",
#     index=False
# )

# print(df.head())
# print(df.shape)


# import pandas as pd

# # Load metadata
# metadata = pd.read_csv("subject_metadata.csv")

# # View first rows
# print(metadata.head())

# # Remove completely empty rows
# metadata = metadata.dropna(how='all')

# # Remove completely empty columns
# metadata = metadata.dropna(axis=1, how='all')

# # Keep only useful columns
# metadata = metadata[
#     [
#         "sample_name",
#         "Case_status",
#         "Sex",
#         "Age_at_collection"
#     ]
# ]

# # Remove rows missing important values
# metadata = metadata.dropna(
#     subset=["sample_name", "Case_status"]
# )

# # Standardize labels
# metadata["Case_status"] = (
#     metadata["Case_status"]
#     .str.strip()
#     .str.upper()
# )

# # Convert Parkinson/control labels to numeric
# metadata["target"] = metadata[
#     "Case_status"
# ].map({
#     "CONTROL": 0,
#     "PD": 1
# })

# # Encode sex column
# metadata["Sex"] = metadata["Sex"].map({
#     "M": 0,
#     "F": 1
# })

# # Convert age to numeric
# metadata["Age_at_collection"] = pd.to_numeric(
#     metadata["Age_at_collection"],
#     errors='coerce'
# )

# # Fill missing ages with median age
# metadata["Age_at_collection"] = (
#     metadata["Age_at_collection"]
#     .fillna(
#         metadata["Age_at_collection"].median()
#     )
# )

# # Remove duplicates
# metadata = metadata.drop_duplicates(
#     subset=["sample_name"]
# )

# # Reset index
# metadata = metadata.reset_index(drop=True)

# # Save cleaned metadata
# metadata.to_csv(
#     "clean_subject_metadata.csv",
#     index=False
# )

# print(metadata.head())
# print(metadata.shape)


# =========================
# IMPORT LIBRARIES
# =========================

import pandas as pd

from ucimlrepo import fetch_ucirepo

# =========================
# FETCH DATASET
# =========================

parkinsons = fetch_ucirepo(id=174)

# =========================
# FEATURES
# =========================

X = parkinsons.data.features

# =========================
# TARGET
# =========================

y = parkinsons.data.targets

# =========================
# DISPLAY DATA
# =========================

print("\nFEATURES:\n")

print(X.head())

print("\nTARGET:\n")

print(y.head())

# =========================
# METADATA
# =========================

print("\nMETADATA:\n")

print(parkinsons.metadata)

# =========================
# VARIABLES
# =========================

print("\nVARIABLES:\n")

print(parkinsons.variables)

# =========================
# COMBINE INTO ONE DATAFRAME
# =========================

df = pd.concat(
    [X, y],
    axis=1
)

# =========================
# SAVE CSV
# =========================

df.to_csv(
    "parkinsons_voice_dataset.csv",
    index=False
)

print("\nCSV SAVED SUCCESSFULLY")
