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
        try:
            # Updated to use the more reliable new API format
            base_url = "https://www.ebi.ac.uk/chembl/api/data"
            
            # Try multiple search approaches
            approaches = [
                # First approach: search by name in molecule endpoint
                f"{base_url}/molecule/search?molecule_structures__canonical_smiles__flexmatch={drug_name}",
                # Second approach: direct text search
                f"{base_url}/molecule/search?q={drug_name}",
                # Third approach: use the molecule concept
                f"{base_url}/drug_mechanism?molecule_chembl_id__molecule__pref_name__icontains={drug_name}"
            ]
            
            response = None
            successful_url = None
            
            # Try each approach until one works
            for url in approaches:
                print(f"Trying ChEMBL URL: {url}")
                try:
                    response = requests.get(url, timeout=15, headers={'Accept': 'application/json'})
                    if response.status_code == 200 and response.text:
                        try:
                            # Check if the response is valid JSON
                            data = response.json()
                            if 'molecules' in data or 'mechanisms' in data or 'drug_mechanisms' in data:
                                successful_url = url
                                break
                        except ValueError:
                            # Not valid JSON, continue to next approach
                            print(f"Response not valid JSON for URL: {url}")
                            continue
                except requests.exceptions.RequestException as e:
                    print(f"Request failed for URL {url}: {str(e)}")
                    continue
            
            # If we found a working approach, return the data
            if successful_url and response and response.status_code == 200:
                print(f"Successful ChEMBL request using: {successful_url}")
                return response.json()
            else:
                # Fall back to a generic search if all else fails
                backup_url = f"https://www.ebi.ac.uk/chembl/api/data/molecule?limit=3&offset=0&q={drug_name}"
                print(f"Trying backup ChEMBL URL: {backup_url}")
                response = requests.get(backup_url, timeout=15, headers={'Accept': 'application/json'})
                
                if response.status_code == 200 and response.text:
                    try:
                        return response.json()
                    except ValueError:
                        return {"error": "Invalid JSON response from ChEMBL API"}
                
                return {"error": f"All ChEMBL API approaches failed with status {response.status_code if response else 'unknown'}"}
                
        except requests.exceptions.RequestException as e:
            print(f"ChEMBL API Error: {str(e)}")
            return {"error": f"Error accessing ChEMBL API: {str(e)}"}
        except Exception as e:
            print(f"Unexpected error in ChEMBL search: {str(e)}")
            return {"error": f"Unexpected error in ChEMBL search: {str(e)}"}

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
        alternatives = []
        print(f"Searching for alternatives to {drug_name}...")
        
        try:
            # First get the rxcui (RxNorm Concept Unique Identifier) for the drug
            rxcui_url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
            print(f"Fetching RxCUI from {rxcui_url}")
            rxcui_response = requests.get(rxcui_url, timeout=10)
            rxcui_response.raise_for_status()
            rxcui_data = rxcui_response.json()
            
            if 'idGroup' in rxcui_data and 'rxnormId' in rxcui_data['idGroup'] and rxcui_data['idGroup']['rxnormId']:
                rxcui = rxcui_data['idGroup']['rxnormId'][0]
                print(f"Found RxCUI: {rxcui}")
                
                # Then get alternatives with the same class
                alt_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={rxcui}&relaSource=ATC"
                print(f"Fetching drug classes from {alt_url}")
                alt_response = requests.get(alt_url, timeout=10)
                alt_response.raise_for_status()
                alt_data = alt_response.json()
                
                # Try multiple relation sources if the first one doesn't yield results
                relation_sources = ["ATC", "MESHPA", "MEDRT", "FDASPL"]
                
                for rel_source in relation_sources:
                    if alternatives:  # If we already found alternatives, break the loop
                        break
                        
                    alt_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui={rxcui}&relaSource={rel_source}"
                    print(f"Trying relation source {rel_source}")
                    alt_response = requests.get(alt_url, timeout=10)
                    
                    if alt_response.status_code == 200:
                        alt_data = alt_response.json()
                        
                        if 'rxclassDrugInfoList' in alt_data and 'rxclassDrugInfo' in alt_data['rxclassDrugInfoList']:
                            for drug_class in alt_data['rxclassDrugInfoList']['rxclassDrugInfo']:
                                if 'rxclassMinConceptItem' in drug_class:
                                    class_name = drug_class['rxclassMinConceptItem']['className']
                                    class_id = drug_class['rxclassMinConceptItem']['classId']
                                    print(f"Found drug class: {class_name} (ID: {class_id})")
                                    
                                    # Now get drugs in this class
                                    class_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId={class_id}&relaSource={rel_source}"
                                    class_response = requests.get(class_url, timeout=10)
                                    class_response.raise_for_status()
                                    class_data = class_response.json()
                                    
                                    if 'drugMemberGroup' in class_data and 'drugMember' in class_data['drugMemberGroup']:
                                        drug_members = class_data['drugMemberGroup']['drugMember']
                                        # Handle both list and dict responses
                                        if not isinstance(drug_members, list):
                                            drug_members = [drug_members]
                                            
                                        for member in drug_members:
                                            if 'minConcept' in member and member['minConcept']['name'].lower() != drug_name.lower():
                                                alt_name = member['minConcept']['name']
                                                print(f"Found alternative: {alt_name}")
                                                alternatives.append({
                                                    'name': alt_name,
                                                    'class': class_name
                                                })
            
            # Add direct brand/generic name alternatives if available
            direct_alternatives = APIHandler._get_direct_alternatives(drug_name)
            for alt in direct_alternatives:
                if alt not in alternatives:
                    alternatives.append(alt)
            
            # If no alternatives found via RxCUI methods, try fallback method
            if not alternatives:
                print("No alternatives found via RxNorm, trying fallback method")
                fallback_alternatives = APIHandler._get_alternatives_fallback(drug_name)
                alternatives.extend(fallback_alternatives)
                
            # Remove duplicates while preserving order
            unique_alternatives = []
            seen_names = set()
            for alt in alternatives:
                if alt['name'].lower() not in seen_names:
                    seen_names.add(alt['name'].lower())
                    unique_alternatives.append(alt)
                    
            print(f"Found {len(unique_alternatives)} total alternatives")
            return unique_alternatives[:15]  # Return up to 15 alternatives
        
        except requests.exceptions.RequestException as e:
            print(f"API Error when fetching alternatives via RxNorm: {str(e)}")
            # Try fallback methods if primary method fails
            fallback_alternatives = APIHandler._get_alternatives_fallback(drug_name)
            direct_alternatives = APIHandler._get_direct_alternatives(drug_name)
            combined_alternatives = fallback_alternatives + direct_alternatives
            
            # Remove duplicates
            unique_alternatives = []
            seen_names = set()
            for alt in combined_alternatives:
                if alt['name'].lower() not in seen_names:
                    seen_names.add(alt['name'].lower())
                    unique_alternatives.append(alt)
                    
            return unique_alternatives[:15]

    @staticmethod
    def _get_direct_alternatives(drug_name):
        """
        Find alternative drugs by brand/generic relationships or other direct connections.
        """
        alternatives = []
        try:
            # Try to get brand name alternatives
            url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'idGroup' in data and 'rxnormId' in data['idGroup'] and data['idGroup']['rxnormId']:
                    rxcui = data['idGroup']['rxnormId'][0]
                    
                    # Get related drugs by brand/generic
                    related_url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/related.json?rela=tradename_of+has_tradename"
                    related_response = requests.get(related_url, timeout=5)
                    
                    if related_response.status_code == 200:
                        related_data = related_response.json()
                        
                        if 'relatedGroup' in related_data and 'conceptGroup' in related_data['relatedGroup']:
                            for group in related_data['relatedGroup']['conceptGroup']:
                                if 'conceptProperties' in group:
                                    for prop in group['conceptProperties']:
                                        if prop['name'].lower() != drug_name.lower():
                                            alternatives.append({
                                                'name': prop['name'],
                                                'class': 'Related Brand/Generic'
                                            })
            
            return alternatives
        except Exception as e:
            print(f"Error getting direct alternatives: {str(e)}")
            return []

    @staticmethod
    def _get_alternatives_fallback(drug_name):
        """
        Fallback method to find drug alternatives using OpenFDA when RxNorm fails.
        """
        alternatives = []
        try:
            # Get information about the drug to determine its class
            url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}&limit=1"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0 and 'openfda' in data['results'][0]:
                openfda = data['results'][0]['openfda']
                
                # Try to get the drug class
                search_terms = []
                if 'pharm_class_epc' in openfda:
                    search_terms.extend(openfda['pharm_class_epc'])
                if 'pharm_class_cs' in openfda:
                    search_terms.extend(openfda['pharm_class_cs'])
                if 'pharm_class_moa' in openfda:
                    search_terms.extend(openfda['pharm_class_moa'])
                
                if search_terms:
                    # Use the first drug class to find alternatives
                    class_term = search_terms[0].split('[')[0].strip()
                    
                    # Search for drugs in this class
                    class_url = f"https://api.fda.gov/drug/label.json?search=openfda.pharm_class_epc:{class_term}+OR+openfda.pharm_class_cs:{class_term}+OR+openfda.pharm_class_moa:{class_term}&limit=10"
                    class_response = requests.get(class_url, timeout=5)
                    class_data = class_response.json()
                    
                    if 'results' in class_data:
                        for result in class_data['results']:
                            if 'openfda' in result and 'generic_name' in result['openfda']:
                                alt_name = result['openfda']['generic_name'][0]
                                if alt_name.lower() != drug_name.lower():
                                    alternatives.append({
                                        'name': alt_name,
                                        'class': class_term
                                    })
            
            return alternatives
        except requests.exceptions.RequestException as e:
            print(f"API Error in fallback alternatives search: {str(e)}")
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

    @staticmethod
    def get_drug_allergies(drug_name):
        """
        Retrieves potential allergic reactions for a specific drug from OpenFDA.
        """
        try:
            url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}+OR+openfda.brand_name:{drug_name}&limit=1"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            allergies = {
                "common_reactions": [],
                "severe_reactions": [],
                "warnings": []
            }
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                # Extract adverse reactions that might indicate allergies
                if 'adverse_reactions' in result:
                    allergies["common_reactions"] = result['adverse_reactions']
                
                # Extract warnings about hypersensitivity or allergic reactions
                if 'warnings' in result:
                    allergies["warnings"] = [warning for warning in result['warnings'] 
                                          if 'allerg' in warning.lower() or 
                                             'hypersensitivity' in warning.lower()]
                
                # Extract boxed warnings related to allergies
                if 'boxed_warning' in result:
                    allergies["severe_reactions"] = [warning for warning in result['boxed_warning'] 
                                                if 'allerg' in warning.lower() or 
                                                   'hypersensitivity' in warning.lower() or
                                                   'anaphyla' in warning.lower()]
                
                # Check contraindications for allergy information
                if 'contraindications' in result:
                    for contra in result['contraindications']:
                        if 'allerg' in contra.lower() or 'hypersensitivity' in contra.lower():
                            allergies["warnings"].append(contra)
            
            return allergies
        except requests.exceptions.RequestException as e:
            print(f"API Error when fetching drug allergies: {e}")
            return {
                "common_reactions": [],
                "severe_reactions": [],
                "warnings": ["Unable to retrieve allergy information due to API error"]
            }
    
    def search_drug_or_disease(self, query, search_type="drug"):
        """
        Searches multiple APIs for a given drug or disease name.
        Returns combined results with indications and alternatives for drugs,
        or recommended medications for diseases.
        """
        results = {}

        # Helper function to safely call APIs and handle errors
        def safe_api_call(api_func, api_name, *args):
            try:
                data = api_func(*args)
                if data and not (isinstance(data, dict) and "error" in data):
                    return data
                elif isinstance(data, dict) and "error" in data:  # Fixed: removed extra closing parenthesis
                    print(f"{api_name} API Error: {data['error']}")
                return None
            except Exception as e:
                print(f"Error in {api_name} API call: {str(e)}")
                return None

        # Handle different search types
        if search_type == "disease":
            # For disease searches, focus on finding drugs that treat the disease
            drugs_for_disease = safe_api_call(self.get_drugs_for_disease, "Disease Medications", query)
            if drugs_for_disease:
                results["Recommended_Medications"] = drugs_for_disease
            
            # Still try to get some general disease info
            disease_info = safe_api_call(self.search_openfda, "Disease OpenFDA", query)
            if disease_info:
                results["Disease_Information"] = disease_info
                
        else:
            # Regular drug search flow with improved error handling
            indications = safe_api_call(self.get_drug_indications, "Drug Indications", query)
            if indications:
                results["Indications"] = indications
                
            alternatives = safe_api_call(self.get_drug_alternatives, "Drug Alternatives", query)
            if alternatives:
                results["Alternatives"] = alternatives
                
            # Get drug allergies information
            allergies = safe_api_call(self.get_drug_allergies, "Drug Allergies", query)
            if allergies:
                results["Allergies"] = allergies

            # OpenFDA data
            openfda_data = safe_api_call(self.search_openfda, "OpenFDA", query)
            if openfda_data:
                results["OpenFDA"] = openfda_data

            # RxNorm data
            rxnorm_data = safe_api_call(self.search_rxnorm, "RxNorm", query)
            if rxnorm_data:
                results["RxNorm"] = rxnorm_data

            # PubChem data
            pubchem_data = safe_api_call(self.search_pubchem, "PubChem", query)
            if pubchem_data:
                results["PubChem"] = pubchem_data

            # ChEMBL data - using our improved method
            chembl_data = safe_api_call(self.search_chembl, "ChEMBL", query)
            if chembl_data:
                results["ChEMBL"] = chembl_data

            # KEGG data
            kegg_data = safe_api_call(self.search_kegg, "KEGG", query)
            if kegg_data:
                results["KEGG"] = kegg_data

        # Return available data or message if none found
        return results if results else {"message": f"No data found for {query}."}
