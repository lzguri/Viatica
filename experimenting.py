
import csv
import re

previous_searches = {}

def memoized_search(pattern, text):
    """Checks against a dict prior to searching to save some time"""
    # Check if the search has been performed before
    if pattern in previous_searches.keys():
        # Return the cached result
        return previous_searches[pattern]

    # Perform the actual search using memoized_search
    match = re.search(pattern, text)


    # Update the cache with the result
    previous_searches[pattern] = bool(match)

    # Return the match object
    return bool(match)


file_text = """

chronic congestive heart fafailure
hyperlipidemia
"""

def medical_conditions1(input_text, chronic=True, acute=True, pmh_only=False):
    conditions_list = []

    chronic_file = "medical_conditions.csv"
    acute_file = "acute_conditions.csv"

    if chronic:
        with open(chronic_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                disease_names = row['1name_of_disease'].split(',')
                pmh_include = row['PMH_include']

                for disease_name in disease_names:
                    disease_name = disease_name.strip()
                    pattern = r"\b{}\b".format(re.escape(disease_name))

                    if re.search(pattern, input_text, flags=re.IGNORECASE):
                        if pmh_only and pmh_include.lower() != 'x':
                            continue

                        abbreviation = row.get('abbreviations', '')
                        conditions_list.append(abbreviation if pmh_only and abbreviation else disease_name)

    if acute:
        with open(acute_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                disease_names = row['1name_of_disease'].split(',')

                for disease_name in disease_names:
                    disease_name = disease_name.strip()
                    pattern = r"\b{}\b".format(re.escape(disease_name))

                    if re.search(pattern, input_text, flags=re.IGNORECASE):
                        conditions_list.append(disease_name)

    # Remove duplicates and empty strings
    conditions_list = list(filter(None, set(conditions_list)))

    return conditions_list


def format_list(list):

    length_list = len(list)

    if length_list > 1:
        return f"{', '.join(list[:-1])}, and {list[-1]}"
    elif length_list == 1:
        return list[0]
    else:
        return '***'


input_text = """

chronic congestive heart failure
dyslipidemia
hypothyroidism
hypercalcemia
chloasma
Cerebral arteriovenous malformation
acute heart failure
benign prostatic hyperplasia
"""


print(format_list(medical_conditions1(input_text, acute=False, pmh_only=True)))