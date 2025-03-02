import pandas as pd
import warnings
from dateutil import parser
from datetime import datetime

from .focus_metadata import FOCUS_METADATA

def enhanced_validate_focus_df(df: pd.DataFrame) -> None:
    """
    Enhanced validation of a DataFrame against FOCUS v1.1 specification.
    Includes additional cross-column validations and more comprehensive checks.
    
    Args:
        df: A pandas DataFrame containing FOCUS-conformed data
        
    Raises:
        ValueError: If any validation rule is violated
    """
    # First, run the basic validations
    basic_validate_focus_df(df)
    
    # Then run enhanced validations
    validate_time_periods(df)
    validate_cost_relationships(df)
    validate_enhanced_cross_column_rules(df)
    validate_data_consistency(df)
    
    print("Enhanced validation passed successfully! No violations found.")

def basic_validate_focus_df(df: pd.DataFrame) -> None:
    """
    Basic validation of a DataFrame against FOCUS metadata constraints.
    This is similar to the original validate_focus_df function.
    """
    # Check mandatory columns
    columns_in_df = set(df.columns)
    for col_name, meta in FOCUS_METADATA.items():
        feature_level = meta.get("feature_level", "").lower()
        if feature_level == "mandatory":
            if col_name not in columns_in_df:
                raise ValueError(
                    f"Missing mandatory column '{col_name}' from the DataFrame."
                )
        elif feature_level == "recommended":
            if col_name not in columns_in_df:
                warnings.warn(
                    f"Recommended column '{col_name}' is missing from the DataFrame."
                )

    # Validate column-level constraints
    for col_name, meta in FOCUS_METADATA.items():
        if col_name not in df.columns:
            continue

        series = df[col_name]
        allows_null = meta.get("allows_nulls", True)
        allowed_values = meta.get("allowed_values", None)
        data_type = meta.get("data_type", None)

        # Null check
        if not allows_null:
            num_nulls = series.isnull().sum()
            if num_nulls > 0:
                raise ValueError(
                    f"Column '{col_name}' has {num_nulls} null values but 'allows_nulls' is False."
                )

        # Allowed values check
        if allowed_values and data_type == "string":
            invalid = series.dropna()[~series.dropna().isin(allowed_values)]
            if len(invalid) > 0:
                raise ValueError(
                    f"Column '{col_name}' has invalid string values not in allowed_values: {invalid.unique()}."
                )

        # Data type check
        if data_type in ["decimal", "numeric"]:
            non_numeric = series.dropna().apply(lambda x: not isinstance(x, (int, float)))
            if non_numeric.any():
                bad_vals = series[non_numeric].unique()
                raise ValueError(
                    f"Column '{col_name}' expects numeric but found: {bad_vals}"
                )
        elif data_type == "string":
            non_string = series.dropna().apply(lambda x: not isinstance(x, str))
            if non_string.any():
                bad_vals = series[non_string].unique()
                raise ValueError(
                    f"Column '{col_name}' expects string but found: {bad_vals}"
                )
        elif data_type == "datetime":
            for idx, val in series.dropna().items():
                if not isinstance(val, str):
                    raise ValueError(
                        f"Column '{col_name}' expects a datetime string, got type {type(val)} at row {idx}."
                    )
                try:
                    _ = parser.parse(val)
                except Exception:
                    raise ValueError(
                        f"Column '{col_name}' has invalid datetime format '{val}' at row {idx}."
                    )
        elif data_type == "json":
            for idx, val in series.dropna().items():
                if not isinstance(val, dict):
                    raise ValueError(
                        f"Column '{col_name}' expects a dict (Key-Value Format), got '{type(val)}' at row {idx}."
                    )

    # Basic cross-column rules
    validate_basic_cross_column_rules(df)

