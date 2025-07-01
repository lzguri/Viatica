import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease


"""
LIST OF DISEASES

DYSPHAGIA
GASTROPARESIS
ACUTE PANCREATITIS
ACUTE DIARRHEA
INFLAMMATORY BOWEL DISEASE
*DIVERTICULITIS --> INF DISEASE
ACUTE MESENTERIC ISCHEMIA
ACUTE LIVER FAILURE/ACUTE LIVER INJURY
ACUTE CHOLECYSTITIS
ACUTE CHOLANGITIS
UPPER GI BLEEDING
LOWER GI BLEEDING
BOWEL OBSTRUCTION/ILEUS


"""


"""CREATE A CLASS FOR UPPER GI BLEEDING"""
class UpperGIBleeding(disease.Disease):
    
    def __init__(self, name, MCI):
        #initialize from dataframe instead of parameters 
        super().__init__("Upper GI Bleeding", MCI=MCI)


        # Get all medical conditions
        self.fn = MCI
        self.diseases = self.fn.medical_conditions()

        # Name of the condition
        self.name = 'GI hemorrhage'

    def need_for_transfusion(self):

        """
        This function should check if there is a need for transfusion 
        – pRBC
        – PLT
        – Reverse anticoagulation

        """

        transfusion = []

        # Get latest lab values
        HGB = self.fn.lab_value('HGB')
        PLT = self.fn.lab_value('PLT')


        # Checks if Hb is < 7 and recommends transfusion
        if HGB is not None and HGB <=7:
                transfusion.append(f"– Transfuse pRBC, [HGB is {HGB} g/dL]")


        # Condition that omit PLT transfusion
        no_plt_conditions = ["Thrombotic thrombocytopenic purpura", "Heparin–induced thrombocytopenia"]

        # Trasfusion goal for PLT is 50 !!!!! Might need to be updated at some point !!!!
        if PLT is not None and PLT < 50:
                transfusion.append(f"– Transfuse PLT, [PLT count is {PLT} K/uL]" + '\n')

        
        return '\n'.join(transfusion)
    

    def determine_cirrhosis(self):
        """
        Look for liver cirrhosis in the medical conditions list
        Function will also look for low albumin and low PLT which might suggest liver cirrhosis
        
        """
        # Initialize an empty list
        add_string = []

        # Get current levels for plt, albumin
        platelet_count = self.fn.lab_value('PLT')
        albumin_level = self.fn.lab_value('HGB')
        albumin_threshold = 3.5
        plt_threshold = 130

        # Check if the patient has liver cirrhosis or findings suggestive of liver cirrhosis
        if "Liver cirrhosis" in self.diseases:
            add_string.append(f"Patient has liver cirrhosis, endoscopy on *** esophageal varices/portal HTN")
        # Check if Albumin and PLT are low – findings suggestive of liver cirrhosis
        elif albumin_level and platelet_count:
            if albumin_level < albumin_threshold and platelet_count < plt_threshold:
                add_string.append(f"\nLow PLT [{platelet_count} K/uL], and low Alb [{albumin_level} g/dL], possible liver cirrhosis")
        else:
            add_string.append("Previous GI work up ***")

        
        return ''.join(add_string)
        

    def UGIB_suggestive(self):

                # check if BUN is elevated ––> BUN > 30 is suggestive of UGIB in absence of other conditions that cause elevated BUN for example AKI, CKD or ESRD
        BUN_UGIB_exclusion = [ "acute kidney injury", "chronic kidney disease", "end–stage renal disease"]
        BUN_UGIB_exclusion_list = [i for i in BUN_UGIB_exclusion if i in self.diseases]

        BUN = self.fn.lab_value('BUN')

        add_string = []
        if BUN != None:
            if BUN > 30 and BUN_UGIB_exclusion_list:
                add_string.append("\n" + f"BUN of {BUN}, however patient has {BUN_UGIB_exclusion_list[0]}""" + '\n')
            elif BUN > 30:
                add_string.append("\n" + f"BUN of {BUN}, suggestive of UGIB" + '\n')
        
        return add_string
    
    def need_for_kcentra(self):
                # assess the nedd for Kcentra

        anticoagulants = self.fn.find_medications_by_contraindication("Upper GI Bleeding")

        Kcentra_ind = ['apixaban', 'rivaroxaban', "endoxaban", "warfarin", "coumadin"]

        Kcentra_indication = [i for i in Kcentra_ind if i in anticoagulants]

        if Kcentra_indication:
            return f"– Patient is on {Kcentra_indication[0]} , 4F–PCC [KCentra] ***"

    def __str__(self):

        BP = self.fn.get_single_vital('BP')
        HR = self.fn.get_single_vital('Pulse')

        # add to the assessment part below BUN > 30 suggests GI bleeding and if Patient ahs liver cirrhosis
        self.assessment['current_labs'] = self.assessment['current_labs'] + self.UGIB_suggestive() + [self.determine_cirrhosis()]

        add_string = [self.static_assessment().replace("Gi", "GI")]

        # another assessment part
        self.assessment['other_assessment'] = 'Presented with ***' + '\n' + f"Hemodynamics: BP {BP} mmHg and HR {HR} bpm" + '\n' + "Endoscopy on *** : ***"

        # changes Upper Gi Bleeding to Upper GI Bleeding

        if 'associated_conditions' in self.assessment:
            self.assessment['associated_conditions'] = [self.determine_cirrhosis()] + self.assessment['associated_conditions']
        # PLAN
        # Gets static plan from csv
        add_string.append(self.static_plan())

        # cheks if you need transfusion
        add_string.append(self.need_for_transfusion())

        # check for Kcentra
        add_string.append(self.need_for_kcentra())



        # start octeotride and ceftriaxone if liver cirrhosis is present or low PLT/Albumin suggestive of Liver cirrhosis
        if self.determine_cirrhosis():
            add_string.append("– IV Pantoprazole, Octeotride and Ceftriaxone" + "\n")
        else:
            add_string.append("– IV Pantoprazole" + "\n")

        # Need to monitor mental status for patient with UGIB and liver cirrhosis as they can develop hepatic encephalopathy
            
        if "Liver cirrhosis" in self.diseases:
            add_string.append("– Monitor mental status, at risk for HE")

        add_string.append(self.fn.type_of_fluids() + ', NPO')

        #To remove empty lines

        add_string = [st.strip() for st in add_string if st]

        return "\n".join(add_string)


