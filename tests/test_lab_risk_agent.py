from agents.lab_risk_agent import LabRiskAgent
from models.schemas import LabValues, Patient


def make_patient(**overrides) -> Patient:
    defaults = {
        "age": 40,
        "gender": "Erkek",
        "current_medications": ["metformin"],
        "lab_values": LabValues(egfr=95, creatinine=0.9, ast=25, alt=22),
    }
    defaults.update(overrides)
    return Patient(**defaults)


def test_healthy_patient_has_no_findings():
    agent = LabRiskAgent()
    findings = agent.analyze(make_patient(), new_medication="aspirin")
    assert findings == []


def test_severe_renal_risk_is_high_for_renal_sensitive_drug():
    agent = LabRiskAgent()
    patient = make_patient(
        lab_values=LabValues(egfr=20, creatinine=2.5, ast=25, alt=22)
    )

    findings = agent.analyze(patient, new_medication="metformin")
    renal = [f for f in findings if "böbrek" in f.title.lower()]
    assert renal and renal[0].severity == "high"


def test_moderate_renal_risk_is_low_for_non_renal_drug():
    agent = LabRiskAgent()
    patient = make_patient(
        lab_values=LabValues(egfr=45, creatinine=1.5, ast=25, alt=22)
    )

    findings = agent.analyze(patient, new_medication="loratadine")
    renal = [f for f in findings if "böbrek" in f.title.lower()]
    assert renal and renal[0].severity == "low"


def test_marked_hepatic_risk_for_hepatotoxic_drug():
    agent = LabRiskAgent()
    patient = make_patient(
        lab_values=LabValues(egfr=95, creatinine=0.9, ast=150, alt=160)
    )

    findings = agent.analyze(patient, new_medication="atorvastatin")
    hepatic = [f for f in findings if "karaciğer" in f.title.lower()]
    assert hepatic and hepatic[0].severity == "high"


def test_elderly_polypharmacy_finding():
    agent = LabRiskAgent()
    patient = make_patient(
        age=70,
        current_medications=["a", "b", "c", "d", "e"],
    )

    findings = agent.analyze(patient, new_medication="aspirin")
    poly = [f for f in findings if "polifarmasi" in f.title.lower()]
    assert len(poly) == 1
