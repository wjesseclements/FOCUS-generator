import random
import uuid
import json
from datetime import datetime, timezone, timedelta

import pandas as pd
from .focus_metadata import FOCUS_METADATA

# Example: Weighted distributions for certain columns
CHARGE_CATEGORY_WEIGHTS = {
    "Usage": 0.7,
    "Purchase": 0.15,
    "Tax": 0.05,
    "Credit": 0.05,
    "Adjustment": 0.05,
}

SERVICE_CATEGORY_WEIGHTS = {
    "Compute": 0.3,
    "Storage": 0.2,
    "Databases": 0.2,
    "Networking": 0.1,
    "AI and Machine Learning": 0.1,
    "Other": 0.1,
}

# Example: T-shirt profile cost ranges (for distributing BilledCost)
PROFILE_COST_RANGES = {
    "Greenfield": (10_000, 50_000),
    "Large Business": (100_000, 250_000),
    "Enterprise": (500_000, 2_000_000),
}

def generate_profile_total_cost(profile):
    """
    Pick a random total cost for the entire dataset, based on the chosen profile.
    """
    min_val, max_val = PROFILE_COST_RANGES.get(profile, (50_000, 100_000))
    return random.uniform(min_val, max_val)

def distribute_billed_cost(row_idx, row_count, total_dataset_cost):
    """
    Distribute the dataset's total cost across rows in a naive way.
    For the final row, we could adjust to ensure exact sum, but for now,
    we'll just approximate by randomizing around a per-row average.
    """
    base_per_row = total_dataset_cost / row_count
    # random factor of ±20%
    factor = random.uniform(0.8, 1.2)
    return round(base_per_row * factor, 2)

def generate_value_for_column(col_name, row_idx, row_data, row_count, profile, total_dataset_cost):
    """
    Generates a single cell for a given column, referencing the FOCUS metadata
    and optionally other already-generated columns in row_data.
    """
    meta = FOCUS_METADATA[col_name]
    data_type = meta.get("data_type")
    allows_null = meta.get("allows_nulls", True)
    allowed_values = meta.get("allowed_values", None)
    value_format = meta.get("value_format", None)

    # --------------------------------------------------------------
    # CUSTOM LOGIC FOR SELECT COLUMNS (examples)
    # --------------------------------------------------------------
    if col_name == "ChargeCategory":
        # Weighted random choice
        categories = list(CHARGE_CATEGORY_WEIGHTS.keys())
        weights = list(CHARGE_CATEGORY_WEIGHTS.values())
        return random.choices(categories, weights=weights, k=1)[0]

    elif col_name == "BilledCost":
        # Distribute total cost across rows
        return distribute_billed_cost(row_idx, row_count, total_dataset_cost)

    elif col_name == "BillingPeriodStart":
        # Hard-code a monthly period start (Jan 1st)
        return "2024-01-01T00:00:00Z"

    elif col_name == "BillingPeriodEnd":
        # Hard-code the monthly period end (Feb 1st)
        return "2024-02-01T00:00:00Z"

    elif col_name == "ChargePeriodStart":
        # Example: each row is a daily usage period
        start_dt = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=row_idx)
        return start_dt.isoformat()

    elif col_name == "ChargePeriodEnd":
        # 1 day after ChargePeriodStart
        cps_str = row_data.get("ChargePeriodStart")
        if cps_str:
            start_dt = datetime.fromisoformat(cps_str)
            end_dt = start_dt + timedelta(days=1)
            return end_dt.isoformat()
        # fallback
        return "2024-01-02T00:00:00+00:00"

    elif col_name == "ServiceCategory":
        # Weighted random choice for demonstration
        cats = list(SERVICE_CATEGORY_WEIGHTS.keys())
        wts = list(SERVICE_CATEGORY_WEIGHTS.values())
        return random.choices(cats, weights=wts, k=1)[0]

    elif col_name == "PricingUnit":
        # Example cross-logic: if ChargeCategory is "Usage" or "Purchase", pick a random unit
        charge_cat = row_data.get("ChargeCategory")
        if charge_cat in ["Usage", "Purchase"]:
            # skip random null chance
            return random.choice(["Hours", "GB-Hours", "Requests", "Transactions"])
        else:
            # null otherwise
            return None

    elif col_name == "SkuId":
        # If ChargeCategory = "Tax", must be null, else random ID
        cc = row_data.get("ChargeCategory")
        if cc == "Tax":
            return None
        # Return a random "SKU-xxxx"
        return f"SKU-{uuid.uuid4().hex[:4]}"

    elif col_name == "SkuPriceId":
        # Same logic: if ChargeCategory = "Tax", must be null
        cc = row_data.get("ChargeCategory")
        if cc == "Tax":
            return None
        return f"SKUPRICE-{uuid.uuid4().hex[:4]}"

    elif col_name == "CapacityReservationId":
        # e.g. 30% chance to have a reservation
        if random.random() < 0.3:
            return f"CapRes-{uuid.uuid4().hex[:4]}"
        else:
            return None

    elif col_name == "CapacityReservationStatus":
        cid = row_data.get("CapacityReservationId")
        if cid is not None:
            return random.choice(["Used", "Unused"])
        else:
            return None

    elif col_name == "CommitmentDiscountId":
        # 20% chance to have an ID
        if random.random() < 0.2:
            return f"CD-{uuid.uuid4().hex[:4]}"
        else:
            return None

    elif col_name == "CommitmentDiscountStatus":
        # If ID != null and ChargeCategory=Usage => pick "Used"/"Unused"
        cdid = row_data.get("CommitmentDiscountId")
        ccat = row_data.get("ChargeCategory")
        if cdid is not None and ccat == "Usage":
            return random.choice(["Used", "Unused"])
        else:
            return None

    elif col_name == "CommitmentDiscountCategory":
        cdid = row_data.get("CommitmentDiscountId")
        if cdid is not None:
            return random.choice(["Spend", "Usage"])
        return None

    elif col_name == "CommitmentDiscountQuantity":
        cdid = row_data.get("CommitmentDiscountId")
        ccat = row_data.get("ChargeCategory")
        if cdid is not None and ccat == "Usage":
            return round(random.uniform(1, 50), 2)
        return None

    elif col_name == "CommitmentDiscountType":
        cdid = row_data.get("CommitmentDiscountId")
        if cdid is not None:
            return random.choice(["Reserved", "SavingsPlan", "Custom"])
        return None

    elif col_name == "CommitmentDiscountUnit":
        cdid = row_data.get("CommitmentDiscountId")
        if cdid is not None:
            # could be "Hours", "GB", etc.
            return random.choice(["Hours", "GB", "Requests"])
        return None

    elif col_name == "ChargeFrequency":
        # If ChargeCategory = "Purchase", avoid "Usage-Based"
        ccat = row_data.get("ChargeCategory")
        if ccat == "Purchase":
            return random.choice(["One-Time", "Recurring"])
        else:
            # For other categories, we can pick from all three
            return random.choice(["One-Time", "Recurring", "Usage-Based"])





    # --------------------------------------------------------------
    # FALLBACK: Generic logic if no special-case logic
    # --------------------------------------------------------------
    return generate_generic_value(col_name, meta, row_idx, row_data)

