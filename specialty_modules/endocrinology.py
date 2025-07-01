import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import disease
import functions


class DiabeticKetoacidosis(disease.Disease):

    def __init__(self, name, MCI):
        #initialize from dataframe instead of parameters 
        import functions
        super().__init__("Diabetic ketoacidosis", MCI=MCI)

        self.fn = MCI
    
    def __str__(self):
    
        
        
		#hold home meds
        ret_string = self.static_assessment() + "\n" + self.static_plan()

        #dynamic plan
        dynamic_labs = self.fn.check_labs(["PHBLOODPOC", "K", "GLUCOSE"], dict_mode=True, days_too_old=2)
        try:
            if float(dynamic_labs["PHBLOODPOC"][0][0]) < 6.9:
                ret_string += "– Start bicarb drip [might worsen hypokalemia]\n"
        except:
            pass
        try:
            if float(dynamic_labs["K"][0][0]) < 3.4:
                ret_string += "– Hold Insulin, K needs to be replaced first [K is " + dynamic_labs["K"][0][0] + "]\n"
        except:
            pass
        try:
            if float(dynamic_labs["K"][0][0]) > 3.3 and float(dynamic_labs["K"][0][0]) < 5.3:
                ret_string += "– IV fluids supplemented with K [20–30 mEq/L] [K is " + dynamic_labs["K"][0][0] + "]\n"
        except:
            pass
        try:
            if float(dynamic_labs["GLUCOSE"][0][0]) < 250:
                ret_string += "– Start Dextrose supplementation [D5W]\n"
        except:
            pass
        try:
            if float(dynamic_labs["GLUCOSE"][0][0]) > 200 and float(dynamic_labs["GLUCOSE"][0][0]) < 250:
                ret_string += "– Add D5W to IV fluids\n"
        except:
            pass
        try:
                if float(dynamic_labs["GLUCOSE"][0][0]) > 250:
                    ret_string += "– When serum glucose is 200–250 add D5W to IV fluids.\n"
        except:
                pass

    
        return ret_string
    
"""
class Hyponatremia(disease.Disease, functions.MasterClass):

	def _init__(self, name, MCI):
		super().__init__(self, "Hyponatremia", MCI)


	def hyponatremia(self):
		sodium_level = self.check_labs(['NA'], dict_mode=True, days_too_old=2)
	#	sodium_level = sodium_level['NA'][0][0]
		if sodium_level:
			return sodium_level
		else:
			return "Nothing found here"
"""




class DiabetesMellitus(disease.Disease, functions.MasterClass):

    def __init__(self, name, MCI):
        super().__init__("Diabetes mellitus", MCI=MCI)




    def __str__(self):

        add_string = self.static_assessment()
        
        Glucose = self.lab_value('GLUCOSE')
        Anion_gap = self.lab_value('ANIONGAP')
        Bicarb = self.lab_value("CO2")

        if Glucose is not None and Glucose > 250:
            add_string += "\n" + "Glucose elevated {Glucose}"
        if Anion_gap is not None and Bicarb is not None:
            if Anion_gap > 15 and Bicarb < 18:
                add_string += "\n" + f"High anion gap metabolic acidosis: AG {Anion_gap}, and Bicarb {Bicarb}"


        home_meds = self.find_medications_by_indication("Diabetes mellitus")

        add_string += home_meds


        return add_string
    
    

