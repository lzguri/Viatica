
import drug_reference as drugs, functions, disease_reference as disr

class ID(functions.MasterClass):
    '''CLASS VARIABLES'''

    def __init__(self, file):
        super().__init__(file)
        self.assess_start = f"""
        C/o ***
        Previous episodes ***
        Previous cultures ***
        """
        self.sepsis_cond = disr.InfectiousDisease_AD['Sepsis']
        self.prolonged_qt_cond = disr.Cardiology['Prolonged QT']
        self.infectious_wu = ['WBC', 'LACTATE']
        self.inflammatory_wu = ['ESR', 'CRP', 'PROCALCITONIN']
        self.immunosuppression_disr = ['HIV', 'SLE', 'Lupus'] #TODO
        #could state 'no recent abx', or 'recently on cefapime'. TODO    opportunistic infection for those w/ weak immune systems, things like [HIV, Lupus ("SLE"), ]
        self.antibiotics_drugs = ['Aminoglycosides', 'Carbapenems', 'Cephalosporins', 'Fluoroquinolones', 'Lincosamide', 'Lipopeptides', 'Macrolides', 'Monobactams', 'Nitroimidazole', 'Oxazolidinones', 'Penicillins', 'Polypeptides', 'Rifamycins', 'Suflonamides', 'Sulfone', 'Tetracyclines']
        #must flag immunosupression d/t weird presentations of sx. TODO
        self.immunosuppression_drugs = ["Folate Antagonists", "Aminosalicylate", "TNF Inhibitors", "Corticosteroids", "DMARDs", 'JAK Inhibitors']
        #throw in viral test, some done. remember reverse = True
        #Fix abx detection

    def detect_sepsis(self):
        #mind software won't produce problem list
        #must use clinical judgement, not SIRS since it's limited. Sepsis d/t PNA, UTI, 
        return "Sepsis due to " if self.check_name(self.sepsis_cond) else ''

    def lactic_acidosis(self):
        #LA = hypoperfusion, must repeat LA after giving fluids to ensure right direction is ocming , if nl don't care 
        if self.get_test_results( 'LACTATE'):
            if float(self.get_test_results( 'LACTATE', result_only=True)) > 2.0:
                return '- Repeat lactic acid'
            else:
                return ''
        else:
            return ''

    def detect_immunosuppressors(self):
        #Use drug_referance to detect immunosupressants. say pt is on immunosupressants and give name of medicine
        all_immunosupressors = ['Folate Antagonists', 'Aminosalicylate', 'TNF Inhibitors', 'Corticosteroids', 'DMARDs', 'JAK Inhibitors'] 
        
        positive = self.find_medication(all_immunosupressors, dictionary = False, only_meds_list = True)

        if len(positive) >= 1:
            return("- Pt is on immunosupression (" + ", ".join(positive)) + ")"

    def detect_overload(self):
        #Detect HF/ESRD/Anasarca (generalized edema), just say to be cautious when giving fluids in this case. 
        key_words = ['CHF', 'ESRD', 'Anasarca', 'edema']
        positives = self.check_name(key_words, full_list = True)
        if type(positives) == list:
            return "- Consider holding fluids (" + ", ".join(positives) + ")"

    def prolonged_QTC(self):
        #Long QTC will be in the problem list, just bring it up when giving abx. 
        return '[Prolonged QTC]' if self.check_name(self.prolonged_qt_cond) else ''

    
    '''ASSESSMENT'''


    def ID_assess(self):
            return f"""
            {self.get_multiple_test_results(self.infectious_wu)}
            {self.get_multiple_test_results(self.inflammatory_wu)}
            {self.risk_factors(self.immunosuppression_disr)}
            {self.find_medication(self.antibiotics_drugs) if self.find_medication(self.antibiotics_drugs) else 'Recent antibiotic use ***'}
            {self.detect_immunosuppressors()}
            {self.detect_overload()}
            """

    '''PLAN'''

    def ID_plan(self):
        #general plan for each ID.
        return f"""Plan
        {self.check_missing_tests(self.infectious_wu, self.ID_assess())}
        {self.lactic_acidosis()}
        - Star Rx with ***  {self.prolonged_QTC()}
        """

    '''ASSESSMENT & PLAN'''

    def assess_plan(self):
            var = functions.CleanText(self.ID_assess() + '\n' + self.ID_plan())
            return var if var else ''


class Diverticulitis(ID, functions.MasterClass):

    def __init__(self, file):
        super().__init__(file)
        self.divert_synonyms = disr.InfectiousDisease_AD['Diverticulitis']
        self.rf = 'Diverticulosis', 'Constipation',
            

    '''ASSESSMENT'''

    def diverticulitis_assessment(self):
        return f"""{self.detect_sepsis()}Diverticulitis
        {self.assess_start}
        Complicated *** Uncomplicated
        {self.ID_assess()}
        CT abdomen showing ***
        """

    '''PLAN'''

    def diverticulitis_plan(self):
        return f"""
        {self.ID_plan()}
        - [Abscess > 3 cm], CT-guided drainage ***
        - Bowel rest
        - Outpatient recommendation: high-fiber diet, colonoscopy after symptoms resolve [***Patient has not had a colonoscopy within the past year]
        """

    '''ASSESS & PLAN'''

    def diverticulitis_AP(self):
        if self.check_name(self.divert_synonyms):
            var = self.diverticulitis_assessment() + '\n' + self.diverticulitis_plan()
            return '+' + var 
        else:
            ''


