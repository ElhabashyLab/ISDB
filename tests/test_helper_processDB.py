import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys

sys.path.insert(1, "../utils")
from uniprot_api import uniprot_request
from helper import *
from helper_processDB import *


class TestCleaners(unittest.TestCase):
    def setUp(self):
        # Shared mock for uniprot_request
        self.mock_uniprot = MagicMock()
        self.mock_uniprot.fast_tax_request.side_effect = lambda x: f"name_{x}"
        self.mock_uniprot.fast_tax_name_request.side_effect = lambda x: (
            f"name_{x}",
            f"id_{x}",
        )

    # -------------------------
    # BV-BRC test (example already)
    # -------------------------
    @patch("os.listdir")
    @patch("pandas.read_csv")
    @patch("helper_processDB.export_dataframe")
    def test_clean_bvbrc(self, mock_export, mock_read_csv, mock_listdir):
        sample_df = pd.DataFrame(
            {
                "NCBI Taxon ID": ["9606", "10090"],
                "Reference": ["ref1", "ref2"],
                "Publication": ["pub1", "pub2"],
                "Host Name": ["Homo sapiens", "Mus musculus"],
            }
        )
        mock_listdir.return_value = ["file1.csv"]
        mock_read_csv.return_value = sample_df

        clean_bvbrc("prefix", "BV_BRC", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called()
        mock_export.assert_called_once()
        df_passed = mock_export.call_args[0][0]
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceName", df_passed.columns)
        self.assertIn("targetName", df_passed.columns)

    # -------------------------
    # GloBI test
    # -------------------------
    @patch("pandas.read_csv")
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    def test_clean_globi(self, mock_get_names, mock_export, mock_read_csv):
        df_chunk = pd.DataFrame(
            {
                "sourceTaxonName": ["A", "B"],
                "sourceTaxonIds": ["NCBI:9606", "NCBI:10090"],
                "interactionTypeName": ["interact1", "interact2"],
                "interactionTypeId": ["ont1", "ont2"],
                "targetTaxonName": ["C", "D"],
                "targetTaxonIds": ["NCBI:10116", "NCBI:10117"],
                "referenceDoi": ["doi1", "doi2"],
            }
        )
        mock_read_csv.return_value = [df_chunk]  # simulate iterator
        mock_get_names.side_effect = lambda x: x

        clean_globi("file1.tsv", "GloBI", "/tmp", self.mock_uniprot)

        mock_export.assert_called_once()

    # -------------------------
    # Biogrid test
    # -------------------------
    @patch("os.listdir")
    @patch("pandas.read_csv")
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    def test_clean_biogrid(
        self, mock_get_names, mock_export, mock_read_csv, mock_listdir
    ):
        mock_listdir.return_value = ["file.tsv"]
        df = pd.DataFrame(
            {
                "Taxid Interactor A": ["taxid:9606"],
                "Alt IDs Interactor A": ["P12345"],
                "Taxid Interactor B": ["taxid:10090"],
                "Alt IDs Interactor B": ["Q67890"],
                "Interaction Types": ["binding(interact)"],
                "Publication Identifiers": ["PMID:123"],
            }
        )
        mock_read_csv.return_value = df
        mock_get_names.side_effect = lambda x: x

        clean_biogrid("path", "BioGRID", "/tmp", self.mock_uniprot)

        mock_export.assert_called_once()
        df_passed = mock_export.call_args[0][0]
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)

    # -------------------------
    # DIP test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("pandas.read_csv")
    @patch("os.listdir")
    def test_clean_dip(self, mock_listdir, mock_read_csv, mock_get_names, mock_export):
        # Mock filesystem
        mock_listdir.return_value = ["test.txt"]  # must end with .txt

        # Mock raw DIP dataframe
        df = pd.DataFrame(
            {
                "Taxid interactor A": ["taxid:9606(human)"],
                "ID interactor A": ["uniprotkb:P12345|something"],
                "Taxid interactor B": ["taxid:10090(mouse)"],
                "ID interactor B": ["uniprotkb:Q67890|something"],
                "Interaction type(s)": ["physical association(binding)"],
                "Publication Identifier(s)": ["PMID:12345"],
            }
        )

        # read_csv returns df → reset_index() is called in function
        mock_read_csv.return_value = df

        # getSourceTargetNames should just return dataframe unchanged
        mock_get_names.side_effect = lambda x: x

        # Run function
        clean_dip("dip_folder", "DIP", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        mock_export.assert_called_once()

        # Get dataframe passed to export
        df_passed = mock_export.call_args[0][0]

        # Check important columns exist
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("ontology", df_passed.columns)

        # Check transformations worked
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "10090")
        self.assertEqual(df_passed["sourceUid"].iloc[0], "P12345")
        self.assertEqual(df_passed["targetUid"].iloc[0], "Q67890")
        self.assertEqual(df_passed["ontology"].iloc[0], "physical association")
        self.assertEqual(df_passed["interactionType"].iloc[0], "binding")

    # -------------------------
    # FSCdb test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.add_taxonomy_info")
    @patch("pandas.read_csv")
    def test_clean_fgscdb(
        self,
        mock_read_csv,
        mock_add_tax,
        mock_clean_df,
        mock_rename,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "Host": ["Homo sapiens"],
                "FGSC": ["F.graminearum"],
                "Pub1": ["PMID:123"],
            }
        )
        mock_read_csv.return_value = df

        def add_tax_side_effect(data, query_col, tax_col, name_col, uniprot):
            data[tax_col] = ["123"]
            data[name_col] = ["mock_name"]
            return data

        mock_add_tax.side_effect = add_tax_side_effect
        mock_clean_df.side_effect = lambda x: x
        mock_rename.side_effect = lambda df, mapping: df

        clean_fgscdb("file.csv", "FGSCdb", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        self.assertEqual(mock_add_tax.call_count, 2)
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceName", df_passed.columns)
        self.assertIn("targetName", df_passed.columns)
        self.assertIn("Fusarium", df_passed["Pathogen"].iloc[0])

    # -------------------------
    # Web of Life Database test
    # -------------------------
    @patch("os.listdir")
    @patch("pandas.read_csv")
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.add_taxonomy_info")
    def test_clean_web_of_life_database(
        self,
        mock_add_tax,
        mock_clean_df,
        mock_export,
        mock_read_csv,
        mock_listdir,
    ):
        references_df = pd.DataFrame(
            {
                "ID": ["A_HP_test"],
                "Reference": ["ref123"],
            }
        )

        interaction_df = pd.DataFrame(
            {
                "Unnamed: 0": ["HostA"],
                "Parasite1": [1],
                "Parasite2": [0],
            }
        )

        mock_read_csv.side_effect = [references_df, interaction_df]
        mock_listdir.return_value = ["A_HP_test.csv"]

        def add_tax_side_effect(data, query_col, tax_col, name_col, uniprot):
            data[tax_col] = ["123"] * len(data)
            data[name_col] = ["mock_name"] * len(data)
            return data

        mock_add_tax.side_effect = add_tax_side_effect
        mock_clean_df.side_effect = lambda x: x

        clean_web_of_life_database("dir", "WebOfLifeDB", "/tmp", self.mock_uniprot)

        self.assertEqual(mock_add_tax.call_count, 2)
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertEqual(df_passed["interactionType"].iloc[0], "parasiteHost")

    # -------------------------
    # HPIDB test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("pandas.read_csv")
    @patch("os.listdir")
    def test_clean_hpidb(
        self,
        mock_listdir,
        mock_read_csv,
        mock_rename,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "protein_taxid_1": ["taxid:9606(human)"],
                "# protein_xref_1": ["uniprotkb:P12345"],
                "protein_taxid_2": ["taxid:10090(mouse)"],
                "protein_xref_2": ["uniprotkb:Q67890"],
                "interaction_type": ["binding(interaction)"],
                "pmid": ["123456"],
            }
        )

        mock_listdir.return_value = ["file1.txt", "file2.zip"]  # zip should be ignored
        mock_read_csv.return_value = df

        mock_rename.side_effect = lambda df, mapping: df.rename(columns=mapping)
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_hpidb("dir", "HPIDB", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_rename.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_get_names.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("ontology", df_passed.columns)
        self.assertIn("reference", df_passed.columns)

        # Check transformations
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "10090")
        self.assertEqual(df_passed["reference"].iloc[0], "PMID:123456")
        self.assertEqual(df_passed["ontology"].iloc[0], "binding")
        self.assertEqual(df_passed["interactionType"].iloc[0], "interaction")

    # -------------------------
    # IntAct test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("pandas.read_csv")
    def test_clean_intact(
        self,
        mock_read_csv,
        mock_rename,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "Publication Identifier(s)": ["PMID:123"],
                "#ID(s) interactor A": ["uniprotkb:P12345"],
                "ID(s) interactor B": ["uniprotkb:Q67890"],
                "Taxid interactor A": ["taxid:9606(human)"],
                "Taxid interactor B": ["taxid:10090(mouse)"],
                "Interaction type(s)": ['"binding(interaction)"'],
            }
        )

        mock_read_csv.return_value = df
        mock_rename.side_effect = lambda df, mapping: df.rename(columns=mapping)
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_intact("file.tsv", "IntAct", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_rename.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_get_names.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Column checks
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("ontology", df_passed.columns)

        # Value checks
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "10090")
        self.assertEqual(df_passed["sourceUid"].iloc[0], "P12345")
        self.assertEqual(df_passed["targetUid"].iloc[0], "Q67890")
        self.assertEqual(df_passed["ontology"].iloc[0], "binding")
        self.assertEqual(df_passed["interactionType"].iloc[0], "interaction")

    # -------------------------


