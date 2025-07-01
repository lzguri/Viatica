import re
import pandas as pd

class Disease():

    def __init__(self, name, MCI, display_home_meds=True, full_meds_plan = False):
        self._extra_assessment_info = []
        self.display_home_meds = display_home_meds
        self.assessment, self.plan = {}, {}
        self.full_meds_plan = full_meds_plan
        self.fn = MCI
        dfrow = pd.read_csv("acute_conditions.csv",
                            keep_default_na=False, na_values=["", " "]) # example if NA (sodium) will no be detected as na
        # extract row from csv matching the name, case insensitive
        dfrow = dfrow[dfrow['1name_of_disease'].str.lower() == name.lower()]

        # Helper function for loading labs
        if dfrow is None or dfrow.empty:
            raise Exception("Disease not found")

        # convert dfrow to dictionary for ease of use
        dfrow = dfrow.to_dict(orient='list')
        dfrow = {key: value[0] for key, value in dfrow.items()}
        # delete null values
        dfrow = {key: value for key,
                 value in dfrow.items() if pd.notnull(value)}
        self.dfrow = dfrow
        keys = dfrow.keys()

        # ==== ASSESSMENT ====
        self.name = dfrow['1name_of_disease']

        # extract the current labs
        if 'current_labs' in keys:
            lists = self._load_labs(dfrow['current_labs'])
            lists, labels = lists[0], lists[1]
            if 'comparison_current_labs' in keys:
                followsups = [x.strip()
                              for x in dfrow['comparison_current_labs'].split(",")]
            else:
                followsups = []
            # Extract the labs into strings
            current_labs = []
            for l in range(len(lists)):
                if labels[l] is not None:
                    check_labs_str = self.fn.check_labs(lists[l], display_text=True,
                                                                         dict_mode=False, comparisons=followsups, days_too_old=2)
                    if check_labs_str:
                        current_labs.append(labels[l] + ": " + check_labs_str)
                else:
                    current_labs.append(self.fn.check_labs(lists[l], display_text=True,
                                                      dict_mode=False, comparisons=followsups, days_too_old=2))
            self.assessment['current_labs'] = current_labs

        # extract followup labs
        if 'followup_labs' in keys:
            lists = self._load_labs(dfrow['followup_labs'])
            lists, labels = lists[0], lists[1]
            if 'comparison_followup_labs' in keys:
                followsups = [x.strip()
                              for x in dfrow['comparison_followup_labs'].split(",")]
            else:
                followsups = []
            # Extract the labs into strings
            followup_labs = []
            for l in range(len(lists)):
                if labels[l] is not None:
                    check_labs_str = self.fn.check_labs(lists[l], display_text=True,
                                                                          dict_mode=False, comparisons=followsups, group_by_date=True, most_recent=True)
                    if check_labs_str:
                        followup_labs.append(labels[l] + ": " + check_labs_str)
                    else:
                        continue
                else:
                    followup_labs.append(self.fn.check_labs(lists[l], display_text=True,
                                                       dict_mode=False, comparisons=followsups, group_by_date=True, most_recent=True))
            self.assessment['followup_labs'] = followup_labs

        if 'superseded_chronic_conditions' in keys:
            self.assessment['superseded_chronic_conditions'] = [
                dfrow['superseded_chronic_conditions']]

        if 'associated_conditions' in keys:
            associated_conditions = []
            for condition in dfrow['associated_conditions'].split(","):
                condition = condition.strip().lower()
                if self.fn.check_name([condition]):
                    associated_conditions.append(condition)
            if associated_conditions != []:
                # Remove duplicates and apply title case
                associated_conditions = list(set(associated_conditions))
                associated_conditions = [x for x in associated_conditions]
                self.assessment['associated_conditions'] = []

            disease_dict = self.fn.medical_conditions(return_dict = True)


            

            self.assessment['associated_conditions'] = self.fn.map_conditions_to_abbr(associated_conditions, disease_dict)

        if 'home_meds' in keys:
            con = [x.strip().lower()
                   for x in dfrow['home_meds'].split(",")] + [self.name.lower()]
            #TODO: i think the loop isn't needed, can just throw every name as a list in at once
            meds = []
            for c in con:
                meds.extend(self.fn.find_medications_by_indication(
                    c, only_meds_list=True))
            meds = list(set(meds))
            if meds != []:
                self.assessment['home_meds'] = meds

        #Check for contraindicated meds
        if 'home_meds' in keys:
            con = [x.strip().lower() for x in dfrow['home_meds'].split(",")] + [self.name.lower()]
            meds = []
            for c in con:
                meds.extend(self.fn.find_medications_by_contraindication(c, only_meds_list=True))
            meds = list(set(meds))
            if meds != []:
                self.assessment['contraindicated'] = meds

        #Check for cautioned meds
        if 'home_meds' in keys:
            con = [x.strip().lower() for x in dfrow['home_meds'].split(",")]
            meds = []
            for c in con:
                meds.extend(self.fn.find_medications_by_cautions(c, only_meds_list=True))
            meds = list(set(meds))
            if meds != []:
                self.assessment['cautioned'] = meds

        if 'other_assessment' in keys:
            self.assessment['other_assessment'] = dfrow['other_assessment']

        if 'hpi_assessment' in keys:
            self._extra_assessment_info = [x.strip() for x in dfrow['hpi_assessment'].split(",")]

        # ==== PLAN ====
        if 'other_plan' in keys:
            self.plan['other_plan'] = dfrow['other_plan']

        if 'check_missing_labs' in keys:
            self.missing_labs = [x.strip()
                                 for x in dfrow['check_missing_labs'].split(",")]
            self.plan['missing_labs'] = []
            miss = self.fn.check_labs(
                self.missing_labs, dict_mode=True, days_too_old=2)
            for lab in miss.keys():
                if miss[lab] == "Not found" or miss[lab] == "Too old" or miss[lab] == []:
                    lab = self.fn.display_name(lab)
                    self.plan['missing_labs'].append(lab)
        try:
            # If no home meds are caught we may error out here
            if self.assessment['home_meds'] != []:
                self.plan['meds_plan'] = self.fn.meds_list_plan(
                    self.assessment['home_meds'])
        except:
            pass

    def get_superseding_conditions(self):
        if "superseded_chronic_conditions" in self.assessment.keys():
            return self.assessment['superseded_chronic_conditions']
        return []
        

    def static_assessment(self):
        akeys = self.assessment.keys()
        ret_string = self.name + "\n"
        if 'other_assessment' in akeys:
            lines = [x.strip()
                     for x in self.assessment['other_assessment'].split(";;")]
            for line in lines:
                ret_string += line + "\n"

        if 'current_labs' in akeys:
            for lab_str in self.assessment['current_labs']:
                if lab_str != "":
                    ret_string += lab_str + "\n"

        if 'followup_labs' in akeys:
            for lab_str in self.assessment['followup_labs']:
                if lab_str != "":
                    ret_string += lab_str + "\n"

        if 'associated_conditions' in akeys and self.assessment['associated_conditions'] != []:
            ret_string += "Predisposing cond. of " + \
                self.fn.output_list(self.assessment['associated_conditions']) + "\n"
