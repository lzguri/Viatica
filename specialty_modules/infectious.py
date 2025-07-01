import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease
import utility_function as utils

"""
DISEASES
Meningitis
Encephalitis
Dental abscess
Pneumonia
Acute diarrhea
Ascending cholangitis
Acute cholecysitis
Diverticulitis
Abdominal abscess
Acute hepatitis
Cellulitis
Necrotizing fasciitis
Urinary tract infection
Pelvic inflammatory disease
Acute epidimitis


GENERIC DISEASES
Abscess
Sepsis of unknown source

"""


# class Sepsis3_0(functions.MasterClass):
#     """
#     This class is dedicated to sepsis in general, now including SIRS criteria.

#     Args:
#         file_contents (str): The text content of the medical record.
#     """

#     def __init__(self, file_contents):
#         super().__init__(file_contents=file_contents)

#         """
#         Initializes the Sepsis3_0 class and extracts medical conditions.

#         Args:
#             file_contents (str): The text content of the medical record.
#         """

#         # Extract all medical conditions from the text (file_contents)
#         self.diseases = self.medical_conditions()

#         # Key labs and vitals
#         self.lactate = self.lab_value('LACTATE')
#         self.wbc = self.lab_value('WBC')
#         self.temp = self.extract_vital('TEMP')
#         self.hr = self.extract_vital('HR')
#         self.rr = self.extract_vital('RR')

#     def sirs_criteria(self):
#         """
#         Returns list of met SIRS criteria:
#         - Temperature >38°C or <36°C
#         - Heart rate >90 bpm
#         - Respiratory rate >20/min
#         - WBC >12k or <4k
#         """
#         criteria = []
#         if self.temp is not "***" and (float(self.temp) > 100.4 or float(self.temp) < 96.8):
#             criteria.append("Abnormal temperature")
#         if self.hr is not "***" and float(self.hr) > 90:
#             criteria.append("Tachycardia")
#         if self.rr is not "***" and float(self.rr) > 20:
#             criteria.append("Tachypnea")
#         if self.wbc is not None and (self.wbc > 12 or self.wbc < 4):
#             criteria.append(f"Abnormal WBC: {self.wbc}")
#         return criteria
    
#     def check_for_sepsis(self):
#         """
#         Sepsis defined by:
#         - Documented sepsis OR
#         - ≥2 SIRS criteria in context of infection
#         """
#         sirs = self.sirs_criteria()
#         # Define infections that qualify for sepsis context
#         infection_markers = [
#             "meningitis", "encephalitis", "dental abscess", "pneumonia",
#             "acute diarrhea", "ascending cholangitis", "acute cholecystitis",
#             "diverticulitis", "abdominal abscess", "acute hepatitis",
#             "cellulitis", "necrotizing fasciitis", "urinary tract infection",
#             "pelvic inflammatory disease", "acute epididimitis"
#         ]
#         has_infection = any(
#             d.lower().startswith('infection') or 'sepsis' in d.lower() or
#             any(marker in d.lower() for marker in infection_markers)
#             for d in self.diseases
#         )
#         if "Sepsis" in self.diseases or (len(sirs) >= 2 and has_infection):
#             return 'Sepsis due to '
#         return ''
    
#     def sps_assessment(self):
#         if not self.check_for_sepsis():
#             return ''
#         parts = []
#         # Include SIRS summary
#         sirs = self.sirs_criteria()
#         if sirs:
#             parts.append(f"SIRS criteria met: {self.format_list(sirs)}")
#         # Standard sepsis bundle
#         parts.append('30 mL/kg IVF *** given')
#         if "Hypertension" in self.diseases:
#             parts.append("BP on presentation ***, Patient has h/o HTN")
#         if self.wbc:
#             parts.append(f"Pt has a WBC of {self.wbc}")
#             if self.lactate:
#                 parts[-1] += f", and lactic of {self.lactate}"
#         return "\n".join(parts)

#     def sps_plan(self):
#         if not self.check_for_sepsis():
#             return ''
#         plan = [
#             "– Blood culture",
#             "– MAP goal > 65"
#         ]
#         if self.lactate is None:
#             plan.append("– Check lactic acid")
#         elif self.lactate > 2:
#             plan.append("– Recheck lactic acid, Goal < 2")
#         plan.append(self.type_of_fluids())
#         return "\n".join(plan)

