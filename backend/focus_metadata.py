# A dictionary containing all 50 columns of the FOCUS v1.1 spec.
# Each key is a column_name, and each value is a dict with metadata.

FOCUS_METADATA = {
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.1  AvailabilityZone
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "AvailabilityZone": {
        "display_name": "Availability Zone",
        "description": (
            "A provider-assigned identifier for a physically separated and "
            "isolated area within a Region that provides high availability "
            "and fault tolerance."
        ),
        "column_type": "Dimension",
        "feature_level": "Recommended",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.2  BilledCost
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BilledCost": {
        "display_name": "Billed Cost",
        "description": (
            "A charge serving as the basis for invoicing, inclusive of all "
            "reduced rates and discounts while excluding the amortization "
            "of upfront charges (one-time or recurring)."
        ),
        "column_type": "Metric",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.3  BillingAccountId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BillingAccountId": {
        "display_name": "Billing Account ID",
        "description": (
            "The identifier assigned to a billing account by the provider."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": None,
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.4  BillingAccountName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BillingAccountName": {
        "display_name": "Billing Account Name",
        "description": "The display name assigned to a billing account.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": True,  
        "data_type": "string",
        "value_format": None,
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.5  BillingCurrency
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BillingCurrency": {
        "display_name": "Billing Currency",
        "description": "Represents the currency that a charge was billed in.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": "Currency Code Format",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.6  BillingPeriodEnd
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BillingPeriodEnd": {
        "display_name": "Billing Period End",
        "description": "The exclusive end date and time of a billing period.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "datetime",
        "value_format": "Date/Time Format",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.7  BillingPeriodStart
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "BillingPeriodStart": {
        "display_name": "Billing Period Start",
        "description": "The inclusive start date and time of a billing period.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "datetime",
        "value_format": "Date/Time Format",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.8  CapacityReservationId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CapacityReservationId": {
        "display_name": "Capacity Reservation ID",
        "description": (
            "The identifier assigned to a capacity reservation by the provider."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional", 
        "allows_nulls": True,
        "data_type": "string",
        "value_format": None,
        "introduced_version": "1.1",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.9  CapacityReservationStatus
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CapacityReservationStatus": {
        "display_name": "Capacity Reservation Status",
        "description": (
            "Indicates whether the charge represents either consumption of a "
            "capacity reservation or when a capacity reservation is unused."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True, 
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Used", "Unused"],
        "introduced_version": "1.1",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.10 ChargeCategory
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargeCategory": {
        "display_name": "Charge Category",
        "description": (
            "Represents the highest-level classification of a charge based on "
            "the nature of how it is billed."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Usage", "Purchase", "Tax", "Credit", "Adjustment"],
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.11 ChargeClass
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargeClass": {
        "display_name": "Charge Class",
        "description": (
            "Indicates whether the row represents a correction to a "
            "previously invoiced billing period."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Correction"],
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.12 ChargeDescription
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargeDescription": {
        "display_name": "Charge Description",
        "description": (
            "Self-contained summary of the charge’s purpose and price."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": True,  # Should NOT be null, but the spec allows it
        "data_type": "string",
        "value_format": None,
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.13 ChargeFrequency
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargeFrequency": {
        "display_name": "Charge Frequency",
        "description": (
            "Indicates how often a charge will occur (One-Time, Recurring, or Usage-Based)."
        ),
        "column_type": "Dimension",
        "feature_level": "Recommended",
        "allows_nulls": False,  # MUST NOT be null
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["One-Time", "Recurring", "Usage-Based"],
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.14 ChargePeriodEnd
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargePeriodEnd": {
        "display_name": "Charge Period End",
        "description": "The exclusive end date and time of a charge period.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "datetime",
        "value_format": "Date/Time Format",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.15 ChargePeriodStart
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ChargePeriodStart": {
        "display_name": "Charge Period Start",
        "description": "The inclusive start date and time within a charge period.",
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "datetime",
        "value_format": "Date/Time Format",
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.16 CommitmentDiscountCategory
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountCategory": {
        "display_name": "Commitment Discount Category",
        "description": (
            "Indicates whether the commitment discount is based on usage quantity "
            "or cost (aka 'spend')."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Spend", "Usage"],
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.17 CommitmentDiscountId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountId": {
        "display_name": "Commitment Discount ID",
        "description": (
            "The identifier assigned to a commitment discount by the provider."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,   # Null if not associated with a discount
        "data_type": "string",
        "value_format": None,
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.18 CommitmentDiscountName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountName": {
        "display_name": "Commitment Discount Name",
        "description": (
            "The display name assigned to a commitment discount."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # Null if not discount-related or if no display name
        "data_type": "string",
        "value_format": None,
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.19 CommitmentDiscountQuantity
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountQuantity": {
        "display_name": "Commitment Discount Quantity",
        "description": (
            "The amount of a commitment discount purchased or accounted for in "
            "commitment discount related rows, denominated in Commitment "
            "Discount Units."
        ),
        "column_type": "Metric",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "1.1",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.20 CommitmentDiscountStatus
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountStatus": {
        "display_name": "Commitment Discount Status",
        "description": (
            "Indicates whether the charge corresponds with the consumption of "
            "a commitment discount or the unused portion of the committed amount."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Used", "Unused"],
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.21 CommitmentDiscountType
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountType": {
        "display_name": "Commitment Discount Type",
        "description": (
            "A provider-assigned identifier for the type of commitment discount "
            "applied to the row."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # Must be null if CommitmentDiscountId is null
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.22 CommitmentDiscountUnit
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "CommitmentDiscountUnit": {
        "display_name": "Commitment Discount Unit",
        "description": (
            "The provider-specified measurement unit indicating how a provider "
            "measures the Commitment Discount Quantity."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Unit Format",  # from spec
        "introduced_version": "1.1",
        # The spec states that if CommitmentDiscountId is not null & ChargeClass != 'Correction', 
        # this must NOT be null. Otherwise, handle in generation/validation logic.
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.23 ConsumedQuantity
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ConsumedQuantity": {
        "display_name": "Consumed Quantity",
        "description": (
            "The volume of a metered SKU associated with a resource or service used, "
            "based on the Consumed Unit."
        ),
        "column_type": "Metric",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.24 ConsumedUnit
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ConsumedUnit": {
        "display_name": "Consumed Unit",
        "description": (
            "Provider-specified measurement unit indicating how a provider measures "
            "usage of a metered SKU associated with a resource or service."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Unit Format",  # recommended by spec
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.25 ContractedCost
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ContractedCost": {
        "display_name": "Contracted Cost",
        "description": (
            "Cost calculated by multiplying contracted unit price and the "
            "corresponding Pricing Quantity."
        ),
        "column_type": "Metric",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.26 ContractedUnitPrice
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ContractedUnitPrice": {
        "display_name": "Contracted Unit Price",
        "description": (
            "The agreed-upon unit price for a single Pricing Unit of the associated SKU, "
            "inclusive of negotiated discounts if present, while excluding negotiated "
            "commitment discounts or other discounts."
        ),
        "column_type": "Metric",
        "feature_level": "Conditional",  # Only if provider supports negotiated pricing
        "allows_nulls": True,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid non-negative decimal value",
        "introduced_version": "1.0",
        # Additional logic from spec:
        # - MUST NOT be null if ChargeCategory is “Usage” or “Purchase” and ChargeClass != "Correction"
        # - MUST be null if ChargeCategory is “Tax”
        # - MAY be null otherwise
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.27 EffectiveCost
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "EffectiveCost": {
        "display_name": "Effective Cost",
        "description": (
            "The amortized cost of the charge after applying all reduced rates, discounts, "
            "and the applicable portion of relevant, prepaid purchases that covered this charge."
        ),
        "column_type": "Metric",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "0.5",
        # Spec includes logic for amortizing commitment purchases, zero cost for purchases
        # covering future charges, etc.
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.28 InvoiceIssuerName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "InvoiceIssuerName": {
        "display_name": "Invoice Issuer",
        "description": (
            "The name of the entity responsible for invoicing for the resources or services consumed."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.29 ListCost
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ListCost": {
        "display_name": "List Cost",
        "description": (
            "Cost calculated by multiplying the list unit price and the corresponding Pricing Quantity."
        ),
        "column_type": "Metric",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",
        "introduced_version": "1.0-preview",
        # Additional fallback logic if ListUnitPrice is null (e.g., match BilledCost if unrelated)
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.30 ListUnitPrice
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ListUnitPrice": {
        "display_name": "List Unit Price",
        "description": (
            "The suggested provider-published unit price for a single Pricing Unit of the "
            "associated SKU, exclusive of any discounts."
        ),
        "column_type": "Metric",
        "feature_level": "Conditional",  # Only if provider publishes discount-excl. prices
        "allows_nulls": True,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid non-negative decimal value",
        "introduced_version": "1.0-preview",
        # Per spec:
        # - MUST NOT be null if ChargeCategory is “Usage” or “Purchase” and ChargeClass != "Correction"
        # - MUST be null if ChargeCategory is “Tax”
        # - MAY be null otherwise
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.31 PricingCategory
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "PricingCategory": {
        "display_name": "Pricing Category",
        "description": (
            "Describes the pricing model used for a charge at the time of use or purchase."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if provider supports multiple pricing categories
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Allowed values",
        "allowed_values": ["Standard", "Dynamic", "Committed", "Other"],
        "introduced_version": "1.0-preview",
        # Spec logic: 
        # - MUST NOT be null if ChargeClass != "Correction" and (ChargeCategory == "Usage" or "Purchase")
        # - MUST be null if ChargeCategory == "Tax"
        # - MAY be null otherwise
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.32 PricingQuantity
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "PricingQuantity": {
        "display_name": "Pricing Quantity",
        "description": (
            "The volume of a given SKU associated with a resource or service used or purchased, "
            "based on the Pricing Unit."
        ),
        "column_type": "Metric",
        "feature_level": "Mandatory",
        "allows_nulls": True,
        "data_type": "decimal",
        "value_format": "Numeric Format",
        "range": "Any valid decimal value",  # can be negative if ChargeClass == "Correction"
        "introduced_version": "1.0-preview",
        # Spec logic:
        # - MUST NOT be null if ChargeClass != "Correction" and ChargeCategory in ["Usage", "Purchase"]
        # - MUST be null if ChargeCategory == "Tax"
        # - MAY be null otherwise
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.33 PricingUnit
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "PricingUnit": {
        "display_name": "Pricing Unit",
        "description": (
            "Provider-specified measurement unit for determining unit prices, indicating how the "
            "provider rates measured usage and purchase quantities after applying pricing rules."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": True,
        "data_type": "string",
        "value_format": "Unit Format",
        "introduced_version": "1.0-preview",
        # Spec logic:
        # - MUST NOT be null if ChargeClass != "Correction" and ChargeCategory in ["Usage","Purchase"]
        # - MUST be null if ChargeCategory == "Tax"
        # - MAY be null otherwise
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.34 ProviderName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ProviderName": {
        "display_name": "Provider",
        "description": (
            "The name of the entity that made the resources or services available for purchase."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.35 PublisherName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "PublisherName": {
        "display_name": "Publisher",
        "description": (
            "The name of the entity that produced the resources or services that were purchased."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.36 RegionId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "RegionId": {
        "display_name": "Region ID",
        "description": (
            "Provider-assigned identifier for an isolated geographic area where a resource "
            "is provisioned or a service is provided."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # May be null if a resource/service isn't region-specific
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.37 RegionName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "RegionName": {
        "display_name": "Region Name",
        "description": (
            "The name of an isolated geographic area where a resource is provisioned or "
            "a service is provided."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # May be null if no region-specific name applies
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.38 ResourceId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ResourceId": {
        "display_name": "Resource ID",
        "description": (
            "Identifier assigned to a resource by the provider."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if provider bills based on provisioned resources
        "allows_nulls": True,           # Rows may not be tied to a specific resource
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.39 ResourceName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ResourceName": {
        "display_name": "Resource Name",
        "description": (
            "Display name assigned to a resource."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # May be null if no resource or no display name is assigned
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.40 ResourceType
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ResourceType": {
        "display_name": "Resource Type",
        "description": (
            "The kind of resource the charge applies to (e.g., Virtual Machine, "
            "Data Warehouse, Load Balancer)."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",
        "allows_nulls": True,  # Tied to ResourceId; must be null if ResourceId is null
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0-preview",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.41 ServiceCategory
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ServiceCategory": {
        "display_name": "Service Category",
        "description": (
            "Highest-level classification of a service based on the core function of the service."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": "Allowed Values",
        "allowed_values": [
            "AI and Machine Learning",
            "Analytics",
            "Business Applications",
            "Compute",
            "Databases",
            "Developer Tools",
            "Multicloud",
            "Identity",
            "Integration",
            "Internet of Things",
            "Management and Governance",
            "Media",
            "Migration",
            "Mobile",
            "Networking",
            "Security",
            "Storage",
            "Web",
            "Other"
        ],
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.42 ServiceName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ServiceName": {
        "display_name": "Service Name",
        "description": (
            "An offering that can be purchased from a provider (e.g., cloud virtual machine, "
            "SaaS database, professional services from a systems integrator)."
        ),
        "column_type": "Dimension",
        "feature_level": "Mandatory",
        "allows_nulls": False,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.43 ServiceSubcategory
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "ServiceSubcategory": {
        "display_name": "Service Subcategory",
        "description": (
            "Secondary classification of the Service Category for a service based on its core function."
        ),
        "column_type": "Dimension",
        "feature_level": "Recommended",
        "allows_nulls": False,   # MUST NOT be null per spec
        "data_type": "string",
        "value_format": "Allowed Values",
        # The spec provides an extensive mapping of subcategories to each ServiceCategory.
        # We store them all in a single list here. Cross-check logic will ensure
        # that e.g. "AI Platforms" is valid only if ServiceCategory == "AI and Machine Learning."
        "allowed_values": [
            # AI and Machine Learning
            "AI Platforms",
            "Bots",
            "Generative AI",
            "Machine Learning",
            "Natural Language Processing",
            "Other (AI and Machine Learning)",
            # Analytics
            "Analytics Platforms",
            "Business Intelligence",
            "Data Processing",
            "Search",
            "Streaming Analytics",
            "Other (Analytics)",
            # Business Applications
            "Productivity and Collaboration",
            "Other (Business Applications)",
            # Compute
            "Containers",
            "End User Computing",
            "Quantum Compute",
            "Serverless Compute",
            "Virtual Machines",
            "Other (Compute)",
            # Databases
            "Caching",
            "Data Warehouses",
            "Ledger Databases",
            "NoSQL Databases",
            "Relational Databases",
            "Time Series Databases",
            "Other (Databases)",
            # Developer Tools
            "Developer Platforms",
            "Continuous Integration and Deployment",
            "Development Environments",
            "Source Code Management",
            "Quality Assurance",
            "Other (Developer Tools)",
            # Identity
            "Identity and Access Management",
            "Other (Identity)",
            # Integration
            "API Management",
            "Messaging",
            "Workflow Orchestration",
            "Other (Integration)",
            # Internet of Things
            "IoT Analytics",
            "IoT Platforms",
            "Other (Internet of Things)",
            # Management and Governance
            "Architecture",
            "Compliance",
            "Cost Management",
            "Data Governance",
            "Disaster Recovery",
            "Endpoint Management",
            "Observability",
            "Support",
            "Other (Management and Governance)",
            # Media
            "Content Creation",
            "Gaming",
            "Media Streaming",
            "Mixed Reality",
            "Other (Media)",
            # Migration
            "Data Migration",
            "Resource Migration",
            "Other (Migration)",
            # Mobile
            "Other (Mobile)",
            # Multicloud
            "Multicloud Integration",
            "Other (Multicloud)",
            # Networking
            "Application Networking",
            "Content Delivery",
            "Network Connectivity",
            "Network Infrastructure",
            "Network Routing",
            "Network Security",
            "Other (Networking)",
            # Security
            "Secret Management",
            "Security Posture Management",
            "Threat Detection and Response",
            "Other (Security)",
            # Storage
            "Backup Storage",
            "Block Storage",
            "File Storage",
            "Object Storage",
            "Storage Platforms",
            "Other (Storage)",
            # Web
            "Application Platforms",
            "Other (Web)",
            # Other
            "Other (Other)"
        ],
        "introduced_version": "1.1",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.44 SkuId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SkuId": {
        "display_name": "SKU ID",
        "description": (
            "A unique identifier that defines a provider-supported construct for "
            "organizing properties common across one or more SKU Prices."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if the provider publishes a SKU list
        "allows_nulls": True,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0-preview",
        # Spec logic:
        # - MUST NOT be null if ChargeClass != "Correction" and ChargeCategory in ["Usage", "Purchase"]
        # - MUST be null if ChargeCategory == "Tax"
        # - MAY be null otherwise
        # - SkuId MUST equal SkuPriceId if the provider doesn't support a separate SKU construct
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.45 SkuMeter
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SkuMeter": {
        "display_name": "SKU Meter",
        "description": (
            "Describes the functionality being metered or measured by a particular SKU in a charge."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if the provider includes a SkuId
        "allows_nulls": True,  # MUST be null if SkuId is null; SHOULD NOT be null otherwise
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.1",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.46 SkuPriceDetails
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SkuPriceDetails": {
        "display_name": "SKU Price Details",
        "description": (
            "A set of properties of a SKU Price ID which are meaningful and common "
            "to all instances of that SKU Price ID."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if the provider includes a SkuPriceId
        "allows_nulls": True,  # MUST be null if SkuPriceId is null
        "data_type": "json",   # per spec: "data type = JSON"
        "value_format": "Key-Value Format",
        "introduced_version": "1.1",
        # Properties across the same SkuPriceId must remain consistent over time
        # but can be extended with additional keys.
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.47 SkuPriceId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SkuPriceId": {
        "display_name": "SKU Price ID",
        "description": (
            "A unique identifier that defines the unit price used to calculate the charge."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if the provider publishes a SKU price list
        "allows_nulls": True,
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "1.0-preview",
        # Spec logic:
        # - MUST NOT be null if ChargeClass != "Correction" and ChargeCategory in ["Usage","Purchase"]
        # - MUST be null if ChargeCategory == "Tax"
        # - MAY be null otherwise
        # - One SkuPriceId references one SkuId (except for commitment discount flexibility).
        # - If no distinct SkuPriceId, the provider can reuse SkuId here.
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.48 SubAccountId
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SubAccountId": {
        "display_name": "Sub Account ID",
        "description": (
            "An ID assigned to a grouping of resources or services, often used "
            "to manage access and/or cost."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if provider supports sub accounts
        "allows_nulls": True,           # Null if the charge does not apply to a sub account
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.49 SubAccountName
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "SubAccountName": {
        "display_name": "Sub Account Name",
        "description": (
            "A name assigned to a grouping of resources or services, often used "
            "to manage access and/or cost."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if provider supports sub accounts
        "allows_nulls": True,            # Null if the charge does not apply to a sub account
        "data_type": "string",
        "value_format": None,  # <not specified>
        "introduced_version": "0.5",
    },

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #  2.50 Tags
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    "Tags": {
        "display_name": "Tags",
        "description": (
            "The set of tags assigned to tag sources, accounting for potential provider-defined "
            "or user-defined tag evaluations."
        ),
        "column_type": "Dimension",
        "feature_level": "Conditional",  # Only if provider supports user/provider-defined tags
        "allows_nulls": True,            # May be null if tagging is not used or no tags exist
        "data_type": "json",
        "value_format": "Key-Value Format",
        "introduced_version": "1.0-preview",
        # Must contain finalized user- and provider-defined tags, typically in a dict-like format.
    },

}


# Provide helper functions to retrieve metadata for validation or generation purposes.
def get_column_metadata(column_name):
    """
    Retrieve metadata for a specific column.
    """
    return FOCUS_METADATA.get(column_name)
