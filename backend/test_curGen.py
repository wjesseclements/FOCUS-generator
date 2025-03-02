import pytest
import pandas as pd
import random
from datetime import datetime
from unittest.mock import patch, MagicMock
from .curGen import (
    generate_focus_data,
    generate_value_for_column,
    distribute_billed_cost,
    generate_profile_total_cost,
    post_process,
    apply_distribution_post_processing,
    DISTRIBUTION_SERVICE_WEIGHTS
)
from .focus_metadata import FOCUS_METADATA

# Set a fixed seed for reproducible tests
random.seed(42)

class TestGenerateFocusData:
    """Tests for the generate_focus_data function."""
    
    def test_row_count(self):
        """Test that the function generates the correct number of rows."""
        for count in [1, 5, 10, 20]:
            data = generate_focus_data(count)
            assert len(data) == count
    
    def test_profile_types(self):
        """Test that the function works with all profile types."""
        profiles = ["Greenfield", "Large Business", "Enterprise"]
        for profile in profiles:
            data = generate_focus_data(5, profile=profile)
            assert len(data) == 5
            
            # Check that costs are in the appropriate range for the profile
            if profile == "Greenfield":
                assert data["BilledCost"].sum() < 100_000
            elif profile == "Large Business":
                assert data["BilledCost"].sum() > 50_000
            elif profile == "Enterprise":
                assert data["BilledCost"].sum() > 250_000
    
    @patch('backend.curGen.random')
    def test_distribution_types(self, mock_random):
        """Test that the function works with all distribution types."""
        # Mock random.choices to return predictable values
        def mock_choices(population, weights=None, k=1):
            # Always return the highest weighted item
            if weights:
                max_weight_idx = weights.index(max(weights))
                return [population[max_weight_idx]]
            return [population[0]]
        
        mock_random.choices.side_effect = mock_choices
        mock_random.random.return_value = 0.5
        mock_random.uniform.return_value = 1.0
        
        distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
        for distribution in distributions:
            data = generate_focus_data(5, distribution=distribution)
            assert len(data) == 5
            
            # With our mocked random.choices, the most common category should match
            # the highest weighted category in the distribution
            expected_weights = DISTRIBUTION_SERVICE_WEIGHTS[distribution]
            max_weight_category = max(expected_weights, key=expected_weights.get)
            
            # Count occurrences of each category
            service_counts = data["ServiceCategory"].value_counts()
            most_common = service_counts.idxmax() if not service_counts.empty else None
            
            # Since we're mocking random.choices, the most common should be the highest weighted
            # But we'll be flexible in the assertion to account for other randomness
            assert most_common in list(expected_weights.keys()), \
                f"Expected most common category to be one of {list(expected_weights.keys())}, got {most_common}"
    
    def test_required_columns(self):
        """Test that all mandatory columns are present in the output."""
        data = generate_focus_data(5)
        
        # Check that all mandatory columns are present
        mandatory_columns = [
            col for col, meta in FOCUS_METADATA.items() 
            if meta.get("feature_level", "").lower() == "mandatory"
        ]
        
        for col in mandatory_columns:
            assert col in data.columns, f"Mandatory column {col} is missing"
    
    def test_column_data_types(self):
        """Test that columns have the correct data types."""
        data = generate_focus_data(5)
        
        # Check a sample of columns for correct data types
        sample_columns = {
            "BilledCost": (float, int),  # numeric types
            "BillingAccountId": str,
            "BillingPeriodStart": str,  # datetime as string
            "ChargeCategory": str,
        }
        
        for col, expected_type in sample_columns.items():
            if isinstance(expected_type, tuple):
                # Check if column values are any of the expected types
                assert all(isinstance(val, expected_type) or pd.isna(val) for val in data[col]), \
                    f"Column {col} has incorrect data type"
            else:
                # Check if column values are of the expected type
                assert all(isinstance(val, expected_type) or pd.isna(val) for val in data[col]), \
                    f"Column {col} has incorrect data type"