class Sepsis2_0(functions.MasterClass):
    """
    This class is dedicated to sepsis in general

    Args:
        file_contents (str): The text content of the medical record.
    """

    def __init__(self, file_contents):
        super().__init__(file_contents=file_contents)

        """
        Initializes the Sepsis2_0 class and extracts medical conditions.

        Args:
            file_contents (str): The text content of the medical record.
        """


        # Extract all medical conditions from the text (file_contents)
        self.diseases = self.medical_conditions() 

        # List of the possible organ dysfunctions seen in sepsis; UPDATE IT
        self.organ_dysfunction = [
            "Acute respiratory failure",
            "Altered mental status",
            "Acute kidney injury",
            "Hypotension",
            "Acute liver failure"
        ]

        # Get lactic acid level and WBC count
        self.lactate = self.lab_value('LACTATE')
        self.wbc = self.lab_value('WBC')


    def check_for_sepsis(self):

        if "Sepsis" in self.diseases:
            return 'Sepsis due to '
        else:
            return ''

    def sps_assessment(self):
        """
        Analyzes extracted data to assess potential sepsis and generates a report.

        Returns:
            str: A report string containing assessment details.
        """

        # Check if sepsis exists, if it doesnt stop there
        if "Sepsis" not in self.diseases:
            return ''
            

        assess_text = '30 mL/kg IVF *** given\n'

        # Check if organ dysfunction exists in the disease list
        existing_organ_dysf = [dis for dis in self.organ_dysfunction if dis in self.diseases]

        if existing_organ_dysf:
            assess_text += f'Organ dysfunction noted: {self.format_list(existing_organ_dysf)}\n'

        # Check if patient has hypertension at baselien
        if "Hypertension" in self.diseases:
            assess_text += "BP on presentation ***, Patient has h/o HTN\n"

        # Report lactic acid level and WBC count:
        if self.wbc:
            assess_text += f"Pt has a WBC of {self.wbc}"

        if self.lactate:
            assess_text += f", and lactic of {self.lactate}"

        return assess_text

    def sps_plan(self):
        """
        Generates a treatment plan for sepsis based on the assessment.

        Returns:
            str: A string containing the treatment plan.
        """

        # Check if sepsis exists, if it doesnt stop there
        if "Sepsis" not in self.diseases:
            return ''

        plan_text = "– Blood culture\n"

        plan_text += "– MAP goal > 65\n"

        # Check if lactic is checked and if elevated, needs to be rechecked
        if self.lactate is None:
            plan_text += "– Check lactic acid\n"
        elif self.lactate > 2:
            plan_text += "– Recheck lactic acid, Goal < 2\n"

        plan_text +=  self.type_of_fluids()

        return utils.remove_empty_lines(plan_text)



"""class Cellulitis(disease.Disease, Sepsis3_0):

    def __init__(self, name, MCI):
        super().__init__('Cellulitis', MCI=MCI)
        self.fn = MCI

        # Extract diseases from the text
        self.diseases = self.fn.medical_conditions() # this returns a list of all the diseases

        # Call instance of sepsis 2.0
        self.sepsis = Sepsis2_0(file_contents=MCI.file_contents) ### WORKS

        self.check_sepsis = [i for i in self.diseases if i == "Sepsis"]

    

    def __str__(self):

        # Assessment part
        # Change name if sepsis is detected
        self.name = self.sepsis.check_for_sepsis() + self.name.lower()


        add_string = '\n' + self.static_assessment()

        if self.check_sepsis is not None:
            add_string += self.sepsis.sps_assessment()


        # Plan part
        add_string += self.static_plan()
        add_string += self.fn.start_new_medication('vancomycin', 'cefepime') + '\n'
        if self.check_sepsis is not None:
            add_string += self.sepsis.sps_plan()

        return add_string"""





