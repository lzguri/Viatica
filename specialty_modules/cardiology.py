import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease


"""
LIST OF CONDITIONS

Coronary artery disease - chronic
NSTEMI, Unstable angina, STEMI - acute
Chest pain rule out ACS - acute
Chronic congestive heart failure - chronic
Acute heart failure - acute
Atrial fibrillation, Atrial flutter - chronic
Atrial fibrillation with RVR, Atrial flutter with RVR
Myocarditis - acute
Acute pericarditis - acute
Cardiac tamponade - acute
Aortic dissection - acute
Peripheral arterial disease - chronic
Acute limb ischemia - acute


"""


class Cardiac(functions.MasterClass):

    def __init__(self, MCI):

        self.fn = MCI
        self.diseases = self.fn.medical_conditions(chronic=False) # Get all the acute medical conditions


    def cardiac_lytes(self):
        '''Check K and Mg levels and provide recommendations'''

        potassium = self.fn.lab_value('K') # Get patient's potassium level
        magnesium = self.fn.lab_value('MG') # Get patient's magnesium level

        recommendations = [] # Start an empty list

        if "Hypomagnesemia" in self.diseases:
            recommendations.append('')
        elif magnesium is not None and magnesium < 2:
            recommendations.append("– Replace Mg, with target ~ 2")

        if "Hypokalemia" in self.diseases:
            recommendations.append('')
        elif potassium is not None and potassium < 4:
            recommendations.append("– Replace K, with target ~ 4")

        recommendations = ('\n').join(recommendations)

        return recommendations

    def check_digoxin(self):
        """
        Function will see if digoxin is present and ask you to check a digoxin level
        If hypokalemia is present it will ask you to be careful with digoxin
        """
        # Check if digoxin is present in the medications list
        # If hypokalemia it will warn you to be careful as this increases toxicity 
        if "digoxin" in self.fn.find_all_medications():
            return "– Digoxin level"
        
    
    def start_heparin(self):

        """
        Checks text for contraindications and certain conditions before starting heparin

        if contraindications exist, Cont/Hold *** Heparin

        1.if no contraindications and patient is not on any anticoagulation at home, start heparin
        2.if Pt is on anticoagulation at home, start heparin without bolus


        
        """

        

        # Contraindications to starting heparin
        """
        Low PLT
        Worsening of anemia
        Upper GI bleeding
        Lower GI bleeding
        Hematuria
        Vaginal bleeding
        Hematoma

        Heparin-induced thrombocytopenia
        
        """

        start_heparin = []

        # Conditions that need attention when starting heparin
        caution = ["Hematoma", "Bleeding", "Upper GI Bleeding", "Lower GI Bleeding", "Hematuria", "Thrombocytopenia", "Anemia", "Heparin-induced thrombocytopenia"]

        caution_diseases = [i for i in caution if i in self.diseases]

        if caution_diseases:
            start_heparin.append(f"– Hold: heparin due to {', '.join(caution_diseases)} ***")
        else:
            start_heparin.append("– Start: heparin")

        # Check if patient already on anticoagulation
        anticoagulation = self.fn.find_medications('Anticoagulants')

        NOACs = ['apixaban', 'rivaroxaban', 'endoxaban', "dabigatran"]

        check_NOACs = [i.lower() for i in NOACs if i.lower() in anticoagulation]

        if check_NOACs:
            start_heparin.append(f' , monitor aPTT, patient is on NOAC: {"".join(check_NOACs)}')
        else:
            start_heparin.append(' , monitor with anti-factor Xa activity')


        return ''.join(start_heparin)
    
    def nitroglycerin(self):

        """
        Function should check for PDE-5 inhibitors
        It should warn you to not start nitroglycerin SL if PDE-5 were taken recently
        """

        PDE_5_inhibitors = self.fn.find_medications('Erectile Dysfunction')

        if PDE_5_inhibitors != "On  at home":
            return f'– Patient is on {PDE_5_inhibitors}, NTG SL ***'
        else: 
            return ' '
    
    def atherosclerosis_rf():
        """
        DM --> target HbA1c
        HLD --> target LDL
        HTN --> target BP
        Smoker --> Smoking cessation
        
        """

        pass
    
    def cad_gdmt(self, assessment = False, plan = False):
        add_string = 'Guideline-directed medical therapy:'

        dict_of_meds = {

            "Antiplatelets" : self.fn.find_medications("Antiplatelets, Cardiovascular", _list_only = True),
            "Antianginals" : self.fn.find_medications(["Beta Blockers", "Calcium Channel Blockers (CCBs), Dihydropyridines", "Nitrates", "Antianginals"], _list_only = True),
            "Lipid Lowering" : self.fn.find_medications(["Dyslipidemia: HMG-CoA Reductase Inhibitors (Statins)", "Dyslipidemia: Cholesterol Absorption Inhibitors", "Dyslipidemia: PCSK9 Inhibitors, Monoclonal Antibodies"], _list_only =  True),
        }

        not_on_gdmt = []
        for med, med_list in dict_of_meds.items():
            if med_list == []:
                not_on_gdmt.append(med)
            else:
                add_string += '\n' + f"   {med} : {', '.join(med_list)}"


        if assessment:
            return add_string
        
        if plan:
            add_string = self.fn.meds_list_plan(dict_of_meds['Antiplatelets'] + dict_of_meds["Antianginals"] + dict_of_meds["Lipid Lowering"])
            return add_string
        
    def chf_gdmt(self, assessment = False, plan = False):


        add_string = 'Guideline-directed medical therapy:'

        dict_of_meds = {

            "Beta-Blockers" : self.fn.find_medications("Beta Blockers", _list_only = True),
            "ACE/ARB/ARNI" : self.fn.find_medications(['Angiotensin-Converting Enzyme (ACE) Inhibitors', 'Angiotensin Receptor Blockers (ARBs)', 'Neprilysin Inhibitors'], _list_only = True),
            "MRA" : self.fn.find_medications(["spironolactone", "eplerenone"], _list_only =  True),
            "SGLT2 Inh." : self.fn.find_medications("SGLT2 Inhibitors, Cardiovascular", _list_only = True),
            "Diuretics" : self.fn.find_medications("Diuretics, Loop", _list_only = True)
            # Might need to add Hydralazine & Nitrate
        }

        # This portion should says Patient is not on MRA, ACE etc
        # If patient on GDMT, it should say Beta-blocker: Metoprolol

        not_on_gdmt = []
        for med, med_list in dict_of_meds.items():
            if med_list == []:
                not_on_gdmt.append(med)
            else:
                add_string += '\n' + f"   {med} : {', '.join(med_list)}"

        
        if assessment:
            if not_on_gdmt:
                return add_string + '\n' + f"   Not on {self.fn.format_list(not_on_gdmt)}"
            else:
                return add_string


        if plan:
            return self.fn.meds_list_plan(dict_of_meds['Beta-Blockers'] + dict_of_meds["ACE/ARB/ARNI"] + dict_of_meds["MRA"] + dict_of_meds["SGLT2 Inh."])



            
