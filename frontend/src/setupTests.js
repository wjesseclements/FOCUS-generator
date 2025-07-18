// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock window.URL methods for file download tests and axios
Object.defineProperty(window, 'URL', {
  value: class URL {
    constructor(url, base) {
      this.href = base ? `${base}/${url}` : url;
      this.protocol = 'https:';
      this.host = 'example.com';
      this.hostname = 'example.com';
      this.port = '';
      this.pathname = url.split('?')[0];
      this.search = url.includes('?') ? url.split('?')[1] : '';
      this.origin = 'https://example.com';
    }
    static createObjectURL = jest.fn(() => 'mocked-url');
    static revokeObjectURL = jest.fn();
  }
});

// Also add global URL
global.URL = window.URL;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Global test setup
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();
});
