import re
import pandas as pd
import datetime
"""import openai"""
import json
from copy import deepcopy
#import UMLS
#import spacy
"""import medspacy"""
import csv
from math import isnan
import disease
from os import linesep


todays_date = datetime.datetime.now()

all_homemeds = []


"""
def extract_conditions(input_text):
    # returns list of detected conditions
    # TODO can import umls vocab, check for negation (AKA "no hx of PE/DVT" wont get picked up), code for diseases not correctly detected
    conditions = []
    sci_nlp = spacy.load("en_ner_bc5cdr_md")
    docxnlp = sci_nlp(input_text)
    for ent in docxnlp.ents:
        if conditions.label_ == "DISEASE":
            conditions.append(ent.text)
    return conditions"""



# load lab data, only columns with 'done' on them


class MasterClass:
    def __init__(self, file_contents):
        self.previous_searches = {}

        

        # This line will change Not Detected to negative from the input text = file_contents
        file_contents = re.sub(r'Not Detected', 'negative', file_contents)
        file_contents = re.sub(r'Presumptive Positive', 'positive', file_contents)

        self.image_text = file_contents
        self.text = file_contents

        # This will convert lines of the text into items of a list
        self.file_contents = file_contents.splitlines()

        # Import laboratory csv file and create a dataframe
        self.labs_data = pd.read_csv(
    "lab_values.csv", keep_default_na=False, na_values=['_', "", " "])

        # Define the regex pattern for the lab format
        pattern = r"^(\s*[0-9A-Z]+)\s+([0-9\.,->=+]*|[A-Za-z]*|[A-Za-z]+.+|[A-Za-z]*)\s*(\(LL\)|\(L\)|\(H\)|\(HH\)|\(A\))?\s+([0-9/]* [0-9:]* [APM]*)$"

        # Create an empty dataframe
        self.df = pd.DataFrame(columns=["Test", "Result", "Indicator", "Date"])


        # Iterate over the lines and extract the the lab name = test, result, indicator .ie (H), date using the regex pattern from above
        for line in self.file_contents:
            match = re.search(pattern, line)
            if match is None:
                continue
            test = match.group(1).strip()
            result = match.group(2).rstrip()
            indicator = match.group(3)
            date = match.group(4)
            date = date.split(' ')[0]

            # Append the extracted data to the dataframe
            temp_df = pd.DataFrame(
                {"Test": [test], "Result": [result], "Indicator": [indicator], "Date": [date]})
            self.df = pd.concat([self.df, temp_df])


        self.file_contents = file_contents.lower()

        # Merge the dataframe created with lab values csv (self.labs_data) with the df created from extracted from the labs from the text self.file_contents
        self.mergeddf = pd.merge(self.df, self.labs_data, on="Test")
        self.mergeddf.drop_duplicates(inplace=True, subset=['Test', 'Result', 'Date'], keep='first')

        self.diseases = self.medical_conditions(chronic=True, pmh_only=False, acute=False)

        all_homemeds = self.find_all_medications(only_meds_list=True)
        all_homemeds = list(map(lambda x: x.lower(), all_homemeds))
        self.all_homemeds = all_homemeds  # Argument for all the home meds

        self.meds_control = {
            "cont": deepcopy(all_homemeds),
            "warning": [],
            "stop": []
        }

        for med in all_homemeds:
            plan = self.medication_plan(med)
            if not plan:
                # no warnings/contraindications
                continue
            if plan[0] == "stop":
                self.meds_control["stop"].append(
                    (med, list(map(str.lower, plan[1]))))
                self.meds_control["cont"].remove(med)
            elif plan[0] == "warning":
                self.meds_control["warning"].append(
                    (med, list(map(str.lower, plan[1]))))
                self.meds_control["cont"].remove(med)    

    def extract_labs(self):
        """
        This function should exctract labs from the text you have entered
        
        """
        # This line will change Not Detected to negative from the input text = file_contents

        # This will convert lines of the text into items of a list
        self.epic_input = self.file_contents.splitlines()


        # Import laboratory csv file and create a dataframe
        self.labs_data = pd.read_csv("lab_values.csv", keep_default_na=False, na_values=['_', "", " "])

        # Define the regex pattern for the lab format
        pattern = r"^(\s*[0-9A-Z]+)\s+([0-9\.,->=]*|[A-Za-z]*|[A-Za-z]+.+|[A-Za-z]*)\s*(\(LL\)|\(L\)|\(H\)|\(HH\)|\(A\))?\s+([0-9/]* [0-9:]* [APM]*)$"

        # Create an empty dataframe
        self.df = pd.DataFrame(columns=["Test", "Result", "Indicator", "Date"])


        # Iterate over the lines and extract the the lab name = test, result, indicator .ie (H), date using the regex pattern from above
        for line in self.epic_input:
            match = re.search(pattern, line)
            if match is None:
                continue
            test = match.group(1).strip()
            result = match.group(2).rstrip()
            indicator = match.group(3)
            date = match.group(4)
            date = date.split(' ')[0]

            # Append the extracted data to the dataframe
            temp_df1 = pd.DataFrame(
                {"Test": [test], "Result": [result], "Indicator": [indicator], "Date": [date]})
            self.df1 = pd.concat([self.df, temp_df1])


        # Merge the dataframe created with lab values csv (self.labs_data) with the df created from extracted from the labs from the text self.file_contents
        self.mergeddf = pd.merge(self.df, self.labs_data, on="Test")
        self.mergeddf.drop_duplicates(inplace=True, subset=['Test', 'Result', 'Date'], keep='first')

        return self.mergeddf




    def get_acute_diseases(self):
        from speciality_modules import endocrinology, gastroenterology, cardiology, infectious, neurology, pulmonary, nephrology, hematology


        expanded_conditions = {
            # Endocrinology goes here 
            'Diabetic ketoacidosis': endocrinology.DiabeticKetoacidosis,
            'Diabetes mellitus' : endocrinology.DM,

            # Gastroenterology goes here
            'Upper GI Bleeding': gastroenterology.UpperGIBleeding,
            'Lower GI Bleeding' : gastroenterology.LowerGIBleeding,
            'Acute Pancreatitis': gastroenterology.AcutePancreatitis,
            "Liver cirrhosis" : gastroenterology.LiverCirrhosis,
            'Clostridium difficile' : gastroenterology.CDiff,
            "Inflammatory Bowel disease" : gastroenterology.IBD_flare,
            "Gastroparesis": gastroenterology.Gastroparesis,
            "Acute diarrhea": gastroenterology.AcuteDiarrhea,

            # Cardiology goes here
            #'Coronary artery disease': cardiology.CAD,
            "Acute heart failure": cardiology.AcuteHeartFailure,
            "Bradycardia": cardiology.Bradycardia,
            "NSTEMI" : cardiology.AcuteCoronarySyndrome,
            "Acute pericarditis" : cardiology.AcutePericarditis,
            "Atrial fibrillation with RVR": cardiology.Afib,

            # Infectious goes here
            'Sepsis': infectious.Sepsis,
            'Cellulitis': infectious.SkinInfections,
            'Diabetic ulcer': infectious.DiabeticUlcer,
            "Acute cholecystitis" : infectious.AcuteCholecystitis,

            # Nephrology goes here
            'Hyponatremia': nephrology.Hyponatremia,
            'Hypokalemia': nephrology.Hypokalemia,
            'Hyperkalemia': nephrology.Hyperkalemia,
            'Hypocalcemia' : nephrology.Hypocalcemia,
            'Hypercalcemia': nephrology.Hypercalcemia,
            "Hypomagnesemia": nephrology.Hypomagnesemia,
            'Acute kidney injury': nephrology.AcuteKidneyInjury,

            # Neurology goes here
            'Altered mental status': neurology.Encephalopathy,
            'Acute cerebrovascular accident': neurology.CVA,

            # Pulmonary goes here
            'COPD exacerbation': pulmonary.COPDexac,
            'Asthma exacerbation': pulmonary.Asthmaexac,
            'ILD exacerbation': pulmonary.ILDexac,
            'Pleural effusion': pulmonary.Pleuraleffusion,
            'Acute pulmonary embolism': pulmonary.AcutePulmonaryEmbolism,
            'COVID-19' : pulmonary.COVID19,

            # Hematology goes here
            'Thrombocytopenia' : hematology.Thrombocytopenia,
            "Anemia": hematology.Anemia

        }
        diseases = []
        diseases_object = []
        acute_db = pd.read_csv("acute_conditions.csv", keep_default_na=False, na_values=['_', "", " "])
        #extract the 1name_of_disease column into a list
        acute_diseases = acute_db['1name_of_disease'].tolist() 
        diseases = self._find_names_in_string(acute_diseases, self.file_contents) + self.sodium_disorder() + self.calcium_disorder() + self.magnesium_disorder() + self.potassium_disorder() + self.blood_disorder()

        for name in diseases:
            for key in expanded_conditions.keys():
                if name == key.lower():
                        diseases_object.append(expanded_conditions[key](key, file_contents = self.old_file_contents))
                        break
            else:
                diseases_object.append(disease.Disease(name, file_contents = self.old_file_contents))
        return diseases, diseases_object
    

    def join_list_to_string(self, insert_list):
        if not insert_list:
            return None
        elif len(insert_list) == 1:
            return f"{insert_list[0]}"
        else:
            return f"{', '.join(insert_list[:len(insert_list)-1])}, and {insert_list[-1]}"

    conditions = pd.read_csv("medical_conditions.csv",
                             keep_default_na=False, na_values=['_', "", " "])
    # NOTE: probably will take this bit out later, for now ignore acute stuff tho
    # conditions = conditions.loc[conditions['acuity_of_condition'] != 'acute']

    def plan_chronic(self, name):
        # Given the detected name of a condition, give boilerplate plan based on conditions csv


        def split_or_none(value):
            # helper function
            try:
                value = value.iloc[0]
            except:
                return False
            if pd.isna(value):
                return False
            else:
                return list(map(str.strip, value.split(",")))

        return_text = ""

        def printf(text, planline=False):
            nonlocal return_text
            if not text:
                return ()
            if planline:
                return_text += "- " + text + "\n"
                return ()
            return_text += text + "\n"
            return ()
        # access disease row
        dz = self.conditions.loc[self.conditions['1name_of_disease'].str.lower(
        ) == name.lower()]

        if dz.empty:
            dz = self.conditions.loc[self.conditions['1name_of_disease'].str.contains(
                name, case=False, na = False)]
        
        #if its empty except for the name and acuity
        sample_row = dz.drop(labels = ['1name_of_disease', 'acuity_of_condition'], axis = 1)

        if sample_row.dropna(how = 'all').empty:
            return ""

        # NOTE: idk if our names in here and the meds csv are mapped...
        home_meds = self.find_medications_by_indication(
            name.lower(), only_meds_list=True)

        currents = split_or_none(dz['current_labs'])
        comp_currents = split_or_none(dz['comparison_current_labs'])
        followups = split_or_none(dz['followup_labs'])
        comp_followups = split_or_none(dz['comparison_followup_labs'])
        associated_conditions = split_or_none(dz['associated_conditions'])

        if associated_conditions:
            caught_associated_conditions = []
            for condition in associated_conditions:
                if self.check_name([condition]):
                    caught_associated_conditions.append(condition)

        printf(name[0].title() + name[1:])

        other_assessment = split_or_none(dz['other_assessment'])
        if other_assessment:
            printf("\n".join(other_assessment))

        if currents:
            labs_string = dz['current_labs'].iloc[0]
            if "(" in labs_string:
                sets = re.findall(r'\((.*?)\)', labs_string)
                for s in range(len(sets)):
                    l = list(map(str.strip, sets[s].split(",")))
                    printf(self.check_labs(l, display_text=True,
                                           dict_mode=False, comparisons=comp_currents, days_too_old=2))
                # remove these tuples from lab string and reset currents
                labs_string = re.sub(r'\(.*?\)', '', labs_string)
                currents = split_or_none(labs_string)

            printf(self.check_labs(currents, display_text=True,
                   dict_mode=False, comparisons=comp_currents, days_too_old=2))
        if followups:
            # add comparison mode to this fn
            printf(self.check_labs(followups, display_text=True,
                   dict_mode=False, comparisons=comp_followups, group_by_date=True))

        if associated_conditions and caught_associated_conditions:
            printf("Associated conditions: " +
                   self.output_list(caught_associated_conditions))

        if home_meds:
            printf("On " + self.output_list(home_meds) + " at home")
        printf(self.meds_list_assessment(
            self.all_homemeds, name))

        printf("Plan")
        printf(self.meds_list_plan(home_meds))
        missing_labs = split_or_none(dz['check_missing_labs'])

        if missing_labs:
            available = self.check_labs(missing_labs, dict_mode=True)
            for lab in missing_labs:
                if available[lab] and "Not found" not in [l[0] for l in available[lab]] and "Too old" not in [l[0] for l in available[lab]]:
                    missing_labs.remove(lab)
                    # Convert to display names
            for i in range(len(missing_labs)):
                try:
                    # Have to use the labs_data dataframe for missing labs
                    display_name = self.labs_data.loc[self.labs_data['Test'] == missing_labs[i], 'test_synonym'].to_numpy()[
                        0]
                    missing_labs[i] = display_name
                except:
                    pass
            if missing_labs:
                printf("Check " + self.output_list(missing_labs), True)

        other_plan = split_or_none(dz['other_plan'])
        if other_plan:
            printf("\n- ".join(other_plan), True)

        # If nothing was detected don't return anything
        if return_text == name + "\nPlan\n":
            return ""
        
        #If there is no plan, remove the plan line
        if return_text.endswith("Plan\n"):
            return_text = return_text[:-5]
        
        return_text = linesep.join([s for s in return_text.splitlines() if s]) #remove empty lines from string

        return return_text

    def plan_chronic_abridged(self, name):
        # Given the detected name of a condition, give boilerplate plan based on conditions csv


        def split_or_none(value):
            # helper function
            try:
                value = value.iloc[0]
            except:
                return False
            if pd.isna(value):
                return False
            else:
                return list(map(str.strip, value.split(",")))


        return_text = ""


        # access disease row
        dz = self.conditions.loc[self.conditions['1name_of_disease'].str.lower(
        ) == name.lower()]

        if dz.empty:
            dz = self.conditions.loc[self.conditions['1name_of_disease'].str.contains(
                name, case=False, na = False)]
            
        #check acuity_of_condition, if 'acute' or 'either or' then return plan_chronic instead of plan_chronic_abridged
        try:
            if dz['acuity_of_condition'].iloc[0] == 'acute' or dz['acuity_of_condition'].iloc[0] == 'either or':
                return self.plan_chronic(name)
        except:
            return ""
    

        # NOTE: idk if our names in here and the meds csv are mapped...
        home_meds = self.find_medications_by_indication(
            name.lower(), only_meds_list=True)

        currents = split_or_none(dz['current_labs'])
        comp_currents = split_or_none(dz['comparison_current_labs'])
        followups = split_or_none(dz['followup_labs'])
        comp_followups = split_or_none(dz['comparison_followup_labs'])
        other_assessment = split_or_none(dz['other_assessment'])


        return_text += name[0].title() + name[1:] 

        if other_assessment:
            return_text += " – " + ", ".join(other_assessment) + ". "

        if home_meds:
            return_text += " (On " + self.output_list(home_meds) + ")"
        #printf(self.meds_list_assessment(
        #    self.all_homemeds, name))


        if currents:
            labs_string = dz['current_labs'].iloc[0]
            if "(" in labs_string:
                sets = re.findall(r'\((.*?)\)', labs_string)
                for s in range(len(sets)):
                    l = list(map(str.strip, sets[s].split(",")))
                    return_text += "[" + self.check_labs(l, display_text=True,
                                           dict_mode=False, comparisons=comp_currents, days_too_old=2) + "]"
                # remove these tuples from lab string and reset currents
                labs_string = re.sub(r'\(.*?\)', '', labs_string)
                currents = split_or_none(labs_string)
            try:
                return_text += " (" + self.check_labs(currents, display_text=True,
                   dict_mode=False, comparisons=comp_currents, days_too_old=2) + ")"
            except:
                pass

        if followups:
            # add comparison mode to this fn
            try:
                return_text += ", (" + self.check_labs(followups, display_text=True,
                    dict_mode=False, comparisons=comp_followups, group_by_date=True) + ")"
            except:
                pass


        return_text += "."
        if home_meds:
            return_text += '\n' + self.meds_list_plan(home_meds) + ". "
        missing_labs = split_or_none(dz['check_missing_labs'])



        if missing_labs:
            available = self.check_labs(missing_labs, dict_mode=True)
            for lab in missing_labs:
                if available[lab] and "Not found" not in [l[0] for l in available[lab]] and "Too old" not in [l[0] for l in available[lab]]:
                    missing_labs.remove(lab)
                    # Convert to display names
            for i in range(len(missing_labs)):
                try:
                    # Have to use the labs_data dataframe for missing labs
                    display_name = self.labs_data.loc[self.labs_data['Test'] == missing_labs[i], 'test_synonym'].to_numpy()[
                        0]
                    missing_labs[i] = display_name
                except:
                    display_name = missing_labs[i].lower()
                missing_labs[i] = display_name
            if missing_labs:
                return_text += "Check " + self.output_list(missing_labs) + ". "

        # Other plan
        other_plan = split_or_none(dz['other_plan'])
        if other_plan:
            if len(other_plan) > 1:
                return_text += "\n- " + "\n- ".join(other_plan) + ". "
            else:
                return_text += "\n- " + other_plan[0] + ". "

        # Remove empty brackets
        return_text = return_text.replace("[]", "")
        #remove newlines
        #return_text = return_text.replace("\n", " ")
        #remove double spaces
        return_text = return_text.replace("  ", " ")
        #remove double periods
        return_text = return_text.replace("..", ".")
        #remove - 
        #return_text = return_text.replace("- ", " ")
        # If nothing was detected don't return anything
        if return_text == name[0].title() + name[1:] + ".":
            return ""
        
        return_text = linesep.join([s for s in return_text.splitlines() if s]) #remove empty lines from string

        return return_text

    def plan_chronic_minimal(self, name):
        # Given the detected name of a condition, give boilerplate plan based on conditions csv

        def split_or_none(value):
            # helper function
            try:
                value = value.iloc[0]
            except:
                return False
            if pd.isna(value):
                return False
            else:
                return list(map(str.strip, value.split(",")))

        return_text = ""


        # access disease row
        dz = self.conditions.loc[self.conditions['1name_of_disease'].str.lower(
        ) == name.lower()]

        if dz.empty:
            dz = self.conditions.loc[self.conditions['1name_of_disease'].str.contains(
                name, case=False, na = False)]
            
        #check acuity_of_condition, if 'acute' or 'either or' then return plan_chronic instead of plan_chronic_abridged
        try:
            if dz['acuity_of_condition'].iloc[0] == 'acute' or dz['acuity_of_condition'].iloc[0] == 'either or':
                return self.plan_chronic(name)
        except:
            return ""
    

        # NOTE: idk if our names in here and the meds csv are mapped...
        home_meds = self.find_medications_by_indication(
            name.lower(), only_meds_list=True)

        currents = split_or_none(dz['current_labs'])
        comp_currents = split_or_none(dz['comparison_current_labs'])
        followups = split_or_none(dz['followup_labs'])
        comp_followups = split_or_none(dz['comparison_followup_labs'])
        other_assessment = split_or_none(dz['other_assessment'])


        return_text += name[0].title() + name[1:] 

        if other_assessment:
            return_text += " – " + ", ".join(other_assessment) + ". "

        #if home_meds:
        #    return_text += " (On " + self.output_list(home_meds) + ")"
        #printf(self.meds_list_assessment(
        #    self.all_homemeds, name))


        if currents:
            labs_string = dz['current_labs'].iloc[0]
            if "(" in labs_string:
                sets = re.findall(r'\((.*?)\)', labs_string)
                for s in range(len(sets)):
                    l = list(map(str.strip, sets[s].split(",")))
                    return_text += "[" + self.check_labs(l, display_text=True,
                                           dict_mode=False, comparisons=comp_currents, days_too_old=2) + "]"
                # remove these tuples from lab string and reset currents
                labs_string = re.sub(r'\(.*?\)', '', labs_string)
                currents = split_or_none(labs_string)
            try:
                lbs = self.check_labs(currents, display_text=True,
                   dict_mode=False, comparisons=comp_currents, days_too_old=2)
                if lbs:
                    return_text += " (" + lbs + ")"
            except:
                pass

        if followups:
            # add comparison mode to this fn
            try:
                return_text += ", (" + self.check_labs(followups, display_text=True,
                    dict_mode=False, comparisons=comp_followups, group_by_date=True) + ")"
            except:
                pass


        #return_text += "."
        if home_meds:
            return_text += '\n' + self.meds_list_plan(home_meds) + ". "
        missing_labs = split_or_none(dz['check_missing_labs'])



        if missing_labs:
            available = self.check_labs(missing_labs, dict_mode=True)
            for lab in missing_labs:
                if available[lab] and "Not found" not in [l[0] for l in available[lab]] and "Too old" not in [l[0] for l in available[lab]]:
                    missing_labs.remove(lab)
                    # Convert to display names
            for i in range(len(missing_labs)):
                try:
                    # Have to use the labs_data dataframe for missing labs
                    display_name = self.labs_data.loc[self.labs_data['Test'] == missing_labs[i], 'test_synonym'].to_numpy()[
                        0]
                    missing_labs[i] = display_name
                except:
                    display_name = missing_labs[i].lower()
                missing_labs[i] = display_name
            if missing_labs:
                return_text += "\n– Check " + self.output_list(missing_labs) + ". "

        # Other plan
        other_plan = split_or_none(dz['other_plan'])
        if other_plan:
            if len(other_plan) > 1:
                return_text += "\n– " + "\n– ".join(other_plan) + ". "
            else:
                return_text += "\n– " + other_plan[0] + ". "

        # Remove empty brackets
        return_text = return_text.replace("[]", "")
        #remove newlines
        #return_text = return_text.replace("\n", " ")
        #remove double spaces
        return_text = return_text.replace("  ", " ")
        #remove double periods
        return_text = return_text.replace("..", ".")
        #remove - 
        #return_text = return_text.replace("- ", " ")
        # If nothing was detected don't return anything
        if return_text == name.title():
            return ""
        #if its only the name and cont one medications keep it on the same line
        if return_text.count("\n") == 1 and "– Cont" in return_text:
            return_text = return_text.replace("\n", " ")

        return_text = linesep.join([s for s in return_text.splitlines() if s]) #remove empty lines from string
            
        return return_text
    

    def check_labs(self, labs, dict_mode=False, display_text=False, comparisons=False, group_by_date=False, most_recent = False, days_too_old=99999, compared_with=False):
        global todays_date
        assert type(comparisons) == bool or type(
            comparisons) == list or type(comparisons) == tuple
        if comparisons:
            assert display_text == True
        if display_text:
            assert dict_mode == False
        if group_by_date:
            assert display_text == True

        if labs == None or labs == False:
            return ()
        if type(labs) == str:
            labs = [labs]

        values = {l: [] for l in labs} if (dict_mode or group_by_date) else []

        for lab in labs:
            if dict_mode or group_by_date:
                try:
                    values[lab] = self.mergeddf.loc[self.mergeddf['Test'] == lab, [
                        "Result", "Date"]].values.tolist()
                    #sort by date
                    values[lab].sort(key=lambda x: datetime.datetime.strptime(x[1], '%m/%d/%Y'))
                    values[lab] = [x for x in values[lab] if (
                        todays_date - datetime.datetime.strptime(x[1], '%m/%d/%Y')).days <= days_too_old]
                except:
                    values[lab] = "Not found"
            else:
                try:
                    dates = self.mergeddf.loc[self.mergeddf['Test'] == lab, "Date"].apply(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y')).sort_values().values
                    dates = list(map(lambda dt64: pd.to_datetime(dt64).to_pydatetime(), dates))
                    if (todays_date - dates[-1]).days <= days_too_old:
                        # get the string format of the date to use it for indexing
                        date_str = dates[-1].strftime('%m/%d/%Y') 
                        values.append(self.mergeddf.loc[(self.mergeddf['Test'] == lab) & (self.mergeddf['Date'] == date_str), "Result"].values[0])
                    else:
                        values.append("Not found")
                except:
                    values.append("Not found")

        for i in range(len(values)):
            try:
                values[i] = float(values[i])
            except:
                continue

        if display_text:
            if group_by_date:
                #TODO: when is this being called?, date handling may be old here
                dates = sorted(set([date for lab in values.keys()
                               for _, date in values[lab]]), reverse=True)
                if most_recent == True and len(dates) > 1:
                    dates = [dates[-1]]
                grouped_text = []
                for date in dates:
                    return_text = ""
                    for i, lab in enumerate(labs):
                        if values[lab] == "Not Found":
                            continue
                        date_values = [
                            val for val, val_date in values[lab] if val_date == date]
                        if len(date_values) > 0:
                            val = date_values[-1]
                            synonym = self.mergeddf.loc[self.mergeddf['Test'] == lab, 'test_synonym'].to_numpy()[
                                0]
                            unit = self.mergeddf.loc[self.mergeddf['Test'] == lab, 'test_unit'].to_numpy()[
                                0]
                            return_text += f"{synonym} of {val} {unit} "
                    return_text = return_text.rstrip(', ')
                    return_text += f" on {date}."
                    grouped_text.append(return_text)
                return "\n".join(grouped_text)

            else:
                return_text = ""
                for i, val in enumerate(values):
                    if val == "Not found":
                        continue

                    try:
                        synonym = self.mergeddf.loc[self.mergeddf['Test'] == labs[i], 'test_synonym'].to_numpy()[
                            0]
                        unit = self.mergeddf.loc[self.mergeddf['Test'] == labs[i], 'test_unit'].to_numpy()[
                            0]
                        all_labs = self.mergeddf.loc[self.mergeddf['Test'] == labs[i], [
                            "Result", "Date"]].values.tolist()
                        
                        #if the unit is nan make it an empty string
                        if pd.isna(unit):
                            unit = ""
                            
                        all_labs.sort(key=lambda x: datetime.datetime.strptime(x[1], '%m/%d/%Y'))

                        comparison_text = ""
                        if comparisons:
                            if len(all_labs) > 1 and (comparisons == True or labs[i] in comparisons):
                                last_lab = all_labs[-2]
                                if compared_with:
                                    comparison_text = f"was {last_lab[0]} {unit} on {last_lab[1]}"
                                else:
                                    comparison_text = f", was {last_lab[0]} {unit} on {last_lab[1]}"

                        # edge case when last value is "not found"
                        values_without_notfound = [
                            x for x in values if x != "Not found"]
                        if i != len(values_without_notfound) - 1:
                            if compared_with:
                                return_text += f"{synonym} of {val}, {comparison_text}, "
                            else:
                                return_text += f"{synonym} of {val} {unit}{comparison_text}, "
                        else:
                            # Remove the last comma and space
                            if len(values_without_notfound) == 1:
                                if compared_with:
                                    return_text += f"{synonym} is {val} {comparison_text}"
                                else:
                                    return_text += f"{synonym} is {val} {comparison_text}."
                            else:
                                return_text = return_text.rstrip(', ')
                                return_text += f" and {synonym} of {val} {unit}{comparison_text}."
                    except:
                        return_text += f"{labs[i]} of {val}.{comparison_text} "

                # Remove the last comma and space and replace with a period
                if return_text.endswith(', '):
                    return_text = return_text.rstrip(', ')
                    return_text += '.'
                return return_text

        return (values)
    

    def format_list(self, list):
        """
        Formats a list of items into a grammatically correct string.

        Args:
            list: A list of strings or other objects.

        Returns:
            A string containing the list items formatted with commas and conjunctions.

        Raises:
            TypeError: If any item in the list is not a string.
        """

        # Get the length of the list
        length_list = len(list)

        # Handle different list lengths with appropriate formatting
        if length_list > 1:
            # Join all items except the last one with commas and spaces
            joined_items = ", ".join(list[:-1])
            # Add the last item with a preceding comma and the word "and"
            formatted_list = f"{joined_items}, and {list[-1]}"
        elif length_list == 1:
            # If there's only one item, return it as is
            formatted_list = list[0]
        else:
            # If the list is empty, return a special string (e.g., "***")
            formatted_list = '***'

        # Implicit return: the function returns the value assigned to `formatted_list`

        # Although not explicitly mentioned in the provided code, it's good practice to
        # consider type checking to ensure the function works as intended.
        # You could add a type check here to ensure all list items are strings.
        # for item in list:
        #   if not isinstance(item, str):
        #     raise TypeError("Items in the list must be strings")

        return formatted_list



    def determine_lab_value_type(self, value_str):
        """
        titer - 0-2
        'positive' 'negative'
        'detected' 'not detected'
        '+1'
        May return: 'number', 'titer', 'p/n' (Positive/Negative), 'd/nd' (Detected or not detected), area (+1, etc), or "unknown'
        """
        # use regex to determine the tpye and figure out what to do from there

        if value_str.replace('.', '', 1).isdigit():
            return 'number'
        else:
            return 'unknown'

    def check_lab_abnormal(self, lab_name, value):
        """Return true if lab is abnormal range, else return False. Value must be a number"""
        # TODO: I'm conveniently ignoring urine/string based labs currently.
        if type(value) == str:
            # Non-integer lab, urine, pathogen panels, etc.
            # get the lower limit in the workup
            low = eval(lab_name)["lower limit"]
            # labs_data.loc[labs_data['epic_name'] == lab_name]
            if low and value != low:
                return True
            return False  # NOTE:in the future we oculd raise an exception here
        try:
            upper_range = float(eval(lab_name)['upper limit'])
            lower_range = float(eval(lab_name)['lower limit'])
        except:
            # If they're not numbers, don't try
            return False
        if value > upper_range or value < lower_range:
            return True
        else:
            return False
        
    def display_name(self, epicname):
        """returns the display name of a lab"""
        try:
            return self.labs_data.loc[self.labs_data['Test'] == epicname, 'test_synonym'].to_numpy()[0]
        except:
            return epicname

    def abnormality_name(self, lab_name, value = None, _lazy_mode=False):
        """Return high name if lab is abnormally high and low name if abnormally low, else return (). Value must be a number for now"""
        if not _lazy_mode:
            assert value is not None
        # TODO: I'm conveniently ignoring urine/string based labs currently.
        if _lazy_mode:
            indication = ''
            try:
                indication = self.mergeddf.loc[self.mergeddf['Test']
                                           == lab_name]["Indicator"].iloc[0]
            except:
                ""
            if indication is None:
                return []
            if indication.lower() == "(h)" or indication.lower() == "(hh)":
                name = self.mergeddf.loc[self.mergeddf['Test']
                                         == lab_name, 'high_abnormal'].iloc[0]
                if type(name) != str:
                    return []
                return name
            elif indication.lower() == "(l)" or indication.lower() == "(ll)":
                name = self.mergeddf.loc[self.mergeddf['Test']
                                         == lab_name, 'low_abnormal'].iloc[0]
                if type(name) != str:
                    return []
                return name
            return []
        try:
            value = float(value)
        except:
            return []
        col = self.mergeddf.loc[self.mergeddf['Test'] == lab_name]
        # sometimes the same lab comes multiple times, typically for sex differences in lab ranges
        if len(col) > 1:
            for _i, row in col.iterrows():
                if row['notes'] == 'male' and self.get_sex() == 'male':
                    col = row
                    break
                elif row['notes'] == 'female':
                    col = row
                    break
                else:
                    # other cases I haven't accounted for yet probably, default to first result
                    continue
        else:
            # convert the col into a series object, so in either case we're working on series
            col = col.squeeze()
        # if nothing is figured out, just use the first one
        if len(col) > 1 and type(col) != pd.Series:
            col = col.iloc[0]

        low, high = float(col['lower_range']), float(col['upper_range'])
        if value >= high:
            high_name = col['high_abnormal']
            if high_name:
                return high_name
            return []
        elif value <= low:
            low_name = col['low_abnormal']
            if low_name:
                return low_name
            return []
        else:
            # if a normal lab is given
            return []
        
    
    def memoized_search(self, pattern, text):
        """Checks against a dict prior to searching to save some time"""
        # Check if the search has been performed before
        if pattern in self.previous_searches.keys():
            # Return the cached result
            return self.previous_searches[pattern]

        # Perform the actual search using self.memoized_search
        match = re.search(pattern, text)


        # Update the cache with the result
        self.previous_searches[pattern] = bool(match)

        # Return the match object
        return bool(match)

    def is_lab_abnormal(self, lab_epic_name, value, _lazy_mode=False):
        """Uses new CSV to return True/False depending on the labs abnormality value"""

        # if lazy mode is true use the 'indicater' column instead of the value
        if _lazy_mode:
            indication = self.mergeddf.loc[self.mergeddf['Test']
                                           == lab_epic_name]["Indicator"].iloc[0]
            return True if indication != None else False

        # Figure out of the value is a number, word, titer, etc TODO
        col = self.labs_data.loc[self.labs_data['Test'] == lab_epic_name]
        # sometimes the same lab comes multiple times, typically for sex differences in lab ranges
        if len(col) > 1:
            for _i, row in col.iterrows():
                if row['notes'] == 'male' and self.get_sex() == 'male':
                    col = row
                    break
                elif row['notes'] == 'female':
                    col = row
                    break
                else:
                    # other cases I haven't accounted for yet probably, default to first result
                    continue
        else:
            # convert the col into a series object, so in either case we're working on series
            col = col.squeeze()
        # if nothing is figured out, just use the first one
        if len(col) > 1 and type(col) != pd.Series:
            col = col.iloc[0]

        value_type = self.determine_lab_value_type(value)

        if value_type == 'number':
            value = float(value)

            # account for some special cases
            if lab_epic_name == 'GFR':
                if value != ">60":
                    return True
                else:
                    return False
                b
            low, high = float(col['lower_range']), float(col['upper_range'])
            if value >= high or value <= low:  # NOTE: includisve or exclusive?
                return True
            else:
                return False
        else:
            return False
        
    def extract_abnormal_labs(self, days=2):
        """
        This function takes a DataFrame containing medical test results and generates a formatted medical report
        based on the tests conducted within the specified number of days.

        Parameters:
        - df: DataFrame containing medical test results with columns 'Date', 'Test', 'Result', 'test_unit', and 'test_synonym'.
        - days: Number of days to consider for generating the report. Default is 2 days.

        Returns:
        - report: Formatted abnormal results string.
        """

        # DataFrame with abnormal labs only 
        filtered_df = self.mergeddf[self.mergeddf["Indicator"].notna() & self.mergeddf["Indicator"].str.contains(r'\(H\)|\(L\)|\(LL\)|\(HH\)|\(A\)', regex=True)]

        # Filter the DataFrame for the past 'days' days
        recent_df = filtered_df[pd.to_datetime(filtered_df['Date']).dt.date >= (pd.Timestamp.now() - pd.DateOffset(days=days)).date()]

        # Create a dictionary to store the test information for each group
        test_info_groups = {}

        # Separate by list
        test_groups = {
            'Complete blood count': ['WBC', 'RBC', 'HGB', 'HCT', 'PLT', 'MCV', 'NEUTROPHIL', 'LYMPHOCYTE', 'EOSINOPHIL'],
            'Chemistry': ['NA', 'K', 'CO2', 'CA', 'BUN', 'CREAT', 'GFR', 'GLUCOSE', 'TOTALPROTEIN', 'ANIONGAP', 'MG', 'PO4'],
            'Liver panel': ['BILITOTAL', 'ALKPHOS', 'AST', 'ALT', 'ALBUMIN'],
            'Cardiac profile': ['BASETROP', '2HRTROP', '6HRTROP', 'PROBNPNTERMI'],
            'Urinalysis': ['SGUR', 'PHUA', "URINELEUKOC", 'NITRITEUA', "PROTEINUA", "GLUUA", 'KETONEURINE', 'BLOODUA', 'WBCU', 'RBCUA', 'BACTERIAUA'],
            'Blood gas': ['PHBLOODPOC', 'PCO2POC', 'PO2POC', 'PFRATIO', 'O2SATPOC'],
            'Coag study': ['INR', 'PT', 'APTT'],
            'Viral panel': ['INFLUENZAA', 'INFLUENZAB', 'COVID19', 'RVSAG'],
            'Drug screen is positive for': ['AMPHETAMINEQ', 'BARBITQLUR', 'BENZDIAQLUR', 'CANNABQLUR', "COCAINEQUAL", "METHADONEU", 'OPIATEQUA', 'OXYCODQLUR', 'PHENCYCLID'],
            'Other labs': ['ESR', 'CRP', 'LACTATE', 'DDIMERQUANT', 'ETHANOL', 'PROCALCITONIN']
        }

        # Iterate over each row in the filtered DataFrame
        for index, row in recent_df.iterrows():
            for group, tests in test_groups.items():
                if row["Test"] in tests:
                    if group == "Urinalysis":
                        if row["Test"] == "PHUA":
                            test_info_str = f"{row['test_synonym']} of {row['Result']} {row['test_unit']}".replace(" nan", "")
                        else:
                            # Concatenate the required information into a string
                            test_info_str = f"{row['Result']} {row['test_unit']} {row['test_synonym']}".replace(" nan", "")
                    elif group == "Drug screen is positive for":
                        test_info_str = f"{row['test_synonym']}".replace(" nan", "")
                    else:
                        test_info_str = f"{row['test_synonym']} of {row['Result']} {row['test_unit']}".replace(" nan", "")

                    # Append the string to the list for the current group
                    if group not in test_info_groups:
                        test_info_groups[group] = []
                    test_info_groups[group].append(test_info_str)

        # Generate the medical report string
        report = ""
        for category, items in test_info_groups.items():
            if category == 'Chemistry':
                if len(items) > 1:
                    report += f"{category} is remarkable for {', '.join(items[:-1])}, and {items[-1]}. "
                else:
                    report += f"{category} is remarkable for {items[0]}. "
            elif category == 'Drug screen is positive for':
                if len(items) > 1:
                    report += f"{category} is {', '.join(items[:-1])}, and {items[-1]}. "
                else:
                    report += f"{category} is {items[0]}. "
            else:
                if len(items) > 1:
                    report += f"{category} is remarkable for {', '.join(items[:-1])}, and {items[-1]}. "
                else:
                    report += f"{category} is remarkable for {items[0]}. "

        return report

    def show_abnormal_labs(self, dict_only=False, days_too_old=99999):
        test_groups = {
            'CBC': ['WBC', 'RBC', 'HGB', 'HCT', 'PLT', 'MCV', 'NEUTROPHIL', 'LYMPHOCYTE', 'EOSINOPHIL'],
            'Chemistry': ['NA', 'K', 'CO2', 'CA', 'BUN', 'CREAT', 'GFR', 'GLUCOSE', 'TOTALPROTEIN', 'ANIONGAP', 'MG'],
            'Liver panel': ['BILITOTAL', 'ALKPHOS', 'AST', 'ALT', 'ALBUMIN'],
            'Cardiac profile': ['BASETROP', '2HRTROP', '6HRTROP', 'PROBNPNTERMI'],
            'Urinalysis': ['PHUA', 'SGUR', 'WBCU', 'RBCUA', 'BACTERIAUA', 'NITRITEUA', 'KETONEURINE'],
            'Blood gas': ['PHBLOODPOC', 'PCO2POC', 'PO2POC', 'PFRATIO', 'O2SATPOC'],
            'Other labs': ['ESR', 'CRP', 'LACTATE', 'DDIMERQUANT', 'ETHANOL', 'PROCALCITONIN']
        }

        abnormal_labs = {test_group: [] for test_group in test_groups.keys()}
        tests_not_done = []
        for test_group, test_list in test_groups.items():
            results = self.check_labs(test_list, dict_mode=True)

            for individual_test in test_list:
                if len(results[individual_test]) == 0:
                    tests_not_done.append(test_group)
                    continue

                # Get the lab value and date
                lab_value, lab_date = results[individual_test][-1]

                # Convert lab_date string to a datetime object
                lab_date = datetime.datetime.strptime(lab_date, '%m/%d/%Y')

                # Calculate how many days ago the lab was performed
                days_ago = (datetime.datetime.now() - lab_date).days

                # If the lab is too old, continue to the next lab
                if days_ago > days_too_old:
                    if "Too old" not in abnormal_labs[test_group]:
                        abnormal_labs[test_group].append("Too old")
                    continue

                if self.is_lab_abnormal(individual_test, lab_value, True):
                    abnormal_labs[test_group].append(
                        (individual_test, lab_value))

        if dict_only:
            return abnormal_labs

        output_strings = []

        for test_group, abnormalities in abnormal_labs.items():
            if "Too old" in abnormalities:
                continue
            elif len(abnormalities) == 0:
                if test_group in tests_not_done:
                    continue
                else:
                    output_strings.append(f"{test_group} unremarkable.")
            else:
                abnormal_values = []
                for individual_test, value in abnormalities:
                    synonym = self.mergeddf.loc[self.mergeddf['Test'] == individual_test, 'test_synonym'].to_numpy()[
                        0]
                    unit = self.mergeddf.loc[self.mergeddf['Test'] == individual_test, 'test_unit'].to_numpy()[
                        0]
                    abnormal_values.append(f"{synonym} of {value} {unit}")

                abnormal_values_text = ", ".join(
                    abnormal_values[:-1]) + " and " + abnormal_values[-1] if len(abnormal_values) > 1 else abnormal_values[0]
                output_strings.append(
                    f"{test_group} remarkable for {abnormal_values_text}.")

        return " ".join(output_strings)

    def labs_with_old(self, lab_name):
        """"
        Print HGB today is *** [*** on ***]
        """
        results = self.check_labs(lab_name, dict_mode=True)[lab_name]
        return (eval(lab_name)['synonyms'][0] + " today is " + str(results[-1][0]) + " [" + str(results[-2][0]) + " on " + results[-2][1] + "]")
    

    def extract_age_gender(self):
        """
        Scans self.file_contents for an age/gender phrase
        (e.g. "86 y.o. male", "72 year-old female") and returns:
          "Patient is {age} year-old {gender}."
        or None if not found.
        """
        pattern = re.compile(
            r'(\d{1,3})\s*'                      # age: 1–3 digits
            r'(?:y(?:\.o\.?|ears?[- ]old))\s*'   # y.o., yo, year-old, years-old
            r'(male|female)',                    # gender
            re.IGNORECASE
        )

        match = pattern.search(self.file_contents)
        if not match:
            return None

        age = int(match.group(1))
        gender = match.group(2).lower()
        return f"Patient is {age} year-old {gender}"
    
    def extract_exam_impressions(self) -> str:
        """
        Finds each Exam:…IMPRESSION: block in self.file_contents,
        keeps only those with 'chest', and returns:

          <exam_name> is showing impression:
          <impression_text>

        where <exam_name> is all lowercase except the modalities
        CT, CTA, US, MRI, XR which are forced uppercase.
        Blocks are separated by a blank line.
        """
        pattern = re.compile(
            r'Exam:\s*(?P<exam>.*?)\s+Date/Time.*?'
            r'IMPRESSION:\s*(?P<imp>.*?)(?=(?:\n[A-Z ]+?:)|\Z)',
            re.DOTALL | re.IGNORECASE
        )

        allowed_mods = {'CT', 'CTA', 'US', 'MRI', 'XR'}
        parts = []

        for m in pattern.finditer(self.file_contents):
            raw = m.group('exam').strip()
            # normalize spaces and lowercase everything
            exam_lower = re.sub(r'\s+', ' ', raw).lower()
            # uppercase only the allowed modalities
            exam_fmt = re.sub(
                r'\b(cta|ct|us|mri|xr)\b',
                lambda mo: mo.group(1).upper(),
                exam_lower,
                flags=re.IGNORECASE
            )

            # filter to chest studies only
            if 'chest' not in exam_fmt:
                continue

            # ensure the first word (modality) is allowed
            modality = exam_fmt.split()[0]
            if modality not in allowed_mods:
                continue

            # clean up the impression text
            imp = m.group('imp').strip()
            imp_clean = re.sub(r'\s+', ' ', imp)

            parts.append(f"{exam_fmt} is showing {imp_clean}")

        return "\n\n".join(parts)

    def get_sex(self):
        return "male" if (self.memoized_search(fr"\bmale\b", self.file_contents)) else "female"

    def get_age(self):
        age_pattern = r'\b\d{1,3}\b'
        try:
            return int(re.search(age_pattern, self.file_contents)[0])
        except:
            return None

    
    def remove_empty_lines(self, text):
        """
        Remove empty or whitespace-only lines from a paragraph.

        Args:
            text: The input string, potentially containing blank lines.

        Returns:
            A string with all empty lines removed.
        """
        # Split into lines, filter out lines that are empty after stripping whitespace,
        # then re-join with the original newline separator.
        non_empty_lines = [line for line in text.splitlines() if line.strip()]
        return "\n".join(non_empty_lines)

    def output_list(self, lst):
        """Returns a comma dilemeted list including 'and' at the end"""
        lst = deepcopy(lst)
        if len(lst) == 0:
            return ("")
        elif len(lst) == 1:
            return lst[0]
        elif len(lst) == 2:
            return lst[0] + " and " + lst[1]
        else:
            lst[-1] = "and " + lst[-1]
            return ", ".join(lst)

    def get_single_vital(self, vital):
        # Use a dictionary to map vital names to regex patterns
        vital_patterns = {
            'BP': r'bp:\s*(?:\(!\)\s*)?([0-9/]+)',
            'Pulse': r'pulse:\s*(?:\(!\)\s*)?(\d+)',
            'Resp': r'resp:\s*(?:\(!\)\s*)?(\d+)',
            'Temp': r'temp:\s*([\d.]+) °f',
            'SpO2': r'spo2:\s*(?:\(!\)\s*)?(\d+)%'
        }

        try:
            # Get the regex pattern for the desired vital
            pattern = vital_patterns[vital]
            # Use the pattern to search the file
            match = re.search(pattern, self.file_contents)
            # If a match is found, return the value of the vital
            if match:
                return match.group(1)
            # If no match is found, return '***'
            else:
                return '***'
        except KeyError:
            # If the vital name is not found in the dictionary, return '***'
            return '***'

    def extract_vitals(self, vital_to_extract=None):
        # Define regex patterns for each vital
        patterns = {
            "BP": r"bp:\s*(\d+/\d+)",
            "Pulse": r"pulse:\s*(\d+)",
            "Resp": r"resp:\s*(\d+)",
            "Temp": r"temp:\s*([\d.]+) °f \(([\d.]+) °C\)",
            "SpO2": r"spo2:\s*(\d+)%"
        }

        vitals = {}
        if vital_to_extract:
            pattern = patterns.get(vital_to_extract)
            if pattern:
                match = re.search(pattern, self.file_contents)
                if match:
                    vitals[vital_to_extract] = match.group(1) if vital_to_extract != "Temp" else (match.group(2), match.group(1))
                else:
                    vitals[vital_to_extract] = "***"
            else:
                raise ValueError("Invalid vital specified.")
        else:
            for vital, pattern in patterns.items():
                match = re.search(pattern, self.file_contents)
                if match:
                    vitals[vital] = match.group(1) if vital != "Temp" else (match.group(2), match.group(1))
                else:
                    vitals[vital] = "***"
        return vitals
    
    def extract_all_vitals(self):
        bp = self.extract_vitals(vital_to_extract="bp")["bp"]
        hr = self.extract_vitals(vital_to_extract="pulse")["pulse"]
        rr = self.extract_vitals(vital_to_extract="resp")["resp"]
        spo2 = self.extract_vitals(vital_to_extract="spo2")["spo2"]
        temp = self.extract_vitals(vital_to_extract="temp")["temp"][0]

        return (f"At the time of my evaluation the patient has a BP of {bp} mm Hg, "
                f"HR of {hr} bpm, RR of {rr}/min, SpO2 of {spo2} on RA***, and a Temp. of {temp} F.") 

    # RETRIEVE VITALS FROM THE DATAFRAME CREATED; IF NOT PRESENT IT WILL RETURN ***
    def get_all_vitals(self):
        # Use the get_single_vital function to retrieve the values for each vital
        bp = self.get_single_vital('BP')
        hr = self.get_single_vital('Pulse')
        rr = self.get_single_vital('Resp')
        spo2 = self.get_single_vital('SpO2')
        temp = self.get_single_vital('Temp')
    # Use the retrieved values to build and return the string
        return (f"At the time of my evaluation the patient has a BP of {bp} mm Hg, "
                f"HR of {hr} bpm, RR of {rr}/min, SpO2 of {spo2} on RA***, and a Temp. of {temp} F.")
    
    def extract_vitals_section(self) -> str:
            """
            Extract the Vitals section from the full file_contents text.
            Assumes the section starts with 'Vitals' and ends with a blank line or next header.
            """
            pattern = re.compile(r'Vitals\s*\n(.*?)(?:\n\s*\n|$)', re.DOTALL | re.IGNORECASE)
            match = pattern.search(self.text)
            return match.group(1).strip() if match else ""

    def summarize_vitals(self) -> str:
        vitals_section = self.extract_vitals_section()
        if not vitals_section:
            return "Vitals section not found."

        # Parse vitals into key-value pairs
        lines = vitals_section.splitlines()
        vitals = {line.split(":")[0].strip(): line.split(":", 1)[1].strip() for line in lines if ":" in line}

        # Extract values
        bp = re.search(r'(\d{2,3}/\d{2,3})', vitals.get("BP", ""))
        temp = re.search(r'([\d.]+)\s*°F', vitals.get("Temp", ""))
        temp_src = re.search(r'([A-Za-z ]+)', vitals.get("Temp src", ""))
        pulse = re.search(r'(\d{1,3})', vitals.get("Pulse", ""))
        resp = re.search(r'(\d{1,3})', vitals.get("Resp", ""))
        spo2 = re.search(r'(\d{1,3})\s*%', vitals.get("SpO2", ""))

        # Format extracted values or use fallback
        bp_val = bp.group(1) if bp else "***"
        temp_val = temp.group(1) if temp else "***"
        temp_src_val = temp_src.group(1).strip() if temp_src else "***"
        pulse_val = pulse.group(1) if pulse else "***"
        resp_val = resp.group(1) if resp else "***"
        spo2_val = spo2.group(1) if spo2 else "***"

        # Compose the summary
        summary = (
            f"At the time of my evaluation the patient has a BP of {bp_val} mm Hg, "
            f"HR of {pulse_val} bpm, RR of {resp_val}/min, SpO2 of {spo2_val} on RA ***, "
            f"and a Temp. of {temp_val} F ({temp_src_val})."
        )

        return summary
    
    def extract_vital(self, vital_name: str) -> str:
        """
        Extract a single vital from the Vitals section.
        vital_name can be one of:
          - 'bp' or 'BP'
          - 'temp' or 'Temp'
          - 'hr' or 'pulse'
          - 'rr' or 'resp'
          - 'spo2'
          - 'temp src' (to get source of temperature)
        Returns the captured value (e.g. '120/80', '98.6', '62', 'Temporal') or '***' if not found.
        """
        section = self.extract_vitals_section()
        if not section:
            return "***"

        # turn the section into a dict like {"BP": "115/51 (…)", "Temp": "96.4 °F (…)", …}
        vitals = {
            line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip()
            for line in section.splitlines()
            if ":" in line
        }

        # map user input to the dict key + regex
        key_map = {
            'bp':       ('BP',       r'(\d{2,3}/\d{2,3})'),
            'temp':     ('Temp',     r'([\d\.]+)\s*°F'),
            'temp src': ('Temp src', r'([A-Za-z ]+)'),
            'hr':       ('Pulse',    r'(\d{1,3})'),
            'pulse':    ('Pulse',    r'(\d{1,3})'),
            'rr':       ('Resp',     r'(\d{1,3})'),
            'resp':     ('Resp',     r'(\d{1,3})'),
            'spo2':     ('SpO2',     r'(\d{1,3})'),
        }

        key = vital_name.strip().lower()
        if key not in key_map:
            raise ValueError(f"Unknown vital: {vital_name!r}")

        dict_key, pattern = key_map[key]
        raw = vitals.get(dict_key, "")
        m = re.search(pattern, raw, re.IGNORECASE)
        return m.group(1) if m else "***"

    def check_name(self, disease_list, full_list=False):
        """
        This method checks if a specific disease is mentioned in the file.
        """
        positive_names = []
        for disease in disease_list:
            if self.memoized_search(fr"\b{disease.lower()}\b", self.file_contents):
                if full_list:
                    positive_names.append(disease)
                else:
                    return disease[0]
        if len(positive_names) >= 1:
            return positive_names
        return ''



    def check_missing_tests(self, lab_list, assessment):
        """
        This method checks if tests are present or not, if not --> will ask you to check.
        """
        missing_labs = []
        for lab in lab_list:
            lab_dict = eval(lab)
            lab_name = lab_dict['synonyms'][0]
            if lab_name not in assessment:
                missing_labs.append(lab_name)

        if missing_labs:
            return f"- Check {self.join_list_to_string(missing_labs)}"
        else:
            return ""

    def find_medications(self, medications, _list_only=False):
        """Pass in a list of medications pertaining to either singular drugs or drug classes and return the home meds they are on
        
        Finds medications in a text document.

        Args:
            medications (list or string): A list of medications to search for.
            _list_only (bool): Whether to return a list of medications or a dictionary of medications and their counts.

        Returns:
            list or dict: A list of medications or a dictionary of medications and their counts.
        
        """

        def clean_med_name(medname):
            return medname.strip().lower()

        # convert to list if not already
        if type(medications) == str:
            medications = [medications]

        # NOTE: may move these vars to the masterclass if they take a while to run
        # brand_names = []
        generic_names = []
        brand_names = []
        found_medications = []
        brand_generic_indices = []  # NOTE: inefficient code, may fix later
        # Load up meds from file
        with open('medications.json', 'r') as f:
            meds_dictionary = json.load(f)
        for overall_class in meds_dictionary.keys():
            # add to the generics and brands
            for drug_class in meds_dictionary[overall_class].keys():
                mlist = meds_dictionary[overall_class][drug_class]['medications']
                num_new_brands = len(brand_names)
                for m in mlist.items():
                    generic_names.append(m[0])
                    brand_names.extend(m[1]['brand_names'])
                    for j in range(len(m[1]['brand_names'])):
                        brand_generic_indices.append(len(generic_names) - 1)
                num_new_brands = len(brand_names) - num_new_brands
                # check for classes passed too
                if drug_class in medications:
                    # go through all the brand names and generics of the current class
                    possible_medications = generic_names[(
                        -1 * len(mlist)):] + brand_names[(-1 * num_new_brands):]
                    for possible_med in possible_medications:
                        if self.memoized_search(fr"\b{possible_med.lower()}\b", self.file_contents):
                            if possible_med in generic_names:
                                # NOTE: copy-pasted from below
                                # its in the file and is a generic name
                                found_medications.append(possible_med)
                            else:
                                try:
                                    # its in the file and a brand name, return the generic name
                                    i = brand_names.index(possible_med)
                                    found_medications.append(
                                        generic_names[brand_generic_indices[i]])

                                except:
                                    # the drug is in the file contents but not in our dictionary
                                    # should be extremely rare, may look into this in the future NOTE
                                    found_medications.append(possible_med)

        brand_names = [clean_med_name(a) for a in brand_names]
        generic_names = [clean_med_name(a) for a in generic_names]

        # Match names (for now only individual drug names)
        for med in medications:
            # Individual Drug
            if not self.memoized_search(fr"\b{med.lower()}\b", self.file_contents):
                continue

            if med in generic_names:
                # its in the file and is a generic name
                found_medications.append(med)
            else:
                try:
                    # its in the file and a brand name, return the generic name
                    i = brand_names.index(med)
                    found_medications.append(
                        generic_names[brand_generic_indices[i]])
                except:
                    # the drug is in the file contents but not in our dictionary
                    # should be extremely rare, may look into this in the future NOTE
                    found_medications.append(med)

        found_medications = list(set(found_medications))  #remove duplicates 
        if _list_only:
            # return the meds in an array, makes some other functions easier to write
            return found_medications

        return "On " + self.output_list(found_medications) + " at home"

    def _find_medication_object(self, med, include_drug_class_info=False):
        """helper function to get the object of a med"""

        # Load up meds from file
        with open('medications.json', 'r') as f:
            meds_dictionary = json.load(f)
        for overall_class in meds_dictionary.keys():
            # add to the generics and brands
            for drug_class in meds_dictionary[overall_class].keys():
                mlist = meds_dictionary[overall_class][drug_class]['medications']
                for m in mlist.items():
                    if med == m[0] or med in m[1]['brand_names']:
                        if include_drug_class_info:
                            class_info = {
                                'contraindications': meds_dictionary[overall_class][drug_class][drug_class + ' contraindications'],
                                'indications': meds_dictionary[overall_class][drug_class][drug_class + ' indications'],
                                'cautions': meds_dictionary[overall_class][drug_class][drug_class + ' cautions']
                            }
                            return ((m, class_info))
                        else:
                            return (m)
                        
    def start_new_medication(self, *names):
        """
        Starts new medications for the patient, checking for duplicates, contraindications, and generating instructions.

        Args:
            *names: Variable number of medication names (strings) to start.

        Returns:
            str: Instructions for starting medications, including warnings or stop recommendations.
        """

        preexisting_meds = self.find_all_medications()
        start_list = []
        cont_list = []
        warning_list = []
        stop_list = []

        for name in names:
            #if name in preexisting_meds:

            # Medication already on the list (consider returning a message here)
            #  NEED TO ADD CONTINUE MEDICATIONS IF ALREADY ORDERED IN THE ER
                #continue

            medication_info = self.medication_plan(name)

            if not medication_info:
                start_list.append(name)
            elif medication_info[0] == 'warning':
                warning_list.append(f'– Start *** {name} {" (".join(medication_info[1])})')  # Consistent f-string formatting
            elif medication_info[0] == 'stop':
                stop_list.append(f'– {name.title()} cannot be started due to [{", ".join(medication_info[1])}]')

        add_string = []

        if start_list:
            add_string.append("– Start " + self.format_list(start_list))

        if warning_list:
            add_string.append('\n'.join(warning_list))

        if stop_list:
            add_string.append('\n'.join(stop_list))

        return '\n' + '\n'.join(add_string)  # Join the list of instructions using newline




    def PMH_abbreviations(self, return_diseases=False, all_disease = False):
        abbreviations = []
        detected_diseases = []
        csv_file = "medical_conditions.csv"

        # Define the path to the acute conditions CSV file
        acute_csv_file = "acute_conditions.csv"

        # Step 1: Read the CSV file
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)

            # Step 2: Iterate over each row in the CSV file
            for row in reader:
                disease_names = row['1name_of_disease'].split(',')
                pmh_include = row['PMH_include']

                # Step 3: Check if any of the disease names are present in the text
                for disease_name in disease_names:
                    disease_name = disease_name.strip()
                    pattern = r"\b{}\b".format(re.escape(disease_name))
                    if self.memoized_search(pattern, self.file_contents):
                        abbreviation = row['abbreviations']

                        # Add the detected disease to the list
                        if return_diseases:
                            detected_diseases.append(disease_name)

                        # Step 4: Check if PMH_include is marked with 'x'
                        if all_disease:
                            if abbreviation:
                                abbreviations.append(abbreviation)
                            else:
                                abbreviations.append(disease_name)


                        if pmh_include.lower() == 'x':
                            # Append the abbreviation or full name to the list
                            if abbreviation:
                                abbreviations.append(abbreviation)
                            else:
                                abbreviations.append(disease_name)

                        # Break the loop if a match is found to avoid duplicate entries
                        break
        # If 'acute_only' is True, search for acute conditions in the additional CSV file 
        # detect lab abnormalities and append them
        abnormal_labs = self.show_abnormal_labs(dict_only=True, days_too_old=2)
        for _, abnormalities in abnormal_labs.items():
            if "Too old" in abnormalities:
                continue
            elif len(abnormalities) == 0:
                continue
            else:
                for individual_test, value in abnormalities:
                    if individual_test == "NA":
                        continue
                    abnormal_name = self.abnormality_name(
                        individual_test, value, _lazy_mode=True)
                    if abnormal_name:
                        detected_diseases.append(abnormal_name.lower())
        detected_diseases = list(map(str.lower, detected_diseases))
        detected_diseases = list(set(detected_diseases))
        #remove '' and '12'
        detected_diseases = [x for x in detected_diseases if x != '' and x != '12']
        if return_diseases:
            return detected_diseases
        else:
            # Generate the sentence with PMH items
            if len(abbreviations) > 1:
                last_item = abbreviations[-1]
                pmh_sentence = ", ".join(
                    abbreviations[:-1]) + ", and " + last_item
            else:
                pmh_sentence = abbreviations[0] if abbreviations else ""

            return " with a PMH of " + pmh_sentence
        
        
    def sodium_disorder(self, corr_sod=False):
        """

        Check for sodium disorders based on glucose and sodium levels.

        Args:
            glucose_level (float): The glucose level.
            sodium_level (float): The sodium level.

        Returns:
            list: A list containing information about sodium disorders, including hyponatremia severity and hypernatremia.
                Returns an empty list if there is no sodium disorder.
        
        """
        # Get recent lab values for glucose and sodium
        sodium = self.lab_value("NA")
        glucose = self.lab_value("GLUCOSE")

        # Check for missing or invalid lab values
        if sodium is None or glucose is None:
            return []

        # Correct sodium level for glucose level
        if glucose > 120:
            corrected_sodium = sodium + ((glucose - 100) / 100) * 1.6
        else: 
            corrected_sodium = sodium

        if corr_sod:
            if corrected_sodium:
                return corrected_sodium

        # Categorize corrected sodium levels
        if corrected_sodium > 145:
            return ["Hypernatremia"]
        elif 129 < corrected_sodium < 135:
            return ["Mild hyponatremia"]
        elif 124 < corrected_sodium <= 129:
            return ["Moderate hyponatremia"]
        elif corrected_sodium <= 124:
            return ["Severe hyponatremia"]
        else:
            return []
        

        """
        Need to add pseudohyponatremia
        Normal sodium level if significant hyperglycemia
        """

    def potassium_disorder(self):
        """
        
        Checks for potassium disorders based on the lab values and returns a list
        
        """

        # Obtain potassium level from the text, it will return a float
        potassium = self.lab_value('K')

        # if potassium level is not found it will return an empty list
        if potassium is None:
            return []
        
        # It will check for hypo or hyperkalemia, if hyperkalemia is found it will check for the severity
        if potassium < 3.5:
            return ["Hypokalemia"]
        elif 5.9 >= potassium > 5.5:
            return ["Mild hyperkalemia"]
        elif 6.4 >= potassium > 6:
            return ["Moderate hyperkalemia"]
        elif potassium > 6.4:
            return ["Severe hyperkalemia"]
        else:
            return []


    def calcium_disorder(self, corrected_calcium_level=False):
        """

        Check for calcium disorders based on calcium and albuminlevels.

        Args:
            calcium (float): The calcium level.
            albumin (float): The albumin level level.

        Returns:
            list: A list containing information about calcium disorders, including hypocalcemia and hypercalcemia, severity.
                Returns an empty list if there is no calcium disorder.
        
        """
        # Get recent lab values for glucose and sodium
        calcium = self.lab_value("CA")
        albumin = self.lab_value("ALBUMIN")
        ionized_calcium = self.lab_value("CAIONIZED")

        # Check for missing or invalid lab values
        if calcium is None or albumin is None:
                return []
        # Corrected calcium level for albumin level
        corrected_calcium = calcium + 0.8 * (4 - albumin)

        if corrected_calcium_level:
            return corrected_calcium


        # Categorize corrected sodium levels
        if 12 >= corrected_calcium > 10 or (ionized_calcium and 8 >= ionized_calcium > 5.2):
            return ["Mild hypercalcemia"]
        elif 14 >= corrected_calcium > 12 or (ionized_calcium and 10 >= ionized_calcium > 8):
            return ["Moderate hypercalcemia"]
        elif corrected_calcium > 14 or (ionized_calcium and ionized_calcium > 10):
            return ["Severe hypercalcemia"]
        elif corrected_calcium < 8.6 or (ionized_calcium and ionized_calcium < 4.8):
            return ["Hypocalcemia"]
        else:
            return []
        
        return []

    def magnesium_disorder(self):
        """

        Checks for magnesium disorder, either hypermagnesemia or hypomagnesemia
        
        """

        magnesium = self.lab_value('MG')
        #abnormality_name = self.abnormality_name('MG')

        if magnesium is None:
            return []
        
        if magnesium <= 1.5:
            return ["Hypomagnesemia"]
        else:
            return []
        

    def blood_disorder(self):
        """
        This function should look for anemia, polycythemia, thrombocytopenia, thrombocytosis if present from the labs

        """

        blood_abnormality = []

        platelets = []
        hemoglobin = []

        PLT = self.lab_value('PLT')

        if PLT is not None and PLT <= 50:
            blood_abnormality.append("Severe thrombocytopenia")

        if PLT is not None and 50 < PLT <= 99:
            blood_abnormality.append("Moderate thrombocytopenia")

        if PLT is not None and 99 < PLT < 140:
            blood_abnormality.append("Mild thrombocytopenia")

        if self.abnormality_name('HGB', _lazy_mode=True):
            hemoglobin = self.abnormality_name('HGB', _lazy_mode=True)
        
        if self.abnormality_name('PLT', _lazy_mode=True):
            platelets = self.abnormality_name('PLT', _lazy_mode=True)

        

        if hemoglobin:
            blood_abnormality.append(hemoglobin.title())

        if platelets:
            blood_abnormality.append(platelets.title())
        
        if blood_abnormality:
            return blood_abnormality
        else:
            return []

        
        
 
    def medical_conditions(self, chronic=True, acute=True, pmh_only=False, return_dict=False):
        conditions_dict = {}
        conditions_list = []

        chronic_file = "medical_conditions.csv" # CSV that has the chronic medical conditions
        acute_file = "acute_conditions.csv" # CSV that has the acute medical conditions


        if chronic:
            with open(chronic_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    disease_names = row['1name_of_disease'].split(',')
                    pmh_include = row['PMH_include']

                    found_first_chronic_disease = False

                    for disease_name in disease_names:
                        disease_name = disease_name.strip()
                        pattern = r"\b{}\b".format(re.escape(disease_name))

                        if re.search(pattern, self.file_contents, flags=re.IGNORECASE):
                            if pmh_only and pmh_include.lower() != 'x':
                                continue

                            abbreviation = row.get('abbreviations', '')
                            # Append only the first chronic disease name if not already found
                            if not found_first_chronic_disease:
                                if return_dict:
                                    conditions_dict[disease_name] = abbreviation
                                conditions_list.append(abbreviation if pmh_only and abbreviation else disease_name)
                                found_first_chronic_disease = True

        if acute:
            with open(acute_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    disease_names = row['1name_of_disease'].split(',')

                    found_first_acute_disease = False

                    for disease_name in disease_names:
                        disease_name = disease_name.strip()
                        pattern = r"\b{}\b".format(re.escape(disease_name))

                        if re.search(pattern, self.file_contents, flags=re.IGNORECASE):
                            # Append only the first acute disease name if not already found
                            if not found_first_acute_disease:
                                conditions_list.append(disease_name)
                                found_first_acute_disease = True
            
            # Add sodium disorder to the conditions_list

            conditions_list = conditions_list + self.sodium_disorder() + self.calcium_disorder() + self.magnesium_disorder() + self.potassium_disorder() + self.blood_disorder()

            omit_list = ["mild", "moderate", "severe"]

            conditions_list = [i for i in conditions_list if i not in omit_list]
        
        conditions_list = list(filter(None, set(conditions_list)))

        if return_dict:
            return conditions_dict
        else:
            
            return conditions_list

        
    
    def Acute_conditions(self):

        acute_csv_file = 'acute_conditions.csv'
        detected_diseases = []

        with open(acute_csv_file, 'r') as acute_file:
                acute_reader = csv.DictReader(acute_file)
                for acute_row in acute_reader:
                    acute_condition_name = acute_row['1name_of_disease']
                    pattern = r"\b{}\b".format(re.escape(acute_condition_name))
                    if pattern in self.file_contents.lower():
                        detected_diseases.append(acute_condition_name)

        return acute_condition_name

    """
    def get_PMH(self):
        return ()
        # gives PMHX of MG,HLD,ALS,MS,T2DM
        # MG, ALS, MS. MG is matching meds with "milligrams" in it..., ""
        conditions = []
        for line in self.file_contents.split("\n"):
            if not line.strip():
                continue

            # caching will go here...
            items_to_cache = {}
            try:
                hit = UMLS.match_searchterm_to_abbreviation(line)
            except:
                continue
            if hit != ():
                if hit == "MS" or hit == "ALS" or hit == "MG":
                    print(hit, line)
                conditions.append(hit)

        # remove duplicates, TODO: in the future get rid of overlap of like DM and T2DM
        conditions = list(set(conditions))
        return ",".join(conditions)
    """


    def find_all_medications(self, only_meds_list=False):
        """
        Finds all medications in a text document
        
        """
        meds_list = []

        def clean_med_name(medname):
            return medname.strip().lower()
        brand_names = []
        generic_names = []
        brand_generic_indices = []
        with open('medications.json', 'r') as f:
            meds_dictionary = json.load(f)
        for overall_class in meds_dictionary.keys():
            # add to the generics and brands
            for drug_class in meds_dictionary[overall_class].keys():
                mlist = meds_dictionary[overall_class][drug_class]['medications']
                for m in mlist.items():
                    generic_names.append(m[0])
                    brand_names.extend(m[1]['brand_names'])
                    for j in range(len(m[1]['brand_names'])):
                        brand_generic_indices.append(len(generic_names) - 1)

        brand_names = [clean_med_name(a) for a in brand_names]
        generic_names = [clean_med_name(a) for a in generic_names]

        for m in generic_names:
            if self.memoized_search(fr"\b{m}\b", self.file_contents):
                meds_list.append(m)
        for i in range(len(brand_names)):
            if self.memoized_search(fr"\b{brand_names[i]}\b", self.file_contents):
                meds_list.append(generic_names[brand_generic_indices[i]])
        meds_list = list(set(meds_list))  
        if only_meds_list:
            return meds_list
        else:
            return self.output_list(meds_list)

    def medication_plan(self, medication):
        """Returns False if the medication has no warnings or contraindications, otherwise returns ("warning/stop", list of warnings)"""
        medobj = self._find_medication_object(
            medication, include_drug_class_info=True)

        all_contraindications = list(map(str.lower, medobj[0][1][medobj[0][0] +
                                             ' contraindications'] + medobj[1]['contraindications']))
        all_cautions = list(map(str.lower, medobj[0][1][medobj[0][0] +
                                    ' cautions'] + medobj[1]['cautions']))
        contras = []
        for c in all_contraindications:
            #if c in self.medical_conditions():
            if self.memoized_search(fr"\b{c}\b", self.file_contents):
                contras.append(c)
        if contras:
            return ("stop", contras)

        warnings = []
        for c in all_cautions:
            if self.memoized_search(fr"\b{c}\b", self.file_contents):
                warnings.append(c)
        if warnings:
            return ("warning", warnings)
        return False
    
    def medication_contraindications(self, medication):
        medobj = self._find_medication_object(
            medication, include_drug_class_info=True)
        all_contraindications = medobj[0][1][medobj[0][0] +
                                             ' contraindications'] + medobj[1]['contraindications']
        return all_contraindications

    def find_medications_by_indication(self, indications, only_meds_list=False):
        """
        Find home meds that were indicated
        
        example: find_medications_by_indications('atrial fibrillation')
        """

        if type(indications) != list:
            indications = [indications]
        #make all lowercase
        indications = list(map(str.lower, indications))

        indicated_medications = []
        respective_indications = []
        home_meds = self.all_homemeds
        for medication in home_meds:
            medinfo = self._find_medication_object(
                medication, include_drug_class_info=True)
            all_indications = medinfo[0][1][medinfo[0][0] +
                                            ' indications'] + medinfo[1]['indications']
            all_indications = list(map(str.lower, all_indications))
            rindi = []
            for indication in indications:
                if indication in all_indications:
                    rindi.append(indication)
            if len(rindi) >= 1:
                indicated_medications.append(medication)
                respective_indications.append(rindi)

        # format the output
        """
        indication_strings = []
        for i in range(len(indicated_medications)):
            indication_strings.append(indicated_medications[i] + " [" + ", ".join(respective_indications[i]) + "]")

        return("Indicated: " + ", ".join(indication_strings))
        """
        if only_meds_list:
            return (indicated_medications)
        return ("On " + self.output_list(indicated_medications) + " at home")

    def find_medications_by_contraindication(self, contraindications, only_meds_list=False):
        """
        Find home meds that were contraindicated
        """

        if type(contraindications) != list:
            contraindications = [contraindications]

        #make all lowercase
        contraindications = list(map(str.lower, contraindications))

        contraindicated_medications = []
        respective_contraindications = []

        home_meds = self.all_homemeds
        for medication in home_meds:
            if medication == "ondansetron" or medication == "olanzapine":
                pass
            medinfo = self._find_medication_object(
                medication, include_drug_class_info=True)
            all_contraindications = medinfo[0][1][medinfo[0][0] +
                                                  ' contraindications'] + medinfo[1]['contraindications']
            
            #make all lowercase
            all_contraindications = list(map(str.lower, all_contraindications))
            rindi = []
            for indication in contraindications:
                if indication in all_contraindications:
                    rindi.append(indication)
            if len(rindi) >= 1:
                contraindicated_medications.append(medication)
                respective_contraindications.append(rindi)

        if only_meds_list:
            return contraindicated_medications
        # format the output
        return ("Contraindicated: " + self.output_list(contraindicated_medications))

    def find_medications_by_cautions(self, cautions, only_meds_list=False):
        """Find home meds that were cautioned"""

        if type(cautions) != list:
            cautions = [cautions]
        #make all lowercase
        cautions = list(map(str.lower, cautions))

        contraindicated_medications = []
        respective_contraindications = []

        home_meds = self.all_homemeds
        for medication in home_meds:
            medinfo = self._find_medication_object(
                medication, include_drug_class_info=True)
            all_contraindications = medinfo[0][1][medinfo[0]
                                                  [0] + ' cautions'] + medinfo[1]['cautions']
            #make all lowercase
            all_contraindications = list(map(str.lower, all_contraindications))
            rindi = []
            for indication in cautions:
                if indication in all_contraindications:
                    rindi.append(indication)
            if len(rindi) >= 1:
                contraindicated_medications.append(medication)
                respective_contraindications.append(rindi)

        if only_meds_list:
            return contraindicated_medications
        # format the output
        return ("Cautioned: " + self.output_list(contraindicated_medications))

    def meds_list_plan(self, meds):
        cont_line, conthold_line, hold_line = "– Cont", "– Cont***Hold", "– Hold"
        meds = list(set(meds))
        #for line combinations, if meds have the same warnings/contraindications combine their names
        
        temp_meds_control = deepcopy(self.meds_control)
        to_remove = []
        for m in temp_meds_control['cont']:
            if m not in meds:
                to_remove.append(m)
                #temp_meds_control['cont'].remove(m)
        for t in to_remove:
            temp_meds_control['cont'].remove(t)
        for k in ['warning', 'stop']:
            to_remove = []
            for m in temp_meds_control[k]:
                if m[0] not in meds:
                    to_remove.append(m)
                    #temp_meds_control[k].remove(m)
            for t in to_remove:
                temp_meds_control[k].remove(t)
        temp_meds_control = self._combine_dict(temp_meds_control)
        """
        for med in meds:
            if med in temp_meds_control['cont']:
                cont_line += " " + med + ","
            elif med in [item[0] for item in temp_meds_control['warning']]:
                i = [item[0] for item in temp_meds_control['warning']].index(med)
                conthold_line += " " + med + \
                    " due to " + ", ".join(temp_meds_control['warning'][i][1]) + ","
            elif med in [item[0] for item in temp_meds_control['stop']]:
                i = [item[0] for item in temp_meds_control['stop']].index(med)
                hold_line += " " + med + \
                    " due to " + ", ".join(temp_meds_control['stop'][i][1])  + ","
        """
        if temp_meds_control['cont']:
            cont_line += " " + ", ".join(temp_meds_control['cont'])
        if temp_meds_control['warning']:
            conthold_line += " "
            for medication, warnings in temp_meds_control['warning']:
                conthold_line += medication + " due to " + self.output_list(warnings)
                # if it's not the last med add ", " too
                if not temp_meds_control['warning'][-1] == (medication, warnings):
                    conthold_line += ", "


        if temp_meds_control['stop']:
            hold_line += " "
            for medication, warnings in temp_meds_control['stop']:
                hold_line += medication + " due to " + self.output_list(warnings)
        # Remove trailing comma and add a period
        cont_line = cont_line.rstrip(',') + "."
        conthold_line = conthold_line.rstrip(',') + "."
        hold_line = hold_line.rstrip(',') + "."

        return_line = ""
        if cont_line != "– Cont.":
            return_line += cont_line + "\n"
        if conthold_line != "– Cont***Hold.":
            return_line += conthold_line + "\n"
        if hold_line != "– Hold.":
            return_line += hold_line

        # strip off the last newline
        if return_line and return_line[-1] == "\n":
            return_line = return_line[:-1]

        return return_line

    def plan_for_condition(self, condition):
        indicated = self.find_medications_by_indication(
            condition, only_meds_list=True)
        contraindicated = self.find_medications_by_contraindication(
            condition, only_meds_list=True)
        cautioned = self.find_medications_by_cautions(
            condition, only_meds_list=True)
        plan_string = ""

        if indicated:
            plan_string = "Cont. "

            plan_string += self.output_list(indicated)

        if contraindicated:
            plan_string += "\n\nHold.\n"

            plan_string += self.output_list(contraindicated)

        if cautioned:
            plan_string += "\n\nCont/Hold***\n"

            plan_string += self.output_list(cautioned)

        return plan_string

    def meds_list_assessment(self, meds, condition):
        conthold_line, hold_line = "Cautioned:", "Contraindicated:"

        for med in meds:
            if med in [item[0] for item in self.meds_control['warning']]:
                i = [item[0] for item in self.meds_control['warning']].index(med)
                if condition.lower() in self.meds_control['warning'][i][1]:
                    conthold_line += " " + med + ","
            elif med in [item[0] for item in self.meds_control['stop']]:
                i = [item[0] for item in self.meds_control['stop']].index(med)
                if condition.lower() in self.meds_control['stop'][i][1]:
                    hold_line += " " + med + ","

        # Remove trailing comma and add a period
        conthold_line = conthold_line.rstrip(',') + "."
        hold_line = hold_line.rstrip(',') + "."

        return_line = ""
        if conthold_line != "Cautioned:.":
            return_line += conthold_line + "\n"
        if hold_line != "Contraindicated:.":
            return_line += hold_line

        # strip off the last newline
        if return_line and return_line[-1] == "\n":
            return_line = return_line[:-1]

        return return_line

    def plan_for_condition(self, condition):
        indicated = self.find_medications_by_indication(
            condition, only_meds_list=True)
        contraindicated = self.find_medications_by_contraindication(
            condition, only_meds_list=True)
        cautioned = self.find_medications_by_cautions(
            condition, only_meds_list=True)
        plan_string = ""

        if indicated:
            plan_string = "Cont. "

            plan_string += self.output_list(indicated)

        if contraindicated:
            plan_string += "\n\nHold.\n"

            plan_string += self.output_list(contraindicated)

        if cautioned:
            plan_string += "\n\nCont/Hold***\n"

            plan_string += self.output_list(cautioned)

        return plan_string

    def plan_for_medication(self, medications):
        output_lines = []
        CI, caut = {}, {}
        cont_meds = deepcopy(medications)
        for med in medications:
            medobj = self._find_medication_object(
                med, include_drug_class_info=True)

            all_contraindications = medobj[0][1][medobj[0][0] +
                                                 ' contraindications'] + medobj[1]['contraindications']
            all_cautions = medobj[0][1][medobj[0][0] +
                                        ' cautions'] + medobj[1]['cautions']

            for c in all_contraindications:
                if self.memoized_search(fr"\b{c}\b", self.file_contents):
                    try:
                        cont_meds.remove(med)
                    except:
                        pass
                    if c in CI.keys():
                        CI[c].append(med)
                    else:
                        CI[c] = [med]

            for c in all_cautions:
                if self.memoized_search(fr"\b{c}\b", self.file_contents):
                    try:
                        cont_meds.remove(med)
                    except:
                        pass
                    if self.memoized_search(fr"\b{c}\b", self.file_contents):
                        if c in caut.keys():
                            caut[c].append(med)
                        else:
                            caut[c] = [med]

            if len(CI) > 0:
                output_lines.append(
                    "Hold " + med + " [" + self.output_list(list(CI.values())[0]) + "]")
            elif len(caut) > 0:
                output_lines.append("Cont/Hold*** " + med +
                                    " [" + self.output_list(caut) + "]")
            else:
                output_lines.append("Cont " + med)

        for contraindication in CI:
            output_lines.append(
                "Hold " + self.output_list(CI[contraindication]) + " [" + contraindication + "]")
        for caution in caut:
            output_lines.append(
                "Cont/Hold***  " + self.output_list(caut[caution]) + " [" + caution + "]")
        if len(cont_meds) > 0:
            output_lines.append("Cont. " + self.output_list(cont_meds))

        return ("\n".join(output_lines))

    def cont_hold_caution_medications(self):
        pass

    def corrected_sodium(self, sodium, glucose):
        if type(sodium) == str:
            sodium = float(sodium)
        if type(glucose) == str:
            glucose = float(glucose)

        return (sodium + 0.0024)/(glucose - 100)

    def corrected_calcium(self, calcium, albumin):
        if type(calcium) == str:
            calcium = float(calcium)
        if type(albumin) == str:
            albumin = float(albumin)

        return (0.8 * (4 - albumin)) + calcium
    

    def ED_medications(self):

        line = "Current Facility-Administered Medications".lower()
        index = self.file_contents.lower().find(line)


        if index != -1:
            # Get the substring starting from the index of the line
            text_after_line = self.file_contents[index + len(line):]

            # List will return only the lines that have completed treatment
            completed_treatment_list = [i for i in text_after_line.splitlines() if "[completed]" in i ]

            completed_treatment_paragraph = "".join(completed_treatment_list)

            # List will return only the lines that have not completed treatment, possibly meaning ordered
            ordered_treatment_list = [i for i in text_after_line.splitlines() if "[completed]" not in i]


        return completed_treatment_paragraph
    
    def Completed_treatment_ED(self, completed_treatment=False, ordered_treatment=False):
        # Find the index of the line
        line = "Current Facility-Administered Medications".lower()
        index = self.file_contents.lower().find(line)

        # If the line is found, extract the paragraphs after it
        if index != -1:
            # Get the substring starting from the index of the line
            text_after_line = self.file_contents.lower()[index + len(line):]

            # List will return only the lines that have completed treatment
            completed_treatment_list = [i for i in text_after_line.splitlines() if "[completed]" in i ]

            # List will return only the lines that have not completed treatment, possibly meaning ordered
            ordered_treatment_list = [i for i in text_after_line.splitlines() if "[completed]" not in i]

            # if completed_treatment is set as true it will return the treatment that has been completed
            if completed_treatment:
                completed_treatment_paragraph = " ".join(completed_treatment_list)
                meds = MasterClass(file_contents=completed_treatment_paragraph).find_all_medications()
                if meds:
                    return meds
                else:
                    return "***"
            # if ordre_treatment is set as true it will return the treatment that has been completed
            if ordered_treatment:
                ordered_treatment_paragraph = " ".join(ordered_treatment_list)
                meds = MasterClass(file_contents=ordered_treatment_paragraph).find_all_medications()
                if meds:
                    return meds
                else:
                    return "***"
                
        else:
            return "***"

    
    def _find_edmedslist(self):
        # Split the text into lines
        lines = self.file_contents.split('\n')
        
        # Initialize an empty list to hold the lines of the paragraph
        paragraph_lines = []
        
        # Initialize a flag to indicate whether we're inside the paragraph
        in_paragraph = False
        
        # For each line in the text...
        for line in lines:
            # If we're inside the paragraph and the line is empty, we're done
            if in_paragraph and line == '':
                break
            
            # If we're inside the paragraph, add the line to the list
            if in_paragraph:
                paragraph_lines.append(line)
                
            # If this line is the start of the paragraph, set the flag to True
            if line.startswith('current facility-administered medications'):
                in_paragraph = True
        
        # Join the lines of the paragraph with newlines
        paragraph = '\n'.join(paragraph_lines)
        
        # If the paragraph is not empty, return it; otherwise, return None
        return paragraph if paragraph != '' else None


    def ed_meds(self, only_meds_list=False):
        """Returns a list of medications that were given in the ED"""

        txt = self._find_edmedslist()
        
        # If a paragraph is found, return it; otherwise, return None
        if not txt:
            return()

        completed_medications = []
        ordered_medications = []
        
        # Split the paragraph into lines
        lines = txt.split("\n")
        
        # For each line in the paragraph
        for line in lines:
            # If the line starts with • [COMPLETED], it's a completed medication
            if "completed" in line:
                completed_medications.append(line[14:].strip())  # Strip the leading '• [COMPLETED] ' and trailing whitespace
            # If the line starts with •, it's an ordered medication
            elif line.startswith("•"):
                ordered_medications.append(line[2:].strip())  # Strip the leading '• ' and trailing whitespace

        #stop each line at the first number
        for i in range(len(completed_medications)):
            completed_medications[i] = re.split(r'(\d+)', completed_medications[i])[0]
        for i in range(len(ordered_medications)):
            ordered_medications[i] = re.split(r'(\d+)', ordered_medications[i])[0]
        
        if only_meds_list:
            return completed_medications, ordered_medications
        else:
            return "ED Meds Administered: " + self.output_list(completed_medications) + "\nED Meds Ordered: " + self.output_list(ordered_medications)


    def lab_value(self, lab_name):
        try:
            lab = self.check_labs([lab_name], dict_mode=True, days_too_old=2)
            return float(lab[lab_name][0][0])
        except:
            pass

    def type_of_fluids(self):
        """
        Determine the type of fluids based on medical conditions.

        This function analyzes medical conditions to provide recommendations for the type of intravenous (IV) fluids to use.
        It considers conditions related to volume overload and preferences for normal saline (NS) in certain situations.

        Returns:
            str: A string describing the recommended type of IV fluids based on medical conditions.
        """

        # Initialize the result string
        ret_string = []

        # Get all the conditions found in the text
        conditions = self.medical_conditions()

        # Conditions associated with volume overload
        volume_overload = ['Acute heart failure', 'End stage renal disease', "Anasarca", 'Volume overload', 'Chronic congestive heart failure']
        volume_overload_list = [i for i in volume_overload if i in conditions]

        # Conditions when normal saline (NS) is a preferred agent
        normal_saline = ["Intractable nausea and vomiting", "Small bowel obstruction"]

        # Checks for conditions where IV fluids can be deleterious
        if volume_overload_list:
            ret_string.append(f'– Cautious with IV fluids [{", ".join(volume_overload_list)}]')
        else:
            ret_string.append('– IV fluids')

        # Check for hypercalcemia; if the patient has hypercalcemia, LR cannot be used    
        if any(condition in conditions for condition in ["Severe hypercalcemia", "Mild hypercalcemia", "Moderate hypercalcemia"]):
            ret_string.append("Avoid LR due to hypercalcemia")

        # Combine the result string and return
        return ' '.join(ret_string)

    
    def detect_anticoagulation(self):
        return self.find_medications("Anticoagulants")
    

    """
    Add a feature to check for warfarin interactions when INR is supratherapeutic
    Drug-drug interactions
    
    """
    
    def _find_names_in_string(self, names_list, content):
        names_list = [str(name).lower() for name in names_list]
        # Convert the list of names into a set for O(1) lookup times
        names_set = set(names_list)

        # Keep a set to store names found in the content
        found_names = set()

        # Split the content by newline characters (or whitespace if it's not line-separated)
        for line in content.split('\n'):
            # Remove any leading/trailing whitespace
            line = line.strip()

            # If the line matches a name in the set, add to found names
            if line in names_set:
                found_names.add(line)

        return list(found_names)
    

    def map_conditions_to_abbr(self, disease_list, disease_dict):
        """
        Maps disease names in a list to corresponding abbreviations from a dictionary, handling different capitalizations.

        Args:
            disease_list: A list of disease names (may have varying capitalizations).
            disease_dict: A dictionary mapping disease names (keys, may have varying capitalizations) to abbreviations (values).

        Returns:
            A list containing abbreviations for diseases with corresponding entries in the dictionary 
            and the original names for those not found or with empty values.
        """
        conditions_assoc = []
        for disease in disease_list:
            # Lowercase the disease name for case-insensitive matching
            disease_lower = disease.lower()
            # Standardize capitalization in the dictionary by lowercasing all keys
            disease_dict_lower = {key.lower(): value for key, value in disease_dict.items()}
            
            if disease_lower in disease_dict_lower:
                abbreviation = disease_dict_lower[disease_lower]
                if abbreviation:
                    conditions_assoc.append(abbreviation)
            else:
                conditions_assoc.append(disease)
        return conditions_assoc





    def shorter_ver_prev_labs(data):
        # Initialize variables to keep track of the oldest TSH level and date
        oldest_level = None
        oldest_date = None

        # Iterate through the list of TSH values in the 'TSH' key of the input dictionary
        for tsh_values in data.get('TSH', []):
            # Check if there are exactly 2 values in the TSH entry (value and date)
            if len(tsh_values) == 2:
                tsh_value, date_str = tsh_values
                try:
                    # Parse the date string into a datetime object
                    date = datetime.strptime(date_str, '%m/%d/%Y')
                    
                    # Check if the current date is older than the previously found oldest date
                    if oldest_date is None or date < oldest_date:
                        # If it is, update the oldest date and TSH level
                        oldest_date = date
                        oldest_level = float(tsh_value)
                except ValueError:
                    # Ignore invalid date formats
                    pass

        # Return the oldest TSH level (or None if no valid levels were found)
        return oldest_level
    
    def _combine_dict(self, dct):
        inverted_dict = {}
        combined_dict = {'cont': dct['cont']}  # initialize combined_dict with 'cont' values

        for k, values in dct.items():
            if k == 'cont':
                continue  # skip 'cont' key as it doesn't have associated values in tuple format
            for v in values:
                drug_name, assoc_values = v
                key = (k, tuple(sorted(assoc_values)))  # tuple with primary key and sorted associated values
                if key in inverted_dict:
                    inverted_dict[key].append(drug_name)
                else:
                    inverted_dict[key] = [drug_name]

        for (main_key, assoc_key), v in inverted_dict.items():
            combined_key = self.output_list(v)
            if main_key in combined_dict:
                combined_dict[main_key].append((combined_key, list(assoc_key)))
            else:
                combined_dict[main_key] = [(combined_key, list(assoc_key))]

        #add warning, stop keys if they are missing
        if "warning" not in combined_dict.keys():
            combined_dict["warning"] = []

        if "stop" not in combined_dict.keys():
            combined_dict["stop"] = []
        return combined_dict
    
    def start_med(self, med):
        if med in self.all_homemeds:
            return()
        else:
            med_plan = self.plan_for_medication([med])
            if "Cont." in med_plan:
                #OK to start it
                return("Start " + med)
            else:
                return(med_plan)
            

    def extract_images(self):
        # Dictionary of the names
        name_of_study = {
            
            'MRI BRAIN WO CONTRAST': 'MRI brain wo contrast',
            "XR ANKLE 3+ VW LEFT": 'X-ray left ankle',
            'XR FOOT 3+ VW LEFT': 'X-ray left foot',
            'MRI FOOT W WO CONTRAST LEFT' : 'MRI foot w and wo contrast',
            'MRI ANKLE W WO CONTRAST LEFT' : 'MRI ankle w and wo contrast',
            'XR CHEST PA OR AP 1 VW' : 'Chest x-ray',


            # Chest imaging
            'CT CHEST WO CONTRAST': 'CT chest wo contrast',
            "XR CHEST PA AND LATERAL 2 VW" : 'Chest x-ray PA/L view',
            'CT CHEST W CONTRAST': 'CT chest w contrast',
            'CT CHEST WO CONTRAST': 'CT chest wo contrast',
            'CTA CHEST W AND/OR WO CONTRAST' : 'CTA chest',
            'CT CHEST ABDOMEN PELVIS W CONT' : 'CT chest/abdomen/pelvis w contrast',


            # Kidney, bladder imaging
            'US RENAL AND BLADDER' : 'US kidney/bladder',

            # Abdominal imaging
            'CT ABDOMEN PELVIS W CONTRAST' : 'CT abdomen/pelis w contrast'

        }
        
        # Clean the text
        self.image_text = re.sub("IMPRESSION: Please see below.", "", self.image_text)

        # Output list
        study_list = []
        
        # Define regex pattern to extract the name of the exam
        exam_pattern = r'^Exam:\s*(.*?)\n'
        
        # Extract exam name
        exam_matches = re.findall(exam_pattern, self.image_text, re.MULTILINE)
        
        # Define regex pattern to extract the entire impression section
        impression_pattern = r'IMPRESSION:\s*([\s\S]*?)(?:\n\n|$)'
        
        # Extract impressions
        impression_matches = re.findall(impression_pattern, self.image_text)
        
        # Print results
        for exam, impression in zip(exam_matches, impression_matches):
            exam_name = exam.strip()
            impression_text = impression.strip().replace('\n', ' ')
            for generic_name, study_name in name_of_study.items():
                if generic_name == exam_name:
                    study_list.append(f"{study_name}: {impression_text}")

        
        return '\n\n'.join(study_list)
    





text_from_epic = """
 is a 81 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	5.3	04/17/2024 06:10 AM
	RBC	4.14 (L)	04/17/2024 06:10 AM
	HGB	10.8 (L)	04/17/2024 06:10 AM
	HGB	11.9 (L)	04/16/2024 12:32 PM
	HCT	34.8 (L)	04/17/2024 06:10 AM
	MCV	84.1	04/17/2024 06:10 AM
	MCH	26.1 (L)	04/17/2024 06:10 AM
	MCHC	31.0	04/17/2024 06:10 AM
	PLT	209	04/17/2024 06:10 AM
	PLT	209	04/16/2024 12:32 PM
	RDW	17.2 (H)	04/17/2024 06:10 AM
	NEUTROPHIL	4.00	04/17/2024 06:10 AM
	LYMPHOCYTE	0.56 (L)	04/17/2024 06:10 AM
	EOSINOPHIL	0.19	04/17/2024 06:10 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	143	04/17/2024 06:10 AM
	K	3.6	04/17/2024 06:10 AM
	CL	102	04/17/2024 06:10 AM
	CO2	30 (H)	04/17/2024 06:10 AM
	CA	9.4	04/17/2024 06:10 AM
	CA	9.1	04/16/2024 12:32 PM
	BUN	13	04/17/2024 06:10 AM
	CREAT	1.06	04/17/2024 06:10 AM
	GFR	>60	04/17/2024 06:10 AM
	GFR	>60	04/16/2024 12:32 PM
	GLUCOSE	98	04/17/2024 06:10 AM
	TOTALPROTEIN	6.9	04/16/2024 12:32 PM
	ALBUMIN	4.0	04/16/2024 12:32 PM
	BILITOTAL	0.4	04/16/2024 12:32 PM
	LIPASE	38	08/14/2020 07:56 PM
	URICACID	7.0	05/04/2023 10:36 AM
	URICACID	6.3	10/21/2019 11:12 AM
	ALKPHOS	103	04/16/2024 12:32 PM
	ALKPHOS	83	11/07/2023 10:09 AM
	ALKPHOS	90	05/04/2023 10:36 AM
	ALKPHOS	83	09/19/2022 02:21 PM
	AST	26	04/16/2024 12:32 PM
	ALT	25	04/16/2024 12:32 PM
	ANIONGAP	11	04/17/2024 06:10 AM
	MG	2.2	04/16/2024 12:32 PM
	MG	2.4	09/16/2022 09:30 AM
	PO4	3.4	05/11/2021 05:39 AM
	T4FREE	1.16	04/20/2021 10:02 AM
	LACTATE	0.7	07/08/2021 01:09 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	48 (H)	04/16/2024 12:32 PM
	BASETROP	38 (H)	09/19/2022 02:21 PM
	2HRTROP	47 (H)	04/16/2024 03:09 PM
	2HRTROP	41 (H)	09/19/2022 04:14 PM
	DELTA	-6	04/16/2024 06:49 PM
	DELTA	-1	04/16/2024 03:09 PM
	6HRTROP	42 (H)	04/16/2024 06:49 PM
	6HRTROP	40 (H)	09/19/2022 08:22 PM
	PROBNPNTERMI	464 (H)	04/16/2024 12:32 PM
	PROBNPNTERMI	129	02/09/2023 12:45 PM
	INR	1.0	04/16/2024 12:32 PM
	PT	14.0	04/16/2024 12:32 PM
	APTT	68.3 (H)	04/15/2021 01:20 PM


workup
Lab Results
Component	Value	Date/Time
	IRON	36 (L)	12/17/2020 03:04 PM
	IRON	38 (L)	08/14/2020 10:08 AM
	TIBC	447	12/17/2020 03:04 PM
	TIBC	508 (H)	08/14/2020 10:08 AM
	IRONPERCENT	8 (L)	12/17/2020 03:04 PM
	IRONPERCENT	7 (L)	08/14/2020 10:08 AM
	FERRITIN	57.5	12/17/2020 03:04 PM
	FERRITIN	208.6	11/01/2018 02:12 AM
	VITAMINB12	870	06/30/2020 11:53 AM
	VITAMINB12	380	11/01/2018 05:43 AM
	FOLATE	>20.0	06/30/2020 11:53 AM
	FOLATE	>20.0 (H)	11/01/2018 05:43 AM


Lab Results
Component	Value	Date/Time
	PHUA	7.0	07/07/2021 02:34 PM
	SGUR	1.010	07/07/2021 02:34 PM
	URINELEUKOC	Negative	07/07/2021 02:34 PM
	NITRITEUA	Negative	07/07/2021 02:34 PM
	KETONEURINE	Negative	07/07/2021 02:34 PM
	PROTEINUA	2+ (A)	07/07/2021 02:34 PM
	GLUUA	Negative	07/07/2021 02:34 PM
	BLOODUA	Negative	07/07/2021 02:34 PM
	WBCU	0-2	07/07/2021 02:34 PM
	RBCUA	0-2	07/07/2021 02:34 PM
	BACTERIAUA	Negative	07/07/2021 02:34 PM
	UREPITHELIAL	0-5	04/26/2021 11:00 AM


Lab Results
Component	Value	Date/Time
	ESR	14	01/02/2020 10:38 AM
	CRP	4.2	01/02/2020 10:38 AM


Lab Results
Component	Value	Date/Time
	PHBLOODPOC	7.44	04/24/2021 06:42 PM
	PCO2POC	40	04/24/2021 06:42 PM
	PO2POC	109 (H)	04/24/2021 06:42 PM
	O2SATPOC	99 (H)	04/24/2021 06:42 PM


Lab Results
Component	Value	Date/Time
	INFLUENZAA	Not Detected	07/07/2021 11:18 AM
	INFLUENZAB	Not Detected	07/07/2021 11:18 AM
	COVID19	Not Detected	04/16/2024 12:31 PM
	RSVAG	Not Detected	07/07/2021 11:18 AM


Lab Results
Component	Value	Date/Time
	HGBA1C	5.6	05/26/2020 08:24 AM
	LDLCALC	101 (H)	11/07/2023 10:09 AM


Lab Results
Component	Value	Date/Time
	TRIGLYCERIDE	132	11/07/2023 10:09 AM
	TSH	2.41	04/16/2024 12:32 PM


No results found for: "AMPHETAMINEQ", "BARBITQLUR", "BENZDIAQLUR", "CANNABQLUR", "COCAINEQUAL", "METHADONEU", "OPIATEQUA", "OXYCODQLUR", "PHENCYCLID"

Toxicology
No results found for: "ETHANOL", "ACETAMINOPHE", "SALICYLATE"

Vitamins
Lab Results
Component	Value	Date/Time
	VITAMINDTO	42	04/02/2018 01:33 PM


Tumor markers
No results found for: "AFPTM"

Virology
Lab Results
Component	Value	Date/Time
	HEPCAB	Non-reactive	08/20/2018 11:05 AM
 


GIPATHOGEN
No results found for: "CLOSTRIDIU"




Principal Problem:
  Acute diastolic heart failure
Active Problems:
  Hypertrophic cardiomyopathy
    Overview: ECHO 2017
    
  COPD, mild
  GAD (generalized anxiety disorder)
  Gastroesophageal reflux disease without esophagitis
  BPH (benign prostatic hyperplasia)
  OSA (obstructive sleep apnea)
  Mixed hyperlipidemia
  Presence of Watchman left atrial appendage closure device
  Atypical atrial flutter
  History of atrial fibrillation
  Acute on chronic congestive heart failure
  Long QT interval
  Atrial fibrillation
  Hypertrophic obstructive cardiomyopathy (HOCM)
 


Vitals:
	04/17/24 1009
BP:	(!) 127/106
Pulse:	(!) 130
Resp:	
Temp:	
SpO2:	



Prior to Admission Medications
Prescriptions	Last Dose	Informant	Patient Reported?	Taking?
DULoxetine (CYMBALTA) 60 mg Capsule, Delayed Release(E.C.)			No	No
Sig: take 1 capsule by mouth twice daily
Potassium 99 mg Tablet			Yes	No
Sig: Take 99 mg by mouth daily.
allopurinoL (ZYLOPRIM) 100 mg tablet			No	No
Sig: take 1 tablet by mouth every day
aspirin (ECOTRIN EC) 81 mg Tablet, Delayed Release (E.C.)			No	No
Sig: Take 1 Tablet (81 mg) by mouth daily.
atorvastatin (LIPITOR) 40 mg tablet			No	No
Sig: TAKE 1 TABLET (40 MG) BY MOUTH DAILY.
buPROPion (WELLBUTRIN) 75 mg tablet			No	No
Sig: TAKE 1 TABLET (75 MG) BY MOUTH 2 TIMES DAILY.
busPIRone (BUSPAR) 7.5 mg Tablet			No	No
Sig: take 1 tablet by mouth two times a day
cetirizine (ZyrTEC) 10 mg tablet			Yes	No
Sig: Take 10 mg by mouth daily.
ciclopirox (LOPROX) 0.77 % Cream			No	No
Sig: Apply to affected area 2 times daily.
cyanocobalamin (VITAMIN B-12) 500 mcg tablet			Yes	No
Sig: Take 500 mcg by mouth daily.
diltiaZEM (CARDIZEM CD) 180 mg Controlled Delivery 24 hour capsule			No	No
Sig: take 1 capsule by mouth two times a day
dofetilide (TIKOSYN) 250 mcg capsule			No	No
Sig: TAKE 1 CAPSULE (250 MCG) BY MOUTH EVERY 12 HOURS.
fluticasone propionate (FLOVENT HFA) 110 mcg/actuation HFA Aerosol Inhaler			No	No
Sig: TAKE 2 PUFFS BY INHALATION 2 TIMES DAILY.
furosemide (LASIX) 40 mg tablet			No	No
Sig: TAKE 1 TABLET (40 MG) BY MOUTH 2 TIMES DAILY.
ketoconazole (NIZORAL) 2 % Cream			No	No
Sig: APPLY TO THE AFFECTED AREA DAILY
magnesium oxide 250 mg magnesium Tablet			Yes	No
Sig: Take 250 mg by mouth daily.
montelukast (SINGULAIR) 10 mg tablet			No	No
Sig: take 1 tablet by mouth every night at bedtime
multivitamin (DAILY-VITE) tablet			Yes	No
Sig: Take 1 Tablet by mouth daily.
pantoprazole (PROTONIX) 40 mg Tablet, Delayed Release (E.C.)			No	No
Sig: TAKE 1 TABLET(40 MG) BY MOUTH TWICE DAILY
pregabalin (Lyrica) 150 mg Capsule			No	No
Sig: Take 1 Capsule (150 mg) by mouth every 8 hours.
tamsulosin (FLOMAX) 0.4 mg capsule			No	No
Sig: TAKE 1 CAPSULE BY MOUTH EVERY DAY

Facility-Administered Medications: None


Current Facility-Administered Medications
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	[COMPLETED] polyethylene glycol (MIRALAX) packet 17 Gram	 17 Gram	Oral	ONE time only	Patel, Taksh, MD	 	17 Gram at 04/17/24 0410
•	[COMPLETED] ipratropium-albuteroL (DUONEB) 0.5 mg-3 mg(2.5 mg base)/3 mL inhalation solution 3 mL	 3 mL	Inhalation	resp, one time only	Gammon, Dustin, DO	 	3 mL at 04/16/24 1454
•	[COMPLETED] LORazepam (ATIVAN) tablet 1 mg	 1 mg	Oral	ONE time only	Gammon, Dustin, DO	 	1 mg at 04/16/24 1222
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	sodium chloride flush injection 5 mL	 5 mL	IV	every 12 hours (2 times daily)	Zguri, Liridon, MD	 	5 mL at 04/17/24 0808
•	sodium chloride flush injection 5 mL	 5 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	sodium chloride 0.9 % 250 mL flush bag 25 mL	 25 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	dextrose 5 % in water 250 mL flush bag 25 mL	 25 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	acetaminophen (TYLENOL) tablet 650 mg	 650 mg	Oral	every 6 hours PRN	Zguri, Liridon, MD	 	 
•	furosemide (LASIX) injection 40 mg	 40 mg	IV	BID, 7 hours apart	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	[COMPLETED] potassium chloride 20 mEq in sodium chloride 0.9% 150 mL IVPB	 20 mEq	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 04/16/24 1708
•	enoxaparin (LOVENOX) injection 40 mg	 40 mg	subCUT	every 24 hours	Gammon, Dustin, DO	 	40 mg at 04/17/24 0808
•	cefTRIAXone (ROCEPHIN) 2,000 mg in sodium chloride 0.9% 50 mL IVPB (MBP)	 2,000 mg	IV	every 24 hours	Zguri, Liridon, MD	 	Stopped at 04/16/24 1643
•	doxycycline hyclate (VIBRAMYCIN) 100 mg in sodium chloride 0.9% 100 mL IVPB (MBP)	 100 mg	IV	every 12 hours	Zguri, Liridon, MD	 	Stopped at 04/17/24 0436
•	diltiaZEM (CARDIZEM CD) SR 24 hour capsule 180 mg	 180 mg	Oral	BID	Farmer, Sarah, FNP	 	180 mg at 04/17/24 1009
•	[COMPLETED] potassium bicarbonate-citric acid (EFFER-K) tablet 20 mEq	 20 mEq	Oral	ONE time only	Zguri, Liridon, MD	 	20 mEq at 04/16/24 1723
•	pantoprazole (PROTONIX) tablet 40 mg	 40 mg	Oral	daily BEFORE breakfast	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	tamsulosin (FLOMAX) SR 24 hour capsule 0.4 mg	 0.4 mg	Oral	daily	Zguri, Liridon, MD	 	0.4 mg at 04/17/24 0807
•	atorvastatin (LIPITOR) tablet 40 mg	 40 mg	Oral	daily	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	DULoxetine (CYMBALTA) capsule 60 mg	 60 mg	Oral	BID	Zguri, Liridon, MD	 	60 mg at 04/17/24 0807
•	montelukast (SINGULAIR) 10 mg tablet 10 mg	 10 mg	Oral	daily BEDTIME	Zguri, Liridon, MD	 	10 mg at 04/16/24 2139
•	[DISCONTINUED] potassium CHLORIDE 20 mEq/50 mL IVPB 20 mEq	 20 mEq	IV	ONE time only	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] enoxaparin (LOVENOX) injection 40 mg	 40 mg	subCUT	every 24 hours	Zguri, Liridon, MD	 	 


CT CHEST WO CONTRAST
Final Result
IMPRESSION: Please see below. 
 
Exam: CT CHEST WO CONTRAST 
 
Date/Time of Exam: 4/16/2024 3:01 PM 
 
REASON FOR EXAM: Respiratory illness, nondiagnostic xray. 
 
DIAGNOSIS: Acute on chronic congestive heart failure, unspecified 
heart failure type; Dyspnea, unspecified type. 
 
Technique: CT of the chest was performed without the administration of 
intravenous contrast. 
 
Findings: Comparison is made to the prior CT of the chest performed 
1/10/2023. 
 
There is a small loculated pleural effusion on the left which is new 
since the prior examination. There are hazy interstitial infiltrates, 
greatest in lung bases likely representing edema. This is seen in the 
setting of pulmonary vascular congestion. Trace right pleural effusion 
with cardiomegaly and pulmonary artery enlargement. Coronary artery 
disease and a left atrial appendage closure device are noted. 
 
The imaged abdominal structures are grossly unremarkable. There is 
cervicothoracic spondylosis. Mild degenerative changes in the right 
shoulder girdle are partially imaged. Old healed bilateral rib 
fractures are seen. 
 
IMPRESSION: 
 
 
Findings most consistent with CHF exacerbation with cardiomegaly, 
pulmonary vascular congestion, and small loculated left pleural 
effusion and trace right pleural effusion. Interstitial infiltrates 
may also represent some degree of pneumonitis and there is some 
peribronchial thickening which could indicate mild 
bronchitis/bronchopneumonia in the proper clinical setting. 
 

XR CHEST PA AND LATERAL 2 VW
Final Result
IMPRESSION: Please see below. 
 
Exam: XR CHEST PA AND LATERAL 2 VW 
 
Date/Time of Exam: 4/16/2024 12:58 PM 
 
REASON FOR EXAM: Shortness of Breath SOB. 
 
DIAGNOSIS: See Reason for Exam. 
 
Findings: Comparison is made to the prior examination performed 
9/19/2022. 
 
There are patchy interstitial infiltrates in the lower lungs with some 
consolidation in the left lung suspected. A small left pleural 
effusion is not entirely excluded. There is cardiomegaly with 
pulmonary vascular congestion and a left atrial appendage occlusion 
devices noted. The thoracic aorta is grossly unremarkable. There is 
cervicothoracic spondylosis. Old healed right rib fractures and left 
rib fractures are noted. Suture anchors are partially imaged in the 
right shoulder girdle. 
 
IMPRESSION: 
 
Findings most consistent with CHF exacerbation with pulmonary vascular 
congestion, cardiomegaly, and mild interstitial edema. There may be 
some mild left basilar consolidation and a small pleural effusion. 




"""

# print(MasterClass(file_contents=text_from_epic).check_labs('HGB', dict_mode=True ))






