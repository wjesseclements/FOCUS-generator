import pandas as pd
import os
from focus_metadata import FOCUS_METADATA

def validate_column(column_name, data, metadata):
    """
    Validate a single column against the FOCUS spec metadata.

    :param column_name: Name of the column to validate.
    :param data: The column data from the DataFrame.
    :param metadata: The metadata for the column from FOCUS_METADATA.
    :return: List of validation errors for the column.
    """
    errors = []

    # Check for required columns
    if metadata.get("required") and data.isnull().all():
        errors.append(f"Column '{column_name}' is required but is completely null.")

    # Check for nullability
    if not metadata.get("allows_nulls", True) and data.isnull().any():
        errors.append(f"Column '{column_name}' contains null values, which are not allowed.")

    # Check for data type
    expected_type = metadata.get("data_type")
    if expected_type:
        if expected_type == "string" and not data.dropna().map(type).eq(str).all():
            errors.append(f"Column '{column_name}' contains non-string values.")
        elif expected_type == "decimal" and not pd.to_numeric(data.dropna(), errors='coerce').notnull().all():
            errors.append(f"Column '{column_name}' contains non-decimal values.")
        elif expected_type == "datetime":
            try:
                pd.to_datetime(data.dropna())
            except Exception:
                errors.append(f"Column '{column_name}' contains invalid datetime values.")

    # Check for allowed values
    allowed_values = metadata.get("allowed_values")
    if allowed_values and not data.dropna().isin(allowed_values).all():
        errors.append(f"Column '{column_name}' contains values not in the allowed set: {allowed_values}")

    return errors


def validate_cur(file_path):
    """
    Validate a FOCUS-conformant CUR dataset against the FOCUS spec metadata.

    :param file_path: Path to the CUR CSV file.
    :return: Validation report.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_csv(file_path)
    report = []

    for column_name, metadata in FOCUS_METADATA.items():
        if column_name not in df.columns:
            if metadata.get("required"):
                report.append(f"Missing required column: {column_name}")
            continue

        # Validate the column
        column_data = df[column_name]
        column_errors = validate_column(column_name, column_data, metadata)
        report.extend(column_errors)

    return report


if __name__ == "__main__":
    # Specify the path to the generated CUR file
    cur_file_path = "synthetic_focus_cur_enterprise_v1_1.csv"

    # Run validation
    print(f"Validating CUR file: {cur_file_path}")
    validation_errors = validate_cur(cur_file_path)

    if validation_errors:
        print("Validation failed with the following errors:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("Validation passed. The CUR dataset adheres to the FOCUS spec.")