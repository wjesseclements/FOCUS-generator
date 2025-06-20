import random
import pandas as pd

from backend.focus_metadata import FOCUS_METADATA
from backend.column_generators import GenerationContext
from backend.generator_factory import get_generator_factory
from backend.logging_config import setup_logging

logger = setup_logging(__name__)

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
    total_cost = random.uniform(min_val, max_val)
    logger.info("Generated total cost", extra={"profile": profile, "total_cost": total_cost})
    return total_cost


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
    Generates a single cell for a given column using the generator architecture.
    
    Args:
        col_name: The name of the column to generate a value for
        row_idx: The index of the current row
        row_data: The data for the current row so far
        row_count: The total number of rows to generate
        profile: The profile to use (Greenfield, Large Business, Enterprise)
        total_dataset_cost: The total cost for the dataset
        distribution: The distribution to use (Evenly Distributed, ML-Focused, Data-Intensive, Media-Intensive)
    """
    # Create generation context
    context = GenerationContext(
        col_name=col_name,
        row_idx=row_idx,
        row_data=row_data,
        row_count=row_count,
        profile=profile,
        total_dataset_cost=total_dataset_cost,
        distribution=distribution,
        metadata=FOCUS_METADATA[col_name]
    )
    
    # Get appropriate generator and generate value
    factory = get_generator_factory()
    generator = factory.get_generator(col_name)
    return generator.generate_value(context)


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
    logger.info("Starting FOCUS data generation", extra={
        "row_count": row_count,
        "profile": profile,
        "distribution": distribution
    })
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
    logger.debug("Applying post-processing")
    df = post_process(df)
    
    logger.info("FOCUS data generation completed", extra={
        "row_count": len(df),
        "columns": len(df.columns)
    })
    
    # Step 3: Apply distribution-specific post-processing
    df = apply_distribution_post_processing(df, distribution)
    
    return df


if __name__ == "__main__":
    # Quick test
    df_test = generate_focus_data(row_count=5, profile="Greenfield")
    print(df_test.head())