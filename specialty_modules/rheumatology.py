
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import disease
import functions


class Vasculitis(disease.Disease):

    def __init__(self, name, file_contents):
        super().__initi__("Vasculitis", file_contents=file_contents)

        self.fn = functions.MasterClass(file_contents=file_contents)

        self.all_diseases = self.fn.medical_conditions()

    """
    Plan for vasculitis
    - ANCA (p and c)
    - ESR/CRP
    - ANA w reflex
    - Complement level
    - HIV, HBV serology, HCV serology
    - Urinalysis
    - Rheumatology consult
    - Possible skin biopsy
    """

    small_vessel_vasculitis = ["Granulomatosis with polyangiitis", "Microscopic polyangiitis", "Eosinophilic granulomatosis with polyangiitis", "IgA vasculitis"]
    medium_vessel_vasculitis = ["Polyarteritis nodosa", "Kawasaki disease", "Buerger disease"]
    large_vessel_vaculitis = ["Giant cell arteritis", "Takayasu arteritis"]
    other_form_vasculitis = []


    def __str__(self):


        add_string = self.static_assessment()


        add_string += self.static_plan()


        return add_string

