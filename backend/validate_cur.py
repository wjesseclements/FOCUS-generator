import pandas as pd
import warnings
from dateutil import parser

from .focus_metadata import FOCUS_METADATA

def validate_focus_df(df: pd.DataFrame) -> None:
    """
    Validates a DataFrame against:
      1. FOCUS metadata column-level constraints (nulls, data types, allowed values, etc.)
      2. Common cross-column rules from the FOCUS v1.1 spec.
    
    Raises ValueError if any hard requirement is violated.
    Prints warnings for recommended columns that are missing or partially violated.
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 1. CHECK THAT ALL COLUMNS REQUIRED BY THE FOCUS SPEC EXIST
    #    AND THAT MANDATORY COLUMNS ARE NOT MISSING
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    columns_in_df = set(df.columns)
    for col_name, meta in FOCUS_METADATA.items():
        feature_level = meta.get("feature_level", "").lower()
        if feature_level == "mandatory":
            if col_name not in columns_in_df:
                raise ValueError(
                    f"Missing mandatory column '{col_name}' from the DataFrame."
                )
        elif feature_level == "recommended":
            # Not strictly an error, but let's warn
            if col_name not in columns_in_df:
                warnings.warn(
                    f"Recommended column '{col_name}' is missing from the DataFrame."
                )
        # For columns that are 'Conditional', we won't enforce presence unless
        # you specifically want to. (We do cross-column checks if they exist.)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 2. VALIDATE COLUMN-LEVEL CONSTRAINTS FOR EACH COLUMN THAT DOES EXIST
    #    - Null constraints
    #    - Allowed values
    #    - Data type checks (decimal, string, datetime, json)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    for col_name, meta in FOCUS_METADATA.items():
        if col_name not in df.columns:
            continue  # If it's missing but only 'Conditional' or 'Recommended', skip

        series = df[col_name]
        allows_null = meta.get("allows_nulls", True)
        allowed_values = meta.get("allowed_values", None)
        data_type = meta.get("data_type", None)

        # 2.1 Null check if NOT allowed
        if not allows_null:
            # If we find nulls, that's a violation
            num_nulls = series.isnull().sum()
            if num_nulls > 0:
                raise ValueError(
                    f"Column '{col_name}' has {num_nulls} null values but 'allows_nulls' is False."
                )

        # 2.2 Allowed values check (if applicable)
        if allowed_values and data_type == "string":
            # We'll ensure that all non-null entries are in allowed_values
            invalid = series.dropna()[~series.dropna().isin(allowed_values)]
            if len(invalid) > 0:
                raise ValueError(
                    f"Column '{col_name}' has invalid string values not in allowed_values: {invalid.unique()}."
                )

        # 2.3 Data type check
        if data_type in ["decimal", "numeric"]:
            # Ensure all non-null are numeric (float or int)
            non_numeric = series.dropna().apply(lambda x: not isinstance(x, (int, float)))
            if non_numeric.any():
                bad_vals = series[non_numeric].unique()
                raise ValueError(
                    f"Column '{col_name}' expects numeric but found: {bad_vals}"
                )

        elif data_type == "string":
            # Ensure all non-null are strings
            non_string = series.dropna().apply(lambda x: not isinstance(x, str))
            if non_string.any():
                bad_vals = series[non_string].unique()
                raise ValueError(
                    f"Column '{col_name}' expects string but found: {bad_vals}"
                )

        elif data_type == "datetime":
            # Try parsing each non-null string to a datetime
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
            # Must be dict or list, etc. We'll assume dict for Key-Value Format
            for idx, val in series.dropna().items():
                if not isinstance(val, dict):
                    raise ValueError(
                        f"Column '{col_name}' expects a dict (Key-Value Format), got '{type(val)}' at row {idx}."
                    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 3. CROSS-COLUMN RULES (SAMPLE LIST)
    #    Expand or modify these to reflect your desired spec constraints.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # 3.1 If ChargeCategory = 'Tax', then SkuId, SkuPriceId MUST be null
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

    # 3.2 If ChargeCategory = 'Purchase', then ChargeFrequency != 'Usage-Based'
    if "ChargeCategory" in df.columns and "ChargeFrequency" in df.columns:
        purchase_mask = df["ChargeCategory"] == "Purchase"
        bad_freq = df.loc[purchase_mask & (df["ChargeFrequency"] == "Usage-Based")]
        if len(bad_freq) > 0:
            raise ValueError(
                "Found rows where ChargeCategory='Purchase' but ChargeFrequency='Usage-Based'. "
                f"Row indices: {bad_freq.index.tolist()}"
            )

    # 3.3 If CommitmentDiscountId is null => other discount columns must be null
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

    # 3.4 If ChargeCategory='Usage' and CommitmentDiscountId is not null, 
    #     then CommitmentDiscountStatus must be either 'Used' or 'Unused' (already covered by allowed_values?)
    if ("ChargeCategory" in df.columns and 
        "CommitmentDiscountId" in df.columns and 
        "CommitmentDiscountStatus" in df.columns):
        usage_mask = df["ChargeCategory"] == "Usage"
        cd_not_null = df["CommitmentDiscountId"].notnull()
        # Must not be null => check if status is missing
        must_have_status = df.loc[usage_mask & cd_not_null & df["CommitmentDiscountStatus"].isnull()]
        if len(must_have_status) > 0:
            raise ValueError(
                "Rows with ChargeCategory='Usage' and non-null CommitmentDiscountId "
                "but null CommitmentDiscountStatus. Indices: "
                f"{must_have_status.index.tolist()}"
            )

    # 3.5 If CapacityReservationId is null => CapacityReservationStatus must be null
    if "CapacityReservationId" in df.columns and "CapacityReservationStatus" in df.columns:
        null_crid_mask = df["CapacityReservationId"].isnull()
        bad_crstatus = df.loc[null_crid_mask & df["CapacityReservationStatus"].notnull()]
        if len(bad_crstatus) > 0:
            raise ValueError(
                "Rows have null CapacityReservationId but non-null CapacityReservationStatus. "
                f"Indices: {bad_crstatus.index.tolist()}"
            )

    # 3.6 If ChargeCategory='Usage' => PricingQuantity MUST NOT be null unless ChargeClass='Correction'
    if "ChargeCategory" in df.columns and "PricingQuantity" in df.columns:
        usage_mask = df["ChargeCategory"] == "Usage"
        # We also need to check 'ChargeClass' if it exists
        if "ChargeClass" in df.columns:
            correction_mask = df["ChargeClass"] == "Correction"
            # So if usage_mask & ~correction_mask => PricingQuantity must not be null
            bad_pq = df.loc[usage_mask & ~correction_mask & df["PricingQuantity"].isnull()]
            if len(bad_pq) > 0:
                raise ValueError(
                    "Rows have ChargeCategory='Usage' and ChargeClass!='Correction' but null PricingQuantity. "
                    f"Indices: {bad_pq.index.tolist()}"
                )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 4. IF WE GET HERE, NO ERRORS WERE FOUND
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    print("Validation passed successfully! No violations found.")