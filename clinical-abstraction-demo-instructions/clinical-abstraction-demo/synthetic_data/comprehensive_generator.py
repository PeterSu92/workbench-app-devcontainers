#!/usr/bin/env python3
"""
Comprehensive Synthetic Clinical Note Generator
Generates realistic cardiology clinical notes with known ground truth values
for testing and validating the clinical abstraction system.
"""

import random
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class ClinicalNoteGenerator:
    """Generate synthetic clinical notes with ground truth annotations."""

    def __init__(self, seed=42):
        random.seed(seed)
        self.patient_counter = 1000

    def generate_patient_name(self):
        """Generate a random patient name."""
        first_names = [
            "John", "Mary", "James", "Patricia", "Robert", "Jennifer",
            "Michael", "Linda", "William", "Barbara", "David", "Elizabeth",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
            "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Margaret"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
            "Martin", "Lee", "Perez", "Thompson", "White", "Harris"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def generate_mrn(self):
        """Generate a medical record number."""
        self.patient_counter += 1
        return str(self.patient_counter)

    def generate_dob(self, age_range=(40, 85)):
        """Generate date of birth for given age range."""
        age = random.randint(*age_range)
        dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 364))
        return dob.strftime("%m/%d/%Y")

    def generate_cardiology_note(self, scenario="heart_failure"):
        """Generate a cardiology consultation note."""

        scenarios = {
            "heart_failure": self._generate_heart_failure_note,
            "cad": self._generate_cad_note,
            "arrhythmia": self._generate_arrhythmia_note,
            "valvular": self._generate_valvular_note,
            "hypertension": self._generate_hypertension_note
        }

        generator = scenarios.get(scenario, self._generate_heart_failure_note)
        return generator()

    def generate_oncology_note(self, scenario="breast_cancer"):
        """Generate an oncology consultation note."""

        scenarios = {
            "breast_cancer": self._generate_breast_cancer_note,
            "lung_cancer": self._generate_lung_cancer_note,
            "colorectal_cancer": self._generate_colorectal_cancer_note
        }

        generator = scenarios.get(scenario, self._generate_breast_cancer_note)
        return generator()

    def _generate_heart_failure_note(self):
        """Generate a heart failure consultation note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(55, 85))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        # Ground truth values
        nyha_class = random.choice(["I", "II", "III", "IV"])
        ef = random.randint(15, 55)  # Reduced EF for HFrEF
        bnp = random.randint(100, 2000)
        systolic_bp = random.randint(90, 160)
        diastolic_bp = random.randint(50, 100)
        hr = random.randint(60, 110)
        creatinine = round(random.uniform(0.8, 2.5), 1)

        # Generate symptoms based on NYHA class
        symptoms = {
            "I": "No limitations. No symptoms with ordinary activity.",
            "II": "Mild symptoms with ordinary activity. Comfortable at rest.",
            "III": "Marked limitation of activity. Comfortable only at rest.",
            "IV": "Symptoms at rest. Severe limitations."
        }

        # Generate exam findings
        jvd_present = nyha_class in ["III", "IV"]
        s3_gallop = nyha_class in ["III", "IV"] or random.random() < 0.3
        rales = nyha_class in ["III", "IV"] or random.random() < 0.4
        edema = random.choice(["none", "trace", "1+", "2+", "3+"])

        note = f"""CARDIOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

CHIEF COMPLAINT:
{"Worsening shortness of breath and fatigue" if nyha_class in ["III", "IV"] else "Follow-up for heart failure management"}

HISTORY OF PRESENT ILLNESS:
{65 + int(mrn) % 20} y/o {"M" if random.random() < 0.6 else "F"} with history of heart failure presents for {"routine" if nyha_class in ["I", "II"] else "urgent"} evaluation. {symptoms[nyha_class]} {"Reports difficulty climbing stairs and performing daily activities." if nyha_class in ["III", "IV"] else "Generally doing well with current medications."} {"Denies chest pain but notes occasional palpitations." if random.random() < 0.4 else "Denies chest pain or palpitations."}

PAST MEDICAL HISTORY:
- Congestive Heart Failure (CHF), diagnosed {random.randint(1, 8)} years ago
- Hypertension
{"- Type 2 Diabetes Mellitus" if random.random() < 0.5 else ""}
{"- Coronary Artery Disease, s/p CABG " + str(datetime.now().year - random.randint(2, 10)) if random.random() < 0.3 else ""}
{"- Atrial Fibrillation" if random.random() < 0.4 else ""}