"""class CAD(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Coronary artery disease", MCI=MCI)

        self.fn = MCI


    def guideline_directed_therapy(self, assessment = False, plan = False):
        add_string = 'GDMT:'

        dict_of_meds = {

            "Antiplatelets" : self.fn.find_medications("Antiplatelets, Cardiovascular", _list_only = True),
            "Antianginals" : self.fn.find_medications(["Beta Blockers", "Calcium Channel Blockers (CCBs), Dihydropyridines", "Nitrates", "Antianginals"], _list_only = True),
            "Lipid Lowering" : self.fn.find_medications(["Dyslipidemia: HMG-CoA Reductase Inhibitors (Statins)", "Dyslipidemia: Cholesterol Absorption Inhibitors", "Dyslipidemia: PCSK9 Inhibitors, Monoclonal Antibodies"], _list_only =  True),
        }

        for med, med_list in dict_of_meds.items():
            if len(med_list) < 1:
                add_string += '\n' + f"   {med} : none"
            else:
                add_string += '\n' + f"   {med} : {', '.join(med_list)}"


        if assessment:
            return add_string
        
        if plan:
            add_string = self.fn.meds_list_plan(dict_of_meds['Antiplatelets'] + dict_of_meds["Antianginals"] + dict_of_meds["Lipid Lowering"])
            return add_string

    def __str__(self):
        add_string = self.static_assessment()

        add_string += '\n' + self.static_plan()

        if self.guideline_directed_therapy(plan=True):
            add_string += self.guideline_directed_therapy(plan=True)

        return add_string"""

