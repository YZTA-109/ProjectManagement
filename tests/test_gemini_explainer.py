from agents.gemini_explainer import GeminiExplainer
from models.schemas import RiskFinding


class FakeModels:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error
        self.last_kwargs = None

    def generate_content(self, **kwargs):
        self.last_kwargs = kwargs
        if self.error:
            raise self.error

        class Response:
            text = self.text

        return Response()


class FakeClient:
    def __init__(self, text=None, error=None):
        self.models = FakeModels(text=text, error=error)


def finding() -> RiskFinding:
    return RiskFinding(
        title="warfarin - aspirin etkileşimi",
        severity="high",
        description="Kanama riski",
        recommendation="INR takibi",
    )


def test_not_available_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    explainer = GeminiExplainer(api_key=None)
    assert not explainer.available


def test_returns_none_when_unavailable(monkeypatch, healthy_patient):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    explainer = GeminiExplainer(api_key=None)

    summary = explainer.generate_summary(
        patient=healthy_patient,
        new_medication="aspirin",
        findings=[finding()],
        safety_score=65,
        risk_level="Orta Risk",
    )
    assert summary is None


def test_generates_summary_with_fake_client(healthy_patient):
    client = FakeClient(text="Özet metni")
    explainer = GeminiExplainer(client=client)

    summary = explainer.generate_summary(
        patient=healthy_patient,
        new_medication="aspirin",
        findings=[finding()],
        safety_score=65,
        risk_level="Orta Risk",
    )

    assert summary == "Özet metni"
    prompt = client.models.last_kwargs["contents"]
    assert "aspirin" in prompt
    assert "warfarin - aspirin etkileşimi" in prompt


def test_api_error_returns_none(healthy_patient):
    explainer = GeminiExplainer(client=FakeClient(error=RuntimeError("quota")))

    summary = explainer.generate_summary(
        patient=healthy_patient,
        new_medication="aspirin",
        findings=[],
        safety_score=100,
        risk_level="Düşük Risk",
    )
    assert summary is None
