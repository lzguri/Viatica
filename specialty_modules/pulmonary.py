import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease



class AcuteRespFailure(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__(self, 'Acute respiratory failure', MCI=MCI)


        self.fn = MCI

        self.diseases = self.fn.medical_conditions() # Get all the diseases

        self.PaO2 = self.fn.lab_value('PO2POC') # Get PaO2 level in the blood
        self.pH = self.fn.lab_value('PHBLOODPOC')
        self.PaCO2 = self.fn.lab_value('PCO2POC')

        "if pH < 7.35 and PaCO2 > 40 mmHg --> Acute respiratory acidosis"

    

        # 1. First determine if its acute respiratory failure or acute on chronic respiratory failure
        if 'Chronic respiratory failure' in self.diseases:
            self.name = "Acute on chronic respiratory failure"

        # 2. Determine the etiology of the respiratory failure

            # Pulmonary causes of respiratory failure
        pulmonary_causes = ["COPD exacerbation", "Asthma exacerbation", "Pneumonia", "Obesity hypoventilation syndrome", 
                            'Atelectasis', "Acute pulmonary embolism", "COVID-19", "Influenza", "Pleural effusion", 
                            'ILD exacerbation']

            # Cardiac causes of respiratory failure
        cardiac_causes = ["Acute heart failure"]

        arf_secondary_to = [disease for disease in pulmonary_causes + cardiac_causes if self.diseases]

        if arf_secondary_to:
            if len(arf_secondary_to) == 1:
                self.name = self.name + " secondary to " + arf_secondary_to[0]
            else:
                self.name = self.name + "\nSecondary to " + self.fn.format_list(arf_secondary_to)

    # Determine there is acute respiratory failure
    # Either by detecting acute respiratory failure on the text
    # Detect type of acute respiratory failure, hypoxic or hypercapnic
    # Detect if PaO2 < 60 mmgHg  

    def arf_assessment(self):

        return self.static_assessment()
    
    def arf_plan(self):

        add_string = self.static_plan()

        # Oxygen target for patients with COPD exacerbation
        if "COPD exacerbation" in self.name:
            add_string += 'Oxygen suppl. O2 target ~ 88% to 92%'
        else:
            add_string += 'O2 suppl. via ***'

    def need_for_bipap(self):
        """
        Determine need for BiPAP
        check for PaC02 and pH
        
        """
        if self.pH is not None and self.PaCO2 is not None:
            if self.pH < 7.35 and self.PaCO2 > 45:
                return " BiPAP, repeat ABG on BiPAP"



class COPDexac(disease.Disease):

    def __init__(self, name, MCI, display_home_meds=True, full_meds_plan = True):
        super().__init__("COPD exacerbation", MCI=MCI, full_meds_plan = True)

        self.fn = MCI

        arf_determine = AcuteRespFailure("Acute respiratory failure", MCI=MCI)


    def acute_resp_failure(self, type=True):
        # Define acute hypercapnic respiratory failure
        # Defines as: PaCO2 > 45 mm Hg, and pH < 7.35

        ph = self.fn.lab_value('PHBLOODPOC') # Check pH level
        CO2 = self.fn.lab_value('PCO2POC') # Check bicarbonate level

        if type:
            if CO2 and ph:
                if ph < 7.35 and CO2 > 45:
                    return "Acute hypercapnic respiratory failure"
                    


    def __str__(self):

        if self.acute_resp_failure(self):
            self.name = '\n' + "Acute hypercapnic respiratory failure" + '\n' + self.name

        add_string = self.static_assessment()


        # Check for eosinophilia; phenotypes with eosinophilia have more exacerbation but are more responsive to steroids

        # Check if the patient is on macrolides suppression therapy

        add_string += self.static_plan()

        if self.acute_resp_failure(self):
            add_string += '- BiPAP ***'

        return add_string

        # define acute on chronic respiratory failure

class Asthmaexac(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Asthma exacerbation", MCI=MCI)

        self.fn = MCI

        # Esoinophilia if > 0.7
        self.eosinophils = self.fn.lab_value('EOSINOPHIL')

        if self.eosinophils:
            if self.eosinophils >= 0.7:
                self.assessment['other_assessment'] = self.assessment['other_assessment'] + '\n' + 'High Eosinophils'

    
    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.static_plan()

        return add_string

class ILDexac(disease.Disease):

    """NOT COMPLETED YET"""

    def __init__(self, name, MCI):
        super().__init__('ILD exacerbation', MCI=MCI)

        # This class should include all the DPLD; diffuse parenchymal lung disease

        self.fn = MCI
        self.all_diseases = self.fn.medical_conditions()



    def __str__(self):

        add_string = self.static_assessment()

        # Assess ability to check A-a gradient automatically, which will be elevated in DPLD

        # HRCT findings

        # PFTs and DLCO in ILD; PFTs will show restrictive pattern, DLCO will be decreased, Vital capacity will be decreased

        # Medications that cause pulmonary fibrosis: Bleomycin, Amiodarone, Methotrexate
        fibrosis_meds_caution = self.fn.find_medications_by_cautions('Pulmonary fibrosis', only_meds_list=True)

        fibrosis_meds_contra = self.fn.find_medications_by_contraindication('Pulmonary fibrosis', only_meds_list=True)

        fibrosis_meds = fibrosis_meds_caution + fibrosis_meds_contra

        if fibrosis_meds:
            add_string += f"Patient is on {', '.join(fibrosis_meds)} which might be contributing to fibrosis" + '\n'

        # Asses for GERD presence and if its being treated
        GERD_rx = self.fn.find_medications_by_indication('Gastroesophageal reflux disease', only_meds_list=True)

        if "GERD" in self.all_diseases:
            if GERD_rx:
                add_string += f"Patient has GERD, Rx with {', '.join(GERD_rx)}"  + '\n'
            else:
                add_string += f"Patient has GERD and is not on any Rx for it" + '\n'


        add_string += self.static_plan()

        return add_string

class Pleuraleffusion(disease.Disease):

    """NOT COMPLETED YET"""

    def __init__(self, name, MCI):
        super().__init__('Pleural effusion', MCI=MCI)


        self.fn = MCI

        self.all_diseases = self.fn.medical_conditions() # with a history of CAP, Pneumonia, AKI, CHF, CHF, , GERD, GERD, Nephrotic syndrome, Nephrotic syndrome, Pleural effusion, and Acute pancreatitis

        # If patient is on diuretics there is a possiblity transudate might be missclassified to exudate

        self.diuretics = self.fn.find_medications('Diuretics, Loop', _list_only=True)

    def __str__(self):

        add_string = self.static_assessment()

        # Conditions that cause exudate
        exudate = ['Pneumonia', 'Acute pulmonary embolism', 'Acute pancreatitis', 'Cancer', 'Abscess', 'Mesothelioma']

        exudate_list = [i for i in exudate if i in self.all_diseases]

        if exudate_list:
            add_string += f'Possible exudative causes: {", ".join(exudate_list)} ***' + '\n'

        # Conditions that cause transudate
        transudate = ['Chronic congestive heart failure', 'Acute heart failure', 'Nephrotic syndrome', 'End-stage renal disease', 'Liver cirrhosis']

        transudate_list = [i for i in transudate if i in self.all_diseases]

        if transudate_list:
            add_string += f'Possible transudative causes: {", ".join(transudate_list)} ***' + '\n'

        # Check albumin gradient

        add_string += self.static_plan()

        if self.diuretics:
            add_string += f'- Check albumin/cholesterol level in the effusion and calculate albumin gradient. Pt. is on {", ".join(self.diuretics)}'

        return add_string

class AcutePulmonaryEmbolism(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Acute pulmonary embolism", MCI=MCI)

        self.fn = MCI



    def __str__(self):


        add_string = self.static_assessment()


        add_string += self.static_plan()

        add_string += self.fn.start_new_medication('heparin')

        return add_string
    
class Pneumonia(disease.Disease):

    def __init__(self, name,MCI):
        super().__init__('Pneumonia',MCI=MCI)



    def __str__(self):

        add_string = self.static_assessment()


        add_string += self.static_plan()

        return add_string

class COVID19(disease.Disease):

    def __init__(self, name,MCI):
        super().__init__('COVID-19',MCI=MCI)


    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.static_plan()


        return add_string
    
class LungAbscess(disease.Disease):

    def __init__(self, name,MCI):
        super().__init__('Lung abscess',MCI=MCI)

        self.fn = functions.MasterClass(file_contents=file_contents)

        self.all_diseases = self.fn.PMH_abbreviations(all_disease=True)

        # Conditions that can predispose to lung abscess: (1) Dysphagia and (2) Impaired consciousness

        self.aspiration_conditions = ["Dysphagia", 'Alcohol use disorder', 'Aspiration pneumonia', 'Dementia', 'CVA']


    def __str__(self):

        add_string = self.static_assessment()

        

        # If IVDU, make sure to rule out endocarditis which can be a cause of septic emboli to the lung

        add_string += self.static_plan()

        # If pleural effusion perform thoracentesis to rule out empyema

        if 'Pleural effusion' in self.all_diseases:
            add_string += '- Thoracentesis to rule out empyema [effusion present]'


        return add_string


class Pneumothorax(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Pneumothorax", MCI=MCI)

    
    def __str__(self):


        add_string = self.static_assessment()

        add_string = self.static_plan()


        return add_string



text_input = """
furosemide
ILD exacerbation
Gastroesophageal reflux disease
methotrexate
Pleural effusion
pneumonia
acute pancreatitis
breast cancer
chronic congestive heart failure
nephrotic syndrome
COPD exacerbation
"""


#obj1 = AcuteRespFailure(file_contents=text_input)

#print(obj1.acute_resp_failure())