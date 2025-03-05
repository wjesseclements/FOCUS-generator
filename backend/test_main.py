import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from .main import app

# Create a test client
client = TestClient(app)

class TestGenerateCurEndpoint:
    """Tests for the /generate-cur endpoint."""
    
    @patch('backend.main.generate_focus_data')
    @patch('backend.main.validate_focus_df')
    @patch('backend.main.boto3.client')
    def test_valid_request(self, mock_s3_client, mock_validate, mock_generate):
        """Test that a valid request returns a successful response."""
        # Mock the generate_focus_data function to return a DataFrame
        mock_df = MagicMock()
        mock_generate.return_value = mock_df
        
        # Mock S3 client and presigned URL
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Create a valid request payload
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed",
            "row_count": 5
        }
        
        # Make the request
        response = client.post("/generate-cur", json=payload)
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the response contains the expected fields
        data = response.json()
        assert "message" in data
        assert "url" in data
        
        # Check that the message mentions the row count
        assert "5 rows" in data["message"]
        
        # Check that the generate_focus_data function was called with the correct arguments
        mock_generate.assert_called_once_with(row_count=5, profile="Greenfield", distribution="Evenly Distributed")
    
    # Other tests remain unchanged
    
    @patch('backend.main.generate_focus_data')
    @patch('backend.main.validate_focus_df')
    @patch('backend.main.boto3.client')
    def test_default_values(self, mock_s3_client, mock_validate, mock_generate):
        """Test that default values are used when not provided."""
        # Mock S3 client and presigned URL
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Create a minimal request
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed"
        }
        
        # Make the request
        response = client.post("/generate-cur", json=payload)
        
        # Check that the response is successful
        assert response.status_code == 200
        
        # Check that the default row count was used
        data = response.json()
        assert "20 rows" in data["message"]

class TestGetFileEndpoint:
    """Tests for the /files/{filename} endpoint."""
    
    @patch('backend.main.boto3.client')
    def test_get_existing_file(self, mock_s3_client):
        """Test that an existing file can be retrieved."""
        # Mock S3 client and presigned URL
        mock_s3 = MagicMock()
        mock_s3_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://example.com/test-file.csv"
        
        # Try to get a file
        filename = "test_file.csv"
        response = client.get(f"/files/{filename}")
        
        # Check for redirect response
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "https://example.com/test-file.csv"
        
        # Check that generate_presigned_url was called with correct parameters
        mock_s3.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'cur-gen-files', 'Key': filename},
            ExpiresIn=3600
        )
    
    # test_get_nonexistent_file remains unchanged
    
    @patch('os.path.exists')
    def test_get_nonexistent_file(self, mock_exists):
        """Test that a 404 is returned for a nonexistent file."""
        # Mock file non-existence
        mock_exists.return_value = False
        
        # Try to get a file that doesn't exist
        response = client.get("/files/nonexistent_file.csv")
        
        # Check that the response is a 404
        assert response.status_code == 404
        
        # Check that the error message mentions the file not being found
        data = response.json()
        assert "not found" in data["detail"]