def validate_basic_cross_column_rules(df: pd.DataFrame) -> None:
    """
    Validates basic cross-column rules from the original validation function.
    """
    # If ChargeCategory = 'Tax', then SkuId, SkuPriceId MUST be null
    if "ChargeCategory" in df.columns:
        tax_mask = df["ChargeCategory"] == "Tax"
        if "SkuId" in df.columns:
            bad_skuid_rows = df.loc[tax_mask & df["SkuId"].notnull()]
            if len(bad_skuid_rows) > 0:
                raise ValueError(
                    "Found rows where ChargeCategory='Tax' but SkuId is not null. "
                    f"Row indices: {bad_skuid_rows.index.tolist()}"
                )
        if "SkuPriceId" in df.columns:
            bad_skuprice_rows = df.loc[tax_mask & df["SkuPriceId"].notnull()]
            if len(bad_skuprice_rows) > 0:
                raise ValueError(
                    "Found rows where ChargeCategory='Tax' but SkuPriceId is not null. "
                    f"Row indices: {bad_skuprice_rows.index.tolist()}"
                )

    # If ChargeCategory = 'Purchase', then ChargeFrequency != 'Usage-Based'
    if "ChargeCategory" in df.columns and "ChargeFrequency" in df.columns:
        purchase_mask = df["ChargeCategory"] == "Purchase"
        bad_freq = df.loc[purchase_mask & (df["ChargeFrequency"] == "Usage-Based")]
        if len(bad_freq) > 0:
            raise ValueError(
                "Found rows where ChargeCategory='Purchase' but ChargeFrequency='Usage-Based'. "
                f"Row indices: {bad_freq.index.tolist()}"
            )

    # If CommitmentDiscountId is null => other discount columns must be null
    cd_cols = [
        "CommitmentDiscountName",
        "CommitmentDiscountCategory",
        "CommitmentDiscountQuantity",
        "CommitmentDiscountStatus",
        "CommitmentDiscountType",
        "CommitmentDiscountUnit"
    ]
    if "CommitmentDiscountId" in df.columns:
        null_cd_mask = df["CommitmentDiscountId"].isnull()
        for ccol in cd_cols:
            if ccol in df.columns:
                bad_rows = df.loc[null_cd_mask & df[ccol].notnull()]
                if len(bad_rows) > 0:
                    raise ValueError(
                        f"Rows have null CommitmentDiscountId but non-null {ccol}. "
                        f"Indices: {bad_rows.index.tolist()}"
                    )

    # If ChargeCategory='Usage' and CommitmentDiscountId is not null, 
    # then CommitmentDiscountStatus must be either 'Used' or 'Unused'
    if ("ChargeCategory" in df.columns and 
        "CommitmentDiscountId" in df.columns and 
        "CommitmentDiscountStatus" in df.columns):
        usage_mask = df["ChargeCategory"] == "Usage"
        cd_not_null = df["CommitmentDiscountId"].notnull()
        must_have_status = df.loc[usage_mask & cd_not_null & df["CommitmentDiscountStatus"].isnull()]
        if len(must_have_status) > 0:
            raise ValueError(
                "Rows with ChargeCategory='Usage' and non-null CommitmentDiscountId "
                "but null CommitmentDiscountStatus. Indices: "
                f"{must_have_status.index.tolist()}"
            )

    # If CapacityReservationId is null => CapacityReservationStatus must be null
    if "CapacityReservationId" in df.columns and "CapacityReservationStatus" in df.columns:
        null_crid_mask = df["CapacityReservationId"].isnull()
        bad_crstatus = df.loc[null_crid_mask & df["CapacityReservationStatus"].notnull()]
        if len(bad_crstatus) > 0:
            raise ValueError(
                "Rows have null CapacityReservationId but non-null CapacityReservationStatus. "
                f"Indices: {bad_crstatus.index.tolist()}"
            )

    # If ChargeCategory='Usage' => PricingQuantity MUST NOT be null unless ChargeClass='Correction'
    if "ChargeCategory" in df.columns and "PricingQuantity" in df.columns:
        usage_mask = df["ChargeCategory"] == "Usage"
        if "ChargeClass" in df.columns:
            correction_mask = df["ChargeClass"] == "Correction"
            bad_pq = df.loc[usage_mask & ~correction_mask & df["PricingQuantity"].isnull()]
            if len(bad_pq) > 0:
                raise ValueError(
                    "Rows have ChargeCategory='Usage' and ChargeClass!='Correction' but null PricingQuantity. "
                    f"Indices: {bad_pq.index.tolist()}"
                )