# make home_meds optional
        if 'home_meds' in akeys and self.display_home_meds:
            ret_string += "PTA meds: " + \
                self.fn.output_list(self.assessment['home_meds']) + "\n"
            
        if 'contraindicated' in akeys:
            ret_string += "Contraindicated: " + \
                self.fn.output_list(self.assessment['contraindicated']) + "\n"
        
        if 'cautioned' in akeys:
            ret_string += "Cautioned: "  + \
                self.fn.output_list(self.assessment['cautioned']) + '\n'

        return ret_string

    def static_plan(self):
        # NOTE: If dynamic portion of plan changes meds, that needs to be taken care of prior to adding the static plan
        pkeys = self.plan.keys()
        ret_string = "" # You can write plan in here 
        if 'missing_labs' in pkeys and self.plan['missing_labs'] != []:
            ret_string += "– Check " + \
                self.fn.output_list(self.plan['missing_labs']) + "\n"
        if 'meds_plan' in pkeys and self.full_meds_plan:
            ret_string += self.plan['meds_plan'] + "\n"
        if 'other_plan' in pkeys:
            other_plan = [x.strip()
                          for x in self.plan['other_plan'].split(",")]
            ret_string += "– " + "\n– ".join(other_plan) + "\n"

        return ret_string

    def __str__(self):
        ret_string = self.static_assessment() +  self.static_plan() 
        return ret_string

    def _load_labs(self, labs_string):
        # Regular expression to match words inside and outside parentheses

        pattern = r'\(([^)]*)\)|([^\s,]+)'
        colon_pattern = r'[^(:),]+:\s*'
        words_before_colons = []

        # Deal with lab group labelling
        for section in labs_string.split("),"):
            if ":" in section:
                # add to words_before_colons
                words_before_colons.append(
                    section.split(":")[0].strip().title())
            else:
                words_before_colons.append(None)

        # Remove the labelling from the string
        labs_string = re.sub(colon_pattern, "", labs_string)

        # Find all matches
        matches = re.findall(pattern, labs_string)

        # Process matches to separate into individual lists
        lists = []
        _other_l = []
        for match in matches:
            if match[0]:  # If the match is from the group inside parentheses
                # Split by comma and strip to remove any leading/trailing whitespaces
                lists.append([x.strip() for x in match[0].split(",")])
            else:  # If the match is from the group outside parentheses
                _other_l.append(match[1].strip())
        if _other_l != []:
            lists.append(_other_l)
        return (lists, words_before_colons)
    
    def get_extra_assessment_info(self):
        return list(set(self._extra_assessment_info))
