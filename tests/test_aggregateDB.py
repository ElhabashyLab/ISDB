import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import pandas as pd
import os
import numpy as np
import sys

sys.path.insert(1, "../utils/")
from aggregateDB import (
    check_dataframe,
    get_additional_frames,
    not_float,
    join_unique,
    main,
)


class TestAggregateDB(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for output
        self.output_dir = tempfile.mkdtemp() + "/"  # os.getcwd() + "/mock/"
        # os.mkdir(self.output_dir)
        self.reference_dir = os.getcwd() + "/test_files_out/"

        # Copy the entire test_files directory to the mock directory
        shutil.copytree(self.reference_dir, self.output_dir, dirs_exist_ok=True)

        # self.prefix = "test_prefix"  # file structure e.g. bvbrc/
        self.columns = [  # TODO update columns
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

    def tearDown(self):
        # Remove the temporary directory after tests
        shutil.rmtree(self.output_dir)

    @patch("datetime.date")
    def test_main(self, mock_date):
        with patch("aggregateDB.tempory_directory", self.output_dir):
            mock_date.today.return_value = pd.Timestamp("2024-10-28")

            # Call the cleaning function
            main()

            # Check output file
            output_file = os.path.join(self.output_dir, "ISDB_2024_10_28")
            self.assertTrue(
                os.path.exists(output_file + ".csv"), "Output file should exist"
            )
            self.assertTrue(
                os.path.exists(output_file + ".tsv"), "Output file should exist"
            )

            # Read the output file and check its content
            ISDB_csv = pd.read_csv(output_file + ".csv")
            ISDB_tsv = pd.read_csv(output_file + ".tsv", sep="\t")

            # Read the expected output from a separate CSV file
            ISDB_csv_ref = pd.read_csv(
                self.reference_dir + "ISDB_2024_10_28.csv"
            )  # TODO Rework files
            ISDB_tsv_ref = pd.read_csv(
                self.reference_dir + "ISDB_2024_10_28.tsv", sep="\t"
            )

            # Check if the output DataFrame matches the expected DataFrame
            self.assertEqual(ISDB_csv.shape, ISDB_csv_ref.shape)
            self.assertEqual(ISDB_tsv.shape, ISDB_tsv_ref.shape)
            self.assertSetEqual(set(ISDB_tsv.columns), set(ISDB_tsv_ref.columns))
            self.assertSetEqual(set(ISDB_csv.columns), set(ISDB_csv_ref.columns))

    def test_not_float(self):
        # Check `not_float` function with various inputs
        self.assertTrue(not_float("not_a_number"))
        self.assertFalse(not_float("123.456"))

    def test_join_unique(self):
        # Test `join_unique` for combining unique values
        result = join_unique(["A|B", "B|C", "D"])
        self.assertEqual(result, "A|B|C|D")

    def test_check_dataframe(self):
        # Run check_dataframe on a invalid input file
        df = check_dataframe(self.reference_dir + "empty_file.csv")
        self.assertSetEqual(set(df.columns), set(self.columns))
        self.assertEqual(df.shape, pd.DataFrame(columns=self.columns).shape)
        # Run check_dataframe on a valid input file
        df = check_dataframe(self.reference_dir + "bvbrc_out.csv")
        df_ref = pd.read_csv(self.reference_dir + "bvbrc_out.csv")
        self.assertSetEqual(set(df.columns), set(df_ref.columns))
        self.assertEqual(df.shape, df_ref.shape)

    def test_get_additional_frames_dir(self):
        with patch("aggregateDB.additional_data", self.output_dir):
            # Run get_additional_frames and validate the DataFrame
            frames = get_additional_frames()
            self.assertTrue(len(frames) == 3)
            self.assertListEqual([10, 10, 11], [len(f.columns) for f in frames])

    def test_get_additional_frames_file(self):
        with patch("aggregateDB.additional_data", self.output_dir + "bvbrc_out.csv"):
            # Run get_additional_frames and validate the DataFrame
            frame = get_additional_frames()
            df = pd.read_csv(self.reference_dir + "bvbrc_out.csv")
            self.assertTrue(len(frame) == 1)
            self.assertSetEqual(set(df.columns), set(frame[0].columns))
            self.assertEqual(df.shape, frame[0].shape)

    def test_get_additional_frames_invalid(self):
        with patch("aggregateDB.additional_data", "/not/valid"):
            # print(additional_data)
            # Run get_additional_frames and validate the DataFrame
            frame = get_additional_frames()
            self.assertTrue(len(frame) == 1)
            self.assertSetEqual(set(self.columns), set(frame[0].columns))
            self.assertEqual(pd.DataFrame(columns=self.columns).shape, frame[0].shape)
