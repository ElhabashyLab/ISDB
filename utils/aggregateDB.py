"""
Script for aggregating data from each database. 

Please do not change code here.
Changes should only be done it file paths 
if users know what they are doing.
"""

import pandas as pd
import numpy as np
import os
from datetime import date

tempory_directory = os.getenv("tempory_directory") + "/"
additional_data = os.getenv("additional__data")


def check_dataframe(file: str) -> pd.DataFrame:
    columns = [
        "TaxIdA",
        "ScientificNameA",
        "UidA",
        "TaxIdB",
        "ScientificNameB",
        "UidB",
        "interactionType",
        "ontology",
        "reference",
        "database",
    ]
    data = pd.read_csv(file)
    missing_columns = [c for c in data.columns if c not in columns]
    usable_columns = [c for c in data.columns if c in columns]
    if usable_columns == []:
        print(f"Error: {file} has no matching columns")
        return pd.DataFrame(columns=columns)
    else:
        data = data["usable_columns"]
        for column in missing_columns:
            data[column] = ""
        return data


def get_additional_frames() -> list:
    """
    Returns a list of valid pandas Dataframes provided by the user
    """
    if os.path.isfile(additional_data):
        return [check_dataframe(additional_data)]
    elif os.path.isdir(additional_data):
        frames = []
        for file in [f for f in os.listdir(additional_data) if file.endswith(".csv")]:
            data = check_dataframe(additional_data + file)
            frames.append(data)
        return frames
    else:
        [
            pd.DataFrame(
                columns=[
                    "TaxIdA",
                    "ScientificNameA",
                    "UidA",
                    "TaxIdB",
                    "ScientificNameB",
                    "UidB",
                    "interactionType",
                    "ontology",
                    "reference",
                    "database",
                ]
            )
        ]

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
    values = [(str(v).replace(", ", "|")) for v in values]
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
    # rename columns TODO rename initial names in processDB.py
    db = db[
        [
            "sourceTaxId",
            "sourceName",
            "sourceUid",
            "targetTaxId",
            "targetName",
            "targetUid",
            "interactionType",
            "ontology",
            "reference",
            "database",
        ]
    ]
    db.columns = [
        "TaxIdA",
        "ScientificNameA",
        "UidA",
        "TaxIdB",
        "ScientificNameB",
        "UidB",
        "interactionType",
        "ontology",
        "reference",
        "database",
    ]
    # incorporate users data
    if additional_data:
        files = get_additional_frames()
        files.append(db)
        db = pd.concat(files)
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

    # Add a serial number column at position 1 09/Sep/2024
    db.insert(0, 'SerialNumber', range(1, len(db) + 1))
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "dir")

    # export db csv
    db.to_csv(
        tempory_directory + "db_" + str(date.today()).replace("-", "_") + ".csv",
        index=False,
    )


if __name__ == "__main__":
    main()
