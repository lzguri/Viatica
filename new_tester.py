import time
import disease
a  = time.time()
Text_input = '''

 is a 81 y.o. male

Complete blood count

Lab Results
Component	Value	Date/Time
	WBC	5.3	04/21/2024 06:10 AM
	RBC	4.14 (L)	04/21/2024 06:10 AM
	HGB	10.8 (L)	04/21/2024 06:10 AM
	HGB	11.9 (L)	04/20/2024 12:32 PM
	HCT	34.8 (L)	04/21/2024 06:10 AM
	MCV	84.1	04/21/2024 06:10 AM
	MCH	26.1 (L)	04/21/2024 06:10 AM
	MCHC	31.0	04/21/2024 06:10 AM
	PLT	209	04/21/2024 06:10 AM
	PLT	209	04/20/2024 12:32 PM
	RDW	17.2 (H)	04/21/2024 06:10 AM
	NEUTROPHIL	4.00	04/21/2024 06:10 AM
	LYMPHOCYTE	0.56 (L)	04/21/2024 06:10 AM
	EOSINOPHIL	0.19	04/21/2024 06:10 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	143	04/21/2024 06:10 AM
	K	3.6	04/21/2024 06:10 AM
	CL	102	04/21/2024 06:10 AM
	CO2	30 (H)	04/21/2024 06:10 AM
	CA	9.4	04/21/2024 06:10 AM
	CA	9.1	04/20/2024 12:32 PM
	BUN	13	04/21/2024 06:10 AM
	CREAT	1.06	04/21/2024 06:10 AM
	GFR	>60	04/21/2024 06:10 AM
	GFR	>60	04/20/2024 12:32 PM
	GLUCOSE	98	04/21/2024 06:10 AM
	TOTALPROTEIN	6.9	04/20/2024 12:32 PM
	ALBUMIN	4.0	04/20/2024 12:32 PM
	BILITOTAL	0.4	04/20/2024 12:32 PM
	LIPASE	38	08/14/2020 07:56 PM
	URICACID	7.0	05/04/2023 10:36 AM
	URICACID	6.3	10/21/2019 11:12 AM
	ALKPHOS	103	04/20/2024 12:32 PM
	ALKPHOS	83	11/07/2023 10:09 AM
	ALKPHOS	90	05/04/2023 10:36 AM
	ALKPHOS	83	09/19/2022 02:21 PM
	AST	26	04/20/2024 12:32 PM
	ALT	25	04/20/2024 12:32 PM
	ANIONGAP	11	04/21/2024 06:10 AM
	MG	2.2	04/20/2024 12:32 PM
	MG	2.4	09/16/2022 09:30 AM
	PO4	3.4	05/11/2021 05:39 AM
	T4FREE	1.16	04/20/2021 10:02 AM
	LACTATE	0.7	07/08/2021 01:09 AM


Cardiac profile

Lab Results
Component	Value	Date/Time
	BASETROP	48 (H)	04/20/2024 12:32 PM
	BASETROP	38 (H)	09/19/2022 02:21 PM
	2HRTROP	47 (H)	04/20/2024 03:09 PM
	2HRTROP	41 (H)	09/19/2022 04:14 PM
	DELTA	-6	04/20/2024 06:49 PM
	DELTA	-1	04/20/2024 03:09 PM
	6HRTROP	42 (H)	04/20/2024 06:49 PM
	6HRTROP	40 (H)	09/19/2022 08:22 PM
	PROBNPNTERMI	464 (H)	04/20/2024 12:32 PM
	PROBNPNTERMI	129	02/09/2023 12:45 PM
	INR	1.0	04/20/2024 12:32 PM
	PT	14.0	04/20/2024 12:32 PM
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
	COVID19	Not Detected	04/20/2024 12:31 PM
	RSVAG	Not Detected	07/07/2021 11:18 AM


Lab Results
Component	Value	Date/Time
	HGBA1C	5.6	05/26/2020 08:24 AM
	LDLCALC	101 (H)	11/07/2023 10:09 AM


Lab Results
Component	Value	Date/Time
	TRIGLYCERIDE	132	11/07/2023 10:09 AM
	TSH	2.41	04/20/2024 12:32 PM


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


dofetilide
prolonged QT

'''


