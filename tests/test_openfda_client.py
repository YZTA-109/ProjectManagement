import requests

from providers.openfda_client import OpenFdaClient


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


def label_payload() -> dict:
    return {
        "results": [
            {
                "openfda": {
                    "generic_name": ["WARFARIN SODIUM"],
                    "brand_name": ["COUMADIN"],
                },
                "boxed_warning": ["WARNING: BLEEDING RISK ..."],
                "warnings": ["Some warning text"],
                "drug_interactions": ["Interacts with aspirin"],
                "indications_and_usage": ["Anticoagulation"],
            }
        ]
    }


def test_parses_label_fields(monkeypatch):
    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: FakeResponse(200, label_payload())
    )

    label = OpenFdaClient(api_key="test").get_label("warfarin")

    assert label is not None
    assert label.generic_name == "WARFARIN SODIUM"
    assert label.boxed_warning.startswith("WARNING")
    assert label.drug_interactions == "Interacts with aspirin"


def test_returns_none_on_http_error(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(404, {}))
    assert OpenFdaClient(api_key="test").get_label("nonexistent") is None


def test_returns_none_on_network_error(monkeypatch):
    def raise_error(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", raise_error)
    assert OpenFdaClient(api_key="test").get_label("warfarin") is None


def test_caches_lookups(monkeypatch):
    calls = []

    def fake_get(*args, **kwargs):
        calls.append(1)
        return FakeResponse(200, label_payload())

    monkeypatch.setattr(requests, "get", fake_get)
    client = OpenFdaClient(api_key="test")

    client.get_label("warfarin")
    client.get_label("Warfarin ")

    assert len(calls) == 1


def test_long_sections_are_truncated(monkeypatch):
    payload = label_payload()
    payload["results"][0]["warnings"] = ["x" * 5000]
    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse(200, payload))

    label = OpenFdaClient(api_key="test").get_label("warfarin")
    assert len(label.warnings) < 1600
    assert label.warnings.endswith("[…]")