def validate_time_periods(df: pd.DataFrame) -> None:
    """
    Validates time period relationships and constraints.
    """
    # Check if required columns exist
    time_columns = ["BillingPeriodStart", "BillingPeriodEnd", "ChargePeriodStart", "ChargePeriodEnd"]
    missing_columns = [col for col in time_columns if col not in df.columns]
    if missing_columns:
        warnings.warn(f"Time period validation skipped due to missing columns: {missing_columns}")
        return
    
    # Parse datetime strings to datetime objects
    try:
        billing_start = df["BillingPeriodStart"].apply(parser.parse)
        billing_end = df["BillingPeriodEnd"].apply(parser.parse)
        charge_start = df["ChargePeriodStart"].apply(parser.parse)
        charge_end = df["ChargePeriodEnd"].apply(parser.parse)
    except Exception as e:
        warnings.warn(f"Time period validation skipped due to parsing error: {str(e)}")
        return
    
    # Check that billing period start is before billing period end
    invalid_billing = df[billing_start >= billing_end].index.tolist()
    if invalid_billing:
        raise ValueError(
            "Found rows where BillingPeriodStart is not before BillingPeriodEnd. "
            f"Row indices: {invalid_billing}"
        )
    
    # Check that charge period start is before charge period end
    invalid_charge = df[charge_start >= charge_end].index.tolist()
    if invalid_charge:
        raise ValueError(
            "Found rows where ChargePeriodStart is not before ChargePeriodEnd. "
            f"Row indices: {invalid_charge}"
        )
    
    # Check that charge period is within billing period
    outside_billing = df[(charge_start < billing_start) | (charge_end > billing_end)].index.tolist()
    if outside_billing:
        raise ValueError(
            "Found rows where charge period is outside billing period. "
            f"Row indices: {outside_billing}"
        )

def validate_cost_relationships(df: pd.DataFrame) -> None:
    """
    Validates relationships between cost columns.
    """
    # Check if we have the necessary columns for cost validation
    cost_columns = ["BilledCost", "ListCost", "ContractedCost", "EffectiveCost"]
    available_cost_columns = [col for col in cost_columns if col in df.columns]
    
    if len(available_cost_columns) < 2:
        warnings.warn("Cost relationship validation skipped due to insufficient cost columns")
        return
    
    # Check that BilledCost is not greater than ListCost (when both are present)
    if "BilledCost" in df.columns and "ListCost" in df.columns:
        # Only compare rows where both values are not null
        comparable = df[df["BilledCost"].notnull() & df["ListCost"].notnull()]
        invalid_cost = comparable[comparable["BilledCost"] > comparable["ListCost"]].index.tolist()
        
        if invalid_cost:
            warnings.warn(
                "Found rows where BilledCost is greater than ListCost, which may indicate "
                f"incorrect discount application. Row indices: {invalid_cost}"
            )
    
    # Check for negative costs (usually not valid except for credits/adjustments)
    for cost_col in available_cost_columns:
        negative_costs = df[
            (df[cost_col] < 0) & 
            (df["ChargeCategory"].isin(["Usage", "Purchase", "Tax"]) if "ChargeCategory" in df.columns else True)
        ].index.tolist()
        
        if negative_costs:
            warnings.warn(
                f"Found negative values in {cost_col} for non-Credit/Adjustment charge categories. "
                f"Row indices: {negative_costs}"
            )