class Sepsis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Sepsis", MCI=MCI)


        self.fn = MCI

        # Get all the medical conditions found in the text
        self.diseases = self.fn.medical_conditions()

        

    
    def immunocompromised(self):

        "drugs"
        "conditions"
        pass



    def sepsis_assessment(self):
        """
        This method identifies if sepsis is present and, if so, determines the cause.
        
        Returns:
            str: A string indicating sepsis along with the cause, if identified.
                If the source is not identified, it returns "Sepsis due to unknown source***".
        """
        
        # Causes of sepsis; INPUT OTHER CAUSES
        conditions_causing_sepsis = [
            'Pneumonia', "Urinary tract infection", "Acute pyelonephritis",
            "Clostridium difficile", "Acute cholecystitis", "Ascending cholangitis",
            "Cellulitis", "Diabetic ulcer", "Febrile neutropenia", "Acute osteomyelitis"
        ]

        # Check if any of the causes above is found in the text
        sepsis_conditions = [i for i in conditions_causing_sepsis if i in self.diseases]

        # Print sepsis due to
        if sepsis_conditions:
            # If causes are found, construct the name accordingly
            self.name = f"Sepsis due to {', '.join(sepsis_conditions).lower()}"
        else:
            # If no causes are found, label it as sepsis from unknown source
            self.name = "Sepsis due to unknown source***"





    
    def __str__(self):

        # variables including temp, BP, lactate, HR, WBC and if any organ dysfunction is present
        labs = {
            "Lactate": self.fn.lab_value('LACTATE'),
            'WBC': self.fn.lab_value('WBC'),
            'Creat.': self.fn.lab_value('CREAT'),
            'Tot. Bili.': self.fn.lab_value('BILITOTAL'),
            'PLT': self.fn.lab_value('PLT'),
            'INR': self.fn.lab_value('INR'),
            'BP': self.fn.get_single_vital('BP'),
            "HR": self.fn.get_single_vital("Pulse"),
            "Temp": self.fn.get_single_vital("Temp"),
            "Organ dysfunction due to sepsis": ['Acute respiratory failure', "Hypotension", "Acute kidney injury", "Altered mental status"]
        }



        add_string = [self.static_assessment()]

        vitals = f"Vitals: BP: {labs['BP']} mmHg, HR: {labs['HR']} bpm, and Temp {labs['Temp']}"



        if labs['WBC']:
            add_string.append(f"WBC: {labs['WBC']} K/uL ")

        if labs['Lactate']:
            if labs['Lactate'] <= 2:
                add_string.append(f"Lactate: {labs['Lactate']} mmol/L")

        if labs['Lactate']:
            if labs['Lactate'] > 2:
                add_string.append(f"  Lactate: {labs['Lactate']} mmol/L ")

        if labs['Creat.']:
            if labs['Creat.'] > 2:
                add_string.append(f"  Creat.: {labs['Creat.']} mg/dL ")

        if labs['Tot. Bili.']:
            if labs['Tot. Bili.'] > 2:
                add_string.append(f"  Tot. Bili.: {labs['Tot. Bili.']} mg/dL ")

        if labs['PLT']:
            if labs['PLT'] < 100:
                add_string.append(f"  PLT: {labs['PLT']} K/uL ")

        if labs['INR']:
            if labs['INR'] > 1.5:
                add_string.append(f"  INR: {labs['INR']}")

        organ_dysfunction = [i for i in labs['Organ dysfunction due to sepsis'] if i in self.diseases]

        if organ_dysfunction != []:
            add_string.append("Organ dysfunction: " + ','.join(organ_dysfunction))


        add_string.append(self.static_plan())

        if "Prolonged qt" in self.diseases:
            add_string.append("– Antibiotics: *** [Prolonged QT]")
        else:
            add_string.append("– Antibiotics: ***")

        add_string.append(self.fn.type_of_fluids())

        if labs['Lactate']:
            if labs['Lactate'] > 2:
                add_string.append('– Repeat lactic acid')

        return utils.remove_empty_lines(add_string)
    
class InfectionBase(disease.Disease):
    """
    Base for focal infections: caches disease list, integrates Sepsis2_0 and common __str__ logic.
    """
    def __init__(self, name, MCI, antibiotics=None):
        super().__init__(name, MCI=MCI)
        self.fn = MCI
        self.diseases = MCI.medical_conditions()
        self.sepsis = Sepsis2_0(file_contents=MCI.file_contents)
        self.antibiotics = antibiotics or []

    def __str__(self):
        # Prepend sepsis label if present
        self.name = self.sepsis.check_for_sepsis() + self.name
        parts = [
            self.static_assessment(),
            self.sepsis.sps_assessment(),
            self.static_plan()
        ]
        if self.antibiotics:
            parts.append(self.fn.start_new_medication(*self.antibiotics))
        parts.append(self.sepsis.sps_plan())
        return utils.remove_empty_lines(parts)
    

