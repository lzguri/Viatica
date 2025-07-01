import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease

#NOTE: add into main program loop w/ superseded, CURRENT labs labelling (see acute HF in acute conditions). [missing labs not accurate]. [GFR not compared to despite being in that box in the csv.] [trailing comma on current labs], [names for missing labs], pioglitazone should be cautioned since its cautioned for CHF, [rstrip other plan and other assessment], [put hyphens in front of plan stuff], getting labs for dynamic stuff is messy so make a helper function for it, , [treat dfrow as dictionary], stuff like DKA you dont continue oral meds alot of the time, home glucose should be held unless it's glargine (make helper med functions for dynamic changes across several diseases.), chronic_disease dynamic for things liek DM

class Hyponatremia(disease.Disease):
    def __init__(self, name, MCI):

        # Get all the medical conditions that exist in the text
        self.fn = MCI
        self.diseases = self.fn.medical_conditions(chronic=False)
       
        if "Mild hyponatremia" in self.diseases:
            super().__init__("Mild hyponatremia", MCI=MCI)
        elif "Moderate hyponatremia" in self.diseases:
                super().__init__("Moderate hyponatremia", MCI=MCI)
        elif "Severe hyponatremia" in self.diseases:
                super().__init__("Severe hyponatremia", MCI=MCI)
        else:
            return ""
    

        
        # Corrected sodium level
        corrected_sodium = self.fn.sodium_disorder(corr_sod=True)
        
        # Add corrected sodium value to the self.asessment['current_labs]
        if corrected_sodium:
            self.assessment['current_labs'] = self.assessment['current_labs'] + [f'Corrected sodium is {round(corrected_sodium, 0)}']
                
        # Define chronic versus acute hyponatremia
        ''' documented hyponatremia of less than 48 hours is considered acute.'''



    def low_sodium_etiology(self):
        # get conditions causing volume overload
        overload = ['Acute heart failure', 'Liver cirrhosis', 'Nephrotic syndrome', 'Anasarca', 'Volume overload']

        # compare it with the conditions that the patient has
        overload_list = [i.lower() for i in overload if i in self.diseases]

        return overload_list


    
    def __str__(self):

        # Determine etiology of hyponatremia
        # Hypervolemic status
        overload_state = ['Acute heart failure', 'Liver cirrhosis', 'Nephrotic syndrome', 'Anasarca', 'Volume overload']

        overload_state_found = [disease for disease in overload_state if disease in self.diseases]

        if overload_state_found:
            self.name = self.name + f'\nLikely hypervolemic - {self.fn.format_list(overload_state_found)}'

        add_string = self.static_assessment()


        add_string += self.static_plan()


        return add_string
            
class Hypokalemia(disease.Disease):

    def __init__(self, name, MCI):

        self.fn = MCI
        self.diseases = self.fn.medical_conditions(chronic=False)

        if "Hypokalemia" in self.diseases:
            super().__init__("Hypokalemia", MCI=MCI, display_home_meds=True)

        
        internal_balance_causes = []
        external_balance_Causes = ["Acute diarrhea", "Vomiting"]


    def __str__(self):

        add_string = self.static_assessment()

        if "Hypomagnesemia" in self.diseases:
            add_string += "Low magnesium contributing to it"

        add_string+= self.static_plan().replace("Plan", "")

        return add_string


