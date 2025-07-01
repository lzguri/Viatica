
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease


class Encephalopathy(disease.Disease):


    def __init__(self, name, MCI):
        super().__init__("Altered mental status", MCI=MCI)

        self.fn = MCI


    def __str__(self):

        add_string = self.static_assessment()
        
        add_string += self.static_plan()


        return add_string


class CVA(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Acute cerebrovascular accident", MCI=MCI, display_home_meds=True, full_meds_plan=True)

        self.fn = MCI
        self.diseases_present = self.fn.medical_conditions()

        embolic_stroke_info = []

        self.get_inr_level = self.fn.lab_value('INR')

        embolism = ["Atrial fibrillation", "Atrial flutter", "Atrial fibrillation with RVR", "Atrial flutter with RVR", "Infective endocarditis"]
        self.embolism_risk = [i for i in embolism if i in self.diseases_present]

        

        anticoagulation = ['warfarin', 'apixaban', 'rivaroxaban', "dabigatran", "endoxaban"]
        self.anticoagulants = self.fn.find_all_medications()

        is_anticoagulation = [i.lower() for i in anticoagulation if i.lower() in self.anticoagulants]

        if self.embolism_risk:
            embolic_stroke_info.extend([f'Patient with {self.embolism_risk[0].lower()}'])

            if is_anticoagulation:
                embolic_stroke_info.extend([f" and is on {is_anticoagulation[0]}"])
                
                # Check for INR level only if patient is on warfarin
                if is_anticoagulation[0] == 'warfarin':
                    inr_level = self.get_inr_level  # Assuming you have a method to get INR level
                    
                    # Check if INR level is available
                    if inr_level is not None:
                        if inr_level > 2:
                            embolic_stroke_info.extend([" and INR is therapeutic"])
                        else:
                            embolic_stroke_info.extend([" but INR is subtherapeutic"])
                    else:
                        embolic_stroke_info.extend([" - INR level pending"])
            else:
                embolic_stroke_info.extend([" and NOT on anticoagulation"])

            self.assessment['other_assessment'] += f"\n{''.join(embolic_stroke_info)}"


    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.fn.start_new_medication('aspirin') + '\n'
        #add_string += self.fn.start_new_medication('atrovastatin') + '\n'
        add_string += self.fn.start_new_medication('clopidogrel') + '\n'
    

        add_string += self.static_plan()

        return add_string


class AcuteNeuropathy(disease.Disease):

    """
    TSH
    Vitamin b12
    HGBA1c
    Serum immunofixation
    alcohol abuse 
    chemotherapy - on cancer patients
    HIV
    """



    pass

class MyastheniaCrisis(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Myasthenia Crisis", MCI=MCI, display_home_meds=True, full_meds_plan=True)

        """
        Infection can make it worse
        
        """


    
    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.static_plan()


        return add_string


class BackPain(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Back pain', MCI=MCI)

        self.fn = MCI

    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.static_plan()

        return add_string
    

class BrainMass(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Brain mass', MCI=MCI)

        self.fn = MCI

        self.diseases = self.fn.medical_conditions()


    def __str__(self):

        add_string = self.static_assessment()

        add_string += self.static_plan()

        add_string += self.fn.start_new_medication("dexamethasone") + " *** concern for lymphoma"

        return add_string



file_contents = """

atrial fibrillation
aspirin
atorvastatin
clopidogrel
bleeding
rhabdomyolysis
atrial fibrillation
warfarin

"""
# MCI = functions.MasterClass(file_contents=file_contents)
# CVA_obj = BrainMass("Brain mass", MCI=MCI)

# print(CVA_obj)