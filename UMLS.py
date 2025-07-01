import requests
from copy import deepcopy


api_url = "https://uts-ws.nlm.nih.gov/rest"
global_payload = {'apiKey': '00a6f297-bd50-4a61-8bc3-9454b3082383'}

#hematochezia not detected 



import pandas as pd

def format_medical_conditions(csv_filename):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    # Initialize an empty list to store the formatted rows
    formatted_rows = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        # Split the "1name_of_disease" column by comma
        diseases = [d.strip() for d in str(row["1name_of_disease"]).split(',')]

        # Check if an abbreviation exists, if not, use the first string from the 1name_of_disease
        abbreviation = row.get("abbreviations", diseases[0].strip())

        # If abbreviation is NaN, use the first disease name
        if pd.isna(abbreviation):
            abbreviation = diseases[0].strip()

        # Ensure abbreviation is a string
        if not isinstance(abbreviation, str):
            abbreviation = str(abbreviation)

        # Create the formatted row as a list
        formatted_row = [diseases, abbreviation]

        # Append the formatted row to the list
        formatted_rows.append(formatted_row)

    # Return the list of formatted rows
    return formatted_rows



terms_to_abbreviations = format_medical_conditions('medical_conditions.csv')

terms_to_abbreviations1 = [
    (["CVA", "cerebrovascular accident", "stroke"], "CVA"),
    (["T2DM", "Diabetes Mellitus, Type 2", "History of diabetes mellitus type 2", "type II diabetes mellitus", "type 2 diabetes mellitus"], "T2DM"),
    (["T1DM", "Diabetes Mellitus, Type 1", "History of diabetes mellitus type 1", "type I diabetes mellitus", "type 1 diabetes mellitus"], "T1DM"),
    (["CKD", "chronic kidney disease", "kidney disease"], "CKD"),
    (["hyperlipidemia", "dyslipidemia"], "HLD"),

    # Cardio
    (["coronary artery disease"], "CAD"),
    (["hypertension"], "HTN"),


    # Neuro
    (["Myasthenia gravis"], "MG"),
    (["Multiple sclerosis"], "MS"),
    (["Parkinson disease"], "Parkinson disease"),
    (["Amyotrophic lateral sclerosis"], "ALS"),
    (["Muscular dystrophy"], "Muscular dystrophy"),
    (["Dementia"], "Dementia"),

    # Musculoskeletal
    (["Cervical osteophytes"], "Cervical osteophytes"),

    # Gastrointestinal
    (["Cricoid webs"], "cricoid webs"),
    (["Phahryngoesophageal diverticulum", "Zenker diverticulum"], "Zenker diverticulum"),
    (["Esophageal strictures"], "Esophageal strictures"),
    (["Eosinophilic esophagitis"], "EoE"),
    (["Achalasia"], "Achalasia"),
    (["Diffuse esophageal spasm"], "Diffuse esophageal spasm"),
    (["Gastroesphageal reflux disease"], "GERD"),
    (["Gastrointestinal hemorrhage"], "GI Bleeding"),

    # Endocrine
    (["Thyroid goiter"], "Thyroid goiter"),
    (["Diabetic neuropathy", "diabetic polyneuropathy"], "Diabetic neuropathy"),
    (["Diabetic nephropathy"], "Diabetic nephropathy"),

    # Hematology
    (["leukopenia"], "leukopenia"),



    # Rheumatic
    (["Sjögren's syndrome"], "Sjögren's syndrome"),
    (["Systemic sclerosis"], "Systemic sclerosis"),
    (["Anti-glomerular basement membrane disease"], "Anti-GBM disease"),

]

terms_to_abbreviations = [[list(map(str.lower, terms)), abbrev] for terms, abbrev in terms_to_abbreviations]

def match_to_abbrev(term):
    """Match a found term to a potential abbreviation contained above """
    term = term.lower()
    for item in terms_to_abbreviations:
        """
        #already an abbreviation or contains it
        if item[1].lower() in term:
            return(item[1])
        """
        #direct match to terms
        if term in item[0]:
            return item[1]
        #contained within one of the terms or vice versa?
        for hit in item[0]:
            if (hit in term) or (term in hit):
                return item[1]
    return False

def cui_to_atoms(cui, include_aui_codes = True):
    search_cui = "/content/current/CUI/" + cui
    response = requests.get(api_url + search_cui + "/atoms?language=ENG", params = global_payload)

    if response.status_code != 200:
        raise Exception("Invalid Search")

    atoms = []

    if include_aui_codes:
        for r in  response.json()["result"]:
            atoms.append((r["name"], r["ui"])) 
    else:
        for r in  response.json()["result"]:
            atoms.append((r["name"]))         

    return atoms



