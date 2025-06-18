# Complete Generator Architecture

This document describes the complete column generator architecture for the FOCUS Generator project.

## 🎯 **Achievement: 100% Generator Coverage**

All 50 FOCUS columns now have specialized generators, eliminating the generic fallback for a completely tailored data generation experience.

## 🏗️ **Generator Architecture Overview**

### **Base Architecture**
- **`ColumnGenerator`** - Abstract base class
- **`GenerationContext`** - Context object with all generation parameters
- **`ColumnGeneratorFactory`** - Factory pattern for managing generators

### **Specialized Generator Classes**

#### **1. ChargeGenerator** (3 columns)
- `ChargeCategory` - Weighted distribution of charge types
- `ChargeFrequency` - Frequency based on charge category rules

#### **2. CostGenerator** (1 column)  
- `BilledCost` - Profile-based cost distribution

#### **3. DateTimeGenerator** (4 columns)
- `BillingPeriodStart/End` - Monthly billing periods
- `ChargePeriodStart/End` - Daily usage periods with relationships

#### **4. ServiceGenerator** (1 column)
- `ServiceCategory` - Distribution-weighted service categories

#### **5. SKUGenerator** (3 columns)
- `SkuId`, `SkuPriceId` - Context-aware SKU identifiers
- `PricingUnit` - Units based on charge category

#### **6. CommitmentDiscountGenerator** (6 columns)
- Complete commitment discount workflow
- Cross-column validation compliance
- Realistic discount names and quantities

#### **7. CapacityReservationGenerator** (2 columns)
- `CapacityReservationId` - Reservation identifiers
- `CapacityReservationStatus` - Status based on ID presence

#### **8. PricingGenerator** (3 columns)
- `PricingQuantity` - FOCUS validation compliant
- `ChargeClass` - Correction vs normal charges
- `PricingCategory` - Standard/Dynamic/Committed/Other

#### **9. ResourceGenerator** (3 columns)
- `ResourceId` - Service-specific resource IDs
- `ResourceName` - Names based on resource type
- `ResourceType` - Service category appropriate types

#### **10. AccountGenerator** (5 columns)
- `BillingAccountId/Name` - Realistic account information
- `SubAccountId/Name` - Department-based sub-accounts
- `BillingCurrency` - Global currency options

#### **11. CostDetailsGenerator** (5 columns)
- `EffectiveCost` - Based on billed cost with discounts
- `ListCost` - Higher than billed cost
- `ContractedCost` - Mandatory field, calculated properly
- `ListUnitPrice/ContractedUnitPrice` - Calculated from costs and quantities

#### **12. LocationGenerator** (3 columns) ⭐ *NEW*
- `RegionId` - Multi-cloud region support (AWS/Azure/GCP)
- `RegionName` - Human-readable region names
- `AvailabilityZone` - Provider-specific zone naming

#### **13. ServiceDetailsGenerator** (2 columns) ⭐ *NEW*
- `ServiceName` - Realistic cloud service names
- `ServiceSubcategory` - FOCUS-compliant subcategories (99 options)

#### **14. UsageMetricsGenerator** (3 columns) ⭐ *NEW*
- `ConsumedQuantity` - Service-appropriate usage amounts
- `ConsumedUnit` - Matching units (Hours, GB, Requests, etc.)
- `SkuMeter` - Descriptive meter names

#### **15. ProviderBusinessGenerator** (3 columns) ⭐ *NEW*
- `ProviderName` - AWS/Azure/Google Cloud
- `PublisherName` - Provider-specific publishers
- `InvoiceIssuerName` - Regional billing entities

#### **16. MetadataGenerator** (4 columns) ⭐ *NEW*
- `Tags` - Realistic resource tags (Environment, Project, Owner, etc.)
- `SkuPriceDetails` - Service-specific pricing metadata (JSON)
- `ChargeDescription` - Human-readable charge descriptions
- `CommitmentDiscountName` - Realistic discount plan names

## 🎨 **Key Features**

### **Cross-Column Relationships**
- Services determine regions and providers
- Regions determine availability zones
- Charge categories affect quantities and units
- Costs are calculated based on relationships

### **Multi-Cloud Support**
- AWS, Microsoft Azure, Google Cloud
- Provider-specific naming conventions
- Realistic service mappings
- Regional distribution patterns

### **FOCUS Compliance**
- All mandatory fields properly handled
- Conditional field logic implemented
- Allowed values respected
- Cross-column validation rules followed

### **Data Realism**
- Industry-standard service names
- Realistic cost distributions
- Proper tag structures
- Believable resource relationships

## 📊 **Coverage Statistics**

- **Total Columns**: 50
- **Specialized Generators**: 50 (100%)
- **Generic Fallback**: 0 (0%)
- **Validation Success**: 12/12 combinations (100%)

## 🧪 **Quality Assurance**

### **Validation Testing**
- All FOCUS validation rules pass
- 12 profile/distribution combinations tested
- Cross-column constraint compliance verified

### **Data Quality**
- Realistic service-provider mappings
- Proper null handling for conditional fields
- Meaningful cross-references between columns
- Industry-standard naming conventions

## 🚀 **Benefits**

1. **Complete Coverage** - No generic fallbacks needed
2. **Data Quality** - Industry-realistic generated data
3. **FOCUS Compliance** - 100% validation success
4. **Maintainability** - Specialized, focused generators
5. **Extensibility** - Easy to add new columns or modify logic
6. **Multi-Cloud** - Support for major cloud providers

This architecture provides a solid foundation for generating high-quality, FOCUS-compliant synthetic cost data for testing and development purposes.