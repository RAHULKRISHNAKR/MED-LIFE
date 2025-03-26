import requests
from config import Config

class APIHandler:
    @staticmethod
    def _fetch_data(url, return_text=False):
        """
        Helper function to make API requests and handle errors.
        """
        try:
            response = requests.get(url, timeout=10)
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
        # Fix the OpenFDA search URL - use proper search term for drugs
        url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}&limit=5"
        return APIHandler._fetch_data(url)

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
        # Fix the PubChem URL to include proper endpoint for drug search
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/JSON"
        return APIHandler._fetch_data(url)

    @staticmethod
    def search_chembl(drug_name):
        """
        Searches ChEMBL API for drug mechanisms.
        """
        # For ChEMBL, we need a ChEMBL ID which is not directly possible from a name
        # Let's use a simplified search
        url = f"https://www.ebi.ac.uk/chembl/api/data/molecule?molecule_structures__canonical_smiles__flexmatch={drug_name}"
        return APIHandler._fetch_data(url)

    @staticmethod
    def search_kegg(drug_name):
        """
        Searches KEGG API for drug pathways.
        """
        # Fix KEGG API format (they typically use lower case)
        url = f"https://rest.kegg.jp/find/drug/{drug_name.lower()}"
        return APIHandler._fetch_data(url, return_text=True)

    @staticmethod
    def search_pharmgkb(drug_name):
        """
        Searches PharmGKB API for pharmacogenomics information.
        """
        # PharmGKB API is tricky and may not be publicly accessible in this way
        # We'll skip it for now
        return None

    @staticmethod
    def get_drug_indications(drug_name):
        """
        Retrieves disease indications for a specific drug from OpenFDA.
        """
        try:
            url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}&limit=1"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                # Extract indications_and_usage if available
                if 'indications_and_usage' in data['results'][0]:
                    return data['results'][0]['indications_and_usage']
                # If not available, get purpose instead
                if 'purpose' in data['results'][0]:
                    return data['results'][0]['purpose']
            return ["Indication information not available"]
        except requests.exceptions.RequestException as e:
            print(f"API Error when fetching indications: {e}")
            return ["Unable to retrieve indications due to API error"]

    @staticmethod
    def get_drug_alternatives(drug_name):
        """
        Retrieves alternative drugs in the same class from RxNorm.
        """
        try:
            # First get the rxcui (RxNorm Concept Unique Identifier) for the drug
            rxcui_url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
            rxcui_response = requests.get(rxcui_url, timeout=5)
            rxcui_response.raise_for_status()
            rxcui_data = rxcui_response.json()
            
            if 'idGroup' in rxcui_data and 'rxnormId' in rxcui_data['idGroup'] and rxcui_data['idGroup']['rxnormId']:
                rxcui = rxcui_data['idGroup']['rxnormId'][0]
                
                # Then get alternatives with the same class
                alt_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={rxcui}&relaSource=MEDRT"
                alt_response = requests.get(alt_url, timeout=5)
                alt_response.raise_for_status()
                alt_data = alt_response.json()
                
                alternatives = []
                if 'rxclassDrugInfoList' in alt_data and 'rxclassDrugInfo' in alt_data['rxclassDrugInfoList']:
                    for drug_class in alt_data['rxclassDrugInfoList']['rxclassDrugInfo']:
                        if 'rxclassMinConceptItem' in drug_class:
                            class_name = drug_class['rxclassMinConceptItem']['className']
                            # Now get drugs in this class
                            class_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId={drug_class['rxclassMinConceptItem']['classId']}&relaSource=MEDRT"
                            class_response = requests.get(class_url, timeout=5)
                            class_data = class_response.json()
                            
                            if 'drugMemberGroup' in class_data and 'drugMember' in class_data['drugMemberGroup']:
                                for member in class_data['drugMemberGroup']['drugMember']:
                                    if 'minConcept' in member and member['minConcept']['name'].lower() != drug_name.lower():
                                        alternatives.append({
                                            'name': member['minConcept']['name'],
                                            'class': class_name
                                        })
                return alternatives[:10]  # Return up to 10 alternatives
            return []
        except requests.exceptions.RequestException as e:
            print(f"API Error when fetching alternatives: {e}")
            return []

    @staticmethod
    def get_drugs_for_disease(disease_name):
        """
        Retrieves drugs recommended for a specific disease from OpenFDA.
        """
        try:
            # Use OpenFDA API to search for drugs that mention this disease in their indications
            url = f"https://api.fda.gov/drug/label.json?search=indications_and_usage:{disease_name}&limit=20"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            recommended_drugs = []
            
            if 'results' in data and len(data['results']) > 0:
                for result in data['results']:
                    drug_info = {}
                    
                    # Extract drug name
                    if 'openfda' in result:
                        if 'brand_name' in result['openfda']:
                            drug_info['brand_name'] = result['openfda']['brand_name'][0]
                        if 'generic_name' in result['openfda']:
                            drug_info['generic_name'] = result['openfda']['generic_name'][0]
                        if 'manufacturer_name' in result['openfda']:
                            drug_info['manufacturer'] = result['openfda']['manufacturer_name'][0]
                    
                    # Extract relevant sections about the disease
                    if 'indications_and_usage' in result:
                        relevant_text = ' '.join(result['indications_and_usage'])
                        # First 200 characters of indication text that mentions the disease
                        disease_pos = relevant_text.lower().find(disease_name.lower())
                        if disease_pos != -1:
                            start = max(0, disease_pos - 50)
                            end = min(len(relevant_text), disease_pos + 150)
                            drug_info['relevance'] = "..." + relevant_text[start:end] + "..."
                    
                    if drug_info.get('brand_name') or drug_info.get('generic_name'):
                        recommended_drugs.append(drug_info)
            
            return recommended_drugs
        except requests.exceptions.RequestException as e:
            print(f"API Error when fetching drugs for disease: {e}")
            return []

    def search_drug_or_disease(self, query, search_type="drug"):
        """
        Searches multiple APIs for a given drug or disease name.
        Returns combined results with indications and alternatives for drugs,
        or recommended medications for diseases.
        """
        results = {}

        # Handle different search types
        if search_type == "disease":
            # For disease searches, focus on finding drugs that treat the disease
            drugs_for_disease = self.get_drugs_for_disease(query)
            if drugs_for_disease:
                results["Recommended_Medications"] = drugs_for_disease
            
            # Still try to get some general disease info
            try:
                disease_info = self.search_openfda(query)
                if disease_info:
                    results["Disease_Information"] = disease_info
            except Exception as e:
                print(f"Error fetching disease info: {str(e)}")
                
        else:
            # Regular drug search flow - continue with existing code
            # Get disease indications and alternatives for drugs
            indications = self.get_drug_indications(query)
            alternatives = self.get_drug_alternatives(query)

            # Add indications and alternatives first
            if indications:
                results["Indications"] = indications
            if alternatives:
                results["Alternatives"] = alternatives

            # Try to fetch data from other APIs - catch any exceptions to prevent 500 errors
            try:
                openfda_data = self.search_openfda(query)
                if openfda_data:
                    results["OpenFDA"] = openfda_data
            except Exception as e:
                print(f"Error in OpenFDA search: {str(e)}")

            try:
                rxnorm_data = self.search_rxnorm(query)
                if rxnorm_data:
                    results["RxNorm"] = rxnorm_data
            except Exception as e:
                print(f"Error in RxNorm search: {str(e)}")

            try:
                pubchem_data = self.search_pubchem(query)
                if pubchem_data:
                    results["PubChem"] = pubchem_data
            except Exception as e:
                print(f"Error in PubChem search: {str(e)}")

            try:
                chembl_data = self.search_chembl(query)
                if chembl_data:
                    results["ChEMBL"] = chembl_data
            except Exception as e:
                print(f"Error in ChEMBL search: {str(e)}")

            try:
                kegg_data = self.search_kegg(query)
                if kegg_data:
                    results["KEGG"] = kegg_data
            except Exception as e:
                print(f"Error in KEGG search: {str(e)}")

        # Return available data or message if none found
        return results if results else {"message": f"No data found for {query}."}