def get_acute_diseases():
    from speciality_modules import endocrinology, gastroenterology, cardiology, infectious, neurology, pulmonary, nephrology, hematology
    import pandas as pd


    expanded_conditions = {
        # High acuity 
        "Acute heart failure": cardiology.AcuteHeartFailure,
        'Acute cerebrovascular accident': neurology.CVA,
        "Bradycardia": cardiology.Bradycardia,
        "NSTEMI" : cardiology.AcuteCoronarySyndrome,
        "Acute pericarditis" : cardiology.AcutePericarditis,
        "Atrial fibrillation with RVR": cardiology.Afib,
        'Diabetic ketoacidosis': endocrinology.DiabeticKetoacidosis,
        'Upper GI Bleeding': gastroenterology.UpperGIBleeding,
        'Lower GI Bleeding' : gastroenterology.LowerGIBleeding,
        'Acute Pancreatitis': gastroenterology.AcutePancreatitis,
        'Clostridium difficile' : gastroenterology.CDiff,
        "Inflammatory Bowel disease" : gastroenterology.IBD_flare,
        "Acute diarrhea": gastroenterology.AcuteDiarrhea,
        'Cellulitis': infectious.SkinInfections,
        #'Cellulitis': infectious.Cellulitis,
        'Diabetic ulcer': infectious.DiabeticUlcer,
        "Acute cholecystitis" : infectious.AcuteCholecystitis,
        'Neutropenic fever': infectious.NeutropenicFever,


        # Moderate
        'Acute kidney injury': nephrology.AcuteKidneyInjury,
        'Hyponatremia': nephrology.Hyponatremia,
        'Hypokalemia': nephrology.Hypokalemia,
        'Hyperkalemia': nephrology.Hyperkalemia,
        'Hypocalcemia' : nephrology.Hypocalcemia,
        'Hypercalcemia': nephrology.Hypercalcemia,
        "Hypomagnesemia": nephrology.Hypomagnesemia,

        # Low acuity
        'Diabetes mellitus' : endocrinology.DM,


        # Gastroenterology goes here
        "Liver cirrhosis" : gastroenterology.LiverCirrhosis,
        "Gastroparesis": gastroenterology.Gastroparesis,
        

        # Neurology goes here
        'Altered mental status': neurology.Encephalopathy,
        
        'Myasthenia crisis': neurology.MyastheniaCrisis,
        'Back pain': neurology.BackPain,

        # Pulmonary goes here
        'COPD exacerbation': pulmonary.COPDexac,
        'Asthma exacerbation': pulmonary.Asthmaexac,
        'ILD exacerbation': pulmonary.ILDexac,
        'Pleural effusion': pulmonary.Pleuraleffusion,
        'Acute pulmonary embolism': pulmonary.AcutePulmonaryEmbolism,
        'COVID-19' : pulmonary.COVID19,

        # Hematology goes here
        'Thrombocytopenia' : hematology.Thrombocytopenia,
        "Anemia": hematology.Anemia,
        "Sickle cell anemia": hematology.SickleCellCrisis

    }
    diseases = []
    diseases_object = []
    #extract the 1name_of_disease column into a list
    diseases = master_class_instance.medical_conditions(chronic=False)  #_find_names_in_string(acute_diseases, self.file_contents)

    for name in diseases:
        for key in expanded_conditions.keys():
            if name.lower() == key.lower():
                    diseases_object.append(expanded_conditions[key](key, master_class_instance))
                    break
        else:
            diseases_object.append(disease.Disease(name, master_class_instance))
    return diseases, diseases_object


