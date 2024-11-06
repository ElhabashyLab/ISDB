import unittest
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(1, "../utils/")
from uniprot_api import uniprot_request


class TestUniprotRequest(unittest.TestCase):

    def setUp(self):
        self.uniprot = uniprot_request()

    @patch("requests.get")
    def test_uid_request_success(self, mock_get):
        # Mock a successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = "<mocked_xml>response</mocked_xml>"
        mock_get.return_value = mock_response

        # Test
        result = self.uniprot.uid_request("P12345")
        self.assertIsNotNone(result)

    @patch("requests.get")
    def test_uid_request_failure(self, mock_get):
        # Mock a failed response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.raise_for_status.side_effect = Exception("Error")
        mock_get.return_value = mock_response

        # Test
        with self.assertRaises(Exception):
            self.uniprot.uid_request("InvalidID")

    @patch("requests.get")
    def test_tax_request(self, mock_get):
        # Mock a response with expected XML structure
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <taxonomyNode>
            <scientificName>TestSpecies</scientificName>
            <commonName>Test Common</commonName>
            <synonym>Test Synonym</synonym>
        </taxonomyNode>
        """
        mock_get.return_value = mock_response

        # Test
        result = self.uniprot.tax_request(9606)
        expected_name = "TestSpecies (Test Common) (Test Synonym)"
        self.assertEqual(result, expected_name)

    @patch("requests.get")
    def test_fast_tax_request_cache(self, mock_get):
        # Populate the cache
        self.uniprot.names[9606] = "Homo sapiens"

        # Test
        result = self.uniprot.fast_tax_request(9606)
        self.assertEqual(result, "Homo sapiens")
        mock_get.assert_not_called()  # Ensure no request was made since it was cached

    @patch("requests.get")
    def test_fast_tax_name_request_cache(self, mock_get):
        # Setup
        self.uniprot.ids["Human"] = (9606, "Homo Sapiens")  # Populate the cache

        # Test
        result = self.uniprot.fast_tax_name_request("Human")
        self.assertEqual(result, (9606, "Homo Sapiens"))
        mock_get.assert_not_called()  # Ensure no request was made due to caching

    @patch("requests.get")
    def test_fast_tax_name_request_dict_cache(self, mock_get):
        # Setup
        self.uniprot.ids["Human"] = (9606, "Homo Sapiens")  # Populate the cache

        # Test
        result = self.uniprot.fast_tax_name_request({"Host Name": "Human"})
        self.assertEqual(result, (9606, "Homo Sapiens"))
        mock_get.assert_not_called()  # Ensure no request was made due to caching

    @patch("requests.get")
    def test_proteome_request_reference(self, mock_get):
        # Mock response with reference proteome
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <proteomes>
            <proteome isReferenceProteome="true" upid="UP000005640" />
        </proteomes>
        """
        mock_get.return_value = mock_response

        # Test
        result = self.uniprot.proteome_request(9606)
        self.assertEqual(result, "UP000005640")

    @patch("requests.get")
    def test_proteome_request_multiple_proteomes(self, mock_get):
        # Mock response with multiple proteomes
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <proteomes>
            <proteome isReferenceProteome="false" upid="UP000005640" />
            <proteome isReferenceProteome="true" upid="UP000005641" />
        </proteomes>
        """
        mock_get.return_value = mock_response

        # Test
        result = self.uniprot.proteome_request(9606)
        self.assertEqual(result, None)

    @patch("requests.get")
    def test_tax_name_request_name(self, mock_get):
        # Mock response for a scientific name
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <taxonomies>
            <taxonomies>
                <taxonomy>
                    <taxonomyId>9606</taxonomyId>
                    <scientificName>Homo sapiens</scientificName>
                </taxonomy>
            </taxonomies>
        </taxonomies>
        """
        mock_get.return_value = mock_response

        # Test
        name, tax_id = self.uniprot.tax_name_request("Homo sapiens")
        self.assertEqual(name, "Homo sapiens")
        self.assertEqual(tax_id, "9606")

    @patch("requests.get")
    def test_tax_name_request_name_dict(self, mock_get):
        # Mock response for a scientific name
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <taxonomies>
            <taxonomies>
                <taxonomy>
                    <taxonomyId>9606</taxonomyId>
                    <scientificName>Homo sapiens</scientificName>
                </taxonomy>
            </taxonomies>
        </taxonomies>
        """
        mock_get.return_value = mock_response

        # Test
        name, tax_id = self.uniprot.tax_name_request({"Host Name": "Homo sapiens"})
        self.assertEqual(name, "Homo sapiens")
        self.assertEqual(tax_id, "9606")

    @patch("requests.get")
    def test_protein_id_request(self, mock_get):
        # Mock response for a scientific name
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = """
        <uniprot>
            <entry>
                <name>ABCD_EFGH</name>
                <accession>P12345</accession>
                <accession>G1SKL2</accession>
            </entry>
        </uniprot>
        """
        mock_get.return_value = mock_response

        # Test
        name, tax_id = self.uniprot.protein_id_request("G1SKL2 ")
        self.assertEqual(name, "ABCD_EFGH")
        self.assertEqual(tax_id, "P12345")

    @patch("requests.get")
    def test_fast_protein_id_request_cache(self, mock_get):
        # Populate the cache
        self.uniprot.uid["P12345"] = ("test", "P12345")

        # Test
        result = self.uniprot.fast_protein_id_request("P12345")
        self.assertEqual(result, ("test", "P12345"))
        mock_get.assert_not_called()  # Ensure no request was made since it was cached


if __name__ == "__main__":
    unittest.main()