MEDICATIONS:
- Furosemide {random.choice(["20", "40", "80"])} mg daily
- Carvedilol {random.choice(["6.25", "12.5", "25"])} mg BID
- Lisinopril {random.choice(["10", "20", "40"])} mg daily
{"- Spironolactone 25 mg daily" if random.random() < 0.5 else ""}
{"- Digoxin 0.125 mg daily" if random.random() < 0.3 else ""}

PHYSICAL EXAMINATION:
Vital Signs:
- BP: {systolic_bp}/{diastolic_bp} mmHg
- HR: {hr} bpm
- RR: {random.randint(14, 22)}
- O2 Sat: {random.randint(92, 98)}% on room air
- Weight: {random.randint(150, 250)} lbs

General: {"Alert and oriented, appears" if nyha_class in ["I", "II"] else "Alert and oriented, appears fatigued and"}
Cardiovascular: {"Regular rhythm" if random.random() < 0.7 else "Irregularly irregular rhythm"}, {"S3 gallop present" if s3_gallop else "no S3"}, {"JVD at " + str(random.randint(8, 12)) + " cm" if jvd_present else "JVD not elevated"}
Respiratory: {"Bilateral rales at bases" if rales else "Clear to auscultation bilaterally"}
Extremities: {edema} pitting edema bilateral lower extremities

ASSESSMENT:
NYHA Class {nyha_class} heart failure {"with reduced ejection fraction (HFrEF)" if ef < 40 else "with mid-range ejection fraction"}. {"Evidence of volume overload." if nyha_class in ["III", "IV"] else "Currently compensated."}

LABS (collected {visit_date}):
- BNP: {bnp} pg/mL {"(elevated)" if bnp > 400 else "(normal to mildly elevated)"}
- Creatinine: {creatinine} mg/dL
- Sodium: {random.randint(135, 142)} mEq/L
- Potassium: {round(random.uniform(3.5, 5.0), 1)} mEq/L
{"- Hemoglobin: " + str(round(random.uniform(10.5, 15.0), 1)) + " g/dL" if random.random() < 0.5 else ""}

ECHOCARDIOGRAM ({visit_date}):
- Left ventricular ejection fraction (LVEF): {ef}%
- {"Moderate" if random.random() < 0.5 else "Severe"} left ventricular dilation
- {"Mild" if random.random() < 0.6 else "Moderate"} mitral regurgitation
{"- Dilated left atrium" if random.random() < 0.5 else ""}

PLAN:
{"1. Increase furosemide to " + str(random.choice([40, 60, 80])) + " mg BID" if nyha_class in ["III", "IV"] else "1. Continue current diuretic dose"}
2. {"Uptitrate" if nyha_class in ["I", "II"] else "Continue"} carvedilol
3. Continue ACE inhibitor
{"4. Strict fluid restriction 2L/day" if nyha_class in ["III", "IV"] else "4. Maintain current fluid intake"}
5. Daily weights
6. Follow-up in {random.choice(["1", "2", "4"])} weeks