class DM(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Diabetes mellitus", MCI=MCI)
        
        self.fn = MCI

        self.home_meds = self.fn.find_medications_by_indication('Diabetes mellitus', only_meds_list=True)  # Retrieves all the diabetic medications including insulin


        # Remove insulin lispro from the self.home_meds
        if self.home_meds is not None and 'insulin lispro' in self.home_meds:
            self.home_meds.remove('insulin lispro')

        
    
    def __str__(self):
        add_string = self.static_assessment()
        
        Glucose = self.fn.lab_value('GLUCOSE')
        Anion_gap = self.fn.lab_value('ANIONGAP')
        Bicarb = self.fn.lab_value("CO2")

        if Glucose is not None and Glucose > 250:
            add_string += "\n" + f"Glucose today {Glucose}\n"
        if Anion_gap is not None and Bicarb is not None:
            if Anion_gap > 15 and Bicarb < 18:
                add_string += f"High anion gap metabolic acidosis: AG {Anion_gap}, and Bicarb {Bicarb}"

        #add_string +=  'Plan'

        

        
        extended_string = '\n' + '– Add sliding scale insulin regimen\n' + '– Monitor glucose per protocol\n'

        # Handle insulin glargine presence efficiently with set difference
        home_meds_without_glargine = set(self.home_meds) - {'insulin glargine'} -{'insulin lispro'}

        if 'insulin glargine' in self.home_meds:
            extended_string = "– Cont with insulin glargine" + extended_string
            if home_meds_without_glargine:
                extended_string = extended_string + '– Hold: ' + ', '.join(home_meds_without_glargine)
        else:
        # Add recommendation to start insulin glargine if not already present
            extended_string = '– Start insulin glargine' + extended_string

        
        return add_string + extended_string
    

class AdrenalCrisis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Adrenal crisis', MCI=MCI)

        self.fn = MCI

        # Get sodium and glucose levels
        self.glucose = self.fn.lab_value("GLUCOSE")
        self.sodium = self.fn.lab_value('NA')
        self.TSH = self.fn.lab_value('TSH')
        self.prev_TSH = self.fn.check_labs('TSH', dict_mode=True, days_too_old=60)

        # Get vitals, BP and HR
        self.BP = self.fn.get_single_vital('BP')
        self.HR = self.fn.get_single_vital('Pulse')

        # Get all diseases
        self.chronic_conditions = self.fn.PMH_abbreviations()

        # Get latest TSH, if more than a month ago, check another level
        self.assessment['other_assessment'] = self.assessment['other_assessment'] # + '\n' + self.prev_TSH['TSH'][0]

        # Get hemodynamics
        self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + f"Hemodynamics: BP {self.BP} mmHg and HR {self.HR} bpm" 


    
    def __str__(self):

        add_string = self.static_assessment()

        # Association with other autoimmune disease

        # Precipitation events: surgery, infection, trauma

        # Low sodium, high potassium, low glucose, n TSH

        # In case of hypotension, check morning cortisol 8 a.m and 9 a.m A; level below 5 micrograms/dL is suggestive of adrenal insufficiency

        add_string += self.static_plan()

        # Monitor glucose if hypoglycemic, care should be taken to avoid worsening hyponatremia

        if self.glucose and self.glucose < 80:
            if self.sodium and self.sodium < 135:
                add_string += "– Start D5NS IV [monitor for hyponatremia closely ***]"
        else: 
            add_string += "– Start D5NS IV"

        # If patient is diabetic, insulin might need to be lowered

        if 'DM' in self.chronic_conditions and self.glucose < 200:
            add_string += '\n' + '– DM: Patient will require less insulin ***'


        '''CHECK IF TSH IS CHECK RECENTLY, IF NOT CHECK A NEW ONE'''



        return add_string


'''

Cushing syndrome; any etiology of excess steroids
Exogenous
– most common cause is iatrogenic
Endogenaous
– ACTH dependent; Pituitary


'''




Text_input = '''
 
Acute heart failure
Coronary artery disease
Chronic kidney disease
Anemia
Gastroesophageal reflux disease
Hyperlipidemia
Aortic regurgitation
Mitral regurgitation
Diabetes mellitus


Alogliptin
Amlodipine
Aspirin
Clopidogrel
Ferrous sulfate
Furosemide
Glipizide
Insulin aspart
Insulin detemir
Isosorbide mononitrate
Lisinopril
Metformin
Metoprolol
Rosuvastatin


 is a 84 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	10.7	03/03/2024 08:00 AM
	RBC	3.62 (L)	03/03/2024 08:00 AM
	HGB	11.1 (L)	03/03/2024 08:00 AM
	HGB	10.8 (L)	03/02/2024 10:30 AM
	HCT	34.8 (L)	03/03/2024 08:00 AM
	MCV	96.1	03/03/2024 08:00 AM
	MCH	30.7	03/03/2024 08:00 AM
	MCHC	31.9	03/03/2024 08:00 AM
	PLT	267	03/03/2024 08:00 AM
	PLT	264	03/02/2024 10:30 AM
	RDW	13.0	03/03/2024 08:00 AM
	NEUTROPHIL	7.40	03/03/2024 08:00 AM
	LYMPHOCYTE	1.94	03/03/2024 08:00 AM
	EOSINOPHIL	0.16	03/03/2024 08:00 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	143	03/03/2024 08:00 AM
	K	4.3	03/03/2024 08:00 AM
	CL	107	03/03/2024 08:00 AM
	CO2	23	03/03/2024 08:00 AM
	CA	9.6	03/03/2024 08:00 AM
	CA	9.2	03/02/2024 10:30 AM
	BUN	36 (H)	03/03/2024 08:00 AM
	CREAT	1.78 (H)	03/03/2024 08:00 AM
	GFR	37	03/03/2024 08:00 AM
	GFR	34	03/02/2024 10:30 AM
	GLUCOSE	306 (H)	03/03/2024 08:00 AM
	TOTALPROTEIN	7.1	03/03/2024 08:00 AM
	ALBUMIN	3.9	03/03/2024 08:00 AM
	BILITOTAL	0.4	03/03/2024 08:00 AM
	ALKPHOS	107	03/03/2024 08:00 AM
	ALKPHOS	113	03/02/2024 10:30 AM
	AST	14	03/03/2024 08:00 AM
	ALT	13	03/03/2024 08:00 AM
	ANIONGAP	13	03/03/2024 08:00 AM
	LACTATE	1.8	03/03/2024 08:01 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	34 (H)	03/03/2024 08:00 AM
	BASETROP	31 (H)	03/02/2024 10:30 AM
	2HRTROP	28 (H)	03/02/2024 12:45 PM
	DELTA	-3	03/02/2024 12:45 PM
	PROBNPNTERMI	6,327 (H)	03/03/2024 08:00 AM
	PROBNPNTERMI	4,126 (H)	03/02/2024 10:30 AM


workup
No results found for: "IRON", "TIBC", "IRONPERCENT", "FERRITIN", "HAPTOGLOBIN", "LD", "VITAMINB12", "FOLATE"

Lab Results
Component	Value	Date/Time
	PHUA	6.0	03/02/2024 11:00 AM
	SGUR	1.020	03/02/2024 11:00 AM
	URINELEUKOC	Negative	03/02/2024 11:00 AM
	NITRITEUA	Negative	03/02/2024 11:00 AM
	KETONEURINE	Negative	03/02/2024 11:00 AM
	PROTEINUA	2+ (A)	03/02/2024 11:00 AM
	GLUUA	Negative	03/02/2024 11:00 AM
	BLOODUA	Trace (A)	03/02/2024 11:00 AM
	WBCU	0-2	03/02/2024 11:00 AM
	RBCUA	0-2	03/02/2024 11:00 AM
	BACTERIAUA	Negative	03/02/2024 11:00 AM


Lab Results
Component	Value	Date/Time
	CRP	4.7	03/02/2024 10:30 AM


No results found for: "PHBLOODPOC", "PCO2POC", "PO2POC", "PFRATIO", "O2SATPOC"

Lab Results
Component	Value	Date/Time
	INFLUENZAA	Not Detected	03/02/2024 10:48 AM
	INFLUENZAB	Not Detected	03/02/2024 10:48 AM
	COVID19	Not Detected	03/02/2024 10:48 AM
	RSVAG	Not Detected	03/02/2024 10:48 AM


No results found for: "HGBA1C", "LDLCALC", "HEPINDPLTAB"

No results found for: "TRIGLYCERIDE", "TSH"

Toxicology
No results found for: "ETHANOL", "ACETAMINOPHE", "SALICYLATE"

Vitamins
No results found for: "VITAMINDTO"

Tumor markers
No results found for: "AFPTM"

Virology
No results found for: "CD4", "HIV1RNACOPIE", "HEPAIGM", "HEPBCORIGM", "HEPBSAG", "HEPCAB" 


GIPATHOGEN
No results found for: "CLOSTRIDIU"



 


Vitals:
	03/03/24 0820
BP:	(!) 160/89
Pulse:	86
Resp:	24
Temp:	98.7 °F (37.1 °C)
SpO2:	94%





aortic stenosis
'''

