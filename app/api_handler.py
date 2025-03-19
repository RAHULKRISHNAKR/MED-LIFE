import requests
from config import Config

class APIHandler:
    @staticmethod
    def _fetch_data(url, return_text=False):
        """
        Helper function to make API requests and handle errors.
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text if return_text else response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")  # Debugging log
            return None  # Returns None if API call fails

    @staticmethod
    def search_openfda(drug_name):
        """
        Searches OpenFDA API for drug information.
        """
        return APIHandler._fetch_data(f"{Config.OPENFDA_API_URL}{drug_name}")

    @staticmethod
    def search_rxnorm(drug_name):
        """
        Searches RxNorm API for drug ingredient details.
        """
        return APIHandler._fetch_data(f"{Config.RXNORM_API_URL}{drug_name}")

    @staticmethod
    def search_pubchem(drug_name):
        """
        Searches PubChem API for drug interactions and properties.
        """
        return APIHandler._fetch_data(Config.PUBCHEM_API_URL.format(drug_name))

    @staticmethod
    def search_chembl(drug_name):
        """
        Searches ChEMBL API for drug mechanisms.
        """
        return APIHandler._fetch_data(f"{Config.CHEMBL_API_URL}mechanism.json?molecule_chembl_id={drug_name}")

    @staticmethod
    def search_kegg(drug_name):
        """
        Searches KEGG API for drug pathways.
        """
        return APIHandler._fetch_data(f"{Config.KEGG_API_URL}{drug_name}", return_text=True)

    @staticmethod
    def search_pharmgkb(drug_name):
        """
        Searches PharmGKB API for pharmacogenomics information.
        """
        return APIHandler._fetch_data(f"{Config.PHARMGKB_API_URL}drug/{drug_name}")

    def search_drug_or_disease(self, query):
        """
        Searches multiple APIs for a given drug or disease name.
        Returns combined results.
        """
        results = {}

        # Fetch data from each API
        openfda_data = self.search_openfda(query)
        rxnorm_data = self.search_rxnorm(query)
        pubchem_data = self.search_pubchem(query)
        chembl_data = self.search_chembl(query)
        kegg_data = self.search_kegg(query)
        pharmgkb_data = self.search_pharmgkb(query)

        # Combine results
        if openfda_data:
            results["OpenFDA"] = openfda_data
        if rxnorm_data:
            results["RxNorm"] = rxnorm_data
        if pubchem_data:
            results["PubChem"] = pubchem_data
        if chembl_data:
            results["ChEMBL"] = chembl_data
        if kegg_data:
            results["KEGG"] = kegg_data
        if pharmgkb_data:
            results["PharmGKB"] = pharmgkb_data

        return results if results else {"message": "No data found for the given query."}
