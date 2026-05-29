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
  
  // Ingestion
  ingestSAP: (data) => apiClient.post('/ingestion/ingest-sap/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  ingestUtility: (data) => apiClient.post('/ingestion/ingest-utility/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  ingestTravel: (data) => apiClient.post('/ingestion/ingest-travel/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  
  // Ingestion Jobs
  getIngestionJobs: (params) => apiClient.get('/ingestion-jobs/', { params }),
};

export default apiClient;