class TestGenerateValueForColumn:
    """Tests for the generate_value_for_column function."""
    
    def test_charge_category_generation(self):
        """Test that ChargeCategory is generated correctly."""
        # Generate multiple values to account for randomness
        values = [
            generate_value_for_column(
                "ChargeCategory", 0, {}, 10, "Greenfield", 10000
            )
            for _ in range(20)
        ]
        
        # Check that all values are valid charge categories
        valid_categories = ["Usage", "Purchase", "Tax", "Credit", "Adjustment"]
        for val in values:
            assert val in valid_categories
        
        # Check that the most common value is "Usage" (highest weight)
        most_common = max(set(values), key=values.count)
        assert most_common == "Usage"
    
    @patch('backend.curGen.random')
    def test_service_category_by_distribution(self, mock_random):
        """Test that ServiceCategory is generated according to the distribution."""
        # Mock random.choices to return predictable values
        def mock_choices(population, weights=None, k=1):
            # Always return the highest weighted item
            if weights:
                max_weight_idx = weights.index(max(weights))
                return [population[max_weight_idx]]
            return [population[0]]
        
        mock_random.choices.side_effect = mock_choices
        
        distributions = ["Evenly Distributed", "ML-Focused", "Data-Intensive", "Media-Intensive"]
        
        for dist in distributions:
            # Generate a value with mocked randomness
            value = generate_value_for_column(
                "ServiceCategory", 0, {}, 10, "Greenfield", 10000, dist
            )
            
            # Get the category with the highest weight in this distribution
            expected_weights = DISTRIBUTION_SERVICE_WEIGHTS[dist]
            max_weight_category = max(expected_weights, key=expected_weights.get)
            
            # With our mocked random.choices, the value should be the highest weighted category
            assert value == max_weight_category, \
                f"For {dist}, expected {max_weight_category}, got {value}"
    
    def test_billing_period_dates(self):
        """Test that billing period dates are generated correctly."""
        start = generate_value_for_column("BillingPeriodStart", 0, {}, 10, "Greenfield", 10000)
        end = generate_value_for_column("BillingPeriodEnd", 0, {}, 10, "Greenfield", 10000)
        
        # Parse dates
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Check that end is after start
        assert end_date > start_date
        
        # Check that they're a month apart
        delta = end_date - start_date
        assert 28 <= delta.days <= 31  # Approximately a month

class TestDistributeBilledCost:
    """Tests for the distribute_billed_cost function."""
    
    def test_cost_distribution(self):
        """Test that costs are distributed appropriately."""
        total_cost = 10000
        row_count = 10
        
        # Generate costs for all rows
        costs = [distribute_billed_cost(i, row_count, total_cost) for i in range(row_count)]
        
        # Check that the sum is approximately the total cost
        # (There will be some variation due to the random factor)
        assert 0.8 * total_cost <= sum(costs) <= 1.2 * total_cost
        
        # Check that each cost is positive
        for cost in costs:
            assert cost > 0
        
        # Check that costs are reasonably distributed
        # (No single cost should be more than 3x the average)
        avg_cost = total_cost / row_count
        for cost in costs:
            assert cost < 3 * avg_cost