Dr. {random.choice(["Sarah Johnson", "Michael Chen", "Emily Rodriguez", "James Wilson", "Lisa Anderson"])}
Cardiology
"""

        ground_truth = {
            "nyha_class": nyha_class,
            "ejection_fraction": ef,
            "bnp": bnp,
            "blood_pressure_systolic": systolic_bp,
            "blood_pressure_diastolic": diastolic_bp,
            "heart_rate": hr,
            "creatinine": creatinine
        }

        return note, ground_truth

    def _generate_cad_note(self):
        """Generate a coronary artery disease note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(50, 80))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        # Ground truth values
        ef = random.randint(45, 65)  # Normal to mildly reduced EF
        systolic_bp = random.randint(110, 150)
        diastolic_bp = random.randint(60, 90)
        hr = random.randint(55, 85)
        ldl = random.randint(70, 180)
        troponin = round(random.uniform(0.01, 0.5), 3) if random.random() < 0.3 else 0.00

        note = f"""CARDIOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

CHIEF COMPLAINT:
{"Chest pain with exertion" if random.random() < 0.6 else "Follow-up post-cardiac catheterization"}

HISTORY OF PRESENT ILLNESS:
{60 + int(mrn) % 15} y/o {"M" if random.random() < 0.7 else "F"} with history of coronary artery disease presents with {"typical anginal symptoms" if random.random() < 0.5 else "atypical chest discomfort"}. {"Symptoms occur with moderate exertion, relieved by rest." if random.random() < 0.5 else "Denies current chest pain."} Patient has history of {"MI in " + str(datetime.now().year - random.randint(1, 5)) if random.random() < 0.4 else "stable angina"}. {"Currently compliant with dual antiplatelet therapy." if random.random() < 0.5 else ""}

PAST MEDICAL HISTORY:
- Coronary Artery Disease
{"- s/p PCI with stent placement to LAD " + str(datetime.now().year - random.randint(1, 3)) if random.random() < 0.6 else ""}
{"- s/p CABG " + str(datetime.now().year - random.randint(3, 10)) if random.random() < 0.3 else ""}
- Hypertension
- Hyperlipidemia
{"- Type 2 Diabetes" if random.random() < 0.5 else ""}

MEDICATIONS:
- Aspirin 81 mg daily
- Atorvastatin {random.choice(["40", "80"])} mg daily
- Metoprolol {random.choice(["25", "50", "100"])} mg BID
{"- Clopidogrel 75 mg daily" if random.random() < 0.5 else ""}
- Lisinopril {random.choice(["10", "20"])} mg daily

PHYSICAL EXAMINATION:
Vital Signs:
- BP: {systolic_bp}/{diastolic_bp} mmHg
- HR: {hr} bpm
- RR: {random.randint(12, 18)}
- O2 Sat: {random.randint(96, 99)}% on room air

General: Well-appearing, no acute distress
Cardiovascular: Regular rate and rhythm, no murmurs
Respiratory: Clear to auscultation bilaterally
Extremities: No edema, pulses intact

LABS:
- Troponin: {troponin} ng/mL {"(elevated)" if troponin > 0.04 else "(negative)"}
- LDL: {ldl} mg/dL
- HDL: {random.randint(35, 65)} mg/dL
- Triglycerides: {random.randint(100, 250)} mg/dL

ECHOCARDIOGRAM:
- LVEF: {ef}%
{"- Regional wall motion abnormalities in " + random.choice(["anterior", "inferior", "lateral"]) + " wall" if random.random() < 0.4 else "- No regional wall motion abnormalities"}

PLAN:
1. {"Increase" if ldl > 100 else "Continue"} statin therapy
2. Continue antiplatelet therapy
3. {"Consider stress test" if random.random() < 0.3 else "Continue medical management"}
4. Lifestyle modifications
5. Follow-up in {random.choice(["3", "6"])} months

Dr. {random.choice(["David Martinez", "Jennifer Lee", "Robert Thompson"])}
Cardiology
"""

        ground_truth = {
            "ejection_fraction": ef,
            "blood_pressure_systolic": systolic_bp,
            "blood_pressure_diastolic": diastolic_bp,
            "heart_rate": hr,
            "ldl_cholesterol": ldl,
            "troponin": troponin
        }

        return note, ground_truth

    def _generate_arrhythmia_note(self):
        """Generate an arrhythmia note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(45, 85))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        # Ground truth values
        af_type = random.choice(["paroxysmal", "persistent", "permanent"])
        hr = random.randint(80, 140) if af_type != "permanent" else random.randint(60, 100)
        ef = random.randint(50, 65)
        chadsvasc = random.randint(2, 6)

        note = f"""CARDIOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

CHIEF COMPLAINT:
{"Palpitations and irregular heartbeat" if random.random() < 0.6 else "Follow-up for atrial fibrillation"}

HISTORY OF PRESENT ILLNESS:
{68 + int(mrn) % 18} y/o {"M" if random.random() < 0.5 else "F"} with history of {af_type} atrial fibrillation presents {"complaining of palpitations and lightheadedness" if random.random() < 0.5 else "for routine follow-up"}. {"Episodes last several hours" if af_type == "paroxysmal" else "Patient remains in atrial fibrillation"}. {"Compliant with rate control medications." if random.random() < 0.7 else "Reports medication non-compliance."}