class Hyperkalemia(disease.Disease):


    def __init__(self, name, MCI):

        # Get the values for potassium, bicarbonate
        self.fn = MCI
        self.diseases = self.fn.medical_conditions(chronic=False)
        self.potassium = self.fn.lab_value("K")
        self.bicarb = self.fn.lab_value("CO2")
        self.name = name
       
        # Set the severity of hyperkalemia; Based on ACP
        if  "Mild hyperkalemia" in self.diseases:
            super().__init__("Mild hyperkalemia", MCI=MCI)
        elif "Moderate hyperkalemia":
            super().__init__("Moderate hyperkalemia", MCI=MCI)
        elif "Severe hyperkalemia":
            super().__init__("Severe hyperkalemia", MCI=MCI)
        else:
            super().__init__("Mild hyperkalemia", MCI=MCI)


    def __str__(self):

        other_plan = []

        if self.name == "Severe hyperkalemia":

            # Make associated an empty list if it's not there
            if 'associated_conditions' not in self.assessment.keys():
                self.assessment['associated_conditions'] = []

            # Add treatment recommendations for ESRD and DKA    
            if 'ESRD' in self.assessment['associated_conditions'] and 'DKA' not in self.assessment['associated_conditions']:
                other_plan += ["- Nephrology consult for dialysis"]


            if 'DKA' in self.assessment['associated_conditions']:
                other_plan += ["- IV Calcium", 
                               "\n- IV insulin for DKA", 
                               "\n- IV fluids", 
                               "\n- Recheck K levels"
                               ]

            if "DKA" not in self.assessment['associated_conditions'] and 'ESRD' not in self.assessment['associated_conditions']:
                other_plan += ["- Insulin + dextrose if glucose < 250", 
                               "\n- IV Calcium gluconate", 
                               "\n- Albuterol", 
                               "\n- Lokelma", 
                               "\n- Nephrology consult"
                               ]
            # Check digoxin level and avoid calcium gluconate as it can make digoxin [cardiac] toxicity worse  
            if "digoxin" in self.fn.find_medications('Antiarrhythmics, Oral', _list_only = True):
                other_plan += '\n' + '- Check digoxin level [Cautious with IV calcium ***]'
                
            # Add treatment recommendations for low bicarbonate      
            if self.bicarb < 17 and "DKA" not in self.assessment['associated_conditions']:
                other_plan += ["- Sodium bicarbonate"]

                ''' 
                rhabdomyolysis - pre-emptive treatment should be considered when creatinine kinase levels are rapidly rising and renal failure is present.

                Hyperkalemia which occurs with use of the aldosterone-receptor antagonist spironolactone can be prolonged owing to the very long half-life of its active metabolites. Measures implemented to reduce serum potassium values in such patients should be continued for 2 to 3 days after being started.
                
                '''

        elif self.name == "Hyperkalemia, moderate":
            other_plan = []


            
        add_string = [self.static_assessment()]

        add_string += [self.static_plan()]

        add_string.extend(other_plan)

        return ''.join([i for i in add_string if i])



class Hypercalcemia(disease.Disease):

    """THIS IS NOT COMPLETE"""

    def __init__(self, name, MCI):

        # Get all diseases found in the text    
        self.fn = MCI
        self.diseases = self.fn.medical_conditions()

        # Get severity of hypercalcemia
        if "Mild hypercalcemia" in self.diseases:
            super().__init__("Mild hypercalcemia", MCI=MCI)
        elif "Moderate hypercalcemia" in self.diseases:
            super().__init__("Moderate hypercalcemia", MCI=MCI)
        elif "Severe hypercalcemia" in self.diseases:
            super().__init__("Severe hypercalcemia", MCI=MCI)
        else:
            super().__init__("Hypercalcemia", MCI=MCI)




    def __str__(self):

        add_string = self.static_assessment()

        add_string = self.static_plan()

        add_string += self.fn.type_of_fluids()

        if "Severe hypercalcemia" in self.diseases:
            add_string += self.fn.start_new_medication("zoledronic acid")

        return add_string




