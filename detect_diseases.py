import pandas as pd
import spacy
from fuzzywuzzy import process

# Load the spaCy model just once
nlp = spacy.load("en_core_web_sm")

def load_medical_conditions(filepath):
    """
    Loads medical conditions from a CSV file.
    Assumes the disease names are in a column named 'name_of_disease'.
    """
    try:
        df = pd.read_csv(filepath)
        col = 'name_of_disease'
        if col not in df.columns:
            raise ValueError(f"CSV must contain a '{col}' column. Found: {df.columns.tolist()}")
        # drop NaNs and return unique list
        return df[col].dropna().unique().tolist()
    except FileNotFoundError:
        print(f"Error: '{filepath}' not found.")
        return []
    except Exception as e:
        print(f"Error loading medical conditions: {e}")
        return []

def detect_and_match_medical_conditions(paragraph, disease_list, threshold=80):
    """
    Detects potential medical terms in `paragraph`, then fuzzy-matches
    them back to `disease_list` (only keeping matches ≥ threshold).
    """
    doc = nlp(paragraph)

    # build a lowercase set for exact token matches
    disease_set = {d.lower() for d in disease_list}

    # 1) Gather candidate phrases (this is very basic)
    candidates = set()
    for ent in doc.ents:
        candidates.add(ent.text)
    for token in doc:
        # exact single-token disease
        if token.text.lower() in disease_set:
            candidates.add(token.text)
        # otherwise consider NOUN/PROPN/ADJ as potential
        elif token.pos_ in {"NOUN","PROPN","ADJ"} and len(token.text)>2:
            candidates.add(token.text)

    # 2) Fuzzy-match each candidate back to the master list
    results = []
    for cand in candidates:
        best = process.extractOne(cand, disease_list, score_cutoff=threshold)
        if best:
            match, score = best
            results.append((cand, match, score))

    # 3) Also catch full-phrase exact matches
    lower_para = paragraph.lower()
    for disease in disease_list:
        if disease.lower() in lower_para:
            tpl = (disease, disease, 100)
            if tpl not in results:
                results.append(tpl)

    return results

if __name__ == "__main__":
    diseases = load_medical_conditions("medical_conditions.csv")
    if not diseases:
        exit(1)

    test = "Patient has COPD and a lung infection plus diabetes mellitus."
    matches = detect_and_match_medical_conditions(test, diseases, threshold=85)
    for detected, matched, score in matches:
        print(f"Detected: '{detected}'  →  Matched: '{matched}' ({score}%)")
