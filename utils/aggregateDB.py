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
from dotenv import load_dotenv
import sys

sys.path.insert(1, "./")
from uniprot_api import uniprot_request
from helper import *


def main():
    # Initialize variables
    load_dotenv("config.env")
    out_directory = os.getenv("OUT_DIRECTORY")
    additional_data = os.getenv("ADDITIONAL_DATA")

    print("### Aggregating data ###")

    # Gather all output file paths from the temporary directory
    file_paths = []
    for path, _, files in os.walk(out_directory):
        for file in files:
            # Filter for output files
            if file.endswith("out.csv") or file.endswith("out.tsv"):
                file_paths.append(path + file)
        break

    # Read all files into DataFrames
    db = read_and_combine_output_files(file_paths)

    # Incorporate additional user data if provided
    if additional_data:
        files = get_additional_frames()
        files.append(db)
        db = pd.concat(files)

    # Standardize column names for consistency # TODO migrate later to helper_processDB.py
    db = db.rename(
        columns={
            "sourceTaxId": "Taxonomy ID A",
            "sourceName": "Organism A",
            "sourceUid": "UniProt ID A",
            "targetTaxId": "Taxonomy ID B",
            "targetName": "Organism B",
            "targetUid": "UniProt ID B",
            "interactionType": "Interaction Type",
            "ontology": "Ontology ID",
            "reference": "Reference",
            "database": "Database",
        }
    )

    # Adding UniProt names and accession number # TODO migrate later to helper_processDB.py
    uniprot = uniprot_request()
    for column in ["UniProt ID A", "UniProt ID B"]:
        tmp = db[column].apply(lambda x: uniprot.fast_protein_id_request(x)[1])
        db[column] = tmp.map(lambda x: x[1])
        db[f"Protein Name {column[-1]}"] = tmp.map(lambda x: x[0])

    # Remove redundancy by aggregating data
    print("Removing redundancies")
    db = db.fillna("")

    # Group by specific columns and aggregate unique values
    db = (
        db.groupby(["Taxonomy ID A", "Taxonomy ID B", "UniProt ID A", "UniProt ID B"])
        .agg(lambda x: join_unique(x))
        .reset_index()
    )

    # Filter rows where TaxId values are greater than 1
    db = db[
        db[["Taxonomy ID A", "Taxonomy ID B"]].apply(
            lambda x: all([int(i) > 1 for i in x]), axis=1
        )
    ]

    # Clean up TaxId values
    db["Taxonomy ID A"] = db["Taxonomy ID A"].apply(
        lambda x: str(x).replace("uniprotkb:", "")
    )
    db["Taxonomy ID B"] = db["Taxonomy ID B"].apply(
        lambda x: str(x).replace("uniprotkb:", "")
    )

    # Create a single direction identifier for entries
    db["direction"] = db[
        ["Taxonomy ID A", "Taxonomy ID B", "UniProt ID A", "UniProt ID B"]
    ].apply(lambda x: tuple(set(x.values)), axis=1)

    # Remove duplicate entries based on direction
    db = db.drop_duplicates(subset=["direction"])
    db = db.drop("direction", axis=1)

    # Add a serial number column at the first position
    print("Adding serial number and exporting data")
    db.insert(0, "Serial Number", range(1, len(db) + 1))

    # reorder
    db = db.loc[
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
    ]

    # Export the aggregated DataFrame to CSV and TSV formats
    db.to_csv(
        out_directory + "ISDB_" + str(date.today()).replace("-", "_") + ".csv",
        index=False,
    )
    db.to_csv(
        out_directory + "ISDB_" + str(date.today()).replace("-", "_") + ".tsv",
        index=False,
        sep="\t",
    )

    # Webpage query datasets
    # Protein search
    export_for_protein_search(db, out_directory)

    # Species search
    export_for_species_search(db, out_directory)


if __name__ == "__main__":
    main()  # Execute the main function
