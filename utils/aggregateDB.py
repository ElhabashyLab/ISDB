"""
Script for aggregating data from each database. 

Please do not change code here.
Changes should only be done it file paths 
if users know what they are doing.
"""

import pandas as pd
import numpy as np

# import sqlite3
import os
from datetime import date

tempory_directory = os.getenv("tempory_directory") + "/"


def not_float(value: str) -> bool:
    """
    Check if string is can not be cast to float
    """
    try:
        int(value)
        return False
    except ValueError:
        return True


def join_unique(values: list) -> list:
    """
    Returns a unique list of items of a list of "|" separated strings
    """
    values = [
        (
            str(v).replace(", ", "|")
            if "http" in v
            else str(v).replace(":", "|").replace("/", "|").replace(", ", "|")
        )
        for v in values
    ]
    unique_values = np.unique([i for v in values for i in v.split("|")])
    return "|".join(unique_values).replace("nan", "").strip("-|")


def main():
    print("### Aggregating data ###")
    # gather all output paths
    file_paths = []
    for path, _, files in os.walk(tempory_directory):
        for file in files:
            if file.endswith("out.csv") or file.endswith("out.tsv"):
                file_paths.append(path + file)
        break

    # read all files
    frames = []
    for file in file_paths:
        if file.endswith("tsv"):
            tmp = pd.read_csv(file, sep="\t")
            if any(
                tmp[["sourceTaxId", "targetTaxId"]].apply(
                    lambda x: any([not_float(i) for i in x]), axis=1
                )
            ):
                print(file)
            frames.append(pd.read_csv(file, sep="\t", dtype=str))
        else:
            tmp = pd.read_csv(file)
            if any(
                tmp[["sourceTaxId", "targetTaxId"]].apply(
                    lambda x: any([not_float(i) for i in x]), axis=1
                )
            ):
                print(file)
            frames.append(pd.read_csv(file, dtype=str))
    db = pd.concat(frames)
    # remove redundancy
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape)
    db = db.fillna("")
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "na")
    db = (
        db.groupby(["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"])
        .agg(lambda x: join_unique(x))
        .reset_index()
    )
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "drop_dup")
    db = db[
        db[["sourceTaxId", "targetTaxId"]].apply(
            lambda x: all([int(i) > 1 for i in x]), axis=1
        )
    ]
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, ">1")
    db["direction"] = db[
        ["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]
    ].apply(lambda x: tuple(set(x.values)), axis=1)
    db = db.drop_duplicates(subset=["direction"])
    db = db.drop("direction", axis=1)
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "dir")

    # export db csv
    db.to_csv(
        tempory_directory + "db_" + str(date.today()).replace("-", "_") + ".csv",
        index=False,
    )

    # export sql-lite
    # db = db[["targetTaxId", "sourceTaxId"]]
    # db.columns = ["species1", "species2"]
    # # Connect to SQLite database (create it if it doesn't exist)
    # conn = sqlite3.connect(
    #     tempory_directory + "db_" + str(date.today()).replace("-", "_") + ".db"
    # )
    # cursor = conn.cursor()

    # # Create a table and import data from CSV
    # cursor.execute(
    #     """
    #     CREATE TABLE IF NOT EXISTS species_species (
    #         species1 INTEGER,
    #         species2 INTEGER
    #     )
    # """
    # )

    # db.to_sql("species_species", conn, if_exists="replace", index=False)

    # conn.commit()
    # conn.close


if __name__ == "__main__":
    main()
