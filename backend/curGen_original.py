import random
import pandas as pd

from .focus_metadata import FOCUS_METADATA
from .column_generators import GenerationContext
from .generator_factory import get_generator_factory


# Profile cost ranges for distributing BilledCost
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

def generate_value_for_column(col_name, row_idx, row_data, row_count, profile, total_dataset_cost, distribution="Evenly Distributed"):
    """
    Generates a single cell for a given column, referencing the FOCUS metadata
    and optionally other already-generated columns in row_data.
    
    Args:
        col_name: The name of the column to generate a value for
        row_idx: The index of the current row
        row_data: The data for the current row so far
        row_count: The total number of rows to generate
        profile: The profile to use (Greenfield, Large Business, Enterprise)
        total_dataset_cost: The total cost for the dataset
        distribution: The distribution to use (Evenly Distributed, ML-Focused, Data-Intensive, Media-Intensive)
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
        # Use distribution-specific weights
        service_weights = DISTRIBUTION_SERVICE_WEIGHTS.get(distribution, DEFAULT_SERVICE_CATEGORY_WEIGHTS)
        cats = list(service_weights.keys())
        wts = list(service_weights.values())
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

def apply_distribution_post_processing(df, distribution):
    """
    Apply distribution-specific post-processing to the generated data.
    
    Args:
        df: The DataFrame to process
        distribution: The distribution to apply
        
    Returns:
        The processed DataFrame
    """
    if distribution == "ML-Focused":
        # Increase costs for AI and ML services
        if "ServiceCategory" in df.columns and "BilledCost" in df.columns:
            ml_mask = df["ServiceCategory"] == "AI and Machine Learning"
            df.loc[ml_mask, "BilledCost"] = df.loc[ml_mask, "BilledCost"] * random.uniform(1.2, 1.5)
            
            # Adjust EffectiveCost if present
            if "EffectiveCost" in df.columns:
                df.loc[ml_mask, "EffectiveCost"] = df.loc[ml_mask, "EffectiveCost"] * random.uniform(1.2, 1.5)
        
        # Add more GPU-related resources
        if "ResourceType" in df.columns:
            compute_mask = (df["ServiceCategory"] == "Compute") & df["ResourceType"].isnull()
            gpu_types = ["GPU Instance", "GPU Accelerator", "ML Instance"]
            df.loc[compute_mask, "ResourceType"] = df.loc[compute_mask].apply(
                lambda _: random.choice(gpu_types) if random.random() < 0.4 else "Standard Instance", 
                axis=1
            )
    
    elif distribution == "Data-Intensive":
        # Increase costs for Storage and Database services
        if "ServiceCategory" in df.columns and "BilledCost" in df.columns:
            data_mask = df["ServiceCategory"].isin(["Storage", "Databases"])
            df.loc[data_mask, "BilledCost"] = df.loc[data_mask, "BilledCost"] * random.uniform(1.1, 1.4)
            
            # Adjust EffectiveCost if present
            if "EffectiveCost" in df.columns:
                df.loc[data_mask, "EffectiveCost"] = df.loc[data_mask, "EffectiveCost"] * random.uniform(1.1, 1.4)
        
        # Add more storage-related resources
        if "ResourceType" in df.columns:
            storage_mask = (df["ServiceCategory"] == "Storage") & df["ResourceType"].isnull()
            storage_types = ["Block Storage", "Object Storage", "File Storage", "Archive Storage"]
            df.loc[storage_mask, "ResourceType"] = df.loc[storage_mask].apply(
                lambda _: random.choice(storage_types), 
                axis=1
            )
    
    elif distribution == "Media-Intensive":
        # Increase costs for Storage and Networking services
        if "ServiceCategory" in df.columns and "BilledCost" in df.columns:
            media_mask = df["ServiceCategory"].isin(["Storage", "Networking"])
            df.loc[media_mask, "BilledCost"] = df.loc[media_mask, "BilledCost"] * random.uniform(1.1, 1.3)
            
            # Adjust EffectiveCost if present
            if "EffectiveCost" in df.columns:
                df.loc[media_mask, "EffectiveCost"] = df.loc[media_mask, "EffectiveCost"] * random.uniform(1.1, 1.3)
        
        # Add more media-related resources
        if "ResourceType" in df.columns:
            compute_mask = (df["ServiceCategory"] == "Compute") & df["ResourceType"].isnull()
            media_types = ["Media Transcoder", "Video Processing", "Content Delivery"]
            df.loc[compute_mask, "ResourceType"] = df.loc[compute_mask].apply(
                lambda _: random.choice(media_types) if random.random() < 0.3 else "Standard Instance", 
                axis=1
            )
    
    # Ensure BilledCost is rounded to 2 decimal places
    if "BilledCost" in df.columns:
        df["BilledCost"] = df["BilledCost"].round(2)
    
    # Ensure EffectiveCost is rounded to 2 decimal places
    if "EffectiveCost" in df.columns:
        df["EffectiveCost"] = df["EffectiveCost"].round(2)
    
    return df


def generate_focus_data(row_count=10, profile="Greenfield", distribution="Evenly Distributed"):
    """
    Generates a synthetic FOCUS dataset with refined logic for certain columns.
    
    Args:
        row_count: The number of rows to generate
        profile: The profile to use (Greenfield, Large Business, Enterprise)
        distribution: The distribution to use (Evenly Distributed, ML-Focused, Data-Intensive, Media-Intensive)
    
    Returns:
        A pandas DataFrame containing the generated data
    """
    # Step 1: Pick a total cost once for the entire dataset
    total_cost = generate_profile_total_cost(profile)
    columns_in_order = list(FOCUS_METADATA.keys())  # or define a custom order

    # Apply distribution-specific adjustments to total cost
    if distribution == "ML-Focused":
        # ML workloads tend to be more expensive
        total_cost *= random.uniform(1.1, 1.3)
    elif distribution == "Data-Intensive":
        # Data storage can be expensive at scale
        total_cost *= random.uniform(1.05, 1.2)
    elif distribution == "Media-Intensive":
        # Media processing can be expensive
        total_cost *= random.uniform(1.1, 1.25)

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
                total_dataset_cost=total_cost,
                distribution=distribution
            )
            row_data[col_name] = val
        rows.append(row_data)

    df = pd.DataFrame(rows, columns=columns_in_order)

    # Step 2: Post-processing to fix cross-column constraints (optional)
    df = post_process(df)
    
    # Step 3: Apply distribution-specific post-processing
    df = apply_distribution_post_processing(df, distribution)
    
    return df


if __name__ == "__main__":
    # Quick test
    df_test = generate_focus_data(row_count=5, profile="Greenfield")
    print(df_test.head())