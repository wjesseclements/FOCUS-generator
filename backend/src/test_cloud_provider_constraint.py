"""
Test to verify that cloud provider constraint is properly enforced.

This test ensures that when a specific cloud provider is selected,
all generated data is consistent with that provider choice.
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from curGen import generate_focus_data


class TestCloudProviderConstraint:
    """Test that cloud provider constraint is enforced across all generated data."""
    
    def test_aws_only_generation(self):
        """Test that selecting AWS only generates AWS services."""
        df = generate_focus_data(
            row_count=50, 
            profile="Greenfield", 
            distribution="Evenly Distributed", 
            cloud_provider="AWS"
        )
        
        # Check ServiceName column - should only contain AWS services
        if "ServiceName" in df.columns:
            service_names = df["ServiceName"].dropna().unique()
            for service in service_names:
                assert any(aws_indicator in service for aws_indicator in ["Amazon", "AWS"]), \
                    f"Non-AWS service found: {service}"
        
        # Check ProviderName column - should only be AWS
        if "ProviderName" in df.columns:
            provider_names = df["ProviderName"].dropna().unique()
            for provider in provider_names:
                assert provider == "AWS", f"Non-AWS provider found: {provider}"
        
        # Check PublisherName column - should only be AWS-related
        if "PublisherName" in df.columns:
            publisher_names = df["PublisherName"].dropna().unique()
            for publisher in publisher_names:
                assert any(aws_indicator in publisher for aws_indicator in ["Amazon", "AWS", "Third Party"]), \
                    f"Non-AWS publisher found: {publisher}"
        
        # Check RegionId column - should only be AWS regions
        if "RegionId" in df.columns:
            region_ids = df["RegionId"].dropna().unique()
            for region in region_ids:
                assert any(prefix in region for prefix in ["us-", "eu-", "ap-", "ca-"]), \
                    f"Non-AWS region found: {region}"
    
    def test_azure_only_generation(self):
        """Test that selecting Azure only generates Azure services."""
        df = generate_focus_data(
            row_count=50, 
            profile="Greenfield", 
            distribution="Evenly Distributed", 
            cloud_provider="AZURE"
        )
        
        # Check ServiceName column - should only contain Azure services
        if "ServiceName" in df.columns:
            service_names = df["ServiceName"].dropna().unique()
            for service in service_names:
                assert "Azure" in service, f"Non-Azure service found: {service}"
        
        # Check ProviderName column - should only be Microsoft Azure
        if "ProviderName" in df.columns:
            provider_names = df["ProviderName"].dropna().unique()
            for provider in provider_names:
                assert provider == "Microsoft Azure", f"Non-Azure provider found: {provider}"
        
        # Check PublisherName column - should only be Azure-related
        if "PublisherName" in df.columns:
            publisher_names = df["PublisherName"].dropna().unique()
            for publisher in publisher_names:
                assert any(azure_indicator in publisher for azure_indicator in ["Microsoft", "Azure", "Third Party"]), \
                    f"Non-Azure publisher found: {publisher}"
        
        # Check RegionId column - should only be Azure regions
        if "RegionId" in df.columns:
            region_ids = df["RegionId"].dropna().unique()
            for region in region_ids:
                assert any(region_part in region.lower() for region_part in ["east", "west", "central", "north", "south"]), \
                    f"Non-Azure region found: {region}"
    
    def test_gcp_only_generation(self):
        """Test that selecting GCP only generates GCP services."""
        df = generate_focus_data(
            row_count=50, 
            profile="Greenfield", 
            distribution="Evenly Distributed", 
            cloud_provider="GCP"
        )
        
        # Check ServiceName column - should only contain GCP services
        if "ServiceName" in df.columns:
            service_names = df["ServiceName"].dropna().unique()
            for service in service_names:
                assert any(gcp_indicator in service for gcp_indicator in ["Google", "GCP"]), \
                    f"Non-GCP service found: {service}"
        
        # Check ProviderName column - should only be Google Cloud
        if "ProviderName" in df.columns:
            provider_names = df["ProviderName"].dropna().unique()
            for provider in provider_names:
                assert provider == "Google Cloud", f"Non-GCP provider found: {provider}"
        
        # Check PublisherName column - should only be GCP-related
        if "PublisherName" in df.columns:
            publisher_names = df["PublisherName"].dropna().unique()
            for publisher in publisher_names:
                assert any(gcp_indicator in publisher for gcp_indicator in ["Google", "Third Party"]), \
                    f"Non-GCP publisher found: {publisher}"
        
        # Check RegionId column - should only be GCP regions
        if "RegionId" in df.columns:
            region_ids = df["RegionId"].dropna().unique()
            for region in region_ids:
                assert any(prefix in region for prefix in ["us-", "europe-", "asia-"]), \
                    f"Non-GCP region found: {region}"
    
    def test_cross_provider_consistency(self):
        """Test that all provider-related columns are consistent within each row."""
        df = generate_focus_data(
            row_count=30, 
            profile="Greenfield", 
            distribution="Evenly Distributed", 
            cloud_provider="AWS"
        )
        
        for index, row in df.iterrows():
            service_name = row.get("ServiceName", "")
            provider_name = row.get("ProviderName", "")
            publisher_name = row.get("PublisherName", "")
            region_id = row.get("RegionId", "")
            
            # If we have AWS provider, all other fields should be AWS-related
            if provider_name == "AWS":
                if service_name and service_name != "":
                    assert any(aws_indicator in service_name for aws_indicator in ["Amazon", "AWS"]), \
                        f"Row {index}: AWS provider but non-AWS service: {service_name}"
                
                if publisher_name and publisher_name != "":
                    assert any(aws_indicator in publisher_name for aws_indicator in ["Amazon", "AWS", "Third Party"]), \
                        f"Row {index}: AWS provider but non-AWS publisher: {publisher_name}"
                
                if region_id and region_id != "":
                    assert any(prefix in region_id for prefix in ["us-", "eu-", "ap-", "ca-"]), \
                        f"Row {index}: AWS provider but non-AWS region: {region_id}"
    
    def test_different_distributions_maintain_constraint(self):
        """Test that cloud provider constraint is maintained across different distributions."""
        distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
        
        for distribution in distributions:
            df = generate_focus_data(
                row_count=20, 
                profile="Greenfield", 
                distribution=distribution, 
                cloud_provider="GCP"
            )
            
            # Check that all services are GCP services regardless of distribution
            if "ServiceName" in df.columns:
                service_names = df["ServiceName"].dropna().unique()
                for service in service_names:
                    assert any(gcp_indicator in service for gcp_indicator in ["Google", "GCP"]), \
                        f"Distribution {distribution}: Non-GCP service found: {service}"
    
    def test_invalid_cloud_provider_defaults_to_aws(self):
        """Test that invalid cloud provider defaults to AWS."""
        df = generate_focus_data(
            row_count=10, 
            profile="Greenfield", 
            distribution="Evenly Distributed", 
            cloud_provider="INVALID_PROVIDER"
        )
        
        # Should default to AWS
        if "ProviderName" in df.columns:
            provider_names = df["ProviderName"].dropna().unique()
            for provider in provider_names:
                assert provider == "AWS", f"Invalid provider should default to AWS, but got: {provider}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])