class Hypocalcemia(disease.Disease):

    """THIS IS NOT COMPLETE"""

    def __init__(self, name, MCI):

        self.fn = MCI
        self.diseases = self.fn.medical_conditions(chronic=True) # Get all diseases list

        self.calcium = self.fn.lab_value('CA') # Calcium level
        self.albumin = self.fn.lab_value(('ALBUMIN')) # Albumin level
        self.magnesium = self.fn.lab_value('MG') # Magnesium level
        self.vitamin_d = self.fn.lab_value('VITAMINDTO') # Vitamin D level current or previous
        self.ionized_calcium = self.fn.lab_value("CAIONIZED") # Ionized calcium level
        '''NEED TO CREATE A FUNCTION THAT CHECKS IF THERE WAS A PREVIOUS VITAMIN D OR NOT'''
        self.prev_vit_D = self.fn.check_labs('VITAMINDTO', dict_mode=True, most_recent=True, days_too_old=30)

        # Initialize self.corrected_calcium variable
        self.corrected_calcium = None
        if self.calcium and self.albumin:
            self.corrected_calcium = self.fn.corrected_calcium(self.calcium, self.albumin)

   

        if self.ionized_calcium and self.ionized_calcium < 4.8:
            super().__init__('Hypocalcemia', MCI=MCI)
        elif self.corrected_calcium and self.corrected_calcium < 8.8:
            super().__init__('Hypocalcemia', MCI=MCI)
        elif 'hypocalcemia' in self.diseases:
            super().__init__('Hypocalcemia', MCI=MCI)
        else:
            print("No calcium detected")

        
        #if self.corrected_calcium:
            #self.assessment['current_labs'] = self.assessment['current_labs'] + [f"Corrected for albumin: {self.corrected_calcium} mg/dL"]

    def Vitamin_D_def(self):
        
        add_string = ''

        # Checks if vitamin D deficiency has already been diagnosed
        if "vitamnin d deficiency" in self.diseases:
            add_string += 'Patient has vitamin D deficiency'
            if self.vitamin_d:
                add_string += f', Vit. D is {self.vitamin_d}'

        # Check for drugs that cause vitamin D deficiency
        vitaminD_def_drugs = self.fn.find_medications_by_cautions('Vitamin D deficiency').replace("Cautioned:", '').strip()

        if vitaminD_def_drugs:
            add_string += f'Patient is on medications that cause vitamin D def.: {vitaminD_def_drugs.title()}' + '\n'
        
        # Get vitamin D levels and check if there is vitamin D deficiency
        if "vitamin d deficiency" in self.diseases:
            pass
        else:
            if self.vitamin_d and self.vitamin_d <= 20:
                add_string += f'Patient has Vit. D deficiency [{self.vitamin_d}]'

        return add_string
    

    def get_previous_labs(self, name, previous=True):

        name_dict = self.fn.check_labs(name, dict_mode=True, most_recent=True)

        if not name_dict[name]:
            return None
        



        return name_dict[name]

    
    def __str__(self):
        

        add_string = self.static_assessment()

        if 'associated_conditions' not in self.assessment.keys():
            self.assessment['associated_conditions'] = []

        # Hypomagnesemia can cause hypocalcemia which is usually resistant
        if self.magnesium and self.magnesium <= 1.6:
            add_string +=  f"Low MG [{self.magnesium}] contributing to hypocalcemia" + '\n'

        '''CONDITIONS OR DRUGS THAT CAUSE LOW VITAMIN D
        NEED ALSO TO CHECK LEVELS OF VITAMIN D PRIOR
        
        '''

        # Checks if vitamin D def is present, else will check Vitamin D levels before and make sure they are above 20, if patient is on any drugs that can cause vitamin D def. it will print the name

        if self.Vitamin_D_def():
            add_string += self.Vitamin_D_def()

        # Possible causes of hypocalcemia or exacerbating factors
        causes = ['chronic kidney disease', 'end-stage renal disease', 'acute pancreatitis', 'vitamin d deficiency', "hypoparathyroidism", 'hungry bone syndrome']
        causes_list = [i for i in causes if i in self.assessment['associated_conditions']]
        if causes_list:
            add_string += '\n' + f'Potential causes: {", ".join(causes_list)}'


        add_string += self.static_plan()

        # Checks for low magnesium and directs to replace it
        if self.magnesium and self.magnesium <= 1.6:
            add_string += '- Replace Mg'

        return add_string
    





