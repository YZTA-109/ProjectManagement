import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from agents.orchestrator import Orchestrator
from models.schemas import LabValues, Patient, PrescriptionRequest


st.set_page_config(
    page_title="PolyPharm AI",
    page_icon="💊",
    layout="wide"
)

st.title("💊 PolyPharm AI")
st.subheader("Akıllı İlaç Etkileşim ve Toksisite Simülatörü")

st.warning(
    "Bu uygulama eğitim amaçlı bir karar destek demosudur. Klinik teşhis, "
    "reçeteleme veya tedavi kararı için kullanılamaz."
)


def load_sample_patients():
    path = Path("data/sample_patients.json")

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


sample_patients = load_sample_patients()

st.sidebar.header("Hasta Seçimi")

patient_mode = st.sidebar.radio(
    "Hasta girişi",
    ["Demo hasta seç", "Manuel hasta gir"]
)

if patient_mode == "Demo hasta seç" and sample_patients:
    patient_names = [patient["name"] for patient in sample_patients]
    selected_name = st.sidebar.selectbox("Demo hasta", patient_names)

    selected_patient = next(
        patient for patient in sample_patients if patient["name"] == selected_name
    )

    age = selected_patient["age"]
    gender = selected_patient["gender"]
    current_medications = selected_patient["current_medications"]
    egfr = selected_patient["lab_values"]["egfr"]
    creatinine = selected_patient["lab_values"]["creatinine"]
    ast = selected_patient["lab_values"]["ast"]
    alt = selected_patient["lab_values"]["alt"]

else:
    age = st.sidebar.number_input("Yaş", min_value=0, max_value=120, value=65)
    gender = st.sidebar.selectbox("Cinsiyet", ["Kadın", "Erkek", "Diğer"])

    meds_text = st.sidebar.text_area(
        "Mevcut ilaçlar",
        value="warfarin, metformin",
        help="İlaçları virgülle ayırarak yazın."
    )

    current_medications = [
        med.strip() for med in meds_text.split(",") if med.strip()
    ]

    egfr = st.sidebar.number_input("eGFR", min_value=0.0, max_value=150.0, value=75.0)
    creatinine = st.sidebar.number_input("Kreatinin", min_value=0.0, max_value=20.0, value=1.0)
    ast = st.sidebar.number_input("AST", min_value=0.0, max_value=1000.0, value=30.0)
    alt = st.sidebar.number_input("ALT", min_value=0.0, max_value=1000.0, value=30.0)


st.header("Reçete Güvenlik Analizi")

new_medication = st.text_input(
    "Yeni yazılmak istenen ilaç",
    value="aspirin"
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Hasta Bilgileri")
    st.write(f"**Yaş:** {age}")
    st.write(f"**Cinsiyet:** {gender}")
    st.write(f"**Mevcut ilaçlar:** {', '.join(current_medications)}")

with col2:
    st.markdown("### Laboratuvar Değerleri")
    st.write(f"**eGFR:** {egfr}")
    st.write(f"**Kreatinin:** {creatinine}")
    st.write(f"**AST:** {ast}")
    st.write(f"**ALT:** {alt}")


if st.button("Analiz Et"):
    patient = Patient(
        age=age,
        gender=gender,
        current_medications=current_medications,
        lab_values=LabValues(
            egfr=egfr,
            creatinine=creatinine,
            ast=ast,
            alt=alt
        )
    )

    request = PrescriptionRequest(
        patient=patient,
        new_medication=new_medication
    )

    orchestrator = Orchestrator()
    result = orchestrator.analyze(request)

    st.divider()

    st.header("Analiz Sonucu")

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric("Güvenlik Skoru", f"{result.safety_score}/100")

    with metric_col2:
        st.metric("Risk Seviyesi", result.risk_level)

    st.markdown("### Özet")
    st.info(result.recommendation_summary)

    st.markdown("### Risk Bulguları")

    if result.findings:
        for finding in result.findings:
            if finding.severity == "high":
                st.error(f"**{finding.title}**\n\n{finding.description}")
            elif finding.severity == "medium":
                st.warning(f"**{finding.title}**\n\n{finding.description}")
            else:
                st.info(f"**{finding.title}**\n\n{finding.description}")

            st.caption(f"Kaynak: {finding.source}")
    else:
        st.success("Belirgin bir risk bulgusu tespit edilmedi.")

    with st.expander("Ham analiz çıktısı"):
        st.json(result.model_dump())