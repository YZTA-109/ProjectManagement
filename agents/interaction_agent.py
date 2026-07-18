from pathlib import Path

from models.schemas import Patient, RiskFinding

from providers.drug_data_service import DrugDataService
from providers.local_json_provider import LocalJsonInteractionProvider


def _normalize_drug_name(value: str) -> str:
    return value.lower().strip()


class InteractionAgent:
    """Checks drug-drug interaction rules.

    Sprint 2 scope:
    - Rules come from a pluggable provider (local JSON by default).
    - Drug names are expanded to their RxNorm ingredients when the local
      RxNorm database is available, so brand names (e.g. Coumadin) match
      ingredient-based rules (e.g. warfarin).
    """

    def __init__(
        self,
        rules_provider: LocalJsonInteractionProvider | None = None,
        drug_service: DrugDataService | None = None,
        data_path: Path | None = None,
    ):
        self.rules_provider = rules_provider or LocalJsonInteractionProvider(data_path)
        self.drug_service = drug_service

    def _aliases(self, drug_name: str) -> set[str]:
        """Raw name plus resolved RxNorm ingredients, all lowercase."""
        aliases = {_normalize_drug_name(drug_name)}
        if self.drug_service is not None:
            aliases.update(self.drug_service.resolve_to_ingredients(drug_name))
        return {alias for alias in aliases if alias}

    def analyze(self, patient: Patient, new_medication: str) -> list[RiskFinding]:
        findings: list[RiskFinding] = []

        current_aliases: set[str] = set()
        for medication in patient.current_medications:
            if medication.strip():
                current_aliases.update(self._aliases(medication))

        new_aliases = self._aliases(new_medication)
        matched_rules: set[int] = set()

        for index, item in enumerate(self.rules_provider.get_interaction_rules()):
            drug_a = _normalize_drug_name(item.get("drug_a", ""))
            drug_b = _normalize_drug_name(item.get("drug_b", ""))

            if not drug_a or not drug_b or index in matched_rules:
                continue

            interaction_exists = (
                drug_a in new_aliases and drug_b in current_aliases
            ) or (
                drug_b in new_aliases and drug_a in current_aliases
            )

            if interaction_exists:
                matched_rules.add(index)
                findings.append(
                    RiskFinding(
                        title=f"{item['drug_a']} - {item['drug_b']} etkileşimi",
                        severity=item.get("severity", "medium"),
                        description=item.get(
                            "description",
                            "Bu ilaç kombinasyonu için etkileşim kuralı bulundu.",
                        ),
                        recommendation=item.get(
                            "recommendation",
                            "Kombinasyonu klinik bağlamda yeniden değerlendirin.",
                        ),
                        source=item.get("source", "Local interaction database"),
                        agent="InteractionAgent",
                    )
                )

        return findings
