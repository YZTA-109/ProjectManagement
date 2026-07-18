import json

from agents.fda_interaction_agent import FdaLabelInteractionAgent
from providers.local_json_provider import LocalJsonInteractionProvider
from providers.openfda_client import OpenFdaLabel


class FakeOpenFdaClient:
    def __init__(self, texts: dict[str, str]):
        self.texts = {name.lower(): text for name, text in texts.items()}
        self.calls: list[str] = []

    def get_label(self, drug_name: str) -> OpenFdaLabel | None:
        normalized = drug_name.strip().lower()
        self.calls.append(normalized)
        text = self.texts.get(normalized)
        if text is None:
            return None
        return OpenFdaLabel(
            generic_name=normalized.upper(),
            brand_name=None,
            boxed_warning=None,
            warnings=None,
            drug_interactions=text[:100],
            indications=None,
            drug_interactions_full=text,
        )


def make_agent(tmp_path, texts, local_rules=None):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps(local_rules or []), encoding="utf-8")
    return FdaLabelInteractionAgent(
        openfda_client=FakeOpenFdaClient(texts),
        rules_provider=LocalJsonInteractionProvider(rules_path),
    )


def test_new_drug_label_mentions_current_med(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["methotrexate"]
    agent = make_agent(
        tmp_path,
        {"ibuprofen": "Concomitant use with methotrexate may increase toxicity."},
    )

    findings = agent.analyze(healthy_patient, new_medication="ibuprofen")

    assert len(findings) == 1
    assert "methotrexate" in findings[0].title
    assert findings[0].agent == "FdaLabelInteractionAgent"
    assert "methotrexate" in findings[0].description


def test_current_med_label_mentions_new_drug(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["warfarin"]
    agent = make_agent(
        tmp_path,
        {"warfarin": "Avoid concurrent use of fluoxetine due to bleeding risk."},
    )

    findings = agent.analyze(healthy_patient, new_medication="fluoxetine")

    assert len(findings) == 1
    assert findings[0].severity == "high"


def test_severity_defaults_to_medium_without_markers(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["methotrexate"]
    agent = make_agent(
        tmp_path,
        {"ibuprofen": "Clinical studies observed altered methotrexate clearance."},
    )

    findings = agent.analyze(healthy_patient, new_medication="ibuprofen")
    assert findings[0].severity == "medium"


def test_pair_covered_by_local_rule_is_skipped(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["aspirin"]
    agent = make_agent(
        tmp_path,
        {"warfarin": "Avoid aspirin during warfarin therapy."},
        local_rules=[{"drug_a": "warfarin", "drug_b": "aspirin", "severity": "high"}],
    )

    findings = agent.analyze(healthy_patient, new_medication="warfarin")
    assert findings == []


def test_pair_reported_only_once_across_directions(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["methotrexate"]
    agent = make_agent(
        tmp_path,
        {
            "ibuprofen": "May increase methotrexate toxicity.",
            "methotrexate": "NSAIDs such as ibuprofen reduce clearance.",
        },
    )

    findings = agent.analyze(healthy_patient, new_medication="ibuprofen")
    assert len(findings) == 1


def test_no_label_available_returns_empty(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["warfarin"]
    agent = make_agent(tmp_path, {})

    assert agent.analyze(healthy_patient, new_medication="parol") == []


def test_word_boundary_prevents_partial_match(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["aspirin"]
    agent = make_agent(
        tmp_path,
        # "aspirinate" must not match the alias "aspirin"
        {"newdrug": "The aspirinate compound is unrelated."},
    )

    assert agent.analyze(healthy_patient, new_medication="newdrug") == []


def test_excerpt_included_and_trimmed(tmp_path, healthy_patient):
    healthy_patient.current_medications = ["methotrexate"]
    long_text = ("x" * 500) + " methotrexate levels may rise. " + ("y" * 500)
    agent = make_agent(tmp_path, {"ibuprofen": long_text})

    findings = agent.analyze(healthy_patient, new_medication="ibuprofen")
    description = findings[0].description
    assert "methotrexate levels may rise" in description
    assert "…" in description
    assert len(description) < 800
