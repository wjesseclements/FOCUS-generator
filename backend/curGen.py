import pandas as pd
import uuid
import random
from datetime import datetime, timezone, timedelta

# Define constants for the FOCUS v1.1 specification
FOCUS_COLUMNS = [
    "InvoiceId",
    "LinkedAccountId",
    "UsageAccountId",
    "ProductName",
    "UsageType",
    "Operation",
    "AvailabilityZone",
    "Region",
    "UsageStartDate",
    "UsageEndDate",
    "ResourceId",
    "UsageAmount",
    "BlendedCost",
    "UnblendedCost",
    "PublicOnDemandCost",
    "SavingsPlanEffectiveCost",
    "ReservationEffectiveCost",
    "DiscountedCost",
    "Tags",
    "CostCategory1",
    "CostCategory2",
    "ResourceTags",
    "ReservationARN",
    "SavingsPlanARN",
    "Tenancy",
    "PurchaseOption",
    "AmortizedCost",
    "NetAmortizedCost",
    "NetUnblendedCost",
    "Credits",
    "NetCredits",
    "Tax",
    "NetTax",
    "OtherDiscounts",
    "NetOtherDiscounts",
    "Rebates",
    "NetRebates",
    "Support",
    "NetSupport",
    "DiscountedBlendedCost",
    "DiscountedUnblendedCost",
    "NormalizedUsageAmount",
    "CurrencyCode",
    "ExchangeRate",
    "BillType",
    "PricingPlanId",
    "ServiceCode",
    "UsageTypeGroup",
    "ChargeType",
    "RateId",
    "BillingEntity",
]

# Generate realistic AWS account numbers
def generate_aws_account():
    prefix = "999"  # Reserved prefix to avoid collisions with real AWS accounts
    random_digits = random.randint(100000000, 999999999)
    return f"{prefix}{random_digits}"

# Generate synthetic data for each column
def generate_focus_data(row_count=20, distribution="Evenly Distributed", profile="Greenfield"):
    current_time = datetime.now(timezone.utc)

    # Base data
    data = {
        "InvoiceId": [str(uuid.uuid4()) for _ in range(row_count)],
        "LinkedAccountId": [generate_aws_account() for _ in range(row_count)],
        "UsageAccountId": [generate_aws_account() for _ in range(row_count)],
        "ProductName": ["Amazon EC2"] * row_count,
        "UsageType": ["BoxUsage:m5.large"] * row_count,
        "Operation": ["RunInstances"] * row_count,
        "AvailabilityZone": random.choices(["us-east-1a", "us-east-1b", "us-east-1c"], k=row_count),
        "Region": ["us-east-1"] * row_count,
        "UsageStartDate": [
            (current_time - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(row_count)
        ],
        "UsageEndDate": [
            (current_time - timedelta(hours=i - 1)).strftime("%Y-%m-%dT%H:%M:%SZ") for i in range(row_count)
        ],
        "ResourceId": [f"i-{uuid.uuid4().hex[:8]}" for _ in range(row_count)],
        "UsageAmount": [round(random.uniform(0.5, 10.0), 2) for _ in range(row_count)],
        "BlendedCost": [round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)],
        "UnblendedCost": [round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)],
        "CurrencyCode": ["USD"] * row_count,
        "ExchangeRate": [1.0] * row_count,
    }

    # Adjust data based on profile
    if profile == "Large Business":
        data["UsageAmount"] = [round(random.uniform(10, 50), 2) for _ in range(row_count)]
        data["BlendedCost"] = [round(random.uniform(5, 25), 5) for _ in range(row_count)]
    elif profile == "Enterprise":
        data["UsageAmount"] = [round(random.uniform(50, 200), 2) for _ in range(row_count)]
        data["BlendedCost"] = [round(random.uniform(25, 100), 5) for _ in range(row_count)]

    # Adjust data based on distribution
    if distribution == "ML-Focused":
        data["ProductName"] = ["SageMaker" if i % 2 == 0 else "Amazon EC2" for i in range(row_count)]
    elif distribution == "Data-Intensive":
        data["ProductName"] = ["Amazon S3" if i % 3 == 0 else "Amazon Redshift" for i in range(row_count)]
    elif distribution == "Media-Intensive":
        data["ProductName"] = ["CloudFront" if i % 4 == 0 else "MediaPackage" for i in range(row_count)]

    return pd.DataFrame(data, columns=FOCUS_COLUMNS)

# Generate the synthetic CUR and save it as a CSV file (for testing standalone usage)
if __name__ == "__main__":
    row_count = 20  # Adjust row count as needed
    synthetic_cur = generate_focus_data(row_count, distribution="ML-Focused", profile="Enterprise")
    synthetic_cur.to_csv("synthetic_focus_cur_v1_1.csv", index=False)
    print("Synthetic CUR generated and saved as 'synthetic_focus_cur_v1_1.csv'.")