import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///medlife.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENFDA_API_URL = "https://api.fda.gov/drug/label.json?search=reactionmeddrapt:"
    RXNORM_API_URL = "https://rxnav.nlm.nih.gov/REST/rxcui.json?name="
    PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
    CHEMBL_API_URL = "https://www.ebi.ac.uk/chembl/api/data/"
    KEGG_API_URL = "https://rest.kegg.jp/link/drug/"
    PHARMGKB_API_URL = "https://api.pharmgkb.org/v1/data/"