class LowerGIBleeding(disease.Disease):
    
    
    def __init__(self, name, MCI):
        super().__init__("Lower GI Bleeding", MCI=MCI)

        self.fn = MCI

        self.transfusion_required = UpperGIBleeding("Upper GI Bleeding", MCI=MCI).need_for_transfusion()

        self.kcentra_needed = UpperGIBleeding("Upper GI Bleeding", MCI=MCI).need_for_kcentra()
    

    def __str__(self):
        # ASSESSMENT PART

        # get static assessment from CSV

        BP = self.fn.get_single_vital('BP')
        HR = self.fn.get_single_vital('Pulse')

        # add to the assessment part below BUN > 30 suggests GI bleeding and if Patient ahs liver cirrhosis


        # another assessment part
        self.assessment['other_assessment'] = 'Presented with ***' + '\n' + f"Hemodynamics: BP {BP} mmHg and HR {HR} bpm" + '\n' + "Colonoscopy on *** : ***"

        # changes Upper Gi Bleeding to Upper GI Bleeding
        add_string = [self.static_assessment().replace("Gi", "GI")]

        # PLAN
        # Gets static plan from csv
        add_string.append(self.static_plan())

        # check for Kcentra
        add_string.append(self.kcentra_needed)


        # cheks if you need transfusion
        add_string.append(self.transfusion_required)

        # start octeotride and ceftriaxone if liver cirrhosis is present or low PLT/Albumin suggestive of Liver cirrhosis

        add_string.append(self.fn.type_of_fluids() + ', NPO')

        #To remove empty lines
        add_string = "\n".join(add_string)
        add_string = [st for st in add_string.split("\n") if st]

        return "\n".join(add_string)

class AcutePancreatitis2(disease.Disease):
    
    def __init__(self, name, MCI):
        #initialize from dataframe instead of parameters 
        super().__init__("Acute Pancreatitis", MCI=MCI)

        self.fn = MCI

        # Get all the medical conditions
        self.diseases = self.fn.med

        # Get pertinent labs for acute pancreatitis
        self.lipase_level = self.fn.lab_value('LIPASE')



    def __str__(self):

        # Get etiology
        # Most common cause are gallstones, alcohol abuse, hypertriglyceridemia, hypercalcemia

        # Make a diagnosis, needs 2/3 of criteria, epigastric pain, elevated lipase, or pancreatitis on imaging

        if self.lipase_level:
            self.name = self.name + '\n' + f"Epigastric pain, lipase {self.lipase_level} U/L, Imaging ***"
        else:
            self.name = self.name + '\n' + f"Epigastric pain, lipase *** U/L, Imaging ***"



        pass

class AcutePancreatitis(disease.Disease):
    def __init__(self, MCI):
        """
        Initialize AcutePancreatitis from a medical conditions interface (MCI).
        """
        super().__init__("Acute Pancreatitis", MCI=MCI)
        self.fn = MCI
        self.lipase_level = self.fn.lab_value('LIPASE')

    def __str__(self):
        # Begin with the static assessment header
        output = self.static_assessment() + "\n"

        # Diagnostic criteria for acute pancreatitis
        criteria = [
            'Epigastric pain ***',
            'CT of abdomen showing ***'
        ]
        if self.lipase_level is not None:
            criteria.append(f'Lipase of {self.lipase_level} U/L')
        else:
            criteria.append('Lipase is *** U/L')

        # Append criteria lines
        for line in criteria:
            output += f"- {line}\n"

        # Volume depletion indicators
        bun = self.fn.lab_value('BUN')
        hct = self.fn.lab_value('HCT')
        if bun is not None and hct is not None:
            if bun > 22 and hct > 44:
                output += (
                    f"- BUN > 22 [current {bun}], "
                    f"Hct > 44 [current {hct}] suggest volume depletion\n"
                )

        # Add the static management plan
        output += self.static_plan()
        return output

    


