import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import functions
import disease
import utility_function as utils



class AcutePancreatitis(disease.Disease):
    """
    Acute Pancreatitis Disease Class
    """

    def __init__(self, name, MCI):
        super().__init__("Acute Pancreatitis", MCI=MCI, display_home_meds=True, full_meds_plan=True)
        self.fn = MCI
        self.diseases_present = self.fn.medical_conditions() # List of medical conditions present in the patient

        self.lipase_level = self.fn.lab_value('LIPASE') if self.fn.lab_value('LIPASE') != None else ""# Assuming this function retrieves the lipase level

        self.calcium_level = self.fn.lab_value('CA') # Retrieving calcium level from lab results

        self.calcium_abnormal = self.fn.abnormality_name('CA', _lazy_mode=True) # Checking if calcium level is abnormal

    def __str__(self):
        self.name = "Acute Pancreatitis" + "\n"

        self.name += f"Epigastric pain ***, Lipase Level: {self.lipase_level}, CT finding ***"+ "\n"
        add_string = self.static_assessment() # Static assessment acute pancreatitis, retrived from acute_conditions.csv, column assessment
        add_string += self.static_plan()
        return utils.remove_empty_lines(add_string)
    



patient_data = """
is a 56 y.o. male


Lab Results
Component	Value	Date/Time
	WBC	8.3	12/15/2022 07:50 AM
	BASETROP	34	12/20/2022 07:50 AM
	2HRTROP	34	12/20/2022 07:50 AM
	HGB	13.3 (L)	12/16/2022 07:50 AM
	HGB	14.4	10/16/2022 06:46 AM
	TG	43.2	12/16/2022 07:50 AM
	PLT	265	12/16/2022 07:50 AM
	MCV	80.6	12/16/2022 07:50 AM
	NA	139	12/16/2022 07:49 AM
	COVID19	Not Detected	12/15/2022 05:01 PM
	INFLUENZAA	Not Detected	11/28/2022 05:01 PM
	INFLUENZAB	Not Detected	11/28/2022 05:01 PM
	RSVAG	Not Detected	11/28/2022 05:01 PM
	CREAT	2.04	12/15/2022 07:49 AM
	K	2.04	12/20/2022 07:49 AM
	TSH	2.04	12/20/2022 07:49 AM
	MG	2.04	12/17/2022 07:49 AM
	CREAT	1.07	10/16/2022 06:46 AM
	CA	16 (H)	06/29/2025 07:49 AM
    LIPASE	161 (H)	06/29/2025 07:49 AM
	TOTALPROTEIN	7.7	10/17/2022 07:49 AM
	ALBUMIN	3.7	12/16/2022 07:49 AM
	BILITOTAL	0.4	10/17/2022 07:49 AM
	ALKPHOS	86	12/17/2022 07:49 AM
	AST	17	12/17/2022 07:49 AM
	ALT	11	12/17/2022 07:49 AM
	ANIONGAP	12	10/17/2022 07:49 AM
	GFR	>60	12/17/2022 07:49 AM
	2HRTROP	21 	10/16/2022 02:22 AM
	HGBA1C	4.7 	10/16/2022 02:22 AM
	
	PROBNPNTERMI	1200	10/13/2015

"""


master_class = functions.MasterClass(patient_data)

pancreatitis = AcutePancreatitis("Acute Pancreatitis", MCI=master_class)

print(master_class.abnormality_name("CA", _lazy_mode=True))

print(pancreatitis)



# self.abnormality_name("HGB", _lazy_mode=True) # Checking if HGB level is abnormal, it should print anemia if HGB is low or polycythema if HGB is high, [] if normal value
# self.lab_value("HGB") # Retrieving HGB level from lab results, it