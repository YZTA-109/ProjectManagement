import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from agents.orchestrator import Orchestrator
from models.schemas import LabValues, Patient, PrescriptionRequest

DATA_DIR = PROJECT_ROOT / "data"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="PolyPharm AI",
    page_icon="💊",
    layout="wide",
)

st.title("💊 PolyPharm AI")
st.subheader("Akıllı İlaç Etkileşim ve Toksisite Simülatörü")

st.warning(
    "Bu uygulama eğitim amaçlı bir karar destek demosudur. Klinik teşhis, "
    "reçeteleme veya tedavi kararı için kullanılamaz."
)


@st.cache_data
def load_json_file(path: Path) -> list[dict]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, list):
        return []

    return payload


def build_patient_from_inputs(
    age: int,
    gender: str,
    current_medications: list[str],
    egfr: float,
    creatinine: float,
    ast: float,
    alt: float,
) -> Patient:
    return Patient(
        age=age,
        gender=gender,
        current_medications=current_medications,
        lab_values=LabValues(
            egfr=egfr,
            creatinine=creatinine,
            ast=ast,
            alt=alt,
        ),
    )


def severity_badge(severity: str) -> str:
    mapping = {
        "critical": "🔴 Kritik",
        "high": "🟠 Yüksek",
        "medium": "🟡 Orta",
        "low": "🔵 Düşük",
    }
    return mapping.get(severity, severity)


sample_patients = load_json_file(DATA_DIR / "sample_patients.json")
interaction_rules = load_json_file(DATA_DIR / "demo_interactions.json")

st.sidebar.header("Hasta Seçimi")

patient_mode = st.sidebar.radio(
    "Hasta girişi",
    ["Demo hasta seç", "Manuel hasta gir"],
)

if patient_mode == "Demo hasta seç" and sample_patients:
    patient_names = [patient["name"] for patient in sample_patients]
    selected_name = st.sidebar.selectbox("Demo hasta", patient_names)

    selected_patient = next(
        patient for patient in sample_patients if patient["name"] == selected_name
    )

    age = int(selected_patient["age"])
    gender = selected_patient["gender"]
    current_medications = selected_patient["current_medications"]
    egfr = float(selected_patient["lab_values"]["egfr"])
    creatinine = float(selected_patient["lab_values"]["creatinine"])
    ast = float(selected_patient["lab_values"]["ast"])
    alt = float(selected_patient["lab_values"]["alt"])
else:
    age = st.sidebar.number_input("Yaş", min_value=0, max_value=120, value=65)
    gender = st.sidebar.selectbox("Cinsiyet", ["Kadın", "Erkek", "Diğer"])

    meds_text = st.sidebar.text_area(
        "Mevcut ilaçlar",
        value="warfarin, metformin",
        help="İlaçları virgülle ayırarak yazın.",
    )

    current_medications = [
        medication.strip()
        for medication in meds_text.split(",")
        if medication.strip()
    ]

    egfr = st.sidebar.number_input("eGFR", min_value=0.0, max_value=150.0, value=75.0)
    creatinine = st.sidebar.number_input("Kreatinin", min_value=0.0, max_value=20.0, value=1.0)
    ast = st.sidebar.number_input("AST", min_value=0.0, max_value=1000.0, value=30.0)
    alt = st.sidebar.number_input("ALT", min_value=0.0, max_value=1000.0, value=30.0)

available_drugs = sorted(
    {
        item["drug_a"]
        for item in interaction_rules
        if "drug_a" in item
    }
    | {
        item["drug_b"]
        for item in interaction_rules
        if "drug_b" in item
    }
    | {"metformin", "atorvastatin", "ibuprofen", "furosemide", "lisinopril"}
)

st.header("Reçete Güvenlik Analizi")

input_mode = st.radio(
    "Yeni ilaç giriş yöntemi",
    ["Listeden seç", "Manuel yaz"],
    horizontal=True,
)

if input_mode == "Listeden seç":
    new_medication = st.selectbox("Yeni yazılmak istenen ilaç", available_drugs, index=available_drugs.index("aspirin") if "aspirin" in available_drugs else 0)
else:
    new_medication = st.text_input("Yeni yazılmak istenen ilaç", value="aspirin")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Hasta Bilgileri")
    st.write(f"**Yaş:** {age}")
    st.write(f"**Cinsiyet:** {gender}")
    st.write(f"**Mevcut ilaç sayısı:** {len(current_medications)}")

with col2:
    st.markdown("### Mevcut İlaçlar")
    if current_medications:
        for medication in current_medications:
            st.write(f"- {medication}")
    else:
        st.write("Mevcut ilaç girilmedi.")

with col3:
    st.markdown("### Laboratuvar Değerleri")
    st.write(f"**eGFR:** {egfr}")
    st.write(f"**Kreatinin:** {creatinine}")
    st.write(f"**AST:** {ast}")
    st.write(f"**ALT:** {alt}")

st.divider()

if st.button("Analiz Et", type="primary"):
    patient = build_patient_from_inputs(
        age=age,
        gender=gender,
        current_medications=current_medications,
        egfr=egfr,
        creatinine=creatinine,
        ast=ast,
        alt=alt,
    )

    request = PrescriptionRequest(
        patient=patient,
        new_medication=new_medication,
    )

    orchestrator = Orchestrator()
    result = orchestrator.analyze(request)

    st.header("Analiz Sonucu")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:
        st.metric("Güvenlik Skoru", f"{result.safety_score}/100")

    with metric_col2:
        st.metric("Risk Seviyesi", result.risk_level)

    with metric_col3:
        st.metric("Bulgu Sayısı", len(result.findings))

    st.progress(result.safety_score / 100)

    st.markdown("### Özet")
    st.info(result.recommendation_summary)

    st.markdown("### Risk Bulguları")

    if result.findings:
        findings_df = pd.DataFrame(
            [
                {
                    "Şiddet": severity_badge(finding.severity),
                    "Başlık": finding.title,
                    "Açıklama": finding.description,
                    "Öneri": finding.recommendation,
                    "Ajan": finding.agent,
                    "Kaynak": finding.source,
                }
                for finding in result.findings
            ]
        )
        st.dataframe(findings_df, use_container_width=True, hide_index=True)

        for finding in result.findings:
            message = f"**{finding.title}**\n\n{finding.description}\n\n**Öneri:** {finding.recommendation}"

            if finding.severity in {"critical", "high"}:
                st.error(message)
            elif finding.severity == "medium":
                st.warning(message)
            else:
                st.info(message)

            st.caption(f"Kaynak: {finding.source} | Ajan: {finding.agent}")
    else:
        st.success("Belirgin bir risk bulgusu tespit edilmedi.")

    st.download_button(
        label="Markdown raporu indir",
        data=result.markdown_report,
        file_name="polypharm_ai_rapor.md",
        mime="text/markdown",
    )

    with st.expander("Ham analiz çıktısı"):
        st.json(result.model_dump())
else:
    st.info("Analizi başlatmak için hasta bilgilerini kontrol edip **Analiz Et** butonuna basın.")
