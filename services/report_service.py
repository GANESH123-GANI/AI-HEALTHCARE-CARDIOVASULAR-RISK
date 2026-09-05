import datetime

try:
    from fpdf import FPDF
    FPDF_LOADED = True
except ImportError:
    FPDF_LOADED = False


def create_pdf_report(
    name: str,
    age: int,
    gender: str,
    height: float,
    weight: float,
    bmi: float,
    bp_hi: int,
    bp_lo: int,
    chol: str,
    gluc: str,
    smoke: str,
    act: str,
    risk: float,
    confidence: float,
    alco: str = "No",
    fam_hist: bool = False
) -> bytes:
    """
    Generates a formal Clinical Intelligence PDF Report using FPDF.
    Returns bytes suitable for Streamlit download button.
    """
    if not FPDF_LOADED:
        return b""

    pdf = FPDF()
    pdf.add_page()

    # Title
    try:
        pdf.set_font("helvetica", 'B', 18)
    except Exception:
        pdf.set_font("Arial", 'B', 18)

    pdf.cell(200, 10, text="CardioXAI Clinical Intelligence Report", align='C')
    pdf.ln(10)

    try:
        pdf.set_font("helvetica", size=10)
    except Exception:
        pdf.set_font("Arial", size=10)

    pdf.cell(200, 8, text=f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y - %H:%M')}", align='C')
    pdf.ln(12)

    # Section 1: Demographics
    try:
        pdf.set_font("helvetica", 'B', 13)
    except Exception:
        pdf.set_font("Arial", 'B', 13)
    pdf.cell(200, 9, text="1. Patient Demographics & Baseline Vitals")
    pdf.ln(9)

    try:
        pdf.set_font("helvetica", size=11)
    except Exception:
        pdf.set_font("Arial", size=11)
    pdf.cell(200, 7, text=f"Patient Name: {name}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Age: {age} yrs | Gender: {gender}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Height: {height} cm | Weight: {weight} kg | BMI: {bmi:.1f} kg/m2")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Blood Pressure: {bp_hi} / {bp_lo} mmHg")
    pdf.ln(11)

    # Section 2: Biomarkers & Lifestyle
    try:
        pdf.set_font("helvetica", 'B', 13)
    except Exception:
        pdf.set_font("Arial", 'B', 13)
    pdf.cell(200, 9, text="2. Biochemical & Lifestyle Factors")
    pdf.ln(9)

    try:
        pdf.set_font("helvetica", size=11)
    except Exception:
        pdf.set_font("Arial", size=11)
    pdf.cell(200, 7, text=f"Serum Cholesterol: {chol}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Fasting Glucose: {gluc}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Active Tobacco Smoking: {smoke}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Alcohol Consumption: {alco}")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Regular Physical Activity: {act}")
    pdf.ln(7)
    fam_hist_str = "Positive (Elevated Familial CVD Risk)" if fam_hist else "Negative / None Reported"
    pdf.cell(200, 7, text=f"Family History of Premature CVD: {fam_hist_str}")
    pdf.ln(11)

    # Section 3: Diagnostic Assessment
    try:
        pdf.set_font("helvetica", 'B', 13)
    except Exception:
        pdf.set_font("Arial", 'B', 13)
    pdf.cell(200, 9, text="3. Explainable AI Diagnostic Assessment")
    pdf.ln(9)

    try:
        pdf.set_font("helvetica", size=11)
    except Exception:
        pdf.set_font("Arial", size=11)
    pdf.cell(200, 7, text=f"Predicted 10-Year Cardiovascular Event Risk: {risk:.1f}%")
    pdf.ln(7)
    pdf.cell(200, 7, text=f"Machine Learning Ensemble Confidence: {confidence:.1f}%")
    pdf.ln(7)
    triage_cat = (
        "High Risk (Immediate Intervention Required)" if risk >= 60 
        else ("Moderate Risk (Lifestyle & Medical Review)" if risk >= 30 
              else "Low Risk (Routine Annual Prevention)")
    )
    pdf.cell(200, 7, text=f"Clinical Triage Tier: {triage_cat}")
    pdf.ln(10)

    out = pdf.output()
    return bytes(out) if isinstance(out, (bytearray, bytes)) else str(out).encode('latin1')
