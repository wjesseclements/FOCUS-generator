# Test Coverage Report

This document provides an overview of the test coverage for the FOCUS Generator project.

## Backend Test Coverage

### Data Generation Tests (`test_curGen.py`)

- **TestGenerateFocusData**: Tests for the `generate_focus_data` function
  - `test_row_count`: Verifies that the correct number of rows are generated
  - `test_profile_types`: Tests that all profile types work correctly
  - `test_distribution_types`: Tests that all distribution types work correctly
  - `test_required_columns`: Ensures all mandatory columns are present
  - `test_column_data_types`: Verifies column data types are correct

- **TestGenerateValueForColumn**: Tests for the `generate_value_for_column` function
  - `test_charge_category_generation`: Tests charge category generation
  - `test_service_category_by_distribution`: Tests service category generation by distribution
  - `test_billing_period_dates`: Tests billing period date generation

- **TestDistributeBilledCost**: Tests for the `distribute_billed_cost` function
  - `test_cost_distribution`: Tests cost distribution logic

- **TestPostProcess**: Tests for the `post_process` function
  - `test_commitment_discount_nulls`: Tests handling of null commitment discount fields

- **TestApplyDistributionPostProcessing**: Tests for the `apply_distribution_post_processing` function
  - `test_ml_focused_processing`: Tests ML-Focused distribution post-processing
  - `test_data_intensive_processing`: Tests Data-Intensive distribution post-processing
  - `test_media_intensive_processing`: Tests Media-Intensive distribution post-processing

### Validation Tests (`test_validate_cur.py`)

- **TestBasicValidation**: Tests for the basic validation functionality
  - `test_mandatory_columns`: Tests validation of mandatory columns
  - `test_null_constraints`: Tests validation of null constraints
  - `test_allowed_values`: Tests validation of allowed values
  - `test_data_type_validation`: Tests validation of data types
  - `test_cross_column_rules`: Tests validation of cross-column rules
  - `test_valid_data`: Tests validation of valid data

- **TestEnhancedValidation**: Tests for the enhanced validation functionality
  - `test_time_period_validation`: Tests validation of time periods
  - `test_cost_relationships`: Tests validation of cost relationships
  - `test_enhanced_cross_column_rules`: Tests validation of enhanced cross-column rules
  - `test_data_consistency`: Tests validation of data consistency
  - `test_enhanced_validation_integration`: Tests end-to-end enhanced validation

### API Tests (`test_main.py`)

- **TestGenerateCurEndpoint**: Tests for the `/generate-cur` endpoint
  - `test_valid_request`: Tests a valid request
  - `test_invalid_profile`: Tests an invalid profile
  - `test_invalid_distribution`: Tests an invalid distribution
  - `test_invalid_row_count`: Tests an invalid row count
  - `test_default_values`: Tests default values

- **TestGetFileEndpoint**: Tests for the `/files/{filename}` endpoint
  - `test_get_existing_file`: Tests retrieving an existing file
  - `test_get_nonexistent_file`: Tests retrieving a nonexistent file

## Test Coverage Summary

The test suite provides comprehensive coverage of the backend functionality:

1. **Data Generation**: Tests cover the core data generation logic, including profile and distribution-specific behavior.

2. **Validation**: Tests cover both basic and enhanced validation, including column constraints and cross-column rules.

3. **API Endpoints**: Tests cover the API endpoints, including error handling and response formatting.

## Future Test Improvements

1. **Frontend Tests**: Add tests for the React components and user interactions.

2. **Integration Tests**: Add tests that verify the frontend and backend work together correctly.

3. **Performance Tests**: Add tests to measure and ensure acceptable performance with large datasets.

4. **Edge Cases**: Add more tests for edge cases and error conditions.

5. **Code Coverage Analysis**: Implement code coverage analysis to identify untested code paths.