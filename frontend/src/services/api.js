import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const api = {
  // Authentication
  login: (credentials) => axios.post(`${API_BASE_URL.replace('/api', '')}/api/auth/login/`, credentials),
  logout: () => apiClient.post('/auth/logout/'),
  
  // Clients
  getClients: () => apiClient.get('/clients/'),
  getClient: (id) => apiClient.get(`/clients/${id}/`),
  createClient: (data) => apiClient.post('/clients/', data),
  updateClient: (id, data) => apiClient.patch(`/clients/${id}/`, data),
  
  // Data Sources
  getDataSources: (clientId) => apiClient.get('/data-sources/', { params: { client: clientId } }),
  createDataSource: (data) => apiClient.post('/data-sources/', data),
  
  // Emission Records
  getRecords: (params) => apiClient.get('/records/', { params }),
  getRecord: (id) => apiClient.get(`/records/${id}/`),
  approveRecord: (id) => apiClient.post(`/records/${id}/approve/`),
  rejectRecord: (id, data) => apiClient.post(`/records/${id}/reject/`, data),
  flagRecord: (id, data) => apiClient.post(`/records/${id}/flag/`, data),
  getDashboardSummary: (clientId) => apiClient.get('/records/dashboard_summary/', { params: { client: clientId } }),
  
  // Ingestion - use form data with multipart headers
  ingestSAP: (data) => {
    const config = { headers: { 'Content-Type': 'multipart/form-data' } };
    return apiClient.post('/ingestion/ingest_sap/', data, config);
  },
  ingestUtility: (data) => {
    const config = { headers: { 'Content-Type': 'multipart/form-data' } };
    return apiClient.post('/ingestion/ingest_utility/', data, config);
  },
  ingestTravel: (data) => {
    const config = { headers: { 'Content-Type': 'multipart/form-data' } };
    return apiClient.post('/ingestion/ingest_travel/', data, config);
  },
  
  // Ingestion Jobs
  getIngestionJobs: (params) => apiClient.get('/ingestion-jobs/', { params }),
};

export default apiClient;
