import json
from pathlib import Path
from typing import Any

from models.schemas import Patient, RiskFinding


def _normalize_drug_name(value: str) -> str:
    return value.lower().strip()


class InteractionAgent:
    """Checks demo drug-drug interaction rules.

    Sprint 1 scope:
    - Rule-based and deterministic.
    - Uses local demo JSON data.
    - Does not claim clinical completeness.
    """

    def __init__(self, data_path: Path | None = None):
        project_root = Path(__file__).resolve().parents[1]
        self.data_path = data_path or project_root / "data" / "demo_interactions.json"
        self.interactions = self._load_interactions()

    def _load_interactions(self) -> list[dict[str, Any]]:
        if not self.data_path.exists():
            return []

        with self.data_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError("demo_interactions.json must contain a list of interaction rules.")

        return payload

    def analyze(self, patient: Patient, new_medication: str) -> list[RiskFinding]:
        findings: list[RiskFinding] = []

        current_meds = {
            _normalize_drug_name(medication)
            for medication in patient.current_medications
            if medication.strip()
        }
        new_med = _normalize_drug_name(new_medication)

        for item in self.interactions:
            drug_a = _normalize_drug_name(item.get("drug_a", ""))
            drug_b = _normalize_drug_name(item.get("drug_b", ""))

            if not drug_a or not drug_b:
                continue

            interaction_exists = (
                new_med == drug_a and drug_b in current_meds
            ) or (
                new_med == drug_b and drug_a in current_meds
            )

            if interaction_exists:
                findings.append(
                    RiskFinding(
                        title=f"{item['drug_a']} - {item['drug_b']} etkileşimi",
                        severity=item.get("severity", "medium"),
                        description=item.get(
                            "description",
                            "Bu ilaç kombinasyonu için demo etkileşim kuralı bulundu.",
                        ),
                        recommendation=item.get(
                            "recommendation",
                            "Kombinasyonu klinik bağlamda yeniden değerlendirin.",
                        ),
                        source=item.get("source", "Demo interaction database"),
                        agent="InteractionAgent",
                    )
                )

        return findings
