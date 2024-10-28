"""
Script for processing data from each database. 

Please do not change code here.
Changes should only be done it file paths 
if users know what they are doing.
"""

import pandas as pd
import numpy as np
import re
import sys
import os
import requests

sys.path.insert(1, "./")
from uniprot_api import uniprot_request

global tempory_directory
if os.getenv("tempory_directory"):
    tempory_directory = os.getenv("tempory_directory")
    global overwrite
    overwrite = os.getenv("overwrite")
    if overwrite.lower() == "true":
        overwrite = True
    else:
        overwrite = False
else:
    print("Caution! Please check main/builtDB.sh")
    tempory_directory = "/mock/temp/dir"


def is_float(value: str) -> bool:
    """
    Check if string can be cast to float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def file_exists(path: str) -> None:
    """
    Checks if file path or path exists
    """
    if (not os.path.isdir(tempory_directory + path)) and (
        not os.path.exists(tempory_directory + path)
    ):
        raise ValueError(f"Provided input path '{path}' is not valid. Check download.")


def check_out_exists(name: str) -> bool:
    """
    Checks if processed data of a single database (_out file) exists
    """
    file_exists = any(
        [file.__contains__(name + "_out") for file in os.listdir(tempory_directory)]
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
    # TODO include same - same mappings
    # dataFrame = dataFrame[dataFrame["sourceTaxId"] != dataFrame["targetTaxId"]]
    dataFrame = (
        dataFrame.groupby(["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"])
        .agg(lambda x: join_unique(x))
        .reset_index()
    )
    # dataFrame = dataFrame.drop_duplicates(
    #     subset=["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]
    # )
    return dataFrame


def getSourceTargetNames(dataFrame: pd.DataFrame) -> pd.DataFrame:
    """
    Retrieves scientific names for source and target via their TaxId
    """
    uniprot = uniprot_request()
    # get Scientific Name
    dataFrame["sourceName"] = dataFrame["sourceTaxId"].apply(
        lambda x: uniprot.fast_tax_request(x)
    )
    dataFrame["targetName"] = dataFrame["targetTaxId"].apply(
        lambda x: uniprot.fast_tax_request(x)
    )
    return dataFrame


def get_taxonomic_identifier(uniprot_id):
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


def clean_bvbrc(prefix: str):
    """Cleaning raw data from BV-BRC"""
    frames = []
    col = ["NCBI Taxon ID", "Reference", "Publication", "Host Name"]
    for file in [
        "BVBRC_genome_bacteria.csv",
        "BVBRC_genome_archaea.csv",
        "BVBRC_genome_viruses.csv",
    ]:
        data = pd.read_csv(
            tempory_directory + prefix + "/" + file,
            usecols=col,
            dtype=str,
        ).astype(str)
        data = data[data["Host Name"].notna()]
        # TaxIds
        uniprot = uniprot_request()
        data["sourceName"] = data["NCBI Taxon ID"].apply(
            lambda x: uniprot.fast_tax_request(x)
        )
        # search uniprot
        data["Host Name"] = data["Host Name"].apply(
            lambda x: x.split(",")[1] if len(x.split(",")) > 1 else x
        )
        species = data["Host Name"].apply(lambda x: uniprot.fast_tax_name_request(x))
        data["targetName"] = list(map(lambda x: x[0], species))
        data["targetTaxId"] = list(map(lambda x: x[1], species))
        # clean data
        data["reference"] = data[["Reference", "Publication"]].apply(
            lambda x: "|".join(x.values), axis=1
        )
        data = data[
            ["NCBI Taxon ID", "sourceName", "reference", "targetName", "targetTaxId"]
        ]
        data.columns = [
            "sourceTaxId",
            "sourceName",
            "reference",
            "targetName",
            "targetTaxId",
        ]
        data["sourceUid"] = ""
        data["targetUid"] = ""
        data = clean_dataframe(data)
        frames.append(data)
    data = pd.concat(frames, axis=0, ignore_index=True)
    # clean
    data = clean_dataframe(data)
    # export
    data["interactionType"] = ""
    data["ontology"] = ""
    data["database"] = "BVBRC"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "bvbrc_out.csv", index=False)


def clean_globi(file: str = "/globi.tsv") -> None:
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
    slice = 5000000
    interaction_types = []
    out = []
    for i in range(2):
        if i + 1 % 2 == 0:
            data = pd.read_csv(
                tempory_directory + file,
                usecols=col,
                sep="\t",
                header=0,
                skiprows=range(1, slice + 1),
            )
        else:
            data = pd.read_csv(
                tempory_directory + "/globi.tsv",
                usecols=col,
                sep="\t",
                header=0,
                nrows=slice,
            )

        data["sourceUid"] = ""
        data["targetUid"] = ""
        data["database"] = "GloBI"
        data = data[
            [
                "sourceTaxonIds",
                "sourceTaxonName",
                "sourceUid",
                "targetTaxonIds",
                "targetTaxonName",
                "targetUid",
                "interactionTypeName",
                "interactionTypeId",
                "referenceDoi",
                "database",
            ]
        ].astype(str)
        data.columns = [
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
        data = getSourceTargetNames(data)
        out.append(data)
    data = pd.concat(out)
    # clean
    data = clean_dataframe(data)
    # export
    data.to_csv(tempory_directory + "/" + "globi_out.tsv", sep="\t", index=False)


def clean_biogrid(path: str):
    """Cleaning biogrid"""
    col = [
        "Taxid Interactor A",
        "Alt IDs Interactor A",  # uniprot/swiss-prot:
        "Taxid Interactor B",
        "Alt IDs Interactor B",
        "Interaction Types",  # Split
        "Publication Identifiers",
    ]
    file = os.listdir(tempory_directory + path)[0]
    data = pd.read_csv(
        tempory_directory + path + "/" + file,
        sep="\t",
        usecols=col,
    ).astype(str)
    data = data[col]
    data.columns = [
        "sourceTaxId",
        "sourceUid",
        "targetTaxId",
        "targetUid",
        "ontology",
        "reference",
    ]
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
    data = getSourceTargetNames(data)
    # export
    data["database"] = "BioGRID"
    data = data[
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
    data.to_csv(
        tempory_directory + "/" + "biogrid_latest_out.tsv", sep="\t", index=False
    )


def clean_DIP(prefix: str):
    """Cleaning raw data DIP"""  # TODO check direction source & target
    # import data
    path = tempory_directory + prefix
    data = []
    for file in os.listdir(path):
        if file.endswith(".txt"):
            tmp = pd.read_csv(
                path + "/" + file,
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
    data[
        [
            "Taxid interactor A",
            "ID interactor A",
            "Taxid interactor B",
            "ID interactor B",
            "Interaction type(s)",
            "Publication Identifier(s)",
        ]
    ]
    data.columns = [
        "sourceTaxId",
        "sourceUid",
        "targetTaxId",
        "targetUid",
        "interactionType",
        "reference",
    ]
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
    data = getSourceTargetNames(data)
    # export
    data["database"] = "DIP"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "dip_out.tsv", sep="\t", index=False)


def clean_fgscdb(file: str):
    """Cleaning raw data FGSCdb"""
    uniprot = uniprot_request()
    col = ["Host", "FGSC", "Pub1"]
    data = pd.read_csv(tempory_directory + file, usecols=col)
    data["FGSC"] = data["FGSC"].apply(lambda x: x.replace("F.", "Fusarium"))
    data.columns = ["Host", "Pathogen", "Ref"]
    # get names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Host"])
        tax_ids.append(id)
        names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Pathogen"])
        tax_ids.append(id)
        names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    data["sourceUid"] = ""
    data["targetUid"] = ""
    # clean data
    data = clean_dataframe(data)
    # export
    data["interactionType"] = ""
    data["database"] = "FGSCdb"
    data["ontology"] = ""
    data = data[
        [
            "sourceTaxId",
            "sourceName",
            "sourceUid",
            "targetTaxId",
            "targetName",
            "targetUid",
            "interactionType",
            "ontology",
            "Ref",
            "database",
        ]
    ]
    data.columns = [
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
    data.to_csv(tempory_directory + "/" + "fgscdb_out.tsv", sep="\t", index=False)


def clean_web_of_life(dir: str):
    """Cleaning raw data web of life"""
    uniprot = uniprot_request()
    path = tempory_directory + dir
    references = pd.read_csv(path + "/references.csv")
    ref = []
    species_columns = ["Host", "Parasite"]
    species_pairs = []
    # go through files
    for file in os.listdir(path):
        if file.startswith("A_HP"):
            data = pd.read_csv(path + "/" + file, on_bad_lines="skip")
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
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Host"])
        tax_ids.append(id)
        names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Parasite"])
        tax_ids.append(id)
        names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["interactionType"] = "parasiteHost"
    data["ontology"] = ""
    data["database"] = "Web of Life database"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "web_of_life_out.tsv", sep="\t", index=False)


def clean_HPIDB(dir: str = "/hpidb"):
    """Cleaning raw data HPIDB"""
    # import data
    path = tempory_directory + dir
    data = []
    for file in os.listdir(path):
        if not file.endswith(".zip"):
            data.append(
                pd.read_csv(
                    path + "/" + file,
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
    data = pd.concat(data)[
        [
            "protein_taxid_1",
            "# protein_xref_1",
            "protein_taxid_2",
            "protein_xref_2",
            "interaction_type",
            "pmid",
        ]
    ]
    data.columns = [
        "sourceTaxId",
        "sourceUid",
        "targetTaxId",
        "targetUid",
        "interactionType",
        "reference",
    ]
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
    data = getSourceTargetNames(data)
    # export
    data["database"] = "HPIDB"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "HPIDB_out.tsv", sep="\t", index=False)


def clean_intact(file: str = "/intact.txt"):
    """Cleaning raw data from intact"""
    # import data
    col = [
        "Publication Identifier(s)",
        "#ID(s) interactor A",
        "ID(s) interactor B",
        "Taxid interactor A",
        "Taxid interactor B",
        "Interaction type(s)",
    ]
    data = pd.read_csv(tempory_directory + file, sep="\t", usecols=col)
    data = data[col]
    data.columns = [
        "reference",
        "sourceUid",
        "targetUid",
        "sourceTaxId",
        "targetTaxId",
        "interactionType",
    ]
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
    data = getSourceTargetNames(data)
    # export
    data["database"] = "Intact"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "intact_out.tsv", sep="\t", index=False)


def clean_iwdb(dir: str = "/iwdb") -> None:
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

    path = tempory_directory + dir
    species_columns = ["Host", "Parasite"]
    species_pairs = []
    for file in os.listdir(path):
        xls = pd.ExcelFile(path + "/" + file)
        if "prevalence" in xls.sheet_names:
            data = pd.read_excel(path + "/" + file, sheet_name="prevalence")
            parasite = (
                data.iloc[0, 3:]
                .reset_index()
                .groupby("index")
                .apply(lambda x: " ".join(x.values[0]))
                .reset_index()[0]
            )
            for row in data.iloc[2:, :].values:
                for j, p in enumerate(parasite):
                    if j > 2 and int(row[j]) == 0:
                        species_pairs.append([row[0], p])
        else:
            species_pairs.extend(get_pairs(xls.parse()))
    data = pd.DataFrame(species_pairs, columns=species_columns)
    data.drop_duplicates()
    # clean names
    data["Parasite"] = data["Parasite"].apply(lambda x: x.replace("(L)", ""))
    data["Parasite"] = data["Parasite"].apply(lambda x: re.sub(".\d", "", x))
    # get TaxIds
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Parasite"])
        tax_ids.append(id)
        names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Host"])
        tax_ids.append(id)
        names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = ""  # TODO extract from file origin
    data["interactionType"] = ""  # TODO extract from file origin
    data["ontology"] = ""
    data["database"] = "IWDB"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "iwdb_out.tsv", sep="\t", index=False)


def clean_phi_base(file: str = "/phi_base.csv"):
    """Cleaning raw data PHI base"""
    col = ["Pathogen ID", "Host ID", "PMID", "DOI", "Protein ID"]
    data = pd.read_csv(
        tempory_directory + file, header=1, usecols=col, dtype=str
    ).astype(str)
    # clean TaxId
    data = data[data["Host ID"].apply(lambda x: x.isdigit())]
    data = data[data["Pathogen ID"].apply(lambda x: x.isdigit())]
    data["reference"] = data[["PMID", "DOI"]].apply(
        lambda x: "|".join(x.values), axis=1
    )
    data = data[["Pathogen ID", "Protein ID", "Host ID", "reference"]]
    data.columns = ["sourceTaxId", "sourceUid", "targetTaxId", "reference"]
    data["targetUid"] = ""
    # clean data
    data = clean_dataframe(data)
    # Scientific names
    data = getSourceTargetNames(data)
    # export
    data["interactionType"] = "pathogenHost"
    data["ontology"] = ""
    data["database"] = "PHI-base"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "phi_base_out.tsv", sep="\t", index=False)


def clean_PHILM2Web(file: str):
    """Cleaning PHILM2Web (Pathogen-Host)"""
    data = pd.read_csv(tempory_directory + file)
    data = data[
        (data["HOST SPECIES"] != "host")
        & (data["HOST SPECIES ID"] > 0)
        & (data["PATHOGEN SPECIES ID"] > 0)
    ]
    # get species names
    data = data[
        ["HOST SPECIES ID", "PATHOGEN SPECIES ID", "PUBMEDID", "INTERACTION KEYWORD(S)"]
    ]
    data.columns = [
        "sourceTaxId",
        "targetTaxId",
        "reference",
        "interactionType",
    ]
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    data = getSourceTargetNames(data)
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["ontology"] = ""
    data["database"] = "PHILM2Web"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "philm2web_out.tsv", sep="\t", index=False)


def clean_pida(file: str = "/pida.tsv"):
    """Cleaning raw data from pida"""
    data = pd.read_csv(
        tempory_directory + file, sep="\t", skiprows=2
    )  # TODO check header and direction
    # get TaxIds
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = " ".join(row[7:9].dropna().values)  # 7:9
        if len(name_tmp) != 0:
            name, id = uniprot.fast_tax_name_request(name_tmp)
            tax_ids.append(id)
            names.append(name)
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
            name, id = uniprot.fast_tax_name_request(name_tmp)
            tax_ids.append(id)
            names.append(name)
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
    data["ontology"] = ""
    data["database"] = "pida"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "pida_out.tsv", sep="\t", index=False)


def clean_virHostNet(file: str = "/vir_host_net.tsv"):
    """Cleaning raw data from VirHostNet"""
    data = pd.read_csv(tempory_directory + file, sep="\t", names=range(15))[
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
    data = getSourceTargetNames(data)
    # export
    data["database"] = "VirHostNet"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "vir_host_net_out.tsv", sep="\t", index=False)


def clean_eid2(file: str = "/eid2.csv"):
    """Cleaning EID2 (Publication)"""
    data = pd.read_csv(tempory_directory + file)
    # Name cleaning
    data["Cargo"] = data["Cargo"].apply(lambda x: x.replace("[", "").replace("]", ""))
    # Retrieve names and TaxIds
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Cargo"])
        tax_ids.append(id)
        names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["Carrier"])
        tax_ids.append(id)
        names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = (
        data["Publications"].astype(str).apply(lambda x: "PMID:" + x if x != "" else "")
    )
    data["database"] = "EID2"  # "https://doi.org/10.1038/sdata.2015.49"
    data["interactionType"] = ""
    data["ontology"] = ""
    data = data[
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
    data.to_csv(tempory_directory + "/" + "eid2_out.tsv", sep="\t", index=False)


def clean_siad(file: str = "/siad.txt"):
    """Cleaning raw data from siad"""
    data = pd.read_csv(tempory_directory + file, sep="\t", index_col=6).reset_index()
    # get names and TaxIds
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["name"])
        tax_ids.append(id)
        names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name, id = uniprot.fast_tax_name_request(row["host name"])
        tax_ids.append(id)
        names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # data formatting
    data = data[
        [
            "targetTaxId",
            "targetName",
            "sourceTaxId",
            "sourceName",
            "interaction",
            "source",
        ]
    ]
    data.columns = [
        "targetTaxId",
        "targetName",
        "sourceTaxId",
        "sourceName",
        "interactionType",
        "reference",
    ]
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["ontology"] = ""
    data["database"] = "Siad"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "siad_out.tsv", sep="\t", index=False)


def clean_bat_eco(file: str):
    """Cleaning Bat Eco-Interactions"""
    data = pd.read_csv(tempory_directory + file)
    # TaxIds and Names
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[:8].dropna().values  # 8
        if len(name_tmp) != 0:
            name, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[8:16].dropna().values  # 8
        if len(name_tmp) != 0:
            name, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["reference"] = data["Citation"]
    data["interactionType"] = data["Type"]
    data["ontology"] = ""
    data["database"] = "BatEco-Interactions"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "bat_eco_out.tsv", sep="\t", index=False)


def clean_gmpd(dir: str):
    """Cleaning Global mammal parasite database"""
    files = []
    for file in os.listdir(tempory_directory + dir):
        if (
            "ungulates" in file or "carnivores" in file
        ):  # ParasiteReportedName ParasiteReportedName
            data = pd.read_csv(
                tempory_directory + dir + "/" + file, on_bad_lines="skip"
            ).astype(str)
            data = data[
                [
                    "ParasiteReportedName",
                    "ParasiteCorrectedName",
                    "HostReportedName",
                    "HostCorrectedName",
                    "ParType",
                    "Citation",
                ]
            ]
            data.columns = [
                "parasiteName1",
                "parasiteName2",
                "hostName1",
                "hostName2",
                "interactionType",
                "reference",
            ]
            data["hostName3"] = np.nan
        elif "primates" in file:
            data = pd.read_csv(
                tempory_directory + dir + "/" + file, index_col=0, on_bad_lines="skip"
            ).astype(str)
            data = data[
                [
                    "Parasite Reported Name",
                    "Parasite Corrected Name",
                    "Host Reported Name",
                    "Host Corrected Name C&H",
                    "Host Corrected Name W&R05",
                    "Parasite Type",
                    "Citation",
                ]
            ]
            data.columns = [
                "parasiteName1",
                "parasiteName2",
                "hostName1",
                "hostName2",
                "hostName3",
                "interactionType",
                "reference",
            ]
        files.append(data)
    data = pd.concat(files)
    # "Parasite Type", "Citation"
    # Get TaxIds and names
    uniprot = uniprot_request()
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[["parasiteName1", "parasiteName2"]].dropna().values
        if len(name_tmp) != 0:
            name, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name)
    data["sourceTaxId"] = tax_ids
    data["sourceName"] = names
    tax_ids = []
    names = []
    for i, row in data.iterrows():
        print(i, end="\r")
        name_tmp = row[["hostName1", "hostName2", "hostName3"]].dropna().values  #:2
        if len(name_tmp) != 0:
            name, id = uniprot.fast_tax_name_request(name_tmp[-1])
            tax_ids.append(id)
            names.append(name)
    data["targetTaxId"] = tax_ids
    data["targetName"] = names
    # clean data
    data["sourceUid"] = ""
    data["targetUid"] = ""
    data = clean_dataframe(data)
    # export
    data["ontology"] = ""
    data["database"] = "GMPD"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "gmpd_out.tsv", sep="\t", index=False)


def clean_phisto(file: str):
    """Cleaning PHISTO"""
    uniprot = uniprot_request()
    data = pd.read_csv(tempory_directory + file, encoding="windows-1252")
    # get names
    data["Taxonomy ID 2"] = 9606
    data["Host"] = uniprot.tax_request(9606)
    data["Pathogen"] = data["Taxonomy ID"].apply(lambda x: uniprot.fast_tax_request(x))
    data = data[
        [
            "Host",
            "Human Protein",
            "Pathogen",
            "Pathogen Protein",
            "Taxonomy ID 2",
            "Taxonomy ID",
            "Pubmed ID",
        ]
    ]
    data.columns = [
        "sourceName",
        "sourceUid",
        "targetName",
        "targetUid",
        "sourceTaxId",
        "targetTaxId",
        "reference",
    ]
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    # clean data
    data = clean_dataframe(data)
    # export
    data["interactionType"] = ""
    data["ontology"] = ""
    data["database"] = "PHISTO"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "phisto_out.tsv", sep="\t", index=False)


def clean_mint(file: str = "/mint.tsv"):
    """Cleaning mint database"""
    data = pd.read_csv(tempory_directory + file, sep="\t", names=range(15))
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
    data = getSourceTargetNames(data)
    # clean data
    data = clean_dataframe(data)
    data = data[(data["targetTaxId"] != "-") & (data["sourceTaxId"] != "-")]
    data = data[
        (data["sourceTaxId"].astype(int) > 0) & (data["targetTaxId"].astype(int) > 0)
    ]
    # export
    data["database"] = "mint"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "mint_out.tsv", sep="\t", index=False)


def clean_interactome(dir: str = "/viral_interactome"):
    """Cleaning a viral interactome (PMC9897028)"""
    data = pd.read_excel(
        tempory_directory + dir + "/supplementary_table_S1.xls"
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
    data = data[
        [
            "Organism_human",
            "Organism_Interactor_human",
            "Uniprot_human",
            "Organism_virus",
            "Organism_Interactor_virus",
            "Uniprot_virus",
            "Interaction_Type",
            "Pubmed_ID",
        ]
    ]
    data.columns = [
        "targetName",
        "targetTaxId",
        "targetUid",
        "sourceName",
        "sourceTaxId",
        "sourceUid",
        "interactionType",
        "reference",
    ]
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    data["sourceTaxId"] = data["sourceTaxId"].astype(int)
    # clean data
    data = clean_dataframe(data)
    # export
    data["ontology"] = ""
    data["database"] = "PMC9897028"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "interactome_out.tsv", sep="\t", index=False)


def clean_signor(file: str = "/signor.tsv"):
    """Cleaning signor"""
    data = pd.read_csv(tempory_directory + "/signor.tsv", sep="\t")
    data = data[(data["DATABASEA"] == "UNIPROT") & (data["DATABASEB"] == "UNIPROT")]
    data["sourceTaxId"] = data["IDA"].apply(lambda x: get_taxonomic_identifier(x))
    data["targetTaxId"] = data["IDB"].apply(lambda x: get_taxonomic_identifier(x))
    data = data[["IDA", "sourceTaxId", "IDB", "targetTaxId", "PMID", "MECHANISM"]]
    data.columns = [
        "sourceUid",
        "sourceTaxId",
        "targetUid",
        "targetTaxId",
        "reference",
        "interactionType",
    ]
    data["reference"] = data["reference"].astype(str).apply(lambda x: "PMID:" + x)
    # clean data
    data = clean_dataframe(data)
    # Scientific names
    data = getSourceTargetNames(data)
    # export
    data["ontology"] = ""
    data["database"] = "Signor"
    data = data[
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
    data.to_csv(tempory_directory + "/" + "signor_out.tsv", sep="\t", index=False)


def main():
    print("### Processing data ###")
    exceptions = []

    try:
        file_exists("/bvbrc")
        print("bvbrc")
        if not check_out_exists("bvbrc") or overwrite:
            clean_bvbrc("/bvbrc")
    except Exception as e:
        exceptions.append(str(e) + "\nbvbrc")

    try:
        file_exists("/biogrid_all_latest")
        print("biogrid")
        if not check_out_exists("biogrid_latest") or overwrite:
            clean_biogrid("/biogrid_all_latest")
    except Exception as e:
        exceptions.append(str(e) + "\nbiogrid")

    try:
        file_exists("/dip")
        print("dip")
        if not check_out_exists("dip") or overwrite:
            clean_DIP("/dip")
    except Exception as e:
        exceptions.append(str(e) + "\ndip")

    try:
        file_exists("/FGSCdb_data.csv")
        print("fgscdb")
        if not check_out_exists("fgscdb") or overwrite:
            clean_fgscdb("/FGSCdb_data.csv")
    except Exception as e:
        exceptions.append(str(e) + "\nfgscdb")

    try:
        file_exists("/web_of_life")
        print("web of life")
        if not check_out_exists("web_of_life") or overwrite:
            clean_web_of_life("/web_of_life")
    except Exception as e:
        exceptions.append(str(e) + "\nwol")

    try:
        file_exists("/globi.tsv")
        print("globi")
        if not check_out_exists("globi") or overwrite:
            clean_globi()
    except Exception as e:
        exceptions.append(str(e) + "\nglobi")

    try:
        file_exists("/hpidb")
        print("hpidb")
        if not check_out_exists("HPIDB") or overwrite:
            clean_HPIDB()
    except Exception as e:
        exceptions.append(str(e) + "\nhpidb")

    try:
        file_exists("/intact.txt")
        print("intact")
        if not check_out_exists("intact") or overwrite:
            clean_intact()
    except Exception as e:
        exceptions.append(str(e) + "\nintact")

    try:
        file_exists("/iwdb")
        print("iwdb")
        if not check_out_exists("iwdb") or overwrite:
            clean_iwdb()
    except Exception as e:
        exceptions.append(str(e) + "\niwdb")

    try:
        file_exists("/phi_base.csv")
        print("phi-base")
        if not check_out_exists("phi_base") or overwrite:
            clean_phi_base()
    except Exception as e:
        exceptions.append(str(e) + "\nphi_base")

    try:
        file_exists("/philm2web.csv")
        print("philm2web")
        if not check_out_exists("philm2web") or overwrite:
            clean_PHILM2Web("/philm2web.csv")
    except Exception as e:
        exceptions.append(str(e) + "\nphilm2web")

    try:
        file_exists("/pida.tsv")
        print("pida")
        if not check_out_exists("pida") or overwrite:
            clean_pida()
    except Exception as e:
        exceptions.append(str(e) + "\npida")

    try:
        file_exists("/vir_host_net.tsv")
        print("virhostnet")
        if not check_out_exists("vir_host_net") or overwrite:
            clean_virHostNet()
    except Exception as e:
        exceptions.append(str(e) + "\nvirhostnet")

    try:
        file_exists("/eid2.csv")
        print("eid2")
        if not check_out_exists("eid2") or overwrite:
            clean_eid2()
    except Exception as e:
        exceptions.append(str(e) + "\neid2")

    try:
        file_exists("/siad.txt")
        print("siad")
        if not check_out_exists("siad") or overwrite:
            clean_siad()
    except Exception as e:
        exceptions.append(str(e) + "\nSiad")

    try:
        file_exists("/BatEco-InteractionRecords.csv")
        print("BatEco")
        if not check_out_exists("bat_eco") or overwrite:
            clean_bat_eco("/BatEco-InteractionRecords.csv")
    except Exception as e:
        exceptions.append(str(e) + "\nBatEco")

    try:
        file_exists("/gmpd")
        print("gmpd")
        if not check_out_exists("gmpd") or overwrite:
            clean_gmpd("/gmpd")
    except Exception as e:
        exceptions.append(str(e) + "\ngmpd")

    try:
        file_exists("/phisto_data.csv")
        print("phisto")
        if not check_out_exists("phisto") or overwrite:
            clean_phisto("/phisto_data.csv")
    except Exception as e:
        exceptions.append(str(e))

    try:
        file_exists("/mint.tsv")
        print("mint")
        if not check_out_exists("mint") or overwrite:
            clean_mint()
    except Exception as e:
        exceptions.append(str(e) + "\nmint")

    try:
        file_exists("/viral_interactome")
        print("interactome")
        if not check_out_exists("interactome") or overwrite:
            clean_interactome()
    except Exception as e:
        exceptions.append(str(e) + "\nvir interactome")

    try:
        file_exists("/signor.tsv")
        print("signor")
        if not check_out_exists("signor") or overwrite:
            clean_signor()
    except Exception as e:
        exceptions.append(str(e) + "\nsignor")

    if exceptions:
        with open("stderr.txt", "w") as f:
            f.write("\n".join(exceptions))


if __name__ == "__main__":
    main()
