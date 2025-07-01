import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import disease
import functions


"""

IRON, TIBC, IRONPERCENT, FERRITIN, VITAMINB12, FOLATE

"""


class Anemia(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__("Anemia", MCI,
                         display_home_meds=True, full_meds_plan=True)

        self.fn = MCI
        self.diseases_present = self.fn.medical_conditions()

        
        self.hgb = self.fn.lab_value('HGB')

        self.current_hb = ''
        self.current_hb += self.fn.check_labs('HGB', comparisons=True, display_text=True, compared_with=True)

        self.today_hb = self.fn.check_labs("HGB", dict_mode=False, display_text=True, comparisons=True, days_too_old=2, compared_with=True)
         
       
    def type_of_anemia(self):
        # Determine morphology of the anemia
        current_mcv = self.fn.abnormality_name("MCV", _lazy_mode=True)  # Microcytic, normocytic, or macrocytic
        current_mchc = self.fn.abnormality_name("MCHC", _lazy_mode=True)

        morphology_name = []

        if current_mchc:
            morphology_name.append(current_mchc.title())
        else:
            morphology_name.append("Normochromic")

        if current_mcv:
            morphology_name.append(f" {current_mcv} anemia")
        else:
            morphology_name.append(" normocytic anemia")

        morphology = ''.join(morphology_name)

        return morphology



    def __str__(self):

        self.name = self.type_of_anemia()

        self.assessment['current_labs'] = []

        self.assessment['current_labs'] = self.assessment['current_labs'] + [self.current_hb]

        final_string = self.static_assessment()

        

        

        final_string += self.static_plan()

        if self.hgb:
            if self.hgb <= 8:
                final_string += '- Type and screen' + '\n'
                if self.hgb <= 7:
                    final_string += f'- Transfuse pRBC [{self.hgb}] and recheck Hgb post-transfusion ***' + '\n' + "- Hgb target > 7 ***"

        return final_string


class Thrombocytopenia(disease.Disease):

    def __init__(self, name, MCI):
        super().__init__('Thrombocytopenia', MCI=MCI)


        self.fn = MCI
        self.diseases = self.fn.medical_conditions()

        if "Severe thrombocytopenia" in self.diseases:
            super().__init__('Severe Thrombocytopenia', MCI=MCI)
            
        elif "Moderate thrombocytopenia" in self.diseases:
            super().__init__('Moderate Thrombocytopenia', MCI=MCI)
            
        elif "Mild thrombocytopenia" in self.diseases:
            super().__init__('Mild Thrombocytopenia', MCI=MCI)

    def __str__(self):

        # Severity of thrombocytopenia
        # Mild – 100,000 to 149,000/microL
        # Moderate – 50,000 to 99,000/microL
        # Severe – <50,000/microL

        add_string = self.static_assessment()
        
        add_string += self.static_plan()
        
        return add_string
    

class SickleCellCrisis(disease.Disease):
    
    def __init__(self, name, MCI):
        super().__init__("Sickle cell crisis", MCI=MCI)
        
        self.fn = MCI
        
	
    def __str__(self):
            
        add_string = self.static_assessment()
        
        add_string += self.static_plan()
        
        add_string += self.fn.type_of_fluids()
        

        return add_string




text_input = """

 is a 81 y.o. male

Complete blood count
l-glutamine
hydroxyurea
Lab Results
Component	Value	Date/Time
	WBC	9.2	03/09/2024 12:59 PM
	RBC	2.78 (L)	03/09/2024 12:59 PM
	HGB	8.3 (L)	03/09/2024 12:59 PM
	HGB	8.9 (L)	01/02/2024 11:31 PM
	HCT	24.9 (L)	03/09/2024 12:59 PM
	MCV	89.6	03/09/2024 12:59 PM
	MCH	29.9	03/09/2024 12:59 PM
	MCHC	33.3	03/09/2024 12:59 PM
	PLT	63 (L)	03/09/2024 12:59 PM
	PLT	70 (L)	01/02/2024 11:31 PM
	RDW	15.8 (H)	03/09/2024 12:59 PM
	NEUTROPHIL	8.08 (H)	01/02/2024 09:51 AM
	LYMPHOCYTE	0.22 (L)	01/02/2024 09:51 AM
	EOSINOPHIL	0.00	01/02/2024 09:51 AM


Chemistry
Lab Results
Component	Value	Date/Time
	NA	141	03/09/2024 12:59 PM
	K	3.1	03/09/2024 12:59 PM
	CL	112 (H)	03/09/2024 12:59 PM
	CO2	19 (L)	03/09/2024 12:59 PM
	CA	7.6 (L)	03/09/2024 12:59 PM
	CA	7.1 (L)	01/02/2024 11:31 PM
	BUN	47 (H)	03/09/2024 12:59 PM
	CREAT	1.72 (H)	03/09/2024 12:59 PM
	GFR	39	03/09/2024 12:59 PM
	GFR	33	01/02/2024 11:31 PM
	GLUCOSE	119 (H)	03/09/2024 12:59 PM
	TOTALPROTEIN	4.1 (L)	03/09/2024 12:59 PM
	ALBUMIN	1.7 (L)	03/09/2024 12:59 PM
	BILITOTAL	0.8	03/09/2024 12:59 PM
	URICACID	6.6	03/09/2024 12:05 PM
	ALKPHOS	62	03/09/2024 12:59 PM
	ALKPHOS	89	01/02/2024 09:51 AM
	AST	52 (H)	03/09/2024 12:59 PM
	ALT	22	03/09/2024 12:59 PM
	ANIONGAP	10	03/09/2024 12:59 PM
	T4FREE	1.25	09/24/2019 01:59 PM
	LACTATE	1.6	03/09/2024 12:59 PM


Cardiac profile

Lab Results
Component	Value	Date/Time
	INR	1.7 (H)	03/09/2024 12:59 PM
	PT	20.7 (H)	03/09/2024 12:59 PM


workup
Lab Results
Component	Value	Date/Time
	IRON	165	03/09/2024 12:05 PM
	IRON	45 (L)	11/14/2023 01:23 PM
	TIBC	301	03/09/2024 12:05 PM
	TIBC	327	11/14/2023 01:23 PM
	IRONPERCENT	55 (H)	03/09/2024 12:05 PM
	IRONPERCENT	14 (L)	11/14/2023 01:23 PM
	FERRITIN	1028 (H)	03/09/2024 12:05 PM
	FERRITIN	149.3	11/21/2023 09:34 AM
	FERRITIN	127	09/20/2023 11:53 AM
	LD	319 (H)	03/09/2024 12:05 PM
	LD	159	04/14/2015 09:46 AM
	VITAMINB12	583	03/09/2024 12:05 PM
	VITAMINB12	490	11/14/2023 01:23 PM
	FOLATE	15.0	03/09/2024 12:05 PM
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
	RBCUA	0-2	09/29/2015 11:52 AM
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

  Protein-calorie malnutrition, severe
 


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
cyanocobalamin (VITAMIN B-12) 1,000 mcg/mL Solution	1/2/2024		No	Yes
Sig: Inject 1 mL (1,000 mcg) by intramuscular injection every 30 days.
cyanocobalamin 1,000 mcg Tablet			No	No
Sig: Take 1 Tablet (1,000 mcg) by mouth daily.
dexAMETHasone (DECADRON) 4 mg tablet			No	No
Sig: Take (5 tablets) in the morning with food once a week, while you are receiving the Velcade.
lenalidomide (Revlimid) 15 mg capsule	1/2/2024		No	Yes
Sig: TAKE 1 CAPSULE BY MOUTH DAILY ON DAYS 1-14 OF A 21 DAY CYCLE
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

Facility-Administered Medications: None


Current Facility-Administered Medications
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	aspirin (ECOTRIN EC) tablet 81 mg	 81 mg	Oral	daily	Gilmore, Lisa L, FNP	 	 
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	[Held by Provider] heparin injection 5,000 Units	 5,000 Units	subCUT	every 8 hours	Gilmore, Lisa L, FNP	 	5,000 Units at 01/03/24 0903
•	HYDROcodone-acetaminophen (NORCO) 7.5-325 mg per tablet 1 Tablet	 1 Tablet	Oral	every 6 hours PRN	Gilmore, Lisa L, FNP	 	 
•	HYDROmorphone (DILAUDID) 2 mg/mL injection 1 mg	 1 mg	IV	every 2 hours PRN	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] vancomycin in sodium chloride 0.9% (VANCOCIN) 750 mg/257.5 mL IVPB 750 mg	 750 mg	IV	ONE time only	Meyer III, Magnus O, DO	 	Stopped at 01/03/24 1529
•	[COMPLETED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Robb, Lauren E, PA	 	Stopped at 01/03/24 1107
•	[START ON 1/4/2024] levothyroxine (SYNTHROID) tablet 100 mcg	 100 mcg	Oral	daily EARLY	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Meyer III, Magnus O, DO	999 mL/hr at 01/03/24 1332	Rate Verify at 01/03/24 1332
•	fentaNYL (PF) 1,500 mcg/30 mL (50 mcg/mL) PCA	 0-150 mcg/hr	IV	titrate	Gilmore, Lisa L, FNP	 	 
•	propofol (DIPRIVAN) 10 mg/mL continuous infusion	 0-50 mcg/kg/min	IV	titrate	Gilmore, Lisa L, FNP	 	 
•	[DISCONTINUED] levothyroxine (SYNTHROID) tablet 100 mcg	 100 mcg	Oral	daily EARLY	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] sodium hypochlorite (DAKIN'S) 0.25% half-strength topical solution	 		intra-proc PRN	Draper, Brian B, DO	 	230 mL at 01/03/24 1516
•	acetaminophen (TYLENOL) tablet 650 mg	 650 mg	Oral	every 6 hours PRN	Gilmore, Lisa L, FNP	 	 
•	VANCOMYCIN CONSULT TO PHARMACY	 	See Admin Instructions	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	naloxone (NARCAN) 0.4 mg/mL injection 0.1 mg	 0.1 mg	IV	see admin instructions	Yassa, Youssef Y, MD	 	 
•	[COMPLETED] albumin, human (BUMINATE) 5 % injection 25 Gram	 25 Gram	IV	ONE time only	Pallohusky, Brian S, MD	 	Stopped at 01/02/24 1815
•	[COMPLETED] lactated ringers infusion	 	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 01/02/24 1830
•	[COMPLETED] lactated ringers infusion	 	IV	ONE time only	Zguri, Liridon, MD	999 mL/hr at 01/02/24 1845	New Bag at 01/02/24 1845
•	[COMPLETED] DEXTROSE 50 % IN WATER (D50W) INTRAVENOUS SYRINGE (CABINET OVERRIDE)	 				 	25 Gram at 01/02/24 1939
•	[COMPLETED] hydrocortisone sod succinate (PF) (Solu-CORTEF) 100 mg in sterile water 2 mL injection	 100 mg	IV	ONE time only	Zguri, Liridon, MD	 	100 mg at 01/02/24 1940
•	[COMPLETED] PHENYLEPHRINE 10 MG/ML INJECTION SOLUTION (CABINET OVERRIDE)	 				 	50 mg at 01/02/24 1936
•	[COMPLETED] HYDROCORTISONE SOD SUCCINATE (PF) 100 MG/2 ML SOLUTION FOR INJECTION (CABINET OVERRIDE)	 				 	100 mg at 01/02/24 1930
•	[COMPLETED] DEXTROSE 5 % IN WATER (D5W) INTRAVENOUS SOLUTION (CABINET OVERRIDE)	 				3.2 mL/hr at 01/02/24 1933	250 mL at 01/02/24 1933
•	[COMPLETED] dextrose 50% (D50) syringe 25 Gram	 25 Gram	IV	ONE time only	Zguri, Liridon, MD	 	25 Gram at 01/02/24 1945
•	norepinephrine bitartrate-D5W (LEVOPHED) 8 mg/250 mL (32 mcg/mL) infusion	 0-0.2 mcg/kg/min	IV	titrate	Gilmore, Lisa L, FNP	7.523 mL/hr at 01/03/24 1504	0.075 mcg/kg/min at 01/03/24 1504
•	[COMPLETED] sodium chloride 0.9% bolus solution 500 mL	 500 mL	IV	ONE time only	Zguri, Liridon, MD	 	Stopped at 01/02/24 2015
•	SEPSIS ANTIBIOTIC ALERT TO PHARMACY	 1 Each	See Admin Instructions	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	sodium chloride 0.9% bolus solution 500 mL	 500 mL	IV	ONE time only	Gilmore, Lisa L, FNP	 	 
•	dextrose 5% - sodium chloride 0.9% infusion	 	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	dextrose 50% (D50) syringe 12.5 Gram	 12.5 Gram	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	dextrose 50% (D50) syringe 25 Gram	 25 Gram	IV	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	glucagon human recombinant (GLUCAGEN) 1 mg/mL injection 1 mg	 1 mg	IM	see admin instructions	Gilmore, Lisa L, FNP	 	 
•	[COMPLETED] ACETAMINOPHEN 325 MG TABLET (CABINET OVERRIDE)	 				 	650 mg at 01/02/24 2117
•	piperacillin-tazobactam (ZOSYN) 3.375 Gram in sodium chloride 0.9% 50 mL IVPB (MBP)	 3.375 Gram	IV	every 8 hours	Gilmore, Lisa L, FNP	 	Stopped at 01/03/24 1258
•	clindamycin (CLEOCIN) 600 mg in 0.9% sodium chloride IVPB	 600 mg	IV	every 8 hours	Gilmore, Lisa L, FNP	 	Stopped at 01/03/24 0952
•	hydrocortisone sod succinate (PF) (Solu-CORTEF) 50 mg in sterile water 1 mL injection	 50 mg	IV	every 6 hours	Gilmore, Lisa L, FNP	 	50 mg at 01/03/24 1229
•	dextran 70-hypromellose PF (ARTIFICIAL TEARS) 0.1-0.3 % ophthalmic solution 1 Drop	 1 Drop	Both Eyes	every 4 hours PRN	Gilmore, Lisa L, FNP	 	1 Drop at 01/03/24 0106
•	[DISCONTINUED] lactated ringers bolus solution 1,000 mL	 1,000 mL	IV	ONE time only	Nguyen, Tina H, MD	 	 
•	[DISCONTINUED] clindamycin (CLEOCIN) 600 mg in dextrose 5% 50 mL IVPB	 600 mg	IV	ONE time only	Nguyen, Tina H, MD	 	 
•	[DISCONTINUED] metroNIDAZOLE (FLAGYL) IVPB 500 mg	 500 mg	IV	ONE time only	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] piperacillin-tazobactam (ZOSYN) 3.375 Gram in sodium chloride 0.9% 50 mL IVPB (MBP)	 3.375 Gram	IV	every 6 hours	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] clindamycin (CLEOCIN) 600 mg in dextrose 5% 50 mL IVPB	 600 mg	IV	every 8 hours	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection 25 mcg	 25 mcg	IV	post-proc every 3 minutes PRN	Yassa, Youssef Y, MD	 	 
•	[DISCONTINUED] HYDROmorphone (DILAUDID) 2 mg/mL injection 0.2 mg	 0.2 mg	IV	post-proc every 5 minutes PRN	Yassa, Youssef Y, MD	 	 
•	[DISCONTINUED] bacitracin-polymyxin B 500-10,000 unit/gram topical ointment	 		intra-proc PRN	Richardson, Tyrun K, MD	 	 
•	[DISCONTINUED] sodium hypochlorite (DAKIN'S) 0.25% half-strength topical solution	 		intra-proc PRN	Richardson, Tyrun K, MD	 	200 mL at 01/02/24 1647
•	[DISCONTINUED] phenylephrine syringe 100 mcg	 100 mcg	IV	post-proc every 10 minutes PRN	Pallohusky, Brian S, MD	 	100 mcg at 01/02/24 1801
•	[DISCONTINUED] phenylephrine 50 mg in sodium chloride 0.9% 250 mL infusion	 0-1 mcg/kg/min	IV	titrate	Zguri, Liridon, MD	11.2 mL/hr at 01/02/24 2210	0.7 mcg/kg/min at 01/02/24 2210
•	[DISCONTINUED] OTHER	 		see admin instructions	Zguri, Liridon, MD	 	 
•	[DISCONTINUED] levothyroxine (SYNTHROID) tablet 50 mcg	 50 mcg	Oral	daily EARLY	Krazer, Kevin B, ANP	 	50 mcg at 01/03/24 0542
•	[DISCONTINUED] dextran 70-hypromellose PF (ARTIFICIAL TEARS) 0.1-0.3 % ophthalmic solution 1 Drop	 1 Drop	Both Eyes	every 4 hours PRN	Anand, Neesha, MD	 	 

Facility-Administered Medications Ordered in Other Encounters
Medication	Dose	Route	Frequency	Provider	Last Rate	Last Admin
•	EPINEPHrine PF 1 mg/mL (1:1,000) solution	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	0.01 mg at 01/03/24 1429
•	phenylephrine syringe	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	200 mcg at 01/03/24 1355
•	phenylephrine 20 mg in sodium chloride 0.9% 250 mL infusion	 	IV	intra-proc continuous PRN	Scott, Christy A, CRNA	15.008 mL/hr at 01/03/24 1516	0.3 mcg/kg/min at 01/03/24 1516
•	fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	50 mcg at 01/03/24 1545
•	sodium chloride 0.9% infusion	 	IV	intra-proc continuous PRN	Scott, Christy A, CRNA	 	New Bag at 01/03/24 1357
•	lactated ringers infusion	 	IV	intra-proc continuous PRN	Scott, Christy A, CRNA	 	New Bag at 01/03/24 1341
•	lidocaine PF 2% (XYLOCAINE MPF) injection	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	2 mL at 01/03/24 1352
•	propofoL (DIPRIVAN) injection	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	50 mg at 01/03/24 1353
•	rocuronium injection	 	IV	intra-proc PRN	Scott, Christy A, CRNA	 	30 mg at 01/03/24 1606
•	[DISCONTINUED] sodium chloride 0.9 % 250 mL flush bag 250 mL	 250 mL	IV	see admin instructions	Grogan, Susan K, FNP	 	Stopped at 01/02/24 1123
•	[DISCONTINUED] dexAMETHasone (DECADRON) 20 mg in sodium chloride 0.9% 100 mL IVPB (PREMIX)	 20 mg	IV	ONE time only	Snider, Jessica Nicole, DO	 	 
•	[DISCONTINUED] iron sucrose (VENOFER) 200 mg in sodium chloride 0.9% 110 mL IVPB (PREMIX)	 200 mg	IV	ONE time only	Snider, Jessica Nicole, DO	 	 
•	[DISCONTINUED] sodium chloride 0.9% infusion	 	IV	intra-proc continuous PRN	Schmitt, Adriel, CRNA	 	Stopped-Anesthesia at 01/02/24 1705
•	[DISCONTINUED] phenylephrine 20 mg in sodium chloride 0.9% 250 mL infusion	 	IV	intra-proc continuous PRN	Schmitt, Adriel, CRNA	 	Stopped at 01/02/24 1654
•	[DISCONTINUED] fentaNYL PF (SUBLIMAZE) 50 mcg/mL injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	25 mcg at 01/02/24 1559
•	[DISCONTINUED] propofoL (DIPRIVAN) injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	60 mg at 01/02/24 1542
•	[DISCONTINUED] ondansetron (ZOFRAN) 4 mg/2 mL injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	4 mg at 01/02/24 1546
•	[DISCONTINUED] dexAMETHasone (DECADRON) injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	8 mg at 01/02/24 1546
•	[DISCONTINUED] lidocaine PF 2% (XYLOCAINE MPF) injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	4 mL at 01/02/24 1542
•	[DISCONTINUED] phenylephrine injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	100 mcg at 01/02/24 1604
•	[DISCONTINUED] ePHEDrine injection	 	IV	intra-proc PRN	Schmitt, Adriel, CRNA	 	10 mg at 01/02/24 1639




"""

# master = functions.MasterClass(text_input)
# print(SickleCellCrisis("Sickle cell crisis", master))

