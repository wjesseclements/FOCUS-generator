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
def generate_column_data(column_name, row_count, profile=None, charge_categories=None):
    metadata = FOCUS_METADATA.get(column_name)
    if not metadata:
        raise ValueError(f"Metadata for column '{column_name}' not found.")

    # Generate data based on column name
    if column_name == "AvailabilityZone":
        zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
        if charge_categories:
            return [
                random.choice(zones) if charge_category in ["Usage", "Purchase"] else None
                for charge_category in charge_categories
            ]
        return [random.choice(zones) if random.random() > 0.1 else None for _ in range(row_count)]
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
        return ["USD"] * row_count
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
    elif column_name == "CapacityReservationId":
        return [
            f"cr-{uuid.uuid4().hex[:8]}" if random.random() > 0.5 else None
            for _ in range(row_count)
        ]
    elif column_name == "CapacityReservationStatus":
        return [
            random.choice(["Used", "Unused"]) if random.random() > 0.5 else None
            for _ in range(row_count)
        ]
    elif column_name == "ChargeCategory":
        return random.choices(
            ["Usage", "Purchase", "Tax", "Credit", "Adjustment"], k=row_count
        )
    return [None] * row_count

# Generate synthetic data for the FOCUS dataset
def generate_focus_data(row_count=20, distribution="Evenly Distributed", profile="Greenfield"):
    current_time = datetime.now(timezone.utc)

    # Generate charge categories first to use them in AvailabilityZone logic
    charge_categories = generate_column_data("ChargeCategory", row_count)

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
        "AvailabilityZone": generate_column_data(
            "AvailabilityZone", row_count, charge_categories=charge_categories
        ),
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
        "ChargeCategory": charge_categories,
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