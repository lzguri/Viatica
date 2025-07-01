import re

text = """
 is a 81 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	5.3	04/17/2024 06:10 AM
	RBC	4.14 (L)	04/17/2024 06:10 AM
	HGB	10.8 (L)	04/17/2024 06:10 AM
	HGB	11.9 (L)	04/16/2024 12:32 PM
	HCT	34.8 (L)	04/17/2024 06:10 AM
	MCV	84.1	04/17/2024 06:10 AM
	MCH	26.1 (L)	04/17/2024 06:10 AM
	MCHC	31.0	04/17/2024 06:10 AM
	PLT	209	04/17/2024 06:10 AM
	PLT	209	04/16/2024 12:32 PM
	RDW	17.2 (H)	04/17/2024 06:10 AM
	NEUTROPHIL	4.00	04/17/2024 06:10 AM
	LYMPHOCYTE	0.56 (L)	04/17/2024 06:10 AM
	EOSINOPHIL	0.19	04/17/2024 06:10 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	143	04/17/2024 06:10 AM
	K	3.6	04/17/2024 06:10 AM
	CL	102	04/17/2024 06:10 AM
	CO2	30 (H)	04/17/2024 06:10 AM
	CA	9.4	04/17/2024 06:10 AM
	CA	9.1	04/16/2024 12:32 PM
	BUN	13	04/17/2024 06:10 AM
	CREAT	1.06	04/17/2024 06:10 AM
	GFR	>60	04/17/2024 06:10 AM
	GFR	>60	04/16/2024 12:32 PM
	GLUCOSE	98	04/17/2024 06:10 AM
	TOTALPROTEIN	6.9	04/16/2024 12:32 PM
	ALBUMIN	4.0	04/16/2024 12:32 PM
	BILITOTAL	0.4	04/16/2024 12:32 PM
	LIPASE	38	08/14/2020 07:56 PM
	URICACID	7.0	05/04/2023 10:36 AM
	URICACID	6.3	10/21/2019 11:12 AM
	ALKPHOS	103	04/16/2024 12:32 PM
	ALKPHOS	83	11/07/2023 10:09 AM
	ALKPHOS	90	05/04/2023 10:36 AM
	ALKPHOS	83	09/19/2022 02:21 PM
	AST	26	04/16/2024 12:32 PM
	ALT	25	04/16/2024 12:32 PM
	ANIONGAP	11	04/17/2024 06:10 AM
	MG	2.2	04/16/2024 12:32 PM
	MG	2.4	09/16/2022 09:30 AM
	PO4	3.4	05/11/2021 05:39 AM
	T4FREE	1.16	04/20/2021 10:02 AM
	LACTATE	0.7	07/08/2021 01:09 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	48 (H)	04/16/2024 12:32 PM
	BASETROP	38 (H)	09/19/2022 02:21 PM
	2HRTROP	47 (H)	04/16/2024 03:09 PM
	2HRTROP	41 (H)	09/19/2022 04:14 PM
	DELTA	-6	04/16/2024 06:49 PM
	DELTA	-1	04/16/2024 03:09 PM
	6HRTROP	42 (H)	04/16/2024 06:49 PM
	6HRTROP	40 (H)	09/19/2022 08:22 PM
	PROBNPNTERMI	464 (H)	04/16/2024 12:32 PM
	PROBNPNTERMI	129	02/09/2023 12:45 PM
	INR	1.0	04/16/2024 12:32 PM
	PT	14.0	04/16/2024 12:32 PM
	APTT	68.3 (H)	04/15/2021 01:20 PM


workup
Lab Results
Component	Value	Date/Time
	IRON	36 (L)	12/17/2020 03:04 PM
	IRON	38 (L)	08/14/2020 10:08 AM
	TIBC	447	12/17/2020 03:04 PM
	TIBC	508 (H)	08/14/2020 10:08 AM
	IRONPERCENT	8 (L)	12/17/2020 03:04 PM
	IRONPERCENT	7 (L)	08/14/2020 10:08 AM
	FERRITIN	57.5	12/17/2020 03:04 PM
	FERRITIN	208.6	11/01/2018 02:12 AM
	VITAMINB12	870	06/30/2020 11:53 AM
	VITAMINB12	380	11/01/2018 05:43 AM
	FOLATE	>20.0	06/30/2020 11:53 AM
	FOLATE	>20.0 (H)	11/01/2018 05:43 AM


Lab Results
Component	Value	Date/Time
	PHUA	7.0	07/07/2021 02:34 PM
	SGUR	1.010	07/07/2021 02:34 PM
	URINELEUKOC	Negative	07/07/2021 02:34 PM
	NITRITEUA	Negative	07/07/2021 02:34 PM
	KETONEURINE	Negative	07/07/2021 02:34 PM
	PROTEINUA	2+ (A)	07/07/2021 02:34 PM
	GLUUA	Negative	07/07/2021 02:34 PM
	BLOODUA	Negative	07/07/2021 02:34 PM
	WBCU	0-2	07/07/2021 02:34 PM
	RBCUA	0-2	07/07/2021 02:34 PM
	BACTERIAUA	Negative	07/07/2021 02:34 PM
	UREPITHELIAL	0-5	04/26/2021 11:00 AM


Lab Results
Component	Value	Date/Time
	ESR	14	01/02/2020 10:38 AM
	CRP	4.2	01/02/2020 10:38 AM


Lab Results
Component	Value	Date/Time
	PHBLOODPOC	7.44	04/24/2021 06:42 PM
	PCO2POC	40	04/24/2021 06:42 PM
	PO2POC	109 (H)	04/24/2021 06:42 PM
	O2SATPOC	99 (H)	04/24/2021 06:42 PM


Lab Results
Component	Value	Date/Time
	INFLUENZAA	Not Detected	07/07/2021 11:18 AM
	INFLUENZAB	Not Detected	07/07/2021 11:18 AM
	COVID19	Not Detected	04/16/2024 12:31 PM
	RSVAG	Not Detected	07/07/2021 11:18 AM


Lab Results
Component	Value	Date/Time
	HGBA1C	5.6	05/26/2020 08:24 AM
	LDLCALC	101 (H)	11/07/2023 10:09 AM


Lab Results
Component	Value	Date/Time
	TRIGLYCERIDE	132	11/07/2023 10:09 AM
	TSH	2.41	04/16/2024 12:32 PM


No results found for: "AMPHETAMINEQ", "BARBITQLUR", "BENZDIAQLUR", "CANNABQLUR", "COCAINEQUAL", "METHADONEU", "OPIATEQUA", "OXYCODQLUR", "PHENCYCLID"

Toxicology
No results found for: "ETHANOL", "ACETAMINOPHE", "SALICYLATE"

Vitamins
Lab Results
Component	Value	Date/Time
	VITAMINDTO	42	04/02/2018 01:33 PM


Tumor markers
No results found for: "AFPTM"

Virology
Lab Results
Component	Value	Date/Time
	HEPCAB	Non-reactive	08/20/2018 11:05 AM
 


GIPATHOGEN
No results found for: "CLOSTRIDIU"




Principal Problem:
  Acute diastolic heart failure
Active Problems:
  Hypertrophic cardiomyopathy
    Overview: ECHO 2017
    
  COPD, mild
  GAD (generalized anxiety disorder)
  Gastroesophageal reflux disease without esophagitis
  BPH (benign prostatic hyperplasia)
  OSA (obstructive sleep apnea)
  Mixed hyperlipidemia
  Presence of Watchman left atrial appendage closure device
  Atypical atrial flutter
  History of atrial fibrillation
  Acute on chronic congestive heart failure
  Long QT interval
  Atrial fibrillation
  Hypertrophic obstructive cardiomyopathy (HOCM)
 


Vitals:
	04/17/24 1009
BP:	(!) 127/106
Pulse:	(!) 130
Resp:	
Temp:	
SpO2:	



Prior to Admission Medications
Prescriptions	Last Dose	Informant	Patient Reported?	Taking?
DULoxetine (CYMBALTA) 60 mg Capsule, Delayed Release(E.C.)			No	No
Sig: take 1 capsule by mouth twice daily
Potassium 99 mg Tablet			Yes	No
Sig: Take 99 mg by mouth daily.
allopurinoL (ZYLOPRIM) 100 mg tablet			No	No
Sig: take 1 tablet by mouth every day
aspirin (ECOTRIN EC) 81 mg Tablet, Delayed Release (E.C.)			No	No
Sig: Take 1 Tablet (81 mg) by mouth daily.
atorvastatin (LIPITOR) 40 mg tablet			No	No
Sig: TAKE 1 TABLET (40 MG) BY MOUTH DAILY.
buPROPion (WELLBUTRIN) 75 mg tablet			No	No
Sig: TAKE 1 TABLET (75 MG) BY MOUTH 2 TIMES DAILY.
busPIRone (BUSPAR) 7.5 mg Tablet			No	No
Sig: take 1 tablet by mouth two times a day
cetirizine (ZyrTEC) 10 mg tablet			Yes	No
Sig: Take 10 mg by mouth daily.
ciclopirox (LOPROX) 0.77 % Cream			No	No
Sig: Apply to affected area 2 times daily.
cyanocobalamin (VITAMIN B-12) 500 mcg tablet			Yes	No
Sig: Take 500 mcg by mouth daily.
diltiaZEM (CARDIZEM CD) 180 mg Controlled Delivery 24 hour capsule			No	No
Sig: take 1 capsule by mouth two times a day
dofetilide (TIKOSYN) 250 mcg capsule			No	No
Sig: TAKE 1 CAPSULE (250 MCG) BY MOUTH EVERY 12 HOURS.
fluticasone propionate (FLOVENT HFA) 110 mcg/actuation HFA Aerosol Inhaler			No	No
Sig: TAKE 2 PUFFS BY INHALATION 2 TIMES DAILY.
furosemide (LASIX) 40 mg tablet			No	No
Sig: TAKE 1 TABLET (40 MG) BY MOUTH 2 TIMES DAILY.
ketoconazole (NIZORAL) 2 % Cream			No	No
Sig: APPLY TO THE AFFECTED AREA DAILY
magnesium oxide 250 mg magnesium Tablet			Yes	No
Sig: Take 250 mg by mouth daily.
montelukast (SINGULAIR) 10 mg tablet			No	No
Sig: take 1 tablet by mouth every night at bedtime
multivitamin (DAILY-VITE) tablet			Yes	No
Sig: Take 1 Tablet by mouth daily.
pantoprazole (PROTONIX) 40 mg Tablet, Delayed Release (E.C.)			No	No
Sig: TAKE 1 TABLET(40 MG) BY MOUTH TWICE DAILY
pregabalin (Lyrica) 150 mg Capsule			No	No
Sig: Take 1 Capsule (150 mg) by mouth every 8 hours.
tamsulosin (FLOMAX) 0.4 mg capsule			No	No
Sig: TAKE 1 CAPSULE BY MOUTH EVERY DAY

Facility-Administered Medications: None


Current Facility-Administered Medications
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	[COMPLETED] polyethylene glycol (MIRALAX) packet 17 Gram	 17 Gram	Oral	ONE time only	Patel, Taksh, MD	 	17 Gram at 04/17/24 0410
•	[COMPLETED] ipratropium-albuteroL (DUONEB) 0.5 mg-3 mg(2.5 mg base)/3 mL inhalation solution 3 mL	 3 mL	Inhalation	resp, one time only	Gammon, Dustin, DO	 	3 mL at 04/16/24 1454
•	[COMPLETED] LORazepam (ATIVAN) tablet 1 mg	 1 mg	Oral	ONE time only	Gammon, Dustin, DO	 	1 mg at 04/16/24 1222
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	sodium chloride flush injection 5 mL	 5 mL	IV	every 12 hours (2 times daily)	Zguri, Liridon, MD	 	5 mL at 04/17/24 0808
•	sodium chloride flush injection 5 mL	 5 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	sodium chloride 0.9 % 250 mL flush bag 25 mL	 25 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	dextrose 5 % in water 250 mL flush bag 25 mL	 25 mL	IV	see admin instructions	Zguri, Liridon, MD	 	 
•	acetaminophen (TYLENOL) tablet 650 mg	 650 mg	Oral	every 6 hours PRN	Zguri, Liridon, MD	 	 
•	furosemide (LASIX) injection 40 mg	 40 mg	IV	BID, 7 hours apart	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	[COMPLETED] potassium chloride 20 mEq in sodium chloride 0.9% 150 mL IVPB	 20 mEq	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 04/16/24 1708
•	enoxaparin (LOVENOX) injection 40 mg	 40 mg	subCUT	every 24 hours	Gammon, Dustin, DO	 	40 mg at 04/17/24 0808
•	cefTRIAXone (ROCEPHIN) 2,000 mg in sodium chloride 0.9% 50 mL IVPB (MBP)	 2,000 mg	IV	every 24 hours	Zguri, Liridon, MD	 	Stopped at 04/16/24 1643
•	doxycycline hyclate (VIBRAMYCIN) 100 mg in sodium chloride 0.9% 100 mL IVPB (MBP)	 100 mg	IV	every 12 hours	Zguri, Liridon, MD	 	Stopped at 04/17/24 0436
•	diltiaZEM (CARDIZEM CD) SR 24 hour capsule 180 mg	 180 mg	Oral	BID	Farmer, Sarah, FNP	 	180 mg at 04/17/24 1009
•	[COMPLETED] potassium bicarbonate-citric acid (EFFER-K) tablet 20 mEq	 20 mEq	Oral	ONE time only	Zguri, Liridon, MD	 	20 mEq at 04/16/24 1723
•	pantoprazole (PROTONIX) tablet 40 mg	 40 mg	Oral	daily BEFORE breakfast	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	tamsulosin (FLOMAX) SR 24 hour capsule 0.4 mg	 0.4 mg	Oral	daily	Zguri, Liridon, MD	 	0.4 mg at 04/17/24 0807
•	atorvastatin (LIPITOR) tablet 40 mg	 40 mg	Oral	daily	Zguri, Liridon, MD	 	40 mg at 04/17/24 0807
•	DULoxetine (CYMBALTA) capsule 60 mg	 60 mg	Oral	BID	Zguri, Liridon, MD	 	60 mg at 04/17/24 0807
•	montelukast (SINGULAIR) 10 mg tablet 10 mg	 10 mg	Oral	daily BEDTIME	Zguri, Liridon, MD	 	10 mg at 04/16/24 2139
•	[DISCONTINUED] potassium CHLORIDE 20 mEq/50 mL IVPB 20 mEq	 20 mEq	IV	ONE time only	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] enoxaparin (LOVENOX) injection 40 mg	 40 mg	subCUT	every 24 hours	Zguri, Liridon, MD	 	 


CT CHEST WO CONTRAST
Final Result
IMPRESSION: Please see below. 
 
Exam: CT CHEST WO CONTRAST 
 
Date/Time of Exam: 4/16/2024 3:01 PM 
 
REASON FOR EXAM: Respiratory illness, nondiagnostic xray. 
 
DIAGNOSIS: Acute on chronic congestive heart failure, unspecified 
heart failure type; Dyspnea, unspecified type. 
 
Technique: CT of the chest was performed without the administration of 
intravenous contrast. 
 
Findings: Comparison is made to the prior CT of the chest performed 
1/10/2023. 
 
There is a small loculated pleural effusion on the left which is new 
since the prior examination. There are hazy interstitial infiltrates, 
greatest in lung bases likely representing edema. This is seen in the 
setting of pulmonary vascular congestion. Trace right pleural effusion 
with cardiomegaly and pulmonary artery enlargement. Coronary artery 
disease and a left atrial appendage closure device are noted. 
 
The imaged abdominal structures are grossly unremarkable. There is 
cervicothoracic spondylosis. Mild degenerative changes in the right 
shoulder girdle are partially imaged. Old healed bilateral rib 
fractures are seen. 
 
IMPRESSION: 
 
 
Findings most consistent with CHF exacerbation with cardiomegaly, 
pulmonary vascular congestion, and small loculated left pleural 
effusion and trace right pleural effusion. Interstitial infiltrates 
may also represent some degree of pneumonitis and there is some 
peribronchial thickening which could indicate mild 
bronchitis/bronchopneumonia in the proper clinical setting. 
 

XR CHEST PA AND LATERAL 2 VW
Final Result
IMPRESSION: Please see below. 
 
Exam: XR CHEST PA AND LATERAL 2 VW 
 
Date/Time of Exam: 4/16/2024 12:58 PM 
 
REASON FOR EXAM: Shortness of Breath SOB. 
 
DIAGNOSIS: See Reason for Exam. 
 
Findings: Comparison is made to the prior examination performed 
9/19/2022. 
 
There are patchy interstitial infiltrates in the lower lungs with some 
consolidation in the left lung suspected. A small left pleural 
effusion is not entirely excluded. There is cardiomegaly with 
pulmonary vascular congestion and a left atrial appendage occlusion 
devices noted. The thoracic aorta is grossly unremarkable. There is 
cervicothoracic spondylosis. Old healed right rib fractures and left 
rib fractures are noted. Suture anchors are partially imaged in the 
right shoulder girdle. 
 
IMPRESSION: 
 
Findings most consistent with CHF exacerbation with pulmonary vascular 
congestion, cardiomegaly, and mild interstitial edema. There may be 
some mild left basilar consolidation and a small pleural effusion. 






"""

