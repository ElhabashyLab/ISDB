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

# Get environment variables for temporary directory and additional data
tempory_directory = os.getenv("tempory_directory") + "/"
additional_data = os.getenv("additional_data")


def check_dataframe(file: str) -> pd.DataFrame:
    """
    Checks if the given file has the necessary columns and returns the full DataFrame.
    
    Args:
        file (str): Path to the CSV file to check.
    
    Returns:
        pd.DataFrame: DataFrame with the necessary columns; empty DataFrame if no matching columns are found.
    """
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
    # Read the CSV file into a DataFrame
    data = pd.read_csv(file)
    
    # Identify missing and usable columns
    missing_columns = [c for c in data.columns if c not in columns]
    usable_columns = [c for c in data.columns if c in columns]
    
    # If no usable columns, return an empty DataFrame
    if usable_columns == []:
        print(f"Error: {file} has no matching columns")
        return pd.DataFrame(columns=columns)
    else:
        # Keep only usable columns and add missing ones as empty
        data = data["usable_columns"]
        for column in missing_columns:
            data[column] = ""
        return data


def get_additional_frames() -> list:
    """
    Returns a list of valid pandas DataFrames provided by the user.
    
    Returns:
        list: List of DataFrames or an empty DataFrame if no valid files are found.
    """
    if os.path.isfile(additional_data):
        return [check_dataframe(additional_data)]
    elif os.path.isdir(additional_data):
        frames = []
        # Iterate through CSV files in the additional data directory
        for file in [f for f in os.listdir(additional_data) if file.endswith(".csv")]:
            data = check_dataframe(additional_data + file)
            frames.append(data)
        return frames
    else:
        # Return an empty DataFrame if no valid additional data found
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
    Check if the string cannot be cast to float.
    
    Args:
        value (str): The string to check.
    
    Returns:
        bool: True if the string cannot be converted to a float; otherwise, False.
    """
    try:
        int(value)
        return False
    except ValueError:
        return True


def join_unique(values: list) -> list:
    """
    Returns a unique list of items from a list of "|" separated strings.
    
    Args:
        values (list): List of strings to process.
    
    Returns:
        str: A "|" separated string of unique values.
    """
    # Replace commas with "|", split into unique values, and join back into a string
    values = [(str(v).replace(", ", "|")) for v in values]
    unique_values = np.unique([i for v in values for i in v.split("|")])
    return "|".join(unique_values).replace("nan", "").strip("-|")



def main():
    print("### Aggregating data ###")
    
    # Gather all output file paths from the temporary directory
    file_paths = []
    for path, _, files in os.walk(tempory_directory):
        for file in files:
             # Filter for output files
            if file.endswith("out.csv") or file.endswith("out.tsv"):
                file_paths.append(path + file)
        break

     # Read all files into DataFrames
    frames = []
    for file in file_paths:
        if file.endswith("tsv"):
            tmp = pd.read_csv(file, sep="\t")
            # Check for non-float values in specified columns
            if any(
                tmp[["sourceTaxId", "targetTaxId"]].apply(
                    lambda x: any([not_float(i) for i in x]), axis=1
                )
            ):
                print(file)  # Print filename if non-float values are found
            frames.append(pd.read_csv(file, sep="\t", dtype=str))
        else:
            tmp = pd.read_csv(file)
            if any(
                tmp[["sourceTaxId", "targetTaxId"]].apply(
                    lambda x: any([not_float(i) for i in x]), axis=1
                )
            ):
                print(file) # Print filename if non-float values are found
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
    # Incorporate additional user data if provided
    if additional_data:
        files = get_additional_frames()
        files.append(db)
        db = pd.concat(files)
    # Remove redundancy by aggregating data
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape)
    db = db.fillna("")
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "na")

    # Group by specific columns and aggregate unique values
    db = (
        db.groupby(["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"])
        .agg(lambda x: join_unique(x))
        .reset_index()
    )
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "drop_dup")

    # Filter rows where TaxId values are greater than 1
    db = db[
        db[["sourceTaxId", "targetTaxId"]].apply(
            lambda x: all([int(i) > 1 for i in x]), axis=1
        )
    ]
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, ">1")
    
    # Clean up TaxId values
    db["TaxIdA"] = db["TaxIdA"].apply(lambda x: str(x).replace("uniprotkb:", ""))
    db["TaxIdB"] = db["TaxIdB"].apply(lambda x: str(x).replace("uniprotkb:", ""))
    
    # Create a single direction identifier for entries
    db["direction"] = db[
        ["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]
    ].apply(lambda x: tuple(set(x.values)), axis=1)

    # Remove duplicate entries based on direction
    db = db.drop_duplicates(subset=["direction"])
    db = db.drop("direction", axis=1)
    
    # Add a serial number column at the first position
    db.insert(0, 'SerialNumber', range(1, len(db) + 1))
    print(db[db["database"].apply(lambda x: "Intact" in x)].shape, "dir")

    # Export the aggregated DataFrame to CSV and TSV formats
    db.to_csv(
        tempory_directory + "ISDB_" + str(date.today()).replace("-", "_") + ".csv",
        index=False,
    )
    db.to_csv(
        tempory_directory + "ISDB_" + str(date.today()).replace("-", "_") + ".tsv",
        index=False, sep="\t",
    )


if __name__ == "__main__":
    main()  # Execute the main function
