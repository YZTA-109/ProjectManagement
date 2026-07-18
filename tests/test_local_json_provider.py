import json

import pytest

from providers.local_json_provider import LocalJsonInteractionProvider


def test_loads_rules_from_file(tmp_path):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps([{"drug_a": "a", "drug_b": "b"}]), encoding="utf-8")

    provider = LocalJsonInteractionProvider(rules_path)
    assert provider.get_interaction_rules() == [{"drug_a": "a", "drug_b": "b"}]


def test_missing_file_returns_empty_list(tmp_path):
    provider = LocalJsonInteractionProvider(tmp_path / "missing.json")
    assert provider.get_interaction_rules() == []


def test_non_list_payload_raises(tmp_path):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

    with pytest.raises(ValueError):
        LocalJsonInteractionProvider(rules_path).get_interaction_rules()


def test_default_project_rules_are_valid():
    rules = LocalJsonInteractionProvider().get_interaction_rules()
    assert len(rules) >= 20
    for rule in rules:
        assert rule["drug_a"] and rule["drug_b"]
        assert rule["severity"] in {"low", "medium", "high", "critical"}
