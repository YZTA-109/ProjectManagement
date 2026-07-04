from models.schemas import AnalysisResult, PrescriptionRequest, RiskFinding

from agents.interaction_agent import InteractionAgent
from agents.lab_risk_agent import LabRiskAgent
from agents.report_agent import ReportAgent
from agents.scoring_agent import ScoringAgent


SEVERITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


class Orchestrator:
    """Coordinates all Sprint 1 analysis agents."""

    def __init__(self):
        self.lab_risk_agent = LabRiskAgent()
        self.interaction_agent = InteractionAgent()
        self.scoring_agent = ScoringAgent()
        self.report_agent = ReportAgent()

    def analyze(self, request: PrescriptionRequest) -> AnalysisResult:
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

        findings = sorted(
            findings,
            key=lambda finding: SEVERITY_ORDER.get(finding.severity, 99),
        )

        safety_score, risk_level = self.scoring_agent.calculate_score(findings)

        recommendation_summary = self.report_agent.generate_summary(
            findings=findings,
            risk_level=risk_level,
        )

        markdown_report = self.report_agent.generate_markdown_report(
            patient=request.patient,
            new_medication=request.new_medication,
            safety_score=safety_score,
            risk_level=risk_level,
            findings=findings,
            summary=recommendation_summary,
        )

        return AnalysisResult(
            safety_score=safety_score,
            risk_level=risk_level,
            findings=findings,
            recommendation_summary=recommendation_summary,
            markdown_report=markdown_report,
        )
