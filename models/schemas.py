from typing import Literal

from pydantic import BaseModel, Field, field_validator


Severity = Literal["low", "medium", "high", "critical"]


class LabValues(BaseModel):
    """Patient laboratory values used by the rule-based demo agents."""

    egfr: float = Field(
        ...,
        ge=0,
        le=150,
        description="Estimated Glomerular Filtration Rate",
    )
    creatinine: float = Field(
        ...,
        ge=0,
        le=20,
        description="Serum creatinine",
    )
    ast: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Aspartate aminotransferase",
    )
    alt: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Alanine aminotransferase",
    )


class Patient(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=1)
    current_medications: list[str] = Field(default_factory=list)
    lab_values: LabValues

    @field_validator("current_medications")
    @classmethod
    def clean_medication_names(cls, values: list[str]) -> list[str]:
        cleaned = []
        for value in values:
            normalized = value.strip()
            if normalized and normalized.lower() not in [item.lower() for item in cleaned]:
                cleaned.append(normalized)
        return cleaned


class PrescriptionRequest(BaseModel):
    patient: Patient
    new_medication: str = Field(..., min_length=1)

    @field_validator("new_medication")
    @classmethod
    def clean_new_medication(cls, value: str) -> str:
        return value.strip()


class DrugInfo(BaseModel):
    """External data gathered for a single drug (RxNorm + openFDA)."""

    query_name: str
    normalized_name: str | None = None
    rxcui: str | None = None
    is_brand: bool = False
    ingredients: list[str] = Field(default_factory=list)
    openfda_found: bool = False
    boxed_warning: str | None = None
    warnings: str | None = None
    drug_interactions: str | None = None
    indications: str | None = None
    source: str = "unknown"


class RiskFinding(BaseModel):
    title: str
    severity: Severity
    description: str
    recommendation: str
    source: str = "PolyPharm AI demo rule"
    agent: str = "unknown"


class AnalysisResult(BaseModel):
    safety_score: int = Field(..., ge=0, le=100)
    risk_level: str
    findings: list[RiskFinding]
    recommendation_summary: str
    markdown_report: str
    new_drug_info: DrugInfo | None = None
    ai_summary: str | None = None
    ai_model: str | None = None
