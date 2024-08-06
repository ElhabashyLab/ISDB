"""
Package for Uniprot taxonomical services

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

    @staticmethod
    def _get_name(tax: dict) -> str:
        if "commonName" in tax.keys() and "synonym" in tax.keys():
            return f"{tax['scientificName']} ({tax['commonName']}) ({tax['synonym']})"
        elif "commonName" in tax.keys():
            return f"{tax['scientificName']} ({tax['commonName']})"
        elif "synonym" in tax.keys():
            return f"{tax['scientificName']} ({tax['synonym']})"
        else:
            return f"{tax['scientificName']}"

    def uid_request(self, uid: str) -> str:
        requestURL = "https://www.ebi.ac.uk/proteins/api/proteins?offset=0&size=100&"
        requestURL += "keywords=" + uid

        r = requests.get(requestURL, headers={"Accept": "application/xml"})

        if not r.ok:
            r.raise_for_status()

        tax = xmltodict.parse(r.text)
        return tax

    def fast_tax_request(self, id) -> str:
        if id in self.names.keys():
            return self.names[id]
        else:
            value = self.tax_request(id)
            self.names[id] = value
            return value

    def tax_request(self, id: int) -> str:
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
    def fast_tax_name_request(self, ids: dict) -> str:
        id = ids["Host Name"]
        if id in self.ids.keys():
            return self.ids[id]
        else:
            value = self.tax_name_request(ids)
            self.ids[id] = value
            return value

    @dispatch(dict)
    def tax_name_request(self, names: dict) -> tuple:
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
    def fast_tax_name_request(self, id: str) -> str:
        if id in self.ids.keys():
            return self.ids[id]
        else:
            value = self.tax_name_request(id)
            self.ids[id] = value
            return value

    @dispatch(str)
    def tax_name_request(self, name: str) -> tuple:
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

    def fast_proteome_request(self, id) -> str:
        if id in self.proteomes.keys():
            return self.proteomes[id]
        else:
            value = self.proteome_request(id)
            self.proteomes[id] = value
            return value

    def proteome_request(self, id: int) -> str:
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
            # print(e, id)
            # print(xmltodict.parse(r.text))
            return
