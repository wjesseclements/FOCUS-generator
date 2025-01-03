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


# Generate synthetic data for each column
def generate_focus_data(row_count=20):
    current_time = datetime.now(timezone.utc)
    data = {
        "InvoiceId": [str(uuid.uuid4()) for _ in range(row_count)],
        "LinkedAccountId": [
            str(random.randint(100000000000, 999999999999))
            for _ in range(row_count)
        ],
        "UsageAccountId": [
            str(random.randint(100000000000, 999999999999))
            for _ in range(row_count)
        ],
        "ProductName": random.choices(
            ["Amazon EC2", "Amazon S3", "Amazon RDS", "Amazon DynamoDB"],
            k=row_count,
        ),
        "UsageType": random.choices(
            ["BoxUsage:m5.large", "TimedStorage-Gb", "ReadCapacityUnit-Hrs"],
            k=row_count,
        ),
        "Operation": random.choices(
            ["RunInstances", "PutObject", "ReadCapacityUnits"], k=row_count
        ),
        "AvailabilityZone": random.choices(
            ["us-east-1a", "us-east-1b", "us-east-1c"], k=row_count
        ),
        "Region": ["us-east-1"] * row_count,
        "UsageStartDate": [
            (current_time - timedelta(hours=i)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            for i in range(row_count)
        ],
        "UsageEndDate": [
            (current_time - timedelta(hours=i - 1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            for i in range(row_count)
        ],
        "ResourceId": [f"i-{uuid.uuid4().hex[:8]}" for _ in range(row_count)],
        "UsageAmount": [
            round(random.uniform(0.5, 10.0), 2) for _ in range(row_count)
        ],
        "BlendedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "UnblendedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "PublicOnDemandCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "SavingsPlanEffectiveCost": [
            round(random.uniform(0.05, 0.9), 5) for _ in range(row_count)
        ],
        "ReservationEffectiveCost": [
            round(random.uniform(0.05, 0.9), 5) for _ in range(row_count)
        ],
        "DiscountedCost": [
            round(random.uniform(0.05, 0.5), 5) for _ in range(row_count)
        ],
        "Tags": ["tag:Environment=Dev" for _ in range(row_count)],
        "CostCategory1": random.choices(
            ["CategoryA", "CategoryB", "CategoryC"], k=row_count
        ),
        "CostCategory2": random.choices(
            ["SubCategoryX", "SubCategoryY", "SubCategoryZ"], k=row_count
        ),
        "ResourceTags": ["Key1=Value1,Key2=Value2" for _ in range(row_count)],
        "ReservationARN": [
            str(uuid.uuid4()) if random.random() > 0.5 else ""
            for _ in range(row_count)
        ],
        "SavingsPlanARN": [
            str(uuid.uuid4()) if random.random() > 0.5 else ""
            for _ in range(row_count)
        ],
        "Tenancy": random.choices(
            ["default", "dedicated", "host"], k=row_count
        ),
        "PurchaseOption": random.choices(
            ["No Upfront", "Partial Upfront", "All Upfront"], k=row_count
        ),
        "AmortizedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "NetAmortizedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "NetUnblendedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "Credits": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "NetCredits": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "Tax": [round(random.uniform(0.01, 0.5), 5) for _ in range(row_count)],
        "NetTax": [
            round(random.uniform(0.01, 0.5), 5) for _ in range(row_count)
        ],
        "OtherDiscounts": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "NetOtherDiscounts": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "Rebates": [
            round(random.uniform(0.01, 0.5), 5) for _ in range(row_count)
        ],
        "NetRebates": [
            round(random.uniform(0.01, 0.5), 5) for _ in range(row_count)
        ],
        "Support": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "NetSupport": [
            round(random.uniform(0.01, 1.0), 5) for _ in range(row_count)
        ],
        "DiscountedBlendedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "DiscountedUnblendedCost": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "NormalizedUsageAmount": [
            round(random.uniform(0.1, 5.0), 5) for _ in range(row_count)
        ],
        "CurrencyCode": ["USD"] * row_count,
        "ExchangeRate": [1.0] * row_count,
        "BillType": random.choices(["Anniversary", "Monthly"], k=row_count),
        "PricingPlanId": [str(uuid.uuid4()) for _ in range(row_count)],
        "ServiceCode": random.choices(
            ["AmazonEC2", "AmazonS3", "AmazonRDS"], k=row_count
        ),
        "UsageTypeGroup": random.choices(
            ["Compute", "Storage", "Database"], k=row_count
        ),
        "ChargeType": random.choices(
            ["Usage", "Recurring", "One-Time"], k=row_count
        ),
        "RateId": [random.randint(1000, 9999) for _ in range(row_count)],
        "BillingEntity": random.choices(["AWS", "ThirdParty"], k=row_count),
    }
    return pd.DataFrame(data)


# Generate the synthetic CUR and save it as a CSV file
if __name__ == "__main__":
    row_count = 20  # Adjust row count as needed
    synthetic_cur = generate_focus_data(row_count)
    synthetic_cur.to_csv("synthetic_focus_cur_v1_1.csv", index=False)
    print(
        "Synthetic CUR generated and saved as 'synthetic_focus_cur_v1_1.csv'."
    )
