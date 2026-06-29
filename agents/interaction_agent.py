import json
from pathlib import Path

from models.schemas import Patient, RiskFinding


class InteractionAgent:
    def __init__(self):
        data_path = Path("data/demo_interactions.json")

        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as file:
                self.interactions = json.load(file)
        else:
            self.interactions = []

    def analyze(self, patient: Patient, new_medication: str) -> list[RiskFinding]:
        findings = []

        current_meds = [med.lower().strip() for med in patient.current_medications]
        new_med = new_medication.lower().strip()

        for item in self.interactions:
            drug_a = item["drug_a"].lower()
            drug_b = item["drug_b"].lower()

            interaction_exists = (
                new_med == drug_a and drug_b in current_meds
            ) or (
                new_med == drug_b and drug_a in current_meds
            )

            if interaction_exists:
                findings.append(
                    RiskFinding(
                        title=f"{item['drug_a']} - {item['drug_b']} etkileşimi",
                        severity=item["severity"],
                        description=item["description"],
                        source=item.get("source", "Demo interaction database")
                    )
                )

        return findings