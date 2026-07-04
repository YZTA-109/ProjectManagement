from models.schemas import Patient, RiskFinding


RENAL_SENSITIVE_MEDICATIONS = {
    "metformin",
    "furosemide",
    "ibuprofen",
    "naproxen",
    "lisinopril",
    "enalapril",
    "digoxin",
}

HEPATIC_RISK_MEDICATIONS = {
    "atorvastatin",
    "simvastatin",
    "warfarin",
    "paracetamol",
    "acetaminophen",
    "methotrexate",
}


def _normalize(value: str) -> str:
    return value.lower().strip()


class LabRiskAgent:
    """Analyzes patient lab values with rule-based demo logic."""

    def analyze(self, patient: Patient, new_medication: str) -> list[RiskFinding]:
        findings: list[RiskFinding] = []

        new_med = _normalize(new_medication)
        egfr = patient.lab_values.egfr
        ast = patient.lab_values.ast
        alt = patient.lab_values.alt

        findings.extend(self._renal_findings(egfr=egfr, new_medication=new_med))
        findings.extend(self._hepatic_findings(ast=ast, alt=alt, new_medication=new_med))
        findings.extend(self._polypharmacy_findings(patient=patient))

        return findings

    def _renal_findings(self, egfr: float, new_medication: str) -> list[RiskFinding]:
        findings: list[RiskFinding] = []
        renal_sensitive = new_medication in RENAL_SENSITIVE_MEDICATIONS

        if egfr < 30:
            severity = "high" if renal_sensitive else "medium"
            findings.append(
                RiskFinding(
                    title="Ciddi böbrek fonksiyon riski",
                    severity=severity,
                    description=(
                        f"Hastanın eGFR değeri {egfr}. Bu değer ciddi böbrek fonksiyon "
                        "azalmasına işaret edebilir."
                    ),
                    recommendation=(
                        "Yeni ilaç böbrekten atılıyorsa doz ayarı, alternatif tedavi veya "
                        "uzman değerlendirmesi yapılmalıdır."
                    ),
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            )
        elif egfr < 60:
            findings.append(
                RiskFinding(
                    title="Orta düzey böbrek fonksiyon riski",
                    severity="medium" if renal_sensitive else "low",
                    description=(
                        f"Hastanın eGFR değeri {egfr}. Böbrek fonksiyonunda azalma olabilir."
                    ),
                    recommendation=(
                        "Renal doz ayarı gerekip gerekmediği ve takip sıklığı kontrol edilmelidir."
                    ),
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            )

        return findings

    def _hepatic_findings(
        self,
        ast: float,
        alt: float,
        new_medication: str,
    ) -> list[RiskFinding]:
        findings: list[RiskFinding] = []
        hepatic_sensitive = new_medication in HEPATIC_RISK_MEDICATIONS

        if ast > 120 or alt > 120:
            findings.append(
                RiskFinding(
                    title="Belirgin karaciğer fonksiyon riski",
                    severity="high" if hepatic_sensitive else "medium",
                    description=(
                        f"AST: {ast}, ALT: {alt}. Karaciğer enzimleri belirgin yüksek görünüyor."
                    ),
                    recommendation=(
                        "Hepatotoksisite riski olan ilaçlarda alternatif tedavi veya yakın takip "
                        "değerlendirilmelidir."
                    ),
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            )
        elif ast > 80 or alt > 80:
            findings.append(
                RiskFinding(
                    title="Karaciğer fonksiyon riski",
                    severity="medium",
                    description=(
                        f"AST: {ast}, ALT: {alt}. Karaciğer enzimleri yüksek görünüyor."
                    ),
                    recommendation=(
                        "Karaciğerden metabolize olan ilaçlar için risk/fayda değerlendirmesi yapılmalıdır."
                    ),
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            )

        return findings

    def _polypharmacy_findings(self, patient: Patient) -> list[RiskFinding]:
        medication_count = len(patient.current_medications)

        if patient.age >= 65 and medication_count >= 5:
            return [
                RiskFinding(
                    title="Yaşlı hastada polifarmasi riski",
                    severity="medium",
                    description=(
                        f"Hasta {patient.age} yaşında ve {medication_count} mevcut ilaç kullanıyor."
                    ),
                    recommendation=(
                        "Tedavi listesi gereklilik, doz, tedavi süresi ve potansiyel advers olaylar "
                        "açısından gözden geçirilmelidir."
                    ),
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            ]

        if medication_count >= 8:
            return [
                RiskFinding(
                    title="Çoklu ilaç kullanımı riski",
                    severity="medium",
                    description=f"Hastanın mevcut ilaç sayısı {medication_count}.",
                    recommendation="İlaç listesinde mükerrerlik ve gereksiz tedaviler kontrol edilmelidir.",
                    source="Rule-based demo clinical logic",
                    agent="LabRiskAgent",
                )
            ]

        return []
