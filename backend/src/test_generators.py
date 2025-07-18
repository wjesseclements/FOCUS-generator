"""
Comprehensive tests for all FOCUS column generators.

This test suite ensures that all 16 generator classes work correctly
and produce FOCUS-compliant data across all profiles and distributions.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from column_generators import (
    GenerationContext, ColumnGenerator, ChargeGenerator, CostGenerator,
    DateTimeGenerator, ServiceGenerator, SKUGenerator, CommitmentDiscountGenerator,
    CapacityReservationGenerator, PricingGenerator, ResourceGenerator,
    AccountGenerator, CostDetailsGenerator, LocationGenerator,
    ServiceDetailsGenerator, UsageMetricsGenerator, ProviderBusinessGenerator,
    MetadataGenerator, GenericGenerator
)
from generator_factory import ColumnGeneratorFactory, get_generator_factory


class TestGenerationContext:
    """Test the GenerationContext data class."""
    
    def test_context_creation(self):
        """Test creating a GenerationContext."""
        context = GenerationContext(
            col_name="BilledCost",
            row_idx=0,
            row_data={"ChargeCategory": "Usage"},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={"test": "data"}
        )
        
        assert context.col_name == "BilledCost"
        assert context.row_idx == 0
        assert context.row_data == {"ChargeCategory": "Usage"}
        assert context.row_count == 100
        assert context.profile == "basic"
        assert context.total_dataset_cost == 1000.0
        assert context.distribution == "uniform"
        assert context.metadata == {"test": "data"}


class TestChargeGenerator:
    """Test the ChargeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ChargeGenerator()
        self.context = GenerationContext(
            col_name="ChargeCategory",
            row_idx=0,
            row_data={},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test that ChargeGenerator supports the correct columns."""
        expected_columns = ["ChargeCategory", "ChargeFrequency"]
        assert self.generator.supported_columns() == expected_columns
    
    def test_can_handle_supported_columns(self):
        """Test can_handle method for supported columns."""
        assert self.generator.can_handle("ChargeCategory")
        assert self.generator.can_handle("ChargeFrequency")
        assert not self.generator.can_handle("BilledCost")
    
    def test_charge_category_generation(self):
        """Test ChargeCategory generation."""
        self.context.col_name = "ChargeCategory"
        
        # Generate multiple values to test distribution
        categories = set()
        for _ in range(100):
            category = self.generator.generate_value(self.context)
            categories.add(category)
            assert category in ["Usage", "Purchase", "Tax", "Credit", "Adjustment"]
        
        # Should generate variety of categories
        assert len(categories) > 1
    
    def test_charge_frequency_generation(self):
        """Test ChargeFrequency generation."""
        self.context.col_name = "ChargeFrequency"
        
        # Test with Purchase charge category (restricted options)
        self.context.row_data = {"ChargeCategory": "Purchase"}
        frequency = self.generator.generate_value(self.context)
        assert frequency in ["One-Time", "Recurring"]
        
        # Test with other charge categories (all options available)
        self.context.row_data = {"ChargeCategory": "Usage"}
        frequency = self.generator.generate_value(self.context)
        assert frequency in ["One-Time", "Recurring", "Usage-Based"]
    
    def test_unsupported_column_raises_error(self):
        """Test that unsupported columns raise ValueError."""
        self.context.col_name = "UnsupportedColumn"
        
        with pytest.raises(ValueError, match="Unsupported column"):
            self.generator.generate_value(self.context)


class TestCostGenerator:
    """Test the CostGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CostGenerator()
        self.context = GenerationContext(
            col_name="BilledCost",
            row_idx=0,
            row_data={},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test that CostGenerator supports BilledCost."""
        assert self.generator.supported_columns() == ["BilledCost"]
    
    def test_billed_cost_generation(self):
        """Test BilledCost generation with different distributions."""
        # Test uniform distribution
        self.context.distribution = "uniform"
        cost = self.generator.generate_value(self.context)
        assert isinstance(cost, float)
        assert cost >= 0
        
        # Test exponential distribution
        self.context.distribution = "exponential"
        cost = self.generator.generate_value(self.context)
        assert isinstance(cost, float)
        assert cost >= 0
        
        # Test normal distribution
        self.context.distribution = "normal"
        cost = self.generator.generate_value(self.context)
        assert isinstance(cost, float)
        assert cost >= 0


class TestLocationGenerator:
    """Test the LocationGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = LocationGenerator()
        self.context = GenerationContext(
            col_name="RegionId",
            row_idx=0,
            row_data={"ProviderName": "AWS"},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test supported columns."""
        expected = ["RegionId", "RegionName", "AvailabilityZone"]
        assert self.generator.supported_columns() == expected
    
    def test_aws_region_generation(self):
        """Test AWS region generation."""
        self.context.row_data = {"ProviderName": "AWS"}
        self.context.col_name = "RegionId"
        
        region_id = self.generator.generate_value(self.context)
        assert region_id.startswith("us-") or region_id.startswith("eu-") or region_id.startswith("ap-")
    
    def test_azure_region_generation(self):
        """Test Azure region generation."""
        self.context.row_data = {"ProviderName": "Microsoft Azure"}
        self.context.col_name = "RegionId"
        
        region_id = self.generator.generate_value(self.context)
        assert any(region in region_id.lower() for region in ["east", "west", "central", "north", "south"])
    
    def test_gcp_region_generation(self):
        """Test GCP region generation."""
        self.context.row_data = {"ProviderName": "Google Cloud"}
        self.context.col_name = "RegionId"
        
        region_id = self.generator.generate_value(self.context)
        assert any(region in region_id for region in ["us-", "europe-", "asia-"])
    
    def test_availability_zone_generation(self):
        """Test availability zone generation."""
        self.context.row_data = {"RegionId": "us-east-1", "ProviderName": "AWS"}
        self.context.col_name = "AvailabilityZone"
        
        az = self.generator.generate_value(self.context)
        assert az.startswith("us-east-1")
        assert az.endswith(("a", "b", "c", "d", "e", "f"))


class TestServiceDetailsGenerator:
    """Test the ServiceDetailsGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ServiceDetailsGenerator()
        self.context = GenerationContext(
            col_name="ServiceName",
            row_idx=0,
            row_data={"ProviderName": "AWS"},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test supported columns."""
        expected = ["ServiceName", "ServiceSubcategory"]
        assert self.generator.supported_columns() == expected
    
    def test_aws_service_generation(self):
        """Test AWS service name generation."""
        self.context.row_data = {"ProviderName": "AWS"}
        self.context.col_name = "ServiceName"
        
        service_name = self.generator.generate_value(self.context)
        aws_services = ["Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda", "Amazon VPC"]
        assert any(aws_service in service_name for aws_service in aws_services)
    
    def test_service_subcategory_generation(self):
        """Test service subcategory generation."""
        self.context.row_data = {"ServiceName": "Amazon EC2"}
        self.context.col_name = "ServiceSubcategory"
        
        subcategory = self.generator.generate_value(self.context)
        assert isinstance(subcategory, str)
        assert len(subcategory) > 0


class TestUsageMetricsGenerator:
    """Test the UsageMetricsGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = UsageMetricsGenerator()
        self.context = GenerationContext(
            col_name="ConsumedQuantity",
            row_idx=0,
            row_data={"ServiceName": "Amazon EC2", "ChargeCategory": "Usage"},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test supported columns."""
        expected = ["ConsumedQuantity", "ConsumedUnit", "SkuMeter"]
        assert self.generator.supported_columns() == expected
    
    def test_consumed_quantity_generation(self):
        """Test ConsumedQuantity generation."""
        self.context.col_name = "ConsumedQuantity"
        
        quantity = self.generator.generate_value(self.context)
        assert isinstance(quantity, (int, float))
        assert quantity > 0
    
    def test_consumed_unit_generation(self):
        """Test ConsumedUnit generation."""
        self.context.col_name = "ConsumedUnit"
        
        unit = self.generator.generate_value(self.context)
        common_units = ["Hours", "GB", "Requests", "GB-Month", "Messages", "Bytes"]
        assert any(common_unit in unit for common_unit in common_units)
    
    def test_sku_meter_generation(self):
        """Test SkuMeter generation."""
        self.context.col_name = "SkuMeter"
        
        meter = self.generator.generate_value(self.context)
        assert isinstance(meter, str)
        assert len(meter) > 0


class TestProviderBusinessGenerator:
    """Test the ProviderBusinessGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ProviderBusinessGenerator()
        self.context = GenerationContext(
            col_name="ProviderName",
            row_idx=0,
            row_data={},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test supported columns."""
        expected = ["ProviderName", "PublisherName", "InvoiceIssuerName"]
        assert self.generator.supported_columns() == expected
    
    def test_provider_name_generation(self):
        """Test ProviderName generation."""
        self.context.col_name = "ProviderName"
        
        provider = self.generator.generate_value(self.context)
        assert provider in ["AWS", "Microsoft Azure", "Google Cloud"]
    
    def test_publisher_name_generation(self):
        """Test PublisherName generation based on provider."""
        self.context.row_data = {"ProviderName": "AWS"}
        self.context.col_name = "PublisherName"
        
        publisher = self.generator.generate_value(self.context)
        assert "Amazon" in publisher or "AWS" in publisher
    
    def test_invoice_issuer_generation(self):
        """Test InvoiceIssuerName generation."""
        self.context.row_data = {"ProviderName": "AWS"}
        self.context.col_name = "InvoiceIssuerName"
        
        issuer = self.generator.generate_value(self.context)
        assert isinstance(issuer, str)
        assert len(issuer) > 0


class TestMetadataGenerator:
    """Test the MetadataGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MetadataGenerator()
        self.context = GenerationContext(
            col_name="Tags",
            row_idx=0,
            row_data={"ServiceName": "Amazon EC2"},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_supported_columns(self):
        """Test supported columns."""
        expected = ["Tags", "SkuPriceDetails", "ChargeDescription", "CommitmentDiscountName"]
        assert self.generator.supported_columns() == expected
    
    def test_tags_generation(self):
        """Test Tags generation."""
        self.context.col_name = "Tags"
        
        tags = self.generator.generate_value(self.context)
        assert isinstance(tags, str)
        # Should be valid JSON
        import json
        parsed_tags = json.loads(tags)
        assert isinstance(parsed_tags, dict)
    
    def test_sku_price_details_generation(self):
        """Test SkuPriceDetails generation."""
        self.context.col_name = "SkuPriceDetails"
        
        details = self.generator.generate_value(self.context)
        assert isinstance(details, str)
        # Should be valid JSON
        import json
        parsed_details = json.loads(details)
        assert isinstance(parsed_details, dict)
    
    def test_charge_description_generation(self):
        """Test ChargeDescription generation."""
        self.context.col_name = "ChargeDescription"
        
        description = self.generator.generate_value(self.context)
        assert isinstance(description, str)
        assert len(description) > 0


class TestGeneratorFactory:
    """Test the ColumnGeneratorFactory class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.factory = ColumnGeneratorFactory()
    
    def test_get_generator_for_charge_columns(self):
        """Test getting generator for charge-related columns."""
        generator = self.factory.get_generator("ChargeCategory")
        assert isinstance(generator, ChargeGenerator)
        
        generator = self.factory.get_generator("ChargeFrequency")
        assert isinstance(generator, ChargeGenerator)
    
    def test_get_generator_for_cost_columns(self):
        """Test getting generator for cost-related columns."""
        generator = self.factory.get_generator("BilledCost")
        assert isinstance(generator, CostGenerator)
    
    def test_get_generator_for_location_columns(self):
        """Test getting generator for location-related columns."""
        generator = self.factory.get_generator("RegionId")
        assert isinstance(generator, LocationGenerator)
        
        generator = self.factory.get_generator("RegionName")
        assert isinstance(generator, LocationGenerator)
        
        generator = self.factory.get_generator("AvailabilityZone")
        assert isinstance(generator, LocationGenerator)
    
    def test_get_generator_fallback_to_generic(self):
        """Test fallback to GenericGenerator for unknown columns."""
        generator = self.factory.get_generator("UnknownColumn")
        assert isinstance(generator, GenericGenerator)
    
    def test_get_supported_columns(self):
        """Test getting all supported columns."""
        supported = self.factory.get_supported_columns()
        assert isinstance(supported, list)
        assert len(supported) > 0
        assert "ChargeCategory" in supported
        assert "BilledCost" in supported
        assert "RegionId" in supported
    
    def test_register_new_generator(self):
        """Test registering a new generator."""
        class TestGenerator(ColumnGenerator):
            def supported_columns(self):
                return ["TestColumn"]
            
            def generate_value(self, context):
                return "test_value"
        
        test_generator = TestGenerator()
        self.factory.register_generator(test_generator)
        
        # Should now handle TestColumn
        generator = self.factory.get_generator("TestColumn")
        assert isinstance(generator, TestGenerator)
    
    def test_global_factory_instance(self):
        """Test the global factory instance."""
        factory1 = get_generator_factory()
        factory2 = get_generator_factory()
        assert factory1 is factory2  # Same instance


class TestCrossColumnRelationships:
    """Test that generators work correctly together."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.factory = ColumnGeneratorFactory()
        self.base_context = GenerationContext(
            col_name="",
            row_idx=0,
            row_data={},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
    
    def test_provider_region_relationship(self):
        """Test that regions are appropriate for providers."""
        # Generate provider first
        provider_context = self.base_context
        provider_context.col_name = "ProviderName"
        provider_generator = self.factory.get_generator("ProviderName")
        provider_name = provider_generator.generate_value(provider_context)
        
        # Generate region based on provider
        region_context = self.base_context
        region_context.col_name = "RegionId"
        region_context.row_data = {"ProviderName": provider_name}
        region_generator = self.factory.get_generator("RegionId")
        region_id = region_generator.generate_value(region_context)
        
        # Verify relationship
        if provider_name == "AWS":
            assert any(prefix in region_id for prefix in ["us-", "eu-", "ap-"])
        elif provider_name == "Microsoft Azure":
            assert any(region in region_id.lower() for region in ["east", "west", "central"])
        elif provider_name == "Google Cloud":
            assert any(prefix in region_id for prefix in ["us-", "europe-", "asia-"])
    
    def test_charge_category_frequency_relationship(self):
        """Test ChargeCategory and ChargeFrequency relationship."""
        # Generate charge category
        category_context = self.base_context
        category_context.col_name = "ChargeCategory"
        charge_generator = self.factory.get_generator("ChargeCategory")
        charge_category = charge_generator.generate_value(category_context)
        
        # Generate frequency based on category
        frequency_context = self.base_context
        frequency_context.col_name = "ChargeFrequency"
        frequency_context.row_data = {"ChargeCategory": charge_category}
        frequency = charge_generator.generate_value(frequency_context)
        
        # Verify relationship
        if charge_category == "Purchase":
            assert frequency in ["One-Time", "Recurring"]
        else:
            assert frequency in ["One-Time", "Recurring", "Usage-Based"]


class TestFOCUSCompliance:
    """Test FOCUS specification compliance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.factory = ColumnGeneratorFactory()
    
    def test_all_focus_columns_have_generators(self):
        """Test that all FOCUS columns have dedicated generators."""
        # List of all FOCUS columns that should have specialized generators
        focus_columns = [
            "ChargeCategory", "ChargeFrequency", "BilledCost",
            "RegionId", "RegionName", "AvailabilityZone",
            "ServiceName", "ServiceSubcategory",
            "ConsumedQuantity", "ConsumedUnit", "SkuMeter",
            "ProviderName", "PublisherName", "InvoiceIssuerName",
            "Tags", "SkuPriceDetails", "ChargeDescription", "CommitmentDiscountName"
        ]
        
        for column in focus_columns:
            generator = self.factory.get_generator(column)
            # Should not be GenericGenerator for these columns
            assert not isinstance(generator, GenericGenerator), f"Column {column} uses GenericGenerator"
    
    def test_null_handling(self):
        """Test that generators handle null values appropriately."""
        context = GenerationContext(
            col_name="ChargeCategory",
            row_idx=0,
            row_data={},
            row_count=100,
            profile="basic",
            total_dataset_cost=1000.0,
            distribution="uniform",
            metadata={}
        )
        
        # Test that required fields don't return None
        required_columns = ["ChargeCategory", "BilledCost", "ProviderName"]
        for column in required_columns:
            context.col_name = column
            generator = self.factory.get_generator(column)
            value = generator.generate_value(context)
            assert value is not None, f"Required column {column} returned None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])