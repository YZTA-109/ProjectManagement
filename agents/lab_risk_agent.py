from models.schemas import Patient, RiskFinding


class LabRiskAgent:
    def analyze(self, patient: Patient, new_medication: str) -> list[RiskFinding]:
        findings = []

        egfr = patient.lab_values.egfr
        ast = patient.lab_values.ast
        alt = patient.lab_values.alt

        if egfr < 30:
            findings.append(
                RiskFinding(
                    title="Ciddi böbrek fonksiyon riski",
                    severity="high",
                    description=(
                        f"Hastanın eGFR değeri {egfr}. Bu değer ciddi böbrek fonksiyon "
                        "azalmasına işaret edebilir. Yeni ilaç böbrekten atılıyorsa doz "
                        "ayarlaması veya alternatif değerlendirmesi gerekebilir."
                    ),
                    source="Rule-based demo clinical logic"
                )
            )
        elif egfr < 60:
            findings.append(
                RiskFinding(
                    title="Orta düzey böbrek fonksiyon riski",
                    severity="medium",
                    description=(
                        f"Hastanın eGFR değeri {egfr}. Böbrek fonksiyonunda azalma olabilir. "
                        "Yeni ilaç için renal doz ayarı kontrol edilmelidir."
                    ),
                    source="Rule-based demo clinical logic"
                )
            )

        if ast > 80 or alt > 80:
            findings.append(
                RiskFinding(
                    title="Karaciğer fonksiyon riski",
                    severity="medium",
                    description=(
                        f"AST: {ast}, ALT: {alt}. Karaciğer enzimleri yüksek görünüyor. "
                        "Hepatotoksisite riski olan ilaçlarda dikkatli olunmalıdır."
                    ),
                    source="Rule-based demo clinical logic"
                )
            )

        if patient.age >= 65 and len(patient.current_medications) >= 5:
            findings.append(
                RiskFinding(
                    title="Polifarmasi riski",
                    severity="medium",
                    description=(
                        f"Hasta {patient.age} yaşında ve {len(patient.current_medications)} "
                        "ilaç kullanıyor. Yaşlı hastalarda çoklu ilaç kullanımı advers olay "
                        "riskini artırabilir."
                    ),
                    source="Rule-based demo clinical logic"
                )
            )

        return findings