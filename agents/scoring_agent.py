from models.schemas import RiskFinding


class ScoringAgent:
    def calculate_score(self, findings: list[RiskFinding]) -> tuple[int, str]:
        score = 100

        for finding in findings:
            if finding.severity == "high":
                score -= 35
            elif finding.severity == "medium":
                score -= 20
            elif finding.severity == "low":
                score -= 10

        score = max(score, 0)

        if score >= 80:
            risk_level = "Düşük Risk"
        elif score >= 50:
            risk_level = "Orta Risk"
        else:
            risk_level = "Yüksek Risk"

        return score, risk_level