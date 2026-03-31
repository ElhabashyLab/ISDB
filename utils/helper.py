"""
Utility functions shared across multiple scripts.
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
from datetime import date

sys.path.insert(1, "./")
from uniprot_api import uniprot_request

# I/O dir suffixes
input_dir = "inputs/"
output_dir = "outputs/"

# Columns for the final output tables
table_columns = [
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

env2name = {
    # ===== Manual files =====
    "BATECO_FILE": "BatEco_Interactions",
    "PHISTO_FILE": "PHISTO",
    "PHILM2WEB_FILE": "PHILM2Web",
    "FGSCDB_FILE": "FGSCdb",
    # ===== Manual directories =====
    "BVBRC_DIR": "BVBRC",
    "DIP_DIR": "DIP",
    "GMPD_DIR": "GMPD",
    # ===== Automatic files =====
    "GLOBI_FILE": "GloBI",
    "INTACT_FILE": "Intact",
    "PHI_BASE_FILE": "PHI_base",
    "PIDA_FILE": "Pida",
    "VIRHOSTNET_FILE": "VirHostNet",
    "EID2_FILE": "EID2",
    "SIAD_FILE": "Siad",
    "MINT_FILE": "Mint",
    "SIGNOR_FILE": "Signor",
    # ===== Automatic directories =====
    "HPIDB_DIR": "HPIDB",
    "BIOGRID_DIR": "BioGRID",
    "WEB_OF_LIFE_DATABASE_DIR": "Web_of_Life_database",
    "HPIDB_DIR": "HPIDB",
    "IWDB_DIR": "IWDB",
    "PMC9897028_DIR": "PMC9897028",
}


def check_dataframe(file: str) -> pd.DataFrame:
    """
    Checks if the given file has the necessary columns and returns the full DataFrame.

    Args:
        file (str): Path to the CSV file to check.

    Returns:
        pd.DataFrame: DataFrame with the necessary columns; empty DataFrame if no matching columns are found.
    """
    # Read the CSV file into a DataFrame
    data = pd.read_csv(file)

    # Identify missing and usable columns
    missing_columns = [c for c in table_columns if c not in data.columns]
    usable_columns = [c for c in data.columns if c in table_columns]
    # If no usable columns, return an empty DataFrame
    if len(usable_columns) == 0:
        print(f"Error: {file} has no matching columns")
        return pd.DataFrame(columns=table_columns)
    else:
        # Keep only usable columns and add missing ones as empty
        data = data[usable_columns]
        for column in missing_columns:
            data[column] = ""
        return data


def get_additional_frames(additional_data: str) -> list:
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
        for file in [f for f in os.listdir(additional_data) if f.endswith(".csv")]:
            data = check_dataframe(additional_data + file)
            frames.append(data)
        return frames
    else:
        # Return an empty DataFrame if no valid additional data found
        return [pd.DataFrame(columns=table_columns)]


def is_float(value: str) -> bool:
    """
    Check if string can be cast to float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def not_float(value: str) -> bool:
    """
    Check if the string cannot be cast to float.

    Args:
        value (str): The string to check.

    Returns:
        bool: True if the string cannot be converted to a float; otherwise, False.
    """
    return not is_float(value)


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
    unique_values = [
        v for v in unique_values if str(v).lower() != "nan" and str(v).lower() != "none"
    ]
    return "|".join(unique_values).strip("-|")


def read_and_combine_output_files(file_paths: list) -> pd.DataFrame:
    """
    Reads multiple output files (CSV/TSV) and combines them into a single DataFrame.

    Args:
        file_paths (list): List of file paths to read.
    Returns:
        pd.DataFrame: Combined DataFrame containing data from all files.
    """
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
                print(file)  # Print filename if non-float values are found
            frames.append(pd.read_csv(file, dtype=str))
    return pd.concat(frames)


def export_for_protein_search(db: pd.DataFrame, tmp_dir: str) -> None:
    """
    Exports a subset of the database for protein search, ensuring that only entries with valid UniProt IDs are included.
    """
    # Protein search
    db.loc[
        :,
        [
            "Serial Number",
            "Taxonomy ID A",
            "Organism A",
            "UniProt ID A",
            "Protein Name A",
            "Taxonomy ID B",
            "Organism B",
            "UniProt ID B",
            "Protein Name B",
            "Interaction Type",
            "Ontology ID",
            "Reference",
            "Database",
        ],
    ].dropna(subset=["UniProt ID A", "UniProt ID B"]).to_csv(
        os.path.join(
            tmp_dir, f"ISDB_Protein_Search_{str(date.today()).replace('-', '_')}.tsv"
        ),
        index=False,
        sep="\t",
    )


