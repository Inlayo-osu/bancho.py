/**
 * API Client - Vanilla JavaScript
 * HTTP request wrapper with error handling
 */

class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json'
    };
  }

  async request(url, options = {}) {
    const config = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers
      }
    };

    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(this.baseURL + url, config);
      
      if (!response.ok) {
        if (response.status === 401) {
          window.location.href = '/login';
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return this.request(fullUrl, { method: 'GET' });
  }

  post(url, data = {}) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  put(url, data = {}) {
    return this.request(url, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  delete(url) {
    return this.request(url, { method: 'DELETE' });
  }
}

// Global API client instance
const api = new ApiClient();