# Dictionary of the names

name_of_study = {
    'CT CHEST WO CONTRAST': 'CT chest wo contrast',
    "XR CHEST PA AND LATERAL 2 VW" : 'Chest x-ray PA/L view',
    'MRI BRAIN WO CONTRAST': 'MRI brain wo contrast'

}

# Create an empty dictionary

studies_printed = {}

# Define regex pattern to extract the name of the exam
exam_pattern = r'^Exam:\s*(.*?)\n'

# Clean the text
text = re.sub("IMPRESSION: Please see below.", "", text)

# Extract exam name
exam_matches = re.findall(exam_pattern, text, re.MULTILINE)

# Define regex pattern to extract the entire impression section
impression_pattern = r'IMPRESSION:\s*([\s\S]*?)(?:\n\n|$)'

# Extract impression
impression_matches = re.findall(impression_pattern, text)

# Print results
for exam, impression in zip(exam_matches, impression_matches):
    exam_name = exam.strip()
    impression_text = impression.strip().replace('\n', ' ')
    for generic_name, study_name in name_of_study.items():
        if generic_name == exam_name:
            studies_printed[study_name] = impression_text

    




def extract_images(text):
    # Dictionary of the names
    name_of_study = {
        'CT CHEST WO CONTRAST': 'CT chest wo contrast',
        "XR CHEST PA AND LATERAL 2 VW" : 'Chest x-ray PA/L view',
        'MRI BRAIN WO CONTRAST': 'MRI brain wo contrast',
        "XR ANKLE 3+ VW LEFT": 'X-ray left ankle',
        'XR FOOT 3+ VW LEFT': 'X-ray left foot',
        'MRI FOOT W WO CONTRAST LEFT' : 'MRI foot w and wo contrast',
        'MRI ANKLE W WO CONTRAST LEFT' : 'MRI ankle w and wo contrast',
        'XR CHEST PA OR AP 1 VW' : 'Chest x-ray',
        'CT CHEST WO CONTRAST' : 'CT chest wo contrast'
    }
    
    # Clean the text
    text = re.sub("IMPRESSION: Please see below.", "", text)

    # Output list
    study_list = []
    
    # Define regex pattern to extract the name of the exam
    exam_pattern = r'^Exam:\s*(.*?)\n'
    
    # Extract exam name
    exam_matches = re.findall(exam_pattern, text, re.MULTILINE)
    
    # Define regex pattern to extract the entire impression section
    impression_pattern = r'IMPRESSION:\s*([\s\S]*?)(?:\n\n|$)'
    
    # Extract impressions
    impression_matches = re.findall(impression_pattern, text)
    
    # Print results
    for exam, impression in zip(exam_matches, impression_matches):
        exam_name = exam.strip()
        impression_text = impression.strip().replace('\n', ' ')
        for generic_name, study_name in name_of_study.items():
            if generic_name == exam_name:
                study_list.append(f"{study_name}: {impression_text}")

    
    return '\n\n'.join(study_list)


print(extract_images(text))



import hashlib

def string_to_hash(input_string):
    # Convert the input string to bytes
    input_bytes = input_string.encode('utf-8')
    
    # Calculate the SHA-1 hash of the input bytes
    hash_object = hashlib.sha1(input_bytes)
    
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    
    return hash_hex

# Example usage:
input_string = "I60313012T"
hashed_string = string_to_hash(input_string)
print("Hashed string:", hashed_string)
