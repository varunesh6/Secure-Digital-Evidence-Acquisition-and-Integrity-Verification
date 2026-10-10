import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
});

export const login = async (credentials) => api.post('/auth/login', credentials);
export const logout = async () => api.post('/auth/logout');
export const getMe = async () => api.get('/auth/me');
export const getDashboard = async () => api.get('/dashboard');
export const getCases = async () => api.get('/cases');
export const createCase = async (payload) => api.post('/cases', payload);
export const getEvidence = async () => api.get('/evidence');
export const uploadEvidence = async (formData) => api.post('/evidence/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
export const verifyEvidence = async (id) => api.post(`/evidence/${id}/verify`);
export const getReports = async () => api.get('/reports');
export const generateReport = async (payload) => api.post('/reports/generate', payload);
export const getAuditLogs = async () => api.get('/audit-logs');
export const getNotifications = async () => api.get('/notifications');
export const createUser = async (payload) => api.post('/admin/users', payload);
export const getUsers = async () => api.get('/admin/users');

export default api;