PAST MEDICAL HISTORY:
- Atrial Fibrillation ({af_type})
- Hypertension
{"- Heart Failure (HFpEF)" if random.random() < 0.3 else ""}
{"- Stroke/TIA " + str(datetime.now().year - random.randint(2, 8)) if chadsvasc > 4 else ""}
{"- Diabetes" if random.random() < 0.4 else ""}

MEDICATIONS:
- {"Apixaban 5 mg BID" if random.random() < 0.5 else "Warfarin (target INR 2-3)"}
- Metoprolol {random.choice(["50", "100", "200"])} mg BID
{"- Diltiazem 240 mg daily" if random.random() < 0.3 else ""}

PHYSICAL EXAMINATION:
Vital Signs:
- BP: {random.randint(110, 150)}/{random.randint(65, 90)} mmHg
- HR: {hr} bpm (irregularly irregular)
- RR: {random.randint(14, 20)}

General: Well-appearing
Cardiovascular: Irregularly irregular rhythm, no murmurs
Respiratory: Clear bilaterally

EKG:
Atrial fibrillation with {"rapid" if hr > 100 else "controlled"} ventricular response, rate {hr} bpm

ECHOCARDIOGRAM:
- LVEF: {ef}%
- Left atrial enlargement
- No significant valvular disease

ASSESSMENT:
{af_type.capitalize()} atrial fibrillation, {"poorly" if hr > 110 else "adequately"} rate controlled
CHA2DS2-VASc score: {chadsvasc}

PLAN:
1. {"Uptitrate" if hr > 100 else "Continue"} rate control medications
2. Continue anticoagulation
{"3. Consider ablation given symptomatic paroxysmal AF" if af_type == "paroxysmal" else "3. Continue medical management"}
4. Follow-up in {random.choice(["1", "3", "6"])} months

Dr. {random.choice(["Amanda Foster", "Kevin Park"])}
Electrophysiology
"""

        ground_truth = {
            "rhythm": "atrial_fibrillation",
            "af_type": af_type,
            "heart_rate": hr,
            "ejection_fraction": ef,
            "chadsvasc_score": chadsvasc
        }

        return note, ground_truth

    def _generate_valvular_note(self):
        """Generate a valvular heart disease note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(55, 85))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        valve_type = random.choice(["aortic_stenosis", "mitral_regurgitation", "aortic_regurgitation"])
        severity = random.choice(["mild", "moderate", "severe"])
        ef = random.randint(50, 70) if severity != "severe" else random.randint(35, 60)

        note = f"""CARDIOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

CHIEF COMPLAINT:
{"Dyspnea on exertion" if severity == "severe" else "Follow-up for valvular heart disease"}

HISTORY OF PRESENT ILLNESS:
{72 + int(mrn) % 15} y/o {"M" if random.random() < 0.6 else "F"} with history of {valve_type.replace("_", " ")} presents for evaluation. {"Reports worsening shortness of breath with activity." if severity == "severe" else "Generally asymptomatic."}

PAST MEDICAL HISTORY:
- {valve_type.replace("_", " ").title()}
- Hypertension
{"- Heart Failure" if severity == "severe" else ""}

PHYSICAL EXAMINATION:
Vital Signs:
- BP: {random.randint(110, 160)}/{random.randint(60, 90)} mmHg
- HR: {random.randint(60, 90)} bpm

Cardiovascular: {"Harsh systolic ejection murmur at right upper sternal border radiating to carotids" if valve_type == "aortic_stenosis" else "Holosystolic murmur at apex radiating to axilla" if valve_type == "mitral_regurgitation" else "Diastolic decrescendo murmur"}

ECHOCARDIOGRAM:
- {valve_type.replace("_", " ").title()}: {severity.capitalize()}
- LVEF: {ef}%
{"- Peak gradient: " + str(random.randint(40, 80)) + " mmHg" if valve_type == "aortic_stenosis" else ""}

PLAN:
{"1. Refer to cardiac surgery for valve replacement" if severity == "severe" else "1. Continue monitoring"}
2. Follow-up in {random.choice(["3", "6", "12"])} months

Dr. {random.choice(["Patricia Kim", "Steven Wu"])}
Cardiology
"""

        ground_truth = {
            "valve_disease": valve_type,
            "valve_severity": severity,
            "ejection_fraction": ef
        }

        return note, ground_truth

    def _generate_hypertension_note(self):
        """Generate a hypertension management note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(40, 75))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        systolic_bp = random.randint(130, 180)
        diastolic_bp = random.randint(80, 110)
        hr = random.randint(60, 90)

        note = f"""CARDIOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