# class Cellulitis(InfectionBase):
#     """
#     Handles cellulitis and sepsis secondary to skin infections.
#     """
#     def __init__(self, name, MCI):
#         # Determine if documented sepsis due to cellulitis
#         diseases = MCI.medical_conditions()
#         if 'sepsis' in [d.lower() for d in diseases] and 'cellulitis' in [d.lower() for d in diseases]:
#             base_name = 'Sepsis due to cellulitis'
#         else:
#             base_name = name
#         super().__init__(base_name, MCI, antibiotics=['vancomycin', 'cefepime'])

#     def __str__(self):
#         # Prefix with any sepsis warning
#         self.name = self.sepsis.check_for_sepsis() + self.name
#         parts = [
#             self.static_assessment(),
#             self.sepsis.sps_assessment(),
#             self.static_plan(),
#             self.fn.start_new_medication('vancomycin', 'cefepime'),
#             self.sepsis.sps_plan()
#         ]
#         return utils.remove_empty_lines(parts)

class SkinInfections(InfectionBase):
    """
    Handles cellulitis and sepsis secondary to skin infections.
    """
    def __init__(self, name, MCI):
        # Determine if documented sepsis due to cellulitis
        diseases = MCI.medical_conditions()
        if 'sepsis' in [d.lower() for d in diseases] and 'cellulitis' in [d.lower() for d in diseases]:
            base_name = 'Sepsis due to cellulitis'
        else:
            base_name = name
        super().__init__(base_name, MCI, antibiotics=['vancomycin', 'cefepime'])

    def __str__(self):
        # Prefix with any sepsis warning
        self.name = self.sepsis.check_for_sepsis() + self.name
        parts = [
            self.static_assessment(),
            self.sepsis.sps_assessment(),
            self.static_plan(),
            self.fn.start_new_medication('vancomycin', 'cefepime'),
            self.sepsis.sps_plan()
        ]
        return "".join(parts)
    

class DiabeticUlcer(disease.Disease):

        def __init__(self, name, MCI):
            super().__init__("Diabetic ulcer", MCI=MCI)
            self.fn = MCI
            self.diseases = self.fn.medical_conditions() # this returns a list of all the diseases

            # Call instance of sepsis 2.0
            self.sepsis = Sepsis(file_contents=MCI.file_contents) ### WORKS

            self.check_sepsis = [i for i in self.diseases if i == "Sepsis"]


                
            
        def __str__(self):

            # Check if patient is septic
            if "Sepsis" in self.diseases:
                self.name = "Sepsis due to " + self.name.lower()

            add_string = self.static_assessment()

            # Add sepsis assesment to the assessment for diabetic ulcer
            if self.check_sepsis is not None:
                add_string += self.sepsis.sps_assessment()

            if "Peripheral arterial disease" in self.diseases:
                add_string += "– Patient has PAD: Vascular study ***" + '\n'
            

            add_string += self.static_plan()

            # Add sepsis plan to the plan for diabetic ulcer
            if self.check_sepsis is not None:
                add_string += self.sepsis.sps_plan()

            # Start vancomycin and cefepime as empiric treatment    
            add_string += self.fn.start_new_medication('vancomycin', 'cefepime')

            return add_string
        
class AcuteCholecystitis(disease.Disease):

        def __init__(self, name, MCI):
            super().__init__('Acute cholecystitis', MCI=MCI)
            self.fn = MCI
            self.diseases = self.fn.medical_conditions() # this returns a list of all the diseases

            # Import sepsis class
            self.sepsis = Sepsis2_0(file_contents=MCI.file_contents)

        def __str__(self):

            self.name = self.sepsis.check_for_sepsis() + self.name

            add_string = self.static_assessment()

            add_string += self.sepsis.sps_assessment()

            add_string += self.static_plan()

            add_string += self.fn.start_new_medication('cefepime', 'metronidazole') + '\n'

            add_string += self.sepsis.sps_plan()

            return add_string

