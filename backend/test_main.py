import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from .main import app

# Create a test client
client = TestClient(app)

class TestGenerateCurEndpoint:
    """Tests for the /generate-cur endpoint."""
    
    @patch('backend.main.generate_focus_data')
    @patch('backend.main.validate_focus_df')
    def test_valid_request(self, mock_validate, mock_generate):
        """Test that a valid request returns a successful response."""
        # Mock the generate_focus_data function to return a DataFrame
        mock_df = MagicMock()
        mock_generate.return_value = mock_df
        
        # Create a valid request payload
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed",
            "row_count": 5
        }
        
        # Create the files directory if it doesn't exist
        os.makedirs("files", exist_ok=True)
        
        # Make the request
        with patch('os.path.exists', return_value=True):  # Mock file existence
            with patch('backend.main.FileResponse', return_value={}):  # Mock file response
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
    
    def test_invalid_profile(self):
        """Test that an invalid profile returns an error."""
        # Create a request with an invalid profile
        payload = {
            "profile": "InvalidProfile",
            "distribution": "Evenly Distributed",
            "row_count": 5
        }
        
        # Make the request
        response = client.post("/generate-cur", json=payload)
        
        # Check that the response is an error
        assert response.status_code == 400
        
        # Check that the error message mentions the invalid profile
        data = response.json()
        assert "Invalid profile" in data["detail"]
    
    def test_invalid_distribution(self):
        """Test that an invalid distribution returns an error."""
        # Create a request with an invalid distribution
        payload = {
            "profile": "Greenfield",
            "distribution": "InvalidDistribution",
            "row_count": 5
        }
        
        # Make the request
        response = client.post("/generate-cur", json=payload)
        
        # Check that the response is an error
        assert response.status_code == 400
        
        # Check that the error message mentions the invalid distribution
        data = response.json()
        assert "Invalid distribution" in data["detail"]
    
    def test_invalid_row_count(self):
        """Test that an invalid row count returns an error."""
        # Create a request with an invalid row count
        payload = {
            "profile": "Greenfield",
            "distribution": "Evenly Distributed",
            "row_count": "not_a_number"
        }
        
        # Make the request
        response = client.post("/generate-cur", json=payload)
        
        # Check that the response is an error
        assert response.status_code == 400
        
        # Check that the error message mentions the row count
        data = response.json()
        assert "row_count" in data["detail"]
    
    def test_default_values(self):
        """Test that default values are used when not provided."""
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
        
        # Clean up the generated file
        file_path = data["url"].split("/files/")[1]
        os.remove(os.path.join("files", file_path))

class TestGetFileEndpoint:
    """Tests for the /files/{filename} endpoint."""
    
    @patch('os.path.exists')
    @patch('backend.main.FileResponse')
    def test_get_existing_file(self, mock_file_response, mock_exists):
        """Test that an existing file can be retrieved."""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock file response
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/csv; charset=utf-8"}
        mock_file_response.return_value = mock_response
        
        # Try to get a file
        filename = "test_file.csv"
        response = client.get(f"/files/{filename}")
        
        # Check that the file response was created with the correct path
        mock_file_response.assert_called_once_with(os.path.join("files", filename))
        
        # The actual response will be the mock, so we can't check status code directly
        # Instead, check that the mock was called correctly
    
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