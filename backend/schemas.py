from pydantic import BaseModel, Field
from typing import List, Optional

class Benefit(BaseModel):
    benefit_name: str = Field(description="Name of the benefit, e.g., Room Rent, Mental Illness, Maternity")
    limit: Optional[str] = Field(description="Financial or percentage limit, e.g., '1% of Sum Insured', 'Upto 5000'")
    waiting_period: Optional[str] = Field(description="Waiting period if any, e.g., '24 months', 'None'")

class Exclusion(BaseModel):
    exclusion_type: str = Field(description="Type of exclusion, e.g., Cosmetic Surgery, Hazardous Sports")
    icd_codes: Optional[List[str]] = Field(description="Any specific ICD codes mentioned for exclusions")

class InsurancePlanData(BaseModel):
    insurer_name: str
    plan_name: str
    plan_type: str = Field(description="e.g., Indemnity, Base, Floater")
    benefits: List[Benefit]
    exclusions: List[Exclusion]