"""class CHF(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Chronic congestive heart failure", MCI=MCI)

        self.fn = MCI

    def guideline_directed_therapy(self, assessment = False, plan = False):


        add_string = 'Guideline-directed medical therapy:'

        dict_of_meds = {

            "Beta-Blockers" : self.fn.find_medications("Beta Blockers", _list_only = True),
            "ACE/ARB/ARNI" : self.fn.find_medications(['Angiotensin-Converting Enzyme (ACE) Inhibitors', 'Angiotensin Receptor Blockers (ARBs)', 'Neprilysin Inhibitors'], _list_only = True),
            "MRA" : self.fn.find_medications(["spironolactone", "eplerenone"], _list_only =  True),
            "SGLT2 Inh." : self.fn.find_medications("SGLT2 Inhibitors, Cardiovascular", _list_only = True),
            "Diuretics" : self.fn.find_medications("Diuretics, Loop", _list_only = True)
            # Might need to add Hydralazine & Nitrate
        }
        counter = 1

        for med, med_list in dict_of_meds.items():
            if len(med_list) < 1:
                add_string += '\n' + f"({counter}) {med} : none"
            else:
                add_string += '\n' + f"({counter}) {med} : {', '.join(med_list)}"
            counter += 1

        
        if assessment:
            return add_string


        if plan:
            return self.fn.meds_list_plan(dict_of_meds['Beta-Blockers'] + dict_of_meds["ACE/ARB/ARNI"] + dict_of_meds["MRA"] + dict_of_meds["SGLT2 Inh."])
 



    def __str__(self):

        
        add_string = self.static_assessment()

        if self.guideline_directed_therapy():
            add_string += self.guideline_directed_therapy()
        return add_string"""

def remove_empty_lines(text: str) -> str:
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

class AcuteCoronarySyndrome(disease.Disease):

    def __init__(self, name, MCI ):
        super().__init__("NSTEMI", MCI=MCI, display_home_meds=False, full_meds_plan=True )
        
        
        self.fn = MCI
        self.card = Cardiac(MCI=MCI)
    
    def __str__(self):

        ret_string = self.static_assessment()
        
        ret_string += self.card.cad_gdmt(assessment=True) + '\n'

        previous_cad = []

        # Check for risk factors

        risk_factors = ['Diabtes mellitus', 'Hyperlipidemia', 'Current smoker', 'Hypertension']

        ret_string += self.static_plan()

        ret_string += self.card.start_heparin() + '\n'

        ret_string += self.card.cad_gdmt(assessment = False, plan=True) + '\n'

        # Start the patient on aspirin and atorvastatin if not already on it

        ret_string += self.fn.start_new_medication('atorvastatin', 'aspirin') + '\n'

        ret_string += self.card.cardiac_lytes() + '\n'

        ret_string += self.card.nitroglycerin() + '\n'


        return remove_empty_lines(ret_string)

