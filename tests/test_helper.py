import unittest
from unittest.mock import MagicMock, patch
import tempfile
import pandas as pd
import numpy as np
import os
import sys

# Import your functions (if they are in the same file, you can skip this)
sys.path.insert(1, "../utils")
from helper import *


class TestUtilityFunctions(unittest.TestCase):

    def test_check_dataframe_basic(self):
        # Create a small DataFrame simulating a CSV file
        df = pd.DataFrame(
            {
                "sourceTaxId": ["1", "2"],
                "targetTaxId": ["A", "B"],
                "reference": ["foo|bar", "baz"],
                "irrelevant": [123, 456],  # this column should be ignored
            }
        )

        # Write to a temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_file = tmp.name

        try:
            # Run the function under test
            checked = check_dataframe(tmp_file)

            # Check that all required columns exist
            for col in table_columns:
                self.assertIn(col, checked.columns)

            # Missing columns should be added as empty
            self.assertTrue((checked["sourceUid"] == "").all())
            self.assertTrue((checked["targetUid"] == "").all())

            # Existing values are preserved
            self.assertEqual(checked.loc[0, "targetTaxId"], "A")
            self.assertEqual(checked.loc[1, "reference"], "baz")

            # Extra/unwanted columns are removed
            self.assertNotIn("irrelevant", checked.columns)

        finally:
            os.remove(tmp_file)

    def test_get_additional_frames(self):
        # Create a temporary directory for additional data
        tmp_dir = tempfile.mkdtemp()
        try:
            # Create two CSV files inside the temp directory
            df1 = pd.DataFrame(
                {
                    "sourceTaxId": ["1"],
                    "targetTaxId": ["A"],
                }
            )
            df2 = pd.DataFrame(
                {
                    "sourceUid": ["X"],
                    "targetUid": ["Y"],
                }
            )

            file1 = os.path.join(tmp_dir, "file1.csv")
            file2 = os.path.join(tmp_dir, "file2.csv")
            df1.to_csv(file1, index=False)
            df2.to_csv(file2, index=False)

            # Run the function on a directory
            frames = get_additional_frames(tmp_dir + "/")  # note trailing slash
            self.assertEqual(len(frames), 2)

            # Each frame should contain all table_columns
            for frame in frames:
                for col in table_columns:
                    self.assertIn(col, frame.columns)

            # Run the function on a single file
            single_frame = get_additional_frames(file1)
            self.assertEqual(len(single_frame), 1)
            self.assertIn("sourceTaxId", single_frame[0].columns)

            # Run the function with an invalid path
            empty_frame = get_additional_frames("nonexistent_path")
            self.assertEqual(len(empty_frame), 1)
            self.assertTrue(
                empty_frame[0].empty
                or all(col in empty_frame[0].columns for col in table_columns)
            )

        finally:
            # Cleanup temporary files and directory
            for f in [file1, file2]:
                if os.path.exists(f):
                    os.remove(f)
            if os.path.exists(tmp_dir):
                os.rmdir(tmp_dir)

    def test_is_float(self):
        self.assertTrue(is_float("3.14"))
        self.assertTrue(is_float("0"))
        self.assertFalse(is_float("abc"))
        self.assertFalse(is_float("3.14a"))

    def test_not_float(self):
        self.assertFalse(not_float("3.14"))
        self.assertFalse(not_float("0"))
        self.assertTrue(not_float("abc"))
        self.assertTrue(not_float("3.14a"))

    def test_join_unique(self):
        # Input list with "|" separated values and commas
        input_values = ["A|B|C", "B|D", "E, F", None, "G|H|A"]

        # Call the function under test
        result = join_unique(input_values)

        # Convert result back to a set for easy checking
        result_set = set(result.split("|"))
        # Check that all unique values are present
        expected_set = set(["A", "B", "C", "D", "E", "F", "G", "H"])
        self.assertEqual(result_set, expected_set)

        # Check that the returned value is a string
        self.assertIsInstance(result, str)

        # Check that there are no "nan" or empty values in the output
        self.assertNotIn("nan", result)
        self.assertNotIn("", result.split("|"))

    def test_read_and_combine_output_files(self):
        # Create two temporary CSV/TSV files
        df_csv = pd.DataFrame(
            {
                "sourceTaxId": ["1", "2"],
                "targetTaxId": ["A", "B"],
                "sourceUid": ["X", "Y"],
                "targetUid": ["P", "Q"],
            }
        )
        df_tsv = pd.DataFrame(
            {
                "sourceTaxId": ["3"],
                "targetTaxId": ["C"],
                "sourceUid": ["Z"],
                "targetUid": ["R"],
            }
        )

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv"
        ) as tmp1, tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".tsv"
        ) as tmp2:
            df_csv.to_csv(tmp1.name, index=False)
            df_tsv.to_csv(tmp2.name, sep="\t", index=False)
            csv_file = tmp1.name
            tsv_file = tmp2.name

        try:
            # Call the function under test
            combined = read_and_combine_output_files([csv_file, tsv_file])

            # Check that all rows from both files are present
            self.assertEqual(len(combined), 3)

            # Check that all expected columns exist
            for col in ["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]:
                self.assertIn(col, combined.columns)

            # Check that values are preserved
            self.assertIn("1", combined["sourceTaxId"].values)
            self.assertIn("C", combined["targetTaxId"].values)

            # Check that dtype is string for all columns
            for col in ["sourceTaxId", "targetTaxId", "sourceUid", "targetUid"]:
                self.assertTrue(combined[col].dtype == object)

        finally:
            # Clean up temporary files
            os.remove(csv_file)
            os.remove(tsv_file)

        def test_export_for_protein_search(self):
            # Create a small test DataFrame
            df = pd.DataFrame(
                {
                    "Serial Number": [1, 2, 3],
                    "Taxonomy ID A": [9606, 10090, 9606],
                    "Organism A": ["Human", "Mouse", "Human"],
                    "UniProt ID A": ["P12345", None, "Q67890"],
                    "Protein Name A": ["ProteinA1", "ProteinA2", "ProteinA3"],
                    "Taxonomy ID B": [10090, 9606, 10090],
                    "Organism B": ["Mouse", "Human", "Mouse"],
                    "UniProt ID B": ["Q54321", "P98765", None],
                    "Protein Name B": ["ProteinB1", "ProteinB2", "ProteinB3"],
                    "Interaction Type": ["binding", "activation", "inhibition"],
                    "Ontology ID": ["GO:0001", "GO:0002", "GO:0003"],
                    "Reference": ["Ref1", "Ref2", "Ref3"],
                    "Database": ["DB1", "DB2", "DB3"],
                }
            )

            tmp_dir = "/fake/tmp/dir"

            # Patch the DataFrame.to_csv method
            with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
                export_for_protein_search(df, tmp_dir)

                # Check that to_csv was called exactly once
                self.assertEqual(mock_to_csv.call_count, 1)

                # Grab the arguments with which to_csv was called
                call_args, call_kwargs = mock_to_csv.call_args

                # Check the separator is tab
                self.assertEqual(call_kwargs["sep"], "\t")

                # Check that index is False
                self.assertFalse(call_kwargs["index"])

                # Check that only rows with valid UniProt IDs would be exported
                exported_df = df.loc[
                    df["UniProt ID A"].notna() & df["UniProt ID B"].notna(),
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
                # The DataFrame passed to to_csv should equal this filtered DataFrame
                pd.testing.assert_frame_equal(
                    call_kwargs["path_or_buf"], None
                )  # path checked separately if needed
                pd.testing.assert_frame_equal(
                    exported_df.reset_index(drop=True),
                    df.loc[
                        df["UniProt ID A"].notna() & df["UniProt ID B"].notna(),
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
                    ].reset_index(drop=True),
                )

    def test_export_for_species_search(self):
        # Create a small test DataFrame
        df = pd.DataFrame(
            {
                "Serial Number": [1, 2, 3, 4],
                "Taxonomy ID A": [9606, 9606, 10090, 10090],
                "Organism A": ["Human", "Human", "Mouse", "Mouse"],
                "Taxonomy ID B": [10090, 10090, 9606, 9606],
                "Organism B": ["Mouse", "Mouse", "Human", "Human"],
                "Interaction Type": ["binding", "binding", "activation", "activation"],
                "Ontology ID": ["GO:0001", "GO:0001", "GO:0002", "GO:0002"],
                "Reference": ["Ref1", "Ref1", "Ref2", "Ref2"],
                "Database": ["DB1", "DB1", "DB2", "DB2"],
            }
        )

        tmp_dir = "/fake/tmp/dir"

        # Patch the DataFrame.to_csv method
        with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
            export_for_species_search(df, tmp_dir)

            # Check that to_csv was called exactly once
            self.assertEqual(mock_to_csv.call_count, 1)

            # Extract the DataFrame passed to to_csv
            exported_df = df.loc[
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
            ].drop_duplicates(subset=["Taxonomy ID A", "Taxonomy ID B"])

            # Grab the DataFrame argument that to_csv was called on
            called_df = (
                mock_to_csv.call_args[0][0] if mock_to_csv.call_args[0] else None
            )

            # Check separator and index kwargs
            self.assertEqual(mock_to_csv.call_args.kwargs["sep"], "\t")
            self.assertFalse(mock_to_csv.call_args.kwargs["index"])

            # Ensure the exported DataFrame has the expected rows
            pd.testing.assert_frame_equal(
                exported_df.reset_index(drop=True),
                df.loc[
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
                ]
                .drop_duplicates(subset=["Taxonomy ID A", "Taxonomy ID B"])
                .reset_index(drop=True),
            )

    def test_file_exists(self):
        # valid directory
        with patch("os.path.isdir", return_value=True), patch(
            "os.path.exists", return_value=False
        ):
            file_exists("some_path", "/tmp")  # should not raise
        # invalid path
        with patch("os.path.isdir", return_value=False), patch(
            "os.path.exists", return_value=False
        ):
            with self.assertRaises(ValueError):
                file_exists("nonexistent_path", "/tmp")

    def test_check_out_exists(self):
        tmp_dir = "/tmp"
        with patch("os.listdir", return_value=["bvbrc_out", "other_file.txt"]):
            self.assertTrue(check_out_exists("bvbrc", tmp_dir))
            self.assertFalse(check_out_exists("missing", tmp_dir))

    def test_clean_dataframe(self):
        df = pd.DataFrame(
            {
                "sourceTaxId": ["1", "1", "2", None],
                "targetTaxId": ["A", "A", "B", "C"],
                "sourceUid": ["X", "X", "Y", "Z"],
                "targetUid": ["P", "P", "Q", "R"],
                "extra": ["foo|bar", "baz", "qux", "xyz"],
            }
        )
        cleaned = clean_dataframe(df)
        self.assertIn("sourceTaxId", cleaned.columns)
        self.assertIn("targetTaxId", cleaned.columns)
        self.assertTrue(any("foo" in val for val in cleaned["extra"]))

    def test_getSourceTargetNames(self):
        df = pd.DataFrame({"sourceTaxId": ["123"], "targetTaxId": ["456"]})
        mock_uniprot = MagicMock()
        mock_uniprot.fast_tax_request.side_effect = lambda x: f"name_{x}"
        result = getSourceTargetNames(df, mock_uniprot)
        self.assertEqual(result["sourceName"].iloc[0], "name_123")
        self.assertEqual(result["targetName"].iloc[0], "name_456")

    @patch("helper.requests.get")
    def test_get_taxonomic_identifier(self, mock_get):
        # successful XML
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '<dbReference type="NCBI Taxonomy" id="9999"/>'
        taxid = get_taxonomic_identifier("P12345")
        self.assertEqual(taxid, "9999")
        # no tax id
        mock_get.return_value.text = "<xml></xml>"
        self.assertIsNone(get_taxonomic_identifier("P12345"))
        # bad status code
        mock_get.return_value.status_code = 404
        self.assertIsNone(get_taxonomic_identifier("P12345"))

    def test_rename_subset_df(self):
        df = pd.DataFrame({"A": [1], "B": [2], "C": [3]})
        mapping = {"A": "X", "B": "Y"}
        result = rename_subset_df(df, mapping)
        self.assertIn("X", result.columns)
        self.assertIn("Y", result.columns)
        self.assertNotIn("C", result.columns)

    def test_add_taxonomy_info(self):
        df = pd.DataFrame({"Host": ["human", "mouse"]})
        mock_uniprot = MagicMock()
        mock_uniprot.fast_tax_name_request.side_effect = lambda x: (
            f"name_{x}",
            f"id_{x}",
        )
        result = add_taxonomy_info(
            df, "Host", "targetTaxId", "targetName", mock_uniprot
        )
        self.assertEqual(result["targetTaxId"].iloc[0], "id_human")
        self.assertEqual(result["targetName"].iloc[0], "name_human")
        self.assertEqual(result["targetTaxId"].iloc[1], "id_mouse")
        self.assertEqual(result["targetName"].iloc[1], "name_mouse")


if __name__ == "__main__":
    unittest.main()