def generate_generic_value(col_name, meta, row_idx, row_data):
    """
    A generic fallback approach for columns that don't have
    special logic above.
    """
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
        return f"{col_name}_{row_idx}_{uuid.uuid4().hex[:4]}"

    # If nothing else matched
    return None

def post_process(df):
    """
    Optional: Second pass to correct or enforce cross-column constraints
    that are easier to fix after the entire row is generated.
    For example:
     - If CommitmentDiscountId is null, set CommitmentDiscountName, etc. to null.
     - If ChargeCategory=Tax, ensure SkuPriceId is null, etc. (We've done some inline, but you can also do it here.)
    """
    # Example: If CommitmentDiscountId is null, null out discount fields
    if "CommitmentDiscountId" in df.columns:
        mask_null_cd = df["CommitmentDiscountId"].isnull()
        discount_cols = [
            "CommitmentDiscountName", "CommitmentDiscountStatus",
            "CommitmentDiscountQuantity", "CommitmentDiscountUnit",
            "CommitmentDiscountType", "CommitmentDiscountCategory"
        ]
        for ccol in discount_cols:
            if ccol in df.columns:
                df.loc[mask_null_cd, ccol] = None

    return df


def generate_focus_data(row_count=10, profile="Greenfield"):
    """
    Generates a synthetic FOCUS dataset with refined logic for certain columns.
    """
    # Step 1: Pick a total cost once for the entire dataset
    total_cost = generate_profile_total_cost(profile)
    columns_in_order = list(FOCUS_METADATA.keys())  # or define a custom order

    rows = []
    for i in range(row_count):
        row_data = {}
        for col_name in columns_in_order:
            val = generate_value_for_column(
                col_name=col_name,
                row_idx=i,
                row_data=row_data,
                row_count=row_count,
                profile=profile,
                total_dataset_cost=total_cost
            )
            row_data[col_name] = val
        rows.append(row_data)

    df = pd.DataFrame(rows, columns=columns_in_order)

    # Step 2: Post-processing to fix cross-column constraints (optional)
    df = post_process(df)
    return df


if __name__ == "__main__":
    # Quick test
    df_test = generate_focus_data(row_count=5, profile="Greenfield")
    print(df_test.head())