def export_for_species_search(db: pd.DataFrame, tmp_dir: str) -> None:
    """
    Exports a subset of the database for species search, ensuring that only entries with valid Taxonomy IDs are included.
    """
    # Species search
    db.loc[
        :,
        [
            "Serial Number",
            "Taxonomy ID A",
            "Organism A",
            "Taxonomy ID B",
            "Organism B",
            "Interaction Type",
            "Ontology ID",
            "Reference",
            "Database",
        ],
    ].drop_duplicates(subset=["Taxonomy ID A", "Taxonomy ID B"]).to_csv(
        os.path.join(
            tmp_dir, f"ISDB_Species_Search_{str(date.today()).replace('-', '_')}.tsv"
        ),
        index=False,
        sep="\t",
    )


def file_exists(path: str, tmp_dir: str) -> None:
    """
    Checks if file path or path exists
    """
    if (not os.path.isdir(os.path.join(tmp_dir, path))) and (
        not os.path.exists(os.path.join(tmp_dir, path))
    ):
        raise ValueError(f"Provided input path '{path}' is not valid. Check download.")


def check_out_exists(name: str, tmp_dir) -> bool:
    """
    Checks if processed data of a single database (_out file) exists
    """
    file_exists = any(
        [file.__contains__(name + "_out") for file in os.listdir(tmp_dir)]
    )
    return file_exists


def clean_dataframe(dataFrame: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans dataframe: drops nan values in TaxIds and duplicate values
    """

    def join_unique(values: list) -> list:
        unique_values = np.unique([i for v in values for i in str(v).split("|")])
        return "|".join(unique_values)

    dataFrame = dataFrame.dropna(subset=["sourceTaxId", "targetTaxId"]).astype(str)
    dataFrame = (
        dataFrame.groupby(["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"])
        .agg(lambda x: join_unique(x))
        .reset_index()
    )
    # dataFrame = dataFrame.drop_duplicates(
    #     subset=["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]
    # )
    return dataFrame


def getSourceTargetNames(
    dataFrame: pd.DataFrame, uniprot: uniprot_request
) -> pd.DataFrame:
    """
    Retrieves scientific names for source and target via their TaxId
    """
    # get Scientific Name
    dataFrame["sourceName"] = dataFrame["sourceTaxId"].apply(
        lambda x: uniprot.fast_tax_request(x)
    )
    dataFrame["targetName"] = dataFrame["targetTaxId"].apply(
        lambda x: uniprot.fast_tax_request(x)
    )
    return dataFrame


def get_taxonomic_identifier(uniprot_id: str) -> str:
    """
    Retrieves TaxId for source and target via their Uniprot Id
    """
    query = uniprot_id.split("-")[0]
    requestURL = (
        "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&accession="
        + query
    )
    response = requests.get(requestURL, headers={"Accept": "application/xml"})
    print(uniprot_id, end="\r")
    if response.status_code != 200:
        return None
    xml_data = response.text
    # Parsing XML to extract taxonomic identifier
    start_index = xml_data.find('<dbReference type="NCBI Taxonomy" id=')
    if start_index == -1:
        return None
    start_index = xml_data.find("id=", start_index) + 4
    end_index = xml_data.find('"', start_index)
    taxonomic_identifier = xml_data[start_index:end_index]
    return taxonomic_identifier


def export_dataframe(
    dataFrame: pd.DataFrame, database: str, tmp_dir: str, typ: str
) -> None:
    """
    Export dataFrame to csv/tsv
    """
    dataFrame["database"] = database
    for c in table_columns:
        if c not in dataFrame.columns:
            dataFrame[c] = ""
    dataFrame = dataFrame[table_columns]
    if typ == "csv":
        dataFrame.to_csv(
            os.path.join(tmp_dir, "..", output_dir, f"{database.lower()}_out.csv"),
            index=False,
        )
    elif typ == "tsv":
        dataFrame.to_csv(
            os.path.join(tmp_dir, "..", output_dir, f"{database.lower()}_out.tsv"),
            sep="\t",
            index=False,
        )
    else:
        raise TypeError(f"{typ} is not a valid file format for export [csv/tsv]")


def rename_subset_df(dataFrame: pd.DataFrame, col_mapping: dict) -> pd.DataFrame:
    """
    Rename columns and subset them
    """
    return dataFrame[list(col_mapping.keys())].rename(columns=col_mapping).astype(str)


def add_taxonomy_info(
    data: pd.DataFrame,
    query_column: str,
    taxid_column: str,
    name_column: str,
    uniprot: uniprot_request,
) -> pd.DataFrame:
    """
    Adds taxonomy IDs and names to a DataFrame based on a query column.
    """
    tax_ids = []
    names = []

    for i, row in data.iterrows():
        print(f"Processing row {i}", end="\r")
        name_, tax_id = uniprot.fast_tax_name_request(row[query_column])
        tax_ids.append(tax_id)
        names.append(name_)

    data[taxid_column] = tax_ids
    data[name_column] = names

    print("\nDone processing taxonomy info.")
    return data
