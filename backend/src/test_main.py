import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from .main import app

# Create a test client
client = TestClient(app)

class TestGenerateCurEndpoint:
    """Tests for the /generate-cur endpoint."""
    
    @patch('boto3.client')  # Patch at the module level, not in main
    @patch('backend.main.generate_focus_data')
    @patch('backend.main.validate_focus_df')
    def test_valid_request(self, mock_validate, mock_generate, mock_boto3):
        """Test that a valid request returns a successful response."""
        # Mock the generate_focus_data function to return a DataFrame
        mock_df = MagicMock()
        mock_df.to_csv.return_value = "csv,data"
        mock_generate.return_value = mock_df
        
        # Mock boto3 client
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Create a valid request payload
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed",
            "row_count": 5
        }
        
        # Set environment variable for bucket name
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket"}):
            # Make the request
            response = client.post("/generate-cur", json=payload)
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the response contains the expected fields
        data = response.json()
        assert "message" in data
        assert "url" in data
        
        # Check that the generate_focus_data function was called with the correct arguments
        mock_generate.assert_called_once_with(row_count=5, profile="Greenfield", distribution="Evenly Distributed")
    
    @patch('boto3.client')  # Patch at the module level
    @patch('backend.main.generate_focus_data')
    @patch('backend.main.validate_focus_df')
    def test_default_values(self, mock_validate, mock_generate, mock_boto3):
        """Test that default values are used when not provided."""
        # Mock the generate_focus_data function to return a DataFrame
        mock_df = MagicMock()
        mock_df.to_csv.return_value = "csv,data"
        mock_generate.return_value = mock_df
        
        # Mock boto3 client
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Create a minimal request
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed"
        }
        
        # Set environment variable for bucket name
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket"}):
            # Make the request
            response = client.post("/generate-cur", json=payload)
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the default row count was used
        data = response.json()
        assert "20 rows" in data["message"]

class TestGetFileEndpoint:
    """Tests for the /files/{filename} endpoint."""
    
    @patch('boto3.client')  # Patch at the module level
    def test_get_existing_file(self, mock_boto3):
        """Test that an existing file can be redirected."""
        # Mock boto3 client
        mock_s3 = MagicMock()
        mock_boto3.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Set environment variable for bucket name
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket"}):
            # Try to get a file
            filename = "test_file.csv"
            response = client.get(f"/files/{filename}")
        
        # Check that generate_presigned_url was called with correct parameters
        mock_s3.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'test-bucket', 'Key': filename},
            ExpiresIn=3600
        )
        
        # Expect a redirect response
        assert response.status_code in [302, 307]
        assert response.headers["location"] == "https://example.com/test-file.csv"