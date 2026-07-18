from datetime import datetime

from models.schemas import DrugInfo, Patient, RiskFinding


class ReportAgent:
    def generate_summary(self, findings: list[RiskFinding], risk_level: str) -> str:
        if not findings:
            return (
                "Belirgin bir risk bulunmadı. Yine de bu çıktı klinik karar yerine geçmez; "
                "hekim değerlendirmesi gereklidir."
            )

        critical_or_high = [
            finding for finding in findings if finding.severity in {"critical", "high"}
        ]
        medium_risks = [finding for finding in findings if finding.severity == "medium"]

        if critical_or_high:
            return (
                "Yüksek öncelikli risk bulguları tespit edildi. Reçete klinik uzman tarafından "
                "yeniden değerlendirilmeli; doz ayarı, ilaç değişimi veya ek izlem seçenekleri "
                "gözden geçirilmelidir."
            )

        if medium_risks:
            return (
                "Orta düzey riskli bulgular tespit edildi. İlgili ilaçlar, laboratuvar değerleri "
                "ve hasta profili dikkate alınarak dikkatli değerlendirme yapılmalıdır."
            )

        return (
            f"Genel risk seviyesi: {risk_level}. Bulgular düşük öncelikli görünmektedir; "
            "klinik bağlam içinde değerlendirilmelidir."
        )

    def generate_markdown_report(
        self,
        patient: Patient,
        new_medication: str,
        safety_score: int,
        risk_level: str,
        findings: list[RiskFinding],
        summary: str,
        drug_info: DrugInfo | None = None,
        ai_summary: str | None = None,
    ) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# PolyPharm AI Reçete Güvenlik Raporu",
            "",
            f"**Oluşturulma zamanı:** {created_at}",
            "",
            "> Bu rapor eğitim amaçlı bir karar destek demosudur. Klinik teşhis, reçeteleme veya tedavi kararı yerine geçmez.",
            "",
            "## Hasta Özeti",
            "",
            f"- Yaş: {patient.age}",
            f"- Cinsiyet: {patient.gender}",
            f"- Mevcut ilaçlar: {', '.join(patient.current_medications) if patient.current_medications else 'Yok'}",
            f"- Yeni ilaç: {new_medication}",
            "",
            "## Laboratuvar Değerleri",
            "",
            f"- eGFR: {patient.lab_values.egfr}",
            f"- Kreatinin: {patient.lab_values.creatinine}",
            f"- AST: {patient.lab_values.ast}",
            f"- ALT: {patient.lab_values.alt}",
            "",
            "## Analiz Sonucu",
            "",
            f"- Güvenlik skoru: **{safety_score}/100**",
            f"- Risk seviyesi: **{risk_level}**",
            f"- Özet: {summary}",
            "",
        ]

        if drug_info is not None and drug_info.normalized_name:
            lines.extend(
                [
                    "## İlaç Bilgisi (Harici Kaynaklar)",
                    "",
                    f"- RxNorm eşleşmesi: {drug_info.normalized_name} (RXCUI: {drug_info.rxcui})",
                    f"- Etken madde(ler): {', '.join(drug_info.ingredients) if drug_info.ingredients else 'Bilinmiyor'}",
                    f"- Veri kaynağı: {drug_info.source}",
                    "",
                ]
            )

        if ai_summary:
            lines.extend(
                [
                    "## Yapay Zeka Değerlendirmesi",
                    "",
                    ai_summary,
                    "",
                ]
            )

        lines.extend(
            [
                "## Risk Bulguları",
                "",
            ]
        )

        if not findings:
            lines.append("Belirgin bir risk bulgusu tespit edilmedi.")
        else:
            for index, finding in enumerate(findings, start=1):
                lines.extend(
                    [
                        f"### {index}. {finding.title}",
                        "",
                        f"- Şiddet: `{finding.severity}`",
                        f"- Açıklama: {finding.description}",
                        f"- Öneri: {finding.recommendation}",
                        f"- Kaynak: {finding.source}",
                        f"- Ajan: {finding.agent}",
                        "",
                    ]
                )

        return "\n".join(lines)
