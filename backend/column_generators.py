"""
Column value generators for FOCUS data generation.

This module provides a clean architecture for generating column values,
replacing the monolithic generate_value_for_column function with specialized
generators following the Strategy pattern.
"""

import random
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from backend.focus_metadata import FOCUS_METADATA
from backend.logging_config import setup_logging

logger = setup_logging(__name__)

# Central provider mapping to ensure consistency across all generators
CLOUD_PROVIDER_MAPPING = {
    "AWS": "AWS",
    "AZURE": "AZURE",
    "GCP": "GCP"
}


@dataclass
class GenerationContext:
    """Context object containing all generation parameters for column generation."""
    col_name: str
    row_idx: int
    row_data: Dict[str, Any]
    row_count: int
    profile: str
    total_dataset_cost: float
    distribution: str
    cloud_provider: str = "AWS"
    billing_period: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class ColumnGenerator(ABC):
    """Base class for column value generators."""
    
    @abstractmethod
    def generate_value(self, context: GenerationContext) -> Any:
        """Generate a value for the column."""
        pass
    
    def can_handle(self, col_name: str) -> bool:
        """Check if this generator can handle the column."""
        return col_name in self.supported_columns()
    
    @abstractmethod
    def supported_columns(self) -> List[str]:
        """Return list of supported column names."""
        pass


