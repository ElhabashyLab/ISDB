#!/usr/bin/env python3

import pandas as pd
import numpy as np
from datetime import datetime

# ============================
# USER INPUT
# ============================
ISDB_FILE = "<path to the isdb database file>.csv"
OUTPUT_LOG = "ISDB_statistics.log"

# ============================
# Logging helper
# ============================
def log(msg, fh):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fh.write(f"[{timestamp}] {msg}\n")

# ============================
# Load data
# ============================
df = pd.read_csv(ISDB_FILE, comment="#", dtype=str)

# ============================
# Normalize column names (R-style)
# ============================
df.columns = df.columns.str.strip().str.replace(" ", ".", regex=False)

# ============================
# Convert empty UniProt IDs to NA
# ============================
for col in ["UniProt.ID.A", "UniProt.ID.B"]:
    df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)

# ============================
# Open log file
# ============================
with open(OUTPUT_LOG, "w") as logf:

    log("ISDB statistics summary", logf)
    log(f"Input file: {ISDB_FILE}", logf)
    log(f"Total rows: {len(df)}", logf)
    log("", logf)

    # ----------------------------
    # 1. Total unique Taxonomy IDs
    # ----------------------------
    unique_tax_ids = pd.unique(pd.concat([df["Taxonomy.ID.A"], df["Taxonomy.ID.B"]]))
    log(f"Total unique Taxonomy IDs: {len(unique_tax_ids)}", logf)

    # ----------------------------
    # 2. Unique Taxonomy pairs (A-B = B-A)
    # ----------------------------
    tax_pair = np.where(
        df["Taxonomy.ID.A"] <= df["Taxonomy.ID.B"],
        df["Taxonomy.ID.A"] + "-" + df["Taxonomy.ID.B"],
        df["Taxonomy.ID.B"] + "-" + df["Taxonomy.ID.A"]
    )
    log(f"Total unique Taxonomy pairs (A-B = B-A): {len(pd.unique(tax_pair))}", logf)

    # ----------------------------
    # 3. Unique PPIs (UniProt A-B symmetric)
    # ----------------------------
    df_ppi = df.dropna(subset=["UniProt.ID.A", "UniProt.ID.B"]).copy()
    ppi_pair = np.where(
        df_ppi["UniProt.ID.A"] <= df_ppi["UniProt.ID.B"],
        df_ppi["UniProt.ID.A"] + "-" + df_ppi["UniProt.ID.B"],
        df_ppi["UniProt.ID.B"] + "-" + df_ppi["UniProt.ID.A"]
    )
    log(f"Total unique PPIs (UniProt A-B = B-A): {len(pd.unique(ppi_pair))}", logf)
    log("", logf)

    # ----------------------------
    # 4. Expand multi-database entries
    # ----------------------------
    df_expanded = df.assign(Database=df["Database"].str.split("|")).explode("Database")

    # Taxonomy pairs for expanded dataframe
    df_expanded["tax_pair"] = np.where(
        df_expanded["Taxonomy.ID.A"] <= df_expanded["Taxonomy.ID.B"],
        df_expanded["Taxonomy.ID.A"] + "-" + df_expanded["Taxonomy.ID.B"],
        df_expanded["Taxonomy.ID.B"] + "-" + df_expanded["Taxonomy.ID.A"]
    )

    # ----------------------------
    # 5. Per-database statistics
    # ----------------------------
    log("Per-database statistics:", logf)

    for db, sub in df_expanded.groupby("Database"):
        tax_ids = pd.unique(pd.concat([sub["Taxonomy.ID.A"], sub["Taxonomy.ID.B"]]))
        tax_pairs = pd.unique(sub["tax_pair"])

        sub_ppi = sub.dropna(subset=["UniProt.ID.A", "UniProt.ID.B"])
        if len(sub_ppi) > 0:
            ppi_pairs = np.where(
                sub_ppi["UniProt.ID.A"] <= sub_ppi["UniProt.ID.B"],
                sub_ppi["UniProt.ID.A"] + "-" + sub_ppi["UniProt.ID.B"],
                sub_ppi["UniProt.ID.B"] + "-" + sub_ppi["UniProt.ID.A"]
            )
            unique_ppi = len(pd.unique(ppi_pairs))
        else:
            unique_ppi = 0

        log(
            f"  {db}: unique_tax_ids={len(tax_ids)}, "
            f"unique_tax_pairs={len(tax_pairs)}, "
            f"unique_ppi={unique_ppi}",
            logf
        )

    log("", logf)
    log("Done.", logf)

print(f"Statistics written to: {OUTPUT_LOG}")