# IWDB test
# -------------------------
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from helper_processDB import clean_iwdb


class TestIWDBCleaner(unittest.TestCase):
    def setUp(self):
        # Mock uniprot
        self.mock_uniprot = MagicMock()
        self.mock_uniprot.fast_tax_name_request.side_effect = lambda x: (
            f"name_{x}",
            f"id_{x}",
        )

    @patch("os.listdir")
    @patch("pandas.ExcelFile")
    @patch("pandas.read_excel")
    @patch("helper_processDB.add_taxonomy_info")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.export_dataframe")
    def test_clean_iwdb(
        self,
        mock_export,
        mock_clean_df,
        mock_add_tax,
        mock_read_excel,
        mock_excel_file,
        mock_listdir,
    ):
        # Setup mock directory listing
        mock_listdir.return_value = ["file1.xlsx"]

        # Mock ExcelFile object
        mock_xls = MagicMock()
        mock_xls.sheet_names = ["prevalence"]
        mock_xls.parse.return_value = pd.DataFrame(
            [
                ["h", "b", "c", "d", "sapiens", "Micky"],
                ["count", 0, 0, 0, 4, 4],
                ["Sp A", 0, 0, 0, 1, 0],
                ["Sp B", 0, 0, 0, 0, 1],
            ],
            columns=["x", "y", "z", "a", "Homo", "Mouse"],
        )
        mock_excel_file.return_value = mock_xls

        # Mock read_excel for prevalence sheet (simulate it does not exist here)
        mock_read_excel.return_value = pd.DataFrame()

        # Mock add_taxonomy_info to just add ID and name columns
        def add_tax_side_effect(df, col, tax_col, name_col, uniprot):
            df[tax_col] = ["id_mock"] * len(df)
            df[name_col] = ["name_mock"] * len(df)
            return df

        mock_add_tax.side_effect = add_tax_side_effect
        mock_clean_df.side_effect = lambda df: df

        # Call function
        clean_iwdb("mock_dir", "IWDB", "/tmp", self.mock_uniprot)

        # Assertions
        mock_listdir.assert_called_once()
        mock_excel_file.assert_called_once()
        mock_add_tax.assert_called()  # called for Host and Parasite
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        # Check dataframe passed to export
        df_passed = mock_export.call_args[0][0]
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceName", df_passed.columns)
        self.assertIn("targetName", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("reference", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)

        self.assertEqual(df_passed.loc[0, "Host"], "Sp A")
        self.assertEqual(df_passed.loc[1, "Parasite"], "Mouse Micky")

    # -------------------------
    # PHI-base test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("pandas.read_csv")
    def test_clean_phi_base(
        self,
        mock_read_csv,
        mock_rename,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "Pathogen ID": ["1234", "not_valid"],
                "Host ID": ["5678", "abcd"],
                "PMID": ["111", "222"],
                "DOI": ["doi1", "doi2"],
                "Protein ID": ["P12345", "Q67890"],
            }
        )

        mock_read_csv.return_value = df
        mock_rename.side_effect = lambda df, mapping: df.rename(columns=mapping)
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_phi_base("file.csv", "PHIbase", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_rename.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_get_names.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Column checks
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("reference", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)

        # Filtering check (only valid numeric IDs should remain)
        self.assertEqual(len(df_passed), 1)

        # Value checks
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "1234")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "5678")
        self.assertEqual(df_passed["reference"].iloc[0], "111|doi1")
        self.assertEqual(df_passed["interactionType"].iloc[0], "pathogenHost")

    # -------------------------
    # PHI-base test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("pandas.read_csv")
    def test_clean_phi_base(
        self,
        mock_read_csv,
        mock_rename,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "Pathogen ID": ["1234", "not_valid"],
                "Host ID": ["5678", "abcd"],
                "PMID": ["111", "222"],
                "DOI": ["doi1", "doi2"],
                "Protein ID": ["P12345", "Q67890"],
            }
        )

        mock_read_csv.return_value = df
        mock_rename.side_effect = lambda df, mapping: df.rename(columns=mapping)
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_phi_base("file.csv", "PHIbase", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_rename.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_get_names.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Column checks
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("reference", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)

        # Filtering check (only valid numeric IDs should remain)
        self.assertEqual(len(df_passed), 1)

        # Value checks
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "1234")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "5678")
        self.assertEqual(df_passed["reference"].iloc[0], "111|doi1")
        self.assertEqual(df_passed["interactionType"].iloc[0], "pathogenHost")

    # -------------------------
    # PHILM2Web test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.rename_subset_df")
    @patch("pandas.read_csv")
    def test_clean_philm2web(
        self,
        mock_read_csv,
        mock_rename,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "HOST SPECIES": ["Homo sapiens", "host"],
                "HOST SPECIES ID": [9606, -1],
                "PATHOGEN SPECIES ID": [1234, 0],
                "PUBMEDID": ["111", "222"],
                "INTERACTION KEYWORD(S)": ["binding", "infection"],
            }
        )

        mock_read_csv.return_value = df
        mock_rename.side_effect = lambda df, mapping: df.rename(columns=mapping)
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_philm2web("file.csv", "PHILM2Web", "/tmp", self.mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_rename.assert_called_once()
        mock_get_names.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Column checks
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("reference", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)

        # Filtering check (only valid row remains)
        self.assertEqual(len(df_passed), 1)

        # Value checks
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], 9606)
        self.assertEqual(df_passed["targetTaxId"].iloc[0], 1234)
        self.assertEqual(df_passed["reference"].iloc[0], "PMID:111")

        # Ensure UID columns were added
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)

    # -------------------------
    # PIDA test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("pandas.read_csv")
    def test_clean_pida(self, mock_read_csv, mock_clean_df, mock_export):
        # Sample data
        df = pd.DataFrame(
            {
                "0": ["", ""],
                "1": ["", ""],
                "2": ["", ""],
                "3": ["", ""],
                "4": ["", ""],
                "5": ["", ""],
                "6": ["", ""],
                "Column7": ["Homo", "Mus"],
                "Column8": ["sapiens", "musculus"],
                "9": ["", ""],
                "10": ["", ""],
                "11": ["", ""],
                "12": ["", ""],
                "Column13": ["Fusarium", "Aspergillus"],
                "Column14": ["graminearum", "niger"],
                "Ecological interaction": ["parasitism", "mutualism"],
                "Reference ": ["ref1", "ref2"],
            }
        )
        mock_read_csv.return_value = df
        mock_clean_df.side_effect = lambda x: x
        mock_export.side_effect = lambda *args, **kwargs: None

        # Mock uniprot
        class MockUniProt:
            def fast_tax_name_request(self, name):
                return f"name_{name}", f"id_{name}"

        mock_uniprot = MockUniProt()

        clean_pida("file.csv", "PIDA", "/tmp", mock_uniprot)

        mock_read_csv.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Column checks
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceName", df_passed.columns)
        self.assertIn("targetName", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("reference", df_passed.columns)

        # Value checks for mocked uniprot
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "id_Homo sapiens")
        self.assertEqual(df_passed["sourceName"].iloc[0], "name_Homo sapiens")
        self.assertEqual(df_passed["targetTaxId"].iloc[1], "id_Aspergillus niger")
        self.assertEqual(df_passed["targetName"].iloc[1], "name_Aspergillus niger")
        self.assertEqual(df_passed["interactionType"].iloc[0], "parasitism")
        self.assertEqual(df_passed["reference"].iloc[1], "ref2")

    # -------------------------
    # VirHostNet test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("pandas.read_csv")
    def test_clean_virhostnet(
        self,
        mock_read_csv,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        # Sample data that mimics VirHostNet format
        df = pd.DataFrame(
            {
                0: ["P11111"],  # targetUid
                1: ["Q22222"],  # sourceUid
                8: ["PMID:123"],  # reference
                9: ["taxid:9606"],  # targetTaxId
                10: ["taxid:10090"],  # sourceTaxId
                11: ["binding(interact)"],  # interactionType
            }
        )
        mock_read_csv.return_value = df

        # Mock helpers
        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x
        # Call function
        clean_virhostnet("file.csv", "VirHostNet", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_get_names.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]
        # Check that all expected columns exist
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("ontology", df_passed.columns)
        self.assertIn("reference", df_passed.columns)

        # Check that IDs are cleaned
        self.assertEqual(df_passed["sourceUid"].iloc[0], "Q22222")
        self.assertEqual(df_passed["targetUid"].iloc[0], "P11111")
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "10090")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["ontology"].iloc[0], "binding")
        self.assertEqual(df_passed["interactionType"].iloc[0], "interact")

    # -------------------------
    # EID2 test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.add_taxonomy_info")
    @patch("pandas.read_csv")
    def test_clean_eid2(self, mock_read_csv, mock_add_tax, mock_clean_df, mock_export):
        # Sample DataFrame mimicking EID2 file
        df = pd.DataFrame(
            {
                "Cargo": ["[Homo sapiens]"],
                "Carrier": ["Mus musculus"],
                "Publications": ["12345"],
            }
        )
        mock_read_csv.return_value = df

        # Mock taxonomy helper
        def add_tax_side_effect(data, query_col, tax_col, name_col, uniprot):
            data[tax_col] = ["9606" if query_col == "Cargo" else "10090"]
            data[name_col] = [
                "Homo sapiens" if query_col == "Cargo" else "Mus musculus"
            ]
            return data

        mock_add_tax.side_effect = add_tax_side_effect
        mock_clean_df.side_effect = lambda x: x

        # Call the function
        clean_eid2("file.csv", "EID2", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        self.assertEqual(mock_add_tax.call_count, 2)
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]
        # Check expected columns
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("sourceName", df_passed.columns)
        self.assertIn("targetName", df_passed.columns)
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("reference", df_passed.columns)

        # Check that names and TaxIds were set correctly
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "10090")
        self.assertEqual(df_passed["sourceName"].iloc[0], "Homo sapiens")
        self.assertEqual(df_passed["targetName"].iloc[0], "Mus musculus")
        self.assertEqual(df_passed["reference"].iloc[0], "PMID:12345")

    # -------------------------
    # SIAD test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.add_taxonomy_info")
    @patch("helper_processDB.pd.read_csv")
    def test_clean_siad(self, mock_read_csv, mock_add_tax, mock_clean_df, mock_export):
        # Sample DataFrame mimicking SIAD file
        df = pd.DataFrame(
            {
                "name": ["VirusA"],
                "host name": ["Homo sapiens"],
                "interaction": ["infection"],
                "source": ["ref123"],
            }
        )
        # Make read_csv accept any args/kwargs
        mock_read_csv.side_effect = lambda *args, **kwargs: df

        # Mock taxonomy helper
        def add_tax_side_effect(data, query_col, tax_col, name_col, uniprot):
            data[tax_col] = ["123" if query_col == "name" else "9606"]
            data[name_col] = ["VirusA" if query_col == "name" else "Homo sapiens"]
            return data

        mock_add_tax.side_effect = add_tax_side_effect
        mock_clean_df.side_effect = lambda x: x

        # Call the function (real rename_subset_df will run)
        clean_siad("file.csv", "SIAD", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        self.assertEqual(mock_add_tax.call_count, 2)
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check expected columns
        expected_columns = [
            "sourceTaxId",
            "targetTaxId",
            "sourceName",
            "targetName",
            "sourceUid",
            "targetUid",
            "interactionType",
            "reference",
        ]
        for col in expected_columns:
            self.assertIn(col, df_passed.columns)

        # Check that names and TaxIds were set correctly
        self.assertEqual(df_passed["sourceTaxId"].iloc[0], "123")
        self.assertEqual(df_passed["targetTaxId"].iloc[0], "9606")
        self.assertEqual(df_passed["sourceName"].iloc[0], "VirusA")
        self.assertEqual(df_passed["targetName"].iloc[0], "Homo sapiens")

    # -------------------------
    # Bateco interactions test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.pd.read_csv")  # Patch the pd used inside helper_processDB
    def test_clean_bateco_interactions(self, mock_read_csv, mock_clean_df, mock_export):
        # Sample DataFrame mimicking Bateco interactions file
        df = pd.DataFrame(
            {
                "Col1": ["BatA"],
                "Col2": [None],
                "Col3": [None],
                "Col4": [None],
                "Col5": [None],
                "Col6": [None],
                "Col7": [None],
                "Col8": [None],
                "Col9": ["VirusB"],
                "Col10": [None],
                "Col11": [None],
                "Col12": [None],
                "Col13": [None],
                "Col14": [None],
                "Col15": [None],
                "Col16": [None],
                "Citation": ["ref123"],
                "Type": ["infection"],
            }
        )

        # Make read_csv accept any args/kwargs
        mock_read_csv.side_effect = lambda *args, **kwargs: df

        # Mock uniprot request
        def fast_tax_side_effect(name):
            return f"name_{name}", f"id_{name}"

        self.mock_uniprot.fast_tax_name_request.side_effect = fast_tax_side_effect

        # Mock clean_dataframe
        mock_clean_df.side_effect = lambda x: x

        # Call the function
        clean_bateco_interactions("file.csv", "Bateco", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check expected columns
        expected_columns = [
            "sourceTaxId",
            "targetTaxId",
            "sourceName",
            "targetName",
            "sourceUid",
            "targetUid",
            "reference",
            "interactionType",
        ]
        for col in expected_columns:
            assert col in df_passed.columns

        # Check TaxIds and names
        assert df_passed["sourceTaxId"].iloc[0] == "id_BatA"
        assert df_passed["targetTaxId"].iloc[0] == "id_VirusB"
        assert df_passed["sourceName"].iloc[0] == "name_BatA"
        assert df_passed["targetName"].iloc[0] == "name_VirusB"
        assert df_passed["reference"].iloc[0] == "ref123"
        assert df_passed["interactionType"].iloc[0] == "infection"

    # -------------------------
    # GMPD test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("pandas.read_csv")
    @patch("os.listdir")
    def test_clean_gmpd(self, mock_listdir, mock_read_csv, mock_clean_df, mock_export):
        # Correctly mock the directory listing
        mock_listdir.return_value = ["ungulates_file.csv", "primates_file.csv"]

        # Mock dataframes for different file types
        df_ungulates = pd.DataFrame(
            {
                "ParasiteReportedName": ["ParasiteA"],
                "ParasiteCorrectedName": ["ParasiteA_corrected"],
                "HostReportedName": ["HostA"],
                "HostCorrectedName": ["HostA_corrected"],
                "ParType": ["infection"],
                "Citation": ["ref1"],
            }
        )
        df_primates = pd.DataFrame(
            {
                "Parasite Reported Name": ["ParasiteB"],
                "Parasite Corrected Name": ["ParasiteB_corrected"],
                "Host Reported Name": ["HostB"],
                "Host Corrected Name C&H": ["HostB_corrected1"],
                "Host Corrected Name W&R05": ["HostB_corrected2"],
                "Parasite Type": ["parasitism"],
                "Citation": ["ref2"],
            }
        )

        # Return appropriate dataframe based on file name
        def read_csv_side_effect(path, *args, **kwargs):
            if "ungulates" in path:
                return df_ungulates
            elif "primates" in path:
                return df_primates
            return pd.DataFrame()

        mock_read_csv.side_effect = read_csv_side_effect

        # Mock clean_dataframe
        mock_clean_df.side_effect = lambda x: x

        # Mock uniprot
        def fast_tax_side_effect(name):
            return f"name_{name}", f"id_{name}"

        self.mock_uniprot.fast_tax_name_request.side_effect = fast_tax_side_effect

        # Call the function
        clean_gmpd("dir", "GMPD", "/tmp", self.mock_uniprot)

        # Assertions
        mock_listdir.assert_called_once()
        mock_read_csv.assert_called()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check expected columns
        expected_columns = [
            "sourceTaxId",
            "targetTaxId",
            "sourceName",
            "targetName",
            "sourceUid",
            "targetUid",
            "parasiteName1",
            "parasiteName2",
            "hostName1",
            "hostName2",
            "hostName3",
            "interactionType",
            "reference",
        ]
        for col in expected_columns:
            assert col in df_passed.columns

        # Check that the TaxIds and names are properly set
        assert df_passed["sourceTaxId"].iloc[0] == "id_ParasiteA_corrected"
        assert df_passed["targetTaxId"].iloc[0] == "id_HostA_corrected"
        assert df_passed["sourceName"].iloc[0] == "name_ParasiteA_corrected"
        assert df_passed["targetName"].iloc[0] == "name_HostA_corrected"

    # -------------------------
    # PHISTO test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.pd.read_csv")  # only patch read_csv here
    def test_clean_phisto(self, mock_read_csv, mock_clean_df, mock_export):
        # Mock input CSV
        df = pd.DataFrame(
            {
                "Taxonomy ID": [1234],
                "Human Protein": ["P12345"],
                "Pathogen Protein": ["Q67890"],
                "Pubmed ID": ["111"],
            }
        )
        # Accept any args/kwargs
        mock_read_csv.side_effect = lambda *args, **kwargs: df

        # Mock uniprot methods
        self.mock_uniprot.tax_request.side_effect = lambda x: "Homo sapiens"
        self.mock_uniprot.fast_tax_request.side_effect = lambda x: f"name_{x}"

        # Mock clean_dataframe
        mock_clean_df.side_effect = lambda x: x

        # Call function
        clean_phisto("file.csv", "PHISTO", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check columns
        expected_columns = [
            "sourceName",
            "sourceUid",
            "targetName",
            "targetUid",
            "sourceTaxId",
            "targetTaxId",
            "reference",
        ]
        for col in expected_columns:
            assert col in df_passed.columns
        # Check values
        assert df_passed["sourceName"].iloc[0] == "Homo sapiens"
        assert df_passed["targetName"].iloc[0] == "name_1234"
        assert df_passed["sourceUid"].iloc[0] == "P12345"
        assert df_passed["targetUid"].iloc[0] == "Q67890"
        assert df_passed["sourceTaxId"].iloc[0] == "9606"
        assert df_passed["targetTaxId"].iloc[0] == "1234"
        assert df_passed["reference"].iloc[0] == "PMID:111"

    # -------------------------
    # MINT database test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("pandas.read_csv")
    def test_clean_mint(
        self, mock_read_csv, mock_get_names, mock_clean_df, mock_export
    ):
        # Mock input CSV
        df = pd.DataFrame(
            {
                0: ["uniprotkb:P12345"],
                1: ["uniprotkb:Q67890"],
                8: ["PMID:123"],
                9: ["taxid:9606(Homo sapiens)"],
                10: ["taxid:10090(Mus musculus)"],
                11: ["binding(interact)"],
            }
        )

        # Mock read_csv to accept any arguments
        mock_read_csv.side_effect = lambda *args, **kwargs: df

        # Mock getSourceTargetNames and clean_dataframe to just return the input
        mock_get_names.side_effect = lambda x: x
        mock_clean_df.side_effect = lambda x: x

        # Call the function
        clean_mint("file.csv", "MINT", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_csv.assert_called_once()
        mock_get_names.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check columns exist
        expected_cols = [
            "sourceUid",
            "targetUid",
            "reference",
            "sourceTaxId",
            "targetTaxId",
            "interactionType",
            "ontology",
        ]
        for col in expected_cols:
            assert col in df_passed.columns

        # Check cleaned values
        assert df_passed["sourceUid"].iloc[0] == "P12345"
        assert df_passed["targetUid"].iloc[0] == "Q67890"
        assert df_passed["sourceTaxId"].iloc[0] == "9606"
        assert df_passed["targetTaxId"].iloc[0] == "10090"
        assert df_passed["interactionType"].iloc[0] == "interact"
        assert df_passed["ontology"].iloc[0] == "binding"
        assert df_passed["reference"].iloc[0] == "PMID:123"

    # -------------------------
    # PMC9897028 viral interactome test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.clean_dataframe")
    @patch("pandas.read_excel")
    def test_clean_pmc9897028(self, mock_read_excel, mock_clean_df, mock_export):
        # Mock input Excel data
        df = pd.DataFrame(
            {
                "Organism_human": ["Homo sapiens"],
                "Organism_Interactor_human": ["9606"],
                "Uniprot_human": ["P12345"],
                "Organism_virus": ["VirusX"],
                "Organism_Interactor_virus": ["1001,1002"],  # Multiple virus IDs
                "Uniprot_virus": ["V123"],
                "Interaction_Type": ["infection"],
                "Pubmed_ID": ["123456"],
            }
        )
        mock_read_excel.return_value = df

        # Use real rename_subset_df, so no patch for it

        # Mock clean_dataframe to pass data through
        mock_clean_df.side_effect = lambda df: df

        # Call function
        clean_pmc9897028("dir", "PMC9897028", "/tmp", self.mock_uniprot)

        # Assertions
        mock_read_excel.assert_called_once()
        mock_clean_df.assert_called_once()
        mock_export.assert_called_once()

        df_passed = mock_export.call_args[0][0]

        # Check columns
        expected_cols = [
            "sourceTaxId",
            "sourceName",
            "sourceUid",
            "targetTaxId",
            "targetName",
            "targetUid",
            "interactionType",
            "reference",
        ]
        for col in expected_cols:
            assert col in df_passed.columns

        # Check splitting of multiple virus IDs
        assert len(df_passed) == 2
        assert set(df_passed["sourceTaxId"].astype(int)) == {1001, 1002}

        # Check reference prefix
        assert df_passed["reference"].iloc[0] == "PMID:123456"

    # -------------------------
    # SIGNOR test
    # -------------------------
    @patch("helper_processDB.export_dataframe")
    @patch("helper_processDB.getSourceTargetNames")
    @patch("helper_processDB.clean_dataframe")
    @patch("pandas.read_csv")
    def test_clean_signor(
        self,
        mock_read_csv,
        mock_clean_df,
        mock_get_names,
        mock_export,
    ):
        df = pd.DataFrame(
            {
                "DATABASEA": ["UNIPROT", "UNIPROT", "OTHER"],
                "DATABASEB": ["UNIPROT", "UNIPROT", "UNIPROT"],
                "IDA": ["P12345", "Q67890", "X11111"],
                "IDB": ["Q67890", "P12345", "Y22222"],
                "PMID": ["111", "222", "333"],
                "MECHANISM": ["binding", "phosphorylation", "unknown"],
            }
        )
        mock_read_csv.return_value = df

        mock_clean_df.side_effect = lambda x: x
        mock_get_names.side_effect = lambda x: x

        clean_signor("file.tsv", "SIGNOR", "/tmp", self.mock_uniprot)

        df_passed = mock_export.call_args[0][0]

        # check columns exist
        self.assertIn("sourceUid", df_passed.columns)
        self.assertIn("targetUid", df_passed.columns)
        self.assertIn("sourceTaxId", df_passed.columns)
        self.assertIn("targetTaxId", df_passed.columns)
        self.assertIn("interactionType", df_passed.columns)
        self.assertIn("reference", df_passed.columns)

        # check only UNIPROT entries are kept
        self.assertTrue(set(df_passed["sourceUid"]) <= {"P12345", "Q67890"})
        self.assertTrue(set(df_passed["targetUid"]) <= {"P12345", "Q67890"})

        # check reference formatting
        self.assertTrue(df_passed["reference"].iloc[0].startswith("PMID:"))


# Run all tests
if __name__ == "__main__":
    unittest.main()