def process(input_text):
    import functions
    rtext = ""
    global master_class_instance
    master_class_instance = functions.MasterClass(input_text)

    # is a {master_class_instance.get_age()} year-old {master_class_instance.get_sex()} with PMH of 

    Text_output = f"{master_class_instance.extract_age_gender()} with PMH of {master_class_instance.format_list(master_class_instance.medical_conditions(acute=False, pmh_only=True))} who presents today with c/o ***" + '\n\n' + \
        f"{master_class_instance.summarize_vitals()}" + '\n\n' + f"{master_class_instance.extract_abnormal_labs(days=3)}" + \
        '\n\n' + master_class_instance.extract_exam_impressions() + \
        '\n\n' + "PLACEHOLDERTEXT" + "\n\n" + \
        f"Patient received {master_class_instance.Completed_treatment_ED(completed_treatment=True)} in the ED." + '\n\n'
    rtext += Text_output + "\n"

    placeholder_replacement = []  # Extra assessment info such as ECG

    chronic_diseases = master_class_instance.medical_conditions(acute=False)  # Retrieve chronic medical conditions from the chart
    acute_diseases, acute_disease_objects = get_acute_diseases()
    acute_diseases_string = ""
    for j in range(len(acute_diseases)):
        acute_diseases_string += acute_disease_objects[j].__str__() + "\n"
        # add a newline if one isn't already there at the end
        if acute_diseases_string[-2] != "\n":
            acute_diseases_string += "\n"

        # remove superseded from chronic
        superseded = [x.lower() for x in acute_disease_objects[j].get_superseding_conditions(
        )] + [acute_diseases[j].lower()]
        for i in range(len(chronic_diseases)):
            if chronic_diseases[i] is not None and chronic_diseases[i].lower() in superseded:
                chronic_diseases[i] = None

        # add placeholder
        extra = acute_disease_objects[j].get_extra_assessment_info()
        if extra:
            placeholder_replacement += extra

    # remove duplicate lines in acute diseases
    acute_diseases_string = acute_diseases_string.splitlines()
    new_lines = []
    for line in acute_diseases_string:
        if line not in new_lines or line in ['Plan', '']:
            # Check if the line is a disease from PMH abbreviations
            if line in acute_diseases:
                line = f"{line}"
            new_lines.append(line)
    acute_diseases_string = '\n'.join(new_lines)
    rtext += acute_diseases_string + "\n"

    # remove None from chronic
    chronic_diseases = [
        x for x in chronic_diseases if x is not None and x != ""]

    for i in chronic_diseases:
        p = master_class_instance.plan_chronic_minimal(i)
        if p and (p.lower() != i.lower()):
            rtext += p + "\n\n"

    rtext += '\nMEDICATIONS REC. HAS NOT BEEN COMPLETED AT THE TIME OF WRITING THIS NOTE - PENDING CONFIRMATION ***'

    # replace the placeholder text with the extra info
    if placeholder_replacement:
        placeholder_replacement = list(set(placeholder_replacement))
        rtext = rtext.replace(
            "PLACEHOLDERTEXT", "\n".join(placeholder_replacement), 1)
    else:
        # remove if nothing to add
        rtext = rtext.replace("PLACEHOLDERTEXT", "")


    #
    # replace multiple blank lines in a row with just one blank line
    rtext = rtext.splitlines()
    # iterate through, if we encounter two empty lines in a row then we remove one of them
    new_lines = []
    for line in rtext:
        if line != "":
            new_lines.append(line)
        else:
            if len(new_lines) == 0 or new_lines[-1] != "":
                new_lines.append(line)
    #print("here")
    #print(master_class_instance.start_med("atenolol"))
    del functions
    return '\n'.join(new_lines) + "\n"


if __name__ == '__main__':
    print(process(Text_input))
    print(time.time() - a, " seconds taken to run")


# import functions
# print(functions.MasterClass(Text_input).extract_images())


# ## IMAGES
