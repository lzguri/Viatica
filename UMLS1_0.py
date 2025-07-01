import pandas as pd
import re

def load_csv_diseases(csv_filename):
    """
    Load one CSV and return a list of (synonyms_list, canonical_name).
    Assumes column "1name_of_disease" contains comma-separated names.
    """
    df = pd.read_csv(csv_filename)
    mappings = []
    for _, row in df.iterrows():
        # split and lower-case all synonyms
        names = [d.strip().lower() for d in str(row["1name_of_disease"]).split(',')]
        canonical = names[0]
        mappings.append((names, canonical))
    return mappings

def load_multiple_csv_diseases(csv_filenames):
    """
    Load multiple CSVs and merge their mappings, deduplicating by canonical name.
    """
    merged = {}
    for fn in csv_filenames:
        for synonyms, canonical in load_csv_diseases(fn):
            if canonical not in merged:
                merged[canonical] = set(synonyms)
            else:
                merged[canonical].update(synonyms)
    # back to list-of-(synonyms, canonical)
    return [(list(syns), canon) for canon, syns in merged.items()]

def detect_and_map_conditions(text, csv_filenames):
    """
    Scans `text` for any synonym in any of the CSVs and returns
    a dict: { found_term: canonical_name }.
    If nothing is found, returns an empty dict.
    """
    mappings = load_multiple_csv_diseases(csv_filenames)
    found = {}
    text_lower = text.lower()
    for synonyms, canonical in mappings:
        for syn in synonyms:
            # word-boundary match
            if re.search(r'\b' + re.escape(syn) + r'\b', text_lower):
                found[syn] = canonical
                break
    return found

if __name__ == "__main__":
    sample_text = """
    
Essential hypertension with goal blood pressure less than 140/90	I10	
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

•	Chronic kidney disease stage 3 (moderate)	N18.3
    """

    files = ['medical_conditions.csv', 'acute_conditions.csv']
    results = detect_and_map_conditions(sample_text, files)

    if results:
        print("Detected mappings:")
        for term, canon in results.items():
            print(f"  {term} : {canon}")
    else:
        print("None")