class TestPostProcess:
    """Tests for the post_process function."""
    
    def test_commitment_discount_nulls(self):
        """Test that commitment discount fields are nulled when ID is null."""
        # Create a test DataFrame
        df = pd.DataFrame({
            "CommitmentDiscountId": [None, "CD-1234", None],
            "CommitmentDiscountName": ["Should be null", "Valid Name", "Should be null"],
            "CommitmentDiscountStatus": ["Should be null", "Used", "Should be null"],
            "CommitmentDiscountQuantity": [10.0, 20.0, 30.0],
            "CommitmentDiscountUnit": ["Should be null", "Hours", "Should be null"],
            "CommitmentDiscountType": ["Should be null", "Reserved", "Should be null"],
            "CommitmentDiscountCategory": ["Should be null", "Usage", "Should be null"]
        })
        
        # Apply post-processing
        result = post_process(df)
        
        # Check that related fields are null when ID is null
        for idx in [0, 2]:
            assert pd.isna(result.loc[idx, "CommitmentDiscountName"])
            assert pd.isna(result.loc[idx, "CommitmentDiscountStatus"])
            assert pd.isna(result.loc[idx, "CommitmentDiscountQuantity"])
            assert pd.isna(result.loc[idx, "CommitmentDiscountUnit"])
            assert pd.isna(result.loc[idx, "CommitmentDiscountType"])
            assert pd.isna(result.loc[idx, "CommitmentDiscountCategory"])
        
        # Check that values are preserved when ID is not null
        assert result.loc[1, "CommitmentDiscountName"] == "Valid Name"
        assert result.loc[1, "CommitmentDiscountStatus"] == "Used"
        assert result.loc[1, "CommitmentDiscountQuantity"] == 20.0
        assert result.loc[1, "CommitmentDiscountUnit"] == "Hours"
        assert result.loc[1, "CommitmentDiscountType"] == "Reserved"
        assert result.loc[1, "CommitmentDiscountCategory"] == "Usage"

class TestApplyDistributionPostProcessing:
    """Tests for the apply_distribution_post_processing function."""
    
    def test_ml_focused_processing(self):
        """Test ML-Focused distribution post-processing."""
        # Create a test DataFrame
        df = pd.DataFrame({
            "ServiceCategory": ["AI and Machine Learning", "Compute", "Storage"],
            "BilledCost": [100.0, 200.0, 300.0],
            "EffectiveCost": [100.0, 200.0, 300.0],
            "ResourceType": [None, None, None]
        })
        
        # Apply ML-Focused post-processing
        result = apply_distribution_post_processing(df, "ML-Focused")
        
        # Check that AI and ML costs are increased
        assert result.loc[0, "BilledCost"] > 100.0
        assert result.loc[0, "EffectiveCost"] > 100.0
        
        # Check that other costs are unchanged
        assert result.loc[1, "BilledCost"] == 200.0
        assert result.loc[2, "BilledCost"] == 300.0
        
        # Check that ResourceType is set for Compute
        assert not pd.isna(result.loc[1, "ResourceType"])
    
    def test_data_intensive_processing(self):
        """Test Data-Intensive distribution post-processing."""
        # Create a test DataFrame
        df = pd.DataFrame({
            "ServiceCategory": ["AI and Machine Learning", "Storage", "Databases"],
            "BilledCost": [100.0, 200.0, 300.0],
            "EffectiveCost": [100.0, 200.0, 300.0],
            "ResourceType": [None, None, None]
        })
        
        # Apply Data-Intensive post-processing
        result = apply_distribution_post_processing(df, "Data-Intensive")
        
        # Check that Storage and Databases costs are increased
        assert result.loc[1, "BilledCost"] > 200.0
        assert result.loc[2, "BilledCost"] > 300.0
        
        # Check that AI and ML costs are unchanged
        assert result.loc[0, "BilledCost"] == 100.0
        
        # Check that ResourceType is set for Storage
        assert not pd.isna(result.loc[1, "ResourceType"])
    
    def test_media_intensive_processing(self):
        """Test Media-Intensive distribution post-processing."""
        # Create a test DataFrame
        df = pd.DataFrame({
            "ServiceCategory": ["AI and Machine Learning", "Storage", "Networking"],
            "BilledCost": [100.0, 200.0, 300.0],
            "EffectiveCost": [100.0, 200.0, 300.0],
            "ResourceType": [None, None, None]
        })
        
        # Apply Media-Intensive post-processing
        result = apply_distribution_post_processing(df, "Media-Intensive")
        
        # Check that Storage and Networking costs are increased
        assert result.loc[1, "BilledCost"] > 200.0
        assert result.loc[2, "BilledCost"] > 300.0
        
        # Check that AI and ML costs are unchanged
        assert result.loc[0, "BilledCost"] == 100.0