def get_ai_ancestors(ai, include_aui_codes = True):
    if type(ai) != str:
        raise Exception("Invalid Parameter")

    search_ai = "/content/current/AUI/" + ai + "/ancestors"

    payload = deepcopy(global_payload)
    payload["language"] = "ENG"
    payload["pageSize"] = "50"

    response = requests.get(api_url + search_ai, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")

    atoms = []

    if include_aui_codes:
        for r in  response.json()["result"]:
            atoms.append((r["name"], r["ui"])) 
    else:
        for r in  response.json()["result"]:
            atoms.append(r["name"])         
      
    return atoms


def get_ai_parents(ai, include_aui_codes = True):
    if type(ai) != str:
        raise Exception("Invalid Parameter")

    search_ai = "/content/current/AUI/" + ai + "/parents"

    payload = deepcopy(global_payload)
    payload["language"] = "ENG"
    payload["pageSize"] = "50"

    response = requests.get(api_url + search_ai, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")

    atoms = []

    if include_aui_codes:
        for r in  response.json()["result"]:
            atoms.append((r["name"], r["ui"])) 
    else:
        for r in  response.json()["result"]:
            atoms.append(r["name"])         
      
    return atoms

def get_ai_descendants(ai, include_aui_codes = True):
    if type(ai) != str:
        raise Exception("Invalid Parameter")

    search_ai = "/content/current/AUI/" + ai + "/descendants"

    payload = deepcopy(global_payload)
    payload["language"] = "ENG"
    payload["pageSize"] = "50"

    response = requests.get(api_url + search_ai, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")

    atoms = []

    if include_aui_codes:
        for r in  response.json()["result"]:
            atoms.append((r["name"], r["ui"])) 
    else:
        for r in  response.json()["result"]:
            atoms.append(r["name"])         
      
    return atoms





def get_ai_children(ai, include_aui_codes = True):
    if type(ai) != str:
        raise Exception("Invalid Parameter")

    search_ai = "/content/current/AUI/" + ai + "/children"

    payload = deepcopy(global_payload)
    payload["language"] = "ENG"
    payload["pageSize"] = "50"

    response = requests.get(api_url + search_ai, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")

    atoms = []

    if include_aui_codes:
        for r in  response.json()["result"]:
            atoms.append((r["name"], r["ui"])) 
    else:
        for r in  response.json()["result"]:
            atoms.append(r["name"])         
      
    return atoms

def search_umls_closest_concept(search_term, return_top_match_only = True, include_cui = True):

    if type(search_term) != str:
        raise Exception("Invalid Parameter")

    search_link = "/search/current?string=" + search_term

    payload = deepcopy(global_payload)
    payload["language"] = "ENG"
    payload["pageSize"] = "50"
    payload["partialSearch"] = "true"

    response = requests.get(api_url + search_link, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")
    
    results = []

    response = response.json()
    if len(response["result"]["results"]) == 0:
        #TODO: assess this default behaviour
        return()
    else:
        if include_cui:
            for r in response["result"]["results"]:
                results.append((r["name"], r["ui"]))
        else:
            for r in response["result"]["results"]:
                results.append(r["name"])   
        
        if return_top_match_only:
            return results[0]
        else:
            return results

def match_searchterm_to_abbreviation(term):
    """Returns None if one isn't found"""
    if type(term) != str:
        raise Exception("Invalid Parameter")
    
        #Check before searching
    _a = match_to_abbrev(term)
    if _a:
        return _a
    
    closest =  search_umls_closest_concept(term)

    if closest == ():
        return()
        
    atoms = cui_to_atoms(closest[1])
    if len(atoms) == 0:
        return()
    
    #check atom hits
    for a in atoms:
        _a = match_to_abbrev(a[0])
        if _a:
            return _a

    #Check ancestors
    ancestors = False
    for atom in atoms:
        try:
            ancestors = get_ai_parents(atom[1], include_aui_codes = False) 
            break #if succesful leave the loop and move on 
        except:
            continue
    if not ancestors: #search failed to catch anything
        return()

    for a in ancestors:
        _a = match_to_abbrev(a)
        if _a:
            return _a
        
    return()

text_analysis = """
    
Active chronic medical issues that patient has been followed for as outpatient:
Patient Active Problem List
Diagnosis	Code
•	Essential hypertension with goal blood pressure less than 140/90	I10
•	Idiopathic chronic gout of multiple sites without tophus	M1A.09X0
•	Type 2 diabetes mellitus with microalbuminuria, without long-term current use of insulin	E11.29, R80.9
•	Dyslipidemia associated with type 2 diabetes mellitus	E11.69, E78.5
•	History of prostate cancer	Z85.46
•	Chronic flank pain	R10.9, G89.29
•	Obesity (BMI 30.0-34.9)	E66.811
•	Early onset Alzheimer's dementia without behavioral disturbance	G30.0, F02.80
•	Sepsis without acute organ dysfunction (CMS/HCC)	A41.9
•	Acute pyelonephritis	N10
•	Urinary retention	R33.9



    """


for i in text_analysis.splitlines():
    try:
        print(search_umls_closest_concept(i))
    except:
        "Invalid Search"


# Set the CUIs of the two concepts that you want to compare
def child_of_disease(name1, name2, page_number = 1):
    """Returns True if name2 is a child of name1 or they are the same"""
    if name1 == name2:
        return True
    cui1 = search_umls_closest_concept(name1)[1]
    search = f"https://uts-ws.nlm.nih.gov/rest/content/current/CUI/{cui1}/relations"


    payload = deepcopy(global_payload)
    payload['includeRelationLabels'] = 'RB,RN'
    payload['pageNumber'] = page_number

    response = requests.get(search, params = payload)
    if response.status_code != 200:
        raise Exception("Invalid Search")

    # Check the response status code
    if response.status_code == 200:
        # Success!
        num_pages = response.json()['pageCount']
        items = response.json()['result']

        # Print the relationships
        for item in items:
            relate_names = []
            if "relatedFromIdName" in item:
                relate_names += item["relatedFromIdName"] 
            if "relatedIDName" in item:
                relate_names += item["relatedIDName"]
            if item["relationLabel"] == "RN" and name2 in relate_names:
                return True
        if page_number < num_pages:
            return child_of_disease(name1, name2, page_number + 1)
        else:
            return False
                
    else:
        return None

'''print(child_of_disease("Diabetes Mellitus, Non-Insulin-Dependent", "Non-insulin-dependent diabetes mellitus with renal complications"))'''