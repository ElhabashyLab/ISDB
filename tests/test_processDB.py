import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import pandas as pd
import os
import numpy as np
import sys

sys.path.insert(1, "../utils/")
from processDB import (
    is_float,
    file_exists,
    check_out_exists,
    clean_dataframe,
    getSourceTargetNames,
    get_taxonomic_identifier,
    clean_bvbrc,
    clean_biogrid,
    clean_DIP,
    clean_fgscdb,
    clean_web_of_life,
    clean_globi,
    clean_HPIDB,
    clean_intact,
    clean_iwdb,
    clean_phi_base,
    clean_PHILM2Web,
    clean_pida,
    clean_virHostNet,
    clean_eid2,
    clean_siad,
    clean_bat_eco,
    clean_gmpd,
    clean_phisto,
    clean_mint,
    clean_interactome,
    clean_signor,
)


class TestProcessDB(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output
        self.output_dir = tempfile.mkdtemp() + "/"  # os.getcwd() + "/mock/"
        # os.mkdir(self.output_dir)
        self.input_dir = os.getcwd() + "/test_files_in/"
        self.true_files_dir = os.getcwd() + "/test_files_out/"

        # Copy the entire test_files directory to the mock directory
        shutil.copytree(self.input_dir, self.output_dir, dirs_exist_ok=True)

        # self.prefix = "test_prefix"  # file structure e.g. bvbrc/

    def tearDown(self):
        # Remove the temporary directory after tests
        shutil.rmtree(self.output_dir)

    def run_cleaning_test(
        self,
        clean_function,
        input_file_prefix,
        output_filename,
    ):
        with patch("processDB.tempory_directory", self.output_dir):
            # Call the cleaning function
            clean_function(input_file_prefix)

            # Check output file
            output_file = os.path.join(self.output_dir, output_filename)
            self.assertTrue(os.path.exists(output_file), "Output file should exist")

            # Read the output file and check its content
            if output_filename.endswith("tsv"):
                output_df = pd.read_csv(self.output_dir + output_filename, sep="\t")
            else:
                output_df = pd.read_csv(self.output_dir + output_filename)

            # Read the expected output from a separate CSV file
            true_output_file = os.path.join(
                self.true_files_dir, output_filename
            )  # Path to the expected output file
            if true_output_file.endswith("tsv"):
                expected_df = pd.read_csv(true_output_file, sep="\t")
            else:
                expected_df = pd.read_csv(true_output_file)

            # Check if the output DataFrame matches the expected DataFrame
            self.assertEqual(output_df.shape, expected_df.shape)
            self.assertSetEqual(set(output_df.columns), set(expected_df.columns))

    def test_is_float(self):
        # Test with valid float strings
        self.assertTrue(is_float("123.45"))
        self.assertTrue(is_float("-0.123"))

        # Test with invalid float strings
        self.assertFalse(is_float("abc"))
        self.assertFalse(is_float("123abc"))

    @patch("os.path.isdir", return_value=False)
    @patch("os.path.exists", return_value=False)
    def test_file_exists_invalid(self, mock_isdir, mock_exists):
        # Test for an invalid file path
        with self.assertRaises(ValueError):
            file_exists("/nonexistent/file/path")

    @patch("os.listdir", return_value=["biogrid_out.csv", "other_file.txt"])
    def test_check_out_exists(self, mock_listdir):
        # Test for a file that exists
        self.assertTrue(check_out_exists("biogrid"))

        # Test for a file that does not exist
        self.assertFalse(check_out_exists("nonexistent"))

    def test_clean_dataframe(self):
        # Sample data
        data = {
            "sourceTaxId": ["9606", "9606", "10090"],
            "targetTaxId": ["10090", "10090", "9606"],
            "sourceUid": ["P12345", "P12345", "Q67890"],
            "targetUid": ["Q67890", "Q67890", "P12345"],
            "extra_col": ["A|B", "B|D", "C"],
        }
        df = pd.DataFrame(data)
        # Test cleaning the dataframe
        cleaned_df = clean_dataframe(df)
        self.assertEqual(cleaned_df["extra_col"].iloc[1], "A|B|D")
        self.assertEqual(len(cleaned_df), 2)  # Duplicates should be combined

    @patch("processDB.uniprot_request")
    def test_getSourceTargetNames(self, mock_uniprot_request):
        # Mock the `fast_tax_request` method
        mock_uniprot_request_instance = mock_uniprot_request.return_value
        mock_uniprot_request_instance.fast_tax_request.side_effect = (
            lambda x: f"Species{x}"
        )

        # Sample data
        df = pd.DataFrame({"sourceTaxId": ["9606"], "targetTaxId": ["10090"]})

        # Test function
        result = getSourceTargetNames(df)
        self.assertEqual(result.loc[0, "sourceName"], "Species9606")
        self.assertEqual(result.loc[0, "targetName"], "Species10090")

    @patch("requests.get")
    def test_get_taxonomic_identifier(self, mock_get):
        # Mock XML response from Uniprot
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
            <entry>
                <dbReference type="NCBI Taxonomy" id="9606"/>
            </entry>
        """
        mock_get.return_value = mock_response

        # Test function
        tax_id = get_taxonomic_identifier("P12345")
        self.assertEqual(tax_id, "9606")

    # Test database functions
    def test_bvbrc(self):
        self.run_cleaning_test(clean_bvbrc, "/bvbrc", "bvbrc_out.csv")

    def test_biogrid(self):
        self.run_cleaning_test(
            clean_biogrid, "/biogrid_all_latest", "biogrid_latest_out.tsv"
        )

    def test_DIP(self):
        self.run_cleaning_test(clean_DIP, "/dip", "dip_out.tsv")

    def test_fgscdb(self):
        self.run_cleaning_test(clean_fgscdb, "/FGSCdb_data.csv", "fgscdb_out.tsv")

    def test_web_of_life(self):
        self.run_cleaning_test(clean_web_of_life, "/web_of_life", "web_of_life_out.tsv")

    def test_globi(self):
        self.run_cleaning_test(clean_globi, "/globi", "globi_out.tsv")

    def test_hpidb(self):
        self.run_cleaning_test(clean_HPIDB, "/hpidb", "HPIDB_out.tsv")

    def test_intact(self):
        self.run_cleaning_test(clean_intact, "/intact.txt", "intact_out.tsv")

    def test_iwdb(self):
        self.run_cleaning_test(clean_iwdb, "/iwdb", "iwdb_out.tsv")

    def test_phi_base(self):
        self.run_cleaning_test(clean_phi_base, "/phi_base.csv", "phi_base_out.tsv")

    def test_PHILM2Web(self):
        self.run_cleaning_test(clean_PHILM2Web, "philm2web.csv", "philm2web_out.tsv")

    def test_pida(self):
        self.run_cleaning_test(clean_pida, "/pida.tsv", "pida_out.tsv")

    def test_virHostNet(self):
        self.run_cleaning_test(
            clean_virHostNet, "/vir_host_net.tsv", "vir_host_net_out.tsv"
        )

    def test_eid2(self):
        self.run_cleaning_test(clean_eid2, "/eid2.csv", "eid2_out.tsv")

    def test_siad(self):
        self.run_cleaning_test(clean_siad, "/siad.txt", "siad_out.tsv")

    def test_bat_eco(self):
        self.run_cleaning_test(
            clean_bat_eco, "/BatEco-InteractionRecords.csv", "bat_eco_out.tsv"
        )

    def test_gmpd(self):
        self.run_cleaning_test(clean_gmpd, "/gmpd", "gmpd_out.tsv")

    def test_phisto(self):
        self.run_cleaning_test(clean_phisto, "/phisto_data.csv", "phisto_out.tsv")

    def test_mint(self):
        self.run_cleaning_test(clean_mint, "/mint.tsv", "mint_out.tsv")

    def test_interactome(self):
        self.run_cleaning_test(
            clean_interactome, "/viral_interactome", "interactome_out.tsv"
        )

    def test_signor(self):
        self.run_cleaning_test(clean_signor, "/signor.tsv", "signor_out.tsv")