CHIEF COMPLAINT:
Hypertension management

HISTORY OF PRESENT ILLNESS:
{58 + int(mrn) % 20} y/o {"M" if random.random() < 0.5 else "F"} with history of hypertension presents for follow-up. {"Blood pressures at home range 140-160/85-95." if systolic_bp > 140 else "Reports improved blood pressure control with current regimen."}

PAST MEDICAL HISTORY:
- Hypertension
{"- Type 2 Diabetes" if random.random() < 0.5 else ""}
{"- Chronic Kidney Disease Stage 3" if random.random() < 0.3 else ""}

MEDICATIONS:
- Lisinopril {random.choice(["10", "20", "40"])} mg daily
{"- Amlodipine " + random.choice(["5", "10"]) + " mg daily" if random.random() < 0.5 else ""}
{"- Hydrochlorothiazide 25 mg daily" if random.random() < 0.4 else ""}

PHYSICAL EXAMINATION:
Vital Signs:
- BP: {systolic_bp}/{diastolic_bp} mmHg
- HR: {hr} bpm
- BMI: {round(random.uniform(24.0, 35.0), 1)}

General: Well-appearing
Cardiovascular: Regular rate and rhythm

PLAN:
{"1. Increase antihypertensive medications" if systolic_bp > 140 else "1. Continue current regimen"}
2. Home blood pressure monitoring
3. Lifestyle modifications
4. Follow-up in {random.choice(["1", "3"])} months

Dr. {random.choice(["Michelle Chang", "Daniel Brown"])}
Cardiology
"""

        ground_truth = {
            "blood_pressure_systolic": systolic_bp,
            "blood_pressure_diastolic": diastolic_bp,
            "heart_rate": hr
        }

        return note, ground_truth

    def _generate_breast_cancer_note(self):
        """Generate a breast cancer oncology note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(45, 75))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        stage = random.choice(["IA", "IB", "IIA", "IIB", "IIIA", "IIIB", "IV"])
        her2_status = random.choice(["positive", "negative"])
        er_status = random.choice(["positive", "negative"])
        pr_status = random.choice(["positive", "negative"])
        ecog = random.choice([0, 1, 2])

        note = f"""ONCOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

DIAGNOSIS:
Invasive ductal carcinoma of the breast, Stage {stage}

HISTORY OF PRESENT ILLNESS:
{55 + int(mrn) % 20} y/o {"F" if random.random() < 0.9 else "M"} presenting for oncology consultation following recent diagnosis of breast cancer. Patient underwent diagnostic mammogram which showed suspicious mass, followed by core needle biopsy confirming invasive ductal carcinoma.

PATHOLOGY:
- Tumor size: {round(random.uniform(0.5, 5.0), 1)} cm
- Grade: {random.choice(["1", "2", "3"])}
- ER: {er_status} ({random.randint(0, 100)}%)
- PR: {pr_status} ({random.randint(0, 100)}%)
- HER2: {her2_status}
- Ki-67: {random.randint(5, 40)}%
{"- Lymph nodes: " + str(random.randint(0, 8)) + " positive nodes" if random.random() < 0.4 else "- Lymph nodes: negative"}

PERFORMANCE STATUS:
ECOG {ecog}

PHYSICAL EXAMINATION:
General: {"Well-appearing, no acute distress" if ecog == 0 else "Appears fatigued"}
Breast: {"Palpable mass right upper outer quadrant" if random.random() < 0.5 else "Post-surgical changes"}
Lymph nodes: {"No palpable axillary lymphadenopathy" if random.random() < 0.7 else "Palpable axillary nodes"}

TREATMENT PLAN:
{f"1. Neoadjuvant chemotherapy - AC-T regimen" if stage in ["IIA", "IIB", "IIIA", "IIIB"] else "1. Surgical consultation for lumpectomy vs mastectomy"}
{"2. Trastuzumab (Herceptin) given HER2+ status" if her2_status == "positive" else "2. Endocrine therapy planned given ER+ status" if er_status == "positive" else "2. Chemotherapy planned"}
3. Genetic counseling and BRCA testing
4. Radiation oncology consultation
5. Follow-up in 2 weeks

Dr. {random.choice(["Emily Roberts", "Maria Santos", "Jennifer Lee"])}
Medical Oncology
"""

        ground_truth = {
            "cancer_type": "breast_cancer",
            "cancer_stage": stage,
            "her2_status": her2_status,
            "er_status": er_status,
            "pr_status": pr_status,
            "ecog_performance_status": ecog
        }

        return note, ground_truth

    def _generate_lung_cancer_note(self):
        """Generate a lung cancer oncology note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(55, 80))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        stage = random.choice(["IA", "IB", "IIA", "IIB", "IIIA", "IIIB", "IV"])
        histology = random.choice(["adenocarcinoma", "squamous cell carcinoma", "small cell carcinoma"])
        ecog = random.choice([0, 1, 2, 3])
        pdl1 = random.randint(0, 90)

        note = f"""ONCOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

