"""
Package for UniProt API services

General Remark:
- Functions including the word 'fast' safe each quired name into a dictionary in the
cache to limit send requests.
- If returned answers from the UniProt services are not unique, the returned value
will be None even if there are multiple feasible solutions.

Author: Michael
"""

# TODO migrate function from processDB.py here
import requests
import xmltodict
from multipledispatch import dispatch


class uniprot_request:
    def __init__(self):
        self.names = {}
        self.proteomes = {}
        self.ids = {}
        self.uid = {}

    @staticmethod
    def _get_name(tax: dict) -> str:
        """Creates full taxonomical name using all annotated naming fields:
        Scientific name, Common name, Synonymes (see UniProt Taxonomy);

        Args:
            tax (dict): Dictionary holding all names

        Returns:
            str: Full taxonomical name
        """
        if "commonName" in tax.keys() and "synonym" in tax.keys():
            return f"{tax['scientificName']} ({tax['commonName']}) ({tax['synonym']})"
        elif "commonName" in tax.keys():
            return f"{tax['scientificName']} ({tax['commonName']})"
        elif "synonym" in tax.keys():
            return f"{tax['scientificName']} ({tax['synonym']})"
        else:
            return f"{tax['scientificName']}"

    def uid_request(self, uid: str) -> dict:
        """Querries information about a single UniProt protein ID

        Args:
            uid (str): UniProt protein ID string

        Returns:
            dict: Dictionary of xml response holding all information
        """
        requestURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&"
        requestURL += "keywords=" + uid

        r = requests.get(requestURL, headers={"Accept": "application/xml"})

        if not r.ok:
            r.raise_for_status()

        tax = xmltodict.parse(r.text)
        return tax

    def fast_tax_request(self, id: int) -> str:
        """Returns full taxonomical name for a given taxonomical ID
        with reusing already quired IDs

        Args:
            id (int): NCBI taxonomical ID

        Returns:
            str: Full taxonomical name
        """
        if id in self.names.keys():
            return self.names[id]
        else:
            value = self.tax_request(id)
            self.names[id] = value
            return value

    def tax_request(self, id: int) -> str:
        """Returns full taxonomical name for a given taxonomical ID

        Args:
            id (int): NCBI taxonomical ID

        Returns:
            str: Full taxonomical name
        """
        requestURL = "https://www.ebi.ac.uk/proteins/api/taxonomy/id/" + str(id)

        try:
            r = requests.get(requestURL, headers={"Accept": "application/xml"})

            if not r.ok:
                r.raise_for_status()

            tax = xmltodict.parse(r.text)["taxonomyNode"]
            return self._get_name(tax)
        except Exception as e:
            # print(e, id, end="\r")
            return None

    @dispatch(dict)
    def fast_tax_name_request(self, ids: dict) -> tuple:
        """Returns for dictionary with Keys 'Host Name', 'Host Common Name'
        a tuple of (Taxon ID, Full scientific name) with reusing already quired IDs

        Args:
            ids (dict): Dictionary with Keys 'Host Name', 'Host Common Name'

        Returns:
            dict: (Taxon ID, Full scientific name)
        """
        id = ids["Host Name"]
        if id in self.ids.keys():
            return self.ids[id]
        else:
            value = self.tax_name_request(ids)
            self.ids[id] = value
            return value

    @dispatch(dict)
    def tax_name_request(self, names: dict) -> tuple:
        """Returns for dictionary with Keys 'Host Name', 'Host Common Name'
        a tuple of (Taxon ID, Full scientific name)

        Args:
            ids (dict): Dictionary with Keys 'Host Name', 'Host Common Name'

        Returns:
            dict: (Taxon ID, Full scientific name)
        """

        def send(name: str, fieldname: str = "SCIENTIFICNAME"):
            requestURL = "https://www.ebi.ac.uk/proteins/api/taxonomy/name/"
            requestURL += name.strip().replace(" ", "%20")
            requestURL += (
                "?pageNumber=1&pageSize=100&searchType=EQUALSTO&fieldName=" + fieldname
            )

            r = requests.get(requestURL, headers={"Accept": "application/xml"})

            if not r.ok:
                r.raise_for_status()
            return r.text

        try:
            r = send(names["Host Name"])
        except Exception as e:
            try:
                r = send(names["Host Common Name"], "COMMONNAME")
            except Exception as e:
                try:
                    r = send(names["Host Name"], "COMMONNAME")
                except Exception:
                    # print(names)
                    return None, None

        tax = xmltodict.parse(r)["taxonomies"]["taxonomies"]["taxonomy"]
        if type(tax) is list:
            # print(names)
            return None, None

        name = self._get_name(tax)

        id = tax["taxonomyId"]
        return name, id

    @dispatch(str)
    def fast_tax_name_request(self, id: str) -> dict:
        """Returns for incomplete or common names of a species a
        a tuple of (Taxon ID, Full scientific name) with reusing already quired IDs

        Args:
            id (str): Incomplete name or common name of a species

        Returns:
            dict: (Taxon ID, Full scientific name)
        """
        if id in self.ids.keys():
            return self.ids[id]
        else:
            value = self.tax_name_request(id)
            self.ids[id] = value
            return value

    @dispatch(str)
    def tax_name_request(self, name: str) -> tuple:
        """Returns for incomplete or common names of a species a
        a tuple of (Taxon ID, Full scientific name)

        Args:
            id (str): Incomplete name or common name of a species

        Returns:
            dict: (Taxon ID, Full scientific name)
        """

        def send(name: str, fieldname: str = "SCIENTIFICNAME"):
            requestURL = "https://www.ebi.ac.uk/proteins/api/taxonomy/name/"
            requestURL += name.strip().replace(" ", "%20")
            requestURL += (
                "?pageNumber=1&pageSize=100&searchType=EQUALSTO&fieldName=" + fieldname
            )

            r = requests.get(requestURL, headers={"Accept": "application/xml"})

            if not r.ok:
                r.raise_for_status()
            return r.text

        try:
            r = send(name)
        except Exception as e:
            try:
                r = send(name, "COMMONNAME")
            except Exception as e:
                return None, None

        tax = xmltodict.parse(r)["taxonomies"]["taxonomies"]["taxonomy"]
        if type(tax) is list:
            # print(name)
            return None, None

        name = self._get_name(tax)

        id = tax["taxonomyId"]
        return name, id

    def fast_proteome_request(self, id: int) -> str:
        """Returns the proteome ID of a given Taxon ID
        with reusing quired IDs

        Args:
            id (int): Taxon ID

        Returns:
            str: Proteome ID
        """
        if id in self.proteomes.keys():
            return self.proteomes[id]
        else:
            value = self.proteome_request(id)
            self.proteomes[id] = value
            return value

    def proteome_request(self, id: int) -> str:
        """Returns the proteome ID of a given Taxon ID

        Args:
            id (int): Taxon ID

        Returns:
            str: Proteome ID
        """
        requestURL = (
            "https://www.ebi.ac.uk/proteins/api/proteomes?offset=0&taxid=" + str(id)
        )
        try:
            r = requests.get(requestURL, headers={"Accept": "application/xml"})

            if not r.ok:
                r.raise_for_status()

            proteomes = xmltodict.parse(r.text)["proteomes"]
            # check for None
            if proteomes is None:
                return None
            # check for reference proteome
            if type(proteomes["proteome"]) == list:
                for p in proteomes["proteome"]:
                    if p["isReferenceProteome"]:
                        return p["@upid"]
            else:
                return proteomes["proteome"]["@upid"]
            # else highest scoring
            return proteomes["proteome"][0]["@upid"]
        except Exception as e:
            return None

    def protein_id_request(self, id: str) -> str:
        """Returns the UniProt name and first accession number of a protein.

        Args:
            id (str): Either the UniProt protein name or the protein accession number

        Returns:
            str: UniProt name and first accession number of the protein
        """

        requestURL = f"https://rest.uniprot.org/uniprotkb/{str(id).strip()}.xml"
        try:
            r = requests.get(requestURL, headers={"Accept": "application/xml"})

            values = xmltodict.parse(r.text)["uniprot"]["entry"]
            if type(values["accession"]) == list:
                return values["name"], values["accession"][0]
            else:
                return values["name"], values["accession"]
        except Exception:
            return None, None

    def fast_protein_id_request(self, id: int) -> str:
        """Returns the UniProt name and first accession number of a protein
        with reusing quired IDs.

        Args:
            id (str): Either the UniProt protein name or the protein accession number

        Returns:
            str: UniProt name and first accession number of the protein
        """
        if id in self.uid.keys():
            return self.uid[id]
        else:
            value = self.fast_protein_id_request(id)
            self.uid[id] = value
            return value
