from models.schemas import (
    AnalysisResult,
    DrugInfo,
    PrescriptionRequest,
    RiskFinding,
)

from agents.fda_interaction_agent import FdaLabelInteractionAgent
from agents.gemini_explainer import GeminiExplainer
from agents.interaction_agent import InteractionAgent
from agents.lab_risk_agent import LabRiskAgent
from agents.report_agent import ReportAgent
from agents.scoring_agent import ScoringAgent
from providers.drug_data_service import DrugDataService


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


class Orchestrator:
    """Coordinates the analysis agents and the Sprint 2 data providers."""

    def __init__(
        self,
        drug_data_service: DrugDataService | None = None,
        gemini_explainer: GeminiExplainer | None = None,
        use_openfda: bool = True,
        use_ai_summary: bool = True,
    ):
        self.drug_data_service = drug_data_service or DrugDataService(
            use_openfda=use_openfda
        )
        self.lab_risk_agent = LabRiskAgent()
        self.interaction_agent = InteractionAgent(
            drug_service=self.drug_data_service
        )
        self.fda_interaction_agent = FdaLabelInteractionAgent(
            openfda_client=self.drug_data_service.openfda,
            drug_service=self.drug_data_service,
            rules_provider=self.interaction_agent.rules_provider,
        )
        self.scoring_agent = ScoringAgent()
        self.report_agent = ReportAgent()
        self.gemini_explainer = gemini_explainer or GeminiExplainer()
        self.use_ai_summary = use_ai_summary

    def analyze(self, request: PrescriptionRequest) -> AnalysisResult:
        drug_info = self.drug_data_service.get_drug_info(request.new_medication)

        findings: list[RiskFinding] = []

        findings.extend(
            self.lab_risk_agent.analyze(
                patient=request.patient,
                new_medication=request.new_medication,
            )
        )
        findings.extend(
            self.interaction_agent.analyze(
                patient=request.patient,
                new_medication=request.new_medication,
            )
        )
        if self.drug_data_service.use_openfda:
            findings.extend(
                self.fda_interaction_agent.analyze(
                    patient=request.patient,
                    new_medication=request.new_medication,
                )
            )
        findings.extend(self._openfda_findings(drug_info))

        findings = sorted(
            findings,
            key=lambda finding: SEVERITY_ORDER.get(finding.severity, 99),
        )

        safety_score, risk_level = self.scoring_agent.calculate_score(findings)

        recommendation_summary = self.report_agent.generate_summary(
            findings=findings,
            risk_level=risk_level,
        )

        ai_summary = None
        ai_model = None
        if self.use_ai_summary and self.gemini_explainer.available:
            ai_summary = self.gemini_explainer.generate_summary(
                patient=request.patient,
                new_medication=request.new_medication,
                findings=findings,
                safety_score=safety_score,
                risk_level=risk_level,
                drug_info=drug_info,
            )
            if ai_summary is not None:
                ai_model = self.gemini_explainer.model

        markdown_report = self.report_agent.generate_markdown_report(
            patient=request.patient,
            new_medication=request.new_medication,
            safety_score=safety_score,
            risk_level=risk_level,
            findings=findings,
            summary=recommendation_summary,
            drug_info=drug_info,
            ai_summary=ai_summary,
        )

        return AnalysisResult(
            safety_score=safety_score,
            risk_level=risk_level,
            findings=findings,
            recommendation_summary=recommendation_summary,
            markdown_report=markdown_report,
            new_drug_info=drug_info,
            ai_summary=ai_summary,
            ai_model=ai_model,
        )

    def _openfda_findings(self, drug_info: DrugInfo) -> list[RiskFinding]:
        """Surface the openFDA boxed warning as a high-severity finding."""
        if not drug_info.openfda_found or not drug_info.boxed_warning:
            return []

        drug_label = drug_info.normalized_name or drug_info.query_name
        return [
            RiskFinding(
                title=f"{drug_label} için FDA kutulu uyarı",
                severity="high",
                description=(
                    "FDA prospektüsünde kutulu (boxed) uyarı bulunuyor: "
                    f"{drug_info.boxed_warning}"
                ),
                recommendation=(
                    "Kutulu uyarı kapsamındaki riskler hasta özelinde değerlendirilmeli "
                    "ve resmi prospektüs incelenmelidir."
                ),
                source="openFDA drug label",
                agent="DrugDataService",
            )
        ]
