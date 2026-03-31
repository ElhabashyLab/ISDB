"""
Utility processing functions for each database
"""

import os
import sys
import pandas as pd
import numpy as np
import requests
import re

sys.path.insert(1, "./")
from uniprot_api import uniprot_request
from helper import *


def clean_bvbrc(
    prefix: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning raw data from BV-BRC"""
    frames = []
    col = ["NCBI Taxon ID", "Reference", "Publication", "Host Name"]
    for file in os.listdir(os.path.join(tempory_directory, prefix)):
        if file.endswith(".csv"):
            data = pd.read_csv(
                os.path.join(tempory_directory, prefix, file),
                usecols=col,
                dtype=str,
            ).astype(str)
            data = data[data["Host Name"].notna()]
            # TaxIds
            data["sourceName"] = data["NCBI Taxon ID"].apply(
                lambda x: uniprot.fast_tax_request(x)
            )
            # search uniprot
            data["Host Name"] = data["Host Name"].apply(
                lambda x: x.split(",")[1] if len(x.split(",")) > 1 else x
            )
            species = data["Host Name"].apply(
                lambda x: uniprot.fast_tax_name_request(x)
            )
            data["targetName"] = list(map(lambda x: x[0], species))
            data["targetTaxId"] = list(map(lambda x: x[1], species))
            # clean data
            data["reference"] = data[["Reference", "Publication"]].apply(
                lambda x: "|".join(x.values), axis=1
            )

            data = rename_subset_df(
                data,
                {
                    "NCBI Taxon ID": "sourceTaxId",
                    "sourceName": "sourceName",
                    "reference": "reference",
                    "targetName": "targetName",
                    "targetTaxId": "targetTaxId",
                },
            )

            data["sourceUid"] = ""
            data["targetUid"] = ""
            data = clean_dataframe(data)
            frames.append(data)
    data = pd.concat(frames, axis=0, ignore_index=True)
    # clean
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "csv")


def clean_globi(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
) -> None:
    """Cleaning raw data from GloBI"""
    # load data
    col = [
        "sourceTaxonName",
        "sourceTaxonIds",
        "interactionTypeName",
        "interactionTypeId",
        "targetTaxonName",
        "targetTaxonIds",
        "referenceDoi",
    ]
    slice_size = 5_000_000
    interaction_types = []
    out = []

    # iterate over file in chunks
    for data in pd.read_csv(
        os.path.join(tempory_directory, file),
        usecols=col,
        sep="\t",
        header=0,
        chunksize=slice_size,
    ):

        data["sourceUid"] = ""
        data["targetUid"] = ""

        data = rename_subset_df(
            data,
            {
                "sourceTaxonIds": "sourceTaxId",
                "sourceTaxonName": "sourceName",
                "sourceUid": "sourceUid",
                "targetTaxonIds": "targetTaxId",
                "targetTaxonName": "targetName",
                "targetUid": "targetUid",
                "interactionTypeName": "interactionType",
                "interactionTypeId": "ontology",
                "referenceDoi": "reference",
            },
        )
        # clean TaxIds
        data["sourceTaxId"] = data["sourceTaxId"].apply(
            lambda x: (
                re.search("NCBI:\d+", x)[0].replace("NCBI:", "")
                if (re.search("NCBI:\d+", x) is not None)
                else None
            )
        )
        data["targetTaxId"] = data["targetTaxId"].apply(
            lambda x: (
                re.search("NCBI:\d+", x)[0].replace("NCBI:", "")
                if (re.search("NCBI:\d+", x) is not None)
                else None
            )
        )
        # clean result
        data = clean_dataframe(data)
        # get Scientific Name
        data = getSourceTargetNames(data, uniprot)
        out.append(data)
    data = pd.concat(out)
    # clean
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_biogrid(
    path: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning biogrid"""
    col_mapping = {
        "Taxid Interactor A": "sourceTaxId",
        "Alt IDs Interactor A": "sourceUid",  # uniprot/swiss-prot:
        "Taxid Interactor B": "targetTaxId",
        "Alt IDs Interactor B": "targetUid",
        "Interaction Types": "ontology",  # Split
        "Publication Identifiers": "reference",
    }
    file = os.listdir(os.path.join(tempory_directory, path))[0]
    data = pd.read_csv(
        os.path.join(tempory_directory, path, file),
        sep="\t",
        usecols=list(col_mapping.keys()),
    ).astype(str)
    data = rename_subset_df(data, col_mapping)
    data["sourceTaxId"] = data["sourceTaxId"].apply(lambda x: x.replace("taxid:", ""))
    data["targetTaxId"] = data["targetTaxId"].apply(lambda x: x.replace("taxid:", ""))
    data = data[
        data[["sourceTaxId", "targetTaxId"]].apply(
            lambda x: all([is_float(i) for i in x]), axis=1
        )
    ]
    data = data[(data["sourceTaxId"] != "nan") | (data["targetTaxId"] != "nan")]

    data["interactionType"] = data["ontology"].apply(
        lambda x: "(".join(x.split("(")[1:]).strip('("')
    )
    data["ontology"] = data["ontology"].apply(lambda x: x.split("(")[0])
    data["sourceUid"] = data["sourceUid"].apply(
        lambda x: x.split("uniprot/swiss-prot:")[-1].split("|")[0]
    )
    data["targetUid"] = data["targetUid"].apply(
        lambda x: x.split("uniprot/swiss-prot:")[-1].split("|")[0]
    )
    # clean data
    data = clean_dataframe(data)
    # get Scientific Name
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_dip(prefix: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning raw data DIP"""  # TODO check direction source & target
    # import data
    data = []
    for file in os.listdir(os.path.join(tempory_directory, prefix)):
        if file.endswith(".txt"):
            tmp = pd.read_csv(
                os.path.join(tempory_directory, prefix, file),
                sep="\t",
                index_col=16,
                encoding="unicode_escape",
            ).reset_index()
            tmp = tmp[
                [
                    "Taxid interactor A",
                    "ID interactor A",
                    "Taxid interactor B",
                    "ID interactor B",
                    "Interaction type(s)",
                    "Publication Identifier(s)",
                ]
            ]
            data.append(tmp)
    data = pd.concat(data)
    data = rename_subset_df(
        data,
        {
            "Taxid interactor A": "sourceTaxId",
            "ID interactor A": "sourceUid",
            "Taxid interactor B": "targetTaxId",
            "ID interactor B": "targetUid",
            "Interaction type(s)": "interactionType",
            "Publication Identifier(s)": "reference",
        },
    )

    # reformat data
    data["sourceUid"] = data["sourceUid"].apply(
        lambda x: x.split("uniprotkb:")[-1].split("|")[0]
    )
    data["targetUid"] = data["targetUid"].apply(
        lambda x: x.split("uniprotkb:")[-1].split("|")[0]
    )

    data["ontology"] = data["interactionType"].apply(lambda x: x.split("(")[0])
    data["interactionType"] = data["interactionType"].apply(
        lambda x: x.split("(")[-1][:-1]
    )
    # clean TaxIds
    data["sourceTaxId"] = data["sourceTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    data["targetTaxId"] = data["targetTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    # clean result
    data = clean_dataframe(data)
    # get Scientific Name
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_fgscdb(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning raw data FGSCdb"""
    col = ["Host", "FGSC", "Pub1"]
    data = pd.read_csv(os.path.join(tempory_directory, file), usecols=col)
    data["FGSC"] = data["FGSC"].apply(lambda x: x.replace("F.", "Fusarium"))
    data.columns = ["Host", "Pathogen", "Ref"]
    # get names
    data = add_taxonomy_info(data, "Pathogen", "sourceTaxId", "sourceName", uniprot)
    data = add_taxonomy_info(data, "Host", "targetTaxId", "targetName", uniprot)
    data["sourceUid"] = ""
    data["targetUid"] = ""
    # clean data
    data = clean_dataframe(data)
    # rename columns
    data = rename_subset_df(
        data,
        {
            "sourceTaxId": "sourceTaxId",
            "sourceName": "sourceName",
            "sourceUid": "sourceUid",
            "targetTaxId": "targetTaxId",
            "targetName": "targetName",
            "targetUid": "targetUid",
            # "interactionType": "interactionType",
            # "ontology": "ontology",
            "Ref": "reference",
            # "database": "database",
        },
    )
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_web_of_life_database(
    dir: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning raw data web of life"""
    references = pd.read_csv(os.path.join(tempory_directory, dir, "references.csv"))
    ref = []
    species_columns = ["Host", "Parasite"]
    species_pairs = []
    # go through files
    for file in os.listdir(os.path.join(tempory_directory, dir)):
        if file.startswith("A_HP"):
            data = pd.read_csv(
                os.path.join(tempory_directory, dir, file), on_bad_lines="skip"
            )
            for i, row in data.iterrows():
                for j, index in enumerate(row.index[1:]):
                    if j > 0 and row.iloc[j] > 0:
                        species_pairs.append([row["Unnamed: 0"], index])
                        ref.append(
                            references[references["ID"] == file.replace(".csv", "")][
                                "Reference"
                            ]
                        )
    data = pd.DataFrame(species_pairs, columns=species_columns).astype(str)
    data["reference"] = ref
    data["reference"] = data["reference"].apply(lambda x: str(x).replace("\n", ""))
    # Taxon IDs
    data = add_taxonomy_info(data, "Host", "targetTaxId", "targetName", uniprot)
    data = add_taxonomy_info(data, "Parasite", "sourceTaxId", "sourceName", uniprot)
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["interactionType"] = "parasiteHost"
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_hpidb(dir: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning raw data HPIDB"""
    # import data
    data = []
    for file in os.listdir(os.path.join(tempory_directory, dir)):
        if not file.endswith(".zip"):
            data.append(
                pd.read_csv(
                    os.path.join(tempory_directory, dir, file),
                    sep="\t",
                    usecols=[
                        "protein_taxid_1",
                        "# protein_xref_1",
                        "protein_taxid_2",
                        "protein_xref_2",
                        "interaction_type",
                        "pmid",
                    ],
                    encoding="unicode_escape",
                )
            )
    data = pd.concat(data)
    data = rename_subset_df(
        data,
        {
            "protein_taxid_1": "sourceTaxId",
            "# protein_xref_1": "sourceUid",
            "protein_taxid_2": "targetTaxId",
            "protein_xref_2": "targetUid",
            "interaction_type": "interactionType",
            "pmid": "reference",
        },
    )
    # data cleaning
    data["ontology"] = data["interactionType"].apply(lambda x: x.split("(")[0])
    data["interactionType"] = data["interactionType"].apply(
        lambda x: x.split("(")[-1][:-1]
    )
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    # clean TaxIds
    data["sourceTaxId"] = data["sourceTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    data["targetTaxId"] = data["targetTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    # clean result
    data = clean_dataframe(data)
    # get Scientific Name
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_intact(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning raw data from intact"""
    # import data
    col_mapping = {
        "Publication Identifier(s)": "reference",
        "#ID(s) interactor A": "sourceUid",
        "ID(s) interactor B": "targetUid",
        "Taxid interactor A": "sourceTaxId",
        "Taxid interactor B": "targetTaxId",
        "Interaction type(s)": "interactionType",
    }
    data = pd.read_csv(
        os.path.join(tempory_directory, file),
        sep="\t",
        usecols=list(col_mapping.keys()),
    )
    data = rename_subset_df(data, col_mapping)
    data["sourceUid"] = data["sourceUid"].apply(lambda x: x.replace("uniprotkb:", ""))
    data["targetUid"] = data["targetUid"].apply(lambda x: x.replace("uniprotkb:", ""))
    data["ontology"] = data["interactionType"].apply(
        lambda x: x.replace('"', "").split("(")[0]
    )
    data["interactionType"] = data["interactionType"].apply(
        lambda x: x.replace('"', "").split("(")[-1][:-1]
    )
    # clean TaxIds
    data["sourceTaxId"] = data["sourceTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    data["targetTaxId"] = data["targetTaxId"].apply(
        lambda x: x.replace("taxid:", "").split("(")[0]
    )
    # clean data
    data = clean_dataframe(data)
    data = data[(data["targetTaxId"] != "-") & (data["sourceTaxId"] != "-")]
    data = data[
        (data["targetTaxId"].astype(int) > 0) & (data["sourceTaxId"].astype(int) > 0)
    ]
    # Scientific names
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_iwdb(
    dir: str, name: str, tempory_directory: str, uniprot: uniprot_request
) -> None:
    """Cleaning raw data iwdb"""

    def get_pairs(frame: pd.DataFrame) -> list:
        pairs = []
        for r in range(1, frame.shape[0]):  # row index
            for c in range(r, frame.shape[1]):  # column index
                if is_float(frame.iloc[r, c]) and (frame.iloc[r, c] > 0):
                    a = frame.iloc[:, 0][r - 1]  # species a
                    b = frame.columns[1:][c - 1]  # species b
                    if not (is_float(a) or is_float(b)):
                        pairs.append([a, b])
        return pairs

    species_columns = ["Host", "Parasite"]
    species_pairs = []
    for file in os.listdir(os.path.join(tempory_directory, dir)):
        xls = pd.ExcelFile(os.path.join(tempory_directory, dir, file))
        if "prevalence" in xls.sheet_names:
            data = xls.parse("prevalence")
            # data = pd.read_excel(
            #     os.path.join(tempory_directory, dir, file), sheet_name="prevalence"
            # )
            parasite = (
                data.iloc[0, 4:]
                .reset_index()
                .groupby("index")
                .apply(lambda x: " ".join(x.values[0]))
                .reset_index()[0]
            )
            for row in data.iloc[2:, :].values:
                for col_number, p in enumerate(parasite):
                    if float(row[col_number + 4]) > 0:
                        species_pairs.append([row[0], p])
        else:
            species_pairs.extend(get_pairs(xls.parse()))
    data = pd.DataFrame(species_pairs, columns=species_columns)
    data.drop_duplicates()
    # clean names
    data["Parasite"] = data["Parasite"].apply(lambda x: x.replace("(L)", ""))
    data["Parasite"] = data["Parasite"].apply(lambda x: re.sub(".\d", "", x))
    # get TaxIds
    data = add_taxonomy_info(data, "Host", "targetTaxId", "targetName", uniprot)
    data = add_taxonomy_info(data, "Parasite", "sourceTaxId", "sourceName", uniprot)
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = ""  # TODO extract reference from file origin
    data["interactionType"] = ""  # TODO extract interactionType from file origin
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_phi_base(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
) -> None:
    """Cleaning raw data PHI base"""
    col = ["Pathogen ID", "Host ID", "PMID", "DOI", "Protein ID"]
    data = pd.read_csv(
        os.path.join(tempory_directory, file), header=1, usecols=col, dtype=str
    ).astype(str)
    # clean TaxId
    data = data[data["Host ID"].apply(lambda x: x.isdigit())]
    data = data[data["Pathogen ID"].apply(lambda x: x.isdigit())]
    data["reference"] = data[["PMID", "DOI"]].apply(
        lambda x: "|".join(x.values), axis=1
    )
    data = rename_subset_df(
        data,
        {
            "Pathogen ID": "sourceTaxId",
            "Protein ID": "sourceUid",
            "Host ID": "targetTaxId",
            "reference": "reference",
        },
    )
    data["targetUid"] = ""
    # clean data
    data = clean_dataframe(data)
    # Scientific names
    data = getSourceTargetNames(data, uniprot)
    # export
    data["interactionType"] = "pathogenHost"
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_philm2web(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning PHILM2Web (Pathogen-Host)"""
    data = pd.read_csv(os.path.join(tempory_directory, file))
    data = data[
        (data["HOST SPECIES"] != "host")
        & (data["HOST SPECIES ID"] > 0)
        & (data["PATHOGEN SPECIES ID"] > 0)
    ]
    # get species names
    data = rename_subset_df(
        data,
        {
            "HOST SPECIES ID": "sourceTaxId",
            "PATHOGEN SPECIES ID": "targetTaxId",
            "PUBMEDID": "reference",
            "INTERACTION KEYWORD(S)": "interactionType",
        },
    )
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    data = getSourceTargetNames(data, uniprot)
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_pida(file: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning raw data from pida"""
    data = pd.read_csv(
        os.path.join(tempory_directory, file), sep="\t", skiprows=2
    )  # TODO check header and direction
    # get TaxIds
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = " ".join(row[7:9].dropna().values)  # 7:9
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp)
            tax_ids.append(id)
            names.append(name_)
        else:
            tax_ids.append(None)
            names.append(None)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = " ".join(row[13:15].dropna().values)  # 13:15
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp)
            tax_ids.append(id)
            names.append(name_)
        else:
            tax_ids.append(None)
            names.append(None)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    data["interactionType"] = data["Ecological interaction"]
    data["sourceUid"] = ""
    data["targetUid"] = ""
    # clean data
    data = clean_dataframe(data)
    # export
    data["reference"] = data["Reference "]
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_virhostnet(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning raw data from VirHostNet"""
    data = pd.read_csv(
        os.path.join(tempory_directory, file), sep="\t", names=range(15)
    )[
        [0, 1, 8, 9, 10, 11]
    ]  # 8,9,10,11
    data.columns = [
        "targetUid",
        "sourceUid",
        "reference",
        "targetTaxId",
        "sourceTaxId",
        "interactionType",
    ]
    # clean TaxId
    data["targetUid"] = data["targetUid"].apply(
        lambda x: x.replace("uniprotkb:", "").split("-")[0]
    )
    data["sourceUid"] = data["sourceUid"].apply(
        lambda x: x.replace("uniprotkb:", "").split("-")[0]
    )
    data["sourceTaxId"] = data["sourceTaxId"].apply(lambda x: x.replace("taxid:", ""))
    data["targetTaxId"] = data["targetTaxId"].apply(lambda x: x.replace("taxid:", ""))
    data["ontology"] = data["interactionType"].apply(lambda x: x.split("(")[0])
    data["interactionType"] = data["interactionType"].apply(
        lambda x: x.split("(")[-1][:-1]
    )
    # cleaning data
    data = clean_dataframe(data)
    # Scientific names
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_eid2(file: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning EID2 (Publication)"""
    data = pd.read_csv(os.path.join(tempory_directory, file))
    # Name cleaning
    data["Cargo"] = data["Cargo"].apply(lambda x: x.replace("[", "").replace("]", ""))
    # Retrieve names and TaxIds
    data = add_taxonomy_info(data, "Cargo", "sourceTaxId", "sourceName", uniprot)
    data = add_taxonomy_info(data, "Carrier", "targetTaxId", "targetName", uniprot)
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = (
        data["Publications"].astype(str).apply(lambda x: "PMID:" + x if x != "" else "")
    )
    export_dataframe(
        data, name, tempory_directory, "tsv"
    )  # "https://doi.org/10.1038/sdata.2015.49"


def clean_siad(file: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning raw data from siad"""
    data = pd.read_csv(
        os.path.join(tempory_directory, file), sep="\t", index_col=6
    ).reset_index()
    # get names and TaxIds
    data = add_taxonomy_info(data, "name", "sourceTaxId", "sourceName", uniprot)
    data = add_taxonomy_info(data, "host name", "targetTaxId", "targetName", uniprot)
    # data formatting
    data = rename_subset_df(
        data,
        {
            "targetTaxId": "targetTaxId",
            "targetName": "targetName",
            "sourceTaxId": "sourceTaxId",
            "sourceName": "sourceName",
            "interaction": "interactionType",
            "source": "reference",
        },
    )
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_bateco_interactions(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning Bat Eco-Interactions"""
    data = pd.read_csv(os.path.join(tempory_directory, file))
    # TaxIds and Names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[:8].dropna().values  # 8
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name_)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[8:16].dropna().values  # 8
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name_)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = data["Citation"]
    data["interactionType"] = data["Type"]
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_gmpd(dir: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning Global mammal parasite database"""
    files = []
    for file in os.listdir(os.path.join(tempory_directory, dir)):
        if (
            "ungulates" in file or "carnivores" in file
        ):  # ParasiteReportedName ParasiteReportedName
            data = pd.read_csv(
                os.path.join(tempory_directory, dir, file), on_bad_lines="skip"
            ).astype(str)
            data = rename_subset_df(
                data,
                {
                    "ParasiteReportedName": "parasiteName1",
                    "ParasiteCorrectedName": "parasiteName2",
                    "HostReportedName": "hostName1",
                    "HostCorrectedName": "hostName2",
                    "ParType": "interactionType",
                    "Citation": "reference",
                },
            )
            data["hostName3"] = np.nan
        elif "primates" in file:
            data = pd.read_csv(
                os.path.join(tempory_directory, dir, file),
                index_col=0,
                on_bad_lines="skip",
            ).astype(str)
            data = rename_subset_df(
                data,
                {
                    "Parasite Reported Name": "parasiteName1",
                    "Parasite Corrected Name": "parasiteName2",
                    "Host Reported Name": "hostName1",
                    "Host Corrected Name C&H": "hostName2",
                    "Host Corrected Name W&R05": "hostName3",
                    "Parasite Type": "interactionType",
                    "Citation": "reference",
                },
            )
        files.append(data)
    data = pd.concat(files)
    # "Parasite Type", "Citation"
    # Get TaxIds and names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[["parasiteName1", "parasiteName2"]].dropna().values
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name_)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[["hostName1", "hostName2", "hostName3"]].dropna().values  #:2
        if len(name_tmp) != 0:
            name_, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name_)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_phisto(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning PHISTO"""
    data = pd.read_csv(os.path.join(tempory_directory, file), encoding="windows-1252")
    # get names
    data["Taxonomy ID 2"] = 9606
    data["Host"] = uniprot.tax_request(9606)
    data["Pathogen"] = data["Taxonomy ID"].apply(lambda x: uniprot.fast_tax_request(x))
    data = rename_subset_df(
        data,
        {
            "Host": "sourceName",
            "Human Protein": "sourceUid",
            "Pathogen": "targetName",
            "Pathogen Protein": "targetUid",
            "Taxonomy ID 2": "sourceTaxId",
            "Taxonomy ID": "targetTaxId",
            "Pubmed ID": "reference",
        },
    )
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    # clean data
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_mint(file: str, name: str, tempory_directory: str, uniprot: uniprot_request):
    """Cleaning mint database"""
    data = pd.read_csv(os.path.join(tempory_directory, file), sep="\t", names=range(15))
    data = data.loc[:, [0, 1, 8, 9, 10, 11]]
    data.columns = [
        "sourceUid",
        "targetUid",
        "reference",
        "sourceTaxId",
        "targetTaxId",
        "interactionType",
    ]
    data["sourceTaxId"] = data["sourceTaxId"].apply(
        lambda x: x.split("(")[0].replace("taxid:", "")
    )
    data["targetTaxId"] = data["targetTaxId"].apply(
        lambda x: x.split("(")[0].replace("taxid:", "")
    )
    data["sourceUid"] = data["sourceUid"].apply(lambda x: x.replace("uniprotkb:", ""))
    data["targetUid"] = data["targetUid"].apply(lambda x: x.replace("uniprotkb:", ""))
    data["ontology"] = data["interactionType"].apply(
        lambda x: x.replace('"', "").split("(")[0]
    )
    data["interactionType"] = data["interactionType"].apply(
        lambda x: x.replace('"', "").split("(")[-1][:-1]
    )
    # scientific names
    data = getSourceTargetNames(data, uniprot)
    # clean data
    data = clean_dataframe(data)
    data = data[(data["targetTaxId"] != "-") & (data["sourceTaxId"] != "-")]
    data = data[
        (data["sourceTaxId"].astype(int) > 0) & (data["targetTaxId"].astype(int) > 0)
    ]
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_pmc9897028(
    dir: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning a viral interactome (PMC9897028)"""
    data = pd.read_excel(
        os.path.join(tempory_directory, dir, "supplementary_table_S1.xls")
    ).astype(str)
    rows = []
    for i, row in data.iterrows():
        if len(row["Organism_Interactor_virus"].split(",")) > 1:
            values = row["Organism_Interactor_virus"].split(",")
            for v in values:
                new_row = row.copy()
                new_row["Organism_Interactor_virus"] = v
                rows.append(new_row)
        else:
            rows.append(row)
    data = pd.concat(rows, axis=1).T
    data = rename_subset_df(
        data,
        {
            "Organism_human": "targetName",
            "Organism_Interactor_human": "targetTaxId",
            "Uniprot_human": "targetUid",
            "Organism_virus": "sourceName",
            "Organism_Interactor_virus": "sourceTaxId",
            "Uniprot_virus": "sourceUid",
            "Interaction_Type": "interactionType",
            "Pubmed_ID": "reference",
        },
    )
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    data["sourceTaxId"] = data["sourceTaxId"].astype(int)
    # clean data
    data = clean_dataframe(data)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")


def clean_signor(
    file: str, name: str, tempory_directory: str, uniprot: uniprot_request
):
    """Cleaning signor"""
    data = pd.read_csv(os.path.join(tempory_directory, file), sep="\t")
    data = data[(data["DATABASEA"] == "UNIPROT") & (data["DATABASEB"] == "UNIPROT")]
    data["sourceTaxId"] = data["IDA"].apply(lambda x: get_taxonomic_identifier(x))
    data["targetTaxId"] = data["IDB"].apply(lambda x: get_taxonomic_identifier(x))
    data = rename_subset_df(
        data,
        {
            "IDA": "sourceUid",
            "sourceTaxId": "sourceTaxId",
            "IDB": "targetUid",
            "targetTaxId": "targetTaxId",
            "PMID": "reference",
            "MECHANISM": "interactionType",
        },
    )
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    # clean data
    data = clean_dataframe(data)
    # Scientific names
    data = getSourceTargetNames(data, uniprot)
    # export
    export_dataframe(data, name, tempory_directory, "tsv")
