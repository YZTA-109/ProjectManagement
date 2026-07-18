import pytest

from agents.gemini_explainer import GeminiExplainer
from agents.orchestrator import Orchestrator
from models.schemas import DrugInfo, PrescriptionRequest
from providers.rxnorm_provider import DEFAULT_DB_PATH


def make_orchestrator(**kwargs) -> Orchestrator:
    kwargs.setdefault("use_openfda", False)
    kwargs.setdefault("use_ai_summary", False)
    return Orchestrator(**kwargs)


def test_low_risk_patient_scores_high(healthy_patient):
    request = PrescriptionRequest(patient=healthy_patient, new_medication="loratadine")
    result = make_orchestrator().analyze(request)

    assert result.safety_score >= 85
    assert result.risk_level == "Düşük Risk"
    assert result.ai_summary is None


def test_high_risk_patient_aggregates_findings(high_risk_patient):
    request = PrescriptionRequest(patient=high_risk_patient, new_medication="aspirin")
    result = make_orchestrator().analyze(request)

    agents = {finding.agent for finding in result.findings}
    assert "InteractionAgent" in agents
    assert "LabRiskAgent" in agents
    assert result.safety_score < 60


def test_findings_sorted_by_severity(high_risk_patient):
    request = PrescriptionRequest(patient=high_risk_patient, new_medication="aspirin")
    result = make_orchestrator().analyze(request)

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    severities = [order[f.severity] for f in result.findings]
    assert severities == sorted(severities)


def test_report_included_in_result(high_risk_patient):
    request = PrescriptionRequest(patient=high_risk_patient, new_medication="aspirin")
    result = make_orchestrator().analyze(request)

    assert "PolyPharm AI" in result.markdown_report
    assert result.recommendation_summary


@pytest.mark.skipif(not DEFAULT_DB_PATH.exists(), reason="rxnorm.db not built")
def test_drug_info_populated_from_rxnorm(healthy_patient):
    request = PrescriptionRequest(patient=healthy_patient, new_medication="Coumadin")
    result = make_orchestrator().analyze(request)

    assert result.new_drug_info is not None
    assert result.new_drug_info.ingredients == ["warfarin"]


def test_boxed_warning_becomes_high_finding(healthy_patient):
    orchestrator = make_orchestrator()
    drug_info = DrugInfo(
        query_name="warfarin",
        openfda_found=True,
        boxed_warning="WARNING: bleeding risk",
    )

    findings = orchestrator._openfda_findings(drug_info)
    assert len(findings) == 1
    assert findings[0].severity == "high"
    assert findings[0].agent == "DrugDataService"


def test_ai_summary_attached_when_explainer_succeeds(healthy_patient):
    class FakeExplainer(GeminiExplainer):
        def __init__(self):
            super().__init__(api_key="fake")
            self.model = "fake-model"

        def generate_summary(self, **kwargs):
            return "AI özeti"

    orchestrator = Orchestrator(
        use_openfda=False,
        use_ai_summary=True,
        gemini_explainer=FakeExplainer(),
    )
    request = PrescriptionRequest(patient=healthy_patient, new_medication="aspirin")
    result = orchestrator.analyze(request)

    assert result.ai_summary == "AI özeti"
    assert result.ai_model == "fake-model"
    assert "Yapay Zeka Değerlendirmesi" in result.markdown_report
