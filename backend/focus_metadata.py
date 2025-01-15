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