class CDiff(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Clostridium difficile", MCI=MCI)

    global fn    
    fn = functions.MasterClass
        
    
    def __str__(self):
        
        # get the float values of Creatinine and WBC; if none detected it will return None
        Creat = fn.lab_value('CREAT')
        WBC = fn.lab_value('WBC')
        C_diff = fn.lab_value('CLOSTRIDIU')

        # get the static assessment from the acute_conditions csv
        add_string = self.static_assessment()
        
        # check if its a severe form of C. diff [WBC > 15 and Creat > 1.5]
        if Creat != None and WBC != None:
             if Creat > 1.5 and WBC > 15:
                attach_string = f"Severe C. diff: WBC {WBC} K/uL [>15] and Creat. {Creat} mg/dL [>1.5]"
                add_string = add_string.replace("Code 1986", attach_string)

        add_string += self.static_plan()
        

        return add_string
        
# ERRATE: FOR SOME REASONS ITS NOT PICKING UP PANTOPRAZOLE OR OMEPRAZOLE AS CAUTION FOR CLOSTRIDIUM 
# ERRATA: NOT DETECTING C. DIFF PCR

class AcuteDiarrhea(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Acute diarrhea", MCI=MCI)

        self.fn = MCI


    
    def __str__(self):


        add_string = self.static_assessment()

        add_string += self.static_plan()

        add_string += self.fn.type_of_fluids()

        lactate = self.fn.lab_value('LACTATE')

        if lactate:
            if lactate > 2:
                add_string += '\n' + "– Repeat lactate after fluids"

        return add_string



class IBD_flare(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Inflammatory bowel disease flare", MCI=MCI)

    global fn
    fn = functions.MasterClass



    def type_of_IBD(self):

        if "Ulcerative colitis" in fn.PMH_abbreviations():
            return "Ulcerative colitis flare"
        elif "Crohn disease" in fn.PMH_abbreviations():
            return "Crohn disease flare"
        

    def __str__(self):

        ret_string = self.static_assessment()

        ALP = fn.lab_value('ALKPHOS')

        if ALP > 140:
            ret_string += f'ALP elevated [{ALP}], PSC *** '


        ret_string = self.static_plan()


        return ret_string
    


class LiverCirrhosis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Liver cirrhosis", MCI=MCI)


        # Get all medical conditions
        self.fn = MCI
        self.diseases = self.fn.medical_conditions()

        self.assessment['associated_conditions'] = []

        if self.assessment['associated_conditions']:
            self.name = f"Liver cirrhosis secondary to {', '.join(self.assessment['associated_conditions'])}"
        else:
            self.name = "Liver cirrhosis secondary to ***"

    import math

    def calculate_meld_score(self):
        # Import math module
        import math

        # Obtain creatinine, bilirubin and inr
        creatinine = self.fn.lab_value('CREAT')
        bilirubin = self.fn.lab_value('BILITOTAL')
        inr = self.fn.lab_value('INR')

        # Check if any of the labs are absent
        if None in (creatinine, bilirubin, inr):
            absent_labs = [lab for lab, value in {'CREAT': creatinine, 'BILITOTAL': bilirubin, 'INR': inr}.items() if value is None]
            print(f"Please provide the following lab values: {', '.join(absent_labs)}")
            return None

        # Calculate MELD score
        meld_score = 10 * ((0.957 * math.log(creatinine)) + (0.378 * math.log(bilirubin)) + (1.12 * math.log(inr))) + 6.43
        return meld_score



    def __str__(self):

        # This will print the meds either treatment or prophylaxis for HE, Eso varices, SBP or ascites
        dict_of_meds = {
            "HE PPx": self.fn.find_medications_by_indication("Hepatic encephalopathy", only_meds_list=True),
            "SBP PPx": self.fn.find_medications_by_indication("Spontaneous bacterial peritonitis", only_meds_list=True),
            "Ascites Rx": self.fn.find_medications_by_indication("Ascites", only_meds_list=True),
            "Esophageal varices PPx": self.fn.find_medications_by_indication("Esophageal varices", only_meds_list=True)
        }


        add_string = self.static_assessment()


        # here we check if the patient is on anticoagulation and PLT/INR level
        anticoagulant = self.fn.detect_anticoagulation()
        INR = self.fn.lab_value('INR')
        PLT = self.fn.lab_value('PLT')

         
        # here we print HE PPx, SBP PPx, Ascite Rx, Esophageal varices PPx
        for med, med_list in dict_of_meds.items():
            if len(med_list) < 1:
                add_string += '\n' + f"Not on any meds *** for {med}"
            else:
                add_string += '\n' + f"On {', '.join(med_list)} for {med}"


        # here we print AFP level if present and HCC screening
        alphafeto = self.fn.lab_value("AFPTM")
        add_string += '\n' + "     Endoscopy: ***"

        if alphafeto:
            add_string += '\n' + f"HCC screening: *** and AFP of {alphafeto} ng/L."
        else:
            add_string += '\n' + f"HCC screening: ***"

        add_string += '\n' + self.static_plan()

        add_string += self.fn.meds_list_plan(dict_of_meds["Ascites Rx"] + dict_of_meds["Esophageal varices PPx"] + dict_of_meds["Esophageal varices PPx"] + dict_of_meds["HE PPx"])

        # checks if ascites is present and prints paracentesis
        if "Ascites" in self.diseases:
            add_string += "\n" + "– Paracentesis w fluid analysis [6–8g/L of 25% of alb. if > 5L are removed] ***" + "\n" + "– Low sodium diet [<2g/d] if not NPO ***"
        
        add_string = "\n".join([st for st in add_string.split("\n") if st])

        return add_string


class Gastroparesis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Gastroparesis", MCI=MCI)

        self.fn = functions.MasterClass
        

    
    def __str__(self):
        
        add_string = self.static_assessment()

        if add_string:
            return add_string
        





class SBO(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Bowel obstruction", MCI=MCI)


    
    def __str__(self):


        add_string = self.static_assessment()
        add_string += self.static_plan()



        return add_string

class IntractableVomiting(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Intractable vomiting", MCI=MCI)

        self.fn = functions.MasterClass
        self.diseases = fn.PMH_abbreviations(return_diseases=True)

        self.Gastroparesis = Gastroparesis("Gastroparesis", MCI=MCI)
        self.SBO = SBO("Small bowel obstruction", MCI=MCI)


    def __str__(self):

        disease_names = {
            "Gastroparesis" : self.Gastroparesis.__str__,
            "Small bowel obstruction" : self.SBO.__str__
        }

        if "Gastroparesis" in self.diseases:
            return self.Gastroparesis


class ElevatedLiverEnzymes(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Elevated liver enzymes", MCI=MCI)


        # Create an instance of the MasterClass from the functions module
        self.fn = MCI

        # Get all the diseases present in the text
        self.diseases = self.fn.medical_conditions()

        # Extract relevant liver enzyme values
        self.ALT = self.fn.lab_value("ALT")
        self.AST = self.fn.lab_value("AST")
        self.ALP = self.fn.lab_value("ALKPHOSPH")
        self.Tot_bilirubin = self.fn.lab_value("TOTBILI")
        self.LDH = self.fn.lab_value('LDH')
        self.INR = self.fn.lab_value('INR')

        # Upper limits of normal for ALT and ALP
        self.ULN_ALT = 40
        self.ULN_ALP = 120


    def calculate_r_factor(self):
        # Calculate R factor to assess the type of injury: hepatocellular, cholestatic injury, mixed injury
        if self.ALT and self.ALP:
            self.r_factor = (self.ALT / self.ULN_ALT) / (self.ALP / self.ULN_ALP)

        # Initialize the pattern attribute
        self.pattern = None

        # Determine the pattern based on the calculated R factor
        if self.r_factor:
            if self.r_factor > 5:
                self.pattern = f"R factor {self.r_factor} suggestive of hepatocellular injury"
            elif 5 >= self.r_factor >= 2:
                self.pattern = f"R factor {self.r_factor} suggestive of mixed injury"
            elif self.r_factor < 2:
                self.pattern = f"R factor {self.r_factor} suggestive of cholestatic injury"

        
        return self.pattern

    def calculate_ALT_LDH_ratio(self):
        """
        Calculate ALT:LDH ratio

        if ratio is > 1.5 it suggest acute viral hepatitis

        if LDH is not present in the text, it will ask the user to check and LDH level and calculate ALT:LDH ratio
        
        """ 
        # Calculate LDH:ALT ratio
        self.ldh_alt_ratio = None
        if self.LDH and self.ALT:
            self.ldh_alt_ratio = self.LDH / self.ALT

        # Differentiate between ischemic hepatitis, alcoholic hepatitis, and DILI based on LDH:ALT ratio
        if self.ldh_alt_ratio:
            if self.ldh_alt_ratio > 1.5:
                self.pattern += f"\nLDH:ALT ratio {self.ldh_alt_ratio} suggestive of viral hepatitis"
        else:
            self.pattern = "– Check serum LDH to calculate ALT:LDH ratio"

        return self.pattern
    

    def acute_liver_failure(self):
        """
        Check for findings suggestive of acute liver failure (ALF) in a patient without pre–existing liver disease.

        Criteria:
        1. Presence of hepatic encephalopathy
        2. International Normalized Ratio (INR) >= 1.5
        3. Both Alanine Aminotransferase (ALT) and Aspartate Aminotransferase (AST) > 1000

        Returns:
        A string indicating whether the patient has findings suggestive of ALF.
        """
        counter = 0

        # Check for the presence of hepatic encephalopathy
        if "Hepatic encephalopathy" in self.fn.diseases:
            counter += 1

        # Check if INR is elevated
        if self.INR and self.INR >= 1.5:
            counter += 1

        # Check if both ALT and AST are elevated
        if self.ALT and self.AST and self.ALT > 1000 and self.AST > 1000:
            counter += 1

        # Determine the overall assessment based on the counter
        if counter == 3:
            return "Patient has findings suggestive of ALF: Altered mental status, Elevated ALT/AST, and INR > 1.5"
        else:
            return "No definitive findings of ALF based on the criteria"

    

        





    
    def __str__(self):

        pass



    """
    Calculate R factor to assess for hepatocellular, mixed or cholestatic
    Calculate ALT–LDH index, this should help differentiate between ischemic hepatitis
    Calculate AST/ALT ratio, if > 2:1 suggestive of alcohol as a cause of elevated liver enzymes
    Calculate ALP to total bilirubin ratio for wilson disease

    Look for non–liver causes of elevated enzymes ––> rhabdomyolyisis
    Look for biliarubin elevation ––> hemolysis: low Hb compared to prior and high MCV or Rct count
    
    """
"""
Bowel Obstruction
Presenting with ***
CT abdomen: ***

Electrolytes: Sod. of 139.0 mEq/L and K of 2.0 mEq/L.
Associated conditions: ULCERATIVE COLITIS
Plan
– Check <––– SHOULD BE CHECK MG AND PHOSPHORUS
– NPO
– NG tube and IV fluids [NS with K supplementation ***]
– Bowel rest
– Surgery consult

"""


class Dyphagia():
     pass


class IntractableNV():
     pass


class ElevatedLiverEnzymes():
     pass

"""class Dysphagia:

    def oropharyngeal_dysphagia():
        # conditions that cause oropharyngeal dyphagia
        # neurologic: ALS, CVA, MG, MS, Muscular dystrophy, CNS tumors, Sjogren syndrome
        pass



# esophageal dysphagia

class GERD:
    pass

class EosinophilicEsophagitis:
    pass


class AcutePancreatitis:

    # cause of acute pancreatitis: gallstones, biliary sludge, microlithiasis, alcohol use/abuse, type V choledochocele
    # cause of acute pancreatitis: labs: hypertriglyceridemia [can cause pseudohyponatremia], hypercalcemia
    # other causes of acute pancreatitis: autoimmune pancreatitis type I and type II <–– associated conditions with type I: sclerosing cholangitis, retroperitoneal fibrosis, Mikulicz disease
    # h/o chronic pancreatitis
    # Labs: serum lipase/amylase >= 3.0 suggestive of alcoholic pancreatitis, serum AST/ALT > 3x suggetive of gallstone pancreatitis
    pass


class ChronicPancreatitis:
    pass



"""





Text_input = '''
 is a 81 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	9.2	02/07/2024 12:59 PM
	RBC	2.78 (L)	02/07/2024 12:59 PM
	HGB	8.3 (L)	02/07/2024 12:59 PM
	HGB	8.9 (L)	01/02/2024 11:31 PM
	HCT	24.9 (L)	02/07/2024 12:59 PM
	MCV	89.6	02/07/2024 12:59 PM
	MCH	29.9	02/07/2024 12:59 PM
	MCHC	33.3	02/07/2024 12:59 PM
	PLT	63 (L)	02/07/2024 12:59 PM
	PLT	70 (L)	01/02/2024 11:31 PM
	RDW	15.8 (H)	02/07/2024 12:59 PM
	NEUTROPHIL	8.08 (H)	01/02/2024 09:51 AM
	LYMPHOCYTE	0.22 (L)	01/02/2024 09:51 AM
	EOSINOPHIL	0.00	01/02/2024 09:51 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	141	02/07/2024 12:59 PM
	K	3.1	02/07/2024 12:59 PM
	CL	112 (H)	02/07/2024 12:59 PM
	CO2	19 (L)	02/07/2024 12:59 PM
	CA	7.6 (L)	02/07/2024 12:59 PM
	CA	7.1 (L)	01/02/2024 11:31 PM
	BUN	47 (H)	02/07/2024 12:59 PM
	CREAT	1.72 (H)	02/07/2024 12:59 PM
	GFR	39	02/07/2024 12:59 PM
	GFR	33	01/02/2024 11:31 PM
	GLUCOSE	119 (H)	02/07/2024 12:59 PM
	TOTALPROTEIN	4.1 (L)	02/07/2024 12:59 PM
	ALBUMIN	1.7 (L)	02/07/2024 12:59 PM
	BILITOTAL	0.8	02/07/2024 12:59 PM
	URICACID	6.6	12/11/2023 12:05 PM
	ALKPHOS	62	02/07/2024 12:59 PM
	ALKPHOS	89	01/02/2024 09:51 AM
	AST	52 (H)	02/07/2024 12:59 PM
	ALT	22	02/07/2024 12:59 PM
	ANIONGAP	10	02/07/2024 12:59 PM
	T4FREE	1.25	09/24/2019 01:59 PM
	LACTATE	1.6	02/07/2024 12:59 PM


Cardiac profile

Lab Results
Component	Value	Date/Time
	INR	1.7 (H)	02/07/2024 12:59 PM
	PT	20.7 (H)	02/07/2024 12:59 PM


workup
Lab Results
Component	Value	Date/Time
	IRON	165	12/11/2023 12:05 PM
	IRON	45 (L)	11/14/2023 01:23 PM
	TIBC	301	12/11/2023 12:05 PM
	TIBC	327	11/14/2023 01:23 PM
	IRONPERCENT	55 (H)	12/11/2023 12:05 PM
	IRONPERCENT	14 (L)	11/14/2023 01:23 PM
	FERRITIN	1028 (H)	12/11/2023 12:05 PM
	FERRITIN	149.3	11/21/2023 09:34 AM
	FERRITIN	127	09/20/2023 11:53 AM
	LD	319 (H)	12/11/2023 12:05 PM
	LD	159	04/14/2015 09:46 AM
	VITAMINB12	583	12/11/2023 12:05 PM
	VITAMINB12	490	11/14/2023 01:23 PM
	FOLATE	15.0	12/11/2023 12:05 PM
	FOLATE	16.1	08/08/2023 11:43 AM


Lab Results
Component	Value	Date/Time
	PHUA	5.5	12/19/2023 09:57 PM
	SGUR	1.024	12/19/2023 09:57 PM
	URINELEUKOC	Negative	12/19/2023 09:57 PM
	NITRITEUA	Negative	12/19/2023 09:57 PM
	KETONEURINE	Negative	12/19/2023 09:57 PM
	PROTEINUA	Negative	12/19/2023 09:57 PM
	GLUUA	Negative	12/19/2023 09:57 PM
	BLOODUA	Trace (A)	12/19/2023 09:57 PM
	RBCUA	0–2	09/29/2015 11:52 AM
	BACTERIAUA	TRACE (A)	09/29/2015 11:52 AM
	UREPITHELIAL	1+	08/26/2015 08:52 AM


Lab Results
Component	Value	Date/Time
	ESR	57 (H)	01/02/2024 11:31 PM
	CRP	203.7 (H)	01/02/2024 11:31 PM


No results found for: "PHBLOODPOC", "PCO2POC", "PO2POC", "PFRATIO", "O2SATPOC"

No results found for: "INFLUENZAA", "INFLUENZAB", "COVID19", "RSVAG"

Lab Results
Component	Value	Date/Time
	HGBA1C	5.2	05/05/2022 10:40 AM
	LDLCALC	72	11/01/2022 09:38 AM


Lab Results
Component	Value	Date/Time
	TRIGLYCERIDE	89	11/01/2022 09:38 AM
	TSH	5.25 (H)	06/06/2023 12:46 PM
	TSH	5.13 (H)	11/01/2022 09:38 AM


Toxicology
No results found for: "ETHANOL", "ACETAMINOPHE", "SALICYLATE"

Vitamins
Lab Results
Component	Value	Date/Time
	VITAMINDTO	43	02/18/2019 10:40 AM


Tumor markers
No results found for: "AFPTM"

Virology
No results found for: "CD4", "HIV1RNACOPIE", "HEPAIGM", "HEPBCORIGM", "HEPBSAG", "HEPCAB" 


GIPATHOGEN
No results found for: "CLOSTRIDIU"




Principal Problem:
  Necrotizing fasciitis
Active Problems:
  Pulmonary emphysema
    Overview: Per query response; office visit 11.5.2021
  Acute kidney injury superimposed on CKD
  Cellulitis and necrosis of penis
  Acute diarrhea
  Severe sepsis with septic shock

  Protein–calorie malnutrition, severe
 


Vitals:
	01/03/24 1300
BP:	118/53
Pulse:	80
Resp:	18
Temp:	
SpO2:	97%



Prior to Admission Medications
Prescriptions	Last Dose	Informant	Patient Reported?	Taking?
acyclovir (ZOVIRAX) 400 mg tablet	1/2/2024		No	Yes
Sig: Take 1 Tablet (400 mg) by mouth 2 times daily.
aspirin (ECOTRIN EC) 81 mg Tablet, Delayed Release (E.C.)	1/2/2024		Yes	Yes
Sig: Take 81 mg by mouth daily.
cyanocobalamin (VITAMIN B–12) 1,000 mcg/mL Solution	1/2/2024		No	Yes
Sig: Inject 1 mL (1,000 mcg) by intramuscular injection every 30 days.
cyanocobalamin 1,000 mcg Tablet			No	No
Sig: Take 1 Tablet (1,000 mcg) by mouth daily.
dexAMETHasone (DECADRON) 4 mg tablet			No	No
Sig: Take (5 tablets) in the morning with food once a week, while you are receiving the Velcade.
lenalidomide (Revlimid) 15 mg capsule	1/2/2024		No	Yes
Sig: TAKE 1 CAPSULE BY MOUTH DAILY ON DAYS 1–14 OF A 21 DAY CYCLE
levothyroxine 100 mcg tablet	1/2/2024		No	Yes
Sig: Take 1 Tablet (100 mcg) by mouth daily in the morning.
lisinopriL (PRINIVIL) 10 mg tablet	1/2/2024		No	Yes
Sig: Take 1 Tablet (10 mg) by mouth daily.
multivitamin/iron/folic acid (CENTRUM ORAL)	1/2/2024		Yes	Yes
Sig: Take 1 Tablet by mouth daily.
ondansetron (ZOFRAN ODT) 8 mg Tablet, Rapid Dissolve	1/2/2024		No	Yes
Sig: Place 1 Tablet (8 mg) under tongue every 8 hours as needed for Nausea/Emesis. Dissolve 1 tablet on top of tongue then swallow with saliva every 8 hours as needed for nausea or vomiting
predniSONE (DELTASONE) 10 mg tablet			No	No
Sig: Take 70 mg PO on day 1 then decrease by 10 mg each day until completed (70, 60, 50, 40, 30, 20, 10 mg over 7 days).
Patient not taking: Reported on 1/2/2024

Facility–Administered Medications: None


Current Facility–Administered Medications
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	aspirin (ECOTRIN EC) tablet 81 mg	 81 mg	Oral	daily	Gilmore, Lisa L, FNP	 	 
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	[Held by Provider] heparin injection 5,000 Units	 5,000 Units	subCUT	every 8 hours	Gilmore, Lisa L, FNP	 	5,000 Units at 01/03/24 0903
•	HYDROcodone–acetaminophen (NORCO) 7.5–325 mg per tablet 1 Tablet	 1 Tablet	Oral	every 6 hours PRN	Gilmore, Lisa L, FNP	 	 
•	HYDROmorphone (DILAUDID) 2 mg/mL injection 1 mg	 1 mg	IV	every 2 hours PRN	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] vancomycin in sodium chloride 0.9% (VANCOCIN) 750 mg/257.5 mL IVPB 750 mg	 750 mg	IV	ONE time only	Meyer III, Magnus O, DO	 	Stopped at 01/03/24 1529
•	[COMPLETED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Robb, Lauren E, PA	 	Stopped at 01/03/24 1107
•	[START ON 1/4/2024] levothyroxine (SYNTHROID) tablet 100 mcg	 100 mcg	Oral	daily EARLY	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Meyer III, Magnus O, DO	999 mL/hr at 01/03/24 1332	Rate Verify at 01/03/24 1332
•	fentaNYL (PF) 1,500 mcg/30 mL (50 mcg/mL) PCA	 0–150 mcg/hr	IV	titrate	Gilmore, Lisa L, FNP	 	 
•	propofol (DIPRIVAN) 10 mg/mL continuous infusion	 0–50 mcg/kg/min	IV	titrate	Gilmore, Lisa L, FNP	 	 
•	[DISCONTINUED] levothyroxine (SYNTHROID) tablet 100 mcg	 100 mcg	Oral	daily EARLY	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] sodium hypochlorite (DAKIN'S) 0.25% half–strength topical solution	 		intra–proc PRN	Draper, Brian B, DO	 	230 mL at 01/03/24 1516
•	acetaminophen (TYLENOL) tablet 650 mg	 650 mg	Oral	every 6 hours PRN	Gilmore, Lisa L, FNP	 	 
•	VANCOMYCIN CONSULT TO PHARMACY	 	See Admin Instructions	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Yassa, Youssef Y, MD	 	 
•	[COMPLETED] albumin, human (BUMINATE) 5 % injection 25 Gram	 25 Gram	IV	ONE time only	Pallohusky, Brian S, MD	 	Stopped at 01/02/24 1815
•	[COMPLETED] lactated ringers infusion	 	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 01/02/24 1830
•	[COMPLETED] lactated ringers infusion	 	IV	ONE time only	Zguri, Liridon, MD	999 mL/hr at 01/02/24 1845	New Bag at 01/02/24 1845
•	[COMPLETED] DEXTROSE 50 % IN WATER (D50W) INTRAVENOUS SYRINGE (CABINET OVERRIDE)	 				 	25 Gram at 01/02/24 1939
•	[COMPLETED] hydrocortisone sod succinate (PF) (Solu–CORTEF) 100 mg in sterile water 2 mL injection	 100 mg	IV	ONE time only	Zguri, Liridon, MD	 	100 mg at 01/02/24 1940
•	[COMPLETED] PHENYLEPHRINE 10 MG/ML INJECTION SOLUTION (CABINET OVERRIDE)	 				 	50 mg at 01/02/24 1936
•	[COMPLETED] HYDROCORTISONE SOD SUCCINATE (PF) 100 MG/2 ML SOLUTION FOR INJECTION (CABINET OVERRIDE)	 				 	100 mg at 01/02/24 1930
•	[COMPLETED] DEXTROSE 5 % IN WATER (D5W) INTRAVENOUS SOLUTION (CABINET OVERRIDE)	 				3.2 mL/hr at 01/02/24 1933	250 mL at 01/02/24 1933
•	[COMPLETED] dextrose 50% (D50) syringe 25 Gram	 25 Gram	IV	ONE time only	Zguri, Liridon, MD	 	25 Gram at 01/02/24 1945
•	norepinephrine bitartrate–D5W (LEVOPHED) 8 mg/250 mL (32 mcg/mL) infusion	 0–0.2 mcg/kg/min	IV	titrate	Gilmore, Lisa L, FNP	7.523 mL/hr at 01/03/24 1504	0.075 mcg/kg/min at 01/03/24 1504
•	[COMPLETED] sodium chloride 0.9% bolus solution 500 mL	 500 mL	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 01/02/24 2015
•	SEPSIS ANTIBIOTIC ALERT TO PHARMACY	 1 Each	See Admin Instructions	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	sodium chloride 0.9% bolus solution 500 mL	 500 mL	IV	ONE time only	Gilmore, Lisa L, FNP	 	 
•	dextrose 5% – sodium chloride 0.9% infusion	 	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	dextrose 50% (D50) syringe 12.5 Gram	 12.5 Gram	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	dextrose 50% (D50) syringe 25 Gram	 25 Gram	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	glucagon human recombinant (GLUCAGEN) 1 mg/mL injection 1 mg	 1 mg	IM	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] ACETAMINOPHEN 325 MG TABLET (CABINET OVERRIDE)	 				 	650 mg at 01/02/24 2117
•	piperacillin–tazobactam (ZOSYN) 3.375 Gram in sodium chloride 0.9% 50 mL IVPB (MBP)	 3.375 Gram	IV	every 8 hours	Gilmore, Lisa L, FNP	 	Stopped at 01/03/24 1258
•	clindamycin (CLEOCIN) 600 mg in 0.9% sodium chloride IVPB	 600 mg	IV	every 8 hours	Gilmore, Lisa L, FNP	 	Stopped at 01/03/24 0952
•	hydrocortisone sod succinate (PF) (Solu–CORTEF) 50 mg in sterile water 1 mL injection	 50 mg	IV	every 6 hours	Gilmore, Lisa L, FNP	 	50 mg at 01/03/24 1229
•	dextran 70–hypromellose PF (ARTIFICIAL TEARS) 0.1–0.3 % ophthalmic solution 1 Drop	 1 Drop	Both Eyes	every 4 hours PRN	Gilmore, Lisa L, FNP	 	1 Drop at 01/03/24 0106
•	[DISCONTINUED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Nguyen, Tina H, MD	 	 
•	[DISCONTINUED] clindamycin (CLEOCIN) 600 mg in dextrose 5% 50 mL IVPB	 600 mg	IV	ONE time only	Nguyen, Tina H, MD	 	 
•	[DISCONTINUED] metroNIDAZOLE (FLAGYL) IVPB 500 mg	 500 mg	IV	ONE time only	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] piperacillin–tazobactam (ZOSYN) 3.375 Gram in sodium chloride 0.9% 50 mL IVPB (MBP)	 3.375 Gram	IV	every 6 hours	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] clindamycin (CLEOCIN) 600 mg in dextrose 5% 50 mL IVPB	 600 mg	IV	every 8 hours	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection 25 mcg	 25 mcg	IV	post–proc every 3 minutes PRN	Yassa, Youssef Y, MD	 	 
•	[DISCONTINUED] HYDROmorphone (DILAUDID) 2 mg/mL injection 0.2 mg	 0.2 mg	IV	post–proc every 5 minutes PRN	Yassa, Youssef Y, MD	 	 
•	[DISCONTINUED] bacitracin–polymyxin B 500–10,000 unit/gram topical ointment	 		intra–proc PRN	Richardson, Tyrun K, MD	 	 
•	[DISCONTINUED] sodium hypochlorite (DAKIN'S) 0.25% half–strength topical solution	 		intra–proc PRN	Richardson, Tyrun K, MD	 	200 mL at 01/02/24 1647
•	[DISCONTINUED] phenylephrine syringe 100 mcg	 100 mcg	IV	post–proc every 10 minutes PRN	Pallohusky, Brian S, MD	 	100 mcg at 01/02/24 1801
•	[DISCONTINUED] phenylephrine 50 mg in sodium chloride 0.9% 250 mL infusion	 0–1 mcg/kg/min	IV	titrate	Zguri, Liridon, MD	11.2 mL/hr at 01/02/24 2210	0.7 mcg/kg/min at 01/02/24 2210
•	[DISCONTINUED] OTHER	 		see admin instructions	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] levothyroxine (SYNTHROID) tablet 50 mcg	 50 mcg	Oral	daily EARLY	Krazer, Kevin B, ANP	 	50 mcg at 01/03/24 0542
•	[DISCONTINUED] dextran 70–hypromellose PF (ARTIFICIAL TEARS) 0.1–0.3 % ophthalmic solution 1 Drop	 1 Drop	Both Eyes	every 4 hours PRN	Anand, Neesha, MD	 	 

Facility–Administered Medications Ordered in Other Encounters
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	EPINEPHrine PF 1 mg/mL (1:1,000) solution	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	0.01 mg at 01/03/24 1429
•	phenylephrine syringe	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	200 mcg at 01/03/24 1355
•	phenylephrine 20 mg in sodium chloride 0.9% 250 mL infusion	 	IV	intra–proc continuous PRN	Scott, Christy A, CRNA	15.008 mL/hr at 01/03/24 1516	0.3 mcg/kg/min at 01/03/24 1516
•	fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	50 mcg at 01/03/24 1545
•	sodium chloride 0.9% infusion	 	IV	intra–proc continuous PRN	Scott, Christy A, CRNA	 	New Bag at 01/03/24 1357
•	lactated ringers infusion	 	IV	intra–proc continuous PRN	Scott, Christy A, CRNA	 	New Bag at 01/03/24 1341
•	lidocaine PF 2% (XYLOCAINE MPF) injection	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	2 mL at 01/03/24 1352
•	propofoL (DIPRIVAN) injection	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	50 mg at 01/03/24 1353
•	rocuronium injection	 	IV	intra–proc PRN	Scott, Christy A, CRNA	 	30 mg at 01/03/24 1606
•	[DISCONTINUED] sodium chloride 0.9 % 250 mL flush bag 250 mL	 250 mL	IV	see admin instructions	Grogan, Susan K, FNP	 	Stopped at 01/02/24 1123
•	[DISCONTINUED] dexAMETHasone (DECADRON) 20 mg in sodium chloride 0.9% 100 mL IVPB (PREMIX)	 20 mg	IV	ONE time only	Snider, Jessica Nicole, DO	 	 
•	[DISCONTINUED] iron sucrose (VENOFER) 200 mg in sodium chloride 0.9% 110 mL IVPB (PREMIX)	 200 mg	IV	ONE time only	Snider, Jessica Nicole, DO	 	 
•	[DISCONTINUED] sodium chloride 0.9% infusion	 	IV	intra–proc continuous PRN	Schmitt, Adriel, CRNA	 	Stopped–Anesthesia at 01/02/24 1705
•	[DISCONTINUED] phenylephrine 20 mg in sodium chloride 0.9% 250 mL infusion	 	IV	intra–proc continuous PRN	Schmitt, Adriel, CRNA	 	Stopped at 01/02/24 1654
•	[DISCONTINUED] fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	25 mcg at 01/02/24 1559
•	[DISCONTINUED] propofoL (DIPRIVAN) injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	60 mg at 01/02/24 1542
•	[DISCONTINUED] ondansetron (ZOFRAN) 4 mg/2 mL injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	4 mg at 01/02/24 1546
•	[DISCONTINUED] dexAMETHasone (DECADRON) injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	8 mg at 01/02/24 1546
•	[DISCONTINUED] lidocaine PF 2% (XYLOCAINE MPF) injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	4 mL at 01/02/24 1542
•	[DISCONTINUED] phenylephrine injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	100 mcg at 01/02/24 1604
•	[DISCONTINUED] ePHEDrine injection	 	IV	intra–proc PRN	Schmitt, Adriel, CRNA	 	10 mg at 01/02/24 1639

primary biliary cholangitis
Upper GI Bleeding

'''
"""dis4 = UpperGIBleeding("Upper GI Bleeding", MCI=Text_input)

dis5 = CDiff("Clostridium difficile", MCI = Text_input)

dis6 = AcutePancreatitis("Acute Pancreatitis", MCI=Text_input)

dis7 = SBO("Bowel obstruction", MCI=Text_input)

print(dis4)

print('\n')

print(dis5)

print(dis6)

print(dis7)"""


"""livercirrhosis = LiverCirrhosis('Liver cirrhosis', MCI=Text_input)

print(str(livercirrhosis))"""


"""AP = UpperGIBleeding("Upper GI Bleeding", MCI=Text_input)

print(AP.PMH)"""


# master_class_instance = functions.MasterClass(Text_input)

# print(UpperGIBleeding("Upper GI Bleeding", MCI=master_class_instance).static_assessment())
