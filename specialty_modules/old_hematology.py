import functions
import disease_database as disb
import drug_reference as drugs
import disease_reference as disr
import workup_reference as wr
import pandas as pd
import datetime




class Hematology(functions.MasterClass):

    """
    'Anemia' : {
                'name':disr.Hematology['Anemia'],
                'test': ['HGB', 'RBC'],
                'previous test' :['IRON', 'TIBC', 'IRONPERCENT', 'FERRITIN', 'VITAMINB12', 'FOLATE'], 
                'medications': ['Vitamin K Antagonists', 'NOACs' ]
}
    """

    def __init__ (self, file_contents):
        super().__init__(file_contents)
        #Is anemia in problems?
        self.anemia_positive = bool(self.check_name(['anemia'])) or bool(self.abnormality_name('HGB'))
        #Tests
        self._labs = self.check_labs(["HGB", "RBC", 'IRON', 'TIBC', 'IRONPERCENT', 'FERRITIN', 'VITAMINB12', 'FOLATE'], dict_mode = True)
        self.all_HGB, self.all_RBC = self._labs["HGB"], self._labs["RBC"]
        #Meds
        self.anticoagulants = ['Vitamin K Antagonists']
        self.antiplatelets = ['P2Y12 Inhibitors']
        #Hx
        self.anemia_risk_factors = ['B12 Deficiency', 'Iron Deficiency Anemia', "Chronic myelogenous leukemia", "Chronic lymphocytic anemia" ]
        self.problem_list = self.get_medical_history(history_list_only = True)
        #today's date
        self.now = datetime.datetime.now()

"""
class Anemia(Hematology, functions.MasterClass):
    def __init__ (self, file_contents):
        super().__init__(file_contents)

    def Anemia_AP(self):
        if not self.anemia_positive:
            return ""

        output_text = "ANEMIA"

        #Print hgb if from today or yesterday, otherwise say to check it
        if len(self.all_HGB) == 0:
            output_text += '\nCheck HGB'
        elif len(self.all_HGB) == 1:
            #Check if the one HGB is from past two days or is old
            latest_HGB_date = datetime.datetime.strptime(self.all_HGB[0][1], '%m/%d/%Y')
            if (self.now - latest_HGB_date).days <= 2:
                #hgb is current
                output_text += "\nCurrent HGB is " + self.all_HGB[0][0] + " " + wr.HGB["unit"] + " [No old HGB to compare with]."
            else:
                #hgb is old
                output_text += '\nLast HGB is ' + self.all_HGB[0][0] + " " + wr.HGB["unit"] + " as of " + self.all_HGB[0][1]
        else:
            #we have multiple
            latest_HGB_date = datetime.datetime.strptime(self.all_HGB[0][1], '%m/%d/%Y')
            if (self.now - latest_HGB_date).days <= 2:
                #hgb is current
                output_text += "\nCurrent HGB is " + self.all_HGB[0][0] + " " + wr.HGB["unit"] + " [HGB on " + self.all_HGB[1][1] + " " + wr.HGB["unit"] +" was " + self.all_HGB[1][0] + "]. "
            else:
                #hgb is old
                output_text += '\nLast HGB is ' + self.all_HGB[0][0] + " " + wr.HGB["unit"] + " as of " + self.all_HGB[0][1]

        #Check previous tests 
        output_text += "\n" + self.group_old_labs(['IRON', 'TIBC', 'IRONPERCENT', 'FERRITIN', 'VITAMINB12', 'FOLATE'])
        
        #Check risk factors
        positive_risk_factors = []
        for disease in self.problem_list:
            #Ignores synonyms, will be dealt with using library later probably TODO
            if disease in self.anemia_risk_factors:
                positive_risk_factors.append(disease)
        if len(positive_risk_factors) >=1 :
            output_text += "\nRisk factors: " + ", ".join(positive_risk_factors) + ". "

        #Home meds
        
        hold = self.find_medication(self.anticoagulants + self.antiplatelets, dictionary=False, only_meds_list=True)
        if hold:
            output_text += "\nThe patient is on " + ".".join(hold) + "***. "
        
        #PLAN
        output_text += "\nPLAN"

        output_text += "\n- " + self.check_missing_labs(['IRON', 'TIBC', 'IRONPERCENT', 'FERRITIN', 'VITAMINB12', 'FOLATE'])


        return output_text
    """

class Anemia2(Hematology, functions.MasterClass):
    def __init__ (self, file_contents):
        super().__init__(file_contents)

    def Anemia_AP(self):
        total_output = ""
        if not bool(self.check_name('anemia')) or not self.abnormality_name('HGB'):
            #no anemia detected
            return ""
        
        #classify type of anemia
        cell_size = self.abnormality_name('MCV')
        cell_size = cell_size.title() if cell_size != None else "Normocytic"

        cell_color = self.abnormality_name('MCH')
        cell_color = cell_color if cell_color != None else "normochromic"

        total_output += cell_size + " " + cell_color + " " + "anemia"
        #TODO: output should look nicer, use synonyms, 'and', add units, etc. 
        #print hgb info
        total_output += "\n" + self.labs_with_old("HGB")

        #print old workup
        total_output += "\n" + self.group_old_labs(['IRON', 'TIBC', 'IRONPERCENT', 'FERRITIN', 'VITAMINB12', 'FOLATE'])

        #meds to alter
        total_output += "\n" + self.plan_for_condition("anemia")
        return total_output

# HEMOLYSIS LABS: 

class CobalamineDeficiency:


# synonyms: Vitamin B12 deficiency, Megaloblastic anemia, Cobalamine deficiency
# etiology: malabsorption, pernicious anemia [autoimmune gastritis], IBD [affects terminal ileum], pancreatic insufficiency, bacterial overgrowth

# Complications: Dementia, neuropsychiatric symptoms


# LABS: vitamin B12, homocysteine, methylmalonic acid [when vitamin B12 < 300]
# GENERAL ANEMIA LABS: hemoglobin, MCV [macrocytic anemia], sometimes pancytopenia
# LABS [ineffective erythropoesis], haptoglobin, bilirubin, LDH
    pass