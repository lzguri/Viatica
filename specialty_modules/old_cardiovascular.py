import functions
import disease_database as disb
import drug_reference as drugs
import disease_reference as disr



class Cardiac(functions.MasterClass):

    def __init__ (self, file_contents):
        super().__init__(file_contents)
        self.disorders = disb.acute_disorders
        self.cardiac = self.disorders['cardiac']
        ### Medicaitons ###
        self.anticoagulants = self.find_medication(self.cardiac['anticoagulation meds'])
        self.cholesterol_meds = self.find_medication(self.cardiac['cholesterol meds'])
        self.antiplatelets = self.find_medication(self.cardiac['anti_platelet meds'])
        self.heartfailure_meds = self.find_medication(self.cardiac['heart_failure meds'] + self.cardiac['diuretics meds'])

        ### Tests ###
        self.cardiac_tests = self.get_multiple_test_results(self.cardiac['cardiac profile tests'])
        self.electrolyte_tests = self.get_multiple_test_results(self.cardiac['electrolyte tests'])
        self.n = '\n'

    def heparin_drip(self):

        ''' checks if the patient is on anticoagulation at home, if you need to start heparin it will let you know if bolus is needed, and which lab to monitor'''
        if self.anticoagulants:
            return f"""- Start heparin drip wo bolus [{''.join(self.anticoagulants)}], monitor per PTT/protocol [{self.get_multiple_test_results('HGB', 'PLT')}]
            - Hold {''.join(self.anticoagulants)} [Started on heparin]
            """
        else:
            return f"- Start heparin drip, monitor per protocol [{self.get_multiple_test_results('HGB', 'PLT')}]"

    def nitroglycerin_use(self):

        '''checks if the patient is taking sildenafil class and warns you for concomitant use of nitroglycerin'''

        list3 = [i for i in drugs.Medications['PDE 5 Inhibitors'] if i in self.file_contents]
        if list3:
            return f'- Nitroglycerin PRN for chest pain [Patient is on {"".join(list3)}***]'
        else:
            return f'- Nitroglycerin PRN for chest pain'

    def assessment(self):

        ''' general assessment for cardiovascular disease, rate controlling agents, troponin,probnp levels, along with electrolytes levels, home meds'''

        assessment = self.cardiac['assessment']
        home_meds = self.find_medication(self.cardiac['rate_controling meds'])
        return f"{self.n.join(assessment)}\n{self.cardiac_tests}\n{self.electrolyte_tests}\n{home_meds}"

    def plan(self):
        cardiac_plan = self.cardiac['plan']
        missing_tests = self.check_missing_tests(self.cardiac['cardiac profile tests'] + self.cardiac['electrolyte tests'], self.cardiac_tests +' '+ self.electrolyte_tests )
        return f"{missing_tests}\n{self.n.join(cardiac_plan)}"



class NSTEMI(Cardiac, functions.MasterClass):
    
    def __init__ (self, file_contents):
        super().__init__(file_contents)
        self.disorders = disb.acute_disorders['nstemi']


    def nstemi_assess_plan(self):
        already_on_antiplatelets = self.antiplatelets if self.antiplatelets else 'Patient is not on antiplatelets'
        already_on_statins = self.cholesterol_meds if self.cholesterol_meds else 'Patient is not on high-intensity statin'
        if self.check_name(disr.Cardiology_AD['NSTEMI']):
            return f"""+NSTEMI\n{self.assessment()}
                {self.n.join(self.disorders['assessment'])}
                {already_on_antiplatelets}
                {already_on_statins}
                Plan
                {self.heparin_drip()}
                {self.nitroglycerin_use()}
                {self.cont_or_hold_meds(*(self.cardiac['cholesterol meds'] + self.cardiac['anti_platelet meds']))}
                {self.plan()}
                {self.n.join(self.disorders['plan'])}"""
        else:
            return ''


class AFIB(Cardiac, functions.MasterClass):
    
    def __init__ (self, file_contents):
        super().__init__(file_contents)
        self.disorders = disb.acute_disorders['atrial_fibrillation']


    def afib_assess_plan(self):
        already_on_anticoagulation = self.anticoagulants if self.anticoagulants else self.n.join(['Patient is not on anticoagulation', 'CHADVASC ***'])
        if self.check_name(disr.Cardiology_AD['AFIB w RVR']):
            return f"""+ATRIAL FIB. WITH RVR\n{self.assessment()}
                
                {already_on_anticoagulation}
                Plan
                {self.cont_or_hold_meds(*(self.cardiac['anticoagulation meds'] + self.cardiac['rate_controling meds'] + self.cardiac['antiarrhythmic meds']))}
                {self.plan()}
                {self.n.join(self.disorders['plan'])}"""
        else:
            return ''



class CHFEXACERBATION(Cardiac, functions.MasterClass):
    
    def __init__ (self, file_contents):
        super().__init__(file_contents)
        self.disorders = disb.acute_disorders['acute heart failure']


    def hf_assess_plan(self):
        if self.check_name(disr.Cardiology_AD['CHF exacerbation']):
            return f"""+CHF EXACERBATION\n{self.assessment()}
                {self.heartfailure_meds}
                Plan
                {self.cont_or_hold_meds(*(self.cardiac['heart_failure meds'] + self.cardiac['rate_controling meds'] + self.cardiac['diuretics meds']))}
                {self.plan()}
                {self.n.join(self.disorders['plan'])}"""
        else:
            return ''



with open('file.txt', 'r') as f:
    file1 = f.read()


