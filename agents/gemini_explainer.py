"""Gemini-based clinical explanation agent.

Turns the rule-based findings plus openFDA label context into a short,
readable Turkish summary for the physician. This agent is strictly
optional: when no API key is configured or the call fails, it returns
``None`` and the orchestrator keeps the rule-based summary.
"""

import os

from models.schemas import DrugInfo, Patient, RiskFinding

DEFAULT_MODEL = "gemini-3.1-flash-lite"

SYSTEM_INSTRUCTION = (
    "Sen bir klinik eczacılık asistanısın. Bir karar destek prototipi için "
    "reçete güvenlik analizini özetliyorsun. Kurallar:\n"
    "- Türkçe yaz, en fazla 200 kelime.\n"
    "- Teşhis koyma, tedavi önerme; yalnızca riskleri açıkla ve hekimin "
    "değerlendirmesi gereken noktaları vurgula.\n"
    "- Verilen bulguların dışına çıkma, yeni risk uydurma.\n"
    "- Net başlıksız akıcı 2-3 paragraf yaz.\n"
    "- Sonuna tek cümlelik 'bu çıktı hekim kararının yerine geçmez' uyarısı ekle."
)


class GeminiExplainer:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        client=None,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self._client = client

    @property
    def available(self) -> bool:
        return bool(self.api_key) or self._client is not None

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_summary(
        self,
        patient: Patient,
        new_medication: str,
        findings: list[RiskFinding],
        safety_score: int,
        risk_level: str,
        drug_info: DrugInfo | None = None,
    ) -> str | None:
        if not self.available:
            return None

        prompt = self._build_prompt(
            patient=patient,
            new_medication=new_medication,
            findings=findings,
            safety_score=safety_score,
            risk_level=risk_level,
            drug_info=drug_info,
        )

        try:
            client = self._get_client()
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "temperature": 0.3,
                },
            )
            text = (response.text or "").strip()
        except Exception:
            return None

        return text or None

    def _build_prompt(
        self,
        patient: Patient,
        new_medication: str,
        findings: list[RiskFinding],
        safety_score: int,
        risk_level: str,
        drug_info: DrugInfo | None,
    ) -> str:
        lines = [
            "Reçete güvenlik analizi verileri:",
            f"- Hasta: {patient.age} yaşında, {patient.gender}",
            f"- Mevcut ilaçlar: {', '.join(patient.current_medications) or 'yok'}",
            (
                f"- Laboratuvar: eGFR {patient.lab_values.egfr}, "
                f"kreatinin {patient.lab_values.creatinine}, "
                f"AST {patient.lab_values.ast}, ALT {patient.lab_values.alt}"
            ),
            f"- Yeni yazılmak istenen ilaç: {new_medication}",
            f"- Güvenlik skoru: {safety_score}/100, risk seviyesi: {risk_level}",
        ]

        if drug_info is not None:
            if drug_info.normalized_name:
                lines.append(
                    f"- RxNorm eşleşmesi: {drug_info.normalized_name} "
                    f"(etken madde: {', '.join(drug_info.ingredients) or 'bilinmiyor'})"
                )
            if drug_info.boxed_warning:
                lines.append(f"- openFDA kutulu uyarı (İngilizce): {drug_info.boxed_warning}")
            if drug_info.drug_interactions:
                lines.append(
                    f"- openFDA etkileşim metni (İngilizce): {drug_info.drug_interactions}"
                )

        if findings:
            lines.append("- Kural tabanlı bulgular:")
            for finding in findings:
                lines.append(
                    f"  * [{finding.severity}] {finding.title}: {finding.description}"
                )
        else:
            lines.append("- Kural tabanlı bulgu yok.")

        lines.append(
            "\nBu verilere dayanarak hekim için kısa bir klinik değerlendirme özeti yaz."
        )
        return "\n".join(lines)