class Nephrolithiasis(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Nephrolithiasis", MCI=MCI)

        self.fn = MCI

        self.all_diseases_abbrev = self.fn.PMH_abbreviations()

        self.prev_calcium = self.fn.check_labs('CA', dict_mode=True) # Get previous calcium levels

        self.prev_calcium_level = self.prev_calcium['CA'][1][0]



    def __str__(self):


        # Check if there is UTI or bacteriuria

        # Check calcium level, phosphate level

        add_string = self.static_assessment()


        add_string += self.static_plan()

        return add_string


class RenalTransplant(disease.Disease):


    pass
      


    """
    hypercalcemia can be classified according to severity (laboratory ranges may vary)2,3
mild hypercalcemia
defined as ionized calcium 5.6-8 mg/dL (1.4-2 mmol/L) or total calcium > 10.6-12 mg/dL (2.6-3 mmol/L)
usually asymptomatic
moderate hypercalcemia
defined as ionized calcium > 8-10 mg/dL (2-2.5 mmol/L) or total calcium > 12-14 mg/dL (3-3.5 mmol/L)
presentation may include fatigue, malaise, anorexia, impaired mental concentration, constipation, polyuria, and polydipsia
severe hypercalcemia (also known as hypercalcemic crisis)
defined as ionized calcium > 10 mg/dL (2.5 mmol/L) or total calcium > 14 mg/dL (3.5 mmol/L)
presentation may include symptoms of nausea, vomiting, dehydration, pancreatitis, peptic ulcers, arrhythmias, cardiac arrest, impaired mental capacity, stupor, or coma, in addition to the symptoms of moderate hypercalcemia
considered a life-threatening emergency requiring hospital admission for IV hydration and treatment
    
    
    """


class Hypomagnesemia(disease.Disease):

    """THIS IS NOT COMPLETE"""

    def __init__(self,name, MCI):

        self.fn = MCI
        self.disease = self.fn.medical_conditions()
        


        if "Hypomagnesemia" in self.disease:
            super().__init__('Hypomagnesemia', MCI=MCI)
        else:
            return None


    def __str__(self):


        # Conditions that can cause low magnesium
        # Alcohol use, diarrhea

        add_string = self.static_assessment()


        add_string += self.static_plan()



        return add_string



class AcuteKidneyInjury(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Acute kidney injury', MCI=MCI, display_home_meds=True)
        
        self.fn = MCI
        
        # Get all diseases
        self.diseases = self.fn.medical_conditions(acute=False)

        # Check if patient has chronic kidney injury
        if 'Chronic kidney disease' in self.diseases:
            self.name = "AKI on CKD"

        # Get todays creatinine level and previous level to compare it with
        self.creat_today = self.fn.lab_value('CREAT')

        self.creat_previos = self.fn.check_labs('CREAT', dict_mode=True)

        if len(self.creat_previos['CREAT']) > 1:
            self.previous_creat = float(self.creat_previos['CREAT'][-2][0])

        # Check bicarb level, check potassium level, BUN and pH 
        self.bicarb = self.fn.lab_value('CO2')

        self.potassium = self.fn.lab_value('K')

        self.pH = self.fn.lab_value('PHBLOODPOC')

        self.BUN = self.fn.lab_value('BUN')

        
        # Checks BUN/creat ratio if no CKD
        if self.creat_today and self.BUN:
            if self.BUN / self.creat_today >= 20:
                if 'Chronic kidney disease' not in self.diseases:
                    self.assessment['current_labs'] = self.assessment['current_labs'] + ['BUN/Creat > 20:1 suggestive of pre-renal AKI although patient has CKD']
                else:
                    self.assessment['current_labs'] = self.assessment['current_labs'] + ['BUN/Creat > 20:1 suggestive of pre-renal AKI']

        # Checks acid-base disorder
        if self.pH and self.bicarb:
            if self.pH < 7.3 or self.bicarb < 20:
                self.assessment['current_labs'] = self.assessment['current_labs'] + [f'Acidosis present pH {self.pH} and bicarb. {self.bicarb}']
                

    def __str__(self):

        # Check if patient has chronic kidney injury
        if 'Chronic kidney disease' in self.diseases:
            self.name = "AKI on CKD"

        # Pre-renal causes of AKI

        pre_renal = ['dehydration', 'acute gastroenteritis', 'acute diarrhea']

        # Renal causes of AKI

        renal = ['rhabdomyolysis', 'acute tubular necrosis', 'acute glomerulonephritis', 'allergic interstitial nephritis']

        # Post-renal causes of AKI

        post_renal = ['hydronephrosis', 'urinary retention']

        add_string = self.static_assessment()

        self.name = "Liridon"

        
        add_string += self.static_plan()

        # Conditions that exclude the need for bicarbonate drip: DKA

        if self.bicarb and self.bicarb < 18:
            if self.pH and self.pH <= 7.35:
                add_string += f'- Start bicarb drip, pH {self.pH}, and bicarb {self.bicarb}'
            elif not self.pH:
                add_string += '- Check pH to assess for bicarb drip need ***'

        add_string += self.fn.type_of_fluids()
    
    # KDIGO criteria for renal failure

        return add_string


class Hyperkalemia2():

    def __init__(self, name, MCI):
        super().__init__('Hyperkalemia', MCI=MCI, display_home_meds=True)

        pass



# Example usage
# result = hypokalemia_severity(your_instance)
# print(result)


text_input = """


 is a 66 y.o. male

Complete blood count
acute heart failure
Lab Results
Component	Value	Date/Time
	WBC	9.5	04/18/2024 05:38 AM
	RBC	3.61 (L)	04/18/2024 05:38 AM
	HGB	10.1 (L)	04/18/2024 05:38 AM
	HGB	12.3 (L)	04/03/2024 10:13 AM
	HCT	32.5 (L)	04/18/2024 05:38 AM
	MCV	90.0	04/18/2024 05:38 AM
	MCH	28.0	04/18/2024 05:38 AM
	MCHC	31.1	04/18/2024 05:38 AM
	PLT	114 (L)	04/18/2024 05:38 AM
	PLT	115 (L)	04/03/2024 10:13 AM
	RDW	15.9 (H)	04/18/2024 05:38 AM
	NEUTROPHIL	6.19	04/18/2024 05:38 AM
	LYMPHOCYTE	1.61	04/18/2024 05:38 AM
	EOSINOPHIL	0.08	04/18/2024 05:38 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	115 (L)	04/18/2024 05:38 AM
	K	3.4 (L)	04/18/2024 05:38 AM
	CL	98	04/18/2024 05:38 AM
	CO2	22	04/18/2024 05:38 AM
	CA	8.3 (L)	04/18/2024 05:38 AM
	CA	8.7 (L)	04/03/2024 09:43 AM
	BUN	57 (H)	04/18/2024 05:38 AM
	CREAT	3.99 (H)	04/18/2024 05:38 AM
	GFR	16 (L)	04/18/2024 05:38 AM
	GFR	18 (L)	04/03/2024 09:43 AM
	GLUCOSE	350 (H)	04/18/2024 05:38 AM
	TOTALPROTEIN	6.8	04/03/2024 09:43 AM
	ALBUMIN	3.1 (L)	04/18/2024 05:38 AM
	BILITOTAL	1.0	04/03/2024 09:43 AM
	LIPASE	51	01/06/2020 02:53 PM
	AMYLASE	54	01/06/2020 02:53 PM
	AMMONIA	15.9 (L)	04/04/2022 09:53 AM
	URICACID	6.2	04/12/2021 09:00 AM
	URICACID	10.0 (H)	07/31/2020 01:49 PM
	ALKPHOS	102	04/03/2024 09:43 AM
	ALKPHOS	92	04/02/2024 12:51 PM
	AST	19	04/03/2024 09:43 AM
	ALT	13	04/03/2024 09:43 AM
	ANIONGAP	14	04/18/2024 05:38 AM
	MG	1.7	08/10/2023 12:01 PM
	MG	2.2	12/31/2021 03:11 AM
	PO4	3.0	04/18/2024 05:38 AM
	LACTATE	1.9	04/03/2024 11:23 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	122 (HH)	12/08/2023 12:18 PM
	BASETROP	113 (HH)	08/10/2023 12:01 PM
	2HRTROP	115 (HH)	12/08/2023 02:39 PM
	2HRTROP	107 (HH)	08/10/2023 02:53 PM
	DELTA	-3	12/28/2021 04:12 AM
	DELTA	-1	12/27/2021 11:08 PM
	6HRTROP	110 (HH)	12/08/2023 06:26 PM
	6HRTROP	97 (H)	08/10/2023 07:49 PM
	PROBNPNTERMI	28,240 (H)	04/02/2024 12:51 PM
	PROBNPNTERMI	6,438 (H)	12/08/2023 12:18 PM
	DDIMERQUANT	0.75 (H)	12/14/2021 05:54 PM
	INR	1.1	12/09/2023 06:02 PM
	PT	14.3	12/09/2023 06:02 PM
	APTT	28.9	12/12/2023 07:17 AM


workup
Lab Results
Component	Value	Date/Time
	IRON	42 (L)	01/07/2022 04:27 AM
	IRON	85	08/10/2020 09:45 AM
	TIBC	178 (L)	01/07/2022 04:27 AM
	TIBC	243 (L)	08/10/2020 09:45 AM
	IRONPERCENT	24	01/07/2022 04:27 AM
	IRONPERCENT	35	08/10/2020 09:45 AM
	FERRITIN	392.8	01/07/2022 04:27 AM
	FERRITIN	101.7	11/08/2019 10:15 AM
	VITAMINB12	309	02/09/2018 09:09 AM
	VITAMINB12	173 (L)	08/31/2017 06:10 AM
	FOLATE	5.6	08/31/2017 06:10 AM


Lab Results
Component	Value	Date/Time
	PHUA	7.0	04/04/2022 11:53 AM
	SGUR	1.011	04/04/2022 11:53 AM
	URINELEUKOC	Negative	04/04/2022 11:53 AM
	NITRITEUA	Negative	04/04/2022 11:53 AM
	KETONEURINE	Negative	04/04/2022 11:53 AM
	PROTEINUA	1+ (A)	04/04/2022 11:53 AM
	GLUUA	Negative	04/04/2022 11:53 AM
	BLOODUA	Negative	04/04/2022 11:53 AM
	WBCU	0-2	04/04/2022 11:53 AM
	RBCUA	0-2	04/04/2022 11:53 AM
	BACTERIAUA	1+ (A)	04/04/2022 11:53 AM
	UREPITHELIAL	0-5	12/30/2021 03:16 PM


Lab Results
Component	Value	Date/Time
	CRP	162.7 (H)	04/02/2024 05:14 PM


Lab Results
Component	Value	Date/Time
	PHBLOODPOC	7.43	08/10/2023 12:45 PM
	PCO2POC	27 (L)	08/10/2023 12:45 PM
	PO2POC	94	08/10/2023 12:45 PM
	PFRATIO	367	04/04/2022 01:48 PM
	O2SATPOC	100 (H)	08/10/2023 12:45 PM


Lab Results
Component	Value	Date/Time
	INFLUENZAA	Not Detected	10/27/2023 12:10 AM
	INFLUENZAB	Not Detected	10/27/2023 12:10 AM
	COVID19	Not Detected	04/02/2024 05:36 PM
	RSVAG	Not Detected	10/27/2023 12:10 AM


Lab Results
Component	Value	Date/Time
	HGBA1C	5.8 (H)	08/10/2023 11:43 AM
	LDLCALC	50	08/24/2023 10:58 AM


Lab Results
Component	Value	Date/Time
	TRIGLYCERIDE	107	08/24/2023 10:58 AM
	TSH	1.60	04/04/2022 09:53 AM


No results found for: "AMPHETAMINEQ", "BARBITQLUR", "BENZDIAQLUR", "CANNABQLUR", "COCAINEQUAL", "METHADONEU", "OPIATEQUA", "OXYCODQLUR", "PHENCYCLID"

Toxicology
Lab Results
Component	Value	Date/Time
	ETHANOL	<10.10	04/04/2022 09:53 AM
	ETHANOL	<0.01	04/04/2022 09:53 AM


Vitamins
Lab Results
Component	Value	Date/Time
	VITAMINDTO	25 (L)	02/05/2021 09:05 AM


Tumor markers
No results found for: "AFPTM"

Virology
Lab Results
Component	Value	Date/Time
	HEPAIGM	Non-reactive	01/01/2022 06:12 PM
	HEPBCORIGM	Non-reactive	01/01/2022 06:12 PM
	HEPBSAG	Non-reactive	01/01/2022 06:12 PM
	HEPCAB	Non-reactive	01/01/2022 06:12 PM
 


GIPATHOGEN
No results found for: "CLOSTRIDIU"




Principal Problem:
  Fever
Active Problems:
  Chronic anticoagulation
  Essential hypertension
  OSA on CPAP
  ESRD (end stage renal disease) on dialysis
  Type 2 diabetes mellitus with chronic kidney disease on chronic dialysis, with long-term current use of insulin
  Dyslipidemia associated with type 2 diabetes mellitus
  Chronic heart failure with preserved ejection fraction
  Major depressive disorder with single episode, in partial remission
  Longstanding persistent atrial fibrillation
  Right atrial thrombus
  Dependence on renal dialysis
  Rigors
  Line sepsis associated with dialysis catheter
 


Vitals:
	04/04/24 1900
BP:	127/79
Pulse:	91
Resp:	20
Temp:	
SpO2:	97%



Prior to Admission Medications
Prescriptions	Last Dose	Informant	Patient Reported?	Taking?
Blood-Glucose Meter,Continuous (Dexcom G4 Receiver-Share Kit)			No	No
Sig: Use as directed to monitor blood sugar
Blood-Glucose Sensor (Dexcom G6 Sensor) Device			No	No
Sig: Use as directed to monitor blood sugars
Blood-Glucose Transmitter (Dexcom G6 Transmitter) Device			No	No
Sig: Use as directed to monitor blood sugars
FLUoxetine (PROzac) 40 mg capsule	3/31/2024		No	No
Sig: Take 1 Capsule (40 mg) by mouth daily.
Insulin Needles, Disposable, (UltiCare Pen Needle) 31 gauge x 3/16" Needle			No	No
Sig: USE AS DIRECTED DAILY FOR INSULIN INJECTION. MAX DAILY AMOUNT 4
Lantus Solostar U-100 Insulin 100 unit/mL (3 mL) solution for injection	3/31/2024		No	No
Sig: Inject 20 Units by subcutaneous injection late in the day. Max Daily amount 60 units
RenaPlex-D 800 mcg-12.5 mg -2,000 unit Tablet			Yes	No
Sig: Take 1 Tablet by mouth daily.
allopurinoL (ZYLOPRIM) 100 mg tablet	3/31/2024		No	No
Sig: TAKE 1 TABLET BY MOUTH EVERY DAY
apixaban (Eliquis) 5 mg tablet	3/31/2024		No	Yes
Sig: TAKE 1 TABLET BY MOUTH TWICE DAILY
bumetanide (BUMEX) 2 mg tablet	3/31/2024		No	No
Sig: TAKE 2 TABLETS BY MOUTH EVERY MORNING and TAKE 1 TABLET EVERY
cpap medical device			No	No
Sig: CPAP (E0601) at 12 cm/H2O with heated humidifier (E0562), nasal pillow/cradle and headgear A7034,A7035 1/6mo, Mask only A7034 1/3mo, Pillows A7033 2/mo.  Also supply heated tubing A4604 1/3mo,water chamber A7046 1/6mo,filter disp A7038 2/mo,Reusable filter A7039 1/6mo, Chin strap A7036 a/6mo LON 99mo DX: OSA (G47.33)
fluticasone propionate (FLONASE) 50 mcg/spray Spray, Suspension nasal inhaler			No	No
Sig: Administer 2 Sprays in each nostril daily.
gabapentin (NEURONTIN) 300 mg capsule	3/31/2024		No	No
Sig: TAKE 1 CAPSULE BY MOUTH EVERY NIGHT AT BEDTIME AS DIRECTED
metoprolol tartrate (LOPRESSOR) 25 mg tablet	4/1/2024		No	Yes
Sig: take 1 tablet by mouth twice daily
mirtazapine (REMERON) 15 mg tablet	3/31/2024		No	No
Sig: Take 1 Tablet (15 mg) by mouth daily at bedtime.
naratriptan (AMERGE) 2.5 mg tablet			No	No
Sig: TAKE 1 TABLET BY MOUTH DAILY AS NEEDED FOR MIGRAINE
ondansetron (ZOFRAN) 4 mg Tablet			Yes	No
Sig: Take 4 mg by mouth every 6 hours as needed.
sevelamer carbonate (RENVELA) 800 mg Tablet	4/1/2024		Yes	Yes
Sig: Take 800 mg by mouth daily.
simvastatin (ZOCOR) 40 mg tablet	3/31/2024		No	No
Sig: Take 1 Tablet (40 mg) by mouth daily at bedtime.
tiZANidine (ZANAFLEX) 2 mg Tablet			No	No
Sig: Take 1 Tablet (2 mg) by mouth every 6 hours as needed for Spasm.

Facility-Administered Medications: None


Current Facility-Administered Medications
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	[COMPLETED] vancomycin (VANCOCIN) 500 mg in sodium chloride 0.9% 100 mL IVPB (MBP)	 500 mg	IV	ONE time only	Haddow, Alastair D, MD	 	Stopped at 04/04/24 1529
•	tiZANidine (ZANAFLEX) tablet 2 mg	 2 mg	Oral	ONE time only	Corum, Laura Michelle, FNP	 	 
•	heparin injection 7,500 Units	 7,500 Units	subCUT	every 8 hours	Virji, Narius Aresh, MD	 	7,500 Units at 04/04/24 1426
•	[COMPLETED] tiZANidine (ZANAFLEX) tablet 2 mg	 2 mg	Oral	ONE time only	Corum, Laura Michelle, FNP	 	2 mg at 04/03/24 2332
•	[Held by Provider] apixaban (ELIQUIS) tablet 5 mg	 5 mg	Oral	BID	Zguri, Liridon, MD	 	 
•	FLUoxetine (PROzac) capsule 40 mg	 40 mg	Oral	daily	Zguri, Liridon, MD	 	40 mg at 04/04/24 1100
•	gabapentin (NEURONTIN) capsule 300 mg	 300 mg	Oral	daily BEDTIME	Zguri, Liridon, MD	 	300 mg at 04/04/24 2111
•	simvastatin (ZOCOR) tablet 40 mg	 40 mg	Oral	daily BEDTIME	Zguri, Liridon, MD	 	40 mg at 04/04/24 2113
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	acetaminophen (TYLENOL) tablet 650 mg	 650 mg	Oral	every 6 hours PRN	Zguri, Liridon, MD	 	 
•	VANCOMYCIN CONSULT TO PHARMACY	 	See Admin Instructions	see admin instructions	Zguri, Liridon, MD	 	 
•	metoprolol tartrate (LOPRESSOR) tablet 25 mg	 25 mg	Oral	BID	Zguri, Liridon, MD	 	25 mg at 04/04/24 2111
•	diltiaZEM in 0.9% sodium chloride (CARDIZEM) 125 mg/125 mL infusion	 0-15 mg/hr	IV	titrate	Zguri, Liridon, MD	5 mL/hr at 04/03/24 1805	5 mg/hr at 04/03/24 1805
•	allopurinoL (ZYLOPRIM) tablet 100 mg	 100 mg	Oral	daily	Zguri, Liridon, MD	 	100 mg at 04/04/24 1100
•	dextrose 5% - sodium chloride 0.9% infusion	 	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	glucagon HCL 1 mg/mL injection 1 mg	 1 mg	IM	see admin instructions	Zguri, Liridon, MD	 	 
•	insulin glargine-yfgn injection 10 Units	 10 Units	subCUT	daily BEDTIME	Zguri, Liridon, MD	 	10 Units at 04/04/24 2111
•	insulin lispro (HumaLOG) injection 0-6 Units	 0-6 Units	subCUT	TID WITH meals	Zguri, Liridon, MD	 	2 Units at 04/04/24 1732
•	insulin lispro (HumaLOG) injection 0-3 Units	 0-3 Units	subCUT	daily BEDTIME	Zguri, Liridon, MD	 	 
•	insulin lispro (HumaLOG) injection 0-3 Units	 0-3 Units	subCUT	daily at 0200	Zguri, Liridon, MD	 	 
•	dextrose 10% bolus solution 125 mL	 125 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	dextrose 10% bolus solution 250 mL	 250 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	cefePIME (MAXIPIME) 1,000 mg in sodium chloride 0.9% 50 mL IVPB (MBP)	 1,000 mg	IV	every 24 hours	Zguri, Liridon, MD	 	Stopped at 04/04/24 1801


"""


# master = functions.MasterClass(file_contents=text_input)

# #print(Hyponatremia('Hyponatremia', MCI=master))