import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.schemas import LabValues, Patient


@pytest.fixture
def healthy_patient() -> Patient:
    return Patient(
        age=40,
        gender="Erkek",
        current_medications=["metformin"],
        lab_values=LabValues(egfr=95, creatinine=0.9, ast=25, alt=22),
    )


@pytest.fixture
def high_risk_patient() -> Patient:
    return Patient(
        age=76,
        gender="Kadın",
        current_medications=[
            "warfarin",
            "metformin",
            "lisinopril",
            "furosemide",
            "digoxin",
        ],
        lab_values=LabValues(egfr=24, creatinine=2.4, ast=130, alt=140),
    )
