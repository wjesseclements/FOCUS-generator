from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import date

class GenerateCURRequest(BaseModel):
    profile: str
    distribution: str 
    row_count: int
    providers: List[str]
    multi_month: Optional[bool] = False
    trend_options: Optional[Dict[str, Any]] = None
    
    @validator('profile')
    def validate_profile(cls, v):
        valid_profiles = ["Greenfield", "Large Business", "Enterprise"]
        if v not in valid_profiles:
            raise ValueError(f"Profile must be one of: {valid_profiles}")
        return v
    
    @validator('distribution')
    def validate_distribution(cls, v):
        valid_distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
        if v not in valid_distributions:
            raise ValueError(f"Distribution must be one of: {valid_distributions}")
        return v
    
    @validator('row_count')
    def validate_row_count(cls, v):
        if v < 1 or v > 1000:
            raise ValueError("Row count must be between 1 and 1000")
        return v
    
    @validator('providers')
    def validate_providers(cls, v):
        valid_providers = ["aws", "azure", "gcp"]
        if not v:
            raise ValueError("At least one provider must be selected")
        for provider in v:
            if provider not in valid_providers:
                raise ValueError(f"Provider must be one of: {valid_providers}")
        return v

class TrendOptions(BaseModel):
    monthCount: int
    scenario: str
    parameters: Dict[str, Any]
    
    @validator('monthCount')
    def validate_month_count(cls, v):
        if v < 2 or v > 12:
            raise ValueError("Month count must be between 2 and 12")
        return v
    
    @validator('scenario')
    def validate_scenario(cls, v):
        valid_scenarios = ["linear", "seasonal", "stepChange", "anomaly"]
        if v not in valid_scenarios:
            raise ValueError(f"Scenario must be one of: {valid_scenarios}")
        return v