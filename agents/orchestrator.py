from models.schemas import PrescriptionRequest, AnalysisResult

from agents.lab_risk_agent import LabRiskAgent
from agents.interaction_agent import InteractionAgent
from agents.scoring_agent import ScoringAgent
from agents.report_agent import ReportAgent


class Orchestrator:
    def __init__(self):
        self.lab_risk_agent = LabRiskAgent()
        self.interaction_agent = InteractionAgent()
        self.scoring_agent = ScoringAgent()
        self.report_agent = ReportAgent()

    def analyze(self, request: PrescriptionRequest) -> AnalysisResult:
        findings = []

        lab_findings = self.lab_risk_agent.analyze(
            patient=request.patient,
            new_medication=request.new_medication
        )

        interaction_findings = self.interaction_agent.analyze(
            patient=request.patient,
            new_medication=request.new_medication
        )

        findings.extend(lab_findings)
        findings.extend(interaction_findings)

        safety_score, risk_level = self.scoring_agent.calculate_score(findings)

        recommendation_summary = self.report_agent.generate_summary(
            findings=findings,
            risk_level=risk_level
        )

        return AnalysisResult(
            safety_score=safety_score,
            risk_level=risk_level,
            findings=findings,
            recommendation_summary=recommendation_summary
        )