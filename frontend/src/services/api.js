import axios from 'axios';

// Defaults to relative path which works with the Nginx proxy
const API_URL = process.env.REACT_APP_API_URL || '';
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v1';

const baseURL = `${API_URL}/api/${API_VERSION}`;

console.log('API Base URL:', baseURL);

const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
    const apiKey = localStorage.getItem('seo_api_key');
    if (apiKey) {
        config.headers['X-API-Key'] = apiKey;
    }
    return config;
});

export const apiService = {
    // Auth
    verifyAuth: () => api.get('/auth/me'),

    // Domains
    getDomains: () => api.get('/domains'),
    createDomain: (data) => api.post('/domains', data),

    // Checking health
    checkHealth: () => axios.get(`${API_URL}/health`),
};

export default api;