class AcuteHeartFailure(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Acute heart failure", MCI=MCI, display_home_meds=False, full_meds_plan = True)

        self.fn = MCI

        self.card = Cardiac(MCI=MCI)

        self.diseases = self.fn.medical_conditions(chronic=False)

        self.name = "CHF exacerbation"


    def __str__(self):
        add_string = [self.static_assessment()]

        add_string.append(self.card.chf_gdmt(assessment=True))

        # check if albumin is contributing to the volume overload
        albumin = self.fn.lab_value('ALBUMIN')

        if albumin:
            if albumin < 3.5:
                add_string.append(f"Low Albumin [{albumin}] might be contributing to volume overload")


        add_string.append(self.static_plan())

        #add_string.append(self.card.guideline_directed_therapy(plan=True))

        # checks if Mg < 2 and asks to replace
        add_string.append(self.card.cardiac_lytes())

        add_string.append(self.card.check_digoxin())
        
        return '\n'.join([i.strip() for i in add_string if i])

class Bradycardia(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Symptomatic bradycardia', MCI=MCI, display_home_meds=True)
        self.fn = MCI
        self.diseases = self.fn.medical_conditions()
        self.cad = Cardiac(MCI=MCI)

        av_blocks = ['Bradycardia', 'Second-degree AV block', 'Mobitz type 1', 'Mobitz type 2', '2:1 AV block', 'High-grade AV block', 'Third-degree AV block']

        self.check_av_block = [i.lower() for i in av_blocks if i.lower() in self.diseases]

        
        hemodynamics = f"Vitals: BP {self.fn.get_single_vital('BP')} mmHg and HR {self.fn.get_single_vital('Pulse')} bpm"

        #self.assessment['other_assessment'] = 'Presented with ***' + '\n' + f"Hemodynamics: BP {BP} mmHg and HR {HR} bpm" + '\n' + "Colonoscopy on *** : ***"
        if self.check_av_block:

            self.assessment['other_assessment'] = f'Secondary to {self.check_av_block[0]}' + '\n' + 'Symptoms: ***' + ', ' +  hemodynamics + ', ' + 'EKG: ***'


    def __str__(self):


        add_string = self.static_assessment()

        contraindicated_meds = self.fn.find_medications_by_contraindication('Bradycardia')
        
        cautioned_meds = self.fn.find_medications_by_cautions('Bradycardia')

        """if contraindicated_meds:
            add_string.append(contraindicated_meds)
        add_string.append(cautioned_meds)"""

        add_string += self.static_plan()

        add_string += self.cad.check_digoxin()

        

        return add_string
    
class Afib(disease.Disease):

        def __init__(self, name, MCI):

            super().__init__('Atrial fibrillation with RVR', MCI=MCI, display_home_meds=False, full_meds_plan=True)

            self.fn = MCI
            self.card = Cardiac(MCI)

            self.diseases = self.fn.medical_conditions(chronic=False)

            # Sepsis as contributor the Afib with RVR or new-onset afib
            if 'Sepsis' in self.diseases:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + 'Likely exacerbated by sepsis'

            # Check if patient is already on anticoagulation; this will negate the need for anticoagulation
            anticoagulation_list = self.fn.find_medications('Anticoagulants',  _list_only = True)

            if anticoagulation_list:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + f"On {self.fn.format_list(anticoagulation_list)} for anticoagulation"
            else:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + 'Not on Anticoagulation due to *** CHA2DS2-VASc score ***'

            # Check for Rate-controlling
            rate_controlling_list = self.fn.find_medications(['Beta Blockers', 'Calcium Channel Blockers (CCBs), Non-dihydropyridines', 'Cardiac glycosides'], _list_only = True)

            if rate_controlling_list:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + f"On {self.fn.format_list(rate_controlling_list)} for rate control"
            else:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + 'Patient is not on rate-controlling agents'

            
            # Check for antiarrhythmics
            antiarrhythmics_list = self.fn.find_medications('Antiarrhythmics, Oral', _list_only = True)

            if antiarrhythmics_list:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + f"On {self.fn.format_list(antiarrhythmics_list)} for antiarrhythmics"



        def __str__(self):

            self.name = "Atrial fibrillation with RVR" #  Change the name to atrial fibrillation with RVR

            add_string = [self.static_assessment()]

            add_string.append(self.static_plan())

            if 'Sepsis' in self.diseases:
                add_string.append('– Allow for reflex tachycardia, Pt is septic ***')

            '''MIGHT NEED TO ADD RATE-CONTROLLING AGENTS AND ANTICOAGULATION'''


            # Checks if warfarin or coumadin is present, asks to check INR level
            check_warfarin = ['warfarin', 'coumadin']

            check_warfarin_list = [i for i in check_warfarin if i in self.fn.find_medications_by_indication('Atrial fibrillation')]

            if check_warfarin_list:
                add_string.append(f"- INR level [on {check_warfarin_list[0]}]")

            add_string.append(self.card.check_digoxin())

            add_string.append(self.card.cardiac_lytes())
         
            return '\n'.join([i.strip() for i in add_string if i])

class SVT(disease.Disease):
    
    """
    This class includes all the SVT other than Afib/Aflutter
    Assessment and plan will be very close to Afib
    
    """

    pass            

class ProlongedQT(disease.Disease):

    """THIS IS NOT COMPLETE - DOESNT DETECT MEDICATIONS TAHT CAUSE PROLONGED QT"""

    def __init__(self, name, MCI):

        super().__init__('Prolonged QT', MCI=MCI)


        # Get electrolytes levels; low K, low Mg, and low Ca can cause prolonged QT

        self.fn = MCI

        self.potassium = self.fn.lab_value('K')
        self.magnesium = self.fn.lab_value('MG')
        self.calcium = self.fn.lab_value('CA')
        """NEED TO CREATE A FUNCTION THAT HELPS WITH CORRECTED CALCIUM, IT IS USED IN MANY PLACES"""



    def __str__(self):

        add_string = self.static_assessment()


        # Check if low Mg or low K is causing prolongation in the QT interval
        lytes_list = []

        if self.potassium and self.potassium < 3.5:
            lytes_list.append(f"low potassium")
        if self.magnesium and self.magnesium <= 1.6:
            lytes_list.append(f"low magnesium")

        

        if lytes_list:
            add_string += 'Possible cause: ' + ', '.join(lytes_list) + '\n'

        add_string += self.static_plan()


        # It will add electrolyte replacement to the plan
        if lytes_list:
            add_string += '– Replace electrolytes'

        return add_string

class AcutePericarditis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Acute pericarditis', MCI=MCI)

        self.fn = MCI


    # Detect autoimmune diseases

    # Detect other causes of pericarditis: ESRD or CKD *** uremic or not, Previous radiation, Hypothyroidism
    # Pericarditis can happen even in patients with ESRD who are compliant with dialysis, dialysis-associated pericarditis

        self.diseases = self.fn.PMH_abbreviations(return_diseases=True)

    # Viral Panel


    def __str__(self):

        add_string = self.static_assessment()


        add_string += self.static_plan()

        # Start ibuprofen if no contraindication exists
        add_string += self.fn.start_new_medication('ibuprofen')

        add_string += '\n' + self.fn.start_new_medication('colchicine')


        return add_string
    

class PericardialEffusion(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Pericardial effusion", MCI=MCI)


        pass
    

class AcuteLimbIschemia(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Acute limb ischemia", MCI=MCI, display_home_meds=True)

    pass


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

apixaban
rivaroxaban
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
Metoprolol succinate
Rosuvastatin
amiodarone


 is a 84 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	10.7	04/22/2024 08:00 AM
	RBC	3.62 (L)	04/22/2024 08:00 AM
	HGB	11.1 (L)	04/22/2024 08:00 AM
	HGB	10.8 (L)	03/02/2024 10:30 AM
	HCT	34.8 (L)	04/22/2024 08:00 AM
	MCV	96.1	04/22/2024 08:00 AM
	MCH	30.7	04/22/2024 08:00 AM
	MCHC	31.9	04/22/2024 08:00 AM
	PLT	267	04/22/2024 08:00 AM
	PLT	264	03/02/2024 10:30 AM
	RDW	13.0	04/22/2024 08:00 AM
	NEUTROPHIL	7.40	04/22/2024 08:00 AM
	LYMPHOCYTE	1.94	04/22/2024 08:00 AM
	EOSINOPHIL	0.16	04/22/2024 08:00 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	143	04/22/2024 08:00 AM
	K	4.3	04/22/2024 08:00 AM
	CL	107	04/22/2024 08:00 AM
	CO2	23	04/22/2024 08:00 AM
	CA	9.6	04/22/2024 08:00 AM
	CA	9.2	03/02/2024 10:30 AM
	BUN	36 (H)	04/22/2024 08:00 AM
	CREAT	1.78 (H)	04/22/2024 08:00 AM
	GFR	37	04/22/2024 08:00 AM
	GFR	34	03/02/2024 10:30 AM
	GLUCOSE	306 (H)	04/22/2024 08:00 AM
	TOTALPROTEIN	7.1	04/22/2024 08:00 AM
	ALBUMIN	3.9	04/22/2024 08:00 AM
	BILITOTAL	0.4	04/22/2024 08:00 AM
	ALKPHOS	107	04/22/2024 08:00 AM
	ALKPHOS	113	03/02/2024 10:30 AM
	AST	14	04/22/2024 08:00 AM
	ALT	13	04/22/2024 08:00 AM
	ANIONGAP	13	04/22/2024 08:00 AM
	LACTATE	1.8	04/22/2024 08:01 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	34 (H)	04/22/2024 08:00 AM
	BASETROP	31 (H)	03/02/2024 10:30 AM
	2HRTROP	28 (H)	03/02/2024 12:45 PM
	DELTA	-3	03/02/2024 12:45 PM
	PROBNPNTERMI	6,327 (H)	04/22/2024 08:00 AM
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

cardizem
metoprolol
flecainide
aortic stenosis
obstructive sleep apnea

'''
"""
dz = AcuteHeartFailure( "Acute heart failure",  MCI=Text_input)
print(dz)
print(" ")
dise = CHF("Chronic congestive heart failure", MCI=Text_input)


print(dise)

"""

#print(Bradycardia("Bradycardia", MCI=Text_input))
#master_class = functions.MasterClass(Text_input)

#print(Afib("Atrial fibrillation with RVR", MCI=master_class))




#print('me')
#print(functions.MasterClass(MCI=Text_input).find_medications(["Beta Blockers", "Calcium Channel Blockers (CCBs), Dihydropyridines", "Nitrates", "Antianginals"], _list_only = True))
#master_class = functions.MasterClass(file_contents=Text_input)
#print(AcuteCoronarySyndrome('NSTEMI', MCI=master_class))
