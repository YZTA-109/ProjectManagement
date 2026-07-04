from models.schemas import RiskFinding


SEVERITY_PENALTY = {
    "critical": 50,
    "high": 35,
    "medium": 20,
    "low": 10,
}


class ScoringAgent:
    """Converts findings into a simple 0-100 prescription safety score."""

    def calculate_score(self, findings: list[RiskFinding]) -> tuple[int, str]:
        score = 100

        for finding in findings:
            score -= SEVERITY_PENALTY.get(finding.severity, 0)

        score = max(score, 0)
        risk_level = self._risk_level_from_score(score=score, findings=findings)

        return score, risk_level

    def _risk_level_from_score(self, score: int, findings: list[RiskFinding]) -> str:
        if any(finding.severity == "critical" for finding in findings):
            return "Kritik Risk"

        if score >= 85:
            return "Düşük Risk"
        if score >= 60:
            return "Orta Risk"
        if score >= 30:
            return "Yüksek Risk"
        return "Kritik Risk"
