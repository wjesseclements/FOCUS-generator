# FOCUS Generator Backend

This directory contains the backend code for generating synthetic FOCUS-conformed Cost and Usage Reports (CURs).

## Key Files

- `main.py`: FastAPI application that serves as the API endpoint for generating CURs
- `curGen.py`: Core logic for generating synthetic FOCUS data
- `focus_metadata.py`: Metadata for all 50 columns in the FOCUS v1.1 specification
- `validate_cur.py`: Basic validation logic for FOCUS-conformed data
- `enhanced_validate_cur.py`: Enhanced validation with additional cross-column checks
- `focus_relationships.md`: Documentation of column relationships and constraints
- `focus_audit.md`: Audit of FOCUS v1.1 columns implemented in this project

## FOCUS Implementation

This project implements the FOCUS v1.1 specification, which defines a standardized format for cloud billing data. The implementation includes:

1. **Complete Column Coverage**: All 50 columns from the FOCUS v1.1 specification are implemented.
2. **Metadata Definition**: Each column includes detailed metadata such as display name, description, data type, and constraints.
3. **Validation Logic**: Both basic and enhanced validation to ensure generated data conforms to the specification.
4. **Synthetic Data Generation**: Logic to generate realistic synthetic data for testing and development.

## Enhanced Validation

The enhanced validation (`enhanced_validate_cur.py`) extends the basic validation with additional checks:

1. **Time Period Validation**: Ensures that time periods are logically consistent (e.g., start dates before end dates).
2. **Cost Relationship Validation**: Checks relationships between different cost columns.
3. **Enhanced Cross-Column Rules**: Additional rules not covered in the basic validation.
4. **Data Consistency Checks**: Overall consistency checks for the dataset.

## Usage

To use the enhanced validation:

```python
from backend.enhanced_validate_cur import enhanced_validate_focus_df

# Generate or load your FOCUS data
df = generate_focus_data(row_count=100, profile="Enterprise")

# Validate the data
enhanced_validate_focus_df(df)
```

## Documentation

For more detailed information about the FOCUS implementation:

- `focus_relationships.md`: Explains the relationships and constraints between columns
- `focus_audit.md`: Provides a detailed audit of all 50 columns and their implementation

## Future Improvements

1. **Version Tracking**: Add explicit version tracking to indicate FOCUS v1.1 compliance.
2. **Metadata Enrichment**: Add additional metadata fields for implementation guidance.
3. **Validation Expansion**: Continue expanding validation to cover more edge cases.
4. **Performance Optimization**: Optimize validation for large datasets.
5. **Schema Evolution**: Prepare for future FOCUS specification versions.