DIAGNOSIS:
Non-small cell lung cancer ({histology}), Stage {stage}

HISTORY OF PRESENT ILLNESS:
{65 + int(mrn) % 15} y/o {"M" if random.random() < 0.6 else "F"} with {random.randint(20, 60)}-pack-year smoking history presents with newly diagnosed lung cancer. Initial presentation with {"persistent cough and hemoptysis" if random.random() < 0.5 else "incidental finding on chest CT"}.

PATHOLOGY:
- Histology: {histology}
- PD-L1 expression: {pdl1}%
{"- EGFR: mutation detected" if random.random() < 0.15 else "- EGFR: wild type"}
{"- ALK: rearrangement positive" if random.random() < 0.05 else "- ALK: negative"}

IMAGING:
- Primary tumor: {"right" if random.random() < 0.5 else "left"} upper lobe, {round(random.uniform(1.5, 6.0), 1)} cm
{"- Mediastinal lymphadenopathy present" if stage in ["IIIA", "IIIB", "IV"] else "- No lymphadenopathy"}
{"- Distant metastases: liver, bone" if stage == "IV" else "- No distant metastases"}

PERFORMANCE STATUS:
ECOG {ecog}

PLAN:
{f"1. Platinum-based chemotherapy with pembrolizumab (given PD-L1 {pdl1}%)" if pdl1 > 50 else "1. Platinum-doublet chemotherapy"}
2. Radiation oncology consultation
3. Smoking cessation counseling
4. Supportive care consultation
5. Follow-up imaging in 8 weeks

Dr. {random.choice(["David Chen", "Susan Miller"])}
Thoracic Oncology
"""

        ground_truth = {
            "cancer_type": "lung_cancer",
            "cancer_stage": stage,
            "histology": histology,
            "ecog_performance_status": ecog,
            "pdl1_expression": pdl1
        }

        return note, ground_truth

    def _generate_colorectal_cancer_note(self):
        """Generate a colorectal cancer oncology note."""
        name = self.generate_patient_name()
        mrn = self.generate_mrn()
        dob = self.generate_dob(age_range=(50, 75))
        visit_date = datetime.now().strftime("%m/%d/%Y")

        stage = random.choice(["I", "II", "IIA", "IIB", "III", "IIIA", "IIIB", "IIIC", "IV"])
        location = random.choice(["cecum", "ascending colon", "transverse colon", "descending colon", "sigmoid colon", "rectum"])
        msi_status = random.choice(["MSI-High", "MSS", "MSI-Low"])
        ecog = random.choice([0, 1, 2])

        note = f"""ONCOLOGY CONSULTATION NOTE

Patient: {name}
MRN: {mrn}
DOB: {dob}
Visit Date: {visit_date}

DIAGNOSIS:
Colorectal adenocarcinoma ({location}), Stage {stage}

HISTORY OF PRESENT ILLNESS:
{62 + int(mrn) % 15} y/o {"M" if random.random() < 0.5 else "F"} with recent diagnosis of colorectal cancer. Patient underwent colonoscopy for {"screening" if random.random() < 0.5 else "evaluation of rectal bleeding"} which revealed mass in {location}.

