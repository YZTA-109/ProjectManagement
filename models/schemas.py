from pydantic import BaseModel, Field
from typing import List, Optional


class LabValues(BaseModel):
    egfr: float = Field(..., description="Estimated Glomerular Filtration Rate")
    creatinine: float = Field(..., description="Serum creatinine")
    ast: float = Field(..., description="Aspartate aminotransferase")
    alt: float = Field(..., description="Alanine aminotransferase")


class Patient(BaseModel):
    age: int
    gender: str
    current_medications: List[str]
    lab_values: LabValues


class PrescriptionRequest(BaseModel):
    patient: Patient
    new_medication: str


class RiskFinding(BaseModel):
    title: str
    severity: str  # low, medium, high
    description: str
    source: Optional[str] = None


class AnalysisResult(BaseModel):
    safety_score: int
    risk_level: str
    findings: List[RiskFinding]
    recommendation_summary: str