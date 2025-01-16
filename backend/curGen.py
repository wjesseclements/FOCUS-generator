import pandas as pd
import uuid
import random
from datetime import datetime, timezone, timedelta
from focus_metadata import FOCUS_METADATA

# Generate realistic AWS account numbers
def generate_aws_account():
    prefix = "999"  # Reserved prefix to avoid collisions with real AWS accounts
    random_digits = random.randint(100000000, 999999999)
    return f"{prefix}{random_digits}"

# Helper function to generate data for a specific column
def generate_column_data(column_name, row_count, profile=None, pricing_quantity=None):
    metadata = FOCUS_METADATA.get(column_name)
    if not metadata:
        raise ValueError(f"Metadata for column '{column_name}' not found.")

    # Generate data based on column name
    if column_name == "ContractedCost":
        return [
            round((contracted_unit_price * (quantity or 0)), 2) if contracted_unit_price else billed_cost
            for contracted_unit_price, quantity, billed_cost in zip(
                generate_column_data("ContractedUnitPrice", row_count),
                pricing_quantity or [1] * row_count,
                generate_column_data("BilledCost", row_count, profile)
            )
        ]
    elif column_name == "ContractedUnitPrice":
        return [
            round(random.uniform(0.01, 10.0), 2) if random.random() > 0.2 else None
            for _ in range(row_count)
        ]
    elif column_name == "EffectiveCost":
        return [
            round(billed_cost * random.uniform(0.8, 1.0), 2) if billed_cost is not None else None
            for billed_cost in generate_column_data("BilledCost", row_count, profile)
        ]
    elif column_name == "InvoiceIssuerName":
        return ["AWS Inc."] * row_count
    elif column_name == "ListCost":
        return [
            round((list_unit_price * (quantity or 0)), 2) if list_unit_price else billed_cost
            for list_unit_price, quantity, billed_cost in zip(
                generate_column_data("ListUnitPrice", row_count),
                pricing_quantity or [1] * row_count,
                generate_column_data("BilledCost", row_count, profile)
            )
        ]
    elif column_name == "ListUnitPrice":
        return [
            round(random.uniform(0.01, 15.0), 2) if random.random() > 0.2 else None
            for _ in range(row_count)
        ]
    elif column_name == "BilledCost":
        if profile == "Greenfield":
            total_cost = random.uniform(20000, 50000)
        elif profile == "Large Business":
            total_cost = random.uniform(100000, 250000)
        elif profile == "Enterprise":
            total_cost = random.uniform(1000000, 2000000)
        else:
            total_cost = 100000  # Default for testing
        return [round(total_cost / row_count, 2) for _ in range(row_count)]
    elif column_name == "BillingCurrency":
        return ["USD"] * row_count  # Default to "USD" for now.
    elif column_name == "BillingPeriodStart":
        return [
            (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for _ in range(row_count)
        ]
    elif column_name == "BillingPeriodEnd":
        return [
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            for _ in range(row_count)
        ]
    elif column_name == "ChargeCategory":
        return random.choices(
            ["Usage", "Purchase", "Tax", "Credit", "Adjustment"], k=row_count
        )
    elif column_name == "ChargeClass":
        return [
            "Correction" if random.random() > 0.5 else None
            for _ in range(row_count)
        ]
    elif column_name == "ChargeDescription":
        return [
            f"Charge description {i}" if random.random() > 0.1 else None
            for i in range(row_count)
        ]
    elif column_name == "ChargeFrequency":
        return [
            random.choice(["One-Time", "Recurring", "Usage-Based"])
            if charge_category != "Purchase" else random.choice(["One-Time", "Recurring"])
            for charge_category in generate_column_data("ChargeCategory", row_count)
        ]
    elif column_name == "ChargePeriodEnd":
        return [
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            for _ in range(row_count)
        ]
    elif column_name == "ChargePeriodStart":
        return [
            (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for _ in range(row_count)
        ]
    return [None] * row_count

# Generate synthetic data for the FOCUS dataset
def generate_focus_data(row_count=20, distribution="Evenly Distributed", profile="Greenfield"):
    current_time = datetime.now(timezone.utc)

    # Generate pricing quantity for applicable calculations
    pricing_quantity = [random.uniform(1, 100) for _ in range(row_count)]

    data = {
        "InvoiceId": [str(uuid.uuid4()) for _ in range(row_count)],
        "LinkedAccountId": [generate_aws_account() for _ in range(row_count)],
        "UsageAccountId": [generate_aws_account() for _ in range(row_count)],
        "UsageStartDate": [
            (current_time - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(row_count)
        ],
        "UsageEndDate": [
            (current_time - timedelta(hours=i - 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(row_count)
        ],
        "AvailabilityZone": generate_column_data("AvailabilityZone", row_count),
        "BilledCost": generate_column_data("BilledCost", row_count, profile=profile),
        "BillingAccountId": [str(uuid.uuid4()) for _ in range(row_count)],
        "BillingAccountName": [
            f"Account-{i}" if random.random() > 0.2 else None for i in range(row_count)
        ],
        "BillingCurrency": generate_column_data("BillingCurrency", row_count),
        "BillingPeriodStart": generate_column_data("BillingPeriodStart", row_count),
        "BillingPeriodEnd": generate_column_data("BillingPeriodEnd", row_count),
        "CapacityReservationId": generate_column_data("CapacityReservationId", row_count),
        "CapacityReservationStatus": generate_column_data("CapacityReservationStatus", row_count),
        "ChargeCategory": generate_column_data("ChargeCategory", row_count),
        "ChargeClass": generate_column_data("ChargeClass", row_count),
        "ChargeDescription": generate_column_data("ChargeDescription", row_count),
        "ChargeFrequency": generate_column_data("ChargeFrequency", row_count),
        "ChargePeriodEnd": generate_column_data("ChargePeriodEnd", row_count),
        "ChargePeriodStart": generate_column_data("ChargePeriodStart", row_count),
        "CommitmentDiscountCategory": generate_column_data("CommitmentDiscountCategory", row_count),
        "CommitmentDiscountId": generate_column_data("CommitmentDiscountId", row_count),
        "CommitmentDiscountName": generate_column_data("CommitmentDiscountName", row_count),
        "CommitmentDiscountQuantity": generate_column_data("CommitmentDiscountQuantity", row_count),
        "CommitmentDiscountStatus": generate_column_data("CommitmentDiscountStatus", row_count),
        "CommitmentDiscountType": generate_column_data("CommitmentDiscountType", row_count),
        "CommitmentDiscountUnit": generate_column_data("CommitmentDiscountUnit", row_count),
        "ConsumedQuantity": pricing_quantity,
        "ConsumedUnit": random.choices(["Hours", "Requests", "GB", "Transactions"], k=row_count),
        "ContractedCost": generate_column_data("ContractedCost", row_count, pricing_quantity=pricing_quantity),
        "ContractedUnitPrice": generate_column_data("ContractedUnitPrice", row_count),
        "EffectiveCost": generate_column_data("EffectiveCost", row_count),
        "InvoiceIssuerName": generate_column_data("InvoiceIssuerName", row_count),
        "ListCost": generate_column_data("ListCost", row_count, pricing_quantity=pricing_quantity),
        "ListUnitPrice": generate_column_data("ListUnitPrice", row_count),
    }

    return pd.DataFrame(data, columns=FOCUS_METADATA.keys())

# Generate and save synthetic CUR for standalone testing
if __name__ == "__main__":
    profiles = ["Greenfield", "Large Business", "Enterprise"]
    distribution = "Evenly Distributed"  # Use a fixed distribution for now
    row_count = 20

    for profile in profiles:
        synthetic_cur = generate_focus_data(row_count, distribution=distribution, profile=profile)
        output_file = f"synthetic_focus_cur_{profile.lower()}_v1_1.csv"
        synthetic_cur.to_csv(output_file, index=False)
        print(f"Synthetic CUR for profile '{profile}' saved as '{output_file}'.")