PATHOLOGY:
- Location: {location}
- Grade: {random.choice(["well differentiated", "moderately differentiated", "poorly differentiated"])}
- Tumor size: {round(random.uniform(2.0, 8.0), 1)} cm
- Microsatellite status: {msi_status}
{"- KRAS: mutation detected" if random.random() < 0.4 else "- KRAS: wild type"}
{"- NRAS: mutation detected" if random.random() < 0.15 else "- NRAS: wild type"}
{"- BRAF: V600E mutation" if random.random() < 0.1 else "- BRAF: wild type"}
- Lymph nodes: {random.randint(0, 12)} positive / {random.randint(12, 20)} examined

PERFORMANCE STATUS:
ECOG {ecog}

CEA: {round(random.uniform(1.0, 250.0), 1)} ng/mL

STAGING:
{"- Liver metastases present" if stage == "IV" else "- No distant metastases"}
{"- Peritoneal involvement" if stage == "IV" and random.random() < 0.3 else ""}

PLAN:
{"1. Surgical resection planned" if stage in ["I", "II", "IIA", "IIB"] else "1. Neoadjuvant FOLFOX chemotherapy"}
{"2. Adjuvant chemotherapy (FOLFOX or CAPOX)" if stage in ["III", "IIIA", "IIIB", "IIIC"] else "2. Immunotherapy consideration given MSI-High status" if msi_status == "MSI-High" else "2. Palliative chemotherapy with bevacizumab"}
3. Genetic counseling for Lynch syndrome
4. Nutritional support
5. Follow-up in 2 weeks

Dr. {random.choice(["Robert Kim", "Patricia Nguyen"])}
Gastrointestinal Oncology
"""

        ground_truth = {
            "cancer_type": "colorectal_cancer",
            "cancer_stage": stage,
            "tumor_location": location,
            "msi_status": msi_status,
            "ecog_performance_status": ecog
        }

        return note, ground_truth


def main():
    """Generate a comprehensive set of synthetic clinical notes."""
    print("=" * 60)
    print("Comprehensive Synthetic Clinical Note Generator")
    print("=" * 60)
    print()

    generator = ClinicalNoteGenerator(seed=42)
    output_dir = Path(__file__).parent / "generated_notes"
    output_dir.mkdir(exist_ok=True)

    # Generate cardiology notes
    cardiology_scenarios = [
        ("heart_failure", 15),
        ("cad", 10),
        ("arrhythmia", 8),
        ("valvular", 5),
        ("hypertension", 7)
    ]

    # Generate oncology notes
    oncology_scenarios = [
        ("breast_cancer", 10),
        ("lung_cancer", 8),
        ("colorectal_cancer", 7)
    ]

    all_notes = []

    for scenario, count in cardiology_scenarios:
        print(f"Generating {count} {scenario.replace('_', ' ').title()} notes...")
        for i in range(count):
            note, ground_truth = generator.generate_cardiology_note(scenario)

            # Save individual note
            filename = f"cardio_{scenario}_{i+1:03d}.txt"
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(note)

            # Collect for summary
            all_notes.append({
                "filename": filename,
                "scenario": f"cardiology_{scenario}",
                "ground_truth": ground_truth
            })

    for scenario, count in oncology_scenarios:
        print(f"Generating {count} {scenario.replace('_', ' ').title()} notes...")
        for i in range(count):
            note, ground_truth = generator.generate_oncology_note(scenario)

            # Save individual note
            filename = f"onc_{scenario}_{i+1:03d}.txt"
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(note)

            # Collect for summary
            all_notes.append({
                "filename": filename,
                "scenario": f"oncology_{scenario}",
                "ground_truth": ground_truth
            })

    # Save ground truth JSON
    ground_truth_file = output_dir / "ground_truth.json"
    with open(ground_truth_file, 'w') as f:
        json.dump(all_notes, f, indent=2)

    print()
    print(f"✓ Generated {len(all_notes)} clinical notes")
    print(f"✓ Saved to: {output_dir}")
    print(f"✓ Ground truth saved to: {ground_truth_file}")
    print()
    print("Summary:")
    print("  Cardiology:")
    for scenario, count in cardiology_scenarios:
        print(f"    - {scenario.replace('_', ' ').title()}: {count} notes")
    print("  Oncology:")
    for scenario, count in oncology_scenarios:
        print(f"    - {scenario.replace('_', ' ').title()}: {count} notes")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
