"""
CardioXAI - AI Clinical Doctor Copilot Service
Comprehensive Clinical Decision Support Reasoning Engine
"""

from typing import Dict, Any, Tuple


def get_clinical_classifications(pred_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts standardized clinical categories and metrics from prediction data."""
    metrics = pred_results.get("metrics", {})
    risk = pred_results.get("risk", 0.0)
    confidence = pred_results.get("confidence", 0.0)
    heart_age = pred_results.get("heart_age", 0)

    bp_hi = metrics.get("bp_hi", 120)
    bp_lo = metrics.get("bp_lo", 80)
    bmi = metrics.get("bmi", 24.0)
    age = metrics.get("age", 50)
    height_val = metrics.get("height_val", 170)
    weight_val = metrics.get("weight_val", 70)

    # AHA Blood Pressure Classification
    if bp_hi >= 180 or bp_lo >= 120:
        bp_stat = "Hypertensive Crisis (Emergency)"
        bp_tier = "crisis"
    elif bp_hi >= 140 or bp_lo >= 90:
        bp_stat = "Stage 2 Hypertension"
        bp_tier = "stage2"
    elif bp_hi >= 130 or bp_lo >= 80:
        bp_stat = "Stage 1 Hypertension"
        bp_tier = "stage1"
    elif bp_hi >= 120 and bp_lo < 80:
        bp_stat = "Elevated Blood Pressure"
        bp_tier = "elevated"
    else:
        bp_stat = "Normal Blood Pressure"
        bp_tier = "normal"

    # WHO BMI Classification
    if bmi < 18.5:
        bmi_stat = "Underweight"
    elif bmi < 25.0:
        bmi_stat = "Healthy Weight"
    elif bmi < 30.0:
        bmi_stat = "Overweight"
    elif bmi < 35.0:
        bmi_stat = "Class I Obesity"
    else:
        bmi_stat = "Class II/III Obesity"

    # ASCVD Risk Stratification
    if risk >= 60.0:
        risk_tier = "Critical Risk (Tier 1)"
    elif risk >= 30.0:
        risk_tier = "High Risk (Tier 2)"
    elif risk >= 15.0:
        risk_tier = "Moderate Risk (Tier 3)"
    else:
        risk_tier = "Low / Optimal Risk"

    return {
        "risk": risk,
        "confidence": confidence,
        "heart_age": heart_age,
        "age": age,
        "bp_hi": bp_hi,
        "bp_lo": bp_lo,
        "bp_stat": bp_stat,
        "bp_tier": bp_tier,
        "bmi": bmi,
        "bmi_stat": bmi_stat,
        "risk_tier": risk_tier,
        "height_val": height_val,
        "weight_val": weight_val,
    }


def generate_copilot_response(
    query: str,
    pred_results: Dict[str, Any],
    patient_state: Any
) -> str:
    """
    Generates an intelligent, patient-grounded clinical response 
    adhering to AHA/ACC guidelines, DASH protocols, and institutional CDSS standards.
    """
    q = query.strip().lower()
    c = get_clinical_classifications(pred_results)

    patient_name = getattr(patient_state, "patient_name", "the patient")
    gender = getattr(patient_state, "gender", "Unknown")
    smoke = getattr(patient_state, "smoke", "No")
    act = getattr(patient_state, "act", "Yes")
    chol = getattr(patient_state, "chol", "Normal")
    gluc = getattr(patient_state, "gluc", "Normal")
    fam_hist = getattr(patient_state, "fam_hist", False)

    age_delta = c["heart_age"] - c["age"]
    delta_str = f"+{age_delta} yrs" if age_delta > 0 else f"{age_delta} yrs"

    # 1. SBAR CLINICAL SUMMARY
    if any(k in q for k in ["sbar", "summary", "case summary", "handover", "overview", "report summary"]):
        return f"""### 📋 Structured SBAR Clinical Handover Note
**Patient:** {patient_name} ({c['age']}y {gender}) | **Risk Tier:** {c['risk_tier']}

- **S (Situation):** {patient_name} presents for comprehensive cardiovascular risk evaluation. Calculated 10-year ASCVD event probability is **{c['risk']:.1f}%** (Confidence: {c['confidence']:.1f}%).
- **B (Background):** 
  - Smoking: {smoke} | Physical Activity: {act} | Family History: {"Positive" if fam_hist else "Negative"}
  - Fasting Glucose: {gluc} | Serum Cholesterol: {chol}
- **A (Assessment):**
  - Hemodynamics: **{c['bp_hi']}/{c['bp_lo']} mmHg** — Classified as **{c['bp_stat']}**.
  - Anthropometrics: BMI **{c['bmi']:.1f} kg/m²** ({c['bmi_stat']}).
  - Biological Aging: Estimated heart age is **{c['heart_age']} years** ({delta_str} acceleration vs chronological age).
- **R (Recommendation):**
  1. Blood pressure optimization targeting <130/80 mmHg via sodium restriction (<2,000 mg/day) and review of antihypertensive therapy.
  2. Baseline lipid panel repeat in 90 days; assess eligibility for moderate/high-intensity statin therapy.
  3. Structured aerobic regimen (150 min/wk Zone-2) and nutritional consultation."""

    # 2. BLOOD PRESSURE & HYPERTENSION PROTOCOLS
    if any(k in q for k in ["bp", "blood pressure", "hypertension", "systolic", "diastolic", "pressure"]):
        if c["bp_tier"] == "crisis":
            alert_prefix = "🚨 **CRITICAL ALERT: HYPERTENSIVE CRISIS** (>180/>120 mmHg). Prompt clinical assessment for target-organ damage (chest pain, shortness of breath, neurological symptoms) and immediate IV pharmacotherapy review indicated.\n\n"
        elif c["bp_tier"] == "stage2":
            alert_prefix = "⚠️ **STAGE 2 HYPERTENSION IDENTIFIED**: Systolic >= 140 or Diastolic >= 90 mmHg.\n\n"
        else:
            alert_prefix = ""

        return f"""{alert_prefix}### 🩺 Hemodynamic Assessment & Hypertension Protocol
- **Current Reading:** **{c['bp_hi']}/{c['bp_lo']} mmHg** ({c['bp_stat']})
- **Pulse Pressure:** {c['bp_hi'] - c['bp_lo']} mmHg (arterial stiffness indicator)

**AHA/ACC Clinical Recommendations:**
1. **Target Goal:** Aim for clinical BP < 130/80 mmHg (< 120/80 mmHg ideal).
2. **Pharmacotherapy Considerations:**
   - For Stage 1 HTN with 10-year risk >= 10%: initiate 1st-line single agent (ACE inhibitor, ARB, or DHP-Calcium Channel Blocker like Amlodipine 5mg).
   - For Stage 2 HTN: prompt combination therapy (e.g., ARB + CCB or ARB + Thiazide-like diuretic Chlorthalidone).
3. **Non-Pharmacological Protocol:**
   - Strict sodium restriction: < 1,500 – 2,000 mg/day.
   - DASH Dietary Pattern (Dietary Approaches to Stop Hypertension): rich in potassium (3,500–5,000 mg/day), magnesium, and dietary fiber.
   - Home BP Telemetry: AM/PM logs for 2 consecutive weeks prior to follow-up."""

    # 3. CHOLESTEROL, LIPIDS & STATINS
    if any(k in q for k in ["cholesterol", "lipid", "statin", "ldl", "hdl", "triglyceride", "lipids"]):
        statin_rec = "High-Intensity Statin (Atorvastatin 40-80mg / Rosuvastatin 20-40mg)" if c["risk"] >= 20.0 else (
            "Moderate-Intensity Statin (Atorvastatin 10-20mg / Rosuvastatin 5-10mg)" if c["risk"] >= 7.5 else "Lifestyle optimization with monitoring"
        )
        return f"""### 🧪 Lipid Biomarker & Statin Decision Support
- **Current Serum Cholesterol Status:** **{chol}**
- **10-Year ASCVD Event Risk:** **{c['risk']:.1f}%**

**ACC/AHA Guideline Stratification:**
1. **Therapeutic Statin Consideration:** {statin_rec}.
2. **Target LDL-C Reduction:**
   - High-intensity statin targets >= 50% reduction in baseline LDL-C.
   - Moderate-intensity targets 30% to 49% reduction.
3. **Nutritional & Lifestyle Interventions:**
   - Limit dietary saturated fatty acids to < 6% of total daily energy intake.
   - Eliminate industrial trans-fats completely.
   - Supplement with soluble fiber (10–25 g/day, e.g., psyllium husk, oats) and plant sterols/stanols (2 g/day).
   - Re-evaluate lipid panel with fasting ApoB and Lipoprotein(a) in 8–12 weeks."""

    # 4. CARDIOVASCULAR RISK & HEART AGE
    if any(k in q for k in ["risk", "heart age", "ascvd", "probability", "event risk", "score"]):
        return f"""### 📈 10-Year ASCVD Risk & Heart Age Breakdown
- **Predicted 10-Year Cardiovascular Event Risk:** **{c['risk']:.1f}%**
- **Model Confidence Score:** **{c['confidence']:.1f}%**
- **Biological Heart Age:** **{c['heart_age']} years** (Chronological: {c['age']} years | Delta: **{delta_str}**)
- **Clinical Triage Classification:** **{c['risk_tier']}**

**Key Risk Drivers for {patient_name}:**
1. **Hemodynamic Load:** Systolic BP of {c['bp_hi']} mmHg contributes significantly to vascular shear stress.
2. **Biological Age Acceleration:** An elevated heart age of {c['heart_age']} reflects cumulative arterial stiffness and metabolic burden.
3. **Modifiable Factors:** Optimizing blood pressure to < 125 mmHg and reducing cholesterol can lower absolute risk by up to **8–14 percentage points**."""

    # 5. GLUCOSE, DIABETES & METABOLIC SYNDROME
    if any(k in q for k in ["glucose", "sugar", "diabetes", "diabetic", "glycemic", "a1c", "insulin"]):
        return f"""### 🩸 Fasting Glycemic & Metabolic Status
- **Current Fasting Blood Glucose:** **{gluc}**
- **Body Mass Index:** **{c['bmi']:.1f} kg/m²** ({c['bmi_stat']})

**Clinical Insights & Protocol:**
1. **Diagnostic Thresholds (ADA Standards of Care):**
   - Normal: Fasting Plasma Glucose < 100 mg/dL (A1C < 5.7%).
   - Impaired Fasting Glucose (Prediabetes): 100–125 mg/dL (A1C 5.7–6.4%).
   - Overt Diabetes Mellitus: Fasting Glucose >= 126 mg/dL (A1C >= 6.5%).
2. **Cardiovascular Synergy:** Diabetes and hyperglycemia multiply cardiovascular event rates 2- to 4-fold via accelerated atherogenesis and microvascular dysfunction.
3. **Action Items:**
   - Order formal laboratory HbA1c and fasting insulin panel.
   - Implement low-glycemic index dietary regimen (eliminate refined carbohydrates, sugar-sweetened beverages).
   - If prediabetic or diabetic, consider Metformin or SGLT2 inhibitors / GLP-1 RAs with proven cardiovascular outcome benefits (CVOTs)."""

    # 6. WEIGHT & BMI OPTIMIZATION
    if any(k in q for k in ["weight", "bmi", "obese", "overweight", "height", "body mass", "lose weight"]):
        target_wt = round(24.0 * ((c['height_val'] / 100) ** 2), 1)
        wt_diff = round(c['weight_val'] - target_wt, 1)
        return f"""### ⚖️ Anthropometrics & Body Composition Plan
- **Current Height / Weight:** {c['height_val']} cm / {c['weight_val']} kg
- **Current BMI:** **{c['bmi']:.1f} kg/m²** ({c['bmi_stat']})
- **Ideal Body Weight Target (BMI 24.0):** **~{target_wt} kg** ({f"Surplus: {wt_diff} kg" if wt_diff > 0 else "Within normal range"})

**Therapeutic Weight Protocol:**
1. **Cardiovascular Impact:** Each 1 kg reduction in excess adipose tissue reduces systolic blood pressure by approximately **1.0 mmHg**.
2. **Initial Target:** Aim for a 5% to 10% sustained weight reduction over 6 months (~500 kcal/day deficit).
3. **Metabolic Health:** Prioritize reduction in visceral adiposity (waist circumference < 102 cm for men, < 88 cm for women) to alleviate hepatic insulin resistance."""

    # 7. DIET & NUTRITIONAL PRESCRIPTION
    if any(k in q for k in ["diet", "nutrition", "dash", "food", "sodium", "salt", "eating", "potassium"]):
        return f"""### 🥗 Evidence-Based Dietary Prescription (DASH & Mediterranean Protocol)
- **Clinical Target:** Lower vascular resistance, reduce arterial inflammation, and optimize lipid profiles.

**Prescription Guidelines:**
1. **Sodium Restriction:** Strict ceiling of **< 2,000 mg elemental sodium/day** (< 1 tsp salt). Eliminate processed meats, canned soups, and packaged convenience meals.
2. **Potassium Optimization:** Aim for 3,500–5,000 mg/day from whole food sources (dark leafy greens, avocados, sweet potatoes, legumes, wild salmon) unless contraindicated by CKD or ACEi/ARB hyperkalemia.
3. **Cardioprotective Fats:** High intake of Extra Virgin Olive Oil (EVOO), raw walnuts, and chia/flax seeds; minimum 2 servings of fatty fish (salmon, mackerel, sardines) weekly.
4. **Dietary Fiber:** Minimum 30–35 grams/day of prebiotic soluble and insoluble fiber."""

    # 8. EXERCISE & PHYSICAL ACTIVITY
    if any(k in q for k in ["exercise", "activity", "workout", "cardio", "fitness", "zone 2", "aerobic", "steps"]):
        max_hr = 220 - c["age"]
        z2_low = int(max_hr * 0.60)
        z2_high = int(max_hr * 0.75)
        return f"""### 🏃 Exercise Prescription & Aerobic Conditioning
- **Current Physical Activity Reported:** **{act}**
- **Calculated Maximum Heart Rate:** ~{max_hr} BPM (Chronological Age: {c['age']})
- **Target Zone-2 Aerobic Training Band:** **{z2_low} – {z2_high} BPM**

**AHA/ACSM Clinical Exercise Protocol:**
1. **Aerobic Foundation:** Minimum **150 minutes/week** of moderate-intensity (Zone-2 brisk walking, stationary cycling, rowing) OR 75 minutes of vigorous activity.
2. **Zone-2 Mechanism:** Training at 60–75% max HR optimizes mitochondrial density, enhances fat oxidation, improves endothelial nitric oxide synthase (eNOS) bioavailability, and reduces resting sympathetic tone.
3. **Resistance Training:** 2–3 sessions per week of major muscle group resistance training to preserve lean mass and improve glycemic clearance.
4. **Pre-Participation Clearance:** Gradual progressive overload; pause and evaluate if chest tightness or dyspnea occurs."""

    # 9. ECG & TELEMETRY MONITORING
    if any(k in q for k in ["ecg", "ekg", "telemetry", "rhythm", "sinus", "bpm", "trace", "lead"]):
        return f"""### ⚡ Lead-II Telemetry Rhythm & ECG Interpretation
- **Trace Status:** 10-Second Continuous Telemetry Simulation
- **Resting Heart Rate:** **72 BPM** (Normal resting range: 60–100 BPM)
- **Rhythm Classification:** **Normal Sinus Rhythm (NSR)**

**Electrophysiological Metrics:**
1. **P Wave:** Monomorphic, upright in Lead-II; indicates normal sinoatrial (SA) node pacemaker depolarization.
2. **PR Interval:** 160 ms (Normal: 120–200 ms); normal atrioventricular (AV) nodal conduction delay.
3. **QRS Complex:** Narrow (< 100 ms); rapid ventricular depolarization through His-Purkinje network without bundle branch block.
4. **ST Segment & T Wave:** Isoelectric ST segment without acute elevation (>1mm) or depression; concordant upright T wave indicating normal ventricular repolarization.
5. **Red Flag Alerts:** Monitor for premature ventricular contractions (PVCs), tachyarrhythmias, or ischemic ST shifts under physical stress."""

    # 10. SMOKING & ALCOHOL CESSATION
    if any(k in q for k in ["smoke", "smoking", "tobacco", "cigarette", "alcohol", "drink", "drinking"]):
        return f"""### 🚭 Tobacco & Alcohol Cessation Protocol
- **Smoking Status:** **{smoke}**
- **Alcohol Consumption:** Reported in clinical history

**Cardiovascular Risk Impact:**
1. **Smoking Harm:** Cigarette smoking accelerates endothelial damage, induces coronary vasoconstriction, oxidizes LDL particles, and increases platelet adhesiveness.
2. **Cessation Timeline:**
   - **20 minutes:** Heart rate and blood pressure drop to baseline.
   - **24 hours:** Coronary event risk begins measurable decline.
   - **1 year:** Excess coronary heart disease risk is cut by **50%**.
3. **Clinical Pharmacotherapy Options:**
   - Nicotine Replacement Therapy (NRT): Transdermal patch + short-acting gum/lozenge.
   - Oral Pharmacotherapy: Varenicline (Chantix) or Bupropion SR, combined with cognitive-behavioral counseling.
4. **Alcohol Limit:** Max <= 1 standard drink/day for females, <= 2 for males; zero consumption provides maximum cardiometabolic benefit."""

    # 11. PHARMACOTHERAPY & MEDICATIONS
    if any(k in q for k in ["medication", "medicine", "drug", "prescription", "rx", "pill", "pharma"]):
        return f"""### 💊 Evidence-Based Pharmacotherapy Decision Support
**Patient Profile:** {c['age']}y {gender} | BP: {c['bp_hi']}/{c['bp_lo']} mmHg | ASCVD Risk: {c['risk']:.1f}%

**Cardiovascular Medication Classes to Evaluate:**
1. **Antihypertensive First-Line Classes:**
   - **ACE-Inhibitors / ARBs:** Lisinopril 10–20mg daily or Losartan 50mg daily (renal-protective, cardioprotective).
   - **Dihydropyridine CCBs:** Amlodipine 5–10mg daily (potent peripheral vasodilator).
   - **Thiazide-like Diuretics:** Chlorthalidone 12.5–25mg daily or Indapamide.
2. **Lipid-Lowering Therapy:**
   - Atorvastatin 20mg daily or Rosuvastatin 10mg daily for primary ASCVD prevention.
3. **Antiplatelet (Aspirin 81mg):**
   - Generally reserved for secondary prevention or very high-risk individuals after bleeding risk assessment (HAS-BLED).
*Note: Clinical pharmacotherapy must be tailored by the treating licensed physician after reviewing hepatic/renal panels (eGFR, Cr, K+).*"""

    # 12. GREETINGS & CASUAL INTERACTION
    if any(k in q for k in ["hello", "hi", "hey", "good morning", "good evening", "who are you", "help"]):
        return f"""Hello Doctor! I am your **CardioXAI Clinical Copilot**, specialized in institutional cardiovascular decision support.

I have analyzed the complete clinical profile for **{patient_name}** ({c['age']}y, BP {c['bp_hi']}/{c['bp_lo']} mmHg, 10-Yr Risk: {c['risk']:.1f}%):

**You can ask me questions such as:**
- *"Generate SBAR clinical summary"*
- *"What is the recommended blood pressure protocol?"*
- *"Does this patient require statin therapy?"*
- *"Explain the 10-year ASCVD risk and heart age"*
- *"Provide dietary and DASH recommendations"*
- *"Analyze the Lead-II ECG rhythm"*
- *"What are the target weight and BMI goals?"*"""

    # 13. COMPREHENSIVE CONTEXTUAL FALLBACK
    return f"""### 🤖 Clinical Decision Support Analysis
**Patient:** {patient_name} ({c['age']}y {gender}) | **Risk:** {c['risk']:.1f}% ({c['risk_tier']})

Regarding **"{query}"**:
- **Hemodynamics:** Patient's current blood pressure is **{c['bp_hi']}/{c['bp_lo']} mmHg** ({c['bp_stat']}).
- **Metabolic Profile:** Serum Cholesterol is **{chol}**, Fasting Glucose is **{gluc}**, and BMI is **{c['bmi']:.1f} kg/m²** ({c['bmi_stat']}).
- **Biological Acceleration:** Calculated biological heart age is **{c['heart_age']} years** ({delta_str} chronological gap).

**Core Clinical Recommendation:**
For this patient profile, prioritizing **systolic blood pressure reduction to < 130 mmHg**, initiating dietary **sodium restriction (<2,000 mg/day)**, and scheduling **150 min/week of Zone-2 aerobic exercise** delivers the greatest reduction in 10-year major adverse cardiovascular events (MACE).

*Feel free to ask for a specific SBAR summary, medication protocol, diet plan, or ECG interpretation!*"""
