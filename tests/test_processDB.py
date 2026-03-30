import unittest
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(1, "../utils")
from processDB import check_and_process_db


class TestCheckAndProcessDB(unittest.TestCase):
    def setUp(self):
        self.mock_uniprot = MagicMock()
        self.mock_process_func = MagicMock()

    @patch("processDB.file_exists")
    @patch("processDB.check_out_exists")
    def test_process_db_runs_when_output_missing(
        self, mock_check_out, mock_file_exists
    ):
        """process_func is called if output does not exist"""
        mock_check_out.return_value = False
        mock_file_exists.return_value = None

        result = check_and_process_db(
            dir="dir",
            name="TEST_DB",
            process_func=self.mock_process_func,
            overwrite=False,
            tmp_dir="/tmp",
            uniprot=self.mock_uniprot,
        )

        self.assertIsNone(result)
        self.mock_process_func.assert_called_once_with(
            "dir", "TEST_DB", "/tmp", self.mock_uniprot
        )
        mock_file_exists.assert_called_once()
        mock_check_out.assert_called_once_with("test_db", "/tmp")  # lowercase name

    @patch("processDB.file_exists")
    @patch("processDB.check_out_exists")
    def test_process_db_skips_when_output_exists_and_no_overwrite(
        self, mock_check_out, mock_file_exists
    ):
        """process_func is NOT called if output exists and overwrite=False"""
        mock_check_out.return_value = True
        mock_file_exists.return_value = None

        result = check_and_process_db(
            dir="dir",
            name="TEST_DB",
            process_func=self.mock_process_func,
            overwrite=False,
            tmp_dir="/tmp",
            uniprot=self.mock_uniprot,
        )

        self.assertIsNone(result)
        self.mock_process_func.assert_not_called()
        mock_file_exists.assert_called_once()
        mock_check_out.assert_called_once_with("test_db", "/tmp")

    @patch("processDB.file_exists")
    @patch("processDB.check_out_exists")
    def test_process_db_overwrite_calls_process_func(
        self, mock_check_out, mock_file_exists
    ):
        """process_func is called if overwrite=True even if output exists"""
        mock_check_out.return_value = True
        mock_file_exists.return_value = None

        result = check_and_process_db(
            dir="dir",
            name="TEST_DB",
            process_func=self.mock_process_func,
            overwrite=True,
            tmp_dir="/tmp",
            uniprot=self.mock_uniprot,
        )

        self.assertIsNone(result)
        self.mock_process_func.assert_called_once_with(
            "dir", "TEST_DB", "/tmp", self.mock_uniprot
        )

    @patch("processDB.file_exists")
    @patch("processDB.check_out_exists")
    def test_process_db_catches_exception(self, mock_check_out, mock_file_exists):
        """Exceptions in process_func are caught and returned"""
        mock_check_out.return_value = False
        mock_file_exists.return_value = None

        self.mock_process_func.side_effect = ValueError("Something went wrong")

        result = check_and_process_db(
            dir="dir",
            name="TEST_DB",
            process_func=self.mock_process_func,
            overwrite=False,
            tmp_dir="/tmp",
            uniprot=self.mock_uniprot,
        )

        self.assertIsNotNone(result)
        self.assertIn("TEST_DB", result)
        self.assertIn("Something went wrong", result)
        self.mock_process_func.assert_called_once()


if __name__ == "__main__":
    unittest.main()
