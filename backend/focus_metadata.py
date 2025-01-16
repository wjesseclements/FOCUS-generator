# Metadata dictionary for the FOCUS v1.1 specification columns.
# Each entry includes column-specific constraints and details to guide data generation.

FOCUS_METADATA = {
    "AvailabilityZone": {
        "description": "A provider-assigned identifier for a physically separated and isolated area "
                       "within a Region that provides high availability and fault tolerance.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": None,
        "generation_logic": "Random selection from a predefined list of availability zones or None.",
    },
    "BilledCost": {
        "description": "Represents a charge serving as the basis for invoicing, inclusive of reduced rates "
                       "and discounts, but excluding amortized purchases.",
        "type": "metric",
        "required": True,
        "data_type": "decimal",
        "allows_nulls": False,
        "value_format": "numeric",
        "range": "any valid decimal",
        "generation_logic": "Random decimal values generated within realistic cost ranges.",
    },
    "BillingAccountId": {
        "description": "The identifier assigned to a billing account by the provider.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": False,
        "value_format": "Globally unique string.",
        "generation_logic": "Globally unique identifier, such as a UUID or AWS-style account ID.",
    },
    "BillingAccountName": {
        "description": "The display name assigned to a billing account.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": None,
        "generation_logic": "Random name string, allowing occasional nulls.",
    },
    "BillingCurrency": {
        "description": "Represents the currency that a charge was billed in.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": False,
        "value_format": "Currency Code Format",
        "generation_logic": "Static value set to 'USD'.",
    },
    "BillingPeriodStart": {
        "description": "The inclusive start date and time of a billing period.",
        "type": "dimension",
        "required": True,
        "data_type": "datetime",
        "allows_nulls": False,
        "value_format": "Date/Time Format",
        "generation_logic": "Derived start date for the billing period, typically 30 days before BillingPeriodEnd.",
    },
    "BillingPeriodEnd": {
        "description": "The exclusive end date and time of a billing period.",
        "type": "dimension",
        "required": True,
        "data_type": "datetime",
        "allows_nulls": False,
        "value_format": "Date/Time Format",
        "generation_logic": "Static or derived end date for the billing period.",
    },
    "CapacityReservationId": {
        "description": "The identifier assigned to a capacity reservation by the provider.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Globally unique string.",
        "generation_logic": "Globally unique identifier, with occasional nulls.",
    },
    "CapacityReservationStatus": {
        "description": "Indicates whether the charge represents either the consumption of a capacity reservation or unused capacity.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Allowed values",
        "allowed_values": ["Used", "Unused"],
        "generation_logic": "Random selection from allowed values, conditional on CapacityReservationId.",
    },
    "ChargeCategory": {
        "description": "Represents the highest-level classification of a charge based on the nature of how it is billed.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": False,
        "value_format": "Allowed values",
        "allowed_values": ["Usage", "Purchase", "Tax", "Credit", "Adjustment"],
        "generation_logic": "Random selection from allowed values.",
    },
    "ChargeClass": {
        "description": "Indicates whether the row represents a correction to a previously invoiced billing period.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Allowed values: Correction or None",
        "generation_logic": "50% chance of 'Correction' if it's a correction, otherwise None.",
    },
    "ChargeDescription": {
        "description": "Self-contained summary of the charge’s purpose and price.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "<not specified>",
        "generation_logic": "Random descriptive string, occasionally allowing nulls.",
    },
    "ChargeFrequency": {
        "description": "Indicates how often a charge will occur.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": False,
        "value_format": "Allowed values: One-Time, Recurring, Usage-Based",
        "generation_logic": "Random choice from the allowed values, avoiding 'Usage-Based' for Purchase charges.",
    },
    "ChargePeriodEnd": {
        "description": "The exclusive end date and time of a charge period.",
        "type": "dimension",
        "required": True,
        "data_type": "datetime",
        "allows_nulls": False,
        "value_format": "Date/Time Format",
        "generation_logic": "Exclusive end date calculated based on the charge period duration.",
    },
    "ChargePeriodStart": {
    "description": "The inclusive start date and time within a charge period.",
    "type": "dimension",
    "required": True,
    "data_type": "datetime",
    "allows_nulls": False,
    "value_format": "Date/Time Format",
    "generation_logic": "Derived from ChargePeriodEnd minus a predefined interval.",
    },
    "CommitmentDiscountCategory": {
        "description": "Indicates whether the commitment discount is based on usage quantity or spend.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Allowed values: Spend, Usage",
        "allowed_values": ["Spend", "Usage"],
        "generation_logic": "Random choice if CommitmentDiscountId is not null, otherwise null.",
    },
    "CommitmentDiscountId": {
        "description": "The identifier assigned to a commitment discount by the provider.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "<not specified>",
        "generation_logic": "UUID if related to a commitment discount, otherwise null.",
    },
    "CommitmentDiscountName": {
        "description": "The display name assigned to a commitment discount.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "<not specified>",
        "generation_logic": "Descriptive string if CommitmentDiscountId is not null, otherwise null.",
    },
    "CommitmentDiscountQuantity": {
        "description": "The amount of a commitment discount purchased or accounted for.",
        "type": "metric",
        "required": False,
        "data_type": "decimal",
        "allows_nulls": True,
        "value_format": "Numeric Format",
        "generation_logic": "Random decimal if CommitmentDiscountId is not null and conditions are met, otherwise null.",
    },
    "CommitmentDiscountStatus": {
        "description": "Indicates whether the charge corresponds with the consumption or unused portion of a commitment discount.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Allowed values: Used, Unused",
        "allowed_values": ["Used", "Unused"],
        "generation_logic": "Random choice if CommitmentDiscountId is not null and ChargeCategory is 'Usage', otherwise null.",
    },
    "CommitmentDiscountType": {
        "description": "A provider-assigned identifier for the type of commitment discount applied to the row.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": None,
        "generation_logic": "Randomly assign a type if CommitmentDiscountId is not null, otherwise set to null.",
    },
    "CommitmentDiscountUnit": {
        "description": "The provider-specified measurement unit indicating how a provider measures the Commitment Discount Quantity.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Unit Format",
        "generation_logic": "Random unit string if CommitmentDiscountId is not null and ChargeClass is not 'Correction', otherwise null.",
    },
    "ConsumedQuantity": {
        "description": "The volume of a metered SKU associated with a resource or service used, based on the Consumed Unit.",
        "type": "metric",
        "required": False,
        "data_type": "decimal",
        "allows_nulls": True,
        "value_format": "Numeric Format",
        "generation_logic": "Positive decimal value for 'Usage' charges if CommitmentDiscountStatus is not 'Unused' and ChargeClass is not 'Correction'.",
    },
    "ConsumedUnit": {
        "description": "Provider-specified measurement unit indicating how a provider measures usage of a metered SKU.",
        "type": "dimension",
        "required": False,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Unit Format",
        "generation_logic": "Random unit string if ChargeCategory is 'Usage' and CommitmentDiscountStatus is not 'Unused', otherwise null.",
    },
    "ContractedCost": {
        "description": "Cost calculated by multiplying contracted unit price and the corresponding Pricing Quantity.",
        "type": "metric",
        "required": True,
        "data_type": "decimal",
        "allows_nulls": False,
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "generation_logic": (
            "Calculated as ContractedUnitPrice × PricingQuantity if ContractedUnitPrice is not null. "
            "Defaults to BilledCost when unrelated to other charges or null in special cases."
        ),
    },
    "ContractedUnitPrice": {
        "description": "The agreed-upon unit price for a single Pricing Unit of the associated SKU.",
        "type": "metric",
        "required": False,
        "data_type": "decimal",
        "allows_nulls": True,
        "value_format": "Numeric Format",
        "range": "Any valid non-negative decimal value",
        "generation_logic": (
            "Random positive decimal for applicable ChargeCategory and ChargeClass combinations. "
            "Null for ChargeCategory 'Tax' or in special cases."
        ),
    },
    "EffectiveCost": {
        "description": "The amortized cost of the charge after applying all reduced rates, discounts, "
                       "and the applicable portion of relevant prepaid purchases.",
        "type": "metric",
        "required": True,
        "data_type": "decimal",
        "allows_nulls": False,
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "generation_logic": (
            "Calculated based on BilledCost, discounts, and prepayments. "
            "Defaults to 0 for purchases covering future charges, matches BilledCost for credits, "
            "and may depend on CommitmentDiscountStatus for commitment-related charges."
        ),
    },
    "InvoiceIssuerName": {
        "description": "The name of the entity responsible for invoicing for the resources or services consumed.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": False,
        "value_format": None,
        "generation_logic": "Static value like 'AWS Inc.' or randomly chosen from predefined issuer names.",
    },
    "ListCost": {
        "description": "Cost calculated by multiplying List Unit Price and the corresponding Pricing Quantity.",
        "type": "metric",
        "required": True,
        "data_type": "decimal",
        "allows_nulls": False,
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "generation_logic": (
            "Calculated as ListUnitPrice × PricingQuantity if ListUnitPrice is not null. "
            "Defaults to BilledCost in other cases."
        ),
    },
    "ListUnitPrice": {
        "description": "The suggested provider-published unit price for a single Pricing Unit of the associated SKU.",
        "type": "metric",
        "required": False,
        "data_type": "decimal",
        "allows_nulls": True,
        "value_format": "Numeric Format",
        "range": "Any valid non-negative decimal value",
        "generation_logic": (
            "Random positive decimal for applicable ChargeCategory and ChargeClass combinations. "
            "Null for ChargeCategory 'Tax' or in special cases."
        ),
    },
    "PricingCategory": {
        "description": "Describes the pricing model used for a charge at the time of use or purchase.",
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Allowed values: Standard, Dynamic, Committed, Other",
        "allowed_values": ["Standard", "Dynamic", "Committed", "Other"],
        "generation_logic": (
            "Random selection from allowed values when ChargeClass is not 'Correction' "
            "and ChargeCategory is 'Usage' or 'Purchase'. Otherwise, null."
        ),
    },
    "PricingQuantity": {
        "description": "The volume of a given SKU associated with a resource or service used or purchased, based on the Pricing Unit.",
        "type": "metric",
        "required": True,
        "data_type": "decimal",
        "allows_nulls": True,
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "generation_logic": (
            "Random decimal value when ChargeClass is not 'Correction' and ChargeCategory is 'Usage' or 'Purchase'. "
            "Otherwise, null."
        ),
    },
    "PricingUnit": {
        "description": (
            "Provider-specified measurement unit for determining unit prices, indicating how the provider rates "
            "measured usage and purchase quantities after applying pricing rules like block pricing."
        ),
        "type": "dimension",
        "required": True,
        "data_type": "string",
        "allows_nulls": True,
        "value_format": "Unit Format",
        "generation_logic": (
            "Random selection from ['Hours', 'GB-Hours', 'Requests', 'Transactions'] "
            "when ChargeClass is not 'Correction' and ChargeCategory is 'Usage' or 'Purchase'. "
            "Otherwise, null."
        ),
    },












}
# Provide helper functions to retrieve metadata for validation or generation purposes.

def get_column_metadata(column_name):
    """
    Retrieve metadata for a specific column.
    
    :param column_name: The name of the column.
    :return: Metadata dictionary for the column or None if not found.
    """
    return FOCUS_METADATA.get(column_name)


# Example usage for testing purposes:
if __name__ == "__main__":
    for column in FOCUS_METADATA:
        print(f"Column: {column}")
        print(f"Metadata: {FOCUS_METADATA[column]}")
        print("-" * 40)