class ChargeGenerator(ColumnGenerator):
    """Handles charge-related columns."""
    
    # Weighted distributions for charge categories
    CHARGE_CATEGORY_WEIGHTS = {
        "Usage": 0.7,
        "Purchase": 0.15,
        "Tax": 0.05,
        "Credit": 0.05,
        "Adjustment": 0.05,
    }
    
    def supported_columns(self) -> List[str]:
        return ["ChargeCategory", "ChargeFrequency"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "ChargeCategory":
            return self._generate_charge_category()
        elif context.col_name == "ChargeFrequency":
            return self._generate_charge_frequency(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_charge_category(self) -> str:
        """Generate a weighted random charge category."""
        categories = list(self.CHARGE_CATEGORY_WEIGHTS.keys())
        weights = list(self.CHARGE_CATEGORY_WEIGHTS.values())
        return random.choices(categories, weights=weights, k=1)[0]
    
    def _generate_charge_frequency(self, context: GenerationContext) -> str:
        """Generate charge frequency based on charge category."""
        charge_cat = context.row_data.get("ChargeCategory")
        if charge_cat == "Purchase":
            # Purchase charges can't be Usage-Based
            return random.choice(["One-Time", "Recurring"])
        else:
            # For other categories, all three options are valid
            return random.choice(["One-Time", "Recurring", "Usage-Based"])


class CostGenerator(ColumnGenerator):
    """Handles cost-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["BilledCost"]
    
    def generate_value(self, context: GenerationContext) -> float:
        if context.col_name == "BilledCost":
            return self._distribute_billed_cost(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _distribute_billed_cost(self, context: GenerationContext) -> float:
        """Distribute the dataset's total cost across rows."""
        base_per_row = context.total_dataset_cost / context.row_count
        # Random factor of ±20%
        factor = random.uniform(0.8, 1.2)
        return round(base_per_row * factor, 2)


class DateTimeGenerator(ColumnGenerator):
    """Handles date/time columns."""
    
    def supported_columns(self) -> List[str]:
        return ["BillingPeriodStart", "BillingPeriodEnd", "ChargePeriodStart", "ChargePeriodEnd"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "BillingPeriodStart":
            return "2024-01-01T00:00:00Z"
        elif context.col_name == "BillingPeriodEnd":
            return "2024-02-01T00:00:00Z"
        elif context.col_name == "ChargePeriodStart":
            return self._generate_charge_period_start(context)
        elif context.col_name == "ChargePeriodEnd":
            return self._generate_charge_period_end(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_charge_period_start(self, context: GenerationContext) -> str:
        """Generate charge period start - each row is a daily usage period."""
        start_dt = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=context.row_idx)
        return start_dt.isoformat()
    
    def _generate_charge_period_end(self, context: GenerationContext) -> str:
        """Generate charge period end - 1 day after start."""
        cps_str = context.row_data.get("ChargePeriodStart")
        if cps_str:
            start_dt = datetime.fromisoformat(cps_str)
            end_dt = start_dt + timedelta(days=1)
            return end_dt.isoformat()
        # Fallback
        return "2024-01-02T00:00:00+00:00"


class ServiceGenerator(ColumnGenerator):
    """Handles service-related columns."""
    
    # Default service category weights (Evenly Distributed)
    DEFAULT_SERVICE_CATEGORY_WEIGHTS = {
        "Compute": 0.3,
        "Storage": 0.2,
        "Databases": 0.2,
        "Networking": 0.1,
        "AI and Machine Learning": 0.1,
        "Other": 0.1,
    }
    
    # Distribution-specific service category weights
    DISTRIBUTION_SERVICE_WEIGHTS = {
        "Evenly Distributed": DEFAULT_SERVICE_CATEGORY_WEIGHTS,
        
        "ML-Focused": {
            "Compute": 0.25,
            "Storage": 0.15,
            "Databases": 0.15,
            "Networking": 0.05,
            "AI and Machine Learning": 0.35,
            "Other": 0.05,
        },
        
        "Data-Intensive": {
            "Compute": 0.2,
            "Storage": 0.35,
            "Databases": 0.3,
            "Networking": 0.05,
            "AI and Machine Learning": 0.05,
            "Other": 0.05,
        },
        
        "Media-Intensive": {
            "Compute": 0.15,
            "Storage": 0.4,
            "Databases": 0.1,
            "Networking": 0.25,
            "AI and Machine Learning": 0.05,
            "Other": 0.05,
        }
    }
    
    def supported_columns(self) -> List[str]:
        return ["ServiceCategory"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "ServiceCategory":
            return self._generate_service_category(context.distribution)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_service_category(self, distribution: str) -> str:
        """Generate service category based on distribution weights."""
        service_weights = self.DISTRIBUTION_SERVICE_WEIGHTS.get(
            distribution, self.DEFAULT_SERVICE_CATEGORY_WEIGHTS
        )
        cats = list(service_weights.keys())
        wts = list(service_weights.values())
        return random.choices(cats, weights=wts, k=1)[0]


class SKUGenerator(ColumnGenerator):
    """Handles SKU-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["SkuId", "SkuPriceId", "PricingUnit"]
    
    def generate_value(self, context: GenerationContext) -> Optional[str]:
        if context.col_name == "SkuId":
            return self._generate_sku_id(context)
        elif context.col_name == "SkuPriceId":
            return self._generate_sku_price_id(context)
        elif context.col_name == "PricingUnit":
            return self._generate_pricing_unit(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_sku_id(self, context: GenerationContext) -> Optional[str]:
        """Generate SKU ID - null if ChargeCategory is Tax."""
        charge_cat = context.row_data.get("ChargeCategory")
        if charge_cat == "Tax":
            return None
        return f"SKU-{uuid.uuid4().hex[:4]}"
    
    def _generate_sku_price_id(self, context: GenerationContext) -> Optional[str]:
        """Generate SKU Price ID - null if ChargeCategory is Tax."""
        charge_cat = context.row_data.get("ChargeCategory")
        if charge_cat == "Tax":
            return None
        return f"SKUPRICE-{uuid.uuid4().hex[:4]}"
    
    def _generate_pricing_unit(self, context: GenerationContext) -> Optional[str]:
        """Generate pricing unit based on charge category."""
        charge_cat = context.row_data.get("ChargeCategory")
        if charge_cat in ["Usage", "Purchase"]:
            return random.choice(["Hours", "GB-Hours", "Requests", "Transactions"])
        else:
            return None


class CommitmentDiscountGenerator(ColumnGenerator):
    """Handles commitment discount-related columns."""
    
    def supported_columns(self) -> List[str]:
        return [
            "CommitmentDiscountId",
            "CommitmentDiscountStatus",
            "CommitmentDiscountCategory",
            "CommitmentDiscountQuantity",
            "CommitmentDiscountType",
            "CommitmentDiscountUnit"
        ]
    
    def generate_value(self, context: GenerationContext) -> Optional[Any]:
        if context.col_name == "CommitmentDiscountId":
            return self._generate_commitment_discount_id()
        elif context.col_name == "CommitmentDiscountStatus":
            return self._generate_commitment_discount_status(context)
        elif context.col_name == "CommitmentDiscountCategory":
            return self._generate_commitment_discount_category(context)
        elif context.col_name == "CommitmentDiscountQuantity":
            return self._generate_commitment_discount_quantity(context)
        elif context.col_name == "CommitmentDiscountType":
            return self._generate_commitment_discount_type(context)
        elif context.col_name == "CommitmentDiscountUnit":
            return self._generate_commitment_discount_unit(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_commitment_discount_id(self) -> Optional[str]:
        """Generate commitment discount ID - 20% chance to have one."""
        if random.random() < 0.2:
            return f"CD-{uuid.uuid4().hex[:4]}"
        return None
    
    def _generate_commitment_discount_status(self, context: GenerationContext) -> Optional[str]:
        """Generate commitment discount status."""
        cdid = context.row_data.get("CommitmentDiscountId")
        ccat = context.row_data.get("ChargeCategory")
        if cdid is not None and ccat == "Usage":
            return random.choice(["Used", "Unused"])
        return None
    
    def _generate_commitment_discount_category(self, context: GenerationContext) -> Optional[str]:
        """Generate commitment discount category."""
        cdid = context.row_data.get("CommitmentDiscountId")
        if cdid is not None:
            return random.choice(["Spend", "Usage"])
        return None
    
    def _generate_commitment_discount_quantity(self, context: GenerationContext) -> Optional[float]:
        """Generate commitment discount quantity."""
        cdid = context.row_data.get("CommitmentDiscountId")
        ccat = context.row_data.get("ChargeCategory")
        if cdid is not None and ccat == "Usage":
            return round(random.uniform(1, 50), 2)
        return None
    
    def _generate_commitment_discount_type(self, context: GenerationContext) -> Optional[str]:
        """Generate commitment discount type."""
        cdid = context.row_data.get("CommitmentDiscountId")
        if cdid is not None:
            return random.choice(["Reserved", "SavingsPlan", "Custom"])
        return None
    
    def _generate_commitment_discount_unit(self, context: GenerationContext) -> Optional[str]:
        """Generate commitment discount unit."""
        cdid = context.row_data.get("CommitmentDiscountId")
        if cdid is not None:
            return random.choice(["Hours", "GB", "Requests"])
        return None


class CapacityReservationGenerator(ColumnGenerator):
    """Handles capacity reservation-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["CapacityReservationId", "CapacityReservationStatus"]
    
    def generate_value(self, context: GenerationContext) -> Optional[str]:
        if context.col_name == "CapacityReservationId":
            return self._generate_capacity_reservation_id()
        elif context.col_name == "CapacityReservationStatus":
            return self._generate_capacity_reservation_status(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_capacity_reservation_id(self) -> Optional[str]:
        """Generate capacity reservation ID - 30% chance to have one."""
        if random.random() < 0.3:
            return f"CapRes-{uuid.uuid4().hex[:4]}"
        return None
    
    def _generate_capacity_reservation_status(self, context: GenerationContext) -> Optional[str]:
        """Generate capacity reservation status."""
        crid = context.row_data.get("CapacityReservationId")
        if crid is not None:
            return random.choice(["Used", "Unused"])
        return None


class PricingGenerator(ColumnGenerator):
    """Handles pricing-related columns with validation rules."""
    
    def supported_columns(self) -> List[str]:
        return ["PricingQuantity", "ChargeClass", "PricingCategory"]
    
    def generate_value(self, context: GenerationContext) -> Any:
        if context.col_name == "PricingQuantity":
            return self._generate_pricing_quantity(context)
        elif context.col_name == "ChargeClass":
            return self._generate_charge_class(context)
        elif context.col_name == "PricingCategory":
            return self._generate_pricing_category(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_pricing_quantity(self, context: GenerationContext) -> Optional[float]:
        """Generate pricing quantity following validation rules."""
        charge_cat = context.row_data.get("ChargeCategory")
        charge_class = context.row_data.get("ChargeClass")
        
        # Rule: If ChargeCategory='Usage' => PricingQuantity MUST NOT be null unless ChargeClass='Correction'
        if charge_cat == "Usage" and charge_class != "Correction":
            # Must have a value
            return round(random.uniform(1.0, 100.0), 2)
        elif charge_cat in ["Purchase", "Tax"]:
            # For these categories, quantity is often null
            return None if random.random() < 0.7 else round(random.uniform(1.0, 10.0), 2)
        else:
            # For other categories, 50% chance of having a value
            return round(random.uniform(1.0, 50.0), 2) if random.random() < 0.5 else None
    
    def _generate_charge_class(self, context: GenerationContext) -> Optional[str]:
        """Generate charge class - must be generated before PricingQuantity."""
        # According to FOCUS spec, only "Correction" is allowed (or null)
        # Most charges are null (normal charges), with small chance of "Correction"
        return "Correction" if random.random() < 0.1 else None
    
    def _generate_pricing_category(self, context: GenerationContext) -> str:
        """Generate pricing category."""
        return random.choice(["Standard", "Dynamic", "Committed", "Other"])


class ResourceGenerator(ColumnGenerator):
    """Handles resource-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["ResourceId", "ResourceName", "ResourceType"]
    
    def generate_value(self, context: GenerationContext) -> Optional[str]:
        if context.col_name == "ResourceId":
            return self._generate_resource_id(context)
        elif context.col_name == "ResourceName":
            return self._generate_resource_name(context)
        elif context.col_name == "ResourceType":
            return self._generate_resource_type(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_resource_id(self, context: GenerationContext) -> Optional[str]:
        """Generate resource ID based on service category."""
        service_cat = context.row_data.get("ServiceCategory", "Other")
        
        if service_cat == "Compute":
            return f"i-{uuid.uuid4().hex[:8]}"
        elif service_cat == "Storage":
            return f"vol-{uuid.uuid4().hex[:8]}"
        elif service_cat == "Databases":
            return f"db-{uuid.uuid4().hex[:8]}"
        elif service_cat == "Networking":
            return f"vpc-{uuid.uuid4().hex[:8]}"
        else:
            return f"res-{uuid.uuid4().hex[:8]}"
    
    def _generate_resource_name(self, context: GenerationContext) -> Optional[str]:
        """Generate resource name based on resource type."""
        service_cat = context.row_data.get("ServiceCategory", "Other")
        resource_id = context.row_data.get("ResourceId", "unknown")
        
        if service_cat == "Compute":
            return f"web-server-{resource_id[-4:]}"
        elif service_cat == "Storage":
            return f"data-volume-{resource_id[-4:]}"
        elif service_cat == "Databases":
            return f"prod-db-{resource_id[-4:]}"
        else:
            return f"resource-{resource_id[-4:]}"
    
    def _generate_resource_type(self, context: GenerationContext) -> Optional[str]:
        """Generate resource type based on service category."""
        service_cat = context.row_data.get("ServiceCategory", "Other")
        
        if service_cat == "Compute":
            return random.choice(["Instance", "Container", "Function", "GPU Instance"])
        elif service_cat == "Storage":
            return random.choice(["Block Storage", "Object Storage", "File Storage"])
        elif service_cat == "Databases":
            return random.choice(["Relational DB", "NoSQL DB", "Cache", "Data Warehouse"])
        elif service_cat == "Networking":
            return random.choice(["Load Balancer", "VPC", "Subnet", "NAT Gateway"])
        elif service_cat == "AI and Machine Learning":
            return random.choice(["ML Model", "Training Job", "Inference Endpoint"])
        else:
            return "Other"


class AccountGenerator(ColumnGenerator):
    """Handles account and billing-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["BillingAccountId", "BillingAccountName", "SubAccountId", "SubAccountName", "BillingCurrency"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "BillingAccountId":
            return f"{random.randint(100000000000, 999999999999)}"
        elif context.col_name == "BillingAccountName":
            companies = ["Acme Corp", "TechStart Inc", "Global Systems", "Data Dynamics", "Cloud Solutions"]
            return random.choice(companies)
        elif context.col_name == "SubAccountId":
            return f"{random.randint(100000000000, 999999999999)}"
        elif context.col_name == "SubAccountName":
            departments = ["Production", "Development", "Testing", "Staging", "Analytics"]
            return random.choice(departments)
        elif context.col_name == "BillingCurrency":
            return random.choice(["USD", "EUR", "GBP", "JPY", "CAD"])
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")


class CostDetailsGenerator(ColumnGenerator):
    """Handles detailed cost-related columns."""
    
    def supported_columns(self) -> List[str]:
        return ["EffectiveCost", "ListCost", "ContractedCost", "ListUnitPrice", "ContractedUnitPrice"]
    
    def generate_value(self, context: GenerationContext) -> Optional[float]:
        if context.col_name == "EffectiveCost":
            return self._generate_effective_cost(context)
        elif context.col_name == "ListCost":
            return self._generate_list_cost(context)
        elif context.col_name == "ContractedCost":
            return self._generate_contracted_cost(context)
        elif context.col_name == "ListUnitPrice":
            return self._generate_list_unit_price(context)
        elif context.col_name == "ContractedUnitPrice":
            return self._generate_contracted_unit_price(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_effective_cost(self, context: GenerationContext) -> Optional[float]:
        """Generate effective cost based on billed cost."""
        billed_cost = context.row_data.get("BilledCost", 0)
        if billed_cost and billed_cost > 0:
            # Effective cost is usually same as billed cost or slightly different due to discounts
            factor = random.uniform(0.85, 1.05)
            return round(billed_cost * factor, 2)
        return None
    
    def _generate_list_cost(self, context: GenerationContext) -> Optional[float]:
        """Generate list cost (usually higher than billed cost)."""
        billed_cost = context.row_data.get("BilledCost", 0)
        if billed_cost and billed_cost > 0:
            # List cost is typically higher than billed cost
            factor = random.uniform(1.1, 1.5)
            return round(billed_cost * factor, 2)
        return None
    
    def _generate_contracted_cost(self, context: GenerationContext) -> float:
        """Generate contracted cost."""
        effective_cost = context.row_data.get("EffectiveCost")
        billed_cost = context.row_data.get("BilledCost", 0)
        
        if effective_cost and effective_cost > 0:
            return effective_cost  # Often same as effective cost
        elif billed_cost and billed_cost > 0:
            # If no effective cost, use billed cost with slight variation
            factor = random.uniform(0.9, 1.1)
            return round(billed_cost * factor, 2)
        else:
            # Fallback to a small positive value (shouldn't happen with proper data)
            return round(random.uniform(0.01, 1.0), 2)
    
    def _generate_list_unit_price(self, context: GenerationContext) -> Optional[float]:
        """Generate list unit price."""
        pricing_quantity = context.row_data.get("PricingQuantity")
        list_cost = context.row_data.get("ListCost")
        
        if pricing_quantity and list_cost and pricing_quantity > 0:
            return round(list_cost / pricing_quantity, 4)
        elif not pricing_quantity:
            # If no quantity, generate a random unit price
            return round(random.uniform(0.01, 10.0), 4)
        return None
    
    def _generate_contracted_unit_price(self, context: GenerationContext) -> Optional[float]:
        """Generate contracted unit price."""
        list_unit_price = context.row_data.get("ListUnitPrice")
        if list_unit_price:
            # Contracted price is usually lower than list price
            factor = random.uniform(0.7, 0.95)
            return round(list_unit_price * factor, 4)
        return None


class LocationGenerator(ColumnGenerator):
    """Handles location-related columns (regions, availability zones)."""
    
    # Cloud provider regions and their availability zones
    REGIONS = {
        "AWS": {
            "us-east-1": {"name": "US East (N. Virginia)", "zones": ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f"]},
            "us-west-2": {"name": "US West (Oregon)", "zones": ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]},
            "eu-west-1": {"name": "Europe (Ireland)", "zones": ["eu-west-1a", "eu-west-1b", "eu-west-1c"]},
            "ap-southeast-1": {"name": "Asia Pacific (Singapore)", "zones": ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]},
            "ca-central-1": {"name": "Canada (Central)", "zones": ["ca-central-1a", "ca-central-1b", "ca-central-1d"]},
        },
        "AZURE": {
            "eastus": {"name": "East US", "zones": ["eastus-1", "eastus-2", "eastus-3"]},
            "westus": {"name": "West US", "zones": ["westus-1", "westus-2", "westus-3"]},
            "northeurope": {"name": "North Europe", "zones": ["northeurope-1", "northeurope-2", "northeurope-3"]},
            "southeastasia": {"name": "Southeast Asia", "zones": ["southeastasia-1", "southeastasia-2", "southeastasia-3"]},
        },
        "GCP": {
            "us-central1": {"name": "Iowa", "zones": ["us-central1-a", "us-central1-b", "us-central1-c", "us-central1-f"]},
            "us-east1": {"name": "South Carolina", "zones": ["us-east1-b", "us-east1-c", "us-east1-d"]},
            "europe-west1": {"name": "Belgium", "zones": ["europe-west1-b", "europe-west1-c", "europe-west1-d"]},
            "asia-southeast1": {"name": "Singapore", "zones": ["asia-southeast1-a", "asia-southeast1-b", "asia-southeast1-c"]},
        }
    }
    
    def supported_columns(self) -> List[str]:
        return ["AvailabilityZone", "RegionId", "RegionName"]
    
    def generate_value(self, context: GenerationContext) -> Optional[str]:
        if context.col_name == "RegionId":
            return self._generate_region_id(context)
        elif context.col_name == "RegionName":
            return self._generate_region_name(context)
        elif context.col_name == "AvailabilityZone":
            return self._generate_availability_zone(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_region_id(self, context: GenerationContext) -> Optional[str]:
        """Generate region ID based on cloud provider."""
        if random.random() < 0.1:  # 10% chance of null for conditional field
            return None
            
        provider = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_regions = self.REGIONS.get(provider, self.REGIONS["AWS"])
        regions = list(provider_regions.keys())
        return random.choice(regions)
    
    def _generate_region_name(self, context: GenerationContext) -> Optional[str]:
        """Generate region name based on region ID."""
        region_id = context.row_data.get("RegionId")
        if not region_id:
            return None if random.random() < 0.1 else "Unknown Region"
        
        provider = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_regions = self.REGIONS.get(provider, self.REGIONS["AWS"])
        region_info = provider_regions.get(region_id, {})
        return region_info.get("name", f"Region {region_id}")
    
    def _generate_availability_zone(self, context: GenerationContext) -> Optional[str]:
        """Generate availability zone based on region."""
        if random.random() < 0.2:  # 20% chance of null (recommended field)
            return None
            
        region_id = context.row_data.get("RegionId")
        if not region_id:
            return None
        
        provider = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_regions = self.REGIONS.get(provider, self.REGIONS["AWS"])
        region_info = provider_regions.get(region_id, {})
        zones = region_info.get("zones", [f"{region_id}a", f"{region_id}b"])
        return random.choice(zones)


class ServiceDetailsGenerator(ColumnGenerator):
    """Handles detailed service information."""
    
    # Service names mapped by provider and service category
    PROVIDER_SERVICE_NAMES = {
        "AWS": {
            "Compute": ["Amazon EC2", "AWS Lambda", "Amazon ECS", "AWS Batch", "Amazon Lightsail", "AWS Fargate"],
            "Storage": ["Amazon S3", "Amazon EBS", "Amazon EFS", "Amazon Glacier", "AWS Storage Gateway", "AWS Backup"],
            "Databases": ["Amazon RDS", "Amazon DynamoDB", "Amazon Redshift", "Amazon ElastiCache", "Amazon DocumentDB", "Amazon Neptune"],
            "Networking": ["Amazon VPC", "AWS Direct Connect", "Amazon CloudFront", "AWS Load Balancer", "Amazon Route 53", "AWS Global Accelerator"],
            "AI and Machine Learning": ["Amazon SageMaker", "Amazon Comprehend", "Amazon Rekognition", "AWS Bedrock", "Amazon Textract", "Amazon Forecast"],
            "Other": ["AWS IAM", "Amazon CloudWatch", "AWS Config", "AWS CloudTrail", "AWS Systems Manager", "AWS Organizations"]
        },
        "AZURE": {
            "Compute": ["Azure Virtual Machines", "Azure Functions", "Azure Container Instances", "Azure Batch", "Azure App Service", "Azure Kubernetes Service"],
            "Storage": ["Azure Blob Storage", "Azure Disk Storage", "Azure Files", "Azure Archive Storage", "Azure Data Lake Storage", "Azure Backup"],
            "Databases": ["Azure SQL Database", "Azure Cosmos DB", "Azure Synapse", "Azure Cache for Redis", "Azure Database for PostgreSQL", "Azure Database for MySQL"],
            "Networking": ["Azure Virtual Network", "Azure ExpressRoute", "Azure CDN", "Azure Load Balancer", "Azure Traffic Manager", "Azure Front Door"],
            "AI and Machine Learning": ["Azure Machine Learning", "Azure Cognitive Services", "Azure Computer Vision", "Azure OpenAI", "Azure Bot Service", "Azure Form Recognizer"],
            "Other": ["Azure Active Directory", "Azure Monitor", "Azure Policy", "Azure Key Vault", "Azure Resource Manager", "Azure Cost Management"]
        },
        "GCP": {
            "Compute": ["Google Compute Engine", "Google Cloud Functions", "Google Cloud Run", "Google Cloud Batch", "Google App Engine", "Google Kubernetes Engine"],
            "Storage": ["Google Cloud Storage", "Google Persistent Disk", "Google Filestore", "Google Cloud Archive", "Google Cloud Backup", "Google Transfer Service"],
            "Databases": ["Google Cloud SQL", "Google Firestore", "Google BigQuery", "Google Memorystore", "Google Cloud Spanner", "Google Bigtable"],
            "Networking": ["Google VPC", "Google Cloud Interconnect", "Google Cloud CDN", "Google Cloud Load Balancing", "Google Cloud DNS", "Google Cloud Armor"],
            "AI and Machine Learning": ["Google AI Platform", "Google Cloud AI", "Google Cloud Vision", "Google Vertex AI", "Google Cloud Natural Language", "Google Cloud Translation"],
            "Other": ["Google Cloud IAM", "Google Cloud Monitoring", "Google Cloud Asset Inventory", "Google Cloud Security Command Center", "Google Cloud Deployment Manager", "Google Cloud Billing"]
        }
    }
    
    
    def supported_columns(self) -> List[str]:
        return ["ServiceName", "ServiceSubcategory"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "ServiceName":
            return self._generate_service_name(context)
        elif context.col_name == "ServiceSubcategory":
            return self._generate_service_subcategory(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_service_name(self, context: GenerationContext) -> str:
        """Generate service name based on cloud provider and service category."""
        service_cat = context.row_data.get("ServiceCategory", "Other")
        provider = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        
        # Get services for the specific provider and category
        provider_services = self.PROVIDER_SERVICE_NAMES.get(provider, self.PROVIDER_SERVICE_NAMES["AWS"])
        services = provider_services.get(service_cat, provider_services["Other"])
        
        return random.choice(services)
    
    def _generate_service_subcategory(self, context: GenerationContext) -> str:
        """Generate service subcategory based on service category."""
        service_cat = context.row_data.get("ServiceCategory", "Other")
        
        # Map service categories to their common subcategories
        subcategory_mapping = {
            "Compute": ["Virtual Machines", "Serverless Compute", "Containers"],
            "Storage": ["Object Storage", "Block Storage", "File Storage", "Backup Storage"],
            "Databases": ["Relational Databases", "NoSQL Databases", "Data Warehouses", "Caching"],
            "Networking": ["Network Infrastructure", "Content Delivery", "Network Security", "Application Networking"],
            "AI and Machine Learning": ["Machine Learning", "Generative AI", "AI Platforms", "Natural Language Processing"],
            "Other": ["Other (Other)", "Identity and Access Management", "Observability"]
        }
        
        subcategories = subcategory_mapping.get(service_cat, ["Other (Other)"])
        return random.choice(subcategories)


class UsageMetricsGenerator(ColumnGenerator):
    """Handles usage metrics and consumption data."""
    
    def supported_columns(self) -> List[str]:
        return ["ConsumedQuantity", "ConsumedUnit", "SkuMeter"]
    
    def generate_value(self, context: GenerationContext) -> Optional[Any]:
        if context.col_name == "ConsumedQuantity":
            return self._generate_consumed_quantity(context)
        elif context.col_name == "ConsumedUnit":
            return self._generate_consumed_unit(context)
        elif context.col_name == "SkuMeter":
            return self._generate_sku_meter(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_consumed_quantity(self, context: GenerationContext) -> Optional[float]:
        """Generate consumed quantity based on service type."""
        # Conditional field - can be null
        if random.random() < 0.3:
            return None
        
        service_cat = context.row_data.get("ServiceCategory", "Other")
        charge_cat = context.row_data.get("ChargeCategory", "Usage")
        
        if charge_cat != "Usage":
            return None  # Only usage charges have consumed quantities
        
        # Generate realistic quantities based on service type
        if service_cat == "Compute":
            return round(random.uniform(1, 720), 2)  # Hours (1 month max)
        elif service_cat == "Storage":
            return round(random.uniform(1, 10000), 2)  # GB
        elif service_cat == "Databases":
            return round(random.uniform(1, 1000), 2)  # GB or hours
        elif service_cat == "Networking":
            return round(random.uniform(0.1, 1000), 2)  # GB transferred
        else:
            return round(random.uniform(1, 100), 2)  # Generic units
    
    def _generate_consumed_unit(self, context: GenerationContext) -> Optional[str]:
        """Generate consumed unit based on service and quantity."""
        consumed_qty = context.row_data.get("ConsumedQuantity")
        if consumed_qty is None:
            return None
        
        service_cat = context.row_data.get("ServiceCategory", "Other")
        
        # Map service categories to typical units
        unit_mapping = {
            "Compute": ["Hours", "vCPU-Hours", "Instance-Hours"],
            "Storage": ["GB", "GB-Month", "TB", "Requests"],
            "Databases": ["GB-Month", "Hours", "RCU", "WCU"],
            "Networking": ["GB", "Requests", "Hours"],
            "AI and Machine Learning": ["Requests", "Training-Hours", "Inference-Hours"],
            "Other": ["Hours", "Requests", "Units"]
        }
        
        units = unit_mapping.get(service_cat, ["Units"])
        return random.choice(units)
    
    def _generate_sku_meter(self, context: GenerationContext) -> Optional[str]:
        """Generate SKU meter description."""
        # Conditional field
        if random.random() < 0.4:
            return None
        
        service_cat = context.row_data.get("ServiceCategory", "Other")
        consumed_unit = context.row_data.get("ConsumedUnit", "") or ""
        
        # Generate meter descriptions based on service and unit
        if service_cat == "Compute" and "Hours" in consumed_unit:
            return "Instance runtime"
        elif service_cat == "Storage" and "GB" in consumed_unit:
            return "Storage capacity"
        elif service_cat == "Databases":
            return "Database runtime"
        elif service_cat == "Networking":
            return "Data transfer"
        elif service_cat == "AI and Machine Learning":
            return "ML processing"
        else:
            return "Service usage"


class ProviderBusinessGenerator(ColumnGenerator):
    """Handles provider, publisher, and business entity information."""
    
    # Cloud providers and their common publishers
    PROVIDERS = {
        "AWS": {
            "name": "AWS",
            "publishers": ["Amazon Web Services", "AWS Marketplace", "Third Party"],
            "invoice_issuers": ["Amazon Web Services, Inc.", "AWS EMEA SARL", "AWS Asia Pacific"]
        },
        "AZURE": {
            "name": "Microsoft Azure",
            "publishers": ["Microsoft", "Azure Marketplace", "Third Party"],
            "invoice_issuers": ["Microsoft Corporation", "Microsoft Ireland", "Microsoft Singapore"]
        },
        "GCP": {
            "name": "Google Cloud",
            "publishers": ["Google", "Google Cloud Marketplace", "Third Party"],
            "invoice_issuers": ["Google LLC", "Google Cloud EMEA", "Google Asia Pacific"]
        }
    }
    
    def supported_columns(self) -> List[str]:
        return ["ProviderName", "PublisherName", "InvoiceIssuerName"]
    
    def generate_value(self, context: GenerationContext) -> str:
        if context.col_name == "ProviderName":
            return self._generate_provider_name(context)
        elif context.col_name == "PublisherName":
            return self._generate_publisher_name(context)
        elif context.col_name == "InvoiceIssuerName":
            return self._generate_invoice_issuer_name(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_provider_name(self, context: GenerationContext) -> str:
        """Generate provider name based on cloud_provider parameter."""
        provider_key = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_info = self.PROVIDERS.get(provider_key, self.PROVIDERS["AWS"])
        return provider_info["name"]
    
    def _generate_publisher_name(self, context: GenerationContext) -> str:
        """Generate publisher name based on cloud_provider parameter."""
        provider_key = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_info = self.PROVIDERS.get(provider_key, self.PROVIDERS["AWS"])
        return random.choice(provider_info["publishers"])
    
    def _generate_invoice_issuer_name(self, context: GenerationContext) -> str:
        """Generate invoice issuer name based on cloud_provider parameter."""
        provider_key = CLOUD_PROVIDER_MAPPING.get(context.cloud_provider.upper() if context.cloud_provider else "AWS", "AWS")
        provider_info = self.PROVIDERS.get(provider_key, self.PROVIDERS["AWS"])
        return random.choice(provider_info["invoice_issuers"])


class MetadataGenerator(ColumnGenerator):
    """Handles metadata fields like tags, descriptions, and JSON data."""
    
    # Common tag categories for cloud resources
    TAG_CATEGORIES = {
        "Environment": ["Production", "Development", "Staging", "Testing"],
        "Project": ["WebApp", "DataPipeline", "Analytics", "ML-Training", "Backup"],
        "Owner": ["Engineering", "DataScience", "DevOps", "Finance", "Marketing"],
        "CostCenter": ["CC-1001", "CC-2002", "CC-3003", "CC-4004"],
        "Application": ["WebServer", "Database", "LoadBalancer", "Cache", "Storage"]
    }
    
    def supported_columns(self) -> List[str]:
        return ["Tags", "SkuPriceDetails", "ChargeDescription", "CommitmentDiscountName"]
    
    def generate_value(self, context: GenerationContext) -> Optional[Any]:
        if context.col_name == "Tags":
            return self._generate_tags(context)
        elif context.col_name == "SkuPriceDetails":
            return self._generate_sku_price_details(context)
        elif context.col_name == "ChargeDescription":
            return self._generate_charge_description(context)
        elif context.col_name == "CommitmentDiscountName":
            return self._generate_commitment_discount_name(context)
        else:
            raise ValueError(f"Unsupported column: {context.col_name}")
    
    def _generate_tags(self, context: GenerationContext) -> Optional[dict]:
        """Generate realistic resource tags."""
        # Conditional field - 40% chance of null
        if random.random() < 0.4:
            return None
        
        tags = {}
        
        # Randomly select 2-4 tag categories
        num_tags = random.randint(2, 4)
        selected_categories = random.sample(list(self.TAG_CATEGORIES.keys()), num_tags)
        
        for category in selected_categories:
            value = random.choice(self.TAG_CATEGORIES[category])
            tags[category] = value
        
        # Add some custom tags occasionally
        if random.random() < 0.3:
            custom_tags = {
                "CreatedBy": "AutomatedDeployment",
                "BillingCode": f"BC-{random.randint(1000, 9999)}",
                "Temporary": str(random.choice([True, False])).lower()
            }
            # Add 1-2 custom tags
            num_custom = random.randint(1, min(2, len(custom_tags)))
            selected_custom = random.sample(list(custom_tags.items()), num_custom)
            tags.update(selected_custom)
        
        return tags
    
    def _generate_sku_price_details(self, context: GenerationContext) -> Optional[dict]:
        """Generate SKU price details metadata."""
        # Conditional field - 50% chance of null
        if random.random() < 0.5:
            return None
        
        sku_id = context.row_data.get("SkuId")
        service_cat = context.row_data.get("ServiceCategory", "Other")
        
        details = {
            "sku_family": self._get_sku_family(service_cat),
            "pricing_model": random.choice(["OnDemand", "Reserved", "Spot", "Committed"]),
            "term_length": random.choice(["None", "1yr", "3yr"]),
            "payment_option": random.choice(["NoUpfront", "PartialUpfront", "AllUpfront"])
        }
        
        # Add service-specific details
        if service_cat == "Compute":
            details.update({
                "instance_type": random.choice(["t3.micro", "m5.large", "c5.xlarge", "r5.2xlarge"]),
                "operating_system": random.choice(["Linux", "Windows", "RHEL"])
            })
        elif service_cat == "Storage":
            details.update({
                "storage_class": random.choice(["Standard", "IA", "Archive", "Glacier"]),
                "redundancy": random.choice(["LRS", "ZRS", "GRS"])
            })
        
        return details
    
    def _get_sku_family(self, service_category: str) -> str:
        """Get SKU family based on service category."""
        family_mapping = {
            "Compute": "Compute Instance",
            "Storage": "Storage",
            "Databases": "Database",
            "Networking": "Network",
            "AI and Machine Learning": "ML Service",
            "Other": "General"
        }
        return family_mapping.get(service_category, "General")
    
    def _generate_charge_description(self, context: GenerationContext) -> Optional[str]:
        """Generate human-readable charge description."""
        # Mandatory field but allows nulls - 10% chance of null
        if random.random() < 0.1:
            return None
        
        service_name = context.row_data.get("ServiceName", "Cloud Service")
        charge_cat = context.row_data.get("ChargeCategory", "Usage")
        region_name = context.row_data.get("RegionName", "")
        consumed_unit = context.row_data.get("ConsumedUnit", "")
        
        # Generate description based on charge category
        if charge_cat == "Usage":
            if consumed_unit:
                desc = f"{service_name} usage in {region_name or 'unspecified region'} - {consumed_unit}"
            else:
                desc = f"{service_name} usage in {region_name or 'unspecified region'}"
        elif charge_cat == "Purchase":
            desc = f"{service_name} reserved capacity purchase"
        elif charge_cat == "Tax":
            desc = f"Tax on {service_name} charges"
        elif charge_cat == "Credit":
            desc = f"Credit applied to {service_name} usage"
        elif charge_cat == "Adjustment":
            desc = f"Billing adjustment for {service_name}"
        else:
            desc = f"{service_name} charge"
        
        return desc
    
    def _generate_commitment_discount_name(self, context: GenerationContext) -> Optional[str]:
        """Generate commitment discount name."""
        commitment_id = context.row_data.get("CommitmentDiscountId")
        if not commitment_id:
            return None
        
        commitment_type = context.row_data.get("CommitmentDiscountType", "Reserved")
        
        # Generate realistic commitment names
        if commitment_type == "Reserved":
            return f"Reserved Instance Plan {random.randint(1000, 9999)}"
        elif commitment_type == "SavingsPlan":
            return f"Savings Plan {random.randint(100, 999)}"
        elif commitment_type == "Custom":
            return f"Enterprise Agreement {random.randint(10, 99)}"
        else:
            return f"Commitment Plan {random.randint(100, 999)}"


class GenericGenerator(ColumnGenerator):
    """Fallback generator for columns without specific logic."""
    
    def supported_columns(self) -> List[str]:
        return []  # Handles any column not handled by others
    
    def can_handle(self, col_name: str) -> bool:
        return True  # Always returns True as fallback
    
    def generate_value(self, context: GenerationContext) -> Any:
        """Generate generic value based on metadata."""
        return self._generate_generic_value(context)
    
    def _generate_generic_value(self, context: GenerationContext) -> Any:
        """Generic fallback approach for columns without special logic."""
        meta = context.metadata
        data_type = meta.get("data_type")
        allows_null = meta.get("allows_nulls", True)
        allowed_values = meta.get("allowed_values", None)
        
        # 10% chance of null if allowed
        if allows_null and random.random() < 0.1:
            return None
        
        # If we have a set of allowed_values for a dimension
        if allowed_values and data_type == "string":
            return random.choice(allowed_values)
        
        if data_type in ("decimal", "numeric"):
            # Return a random float in some range
            return round(random.uniform(1.0, 500.0), 2)
        
        if data_type == "datetime":
            # Simplistic datetime
            return "2024-01-01T00:00:00Z"
        
        if data_type == "json":
            # Example
            return {"exampleKey": "exampleValue"}
        
        # string fallback
        if data_type == "string":
            return f"{context.col_name}_{context.row_idx}_{uuid.uuid4().hex[:4]}"
        
        # If nothing else matched
        return None