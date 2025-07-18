from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import date
from validation import (
    validate_enum_value, 
    validate_numeric_range, 
    validate_array_length,
    validate_json_object,
    SecurityValidationMixin
)

class GenerateCURRequest(BaseModel, SecurityValidationMixin):
    profile: str = Field(..., description="User profile type")
    distribution: str = Field(..., description="Cost distribution pattern")
    row_count: int = Field(..., ge=1, le=100000, description="Number of rows to generate")
    providers: List[str] = Field(..., min_items=1, max_items=10, description="Cloud providers")
    multi_month: Optional[bool] = Field(False, description="Generate multi-month data")
    trend_options: Optional[Dict[str, Any]] = Field(None, description="Trend configuration")
    
    @validator('profile')
    def validate_profile(cls, v):
        valid_profiles = ["Greenfield", "Large Business", "Enterprise"]
        return validate_enum_value(v, valid_profiles, "profile")
    
    @validator('distribution')
    def validate_distribution(cls, v):
        valid_distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
        return validate_enum_value(v, valid_distributions, "distribution")
    
    @validator('row_count')
    def validate_row_count(cls, v):
        return validate_numeric_range(v, 1, 100000, "row_count")
    
    @validator('providers')
    def validate_providers(cls, v):
        valid_providers = ["aws", "azure", "gcp"]
        validated_array = validate_array_length(v, 10, "providers")
        
        if not validated_array:
            raise ValueError("At least one provider must be selected")
        
        for provider in validated_array:
            validate_enum_value(provider, valid_providers, "provider")
        
        return validated_array
    
    @validator('trend_options')
    def validate_trend_options(cls, v):
        if v is not None:
            return validate_json_object(v, max_depth=3, max_keys=50)
        return v

class TrendOptions(BaseModel, SecurityValidationMixin):
    monthCount: int = Field(..., ge=2, le=12, description="Number of months to generate")
    scenario: str = Field(..., description="Trend scenario type")
    parameters: Dict[str, Any] = Field(..., description="Scenario parameters")
    
    @validator('monthCount')
    def validate_month_count(cls, v):
        return validate_numeric_range(v, 2, 12, "monthCount")
    
    @validator('scenario')
    def validate_scenario(cls, v):
        valid_scenarios = ["linear", "seasonal", "stepChange", "anomaly"]
        return validate_enum_value(v, valid_scenarios, "scenario")
    
    @validator('parameters')
    def validate_parameters(cls, v):
        return validate_json_object(v, max_depth=2, max_keys=20)