def validate_enhanced_cross_column_rules(df: pd.DataFrame) -> None:
    """
    Validates additional cross-column rules not covered in the basic validation.
    """
    # If ChargeCategory = 'Credit', BilledCost should be negative or zero
    if "ChargeCategory" in df.columns and "BilledCost" in df.columns:
        credit_mask = df["ChargeCategory"] == "Credit"
        positive_credits = df.loc[credit_mask & (df["BilledCost"] > 0)]
        if len(positive_credits) > 0:
            warnings.warn(
                "Found rows where ChargeCategory='Credit' but BilledCost is positive. "
                f"Row indices: {positive_credits.index.tolist()}"
            )
    
    # If ChargeCategory = 'Purchase', check for appropriate ChargeFrequency
    if "ChargeCategory" in df.columns and "ChargeFrequency" in df.columns:
        purchase_mask = df["ChargeCategory"] == "Purchase"
        missing_freq = df.loc[purchase_mask & df["ChargeFrequency"].isnull()]
        if len(missing_freq) > 0:
            warnings.warn(
                "Found rows where ChargeCategory='Purchase' but ChargeFrequency is null. "
                f"Row indices: {missing_freq.index.tolist()}"
            )
    
    # If ResourceId is present, ResourceType should also be present
    if "ResourceId" in df.columns and "ResourceType" in df.columns:
        missing_type = df.loc[df["ResourceId"].notnull() & df["ResourceType"].isnull()]
        if len(missing_type) > 0:
            warnings.warn(
                "Found rows with ResourceId but missing ResourceType. "
                f"Row indices: {missing_type.index.tolist()}"
            )
    
    # If ServiceName is present, ServiceCategory should also be present and not null
    if "ServiceName" in df.columns and "ServiceCategory" in df.columns:
        missing_category = df.loc[df["ServiceName"].notnull() & df["ServiceCategory"].isnull()]
        if len(missing_category) > 0:
            raise ValueError(
                "Found rows with ServiceName but missing ServiceCategory. "
                f"Row indices: {missing_category.index.tolist()}"
            )
    
    # If CommitmentDiscountStatus = 'Unused', check for appropriate BilledCost
    if "CommitmentDiscountStatus" in df.columns and "BilledCost" in df.columns:
        unused_mask = df["CommitmentDiscountStatus"] == "Unused"
        non_zero_unused = df.loc[unused_mask & (df["BilledCost"] != 0)]
        if len(non_zero_unused) > 0:
            warnings.warn(
                "Found rows where CommitmentDiscountStatus='Unused' but BilledCost is not zero. "
                f"Row indices: {non_zero_unused.index.tolist()}"
            )

def validate_data_consistency(df: pd.DataFrame) -> None:
    """
    Validates overall data consistency and patterns.
    """
    # Check for duplicate rows
    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        warnings.warn(f"Found {duplicate_rows} duplicate rows in the dataset")
    
    # Check for consistent currency
    if "BillingCurrency" in df.columns:
        unique_currencies = df["BillingCurrency"].nunique()
        if unique_currencies > 1:
            warnings.warn(
                f"Found {unique_currencies} different currencies in BillingCurrency. "
                "This may be expected but could cause issues with cost aggregation."
            )
    
    # Check for consistent time periods
    if "BillingPeriodStart" in df.columns and "BillingPeriodEnd" in df.columns:
        unique_periods = df[["BillingPeriodStart", "BillingPeriodEnd"]].drop_duplicates().shape[0]
        if unique_periods > 1:
            warnings.warn(
                f"Found {unique_periods} different billing periods in the dataset. "
                "This may be expected but could cause issues with period-based analysis."
            )
    
    # Check for missing tags on resources
    if "ResourceId" in df.columns and "Tags" in df.columns:
        missing_tags = df.loc[df["ResourceId"].notnull() & df["Tags"].isnull()]
        if len(missing_tags) > 0:
            warnings.warn(
                f"Found {len(missing_tags)} rows with ResourceId but missing Tags. "
                "This may indicate incomplete tagging."
            )
    
    # Check for consistent provider
    if "ProviderName" in df.columns:
        unique_providers = df["ProviderName"].nunique()
        if unique_providers > 1:
            warnings.warn(
                f"Found {unique_providers} different providers in ProviderName. "
                "This may be expected for multi-cloud data but could cause issues with provider-specific analysis."
            )

# For backward compatibility
def validate_focus_df(df: pd.DataFrame) -> None:
    """
    Original validation function for backward compatibility.
    """
    basic_validate_focus_df(df)