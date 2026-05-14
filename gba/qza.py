# =========================================================
# qza_to_csv.py
# NO QIIME2 REQUIRED
# =========================================================

import os
import zipfile
import biom
import pandas as pd

# =====================================================
# PATHS
# =====================================================

QZA_PATH = "table.qza"

EXTRACT_DIR = "qza_extracted"

OUTPUT_CSV = "feature-table.csv"

os.makedirs(
    EXTRACT_DIR,
    exist_ok=True
)

# =====================================================
# EXTRACT QZA
# =====================================================

print("\nEXTRACTING QZA...")

with zipfile.ZipFile(
    QZA_PATH,
    'r'
) as zip_ref:

    zip_ref.extractall(
        EXTRACT_DIR
    )

print("\nQZA EXTRACTED")

# =====================================================
# FIND BIOM FILE
# =====================================================

biom_path = None

for root, dirs, files in os.walk(
    EXTRACT_DIR
):

    for file in files:

        if file.endswith(".biom"):

            biom_path = os.path.join(
                root,
                file
            )

            break

print("\nBIOM FILE FOUND:")
print(biom_path)

# =====================================================
# LOAD BIOM
# =====================================================

table = biom.load_table(
    biom_path
)

# =====================================================
# CONVERT TO DATAFRAME
# =====================================================

df = table.to_dataframe(
    dense=True
)

# =====================================================
# TRANSPOSE
# =====================================================

df = df.T

# =====================================================
# SAVE CSV
# =====================================================

df.to_csv(
    OUTPUT_CSV
)

print("\nCSV SAVED")

print("\nOUTPUT:")
print(OUTPUT_CSV)

print("\nSHAPE:")
print(df.shape)

print(df.head())
