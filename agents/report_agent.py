from models.schemas import RiskFinding


class ReportAgent:
    def generate_summary(self, findings: list[RiskFinding], risk_level: str) -> str:
        if not findings:
            return (
                "Belirgin bir risk bulunmadı. Yine de bu sonuç klinik karar yerine "
                "geçmez; hekim değerlendirmesi gereklidir."
            )

        high_risks = [f for f in findings if f.severity == "high"]
        medium_risks = [f for f in findings if f.severity == "medium"]

        if high_risks:
            return (
                "Yüksek riskli bulgular tespit edildi. Reçete klinik uzman tarafından "
                "yeniden değerlendirilmeli, doz ayarı veya alternatif tedavi seçenekleri "
                "gözden geçirilmelidir."
            )

        if medium_risks:
            return (
                "Orta düzey riskli bulgular tespit edildi. İlgili ilaçlar, laboratuvar "
                "değerleri ve hasta yaşı dikkate alınarak dikkatli değerlendirme yapılmalıdır."
            )

        return (
            f"Genel risk seviyesi: {risk_level}. Bulgular düşük öncelikli görünmektedir; "
            "klinik bağlam içinde değerlendirilmelidir."
        )