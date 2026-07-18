import json

import pytest

from agents.interaction_agent import InteractionAgent
from providers.drug_data_service import DrugDataService
from providers.local_json_provider import LocalJsonInteractionProvider
from providers.rxnorm_provider import DEFAULT_DB_PATH


def make_agent(tmp_path, rules, drug_service=None):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(rules), encoding="utf-8")
    return InteractionAgent(
        rules_provider=LocalJsonInteractionProvider(rules_path),
        drug_service=drug_service,
    )


BASE_RULE = {
    "drug_a": "warfarin",
    "drug_b": "aspirin",
    "severity": "high",
    "description": "Kanama riski",
    "recommendation": "INR takibi",
}


def test_detects_interaction_in_both_directions(tmp_path, healthy_patient):
    agent = make_agent(tmp_path, [BASE_RULE])

    healthy_patient.current_medications = ["warfarin"]
    findings = agent.analyze(healthy_patient, new_medication="aspirin")
    assert len(findings) == 1
    assert findings[0].severity == "high"

    healthy_patient.current_medications = ["aspirin"]
    findings = agent.analyze(healthy_patient, new_medication="warfarin")
    assert len(findings) == 1


def test_no_finding_without_matching_rule(tmp_path, healthy_patient):
    agent = make_agent(tmp_path, [BASE_RULE])
    healthy_patient.current_medications = ["metformin"]

    findings = agent.analyze(healthy_patient, new_medication="aspirin")
    assert findings == []


def test_matching_is_case_insensitive(tmp_path, healthy_patient):
    agent = make_agent(tmp_path, [BASE_RULE])
    healthy_patient.current_medications = ["  WARFARIN "]

    findings = agent.analyze(healthy_patient, new_medication="Aspirin")
    assert len(findings) == 1


@pytest.mark.skipif(not DEFAULT_DB_PATH.exists(), reason="rxnorm.db not built")
def test_brand_name_resolves_to_ingredient_rule(tmp_path, healthy_patient):
    service = DrugDataService(use_openfda=False)
    agent = make_agent(tmp_path, [BASE_RULE], drug_service=service)

    healthy_patient.current_medications = ["Coumadin"]
    findings = agent.analyze(healthy_patient, new_medication="aspirin")

    assert len(findings) == 1
    assert "warfarin" in findings[0].title.lower()


def test_rule_matched_only_once_with_alias_overlap(tmp_path, healthy_patient):
    class FakeService:
        def resolve_to_ingredients(self, name):
            return {"coumadin": ["warfarin"], "warfarin": ["warfarin"]}.get(
                name.strip().lower(), [name.strip().lower()]
            )

    agent = make_agent(tmp_path, [BASE_RULE], drug_service=FakeService())
    healthy_patient.current_medications = ["Coumadin", "warfarin"]

    findings = agent.analyze(healthy_patient, new_medication="aspirin")
    assert len(findings) == 1
