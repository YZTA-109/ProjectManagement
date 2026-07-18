from agents.report_agent import ReportAgent
from models.schemas import DrugInfo, RiskFinding


def finding(severity: str) -> RiskFinding:
    return RiskFinding(
        title="Test bulgusu",
        severity=severity,
        description="Açıklama",
        recommendation="Öneri",
    )


def test_summary_without_findings_mentions_no_risk():
    summary = ReportAgent().generate_summary([], risk_level="Düşük Risk")
    assert "risk bulunmadı" in summary.lower()


def test_summary_prioritizes_high_findings():
    summary = ReportAgent().generate_summary(
        [finding("high"), finding("medium")], risk_level="Yüksek Risk"
    )
    assert "yüksek öncelikli" in summary.lower()


def test_markdown_report_contains_drug_info_and_ai_summary(healthy_patient):
    drug_info = DrugInfo(
        query_name="Coumadin",
        normalized_name="Coumadin",
        rxcui="202421",
        is_brand=True,
        ingredients=["warfarin"],
        source="RxNorm (local)",
    )

    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient,
        new_medication="Coumadin",
        safety_score=65,
        risk_level="Orta Risk",
        findings=[finding("medium")],
        summary="Özet",
        drug_info=drug_info,
        ai_summary="AI değerlendirme metni",
    )

    assert "İlaç Bilgisi (Harici Kaynaklar)" in report
    assert "202421" in report
    assert "Yapay Zeka Değerlendirmesi" in report
    assert "AI değerlendirme metni" in report


def test_markdown_report_without_optional_sections(healthy_patient):
    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient,
        new_medication="aspirin",
        safety_score=100,
        risk_level="Düşük Risk",
        findings=[],
        summary="Özet",
    )

    assert "İlaç Bilgisi" not in report
    assert "Yapay Zeka Değerlendirmesi" not in report
    assert "Belirgin bir risk bulgusu tespit edilmedi." in report
