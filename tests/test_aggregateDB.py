import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date
import sys

sys.path.insert(1, "../utils")
from uniprot_api import uniprot_request
from aggregateDB import main


class TestMainFunction(unittest.TestCase):
    @patch("aggregateDB.export_for_species_search")
    @patch("aggregateDB.export_for_protein_search")
    @patch("aggregateDB.uniprot_request")
    @patch("aggregateDB.get_additional_frames")
    @patch("aggregateDB.read_and_combine_output_files")
    @patch("aggregateDB.os")  # Patch os functions in aggregateDB
    def test_main(
        self,
        mock_os,
        mock_read_db,
        mock_get_additional,
        mock_uniprot,
        mock_export_protein,
        mock_export_species,
    ):
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key: {
            "OUT_DIRECTORY": "/fake/out_dir/",
            "ADDITIONAL_DATA": None,
        }[key]

        # Mock os.walk to return one fake directory with two output files
        mock_os.walk.return_value = [
            ("/fake/out_dir/", [], ["file1.out.csv", "file2.out.tsv"])
        ]

        # Mock read_and_combine_output_files to return a small DataFrame
        df_db = pd.DataFrame(
            {
                "sourceTaxId": ["1", "2"],
                "sourceName": ["A", "B"],
                "sourceUid": ["P123", "Q456"],
                "targetTaxId": ["3", "4"],
                "targetName": ["C", "D"],
                "targetUid": ["R789", "S012"],
                "interactionType": ["binding", "activation"],
                "ontology": ["GO:1", "GO:2"],
                "reference": ["Ref1", "Ref2"],
                "database": ["DB1", "DB2"],
            }
        )
        mock_read_db.return_value = df_db

        # Mock get_additional_frames to return empty list (no extra data)
        mock_get_additional.return_value = []

        # Mock uniprot_request and its fast_protein_id_request method
        mock_uniprot_instance = MagicMock()
        mock_uniprot_instance.fast_protein_id_request.side_effect = lambda x: (
            f"Protein_{x}",
            x,
        )
        mock_uniprot.return_value = mock_uniprot_instance

        # Patch DataFrame.to_csv to prevent actual file creation
        with patch.object(pd.DataFrame, "to_csv") as mock_to_csv:
            main()

            # Check that read_and_combine_output_files was called with the correct files
            mock_read_db.assert_called_once_with(
                ["/fake/out_dir/file1.out.csv", "/fake/out_dir/file2.out.tsv"]
            )

            # get_additional_frames should NOT be called because ADDITIONAL_DATA=None
            mock_get_additional.assert_not_called()

            # uniprot_request should have been instantiated
            mock_uniprot.assert_called_once()

            # Export functions should have been called
            self.assertTrue(mock_export_protein.called)
            self.assertTrue(mock_export_species.called)

            # DataFrame.to_csv should be called twice (CSV + TSV)
            self.assertEqual(mock_to_csv.call_count, 2)


if __name__ == "__main__":
    unittest.main()
