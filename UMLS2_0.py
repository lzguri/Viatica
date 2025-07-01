import spacy
from spacy.matcher import PhraseMatcher
import csv

def load_conditions_from_csv(csv_path):
    """
    Reads a CSV file (one condition per line or one column) 
    and returns a list of condition strings.
    """
    conditions = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0].strip():
                conditions.append(row[0].strip())
    return conditions

def build_matcher(nlp, condition_list):
    """
    Given a spaCy Language object and a list of condition strings,
    build and return a PhraseMatcher configured to find them case-insensitively.
    """
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(cond) for cond in condition_list]
    matcher.add("MED_COND", patterns)
    return matcher

def detect_conditions(text, nlp, matcher):
    """
    Runs the matcher over text and returns a sorted, deduplicated list of spans.
    """
    doc = nlp(text)
    matches = matcher(doc)
    found = {doc[start:end].text for _, start, end in matches}
    return sorted(found)

if __name__ == "__main__":
    # 1) Load spaCy model (install with `pip install spacy` & `python -m spacy download en_core_web_sm`)
    nlp = spacy.load("en_core_web_sm")

    # 2) Load your conditions list:
    #    Option A: from CSV
    #conditions = load_conditions_from_csv("conditions.csv")
    #    Option B: directly as a Python list
    conditions = [
        "pneumonia",
        "hypertension",
        "type 2 diabetes mellitus",
        "coronary artery disease",
        "urinary tract infection",
        # …etc…
    ]

    # 3) Build the matcher
    matcher = build_matcher(nlp, conditions)

    # 4) Get input paragraph and detect
    paragraph = """
    The patient presents with fever and cough suggestive of pneumonia. 
    He also has a history of hypertension and type 2 diabetes mellitus, 
    but no signs of urinary tract infection.
    """
    found_conditions = detect_conditions(paragraph, nlp, matcher)

    print("Detected medical conditions:")
    for cond in found_conditions:
        print(" -", cond)