class Diverticulitis(disease.Disease):

        def __init__(self, name, MCI):
            super().__init__("Diverticulitis", MCI=MCI)

            self.fn = MCI

            self.diseases = self.fn.medical_conditions() # this returns a list of all the disease

            # Import sepsis class
            self.sepsis = Sepsis2_0(file_contents=MCI.file_contents)


        def __str__(self):
            
            self.name = self.sepsis.check_for_sepsis() + self.name

            add_string = self.static_assessment()

            add_string += self.sepsis.sps_assessment()

            add_string += self.static_plan()

            add_string += self.sepsis.sps_plan()

            add_string += self.fn.start_new_medication('cefepime', 'metronidazole') + '\n'

            return add_string


class NeutropenicFever(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Neutropenic fever', MCI=MCI)

        self.sepsis = Sepsis2_0(file_contents=MCI.file_contents)

    
    def __str__(self):

        # Check if sepsis is present or not
        self.name = self.sepsis.check_for_sepsis() + self.name.lower()

        # Add assessment for neutropenic fever
        """
        Etiology:
            urinalysis
            chest xray
            diarrhea
            viral panel
        
        """
        add_string = self.static_assessment()

        add_string += self.sepsis.sps_assessment()

        add_string += self.static_plan()

        add_string += self.fn.start_new_medication('vancomycin', 'cefepime') + '\n'

        add_string += self.sepsis.sps_plan()

        return add_string




text_input = """

 is a 66 y.o. male



Complete blood count


Lab Results
Component   Value   Date/Time
    WBC 9.5 04/19/2024 05:38 AM
    RBC 3.61 (L)    04/19/2024 05:38 AM
    HGB 10.1 (L)    04/19/2024 05:38 AM
    HGB 12.3 (L)    04/03/2024 10:13 AM
    HCT 32.5 (L)    04/19/2024 05:38 AM
    MCV 90.0    04/19/2024 05:38 AM
    MCH 28.0    04/19/2024 05:38 AM
    MCHC    31.1    04/19/2024 05:38 AM
    PLT 114 (L) 04/19/2024 05:38 AM
    PLT 115 (L) 04/03/2024 10:13 AM
    RDW 15.9 (H)    04/19/2024 05:38 AM
    NEUTROPHIL  6.19    04/19/2024 05:38 AM
    LYMPHOCYTE  1.61    04/19/2024 05:38 AM
    EOSINOPHIL  0.08    04/19/2024 05:38 AM



Chemistry
Lab Results
Component   Value   Date/Time
    NA  134 (L) 04/19/2024 05:38 AM
    K   3.4 (L) 04/19/2024 05:38 AM
    CL  98  04/19/2024 05:38 AM
    CO2 22  04/19/2024 05:38 AM
    CA  8.3 (L) 04/19/2024 05:38 AM
    CA  8.7 (L) 04/03/2024 09:43 AM
    BUN 57 (H)  04/19/2024 05:38 AM
    CREAT   3.99 (H)    04/19/2024 05:38 AM
    GFR 16 (L)  04/19/2024 05:38 AM
    GFR 18 (L)  04/03/2024 09:43 AM
    GLUCOSE 150 (H) 04/19/2024 05:38 AM
    TOTALPROTEIN    6.8 04/03/2024 09:43 AM
    ALBUMIN 3.1 (L) 04/19/2024 05:38 AM
    BILITOTAL   1.0 04/03/2024 09:43 AM
    LIPASE  51  01/06/2020 02:53 PM
    AMYLASE 54  01/06/2020 02:53 PM
    AMMONIA 15.9 (L)    04/04/2022 09:53 AM
    URICACID    6.2 04/12/2021 09:00 AM
    URICACID    10.0 (H)    07/31/2020 01:49 PM
    ALKPHOS 102 04/03/2024 09:43 AM
    ALKPHOS 92  04/02/2024 12:51 PM
    AST 19  04/03/2024 09:43 AM
    ALT 13  04/03/2024 09:43 AM
    ANIONGAP    14  04/19/2024 05:38 AM
    MG  1.7 08/10/2023 12:01 PM
    MG  2.2 12/31/2021 03:11 AM
    PO4 3.0 04/19/2024 05:38 AM
    LACTATE 1.9 04/03/2024 11:23 AM



Cardiac profile


Lab Results
Component   Value   Date/Time
    BASETROP    122 (HH)    12/08/2023 12:18 PM
    BASETROP    113 (HH)    08/10/2023 12:01 PM
    2HRTROP 115 (HH)    12/08/2023 02:39 PM
    2HRTROP 107 (HH)    08/10/2023 02:53 PM
    DELTA   -3  12/28/2021 04:12 AM
    DELTA   -1  12/27/2021 11:08 PM
    6HRTROP 110 (HH)    12/08/2023 06:26 PM
    6HRTROP 97 (H)  08/10/2023 07:49 PM
    PROBNPNTERMI    28,240 (H)  04/02/2024 12:51 PM
    PROBNPNTERMI    6,438 (H)   12/08/2023 12:18 PM
    DDIMERQUANT 0.75 (H)    12/14/2021 05:54 PM
    INR 1.1 12/09/2023 06:02 PM
    PT  14.3    12/09/2023 06:02 PM
    APTT    28.9    12/12/2023 07:17 AM



workup
Lab Results
Component   Value   Date/Time
    IRON    42 (L)  01/07/2022 04:27 AM
    IRON    85  08/10/2020 09:45 AM
    TIBC    178 (L) 01/07/2022 04:27 AM
    TIBC    243 (L) 08/10/2020 09:45 AM
    IRONPERCENT 24  01/07/2022 04:27 AM
    IRONPERCENT 35  08/10/2020 09:45 AM
    FERRITIN    392.8   01/07/2022 04:27 AM
    FERRITIN    101.7   11/08/2019 10:15 AM
    VITAMINB12  309 02/09/2018 09:09 AM
    VITAMINB12  173 (L) 08/31/2017 06:10 AM
    FOLATE  5.6 08/31/2017 06:10 AM



Lab Results
Component   Value   Date/Time
    PHUA    7.0 04/04/2022 11:53 AM
    SGUR    1.011   04/04/2022 11:53 AM
    URINELEUKOC Negative    04/04/2022 11:53 AM
    NITRITEUA   Negative    04/04/2022 11:53 AM
    KETONEURINE Negative    04/04/2022 11:53 AM
    PROTEINUA   1+ (A)  04/04/2022 11:53 AM
    GLUUA   Negative    04/04/2022 11:53 AM
    BLOODUA Negative    04/04/2022 11:53 AM
    WBCU    0-2 04/04/2022 11:53 AM
    RBCUA   0-2 04/04/2022 11:53 AM
    BACTERIAUA  1+ (A)  04/04/2022 11:53 AM
    UREPITHELIAL    0-5 12/30/2021 03:16 PM



Lab Results
Component   Value   Date/Time
    CRP 162.7 (H)   04/02/2024 05:14 PM



Lab Results
Component   Value   Date/Time
    PHBLOODPOC  7.43    08/10/2023 12:45 PM
    PCO2POC 27 (L)  08/10/2023 12:45 PM
    PO2POC  94  08/10/2023 12:45 PM
    PFRATIO 367 04/04/2022 01:48 PM
    O2SATPOC    100 (H) 08/10/2023 12:45 PM



Lab Results
Component   Value   Date/Time
    INFLUENZAA  Not Detected    10/27/2023 12:10 AM
    INFLUENZAB  Not Detected    10/27/2023 12:10 AM
    COVID19 Not Detected    04/02/2024 05:36 PM
    RSVAG   Not Detected    10/27/2023 12:10 AM



Lab Results
Component   Value   Date/Time
    HGBA1C  5.8 (H) 08/10/2023 11:43 AM
    LDLCALC 50  08/24/2023 10:58 AM



Lab Results
Component   Value   Date/Time
    TRIGLYCERIDE    107 08/24/2023 10:58 AM
    TSH 1.60    04/04/2022 09:53 AM



No results found for: "AMPHETAMINEQ", "BARBITQLUR", "BENZDIAQLUR", "CANNABQLUR", "COCAINEQUAL", "METHADONEU", "OPIATEQUA", "OXYCODQLUR", "PHENCYCLID"


Toxicology
Lab Results
Component   Value   Date/Time
    ETHANOL <10.10  04/04/2022 09:53 AM
    ETHANOL <0.01   04/04/2022 09:53 AM



Vitamins
Lab Results
Component   Value   Date/Time
    VITAMINDTO  25 (L)  02/05/2021 09:05 AM



Tumor markers
No results found for: "AFPTM"


Virology
Lab Results
Component   Value   Date/Time
    HEPAIGM Non-reactive    01/01/2022 06:12 PM
    HEPBCORIGM  Non-reactive    01/01/2022 06:12 PM
    HEPBSAG Non-reactive    01/01/2022 06:12 PM
    HEPCAB  Non-reactive    01/01/2022 06:12 PM
 



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
 
cellulitis
hyponatremia
Vitals:
    04/04/24 1900
BP: 127/79
Pulse:  91
Resp:   20
Temp:   101
SpO2:   97%


insulin lispro


Prior to Admission Medications
Prescriptions   Last Dose   Informant   Patient Reported?   Taking?
Blood-Glucose Meter,Continuous (Dexcom G4 Receiver-Share Kit)           No  No
Sig: Use as directed to monitor blood sugar
Blood-Glucose Sensor (Dexcom G6 Sensor) Device          No  No
Sig: Use as directed to monitor blood sugars
Blood-Glucose Transmitter (Dexcom G6 Transmitter) Device            No  No
Sig: Use as directed to monitor blood sugars
FLUoxetine (PROzac) 40 mg capsule   3/31/2024       No  No
Sig: Take 1 Capsule (40 mg) by mouth daily.
Insulin Needles, Disposable, (UltiCare Pen Needle) 31 gauge x 3/16" Needle          No  No
Sig: USE AS DIRECTED DAILY FOR INSULIN INJECTION. MAX DAILY AMOUNT 4
Insulin 100 unit/mL (3 mL) solution for injection   3/31/2024       No  No
Sig: Inject 20 Units by subcutaneous injection late in the day. Max Daily amount 60 units
RenaPlex-D 800 mcg-12.5 mg -2,000 unit Tablet           Yes No
Sig: Take 1 Tablet by mouth daily.
allopurinoL (ZYLOPRIM) 100 mg tablet    3/31/2024       No  No
Sig: TAKE 1 TABLET BY MOUTH EVERY DAY
apixaban (Eliquis) 5 mg tablet  3/31/2024       No  Yes
Sig: TAKE 1 TABLET BY MOUTH TWICE DAILY
bumetanide (BUMEX) 2 mg tablet  3/31/2024       No  No
Sig: TAKE 2 TABLETS BY MOUTH EVERY MORNING and TAKE 1 TABLET EVERY
cpap medical device         No  No
Sig: CPAP (E0601) at 12 cm/H2O with heated humidifier (E0562), nasal pillow/cradle and headgear A7034,A7035 1/6mo, Mask only A7034 1/3mo, Pillows A7033 2/mo.  Also supply heated tubing A4604 1/3mo,water chamber A7046 1/6mo,filter disp A7038 2/mo,Reusable filter A7039 1/6mo, Chin strap A7036 a/6mo LON 99mo DX: OSA (G47.33)
fluticasone propionate (FLONASE) 50 mcg/spray Spray, Suspension nasal inhaler           No  No
Sig: Administer 2 Sprays in each nostril daily.
gabapentin (NEURONTIN) 300 mg capsule   3/31/2024       No  No
Sig: TAKE 1 CAPSULE BY MOUTH EVERY NIGHT AT BEDTIME AS DIRECTED
metoprolol tartrate (LOPRESSOR) 25 mg tablet    4/1/2024        No  Yes
Sig: take 1 tablet by mouth twice daily
mirtazapine (REMERON) 15 mg tablet  3/31/2024       No  No
Sig: Take 1 Tablet (15 mg) by mouth daily at bedtime.
naratriptan (AMERGE) 2.5 mg tablet          No  No
Sig: TAKE 1 TABLET BY MOUTH DAILY AS NEEDED FOR MIGRAINE
ondansetron (ZOFRAN) 4 mg Tablet            Yes No
Sig: Take 4 mg by mouth every 6 hours as needed.
sevelamer carbonate (RENVELA) 800 mg Tablet 4/1/2024        Yes Yes
Sig: Take 800 mg by mouth daily.
simvastatin (ZOCOR) 40 mg tablet    3/31/2024       No  No
Sig: Take 1 Tablet (40 mg) by mouth daily at bedtime.
tiZANidine (ZANAFLEX) 2 mg Tablet           No  No
Sig: Take 1 Tablet (2 mg) by mouth every 6 hours as needed for Spasm.


Facility-Administered Medications: None



Current Facility-Administered Medications
Medication  Dose    Route   Frequency   Provider    Last Rate   Last Admin
•   [COMPLETED] vancomycin (VANCOCIN) 500 mg in sodium chloride 0.9% 100 mL IVPB (MBP)   500 mg IV  ONE time only   Haddow, Alastair D, MD      Stopped at 04/04/24 1529
•   tiZANidine (ZANAFLEX) tablet 2 mg    2 mg   Oral    ONE time only   Corum, Laura Michelle, FNP       
•   heparin injection 7,500 Units    7,500 Units    subCUT  every 8 hours   Virji, Narius Aresh, MD     7,500 Units at 04/04/24 1426
•   [COMPLETED] tiZANidine (ZANAFLEX) tablet 2 mg    2 mg   Oral    ONE time only   Corum, Laura Michelle, FNP      2 mg at 04/03/24 2332
•   [Held by Provider] apixaban (ELIQUIS) tablet 5 mg    5 mg   Oral    BID Zguri, Liridon, MD       
•   FLUoxetine (PROzac) capsule 40 mg    40 mg  Oral    daily   Zguri, Liridon, MD      40 mg at 04/04/24 1100
•   gabapentin (NEURONTIN) capsule 300 mg    300 mg Oral    daily BEDTIME   Zguri, Liridon, MD      300 mg at 04/04/24 2111
•   simvastatin (ZOCOR) tablet 40 mg     40 mg  Oral    daily BEDTIME   Zguri, Liridon, MD      40 mg at 04/04/24 2113
•   naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg     0.1 mg IV  see admin instructions  Zguri, Liridon, MD       
•   acetaminophen (TYLENOL) tablet 650 mg    650 mg Oral    every 6 hours PRN   Zguri, Liridon, MD       
         
•   metoprolol tartrate (LOPRESSOR) tablet 25 mg     25 mg  Oral    BID Zguri, Liridon, MD      25 mg at 04/04/24 2111
•   diltiaZEM in 0.9% sodium chloride (CARDIZEM) 125 mg/125 mL infusion  0-15 mg/hr IV  titrate Zguri, Liridon, MD  5 mL/hr at 04/03/24 1805    5 mg/hr at 04/03/24 1805
•   allopurinoL (ZYLOPRIM) tablet 100 mg     100 mg Oral    daily   Zguri, Liridon, MD      100 mg at 04/04/24 1100
•   dextrose 5% - sodium chloride 0.9% infusion     IV  see admin instructions  Zguri, Liridon, MD       
•   glucagon HCL 1 mg/mL injection 1 mg  1 mg   IM  see admin instructions  Zguri, Liridon, MD       
metformin    
•   dextrose 10% bolus solution 125 mL   125 mL IV  see admin instructions  Zguri, Liridon, MD       
•   dextrose 10% bolus solution 250 mL   250 mL IV  see admin instructions  Zguri, Liridon, MD       


peripheral arterial disease
lymphedema
acute heart failure
atrial fibrillation with rvr
coronary artery disease
alcohol abuse
"""


"""print(Sepsis("Sepsis", MCI=text_input))

print(SkinInfections("Cellulitis", MCI=text_input))

print('')

print(DiabeticUlcer("Diabetic ulcer", MCI=text_input))


print('')

print(Diverticulitis("Diverticulitis", MCI=text_input))"""


#print(DiabeticUlcer("Diabetic ulcer", MCI=text_input).diseases)


# print(Sepsis2_0(file_contents=text_input).sps_assessment())

# master = functions.MasterClass(file_contents=text_input)
# print(AcuteCholecystitis("Acute cholecystitis", MCI=master ))