# FOCUS Column Relationships and Constraints

This document provides detailed information about the relationships and constraints between columns in the FOCUS specification as implemented in this project.

## Core Column Groups and Their Relationships

### 1. Billing Hierarchy Columns
- **BillingAccountId** and **BillingAccountName**: These columns represent the top-level billing entity. BillingAccountId is mandatory and cannot be null, while BillingAccountName can be null.
- **SubAccountId** and **SubAccountName**: These represent sub-entities within the billing account hierarchy. They are often used for organizational grouping and cost allocation.

### 2. Charge Classification Columns
- **ChargeCategory**: Defines the type of charge (Usage, Purchase, Tax, Credit, Adjustment). This column influences many other columns' requirements.
- **ChargeClass**: Indicates if a charge is a correction to a previous charge.
- **ChargeFrequency**: Indicates how often a charge occurs (One-Time, Recurring, Usage-Based).

### 3. Time Period Columns
- **BillingPeriodStart** and **BillingPeriodEnd**: Define the billing cycle timeframe.
- **ChargePeriodStart** and **ChargePeriodEnd**: Define when a specific charge occurred, which is typically a subset of the billing period.

### 4. Cost Columns
- **BilledCost**: The actual invoiced amount (mandatory).
- **ListCost**: The cost before any discounts.
- **ContractedCost**: The cost after negotiated discounts but before commitment-based discounts.
- **EffectiveCost**: The fully amortized cost including all discounts and spreading one-time purchases over their useful life.

### 5. Commitment Discount Columns
- **CommitmentDiscountId**: The identifier for a commitment-based discount.
- **CommitmentDiscountStatus**: Indicates if the commitment was used or unused.
- **CommitmentDiscountType**: The type of commitment (Reserved, SavingsPlan, etc.).
- **CommitmentDiscountCategory**: Whether the commitment is based on usage or spend.
- **CommitmentDiscountQuantity** and **CommitmentDiscountUnit**: The amount and unit of measurement for the commitment.

### 6. Capacity Reservation Columns
- **CapacityReservationId**: The identifier for a capacity reservation.
- **CapacityReservationStatus**: Indicates if the reservation was used or unused.

### 7. Resource Identification Columns
- **ResourceId** and **ResourceName**: Identify specific resources.
- **ResourceType**: Categorizes the type of resource.
- **ServiceName**, **ServiceCategory**, and **ServiceSubcategory**: Identify and categorize the service.

### 8. SKU and Pricing Columns
- **SkuId** and **SkuPriceId**: Identify the specific SKU and its pricing.
- **SkuMeter** and **SkuPriceDetails**: Provide additional details about the SKU.
- **PricingQuantity** and **PricingUnit**: The amount and unit used for pricing.
- **ConsumedQuantity** and **ConsumedUnit**: The amount and unit of actual consumption.

## Critical Cross-Column Constraints

1. **Tax-Related Constraints**:
   - When ChargeCategory = 'Tax', both SkuId and SkuPriceId MUST be null.

2. **Purchase-Related Constraints**:
   - When ChargeCategory = 'Purchase', ChargeFrequency MUST NOT be 'Usage-Based'.

3. **Commitment Discount Constraints**:
   - When CommitmentDiscountId is null, all other commitment discount columns MUST be null.
   - When ChargeCategory = 'Usage' and CommitmentDiscountId is not null, CommitmentDiscountStatus MUST NOT be null.

4. **Capacity Reservation Constraints**:
   - When CapacityReservationId is null, CapacityReservationStatus MUST be null.

5. **Usage Pricing Constraints**:
   - When ChargeCategory = 'Usage' and ChargeClass is not 'Correction', PricingQuantity MUST NOT be null.

6. **Time Period Constraints**:
   - ChargePeriodStart and ChargePeriodEnd MUST fall within BillingPeriodStart and BillingPeriodEnd.
   - ChargePeriodStart MUST be before ChargePeriodEnd.
   - BillingPeriodStart MUST be before BillingPeriodEnd.

7. **Cost Relationship Constraints**:
   - BilledCost is typically less than or equal to ListCost due to discounts.
   - EffectiveCost may differ from BilledCost due to amortization of upfront purchases.

## Data Validation Considerations

When validating FOCUS-conformed data, consider these aspects:

1. **Mandatory Column Presence**: Ensure all mandatory columns are present.
2. **Data Type Validation**: Ensure each column contains values of the correct data type.
3. **Null Validation**: Ensure columns that don't allow nulls don't contain null values.
4. **Allowed Values**: For columns with enumerated allowed values, ensure values are from the allowed set.
5. **Cross-Column Validation**: Enforce the relationships and constraints described above.
6. **Temporal Logic**: Ensure time periods are logically consistent.
7. **Numeric Consistency**: Ensure cost columns have consistent relationships where applicable.

## Implementation Notes

The validation logic in `validate_cur.py` implements many of these constraints, but not all. Consider enhancing the validation to cover more of these relationships for a more robust implementation.