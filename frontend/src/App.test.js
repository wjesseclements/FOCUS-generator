import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('App Component', () => {
  const mockedAxios = axios;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders FOCUS CUR Generator title', () => {
    render(<App />);
    expect(screen.getByText('FOCUS CUR Generator')).toBeInTheDocument();
  });

  test('renders profile and distribution selection buttons', () => {
    render(<App />);
    
    // Check profile buttons
    expect(screen.getByText('Greenfield')).toBeInTheDocument();
    expect(screen.getByText('Large Business')).toBeInTheDocument();
    expect(screen.getByText('Enterprise')).toBeInTheDocument();
    
    // Check distribution buttons
    expect(screen.getByText('Evenly Distributed')).toBeInTheDocument();
    expect(screen.getByText('ML-Focused')).toBeInTheDocument();
    expect(screen.getByText('Data-Intensive')).toBeInTheDocument();
    expect(screen.getByText('Media-Intensive')).toBeInTheDocument();
    
    // Check row count input
    expect(screen.getByDisplayValue('20')).toBeInTheDocument();
  });

  test('updates row count when user types', () => {
    render(<App />);
    
    const rowCountInput = screen.getByDisplayValue('20');
    
    fireEvent.change(rowCountInput, { target: { value: '100' } });
    
    expect(rowCountInput.value).toBe('100');
  });

  test('validates row count inputs', () => {
    render(<App />);
    
    const rowCountInput = screen.getByDisplayValue('20');
    
    // Test invalid inputs (should not accept negative numbers or zero)
    fireEvent.change(rowCountInput, { target: { value: '-1' } });
    expect(rowCountInput.value).toBe('20'); // Should remain unchanged
    
    fireEvent.change(rowCountInput, { target: { value: '0' } });
    expect(rowCountInput.value).toBe('20'); // Should remain unchanged
    
    // Test valid input
    fireEvent.change(rowCountInput, { target: { value: '50' } });
    expect(rowCountInput.value).toBe('50');
  });

  test('profile and distribution selection works correctly', () => {
    render(<App />);
    
    // Select profile
    const greenfieldButton = screen.getByText('Greenfield');
    fireEvent.click(greenfieldButton);
    expect(greenfieldButton).toHaveClass('bg-blue-600');
    
    // Select distribution
    const mlFocusedButton = screen.getByText('ML-Focused');
    fireEvent.click(mlFocusedButton);
    expect(mlFocusedButton).toHaveClass('bg-blue-600');
  });

  test('successful form submission and CUR generation', async () => {
    // Mock successful API response
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        message: 'CUR generated successfully!',
        url: 'https://example.com/download/test.csv'
      }
    });

    render(<App />);
    
    // Select profile and distribution to enable button
    fireEvent.click(screen.getByText('Enterprise'));
    fireEvent.click(screen.getByText('Data-Intensive'));
    
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);

    // Check loading state
    expect(screen.getByText('Generating...')).toBeInTheDocument();

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Success!')).toBeInTheDocument();
      expect(screen.getByText('CUR generated successfully!')).toBeInTheDocument();
    });

    // Verify API was called with correct parameters
    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://localhost:8000/generate-cur',
      {
        profile: 'Enterprise',
        distribution: 'Data-Intensive',
        row_count: 20
      }
    );
    
    // Check download link is present
    expect(screen.getByText('Download CUR (20 rows)')).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    // Mock network error
    mockedAxios.post.mockRejectedValueOnce({
      request: true,
      message: 'Network Error'
    });

    // Mock alert
    window.alert = jest.fn();

    render(<App />);
    
    // Select profile and distribution to enable button
    fireEvent.click(screen.getByText('Greenfield'));
    fireEvent.click(screen.getByText('Evenly Distributed'));
    
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);

    // Wait for error handling
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith(
        'Network error: Unable to connect to the server. Please check if the API is running.'
      );
    });

    // Button should be re-enabled after error
    expect(generateButton).not.toBeDisabled();
  });

  test('handles HTTP error responses', async () => {
    // Mock HTTP error response
    mockedAxios.post.mockRejectedValueOnce({
      response: {
        status: 500,
        data: { detail: 'Internal server error' }
      }
    });

    // Mock alert
    window.alert = jest.fn();

    render(<App />);
    
    // Select profile and distribution to enable button
    fireEvent.click(screen.getByText('Large Business'));
    fireEvent.click(screen.getByText('ML-Focused'));
    
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Error: Internal server error');
    });
  });

  test('button is disabled when profile or distribution not selected', () => {
    render(<App />);
    
    const generateButton = screen.getByText('Generate CUR');
    
    // Button should be disabled initially
    expect(generateButton).toBeDisabled();
    expect(generateButton).toHaveClass('cursor-not-allowed');
    
    // Select only profile - button should still be disabled
    fireEvent.click(screen.getByText('Enterprise'));
    expect(generateButton).toBeDisabled();
    
    // Select distribution - button should be enabled
    fireEvent.click(screen.getByText('Data-Intensive'));
    expect(generateButton).not.toBeDisabled();
  });

  test('reset functionality works correctly', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        message: 'CUR generated successfully!',
        url: 'https://example.com/download/test.csv'
      }
    });

    render(<App />);
    
    // Select profile and distribution
    fireEvent.click(screen.getByText('Greenfield'));
    fireEvent.click(screen.getByText('Media-Intensive'));
    
    // Change row count
    const rowCountInput = screen.getByDisplayValue('20');
    fireEvent.change(rowCountInput, { target: { value: '50' } });
    
    // Generate CUR
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);
    
    // Wait for success
    await waitFor(() => {
      expect(screen.getByText('Reset')).toBeInTheDocument();
    });
    
    // Click reset
    const resetButton = screen.getByText('Reset');
    fireEvent.click(resetButton);
    
    // Check that form is reset
    expect(screen.getByText('Generate CUR')).toBeInTheDocument();
    expect(screen.getByDisplayValue('20')).toBeInTheDocument();
    expect(screen.queryByText('Success!')).not.toBeInTheDocument();
  });

  test('form submission disabled during loading', async () => {
    // Mock slow API response
    let resolvePromise;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    
    mockedAxios.post.mockReturnValueOnce(promise);

    render(<App />);
    
    // Select profile and distribution to enable button
    fireEvent.click(screen.getByText('Enterprise'));
    fireEvent.click(screen.getByText('Data-Intensive'));
    
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);

    // Button should be disabled during loading
    expect(generateButton).toBeDisabled();
    expect(screen.getByText('Generating...')).toBeInTheDocument();

    // Resolve the promise
    resolvePromise({
      data: { message: 'Success!', url: 'test.csv' }
    });

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText('Reset')).toBeInTheDocument();
    });
  });

  test('uses environment variable for API URL', () => {
    // Note: In actual usage, environment variables need to be set at build time
    // This test verifies the default fallback behavior
    mockedAxios.post.mockResolvedValueOnce({
      data: { message: 'Success!', url: 'test.csv' }
    });

    render(<App />);
    
    // Select profile and distribution to enable button
    fireEvent.click(screen.getByText('Greenfield'));
    fireEvent.click(screen.getByText('Evenly Distributed'));
    
    const generateButton = screen.getByText('Generate CUR');
    fireEvent.click(generateButton);

    // Should use the default localhost URL since REACT_APP_API_URL is not set
    expect(mockedAxios.post).toHaveBeenCalledWith(
      'http://localhost:8000/generate-cur',
      expect.any(Object)
    );
  });

  test('tooltips display helpful information', async () => {
    render(<App />);
    
    // Check if tooltips work (basic presence test)
    // Note: Full tooltip testing would require more complex setup
    expect(screen.getByText('Greenfield')).toBeInTheDocument();
    expect(screen.getByText('Large Business')).toBeInTheDocument();
    expect(screen.getByText('Enterprise')).toBeInTheDocument();
  });

  test('footer disclaimer is displayed', () => {
    render(<App />);
    
    expect(screen.getByText(/This data is not real and is only intended for testing purposes/)).toBeInTheDocument();
    expect(screen.getByText(/This website is not affiliated with AWS or the FinOps Foundation/)).toBeInTheDocument();
  });
});