class Pneumonia(ID):

    def __init__(self, file):
        super().__init__(file)
        self.pneumo_synonyms = disr.InfectiousDisease_AD['Pneumonia']
        self.respiratory_pcr_wu = 'COVID19', 'INFLUENZAA', 'INFLUENZAB', 'RSVAG',


    def pneumonia_assessment(self):
        return f"""{self.detect_sepsis()}Pneumonia
        {self.assess_start}
        CXR showing ***
        {self.ID_assess()}
        {self.get_multiple_test_results(self.respiratory_pcr_wu)}
        """


    def pneumonia_plan(self):
        return f"""
        {self.ID_plan()}
        - Blood cultures *** [Severe pneumonia/Rx for MRSA, Pseudomonas]
        - Strep urine antigen, Legionella urine antigen [***Severe pneumonia]
        - Sputum culture ***
        - MRSA PCR ***
        """


    def pneumonia_AP(self):
        if self.check_name( self.pneumo_synonyms):
            var = (self.pneumonia_assessment() + '\n' + self.pneumonia_plan())
            return '+' + var 
        else:
            ''


class Osteomyelitis(ID):

    def __init__(self, file):
        super().__init__(file)
        self.osteomyelitis_synonyms = disr.InfectiousDisease_AD['Osteomyelitis']
        self.vertabral_osteomyelitis_synonyms = disr.InfectiousDisease_AD['Vertebral osteomyelitis']
        self.diabetic_foot_ulcer_synonyms = disr.InfectiousDisease_AD['Diabetic foot ulcer']


    def osteomyelitis_assessment(self):
        return f"""{self.detect_sepsis()}Osteomyelitis
        {self.assess_start}
        XR showing ***
        CT showing ***
        {self.get_multiple_test_results(self.inflammatory_wu)}
        {self.ID_assess()}
        
        """


    def osteomyelitis_plan(self):
        return f"""
        {self.ID_plan()}
        {self.check_missing_tests(self.inflammatory_wu, self.osteomyelitis_assessment())}
        - Blood cultures
        - Follow ESR/CRP for response to therapy
        """

    def diabetic_foot_ulcer_plan(self):
        if self.check_name(self.diabetic_foot_ulcer_synonyms):
            return f"""
        - Podiatry consult
        - Arterial doppler of the lower ext.
        """

    def vertebral_osteomyelitis_plan(self):
        if self.check_name(self.vertabral_osteomyelitis_synonyms):
            return f"""
        - MRI of the spine ***
        - Urinalysis/urine culture
        - Start antibiotics with ***  [***sepsis/neurologic deficits/spinal instability/epidural abscess]
        - Neurosurgery consult
        - Infectious disease consult
        - Neurological checks
        """
        else:
            return ''

    f"""
    
    
    """


    def osteomyelitis_AP(self):
        if self.check_name(self.osteomyelitis_synonyms):
            var = (self.osteomyelitis_assessment() + '\n' + self.osteomyelitis_plan())
            return (f"""+{var}
            {self.vertebral_osteomyelitis_plan() if self.vertebral_osteomyelitis_plan() else ''}
            {self.diabetic_foot_ulcer_plan() if self.diabetic_foot_ulcer_plan() else ''}
            """)
        else:
            ''

class UTI(ID, functions.MasterClass):

    def __init__(self, file):
        super().__init__(file)
        self.UTI_synonyms = disr.InfectiousDisease_AD['UTI']
        self.urinalysis_wu = 'WBCU', 'RBCUA', 
        self.urinalysis_reverse_wu = 'URINELEUKOC', 'BACTERIAUA', 'NITRITEUA',


    def UTI_assessment(self):
        return f"""{self.detect_sepsis()}UTI
        {self.assess_start}
        {self.ID_assess()}
        {'Urinalysis is showing ' + self.get_multiple_test_results(self.urinalysis_wu) if self.get_multiple_test_results(self.urinalysis_wu) else ''} {self.get_multiple_test_results(self.urinalysis_reverse_wu)}
        """


    def UTI_plan(self):
        return f"""
        {self.ID_plan()}
        - Blood cultures *** 
        - Urine cultures

        """


    def UTI_AP(self):
        if self.check_name(self.UTI_synonyms):
            var = (self.UTI_assessment() + '\n' + self.UTI_plan())
            return '+' + var 
        else:
            ''



with open('file.txt', 'r') as f:
    file1 = f.read()


div1 = UTI(file1)
print(div1.UTI_AP())